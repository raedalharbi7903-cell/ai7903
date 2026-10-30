import { spawn } from "node:child_process";
import { createServer } from "node:net";
import { resolve } from "node:path";
import { setTimeout } from "node:timers/promises";
import type { TestProject } from "vitest/node";

async function startServer(module: string) {
  const reservation = createServer();
  await new Promise<void>((done) => reservation.listen(0, "127.0.0.1", done));
  const address = reservation.address();
  if (!address || typeof address === "string") throw new Error("No test port");
  const port = address.port;
  await new Promise<void>((done) => reservation.close(() => done()));
  const backend = resolve("../backend");
  const python =
    process.env.BACKEND_PYTHON ??
    resolve(
      backend,
      ".venv",
      process.platform === "win32" ? "Scripts/python.exe" : "bin/python",
    );
  const child = spawn(
    python,
    [
      "-m",
      "uvicorn",
      module,
      "--no-access-log",
      "--host",
      "127.0.0.1",
      "--port",
      String(port),
    ],
    {
      cwd: backend,
      windowsHide: true,
      env: {
        ...process.env,
        APP_NAME: "integration-tests",
        APP_ENVIRONMENT: "testing",
        LOG_LEVEL: "WARNING",
        DATABASE_URL: "sqlite://",
      },
      stdio: ["ignore", "pipe", "pipe"],
    },
  );
  let logs = "";
  let startupError: Error | undefined;
  child.on("error", (error) => {
    startupError = error;
  });
  child.stdout.on("data", (chunk) => {
    logs = (logs + String(chunk)).slice(-4000);
  });
  child.stderr.on("data", (chunk) => {
    logs = (logs + String(chunk)).slice(-4000);
  });
  const url = `http://127.0.0.1:${port}`;
  for (let attempt = 0; attempt < 100; attempt++) {
    if (startupError || child.exitCode !== null) {
      child.kill();
      throw new Error(`Backend test startup failed: ${startupError?.message ?? logs}`);
    }
    try {
      const health = await fetch(`${url}/health`, { signal: AbortSignal.timeout(500) });
      if (health.ok) {
        return {
          url,
          stop: async () => {
            child.kill();
            if (child.exitCode === null)
              await new Promise<void>((done) => child.once("exit", () => done()));
          },
        };
      }
    } catch {
      /* Startup polling only; failures are reported at the deadline. */
    }
    await setTimeout(100);
  }
  child.kill();
  throw new Error(`Backend test startup timed out: ${logs}`);
}

export default async function setup(project: TestProject) {
  const api = await startServer("app.main:app");
  try {
    const history = await startServer("tests.http_history_fixture:app");
    project.provide("apiUrl", api.url);
    project.provide("historyApiUrl", history.url);
    return async () => {
      await Promise.all([api.stop(), history.stop()]);
    };
  } catch (error) {
    await api.stop();
    throw error;
  }
}
