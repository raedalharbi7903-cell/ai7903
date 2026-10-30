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
  if (typeof value !== "string") return false;
  const match =
    /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(?:Z|[+-](\d{2}):(\d{2}))$/.exec(
      value,
    );
  if (!match) return false;
  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);
  const hour = Number(match[4]);
  const minute = Number(match[5]);
  const second = Number(match[6]);
  const offsetHour = Number(match[7] ?? 0);
  const offsetMinute = Number(match[8] ?? 0);
  const leapYear = year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
  const monthDays = [31, leapYear ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  // Date.parse normalizes impossible days and 24:00 instead of rejecting them.
  // Match the backend datetime calendar before relying on its ISO parser.
  return (
    year >= 1 &&
    month >= 1 &&
    month <= 12 &&
    day >= 1 &&
    day <= (monthDays[month - 1] ?? 0) &&
    hour < 24 &&
    minute < 60 &&
    second < 60 &&
    offsetHour < 24 &&
    offsetMinute < 60 &&
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
