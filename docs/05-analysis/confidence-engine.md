---
title: Confidence Engine
document_id: DOC-ANALYSIS-CONFIDENCE_ENGINE-001
version: 1.1.0
status: proposed
owner: Engineering
reviewers: CTO
last_updated: 2026-10-29
next_review: 2026-11-11
related_documents: [DOC-MANIFEST-001]
---

# Confidence Engine
## Purpose
Define the architectural responsibility of Confidence Engine.
## Scope
Current fixture-backed analytical-quality labeling and its uncalibrated boundary.
## Main Content
ConfidenceEngine in backend/app/analysis/engines.py consumes directional evidence
family count, confluence, MTF alignment, data quality/freshness and risk status.
Labels are high, medium or low analytical quality, not win probabilities.
Data, freshness, MTF or risk penalties reduce the result to low. The existing
provisional label thresholds are engineering defaults, not validated calibration.

Every runtime response declares calibration=uncalibrated. Validation remains
independent: confidence cannot override risk, data or required-engine failures.
The frontend displays analytical-quality and uncalibrated disclaimers and does
not invent percentages.

CalibrationWorkflow maintains separate development fitting and OOS evaluation
boundaries. Dataset identity/role/content version, configuration identity and
finite numeric fitter outputs are checked. Its evaluation result remains
evaluation_pending: no historical data, completed scoring or empirical calibration
evidence is fabricated by that record. A successful fit call is not proof of
predictive quality or permission to label confidence calibrated.

Verification: test_calibration.py, test_safety_acceptance.py,
test_failure_isolation.py and frontend AnalysisResults.test.tsx. Licensed datasets,
an empirical calibration protocol and acceptance evidence remain unresolved.
## Related Documents
[Project Manifest](../01-project/project-manifest.md)
## Change History
- 1.1.0 — Replaced obsolete documentation-only status with bounded runtime evidence.
- 1.0.0 — Initial proposed specification.
## Approval
Proposed; CTO approval required.
