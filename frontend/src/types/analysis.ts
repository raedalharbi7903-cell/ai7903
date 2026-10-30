export const decisions = [
  "buy",
  "sell",
  "no_trade",
  "wait",
  "insufficient_data",
] as const;
export type Decision = (typeof decisions)[number];
export type EngineStatus = "pending" | "running" | "completed" | "failed" | "degraded";
export type Validation = "pass" | "fail" | "degraded";
export const timeframes = ["1m", "5m", "15m", "1h", "4h", "1d"] as const;
export type Timeframe = (typeof timeframes)[number];
export interface Candle {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number | null;
  complete: boolean;
}
export interface FixtureData {
  instrument: string;
  market: "crypto";
  timeframe: Timeframe;
  provider: string;
  source_timestamp: string;
  fixture: true;
  candles: Candle[];
}
export interface AnalysisRequest {
  pair: string;
  timeframe: Timeframe;
  request_id: string;
  market_data: FixtureData;
  metadata: { timeframes: Partial<Record<"htf" | "itf" | "ltf", FixtureData>> };
}
export interface Evidence {
  evidence_id: string;
  source_engine: string;
  family: string;
  finding: string;
  bias: string | null;
  independent: boolean;
  provenance: Record<string, string>;
}
export interface EngineOutput {
  engine_name: string;
  status: EngineStatus;
  data: Record<string, unknown>;
  warnings: string[];
  evidence: Evidence[];
}
export interface AdvancedFinding {
  engine_id: string;
  status: EngineStatus;
  classification: string | null;
  direction: string | null;
  family: string | null;
  details: Record<string, unknown>;
  provenance: Record<string, string>;
  warnings: string[];
}
export interface AnalysisResult {
  contract_version: "1.0";
  status: EngineStatus;
  decision: Decision;
  validation: Validation;
  generated_at: string;
  outputs: EngineOutput[];
  advanced_findings: AdvancedFinding[];
}
function record(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
function strings(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((entry) => typeof entry === "string");
}
function stringMap(value: unknown): value is Record<string, string> {
  return (
    record(value) && Object.values(value).every((item) => typeof item === "string")
  );
}
const statuses = ["pending", "running", "completed", "failed", "degraded"];
function evidence(value: unknown): boolean {
  return (
    record(value) &&
    typeof value.evidence_id === "string" &&
    typeof value.source_engine === "string" &&
    typeof value.family === "string" &&
    typeof value.finding === "string" &&
    (value.bias === null || typeof value.bias === "string") &&
    typeof value.independent === "boolean" &&
    stringMap(value.provenance)
  );
}
export function parseAnalysisResult(value: unknown): AnalysisResult {
  if (
    !record(value) ||
    value.contract_version !== "1.0" ||
    !decisions.includes(value.decision as Decision) ||
    !statuses.includes(String(value.status)) ||
    !["pass", "fail", "degraded"].includes(String(value.validation)) ||
    typeof value.generated_at !== "string" ||
    !Number.isFinite(Date.parse(value.generated_at)) ||
    !Array.isArray(value.outputs) ||
    !Array.isArray(value.advanced_findings) ||
    !value.outputs.every(
      (item) =>
        record(item) &&
        typeof item.engine_name === "string" &&
        statuses.includes(String(item.status)) &&
        record(item.data) &&
        strings(item.warnings) &&
        Array.isArray(item.evidence) &&
        item.evidence.every(evidence),
    ) ||
    !value.advanced_findings.every(
      (item) =>
        record(item) &&
        typeof item.engine_id === "string" &&
        statuses.includes(String(item.status)) &&
        [item.classification, item.direction, item.family].every(
          (field) => field === null || typeof field === "string",
        ) &&
        record(item.details) &&
        stringMap(item.provenance) &&
        strings(item.warnings),
    )
  ) {
    throw new Error("The analysis response is incompatible or incomplete.");
  }
  return value as unknown as AnalysisResult;
}
