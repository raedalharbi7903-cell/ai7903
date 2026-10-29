import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { expect, inject, it, vi } from "vitest";
import { App } from "../../app/App";

declare module "vitest" {
  export interface ProvidedContext {
    apiUrl: string;
  }
}

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
  fireEvent.click(screen.getByRole("button", { name: "Analyze fixture" }));
  expect(await screen.findByRole("heading", { name: "NO TRADE" })).toBeVisible();
  expect(screen.getByText("regular bullish divergence")).toBeVisible();
  expect(screen.getByText("synthetic_demo")).toBeVisible();
  expect(screen.getByText("uncalibrated")).toBeVisible();
  expect(screen.getByText(/Risk levels are withheld/)).toBeVisible();
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
});
