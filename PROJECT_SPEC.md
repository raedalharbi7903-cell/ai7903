# Project specification and evidence inventory

Version: 1.0 | Updated: 2026-10-29 | Owner: Engineering | Status: incomplete product

## Authority and boundaries

The current CTO master directive governs this execution. Existing proposed documents
are evidence of intended scope, not proof of implementation or approval of unspecified
algorithms. Preserve spot-only, no automatic trading, deterministic analysis before
AI explanation, and transparent demo provenance. No feature is silently removed.

## Inventory at baseline 7e24bf8

| Requirement | Evidence | Baseline status |
| --- | --- | --- |
| Backend configuration, health, database, repositories, services | backend/app, backend/tests | Implemented; revalidation pending |
| Sequential engine registry, pipeline, lifecycle, telemetry | backend/app/analysis | Implemented; insufficiently tested |
| Structure, trend, levels, zones, momentum, volume, volatility, patterns | deterministic.py, engines.py | Partial: simple provisional methodologies |
| Four divergence classes and effective configuration | deterministic.py | Partial: configuration unused; momentum pivots not matched |
| Confirmed structure breaks, liquidity sweeps, volume anomaly, candle patterns | deterministic.py | Partial: fixed policies and missing boundary tests |
| Evidence, confluence, opportunity, five decisions | engines.py | Partial: same-family conflict handling needs correction |
| Structural risk and final validation | engines.py | Partial: target fallback and invalid-data gate risks |
| MTF and benchmark correlation | engines.py | Partial: fixture frame identity not verified |
| Historical service execution, fees, slippage, stop-first | backtesting.py | Partial: same primary series reused as all timeframes |
| Development/OOS split and calibration | calibration.py | Partial; no empirical calibration evidence |
| Fixture analysis API and advanced output | api/v1/analysis.py, models.py | Partial: provenance validation incomplete |
| React analysis experience and typed API client | frontend/src | Partial: minimal panels; no component test configuration |
| React Router, Tailwind, ESLint, Prettier | prior approved frontend stack | Missing or incomplete configuration |
| AI narrative constrained by deterministic safety | AIReasoningLayer | Missing; provider unavailable |
| Live cryptocurrency data | providers.py, CTO safety boundary | Externally blocked: approved commercial rights/access not established |
| Authentication/authorization and administration | docs/06-security, docs/07-organization | Missing; identity method and role permissions Decision Required |
| Operations, deployment, monitoring, backup/restore | docs/09-devops | Partial: Dockerfile and hooks; no demonstrated deployment/restore |
| Complete governance and documentation portal | docs/README.md and linked documents | Partial: missing governance/baseline documents and stale implementation claims |

No row is marked verified solely because a file exists. Current-run evidence is
recorded in PROGRESS.md.

## Canonical engine responsibilities

The catalogue at docs/05-analysis/engine-catalog.md defines 24 components: Data,
Market Context, Market Structure, Trend, Support/Resistance, Supply/Demand,
Liquidity, Volume, Momentum, Volatility, Pattern Recognition, Candlestick,
Correlation, Multi-Timeframe, Evidence, Confluence, Opportunity Filter, Decision,
Risk, Confidence, Validation, Explainability, AI Reasoning, Strategy/Backtesting.
The current pipeline adds divergence, volume anomaly, liquidity sweep, and market
transition. These share existing evidence families; 28 engines are not 28 independent
votes. All components remain in scope.

## Reconstructability and external decisions

docs/02-product/product-requirements.md leaves pricing and recommendation behavior
Decision Required. docs/07-organization/administrative-roles.md explicitly says
administrative roles cannot be recovered. The referenced project manifest,
architecture baseline and several governance documents are absent from tracked files.
Do not manufacture their approval or replace missing history with assumptions.
Authentication provider, production deployment target, AI provider, real data rights,
role-permission matrix, and exact release milestones need explicit evidence/decisions.

## Acceptance

## Current verification overlay

The baseline table is historical, not the current completion claim. See
[requirement evidence](docs/10-testing/requirement-evidence-matrix.md) for every
inventory row, code/test locations, partial scopes and unresolved acceptance.
The current complete local gate runner passes 13 gates; this does not close
production deployment, empirical calibration, governance or external decisions.

Every supported requirement must be implemented, integrated, tested, documented,
and accurately classified. Full completion requires frontend/API integration,
historical safety, risk gates, and operational/security acceptance, not just compilation.
