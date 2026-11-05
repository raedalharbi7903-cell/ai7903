import { parseHistoryPage, validAwareTimestamp } from "./history";
import type { HistoryCursor } from "./history";

export const subscriptionStates = [
  "none",
  "active",
  "scheduled",
  "expired",
  "review_required",
] as const;
export interface SubscriptionSummary {
  contract_version: "1.0";
  plan: "monthly";
  state: (typeof subscriptionStates)[number];
  entitled: boolean;
  paid_period_start: string | null;
  paid_period_end: string | null;
  cancel_at_period_end: boolean;
  renewal_consent: boolean;
  review_required: boolean;
}
export interface BillingHistoryItem {
  id: string;
  kind: string;
  amount_minor: string | null;
  currency: string | null;
  recorded_at: string;
  retained_until: string;
  processing_status: "applied" | "review_required";
}
export interface BillingHistoryPage {
  contract_version: "1.0";
  items: BillingHistoryItem[];
  next_cursor: HistoryCursor | null;
}
function record(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
export function parseSubscription(value: unknown): SubscriptionSummary {
  if (
    !record(value) ||
    value.contract_version !== "1.0" ||
    value.plan !== "monthly" ||
    !subscriptionStates.some((state) => state === value.state) ||
    ["entitled", "cancel_at_period_end", "renewal_consent", "review_required"].some(
      (key) => typeof value[key] !== "boolean",
    )
  ) {
    throw new Error("Invalid subscription response");
  }
  const empty = value.paid_period_start === null && value.paid_period_end === null;
  if (
    !empty &&
    (!validAwareTimestamp(value.paid_period_start) ||
      !validAwareTimestamp(value.paid_period_end) ||
      Date.parse(value.paid_period_end) <= Date.parse(value.paid_period_start))
  )
    throw new Error("Invalid paid window");
  if (
    (value.entitled &&
      (empty || (value.state !== "active" && value.state !== "review_required"))) ||
    (value.state === "active" && !value.entitled) ||
    (empty && ["active", "scheduled", "expired"].includes(value.state as string)) ||
    (value.state === "none" && (!empty || value.entitled)) ||
    (value.state === "review_required") !== value.review_required
  )
    throw new Error("Inconsistent subscription state");
  return {
    contract_version: "1.0",
    plan: "monthly",
    state: value.state as SubscriptionSummary["state"],
    entitled: value.entitled as boolean,
    paid_period_start: value.paid_period_start as string | null,
    paid_period_end: value.paid_period_end as string | null,
    cancel_at_period_end: value.cancel_at_period_end as boolean,
    renewal_consent: value.renewal_consent as boolean,
    review_required: value.review_required as boolean,
  };
}
export function parseBillingHistory(value: unknown): BillingHistoryPage {
  if (!record(value) || !Array.isArray(value.items))
    throw new Error("Invalid billing page");
  const rows = value.items;
  const metadata = parseHistoryPage({
    ...value,
    items: rows.map((row: unknown) =>
      record(row)
        ? {
            id: row.id,
            created_at: row.recorded_at,
            expires_at: row.retained_until,
          }
        : row,
    ),
  });
  const kinds = ["paid", "payment_failed", "refund", "dispute", "unsupported"];
  const items = metadata.items.map((item, index): BillingHistoryItem => {
    const row: unknown = rows[index];
    if (
      !record(row) ||
      !kinds.some((kind) => kind === row.kind) ||
      (row.processing_status !== "applied" &&
        row.processing_status !== "review_required") ||
      (row.amount_minor === null) !== (row.currency === null) ||
      (row.amount_minor !== null &&
        (typeof row.amount_minor !== "string" ||
          !/^[1-9][0-9]{0,18}$/.test(row.amount_minor) ||
          BigInt(row.amount_minor) > 9223372036854775807n)) ||
      (row.currency !== null &&
        (typeof row.currency !== "string" || !/^[A-Z]{3}$/.test(row.currency)))
    )
      throw new Error("Invalid billing entry");
    if (row.kind === "paid" && (row.amount_minor === null || row.currency === null))
      throw new Error("Missing paid-event amount");
    return {
      id: item.id,
      kind: row.kind as string,
      amount_minor: row.amount_minor as string | null,
      currency: row.currency as string | null,
      recorded_at: item.created_at,
      retained_until: item.expires_at,
      processing_status: row.processing_status,
    };
  });
  return { ...metadata, items };
}
