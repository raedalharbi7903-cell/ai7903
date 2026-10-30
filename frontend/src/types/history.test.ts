import { describe, expect, it } from "vitest";
import { parseHistoryEntry, parseHistoryPage } from "./history";
import { historyEntry, historyHeader, historyPage } from "../test/history";

describe("private history contracts", () => {
  it("parses metadata pages and full saved results separately", () => {
    expect(parseHistoryPage(historyPage())).toEqual(historyPage());
    expect(parseHistoryEntry(historyEntry()).result.decision).toBe("wait");
    expect(parseHistoryPage(historyPage()).items[0]).not.toHaveProperty("result");
  });
  it.each([
    null,
    {},
    { ...historyPage(), contract_version: "2.0" },
    { ...historyPage(), items: [historyHeader, historyHeader] },
    { ...historyPage(), items: Array(101).fill(historyHeader) },
    { ...historyPage(), items: [{ ...historyHeader, id: "../other-owner" }] },
    {
      ...historyPage(),
      items: [{ ...historyHeader, created_at: "2026-01-01T00:00:00" }],
    },
    {
      ...historyPage(),
      items: [{ ...historyHeader, expires_at: historyHeader.created_at }],
    },
    {
      ...historyPage(),
      next_cursor: { id: "wrong", created_at: historyHeader.created_at },
    },
    {
      ...historyPage(),
      next_cursor: { id: historyHeader.id, created_at: "2025-01-01T00:00:00Z" },
    },
  ])(
    "rejects incompatible, duplicate, naive, unsafe or mismatched page %j",
    (value) => {
      expect(() => parseHistoryPage(value)).toThrow();
    },
  );
  it("rejects a saved entry with incompatible analysis rather than fabricating a result", () => {
    expect(() => parseHistoryEntry({ ...historyEntry(), result: {} })).toThrow();
  });
});
