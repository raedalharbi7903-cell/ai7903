# Dependency-aware implementation plan

Version: 1.0 | Updated: 2026-10-29 | Status: executing

| Package | Required changes and files | Acceptance and tests | Depends on | Evidence |
| --- | --- | --- | --- | --- |
| P0 memory | Root governance/inventory/progress files | Source-grounded scope, no invented approvals | Repository inspection | Baseline recorded |
| P1 advanced analysis | analysis/advanced.py, deterministic.py, engines.py; dedicated tests | Effective validated configs; four divergence classes; closed confirmed matched pivots; stable references; sweep/volume/candle boundaries | P0 | Pending execution |
| P2 safety integration | engines.py, providers.py, pipeline.py, risk tests | Family conflicts cannot inflate votes; invalid data/risk never actionable; final explanation agrees with final decision | P1 | Pending |
| P3 historical evaluation | backtesting.py, calibration.py, historical tests | True as-of frames, fees/slippage, no lookahead, invalid-trade exclusion, reproducible metrics and OOS isolation | P2 | Pending |
| P4 API/frontend | api/v1/analysis.py, frontend/src, frontend tooling/tests | Strict fixture provenance; typed panels, five states, safe errors, loading/empty/degraded states, actual API integration tests | P2 | Pending |
| P5 operational/security scope | docs/06-security, docs/07-organization, docs/09-devops and corresponding runtime modules | Implement reconstructable approved scope; leave unknown roles/providers explicitly unresolved; deployment and restore evidence | P0, P4; external decisions | Pending |
| P6 acceptance | Backend/frontend checks and relevant documentation | Full tests, static checks, formatting, builds, leakage/security review; feature branch clean and pushed | P1-P5 | Pending |

After each substantial package, record exact commands and outcomes in PROGRESS.md,
commit coherent progress, then continue independent executable work. No arbitrary
single-file checkpoint counts as completion.

## Current evidence overlay

P0 is established. P1-P4 have verified integrated implementation at 7494cf8, with
remaining methodological limits listed in the requirement-evidence matrix.
P5 is active: non-root container/healthcheck, reproducible verification runner,
runner failure tests and operational runbook added. Docker execution remains
environment-blocked. P6 local gates pass, but full product acceptance remains
incomplete. Next: hosted CI configuration/execution and documentation consistency
audit, followed by remaining independent security/performance work. External
provider/identity/role decisions remain unresolved, not silently deferred.
