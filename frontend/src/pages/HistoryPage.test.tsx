import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { expect, it, vi } from "vitest";
import { App } from "../app/App";
import { historyEntry, historyHeader, historyPage } from "../test/history";
import { requestHistoryEntry } from "../services/history";

function show() {
  return render(
    <MemoryRouter initialEntries={["/history"]}>
      <App />
    </MemoryRouter>,
  );
}
it("loads only on request, shows loading and opens an existing result without analysis", async () => {
  let finish!: (response: Response) => void;
  const fetch = vi
    .fn()
    .mockImplementationOnce(
      () =>
        new Promise<Response>((resolve) => {
          finish = resolve;
        }),
    )
    .mockResolvedValueOnce(new Response(JSON.stringify(historyEntry())));
  vi.stubGlobal("fetch", fetch);
  show();
  expect(fetch).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole("button", { name: "تحميل السجل" }));
  expect(screen.getByRole("status")).toHaveTextContent("جارٍ قراءة السجل");
  expect(screen.getByRole("button", { name: "تحميل السجل" })).toBeDisabled();
  finish(new Response(JSON.stringify(historyPage())));
  const open = await screen.findByRole("button", { name: /^فتح السجل / });
  fireEvent.click(open);
  expect(await screen.findByRole("region", { name: "نتيجة محفوظة" })).toBeVisible();
  expect(screen.getByRole("heading", { name: "انتظار" })).toBeVisible();
  expect(fetch).toHaveBeenCalledTimes(2);
  expect(fetch.mock.calls.every(([, init]) => init.method === "GET")).toBe(true);
  expect(fetch.mock.calls.every(([, init]) => init.credentials === "same-origin")).toBe(
    true,
  );
  fireEvent.click(screen.getByRole("button", { name: "العودة إلى القائمة" }));
  expect(screen.getByRole("region", { name: "السجلات المحفوظة" })).toBeVisible();
});
it.each([401, 403, 404, 503, 500])(
  "shows a safe %s error, never raw private response",
  async (status) => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response("PRIVATE_SESSION_SECRET", { status })),
    );
    show();
    fireEvent.click(screen.getByRole("button", { name: "تحميل السجل" }));
    expect(await screen.findByRole("alert")).toBeVisible();
    expect(screen.queryByText(/PRIVATE_SESSION_SECRET/)).not.toBeInTheDocument();
    expect(
      screen.queryByRole("region", { name: "السجلات المحفوظة" }),
    ).not.toBeInTheDocument();
  },
);
it("shows empty history without inventing a saved result", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(
      async () =>
        new Response(
          JSON.stringify({
            contract_version: "1.0",
            items: [],
            next_cursor: null,
          }),
        ),
    ),
  );
  show();
  fireEvent.click(screen.getByRole("button", { name: "تحميل السجل" }));
  expect(await screen.findByText("لا توجد سجلات متاحة في هذه الصفحة.")).toBeVisible();
});
it("uses validated cursor fields for pagination", async () => {
  const fetch = vi
    .fn()
    .mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          ...historyPage(),
          next_cursor: { id: historyHeader.id, created_at: historyHeader.created_at },
        }),
      ),
    )
    .mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          contract_version: "1.0",
          items: [],
          next_cursor: null,
        }),
      ),
    );
  vi.stubGlobal("fetch", fetch);
  show();
  fireEvent.click(screen.getByRole("button", { name: "تحميل السجل" }));
  fireEvent.click(await screen.findByRole("button", { name: "الصفحة التالية" }));
  expect(await screen.findByText("لا توجد سجلات متاحة في هذه الصفحة.")).toBeVisible();
  expect(
    new URL(fetch.mock.calls[1][0], "https://test.invalid").searchParams.get(
      "before_id",
    ),
  ).toBe(historyHeader.id);
});
it("forgets loaded private records when a later request loses authorization", async () => {
  const fetch = vi
    .fn()
    .mockResolvedValueOnce(new Response(JSON.stringify(historyPage())))
    .mockResolvedValueOnce(new Response("PRIVATE", { status: 401 }));
  vi.stubGlobal("fetch", fetch);
  show();
  fireEvent.click(screen.getByRole("button", { name: "تحميل السجل" }));
  await screen.findByRole("button", { name: /^فتح السجل / });
  fireEvent.click(screen.getByRole("button", { name: "تحميل السجل" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("يلزم تسجيل دخول موثوق");
  expect(screen.queryByRole("button", { name: /^فتح السجل / })).not.toBeInTheDocument();
});
it("cancels the actual pending signal on unmount", () => {
  let pending: AbortSignal | undefined;
  vi.stubGlobal(
    "fetch",
    vi.fn((_, init) => {
      pending = init.signal;
      return new Promise<Response>(() => {});
    }),
  );
  const view = show();
  fireEvent.click(screen.getByRole("button", { name: "تحميل السجل" }));
  expect(pending?.aborted).toBe(false);
  view.unmount();
  expect(pending?.aborted).toBe(true);
});
it("blocks unsafe resource identifiers without performing a request", async () => {
  const fetch = vi.fn();
  vi.stubGlobal("fetch", fetch);
  await expect(requestHistoryEntry("../foreign")).rejects.toThrow();
  expect(fetch).not.toHaveBeenCalled();
});

it("rejects a valid-looking response for a different requested record", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => new Response(JSON.stringify(historyEntry()))),
  );
  await expect(
    requestHistoryEntry("00000000-0000-4000-8000-000000000002"),
  ).rejects.toThrow("تعذّر التحقق");
});

it("requires explicit confirmation and waits for delete completion before success", async () => {
  let finish!: (response: Response) => void;
  const fetch = vi
    .fn()
    .mockResolvedValueOnce(new Response(JSON.stringify(historyPage())))
    .mockResolvedValueOnce(new Response(JSON.stringify(historyEntry())))
    .mockImplementationOnce(
      () =>
        new Promise<Response>((resolve) => {
          finish = resolve;
        }),
    );
  vi.stubGlobal("fetch", fetch);
  show();
  fireEvent.click(screen.getByRole("button", { name: "تحميل السجل" }));
  fireEvent.click(await screen.findByRole("button", { name: /^فتح السجل / }));
  await screen.findByRole("region", { name: "نتيجة محفوظة" });
  fireEvent.click(screen.getByRole("button", { name: "حذف النتيجة المحفوظة" }));
  expect(fetch).toHaveBeenCalledTimes(2);
  fireEvent.click(screen.getByRole("button", { name: "إلغاء" }));
  expect(fetch).toHaveBeenCalledTimes(2);
  fireEvent.click(screen.getByRole("button", { name: "حذف النتيجة المحفوظة" }));
  fireEvent.click(screen.getByRole("button", { name: "تأكيد الحذف" }));
  expect(screen.getByRole("status")).toHaveTextContent("جارٍ حذف السجل");
  expect(screen.queryByText("حُذفت النتيجة المحفوظة.")).not.toBeInTheDocument();
  finish(new Response(null, { status: 204 }));
  expect(await screen.findByText("حُذفت النتيجة المحفوظة.")).toBeVisible();
  expect(
    screen.queryByRole("region", { name: "نتيجة محفوظة" }),
  ).not.toBeInTheDocument();
  expect(fetch.mock.calls[2][1].method).toBe("DELETE");
});

it.each([500, 503, 200])(
  "never claims deletion on failed/incompatible %s response",
  async (status) => {
    const fetch = vi
      .fn()
      .mockResolvedValueOnce(new Response(JSON.stringify(historyPage())))
      .mockResolvedValueOnce(new Response(JSON.stringify(historyEntry())))
      .mockResolvedValueOnce(new Response("PRIVATE_AUDIT_SECRET", { status }));
    vi.stubGlobal("fetch", fetch);
    show();
    fireEvent.click(screen.getByRole("button", { name: "تحميل السجل" }));
    fireEvent.click(await screen.findByRole("button", { name: /^فتح السجل / }));
    await screen.findByRole("region", { name: "نتيجة محفوظة" });
    fireEvent.click(screen.getByRole("button", { name: "حذف النتيجة المحفوظة" }));
    fireEvent.click(screen.getByRole("button", { name: "تأكيد الحذف" }));
    expect(await screen.findByRole("alert")).toBeVisible();
    expect(screen.queryByText(/PRIVATE_AUDIT_SECRET/)).not.toBeInTheDocument();
    expect(screen.queryByText("حُذفت النتيجة المحفوظة.")).not.toBeInTheDocument();
  },
);

it("redacts native failures and malformed successful responses", async () => {
  const fetch = vi
    .fn()
    .mockRejectedValueOnce(new Error("PRIVATE_NETWORK_SECRET"))
    .mockResolvedValueOnce(new Response("{broken"));
  vi.stubGlobal("fetch", fetch);
  show();
  fireEvent.click(screen.getByRole("button", { name: "تحميل السجل" }));
  expect(await screen.findByRole("alert")).not.toHaveTextContent(
    "PRIVATE_NETWORK_SECRET",
  );
  fireEvent.click(screen.getByRole("button", { name: "تحميل السجل" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("تعذّر التحقق");
});
