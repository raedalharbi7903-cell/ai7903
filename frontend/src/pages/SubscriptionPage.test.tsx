import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { expect, it, vi } from "vitest";
import { App } from "../app/App";
import { subscription, billingItem, billingPage } from "../test/billing";
function show() {
  return render(
    <MemoryRouter initialEntries={["/subscription"]}>
      <App />
    </MemoryRouter>,
  );
}
it("does not fetch, quote a price, charge or invent an account on mount", () => {
  const fetch = vi.fn();
  vi.stubGlobal("fetch", fetch);
  show();
  expect(fetch).not.toHaveBeenCalled();
  expect(
    screen.getByRole("complementary", { name: "حدود خدمة الاشتراك" }),
  ).toHaveTextContent("السعر النهائي لم يُعتمد");
  expect(screen.queryByText(/169/)).not.toBeInTheDocument();
  expect(
    screen.queryByRole("button", { name: /ادفع|اشترك الآن/ }),
  ).not.toBeInTheDocument();
});
it("shows loading then server-recorded access only after successful read", async () => {
  let finish!: (r: Response) => void;
  vi.stubGlobal(
    "fetch",
    vi.fn(
      () =>
        new Promise<Response>((done) => {
          finish = done;
        }),
    ),
  );
  show();
  fireEvent.click(screen.getByRole("button", { name: "تحميل حالة الاشتراك" }));
  expect(screen.getByRole("status")).toHaveTextContent("جارٍ تنفيذ");
  expect(
    screen.queryByRole("region", { name: "حالة الاشتراك" }),
  ).not.toBeInTheDocument();
  finish(new Response(JSON.stringify(subscription)));
  expect(
    await screen.findByRole("region", { name: "حالة الاشتراك" }),
  ).toHaveTextContent("فترة مدفوعة سارية");
});
it("requires cancellation confirmation, preserves recorded paid end and never promises a provider call", async () => {
  const fetch = vi
    .fn<typeof globalThis.fetch>()
    .mockResolvedValueOnce(new Response(JSON.stringify(subscription)))
    .mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          ...subscription,
          cancel_at_period_end: true,
          renewal_consent: false,
        }),
      ),
    );
  vi.stubGlobal("fetch", fetch);
  show();
  fireEvent.click(screen.getByRole("button", { name: "تحميل حالة الاشتراك" }));
  fireEvent.click(await screen.findByRole("button", { name: "طلب إيقاف التجديد" }));
  fireEvent.click(screen.getByRole("button", { name: "رجوع" }));
  expect(fetch).toHaveBeenCalledTimes(1);
  fireEvent.click(screen.getByRole("button", { name: "طلب إيقاف التجديد" }));
  fireEvent.click(screen.getByRole("button", { name: "تأكيد إيقاف التجديد" }));
  expect(await screen.findByText(/سُجّل طلب إيقاف التجديد محلياً/)).toBeVisible();
  expect(screen.getByRole("region", { name: "حالة الاشتراك" })).toHaveTextContent(
    "لا يُختصر",
  );
  expect(
    screen
      .getByRole("region", { name: "حالة الاشتراك" })
      .querySelector(`time[datetime="${subscription.paid_period_end}"]`),
  ).not.toBeNull();
  expect(fetch.mock.calls[1][1]?.body).toBe("{}");
  expect(String(fetch.mock.calls[1][0])).toMatch(/\/billing\/subscription\/cancel$/);
});
it.each([401, 403, 404, 409, 500, 503])(
  "clears private state on%s without exposing provider/internal text",
  async (status) => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(new Response(JSON.stringify(subscription)))
        .mockResolvedValueOnce(new Response("PRIVATE_BILLING_SECRET", { status })),
    );
    show();
    fireEvent.click(screen.getByRole("button", { name: "تحميل حالة الاشتراك" }));
    await screen.findByRole("region", { name: "حالة الاشتراك" });
    fireEvent.click(screen.getByRole("button", { name: "تحميل حالة الاشتراك" }));
    expect(await screen.findByRole("alert")).toBeVisible();
    expect(
      screen.queryByRole("region", { name: "حالة الاشتراك" }),
    ).not.toBeInTheDocument();
    expect(screen.queryByText(/PRIVATE_BILLING_SECRET/)).not.toBeInTheDocument();
  },
);
it("does not claim recorded cancellation if the response fails to confirm it", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => new Response(JSON.stringify(subscription))),
  );
  show();
  fireEvent.click(screen.getByRole("button", { name: "تحميل حالة الاشتراك" }));
  fireEvent.click(await screen.findByRole("button", { name: "طلب إيقاف التجديد" }));
  fireEvent.click(screen.getByRole("button", { name: "تأكيد إيقاف التجديد" }));
  expect(await screen.findByRole("alert")).toBeVisible();
  expect(screen.queryByText(/سُجّل طلب/)).not.toBeInTheDocument();
});
it("lists exact minor-unit event amounts, handles empty pages and uses validated cursor", async () => {
  const fetch = vi
    .fn<typeof globalThis.fetch>()
    .mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          ...billingPage(),
          next_cursor: { id: billingItem.id, created_at: billingItem.recorded_at },
        }),
      ),
    )
    .mockResolvedValueOnce(
      new Response(JSON.stringify({ ...billingPage(), items: [] })),
    );
  vi.stubGlobal("fetch", fetch);
  show();
  fireEvent.click(screen.getByRole("button", { name: "تحميل سجل الفوترة" }));
  expect(
    await screen.findByRole("region", { name: "أحداث الفوترة" }),
  ).toHaveTextContent("12345 SAR");
  expect(screen.getByText(/ليس فاتورة ضريبية/)).toBeVisible();
  fireEvent.click(screen.getByRole("button", { name: "صفحة الفوترة التالية" }));
  expect(await screen.findByText("لا توجد أحداث متاحة في هذه الصفحة.")).toBeVisible();
  expect(
    new URL(String(fetch.mock.calls[1][0]), "https://frontend.test").searchParams.get(
      "before_created_at",
    ),
  ).toBe(billingItem.recorded_at);
});
