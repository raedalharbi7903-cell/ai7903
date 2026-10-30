import { parseAnalysisResult } from "./analysis";
import type { AnalysisResult } from "./analysis";

export interface HistoryHeader {
  id: string;
  created_at: string;
  expires_at: string;
}
export interface HistoryCursor {
  id: string;
  created_at: string;
}
export interface HistoryPage {
  contract_version: "1.0";
  items: HistoryHeader[];
  next_cursor: HistoryCursor | null;
}
export interface HistoryEntry extends HistoryHeader {
  result: AnalysisResult;
}

export function validHistoryId(value: unknown): value is string {
  return (
    typeof value === "string" &&
    /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(value)
  );
}
function record(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}
function awareDate(value: unknown): value is string {
  return (
    typeof value === "string" &&
    /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/.test(
      value,
    ) &&
    Number.isFinite(Date.parse(value))
  );
}
function header(value: unknown): HistoryHeader {
  if (
    !record(value) ||
    !validHistoryId(value.id) ||
    !awareDate(value.created_at) ||
    !awareDate(value.expires_at) ||
    Date.parse(value.expires_at) <= Date.parse(value.created_at)
  ) {
    throw new Error("Invalid history header");
  }
  return { id: value.id, created_at: value.created_at, expires_at: value.expires_at };
}
export function parseHistoryPage(value: unknown): HistoryPage {
  if (
    !record(value) ||
    value.contract_version !== "1.0" ||
    !Array.isArray(value.items) ||
    value.items.length > 100
  ) {
    throw new Error("Invalid history page");
  }
  const items = value.items.map(header);
  if (new Set(items.map((item) => item.id.toLowerCase())).size !== items.length) {
    throw new Error("Duplicate history entry");
  }
  let next: HistoryCursor | null = null;
  if (value.next_cursor !== null) {
    const cursor = value.next_cursor;
    const last = items.at(-1);
    if (
      !record(cursor) ||
      !validHistoryId(cursor.id) ||
      !awareDate(cursor.created_at) ||
      !last ||
      cursor.id !== last.id ||
      cursor.created_at !== last.created_at
    ) {
      throw new Error("Invalid history cursor");
    }
    next = { id: cursor.id, created_at: cursor.created_at };
  }
  return { contract_version: "1.0", items, next_cursor: next };
}
export function parseHistoryEntry(value: unknown): HistoryEntry {
  const item = header(value);
  if (!record(value)) throw new Error("Invalid history entry");
  return { ...item, result: parseAnalysisResult(value.result) };
}
