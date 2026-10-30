import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { expect, inject, it, vi } from "vitest";
import { App } from "../app/App";

declare module "vitest" {
  export interface ProvidedContext {
    historyApiUrl: string;
  }
}

it("reads actual owned pipeline snapshots through HTTP without running new analysis", async () => {
  const original = globalThis.fetch;
  const requests: RequestInit[] = [];
  vi.stubGlobal("fetch", (url: string, options: RequestInit = {}) => {
    requests.push(options);
    // Test harness only: production source never creates a synthetic identity.
    return original(new URL(url, inject("historyApiUrl")), {
      ...options,
      headers: { Authorization: "Bearer synthetic-history-test" },
    });
  });
  render(
    <MemoryRouter initialEntries={["/history"]}>
      <App />
    </MemoryRouter>,
  );
  expect(requests).toHaveLength(0);
  fireEvent.click(screen.getByRole("button", { name: "تحميل السجل" }));
  const open = await screen.findAllByRole("button", { name: /^فتح السجل / });
  expect(open).toHaveLength(1); // The other synthetic owner's record is absent.
  fireEvent.click(open[0]);
  expect(await screen.findByRole("region", { name: "نتيجة محفوظة" })).toBeVisible();
  expect(screen.getByRole("heading", { name: "شراء" })).toBeVisible();
  expect(screen.getByText(/ليست تحديثاً للسوق/)).toBeVisible();
  expect(
    screen.getByText(/البيانات تجريبية مصطنعة وليست بيانات سوق حية/),
  ).toBeVisible();
  expect(requests).toHaveLength(2);
  expect(requests.every((request) => request.method === "GET")).toBe(true);
  expect(requests.every((request) => request.cache === "no-store")).toBe(true);
});

it("explicitly saves a fresh analysis then reads and confirms deletion over real HTTP", async () => {
  const original = globalThis.fetch;
  const calls: { url: string; method: string }[] = [];
  vi.stubGlobal("fetch", (url: string, options: RequestInit = {}) => {
    const headers = new Headers(options.headers);
    headers.set("Authorization", "Bearer synthetic-save-test");
    // Native Node fetch does not supply browser Origin; test harness only.
    if (options.method === "POST" || options.method === "DELETE") {
      headers.set("Origin", "https://frontend.test");
    }
    calls.push({ url, method: options.method ?? "GET" });
    return original(new URL(url, inject("historyApiUrl")), { ...options, headers });
  });
  render(
    <MemoryRouter>
      <App />
    </MemoryRouter>,
  );
  expect(calls).toHaveLength(0);
  fireEvent.click(screen.getByRole("button", { name: "تحليل جديد وحفظ النتيجة" }));
  await screen.findByText(/حُفظت النتيجة/);
  expect(screen.getByRole("status")).toHaveTextContent("حُفظت النتيجة");
  expect(calls.filter((call) => call.method === "POST")).toHaveLength(1);
  expect(calls[0].url).toMatch(/\/history$/);
  fireEvent.click(screen.getByRole("link", { name: "افتح سجل التحليلات" }));
  fireEvent.click(screen.getByRole("button", { name: "تحميل السجل" }));
  const entries = await screen.findAllByRole("button", { name: /^فتح السجل / });
  expect(entries).toHaveLength(1);
  fireEvent.click(entries[0]);
  await screen.findByRole("region", { name: "نتيجة محفوظة" });
  fireEvent.click(screen.getByRole("button", { name: "حذف النتيجة المحفوظة" }));
  expect(calls.filter((call) => call.method === "DELETE")).toHaveLength(0);
  fireEvent.click(screen.getByRole("button", { name: "إلغاء" }));
  expect(calls.filter((call) => call.method === "DELETE")).toHaveLength(0);
  fireEvent.click(screen.getByRole("button", { name: "حذف النتيجة المحفوظة" }));
  fireEvent.click(screen.getByRole("button", { name: "تأكيد الحذف" }));
  expect(await screen.findByText("حُذفت النتيجة المحفوظة.")).toBeVisible();
  fireEvent.click(screen.getByRole("button", { name: "تحميل السجل" }));
  expect(await screen.findByText("لا توجد سجلات متاحة في هذه الصفحة.")).toBeVisible();
  expect(calls.filter((call) => call.method === "DELETE")).toHaveLength(1);
});

it("actual default API refuses history without a configured identity provider", async () => {
  const original = globalThis.fetch;
  vi.stubGlobal("fetch", (url: string, options: RequestInit) =>
    original(new URL(url, inject("apiUrl")), options),
  );
  render(
    <MemoryRouter initialEntries={["/history"]}>
      <App />
    </MemoryRouter>,
  );
  fireEvent.click(screen.getByRole("button", { name: "تحميل السجل" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("يلزم تسجيل دخول موثوق");
  expect(
    screen.queryByRole("region", { name: "نتيجة محفوظة" }),
  ).not.toBeInTheDocument();
});
