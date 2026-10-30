import { parseAnalysisResult } from "../types/analysis";
import type { AnalysisRequest, AnalysisResult } from "../types/analysis";
import { ar } from "../i18n/ar";
import { requestJson } from "./http";

export { ApiClientError as AnalysisClientError } from "./http";

export function requestAnalysis(
  payload: AnalysisRequest,
  signal?: AbortSignal,
): Promise<AnalysisResult> {
  return requestJson(
    "/analysis",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal,
    },
    parseAnalysisResult,
    {
      unavailable: ar.unavailable,
      invalidResponse: ar.invalidResponse,
      statuses: { 422: ar.invalidRequest, 503: ar.providerUnavailable },
    },
  );
}
