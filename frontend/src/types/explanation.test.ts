import { describe, expect, it } from "vitest";
import { readArabicExplanation } from "./explanation";
import { syntheticResult } from "../test/results";

function sample() {
  const result = syntheticResult();
  result.outputs.push({
    engine_name: "explainability",
    status: "completed",
    evidence: [],
    warnings: [],
    data: {
      arabic_explanation: {
        methodology_version: "deterministic-ar-v1",
        language: "ar",
        mode: "deterministic_fallback",
        decision: result.decision,
        validation: result.validation,
        summary: "لا تداول",
        limitations: ["البيانات مصطنعة"],
      },
    },
  });
  return result;
}

describe("grounded Arabic contract", () => {
  it("accepts matching versioned final-state explanation", () => {
    expect(readArabicExplanation(sample())).toEqual({
      summary: "لا تداول",
      limitations: ["البيانات مصطنعة"],
    });
  });
  it("fails closed for absent, malformed, unsupported or stale claims", () => {
    expect(readArabicExplanation(syntheticResult())).toBeUndefined();
    for (const change of [
      { decision: "buy" },
      { validation: "fail" },
      { summary: 42 },
      { summary: "" },
      { language: "en" },
      { mode: "live_ai" },
      { methodology_version: "future-v9" },
      { limitations: [42] },
    ]) {
      const result = sample();
      const output = result.outputs[result.outputs.length - 1];
      output.data.arabic_explanation = {
        ...(output.data.arabic_explanation as Record<string, unknown>),
        ...change,
      };
      expect(readArabicExplanation(result)).toBeUndefined();
    }
  });
});
