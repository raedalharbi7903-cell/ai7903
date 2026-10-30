import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AnalysisResults, decisionLabels } from "./AnalysisResults";
import { decisions, parseAnalysisResult } from "../../types/analysis";
import { syntheticResult } from "../../test/results";
import { createFixture } from "./fixture";

describe("analysis contracts and display", () => {
  it("identifies contextual findings as non-directional observations", () => {
    const result = syntheticResult();
    result.outputs[1].evidence.push({
      evidence_id: "context-test",
      source_engine: "market_context",
      family: "context",
      finding: "context is bullish",
      bias: null,
      independent: true,
      provenance: { provider: "synthetic-unit-test", fixture: "True" },
    });
    render(<AnalysisResults result={result} />);
    expect(screen.getByText(/ملاحظة غير اتجاهية/)).toBeVisible();
    expect(screen.getByText(/context is bullish/)).toBeVisible();
  });
  it.each(decisions)("renders %s without inventing confidence", (decision) => {
    render(<AnalysisResults result={syntheticResult(decision)} />);
    expect(
      screen.getByRole("heading", { name: decisionLabels[decision] }),
    ).toBeVisible();
    expect(screen.getByText("غير مُعاير")).toBeVisible();
    expect(screen.getByText(/ليست احتمالًا لتحقيق الربح/)).toBeVisible();
    expect(screen.queryByText(/\d+%/)).not.toBeInTheDocument();
  });
  it("withholds rejected risk and displays provenance and missing data", () => {
    const result = syntheticResult("buy");
    result.validation = "fail";
    result.outputs.push({
      engine_name: "risk",
      status: "failed",
      evidence: [],
      warnings: ["Risk rejected"],
      data: { stop_loss: 912345 },
    });
    render(<AnalysisResults result={result} />);
    const risk = screen.getByRole("region", { name: "المخاطر والتحقق" });
    expect(within(risk).getByText(/حُجبت مستويات المخاطر/)).toBeVisible();
    expect(screen.queryByText("912345")).not.toBeInTheDocument();
    expect(screen.getByText("synthetic-unit-test")).toBeVisible();
    expect(screen.getByText("لا تتوفر نتائج تحليل متقدم.")).toBeVisible();
    expect(screen.getByText("Risk rejected")).toBeVisible();
  });
  it("renders advanced classifications and family attribution", () => {
    const result = syntheticResult();
    result.advanced_findings.push({
      engine_id: "momentum_divergence",
      status: "completed",
      classification: "hidden_bullish_divergence",
      direction: "bullish",
      family: "momentum",
      details: { momentum_method: "one_period_close_difference" },
      provenance: {},
      warnings: [],
    });
    render(<AnalysisResults result={result} />);
    expect(screen.getByText("تباعد صاعد خفي")).toBeVisible();
    expect(screen.getByText(/عائلة الزخم/)).toBeVisible();
  });
  it("rejects incompatible or malformed responses", () => {
    expect(parseAnalysisResult(syntheticResult())).toEqual(syntheticResult());
    for (const value of [
      null,
      {},
      { ...syntheticResult(), contract_version: "2.0" },
      { ...syntheticResult(), decision: "certain_profit" },
      { ...syntheticResult(), outputs: [{}] },
    ]) {
      expect(() => parseAnalysisResult(value)).toThrow(/incompatible/);
    }
  });
  it.each(["1h", "4h", "1d"] as const)(
    "generates honest %s fixture timestamps",
    (frame) => {
      const request = createFixture("TEST-USDT", frame);
      const hours = { "1h": 1, "4h": 4, "1d": 24 }[frame];
      expect(
        Date.parse(request.market_data.candles[1].timestamp) -
          Date.parse(request.market_data.candles[0].timestamp),
      ).toBe(hours * 3600000);
      expect(request.market_data.fixture).toBe(true);
      expect(request.metadata.timeframes).toEqual({});
    },
  );
});
