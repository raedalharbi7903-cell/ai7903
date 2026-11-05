import type { SubscriptionSummary } from "../types/billing";
export const subscription: SubscriptionSummary = {
  contract_version: "1.0",
  plan: "monthly",
  state: "active",
  entitled: true,
  paid_period_start: "2026-11-01T00:00:00Z",
  paid_period_end: "2026-12-01T00:00:00Z",
  cancel_at_period_end: false,
  renewal_consent: true,
  review_required: false,
};
export const billingItem = {
  id: "00000000-0000-4000-8000-000000000001",
  kind: "paid",
  amount_minor: "12345",
  currency: "SAR",
  recorded_at: "2026-11-01T00:01:00Z",
  retained_until: "2027-01-01T00:00:00Z",
  processing_status: "applied",
};
export function billingPage() {
  return { contract_version: "1.0", items: [{ ...billingItem }], next_cursor: null };
}
