---
title: Provider-Neutral Grounded Explanation Selection
document_id: DOC-AI-GROUNDED-001
version: 1.0.0
status: constrained-foundation-no-external-provider
owner: Engineering
reviewers: Founder, Security
last_updated: 2026-10-31
next_review: 2026-11-30
related_documents: [DOC-PROD-MASTER-GOAL-001]
---

# Grounded explanation selection

## Purpose

Provide an executable safe provider boundary within the existing AIReasoningLayer,
without authorizing a vendor or unreviewed customer-data transfer.

## Scope

This is constrained selection of deterministic Arabic facts, NOT free-form
generative reasoning, market inference or complete AI product acceptance.
Ordinary application output remains available:false. No HTTP input, settings
switch, vendor SDK, credentials or network adapter enables it.

## Main content

AnalysisService optionally accepts GroundedExplanationService through trusted
construction, passing it into the same 28-stage default pipeline. A synthetic
adapter proves reachability in tests. Existing custom-engine injection is preserved.

The immutable minimized packet contains final decision/validation, server-authored
Arabic summary/limitations and opaque hashed evidence references with relations.
Raw candles, account/request metadata, source findings and prompt-like strings
are not forwarded. Opaque hashes are pseudonymous references, not anonymity.

The adapter returns bounded JSON (16KiB maximum), contract grounded-selection-v1,
decision/validation, ordered fact IDs and reference IDs only. Duplicate JSON keys,
nonfinite constants, duplicate/unknown IDs, extra provider prose/numbers and state
mismatch are rejected. Every deterministic limitation/fact remains mandatory;
conflicting references cannot be hidden. Text is rendered locally from trusted facts.

Policy is frozen/revalidated and disabled by default. Invocation requires exact
injected provider ID plus explicit provider/data-transfer approval references.
References are traceability, not proof of legal/founder approval. No real adapter
is installed. A future approved adapter must independently bound request duration,
retries and cost and satisfy privacy/security review.

Failure returns a safe unavailable reason; raw adapter errors are not exposed.
AI cannot change deterministic evidence, decision, risk, confidence or validation.
Late required-engine failure withholds previously valid selection and regenerates
the deterministic fallback according to the final safety state.

### Verification

backend/tests/analysis/test_grounded_ai.py has 37 tests covering absent/denied
providers, strict models/JSON bounds, malicious prose/ID/state changes, minimized
packet, mandatory limitations/conflicts, actual service reachability, mutation
isolation and late failure. Existing API/history/historical regressions also ran.
These do not establish a real provider, data-sharing approval, model quality or
commercial narrative capability.

## Related documents

- [Arabic deterministic fallback](arabic-deterministic-explanation.md)
- [AI philosophy](../01-project/ai-philosophy.md)
- [Canonical requirements](../02-product/canonical-requirements.json)

## Change history

- 1.0.0 — Constrained provider-neutral selection with no live integration.
