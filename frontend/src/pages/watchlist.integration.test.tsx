import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { expect, inject, it, vi } from "vitest";
import { App } from "../app/App";

it("saves, deduplicates, lists and removes a real owned preference over HTTP without analysis", async () => {
  const original = globalThis.fetch;
  const calls: { url: string; method: string }[] = [];
  vi.stubGlobal("fetch", (url: string, options: RequestInit = {}) => {
    const headers = new Headers(options.headers);
    headers.set("Authorization", "Bearer synthetic-watchlist-test"); // test harness only
    if (options.method === "POST" || options.method === "DELETE")
      headers.set("Origin", "https://frontend.test");
    calls.push({ url, method: options.method ?? "GET" });
    return original(new URL(url, inject("historyApiUrl")), { ...options, headers });
  });
  render(
    <MemoryRouter initialEntries={["/watchlist"]}>
      <App />
    </MemoryRouter>,
  );
  expect(calls).toHaveLength(0);
  fireEvent.change(screen.getByRole("textbox", { name: "زوج العملات" }), {
    target: { value: "BTC-USDT" },
  });
  fireEvent.click(screen.getByRole("button", { name: "حفظ في قائمة المتابعة" }));
  await screen.findByText(/الزوج BTC-USDT محفوظ/);
  fireEvent.click(screen.getByRole("button", { name: "حفظ في قائمة المتابعة" }));
  await screen.findByText(/الزوج BTC-USDT محفوظ/);
  fireEvent.click(screen.getByRole("button", { name: "تحميل قائمة المتابعة" }));
  const remove = await screen.findAllByRole("button", { name: "إزالة BTC-USDT" });
  expect(remove).toHaveLength(1);
  fireEvent.click(remove[0]);
  expect(calls.filter((call) => call.method === "DELETE")).toHaveLength(0);
  fireEvent.click(screen.getByRole("button", { name: "تأكيد الإزالة" }));
  await screen.findByText("أُزيل العنصر من قائمة المتابعة.");
  fireEvent.click(screen.getByRole("button", { name: "تحميل قائمة المتابعة" }));
  expect(await screen.findByText("لا توجد عناصر متاحة في هذه الصفحة.")).toBeVisible();
  expect(calls.every((call) => call.url.includes("/watchlist"))).toBe(true);
  expect(calls.filter((call) => call.method === "POST")).toHaveLength(2);
});
it("ordinary API rejects test identity instead of providing a fake customer account", async () => {
  const response = await fetch(new URL("/api/v1/watchlist", inject("apiUrl")), {
    headers: { Authorization: "Bearer synthetic-watchlist-test", "X-Role": "founder" },
  });
  expect(response.status).toBe(401);
  expect((await response.json()).error.code).toBe("authentication_required");
});
