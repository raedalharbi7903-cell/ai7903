"""Arabic deterministic fallback: fixed claims, no free-form source instructions."""

from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.analysis.context import AnalysisContext
from app.analysis.models import DecisionState, ValidationStatus

DECISION_TEXT = {
    DecisionState.BUY: "الاتجاه التحليلي النهائي شراء؛ ليس أمراً لتنفيذ صفقة.",
    DecisionState.SELL: (
        "الاتجاه التحليلي النهائي بيع؛ " "لا يعني فتح مركز بيع على المكشوف."
    ),
    DecisionState.NO_TRADE: "القرار النهائي لا تداول؛ لا توجد توصية تنفيذية.",
    DecisionState.WAIT: "القرار النهائي انتظار؛ لا توجد توصية تنفيذية حالية.",
    DecisionState.INSUFFICIENT_DATA: (
        "البيانات غير كافية لإصدار قرار تحليلي قابل للاستخدام."
    ),
}


class ExplanationReference(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    evidence_id: str
    source_engine: str
    family: str
    relation: Literal["supporting", "conflicting", "contextual"]


class ArabicExplanation(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    methodology_version: Literal["deterministic-ar-v1"] = "deterministic-ar-v1"
    language: Literal["ar"] = "ar"
    mode: Literal["deterministic_fallback"] = "deterministic_fallback"
    decision: DecisionState
    validation: ValidationStatus
    summary: str
    limitations: list[str]
    references: list[ExplanationReference]


def explain_in_arabic(context: AnalysisContext) -> ArabicExplanation:
    """Read existing final state; never change votes, confidence, risk or decisions."""
    validation = ValidationStatus(
        context.state.get("validation", ValidationStatus.FAIL)
    )
    if context.market_data is None:
        decision = DecisionState.INSUFFICIENT_DATA
    elif validation != ValidationStatus.PASS:
        decision = DecisionState.NO_TRADE
    else:
        decision = DecisionState(context.state.get("decision", DecisionState.NO_TRADE))
    confluence = context.output("confluence")
    conflicted = (
        set(confluence.data.get("conflicted_families", [])) if confluence else set()
    )
    direction = {
        DecisionState.BUY: "bullish",
        DecisionState.SELL: "bearish",
    }.get(decision)
    references = []
    directional_conflict = {"bullish", "bearish"} <= {
        item.bias for item in context.evidence if item.bias is not None
    }
    for item in context.evidence:
        relation = "contextual"
        if (
            item.family in conflicted
            or item.conflicts
            or (directional_conflict and item.bias in {"bullish", "bearish"})
        ):
            relation = "conflicting"
        elif direction and item.bias in {"bullish", "bearish"}:
            relation = "supporting" if item.bias == direction else "conflicting"
        references.append(
            ExplanationReference(
                evidence_id=item.evidence_id,
                source_engine=item.source_engine,
                family=item.family,
                relation=relation,
            )
        )
    limitations = [
        "هذا شرح حتمي للنتيجة، وليس نصاً مولداً بواسطة مزوّد ذكاء اصطناعي.",
        "الثقة التحليلية ليست احتمالاً مثبتاً لتحقيق الربح ولا ضماناً للنتيجة.",
        "مراجع الأدلة لا تضيف أصواتاً مستقلة ولا تغيّر القرار أو حدود المخاطر.",
    ]
    if validation != ValidationStatus.PASS:
        limitations.append(
            "التحقق النهائي غير ناجح؛ لا تعتمد على مستويات المخاطر كفرصة تنفيذية."
        )
    if context.market_data is None:
        limitations.append("بيانات السوق الموثوقة غير متاحة لهذه النتيجة.")
    elif context.market_data.fixture:
        limitations.append("البيانات تجريبية مصطنعة وليست بيانات سوق حية.")
    if any(item.relation == "conflicting" for item in references):
        limitations.append("توجد أدلة متعارضة؛ لا يخفي هذا الشرح التعارض.")
    return ArabicExplanation(
        decision=decision,
        validation=validation,
        summary=DECISION_TEXT[decision],
        limitations=limitations,
        references=references,
    )
