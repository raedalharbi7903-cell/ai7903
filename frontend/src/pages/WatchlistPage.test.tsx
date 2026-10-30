import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { expect, it, vi } from "vitest";
import { App } from "../app/App";
import { watchlistItem, watchlistPage } from "../test/watchlist";
import { saveWatchlistItem } from "../services/watchlist";

function show() {
  return render(
    <MemoryRouter initialEntries={["/watchlist"]}>
      <App />
    </MemoryRouter>,
  );
}
it("loads only on request with empty/loading states and no analysis", async () => {
  let finish!: (value: Response) => void;
  const fetch = vi.fn(
    () =>
      new Promise<Response>((done) => {
        finish = done;
      }),
  );
  vi.stubGlobal("fetch", fetch);
  show();
  expect(fetch).not.toHaveBeenCalled();
  expect(
    screen.getByRole("complementary", { name: "حدود قائمة المتابعة" }),
  ).toHaveTextContent("لا تُجري القائمة تحليلاً");
  fireEvent.click(screen.getByRole("button", { name: "تحميل قائمة المتابعة" }));
  expect(screen.getByRole("status")).toHaveTextContent("جارٍ تنفيذ");
  finish(new Response(JSON.stringify({ ...watchlistPage(), items: [] })));
  expect(await screen.findByText("لا توجد عناصر متاحة في هذه الصفحة.")).toBeVisible();
  expect(fetch).toHaveBeenCalledTimes(1);
});
it.each([200, 201])(
  "saves explicit preference without invented prices or analysis, HTTP %s",
  async (status) => {
    const fetch = vi.fn<typeof globalThis.fetch>(
      async () => new Response(JSON.stringify(watchlistItem), { status }),
    );
    vi.stubGlobal("fetch", fetch);
    show();
    fireEvent.change(screen.getByRole("textbox", { name: "زوج العملات" }), {
      target: { value: "btc-usdt" },
    });
    fireEvent.click(screen.getByRole("button", { name: "حفظ في قائمة المتابعة" }));
    await screen.findByText(/الزوج BTC-USDT محفوظ/);
    expect(screen.getByRole("status")).toHaveTextContent("محفوظ");
    expect(JSON.parse(String(fetch.mock.calls[0][1]?.body))).toEqual({
      pair: "BTC-USDT",
      timeframe: "1h",
    });
    expect(String(fetch.mock.calls[0][0])).toMatch(/\/watchlist$/);
    expect(fetch.mock.calls[0][1]?.credentials).toBe("same-origin");
    expect(fetch.mock.calls[0][1]?.cache).toBe("no-store");
  },
);
it("requires delete confirmation, cancel sends nothing, and selecting analysis only prefills", async () => {
  const fetch = vi
    .fn()
    .mockResolvedValueOnce(new Response(JSON.stringify(watchlistPage())))
    .mockResolvedValueOnce(new Response(null, { status: 204 }));
  vi.stubGlobal("fetch", fetch);
  show();
  fireEvent.click(screen.getByRole("button", { name: "تحميل قائمة المتابعة" }));
  fireEvent.click(await screen.findByRole("button", { name: "إزالة BTC-USDT" }));
  fireEvent.click(screen.getByRole("button", { name: "إلغاء" }));
  expect(fetch).toHaveBeenCalledTimes(1);
  fireEvent.click(screen.getByRole("button", { name: "إزالة BTC-USDT" }));
  fireEvent.click(screen.getByRole("button", { name: "تأكيد الإزالة" }));
  expect(await screen.findByText("أُزيل العنصر من قائمة المتابعة.")).toBeVisible();
  expect(fetch.mock.calls[1][1].method).toBe("DELETE");
});
it("prefills a selected minute timeframe without running analysis", async () => {
  const fetch = vi.fn(
    async () =>
      new Response(
        JSON.stringify({
          ...watchlistPage(),
          items: [{ ...watchlistItem, timeframe: "5m" }],
        }),
      ),
  );
  vi.stubGlobal("fetch", fetch);
  show();
  fireEvent.click(screen.getByRole("button", { name: "تحميل قائمة المتابعة" }));
  fireEvent.click(
    await screen.findByRole("link", { name: "اختيار BTC-USDT للتحليل التجريبي" }),
  );
  expect((screen.getByRole("textbox", { name: /زوج/ }) as HTMLInputElement).value).toBe(
    "BTC-USDT",
  );
  expect((screen.getByRole("combobox") as HTMLSelectElement).value).toBe("5m");
  expect(fetch).toHaveBeenCalledTimes(1);
});
it.each([401, 403, 404, 500, 503])(
  "clears private data on %s and never exposes response text",
  async (status) => {
    const fetch = vi
      .fn()
      .mockResolvedValueOnce(new Response(JSON.stringify(watchlistPage())))
      .mockResolvedValueOnce(new Response("PRIVATE_WATCHLIST_SECRET", { status }));
    vi.stubGlobal("fetch", fetch);
    show();
    fireEvent.click(screen.getByRole("button", { name: "تحميل قائمة المتابعة" }));
    await screen.findByRole("region", { name: "عناصر قائمة المتابعة" });
    fireEvent.click(screen.getByRole("button", { name: "تحميل قائمة المتابعة" }));
    expect(await screen.findByRole("alert")).toBeVisible();
    expect(
      screen.queryByRole("region", { name: "عناصر قائمة المتابعة" }),
    ).not.toBeInTheDocument();
    expect(screen.queryByText(/PRIVATE_WATCHLIST_SECRET/)).not.toBeInTheDocument();
  },
);
it("rejects a returned preference different from the request", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(
      async () => new Response(JSON.stringify({ ...watchlistItem, pair: "ETH-USDT" })),
    ),
  );
  await expect(
    saveWatchlistItem({ pair: "BTC-USDT", timeframe: "1h" }),
  ).rejects.toThrow("تعذّر التحقق");
});
it("does not claim removal on incompatible successful response", async () => {
  vi.stubGlobal(
    "fetch",
    vi
      .fn()
      .mockResolvedValueOnce(new Response(JSON.stringify(watchlistPage())))
      .mockResolvedValueOnce(new Response("PRIVATE", { status: 200 })),
  );
  show();
  fireEvent.click(screen.getByRole("button", { name: "تحميل قائمة المتابعة" }));
  fireEvent.click(await screen.findByRole("button", { name: "إزالة BTC-USDT" }));
  fireEvent.click(screen.getByRole("button", { name: "تأكيد الإزالة" }));
  expect(await screen.findByRole("alert")).toBeVisible();
  expect(screen.queryByText("أُزيل العنصر من قائمة المتابعة.")).not.toBeInTheDocument();
});
