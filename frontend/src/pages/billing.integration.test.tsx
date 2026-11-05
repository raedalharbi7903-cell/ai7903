import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { expect, inject, it, vi } from "vitest";
import { App } from "../app/App";

it("reads real persisted normalized billing then explicitly records local cancellation over HTTP", async () => {
  const original = globalThis.fetch;
  const calls: { url: string; method: string }[] = [];
  vi.stubGlobal("fetch", (url: string, options: RequestInit = {}) => {
    const headers = new Headers(options.headers);
    headers.set("Authorization", "Bearer synthetic-billing-test"); // test harness only
    if (options.method === "POST") headers.set("Origin", "https://frontend.test");
    calls.push({ url, method: options.method ?? "GET" });
    return original(new URL(url, inject("historyApiUrl")), { ...options, headers });
  });
  render(
    <MemoryRouter initialEntries={["/subscription"]}>
      <App />
    </MemoryRouter>,
  );
  expect(calls).toHaveLength(0);
  fireEvent.click(screen.getByRole("button", { name: "تحميل حالة الاشتراك" }));
  const summary = await screen.findByRole("region", { name: "حالة الاشتراك" });
  expect(summary).toHaveTextContent("فترة مدفوعة سارية");
  fireEvent.click(screen.getByRole("button", { name: "تحميل سجل الفوترة" }));
  expect(
    await screen.findByRole("region", { name: "أحداث الفوترة" }),
  ).toHaveTextContent("12345 SAR");
  fireEvent.click(screen.getByRole("button", { name: "طلب إيقاف التجديد" }));
  fireEvent.click(screen.getByRole("button", { name: "رجوع" }));
  expect(calls.filter((call) => call.method === "POST")).toHaveLength(0);
  fireEvent.click(screen.getByRole("button", { name: "طلب إيقاف التجديد" }));
  fireEvent.click(screen.getByRole("button", { name: "تأكيد إيقاف التجديد" }));
  expect(await screen.findByText(/سُجّل طلب إيقاف التجديد محلياً/)).toBeVisible();
  expect(screen.getByRole("region", { name: "حالة الاشتراك" })).toHaveTextContent(
    "لا يُختصر",
  );
  fireEvent.click(screen.getByRole("button", { name: "تحميل حالة الاشتراك" }));
  expect(
    await screen.findByRole("region", { name: "حالة الاشتراك" }),
  ).toHaveTextContent("إيقاف التجديد مسجل");
  expect(calls.every((call) => call.url.startsWith("/api/v1/billing/"))).toBe(true);
  expect(calls.filter((call) => call.method === "POST")).toHaveLength(1);
});
it("ordinary API denies the exact synthetic billing identity and unconfigured payment ingress", async () => {
  const response = await fetch(
    new URL("/api/v1/billing/subscription", inject("apiUrl")),
    {
      headers: { Authorization: "Bearer synthetic-billing-test", "X-Role": "founder" },
    },
  );
  expect(response.status).toBe(401);
  const forged = await fetch(new URL("/api/v1/billing/events", inject("apiUrl")), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      kind: "paid",
      owner_key: "a".repeat(64),
      amount_minor: 16900,
    }),
  });
  expect(forged.status).toBe(503);
});
