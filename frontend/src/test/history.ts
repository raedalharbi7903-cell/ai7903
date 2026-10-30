import { syntheticResult } from "./results";

export const historyHeader = {
  id: "00000000-0000-4000-8000-000000000001",
  created_at: "2026-01-01T00:00:00Z",
  expires_at: "2027-01-01T00:00:00Z",
};
export function historyPage() {
  return {
    contract_version: "1.0" as const,
    items: [{ ...historyHeader }],
    next_cursor: null,
  };
}
export function historyEntry() {
  return { ...historyHeader, result: syntheticResult("wait") };
}
