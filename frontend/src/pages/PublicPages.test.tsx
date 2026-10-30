import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { describe, expect, it, vi } from "vitest";
import { App } from "../app/App";
import { ar } from "../i18n/ar";

describe("public Arabic guidance", () => {
  it.each([
    ["/welcome", "فهم منظم للتحليل الفني، مع حدود واضحة."],
    ["/product", "منهج التحليل وحدوده"],
    ["/help", "دليل استخدام النسخة التجريبية"],
  ])(
    "renders %s without automatic requests or invented live service",
    (route, title) => {
      const fetch = vi.fn();
      vi.stubGlobal("fetch", fetch);
      render(
        <MemoryRouter initialEntries={[route]}>
          <App />
        </MemoryRouter>,
      );
      expect(screen.getByRole("heading", { level: 1, name: title })).toBeVisible();
      expect(
        screen.getByRole("complementary", { name: "حدود النسخة الحالية" }),
      ).toHaveTextContent("ليست خدمة تحليل حي");
      expect(
        screen.getByRole("main").closest('[dir="rtl"]')?.getAttribute("lang"),
      ).toBe("ar");
      expect(screen.getByText(ar.designPending)).toBeVisible();
      expect(fetch).not.toHaveBeenCalled();
      expect(screen.queryByText(/169/)).not.toBeInTheDocument();
      expect(screen.queryByRole("textbox")).not.toBeInTheDocument();
    },
  );
  it("navigates to the actual existing analysis without starting it", () => {
    const fetch = vi.fn();
    vi.stubGlobal("fetch", fetch);
    render(
      <MemoryRouter initialEntries={["/welcome"]}>
        <App />
      </MemoryRouter>,
    );
    fireEvent.click(screen.getByRole("link", { name: "افتح التحليل التجريبي" }));
    expect(
      screen.getByRole("button", { name: "حلّل البيانات التجريبية" }),
    ).toBeVisible();
    expect(fetch).not.toHaveBeenCalled();
  });
  it("uses native accessible help disclosures instead of simulated support submission", () => {
    render(
      <MemoryRouter initialEntries={["/help"]}>
        <App />
      </MemoryRouter>,
    );
    const question = screen.getByText("هل توجد حسابات أو فواتير أو تذاكر دعم الآن؟");
    expect(question.closest("details")).not.toBeNull();
    expect(screen.queryByRole("button", { name: /إرسال/ })).not.toBeInTheDocument();
  });
});
