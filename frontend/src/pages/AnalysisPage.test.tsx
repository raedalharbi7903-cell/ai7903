import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { expect, it, vi } from "vitest";
import { App } from "../app/App";
import { syntheticResult } from "../test/results";
import { historyEntry } from "../test/history";

it("saves only through the explicit save action and displays committed success", async () => {
  const fetch = vi.fn<typeof globalThis.fetch>(
    async () => new Response(JSON.stringify(historyEntry()), { status: 201 }),
  );
  vi.stubGlobal("fetch", fetch);
  render(
    <MemoryRouter>
      <App />
    </MemoryRouter>,
  );
  fireEvent.click(screen.getByRole("button", { name: "تحليل جديد وحفظ النتيجة" }));
  expect(await screen.findByText(/حُفظت النتيجة/)).toBeVisible();
  expect(fetch).toHaveBeenCalledTimes(1);
  expect(String(fetch.mock.calls[0][0])).toMatch(/\/history$/);
  const body = JSON.parse(String(fetch.mock.calls[0][1]?.body));
  expect(body).not.toHaveProperty("result");
  expect(body).not.toHaveProperty("owner");
});

it("does not present saving as successful when authentication is unavailable", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => new Response("PRIVATE", { status: 401 })),
  );
  render(
    <MemoryRouter>
      <App />
    </MemoryRouter>,
  );
  fireEvent.click(screen.getByRole("button", { name: "تحليل جديد وحفظ النتيجة" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("يلزم تسجيل دخول موثوق");
  expect(screen.queryByText(/حُفظت النتيجة/)).not.toBeInTheDocument();
});

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
  expect(screen.getByText(/مساحة التحليل جاهزة/)).toBeVisible();
  expect(screen.getByText(/وضع تجريبي/)).toBeVisible();
  fireEvent.click(screen.getByRole("button", { name: "حلّل البيانات التجريبية" }));
  expect(screen.getByRole("status")).toHaveTextContent("جارٍ تنفيذ التحليل الحتمي");
  expect(screen.getByRole("button", { name: "جارٍ التحليل…" })).toBeDisabled();
  finish(new Response(JSON.stringify(syntheticResult("wait"))));
  expect(await screen.findByRole("heading", { name: "انتظار" })).toBeVisible();
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
  fireEvent.click(screen.getByRole("button", { name: "حلّل البيانات التجريبية" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("التحليل غير متاح حاليًا");
  expect(screen.queryByText(/secret internal/)).not.toBeInTheDocument();
});
it("routes missing pages", () => {
  render(
    <MemoryRouter initialEntries={["/missing"]}>
      <App />
    </MemoryRouter>,
  );
  expect(screen.getByRole("heading", { name: "الصفحة غير موجودة" })).toBeVisible();
});

it("renders an Arabic RTL workflow without making unsolicited analysis requests", () => {
  const fetch = vi.fn();
  vi.stubGlobal("fetch", fetch);
  render(
    <MemoryRouter>
      <App />
    </MemoryRouter>,
  );
  const main = screen.getByRole("main");
  expect(main.closest('[dir="rtl"]')?.getAttribute("lang")).toBe("ar");
  expect(main.getAttribute("tabindex")).toBe("-1");
  const pair = screen.getByRole("textbox", { name: "زوج الأصول" });
  expect(pair.getAttribute("dir")).toBe("ltr");
  expect(pair.getAttribute("aria-describedby")).toBe("pair-hint");
  expect(fetch).not.toHaveBeenCalled();
});

it.each(["network", "malformed-response"])(
  "does not expose private %s errors to the customer",
  async (failure) => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        if (failure === "network") throw new Error("private-network-secret");
        return new Response("private-response-secret", { status: 200 });
      }),
    );
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>,
    );
    fireEvent.click(screen.getByRole("button", { name: "حلّل البيانات التجريبية" }));
    expect(await screen.findByRole("alert")).toBeVisible();
    expect(screen.queryByText(/private-.*-secret/)).not.toBeInTheDocument();
  },
);
