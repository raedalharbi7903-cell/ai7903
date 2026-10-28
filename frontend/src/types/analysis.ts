export type Decision = "buy" | "sell" | "no_trade" | "wait" | "insufficient_data";
export interface AdvancedFinding { engine_id: string; classification: string | null; direction: string | null; family: string | null; details: Record<string, unknown>; warnings: string[]; }
export interface AnalysisResult { decision: Decision; validation: string; generated_at: string; outputs: Array<{engine_name: string; data: Record<string, unknown>; warnings: string[]}>; advanced_findings: AdvancedFinding[]; }
