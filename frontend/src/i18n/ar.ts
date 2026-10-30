/** Arabic functional copy; visual identity, typography and final copy review pending. */
export const ar = {
  skip: "انتقل إلى المحتوى",
  navigation: "التنقل الرئيسي",
  workspace: "مساحة بحث تجريبية",
  footer: "أدلة حتمية، وعدم يقين واضح، ودون تنفيذ تلقائي للتداول.",
  designPending: "التصميم المرئي مؤقت وينتظر موافقة المؤسس.",
  category: "أصول رقمية / سوق فوري / بحث",
  heading: "افهم الأدلة وحدود التحليل.",
  introduction: "استعرض البنية والمخاطر والتعارضات دون افتراض اليقين.",
  demoLabel: "حدود الوضع التجريبي",
  demoTitle: "وضع تجريبي — بيانات اصطناعية فقط",
  demoDescription:
    "لا أسعار حية ولا بيانات سوق فعلية. اسم الزوج يعرّف مثالًا اصطناعيًا، ولا يمثل تاريخه الحقيقي. لا تُنسخ بيانات الإطار الأساسي لتبدو كتأكيد مستقل من أطر أخرى.",
  pair: "زوج الأصول",
  pairHint: "صيغة الزوج: TEST-USDT. الاسم يعرّف مثالًا اصطناعيًا فقط.",
  timeframe: "الإطار الزمني الأساسي",
  hour: "ساعة واحدة",
  fourHours: "أربع ساعات",
  day: "يوم واحد",
  analyze: "حلّل البيانات التجريبية",
  analyzing: "جارٍ التحليل…",
  progress: "جارٍ تنفيذ التحليل الحتمي…",
  ready: "مساحة التحليل جاهزة.",
  empty:
    "ابدأ بالمثال الاصطناعي المعلن لاستعراض الأدلة وفحوص السلامة والنتائج المتقدمة.",
  unavailable: "التحليل غير متاح حاليًا. حاول مجددًا.",
  invalidRequest: "رُفضت البيانات أو إعدادات التحليل. تحقّق من الزوج والإطار الزمني.",
  providerUnavailable:
    "التحليل غير متاح حاليًا. تدعم هذه الواجهة بيانات تجريبية معلنة فقط.",
  invalidResponse: "تعذّر التحقق من استجابة التحليل. لم تُعرض نتائج غير موثوقة.",
  missingPage: "الصفحة غير موجودة",
  returnToAnalysis: "العودة إلى التحليل",
  decision: "قرار التحليل",
  deterministic: "نتيجة التحليل الحتمي",
  validation: "التحقق",
  generated: "وقت إنشاء التحليل",
  contract: "إصدار العقد",
  notActionable: "هذه النتيجة ليست إعدادًا صالحًا لاتخاذ إجراء تداول.",
  spotOnly:
    "تحليل للسوق الفوري فقط. لا تُنفّذ أوامر؛ وقرار البيع لا يجيز فتح مركز بيع على المكشوف.",
  context: "سياق السوق",
  confidence: "الجودة التحليلية",
  confidenceNote: "جودة تحليلية وليست احتمالًا لتحقيق الربح.",
  calibrationNote: "لا تُدّعى نسبة نجاح مُعايرة أو درجة يقين مالي.",
  provenance: "جودة البيانات ومصدرها",
  mtf: "توافق الأطر الزمنية",
  advanced: "التحليل المتقدم",
  noAdvanced: "لا تتوفر نتائج تحليل متقدم.",
  family: "عائلة",
  contextual: "ملاحظة سياقية",
  evidence: "الأدلة والتوافق",
  independence: "تعدد الملاحظات في العائلة نفسها لا ينشئ أصواتًا مستقلة.",
  representative: "ممثل العائلة",
  shared: "عائلة مشتركة",
  nonDirectional: "ملاحظة غير اتجاهية",
  noEvidence: "لا تتوفر أدلة.",
  risk: "المخاطر والتحقق",
  withheldRisk: "حُجبت مستويات المخاطر لأن النتيجة ليست إعدادًا صالحًا اجتاز التحقق.",
  explanation: "تفسير النتيجة",
  noTrustedExplanation: "لا يتوفر شرح موثوق مطابق للنتيجة النهائية.",
  aiAvailability: "توفر التفسير المولّد بالذكاء الاصطناعي",
  warnings: "تحذيرات نقص التحليل",
  noWarnings: "لم تُبلّغ تحذيرات نقص.",
  notAvailable: "غير متاح",
  details: "التفاصيل التقنية",
} as const;

const tokens: Record<string, string> = {
  buy: "شراء",
  sell: "بيع",
  no_trade: "لا تداول",
  wait: "انتظار",
  insufficient_data: "بيانات غير كافية",
  completed: "مكتمل",
  failed: "فشل",
  degraded: "منقوص",
  pending: "قيد الانتظار",
  running: "قيد التنفيذ",
  pass: "اجتاز",
  fail: "لم يجتز",
  uncalibrated: "غير مُعاير",
  evaluation_pending: "التقييم معلّق",
  low: "منخفض",
  medium: "متوسط",
  high: "مرتفع",
  bullish: "صاعد",
  bearish: "هابط",
  neutral: "محايد",
  context: "السياق",
  structure: "البنية",
  trend: "الاتجاه",
  levels: "المستويات",
  zones: "المناطق",
  liquidity: "السيولة",
  volume: "الحجم",
  momentum: "الزخم",
  volatility: "التذبذب",
  pattern: "الأنماط",
  candlestick: "الشموع",
  timeframe: "الإطار الزمني",
  market_context: "سياق السوق",
  momentum_divergence: "تباعد الزخم",
  liquidity_sweep: "استدلال اجتياح السيولة",
  market_transition: "انتقال بنية السوق",
  volume_anomaly: "شذوذ الحجم",
  regular_bullish_divergence: "تباعد صاعد عادي",
  regular_bearish_divergence: "تباعد هابط عادي",
  hidden_bullish_divergence: "تباعد صاعد خفي",
  hidden_bearish_divergence: "تباعد هابط خفي",
  insufficient_evidence: "أدلة غير كافية",
  "insufficient evidence": "أدلة غير كافية",
  no_divergence: "لا تباعد",
  no_sweep: "لا اجتياح مستدل",
  unassigned: "غير مصنّفة",
  hammer: "مطرقة",
  shooting_star: "شهاب",
  doji: "دوجي",
  neutral_candle: "شمعة محايدة",
  bullish_engulfing: "ابتلاع صاعد",
  bearish_engulfing: "ابتلاع هابط",
  fresh: "حديثة",
  delayed: "متأخرة",
  stale: "قديمة",
  missing: "مفقودة",
  invalid: "غير صالحة",
  provider: "المزوّد",
  fixture: "بيانات اصطناعية",
  instrument: "الزوج",
  source_timestamp: "وقت المصدر",
  candles: "عدد الشموع",
  quality: "الجودة",
  freshness: "حداثة البيانات",
  freshness_reason: "سبب حالة الحداثة",
  confidence: "الجودة التحليلية",
  calibration: "المعايرة",
  validation: "التحقق",
  summary: "الملخص",
  available: "متاح",
  aligned: "متوافق",
  independent_families: "العائلات المستقلة",
  directional_families: "العائلات الاتجاهية",
  entry: "سيناريو الدخول",
  stop_loss: "سيناريو وقف الخسارة",
  target: "سيناريو الهدف",
  risk_reward: "نسبة العائد إلى المخاطرة",
  reasons: "الأسباب",
  status: "الحالة",
  "Decision: buy": "القرار: شراء",
  "Decision: sell": "القرار: بيع",
  "Decision: no_trade": "القرار: لا تداول",
  "Decision: wait": "القرار: انتظار",
  "Decision: insufficient_data": "القرار: بيانات غير كافية",
};

export function analysisLabel(value: string): string {
  return tokens[value] ?? value.replaceAll("_", " ");
}

const enumFields = new Set([
  "decision",
  "bias",
  "direction",
  "confidence",
  "calibration",
  "validation",
  "status",
  "quality",
  "freshness",
  "alignment",
  "classification",
]);

export function analysisValue(key: string, value: unknown): string {
  if (value === null || value === undefined) return ar.notAvailable;
  if (typeof value === "number" && !Number.isFinite(value)) return ar.notAvailable;
  if (key === "confidence" && !["low", "medium", "high"].includes(String(value))) {
    return ar.notAvailable;
  }
  if (typeof value === "boolean") return value ? "نعم" : "لا";
  if (typeof value === "string" && (enumFields.has(key) || key === "summary")) {
    return analysisLabel(value);
  }
  // Provider IDs, instruments, timestamps and source observations remain intact.
  return String(value);
}

export function formatUtcTimestamp(value: string): string {
  if (!/(Z|[+-]\d{2}:\d{2})$/.test(value) || !Number.isFinite(Date.parse(value))) {
    return ar.notAvailable;
  }
  return new Date(value).toISOString() + " (UTC)";
}
