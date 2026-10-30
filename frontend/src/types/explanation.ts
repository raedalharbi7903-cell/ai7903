import type { AnalysisResult } from "./analysis";

export interface ArabicExplanation {
  summary: string;
  limitations: string[];
}

export function readArabicExplanation(
  result: AnalysisResult,
): ArabicExplanation | undefined {
  const raw = result.outputs.find((output) => output.engine_name === "explainability")
    ?.data.arabic_explanation;
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return undefined;
  const value = raw as Record<string, unknown>;
  if (
    value.methodology_version !== "deterministic-ar-v1" ||
    value.language !== "ar" ||
    value.mode !== "deterministic_fallback" ||
    value.decision !== result.decision ||
    value.validation !== result.validation ||
    typeof value.summary !== "string" ||
    !value.summary.trim() ||
    !Array.isArray(value.limitations) ||
    !value.limitations.every((line) => typeof line === "string")
  )
    return undefined;
  return { summary: value.summary, limitations: value.limitations as string[] };
}
