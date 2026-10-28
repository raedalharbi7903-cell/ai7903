export type Decision = "buy" | "sell" | "no_trade" | "wait" | "insufficient_data";
export interface AnalysisResult { decision: Decision; validation: string; generated_at: string; outputs: Array<{engine_name: string; data: Record<string, unknown>; warnings: string[]}>; }
