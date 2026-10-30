import { describe, expect, it } from "vitest";
import { analysisLabel, analysisValue, ar, formatUtcTimestamp } from "./ar";

describe("Arabic analysis semantics", () => {
  it.each([
    ["buy", "شراء"],
    ["sell", "بيع"],
    ["no_trade", "لا تداول"],
    ["wait", "انتظار"],
    ["insufficient_data", "بيانات غير كافية"],
  ])("preserves decision %s as its Arabic label", (key, expected) => {
    expect(analysisLabel(key)).toBe(expected);
  });

  it("does not translate or alter provenance identifiers as confidence labels", () => {
    expect(analysisValue("provider", "high")).toBe("high");
    expect(analysisValue("instrument", "TEST-USDT")).toBe("TEST-USDT");
    expect(analysisValue("confidence", "high")).toBe("مرتفع");
    expect(analysisValue("calibration", "uncalibrated")).toBe("غير مُعاير");
    expect(analysisValue("fixture", true)).toBe("نعم");
  });

  it("withholds absent, nonfinite and unsupported numerical confidence", () => {
    expect(analysisValue("target", null)).toBe(ar.notAvailable);
    expect(analysisValue("target", Number.NaN)).toBe(ar.notAvailable);
    expect(analysisValue("confidence", "99%")).toBe(ar.notAvailable);
    expect(analysisValue("confidence", 0.99)).toBe(ar.notAvailable);
  });

  it("normalizes aware timestamps without inventing a timezone for naive values", () => {
    expect(formatUtcTimestamp("2026-01-01T03:00:00+03:00")).toBe(
      "2026-01-01T00:00:00.000Z (UTC)",
    );
    expect(formatUtcTimestamp("2026-01-01T00:00:00")).toBe(ar.notAvailable);
    expect(formatUtcTimestamp("not-a-date")).toBe(ar.notAvailable);
  });
});
