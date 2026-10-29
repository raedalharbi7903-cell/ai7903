import { parseAnalysisResult } from "../types/analysis";
import type { AnalysisRequest, AnalysisResult } from "../types/analysis";
const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";
export async function requestAnalysis(
  payload: AnalysisRequest,
  signal?: AbortSignal,
): Promise<AnalysisResult> {
  const response = await fetch(`${baseUrl}/analysis`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal: signal ?? AbortSignal.timeout(30_000),
  });
  if (!response.ok) {
    const message =
      response.status === 422
        ? "The fixture or analysis settings were rejected. Check the pair and timeframe."
        : response.status === 503
          ? "Live data is unavailable. Only explicitly labeled fixtures are supported."
          : "Analysis is unavailable. Please retry.";
    throw new Error(message);
  }
  return parseAnalysisResult(await response.json());
}
