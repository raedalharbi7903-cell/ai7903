import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { expect, inject, it, vi } from "vitest";
import { App } from "../../app/App";
import { createFixture } from "./fixture";
import { requestAnalysis } from "../../services/analysis";

declare module "vitest" {
  export interface ProvidedContext {
    apiUrl: string;
  }
}

it("isolates concurrent typed requests through the actual HTTP server", async () => {
  const nativeFetch = globalThis.fetch;
  vi.stubGlobal("fetch", (url: string, init?: RequestInit) =>
    nativeFetch(new URL(url, inject("apiUrl")), init),
  );
  const pairs = Array.from({ length: 16 }, (_, index) => `FIXTURE${index}-USDT`);
  const results = await Promise.all(
    pairs.map((pair) => requestAnalysis(createFixture(pair, "1h"))),
  );
  results.forEach((result, index) => {
    expect(result.contract_version).toBe("1.0");
    expect(["buy", "sell"]).not.toContain(result.decision);
    const data = result.outputs.find((output) => output.engine_name === "data");
    expect(data?.data.instrument).toBe(pairs[index]);
    expect(data?.data.fixture).toBe(true);
    const confidence = result.outputs.find(
      (output) => output.engine_name === "confidence",
    );
    expect(confidence?.data.calibration).toBe("uncalibrated");
    expect(result.advanced_findings).toHaveLength(5);
  });
});

it("runs React → real FastAPI → AnalysisService → advanced results → React", async () => {
  const nativeFetch = globalThis.fetch;
  // URL adaptation only. No response or analysis engine is mocked.
  vi.stubGlobal("fetch", (url: string, init?: RequestInit) =>
    nativeFetch(new URL(url, inject("apiUrl")), init),
  );
  render(
    <MemoryRouter>
      <App />
    </MemoryRouter>,
  );
  fireEvent.click(screen.getByRole("button", { name: "حلّل البيانات التجريبية" }));
  expect(await screen.findByRole("heading", { name: "لا تداول" })).toBeVisible();
  // Classification and the raw details field now share the same Arabic label.
  expect(
    screen.getByText("تباعد صاعد عادي", { selector: ".classification" }),
  ).toBeVisible();
  expect(screen.getByText("synthetic_demo")).toBeVisible();
  expect(screen.getByText("غير مُعاير")).toBeVisible();
  expect(screen.getByText(/حُجبت مستويات المخاطر/)).toBeVisible();
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
});
