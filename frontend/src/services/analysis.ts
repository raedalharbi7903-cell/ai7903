import { parseAnalysisResult } from "../types/analysis";
import type { AnalysisRequest, AnalysisResult } from "../types/analysis";
import { ar } from "../i18n/ar";
const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

export class AnalysisClientError extends Error {}

export async function requestAnalysis(
  payload: AnalysisRequest,
  signal?: AbortSignal,
): Promise<AnalysisResult> {
  let response: Response;
  try {
    response = await fetch(`${baseUrl}/analysis`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: signal ?? AbortSignal.timeout(30_000),
    });
  } catch {
    throw new AnalysisClientError(ar.unavailable);
  }
  if (!response.ok) {
    const message =
      response.status === 422
        ? ar.invalidRequest
        : response.status === 503
          ? ar.providerUnavailable
          : ar.unavailable;
    throw new AnalysisClientError(message);
  }
  try {
    return parseAnalysisResult(await response.json());
  } catch {
    throw new AnalysisClientError(ar.invalidResponse);
  }
}
