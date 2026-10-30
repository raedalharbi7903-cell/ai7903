/** Requirements: UI-APPROVAL. Final visual acceptance remains founder-gated. */
import { render, screen } from "@testing-library/react";
import { createElement } from "react";
import { MemoryRouter } from "react-router";
import { describe, expect, it } from "vitest";
import { Layout } from "../layouts/Layout";
import { visualApproval } from "./approval";

describe("visual approval boundary", () => {
  it("keeps all ten visual approval categories pending", () => {
    expect(visualApproval.status).toBe("pending");
    expect(visualApproval.approvalReference).toBeNull();
    expect(visualApproval.decisions).toHaveLength(10);
    expect(new Set(visualApproval.decisions).size).toBe(10);
  });

  it("identifies the current interface as provisional", () => {
    render(createElement(MemoryRouter, null, createElement(Layout)));
    expect(screen.getByText(/Visual design is provisional/)).toBeVisible();
    expect(
      screen.getByRole("link", { name: "Skip to analysis" }).getAttribute("href"),
    ).toBe("#content");
  });
});
