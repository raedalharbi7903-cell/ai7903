import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { expect, it, vi } from "vitest";
import { App } from "../app/App";
import { syntheticResult } from "../test/results";

it("renders empty and loading states, then a typed API result", async () => {
  let finish!: (response: Response) => void;
  vi.stubGlobal(
    "fetch",
    vi.fn(
      () =>
        new Promise<Response>((resolve) => {
          finish = resolve;
        }),
    ),
  );
  render(
    <MemoryRouter>
      <App />
    </MemoryRouter>,
  );
  expect(screen.getByText(/workspace is ready/)).toBeVisible();
  expect(screen.getByText(/DEMO MODE/)).toBeVisible();
  fireEvent.click(screen.getByRole("button", { name: "Analyze fixture" }));
  expect(screen.getByRole("status")).toHaveTextContent(
    "Running deterministic analysis",
  );
  expect(screen.getByRole("button", { name: "Analyzing…" })).toBeDisabled();
  finish(new Response(JSON.stringify(syntheticResult("wait"))));
  expect(await screen.findByRole("heading", { name: "WAIT" })).toBeVisible();
});
it("displays safe API errors without raw internals", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => new Response("secret internal stack", { status: 500 })),
  );
  render(
    <MemoryRouter>
      <App />
    </MemoryRouter>,
  );
  fireEvent.click(screen.getByRole("button", { name: "Analyze fixture" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("Analysis is unavailable");
  expect(screen.queryByText(/secret internal/)).not.toBeInTheDocument();
});
it("routes missing pages", () => {
  render(
    <MemoryRouter initialEntries={["/missing"]}>
      <App />
    </MemoryRouter>,
  );
  expect(screen.getByRole("heading", { name: "Page not found" })).toBeVisible();
});
