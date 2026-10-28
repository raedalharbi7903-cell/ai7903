import type { AnalysisResult } from "../types/analysis";
const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";
export async function requestAnalysis(payload: Record<string, unknown>): Promise<AnalysisResult> {
  const response = await fetch(`${baseUrl}/analysis`, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload)});
  if (!response.ok) throw new Error("Analysis is unavailable. Demo data may be required.");
  return response.json() as Promise<AnalysisResult>;
}
