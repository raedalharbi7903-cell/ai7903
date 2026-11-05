import { expect, it } from "vitest";
import { parseBillingHistory, parseSubscription, subscriptionStates } from "./billing";
import { billingItem, billingPage, subscription } from "../test/billing";

it.each(subscriptionStates)(
  "reads recorded state %s without inferring payment",
  (state) => {
    const value = {
      ...subscription,
      state,
      entitled: state === "active",
      review_required: state === "review_required",
      ...(state === "none" ? { paid_period_start: null, paid_period_end: null } : {}),
    };
    expect(parseSubscription(value).state).toBe(state);
  },
);
it.each([
  { plan: "annual" },
  { plan: "trial" },
  { entitled: "true" },
  { contract_version: "2.0" },
  { paid_period_end: "2026-11-01T00:00:00Z" },
  { paid_period_start: null },
  { state: "expired", entitled: true },
  { state: "review_required", review_required: false },
  { paid_period_start: "2026-02-30T00:00:00Z" },
])("rejects unsafe subscription %j", (change) => {
  expect(() => parseSubscription({ ...subscription, ...change })).toThrow();
});
it("retains exact signed64bit money strings without JavaScript number conversion", () => {
  const page = parseBillingHistory({
    ...billingPage(),
    items: [{ ...billingItem, amount_minor: "9223372036854775807" }],
  });
  expect(page.items[0].amount_minor).toBe("9223372036854775807");
});
it.each([12345, true, "0", "-1", "01", "1.5", "1e3", "9223372036854775808", "NaN"])(
  "rejects inexact/noncanonical amount %s",
  (amount) => {
    expect(() =>
      parseBillingHistory({
        ...billingPage(),
        items: [{ ...billingItem, amount_minor: amount }],
      }),
    ).toThrow();
  },
);
it("rejects missing paid money and corrupt page metadata", () => {
  for (const value of [
    { ...billingPage(), items: [{ ...billingItem, amount_minor: null }] },
    { ...billingPage(), items: [{ ...billingItem, currency: null }] },
    {
      ...billingPage(),
      items: [{ ...billingItem, recorded_at: "2026-11-31T00:00:00Z" }],
    },
    { ...billingPage(), items: [billingItem, billingItem] },
    {
      ...billingPage(),
      next_cursor: { id: billingItem.id, created_at: "2026-11-02T00:00:00Z" },
    },
  ])
    expect(() => parseBillingHistory(value)).toThrow();
});
it("accepts unknown-money failure events without replacing missing money with zero", () => {
  const result = parseBillingHistory({
    ...billingPage(),
    items: [
      { ...billingItem, kind: "payment_failed", amount_minor: null, currency: null },
    ],
  });
  expect(result.items[0].amount_minor).toBeNull();
});

it.each(["active", "scheduled", "expired"])(
  "rejects %s without paid bounds",
  (state) => {
    expect(() =>
      parseSubscription({
        ...subscription,
        state,
        entitled: false,
        paid_period_start: null,
        paid_period_end: null,
      }),
    ).toThrow();
  },
);
it("accepts unresolved event review without inventing revocation of a confirmed paid window", () => {
  expect(
    parseSubscription({
      ...subscription,
      state: "review_required",
      review_required: true,
    }).entitled,
  ).toBe(true);
});
it.each([
  { amount_minor: null, currency: "SAR" },
  { amount_minor: "123", currency: null },
])("rejects one-sided money on nonpaid event %j", (money) => {
  expect(() =>
    parseBillingHistory({
      ...billingPage(),
      items: [
        {
          ...billingItem,
          kind: "payment_failed",
          ...money,
        },
      ],
    }),
  ).toThrow();
});
