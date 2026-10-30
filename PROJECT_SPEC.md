# Project specification and evidence inventory

Version: 1.0 | Updated: 2026-10-29 | Owner: Engineering | Status: incomplete product

## Authority and boundaries

D3 overlay: public Arabic guidance at /welcome, /product and /help now exists in
the original router; analysis root and API unchanged. No live market/account/
billing/support submission implied. Founder visual/copy/browser approval remains
pending, so these customer workflows are PARTIAL rather than visually complete.

B1 overlay: optional versioned Arabic deterministic explanation is produced in
the existing pipeline and rendered only when matching final decision/validation.
Legacy summary and top-level API 1.0 remain compatible. No external AI, new
decision contribution or market fact. See docs/05-analysis/arabic-deterministic-explanation.md.

C3 overlay: internal owner-scoped analysis history model/repository/service and
additive 20261030_0002 migration now exist. Default disabled without explicit
retention policy; no public history route or auth vendor introduced. Customer
history is PARTIAL, not production-enabled. See
docs/04-architecture/analysis-history-foundation.md and its scoped evidence.

2026-10-30 safety overlay: shared Candle/MarketData parsing now rejects boolean
prices/volume and non-boolean closed/fixture flags instead of silently coercing
them. Valid inputs and analytical/public API semantics are unchanged. Regression
evidence: backend/tests/analysis/test_boolean_boundaries.py; PROGRESS.md records
the complete verified checkpoint. This is not completion of the data product.

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
administrative roles cannot be recovered. Governance/baseline documents initially
missing from this checkout were recovered unchanged from historical commits.
Do not manufacture their approval or replace missing history with assumptions.
Authentication provider, production deployment target, AI provider, real data rights,
role-permission matrix, and exact release milestones need explicit evidence/decisions.

## Acceptance

## Current verification overlay

### Active master execution directive — 2026-10-30

The complete 31-section founder directive is preserved in
[approved master goal](docs/02-product/approved-master-execution-goal.md).
[Canonical requirements](docs/02-product/canonical-requirements.json) groups its
entire scope, 28 analytical components, 23 customer workflows and eleven executive
sections with approval/status/code/test/dependency fields and reverse references.
Group records overlap; their count is not an atomic feature-completion percentage.
The initial commercial model is one monthly tier, consent-based renewal,
end-of-paid-period cancellation, no launch trial or annual plan; price is unapproved.
Separate staging is required in addition to development/testing/production.
Final visual identity and ten design categories require explicit founder approval;
current styling is provisional. No vendor, paid commitment, live-data rights,
external customer-data transfer or production deployment is implicitly approved.

### Handover authority overlay — 2026-10-30

The founder's Safe Project Handover directive explicitly approves Saudi-first,
Arabic-first, customer-requested cryptocurrency spot analysis, with later markets
only through approved phases. No automated customer opportunity scanning/alerts,
trade execution or customer-facing interactive AI chat. Pricing is deferred until
measured operating cost; 169 SAR is not approved as final launch pricing.
Exactly eleven founder-only Command Center sections, nested AI CTO/CFO and the
independent weekly interactive executive Board Meeting are approved requirements.
They are not implemented features. No employee/delegated initial administration.
No paid commitments or external customer-data transfers without approval.

[Founder decisions](docs/handover/FOUNDER_DECISIONS.md) records every approved
boundary, all eleven names and explicit conflicts with historical proposals.
[Implementation inventory](docs/handover/IMPLEMENTATION_STATUS.md) and
[gap register](docs/handover/REMAINING_WORK.md) distinguish existing code,
missing features, evidence and external dependencies. Older baseline rows and
proposed documents remain historical; they do not override these newer approvals.
This overlay records authority, not an architecture redesign or product completion.

2026-10-30 founder approval resolves the initial access model: email-based
customers, one founder-only administrator with mandatory MFA, no employees or
delegated access. Vendor-neutral deny-by-default dependencies are implemented;
provider login/session/recovery and actual protected routes are not.
Authentication vendor remains subject to security/cost review. PostgreSQL is
the intended production database; development/testing/production must be separate.
No AI vendor or paid hosting is approved; customer data may not be sent to external
AI until privacy approval. Hosting, release security review and founder approval
remain required. Market-data rights are still unestablished.
See docs/06-security/identity-access-foundation.md for precise scope and gates.

Missing governance/baseline targets were recovered unchanged from historical
commits d78bbf7/e56261d. Their proposed status remains unchanged; restoration
is not a new approval. Inline local document file links now pass the executable
audit; semantic consistency and full governance acceptance remain incomplete.

The baseline table is historical, not the current completion claim. See
[requirement evidence](docs/10-testing/requirement-evidence-matrix.md) for every
inventory row, code/test locations, partial scopes and unresolved acceptance.
The current complete local gate runner passes 17 gates; this does not close
production deployment, empirical calibration, governance or external decisions.
Hosted run 40917970124 also passed Linux full-stack tests, Docker build and
container runtime safety checks at b8d8499. This is CI acceptance, not deployment.

The CTO approved Option A on 2026-10-29: context, level/zone and basic liquidity
observations now remain non-directional. Their measurements remain available;
own-method sweep inference retains direction. This closes the specific approval
blocker without claiming empirical independence/calibration of remaining methods.
[Approval dependencies](docs/03-engineering/acceptance-dependencies.md) records
other unresolved product/access decisions without inventing behavior.

Every supported requirement must be implemented, integrated, tested, documented,
and accurately classified. Full completion requires frontend/API integration,
historical safety, risk gates, and operational/security acceptance, not just compilation.
