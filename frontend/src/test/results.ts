import type { AnalysisResult, Decision } from "../types/analysis";
export function syntheticResult(decision: Decision = "no_trade"): AnalysisResult {
  return {
    contract_version: "1.0",
    status: "completed",
    decision,
    validation: "pass",
    generated_at: "2026-01-01T08:00:00Z",
    advanced_findings: [],
    outputs: [
      {
        engine_name: "confidence",
        status: "completed",
        evidence: [],
        warnings: [],
        data: { confidence: "low", calibration: "uncalibrated" },
      },
      {
        engine_name: "data",
        status: "completed",
        evidence: [],
        warnings: [],
        data: { fixture: true, provider: "synthetic-unit-test", quality: "pass" },
      },
    ],
  };
}
