"""Provider-neutral constrained explanation selection, never free-form market claims.

There is deliberately no network adapter. A future reviewed adapter receives only
server-authored facts and opaque references and must enforce its own request/cost
limits. Policy references record a trusted operator's approval; they do not grant
legal permission or prove founder approval by themselves.
"""

import hashlib
import json
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.analysis.context import AnalysisContext
from app.analysis.explanations import (
    ArabicExplanation,
    ExplanationReference,
    explain_in_arabic,
)
from app.analysis.models import DecisionState, ValidationStatus

MAX_RESPONSE_BYTES = 16 * 1024
MAX_FACTS = 32
MAX_REFERENCES = 128


class ImmutableContract(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")


class ExplanationPolicy(ImmutableContract):
    """Trusted injection only; public request metadata never enables AI transfer."""

    enabled: bool = False
    provider_id: str | None = Field(default=None, pattern=r"^[a-z0-9_-]{1,64}$")
    provider_approval_reference: str | None = Field(
        default=None, min_length=1, max_length=200, pattern=r"\S"
    )
    data_transfer_approval_reference: str | None = Field(
        default=None, min_length=1, max_length=200, pattern=r"\S"
    )

    def permits(self, provider_id: str) -> bool:
        return bool(
            self.enabled
            and self.provider_id == provider_id
            and self.provider_approval_reference
            and self.data_transfer_approval_reference
        )


class GroundedFact(ImmutableContract):
    id: str
    text: str


class OpaqueReference(ImmutableContract):
    id: str
    relation: Literal["supporting", "conflicting", "contextual"]


class ExplanationPacket(ImmutableContract):
    contract_version: Literal["grounded-selection-v1"] = "grounded-selection-v1"
    language: Literal["ar"] = "ar"
    decision: DecisionState
    validation: ValidationStatus
    facts: tuple[GroundedFact, ...] = Field(max_length=MAX_FACTS)
    references: tuple[OpaqueReference, ...] = Field(max_length=MAX_REFERENCES)


class ExplanationSelection(ImmutableContract):
    """Only selection/reordering is allowed; no provider-authored prose or numbers."""

    contract_version: Literal["grounded-selection-v1"]
    decision: DecisionState
    validation: ValidationStatus
    fact_ids: tuple[str, ...] = Field(min_length=1, max_length=MAX_FACTS)
    reference_ids: tuple[str, ...] = Field(max_length=MAX_REFERENCES)

    @model_validator(mode="after")
    def unique_ids(self) -> "ExplanationSelection":
        if len(set(self.fact_ids)) != len(self.fact_ids) or len(
            set(self.reference_ids)
        ) != len(self.reference_ids):
            raise ValueError("Duplicate explanation selection")
        return self


class GroundedExplanation(ImmutableContract):
    methodology_version: Literal["grounded-selection-v1"] = "grounded-selection-v1"
    language: Literal["ar"] = "ar"
    mode: Literal["constrained_provider_selection"] = "constrained_provider_selection"
    decision: DecisionState
    validation: ValidationStatus
    statements: tuple[str, ...]
    references: tuple[ExplanationReference, ...]


class ExplanationProvider(Protocol):
    """A reviewed adapter must bound duration, retries and cost independently.

    This protocol has no credentials/network/default vendor. No adapter is wired
    to application settings or public HTTP input by this foundation.
    """

    @property
    def provider_id(self) -> str: ...

    def select(self, packet: ExplanationPacket) -> str:
        """Return bounded JSON matching ExplanationSelection, never free-form text."""
        ...


def _opaque(identifier: str) -> str:
    return hashlib.sha256(identifier.encode("utf-8")).hexdigest()


def _packet(fallback: ArabicExplanation) -> ExplanationPacket:
    facts = (GroundedFact(id="decision", text=fallback.summary),) + tuple(
        GroundedFact(id=f"limitation_{index}", text=text)
        for index, text in enumerate(fallback.limitations)
    )
    references = tuple(
        OpaqueReference(id=_opaque(item.evidence_id), relation=item.relation)
        for item in fallback.references
    )
    if len({item.id for item in references}) != len(references):
        raise ValueError("Ambiguous explanation references")
    return ExplanationPacket(
        decision=fallback.decision,
        validation=fallback.validation,
        facts=facts,
        references=references,
    )


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _invalid_constant(value: str) -> None:
    raise ValueError("Nonfinite JSON value")


def _selection(response: object, packet: ExplanationPacket) -> ExplanationSelection:
    if not isinstance(response, str) or len(response.encode("utf-8")) > (
        MAX_RESPONSE_BYTES
    ):
        raise ValueError("Invalid explanation response size/type")
    json.loads(
        response, object_pairs_hook=_unique_object, parse_constant=_invalid_constant
    )
    selected = ExplanationSelection.model_validate_json(response)
    if selected.decision != packet.decision or selected.validation != packet.validation:
        raise ValueError("Explanation cannot override final analytical state")
    # Every supplied limitation is mandatory, including uncertainty and fixture
    # disclosure. Selection may reorder facts, never suppress these safeguards.
    if set(selected.fact_ids) != {item.id for item in packet.facts}:
        raise ValueError("Missing or unsupported explanation facts")
    allowed = {item.id for item in packet.references}
    required = {item.id for item in packet.references if item.relation == "conflicting"}
    if not set(selected.reference_ids) <= allowed or not required <= set(
        selected.reference_ids
    ):
        raise ValueError("Unsupported or concealed conflicting reference")
    return selected


class GroundedExplanationService:
    def __init__(
        self,
        provider: ExplanationProvider | None = None,
        policy: ExplanationPolicy | None = None,
    ) -> None:
        self._provider = provider
        # Revalidate copied/constructed models; frozen=True alone is not trust.
        self._policy = ExplanationPolicy.model_validate(
            (policy or ExplanationPolicy()).model_dump(warnings="error")
        )

    def explain(
        self, context: AnalysisContext
    ) -> tuple[GroundedExplanation | None, str]:
        if self._provider is None:
            return None, "provider_unavailable"
        try:
            if not self._policy.permits(self._provider.provider_id):
                return None, "transfer_not_approved"
            fallback = explain_in_arabic(context)
            packet = _packet(fallback)
            # A misbehaving adapter cannot mutate the validation source or context.
            raw = self._provider.select(packet.model_copy(deep=True))
            selected = _selection(raw, packet)
            facts = {item.id: item.text for item in packet.facts}
            references = {
                _opaque(item.evidence_id): item for item in fallback.references
            }
            return (
                GroundedExplanation(
                    decision=packet.decision,
                    validation=packet.validation,
                    statements=tuple(facts[key] for key in selected.fact_ids),
                    references=tuple(references[key] for key in selected.reference_ids),
                ),
                "validated_selection",
            )
        except Exception:
            # Never expose raw adapter exceptions or convert optional AI failure
            # into a change to deterministic evidence/decision/confidence.
            return None, "explanation_withheld"
