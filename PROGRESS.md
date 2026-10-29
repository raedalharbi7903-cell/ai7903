# Execution progress

Updated: 2026-10-29
Branch: feature/crypto-analysis-validation
Baseline: 7e24bf88d4de1a240291b565b8e6f1108223e785
Product status: NOT COMPLETE

## Legacy methodology and numerical review continuation

Previous turn was progress at 1678fb3. Eighteen initial boundary tests reproduced
invalid-period handling, overflowed SMA/RSI and unstable large/tiny correlation.
Corrected numerical arithmetic without replacing the existing arithmetic-window
methods; added reference-value and nonfinite-output production rejection tests.
The pipeline now rejects nonfinite measurements before publishing results.
Full local 17-gate run PASSED: 265 backend, 16 frontend, 11 tooling tests.

Critical review finding: several distinct evidence-family labels inherit the same
whole-prefix price direction, so family-name deduplication alone does not prove
independence. Fixing contributions affects decision/confidence behavior and is a
red-level CTO decision, not an autonomous methodology redesign. Options and
recommendation are recorded in docs/05-analysis/legacy-methodology-review.md.
This gap invalidates any broad claim that evidence independence is fully accepted;
existing tests only prove same-family grouping/conflict handling.

## Migration packaging and disposable recovery continuation

Previous turn was progress at b01fac9. Added actual Alembic subprocess migration
roundtrips and offline generation plus SQLite backup/restore integrity tests.
The percent-containing database URL case initially failed ConfigParser
interpolation; fixed configuration-layer percent escaping without changing the
actual database URL. Seven targeted migration/recovery/session tests now PASS.
Session tests cover rollback, close, early generator close and no hidden commit.

Backend container previously omitted Alembic sources/configuration; packaged them
and extended smoke verification to upgrade a disposable container-local /tmp DB.
Hosted confirmation of this new packaging/smoke extension is pending; earlier
container results do not prove this extension. Full local 17-gate run PASSED:
243 backend, 16 frontend, 11 tooling tests. Adding Alembic env.py to the lint/
format gates exposed an existing import-order failure; corrected and reran all.
Hosted confirmation obtained: run 40919739638, job 123609406267, commit 7addc48
completed SUCCESS. Full-stack gates, document audit, Docker build and extended
container smoke (including packaged Alembic upgrade/current) all PASS. This closes
CI migration packaging verification, not production deployment or backup policy.
Backup documentation now distinguishes disposable SQLite evidence from unapproved
production recovery/storage/RPO/RTO decisions. No business tables were introduced.

## Request isolation and fixture-security continuation

Previous turn was progress at cd60ff5. The mutation-probe test reproduced caller
input corruption through shared AnalysisContext. Fixed by copying AnalysisInput
deeply at the service boundary; no public contracts or engine ordering changed.
Tests cover nested caller-state preservation, 64 parallel service requests with
mixed failures, 32 parallel API requests with provider/external-GET denial hooks,
negative candle validation and fixture-size limits. Added 16 concurrent actual
HTTP requests via the typed frontend client to isolated Uvicorn/FastAPI.
These are bounded regression workloads, not production capacity/security claims.
Acceptance scope is in docs/10-testing/request-isolation-acceptance.md.

Full 17-gate run PASSED: 236 backend, 16 frontend and 11 tooling tests.
Post-change synthetic sequential benchmark (20 samples, incomplete MTF workload):
p95 1.108ms / 4.068ms / 12.909ms for 32 / 256 / 1024 candles. Maximum at 1024
was 20.039ms. Snapshot copying has a cost; no production SLA is inferred.
External licensing, identity/administration,
AI-provider and deployment decisions remain unresolved; no scope was removed.

## Hosted POSIX fix verified

Run 40917970124, job 123603158560, commit b8d8499 completed SUCCESS:
all backend/frontend gates, documentation audit, Docker build, actual container
health/non-root/production-denial smoke, and evidence upload PASS. Frontend
integration executed on Linux, confirming the virtualenv symlink root-cause fix.
Local verification: all 17 gates PASS (227 backend, 15 frontend, 11 tooling tests).
Removed the ineffective onTestRunEnd diagnostic reporter; retained the native
failure-only diagnostic for future startup troubleshooting.

Updated confidence documentation with actual uncalibrated runtime semantics and
pending empirical evaluation; document link audit PASS. This is not full product
completion: production deployment/restore, full security and concurrency/load
acceptance, remaining engine methodology review, semantic documentation coverage,
licensed historical/live data, identity/role and AI-provider decisions remain.
Next executable package: broader security/concurrency acceptance and complete
requirement-matrix reconciliation against current runtime evidence.

## POSIX interpreter-path root-cause correction

Previous turn was progress at 5bbb04e. Verified run 40917306443 / job 123600847179:
normal test gate FAIL, but standalone supported-API diagnostic discovered all
three modules and started without throwing. Docker/runtime checks still PASS.
The runner alone set BACKEND_PYTHON using Path.resolve(): on POSIX virtualenv
executables are symlinks, so dereferencing selects the base interpreter outside
the installed backend environment. Changed to lexical os.path.abspath and added
a regression that fails if interpreter dereferencing is attempted. Hosted
confirmation remains required; diagnostics are not a substitute for green tests.

While waiting for that live run, hardened calibration records: configuration and
dataset identity/roles are validated; empty, nonfinite, boolean and malformed
fitter outputs are rejected. Added 17 cases. No fitting algorithm, probability,
profit result or empirical calibration claim was introduced. Calibration remains
uncalibrated/evaluation_pending until real independent evidence exists.

## Linux startup investigation and semantic consistency continuation

Previous turn was progress at 0bf8788. Verified run 40916739739 / job 123598875758:
full-stack FAIL at Linux Vitest startup; Docker build, container smoke, document
audit and evidence upload PASS. Reporter onTestRunEnd did not execute before the
startup error, so it did not reveal the underlying exception. Added a CI-only
supported createVitest API diagnostic after the failing normal gate; it discovers
test specifications and catches original fields without CLI stack formatting.
Validated this diagnostic locally; the normal failing gate remains authoritative.
No toolchain patch release is available beyond installed Vite 8.3.5/Vitest 5.0.5.

Closed internal freshness coercion: boolean, fractional and string settings cannot
be converted to accepted integer policy values. Added four production-service
regressions. Corrected genuine stale claims in the catalogue, pipeline document
and portal; preserved proposal/approval status and did not modify the manifest,
handbook or architecture baseline. The portal now distinguishes historical intent
from runtime acceptance and links current evidence.

Final 17-gate local verification PASSED: 210 backend, 15 frontend, 10 tooling tests,
zero broken inline file links, lint/format/build/type/import/dependency gates PASS.
Hosted startup remains unresolved;
next executable task is reading the native diagnostic in the new pushed run.

## Historical evidence and hosted-runtime continuation

Previous turn was progress at 6ef44a1. Verified GitHub run 40915941075 / job
123596050191: Docker build and actual container smoke PASS (health, non-root UID,
production demo denial). Full-stack CI still FAILS on Linux Vitest startup with
the same source-map error; NODE_OPTIONS diagnostics did not resolve it.
Added an original-error diagnostic reporter alongside the default failing reporter
to expose the underlying message without suppressing errors. Hosted verification
of this diagnostic remains pending.

Historical evidence now uses the last closed observation timestamp, separate from
result generation time. Added replay/provenance tests; backend suite 206 PASS.
No wall-clock evidence timestamps or live market outputs are fabricated.
Container deployment/restore and full security/performance acceptance remain open.

Reporter lint initially failed; its unused parameter was corrected. That failure
also exposed a verification-runner bug: Unicode diagnostics crashed legacy Windows
stdout before later gates/reporting. The runner now explicitly configures UTF-8
output instead of dropping diagnostics. Root README now reflects implemented
architecture, actual setup/verification commands and incomplete/demo boundaries.
Final full-stack local rerun PASSED all 17 gates: 206 backend, 15 frontend and
10 tooling tests. No hosted startup fix is claimed; the new reporter must execute
on Linux to expose the masked startup message.

## Freshness, legacy volume and hosted-CI continuation

Previous turn was progress at f0ed0a4. GitHub's general runs endpoint exposes push
runs omitted by the specialized lookup. Verified run 40915087207 / job 123593341472:
Docker build PASS; documentation audit PASS; full-stack gate FAIL due Linux
frontend startup (Vite source-map TypeError code.charCodeAt is not a function).
This is an unresolved hosted-toolchain defect, not a passing CI claim.
Native source-map diagnostics are enabled for the next run; no tests are skipped.

Closed a freshness bypass: a recent incomplete candle no longer refreshes stale
closed data. Naive reference timestamps, incomplete middle history, empty closed
history and invalid freshness policy values are handled explicitly. Flat RSI is
neutral 50, not overbought 100. Classic volume now shares the validated rolling
baseline methodology: missing current/prior volume or a zero baseline cannot
create a directional vote from an older sample. Backend suite reached 204 PASS.

Added CI container smoke verification (loopback-only binding, health, non-root UID,
production demo denial, exact-container cleanup), independent of frontend success.
Local Docker execution is still unavailable; mocked cleanup tests are not runtime
acceptance. The next push must be inspected for actual Linux and container results.

## Runtime security and resilience continuation

Previous turn was progress at 7f6ef5d. Hosted workflow lookup still returned no
runs; hosted CI/Docker success is not claimed. Added sanitized global unexpected
error responses, isolated failed-engine outputs, final safety reconciliation after
late failures, and invalid-volatility rejection. Added 11 backend cases:
four injection positions, two API error boundaries and five invalid ATR inputs.
An initial test referenced the wrong telemetry attribute; corrected to the actual
sink contract without removing assertions.

Added a reproducible synthetic service-latency benchmark and explicit limitations
in docs/10-testing/runtime-resilience-results.md. Actual observed p95: 0.772ms
(32 candles), 3.498ms (256), 7.274ms (1024), 20 samples each. This is not concurrent
HTTP or full-MTF performance acceptance. No financial measurements are fabricated.

The verification runner now uses dedicated .verification pytest/Ruff caches to
resolve previously reported Windows access-denied cache warnings. One benchmark
line-length failure was corrected. Final repeat run PASSED all 17 gates:
189 backend tests, 15 frontend tests, 7 tooling tests, zero broken local file links.
The pytest cache warning is resolved; backend Ruff still emitted an access-denied
scan warning. Legacy pytest cache directories are now explicitly ignored; the
warning is disclosed rather than treated as a clean security/operational gate.
Remaining scope is unchanged: hosted execution, deployment/restore, full
performance/security acceptance, legacy-engine review, prose consistency and
external data/identity/AI decisions.

## CI and documentation recovery continuation

Previous turn was verified progress at 3119f38. Added a SHA-pinned, read-only
GitHub Actions workflow for Python 3.12 / Node 24.14 / pnpm 11.25, full-stack
verification, documentation audit, Docker build and retained evidence.
Workflow YAML parsed and security/step assertions passed locally; hosted execution
is not yet claimed.

The new documentation audit initially found 128 missing links. Git history
contained all 21 missing target files: restored unchanged from d78bbf7 and e56261d.
Every restored file matches its original Git blob. No manifest, handbook or
baseline wording/approval status was changed. Audit now reports zero missing
inline local file links. This does not validate prose consistency, reference-style
links or anchors; those remain separate work.

Seven tooling tests pass. Verification now includes 17 gates, covering tooling
tests/lint/format and documentation file links as well as the prior full stack.
A newly exposed tooling line-length failure was repaired; the complete repeat run
PASSED all 17 gates (178 backend tests, 15 frontend tests, 7 tooling tests).
Next: inspect hosted CI results, repair cross-platform failures if present, then
continue security/performance and prose-consistency acceptance work.

## Latest operational verification package

Previous continuation was progress: integrated work committed/pushed at 7494cf8.
Current continuation preserved that clean feature branch and implemented:

- scripts/verify.py: all 13 backend/frontend gates, exact command/exit/output JSON,
  nonzero aggregate status, explicit missing-tool/timeout failures.
- scripts/test_verify.py: 4 tests PASS for gate inventory and failure reporting.
- backend Dockerfile: unprivileged runtime account and internal health check;
  .dockerignore excludes environment files/caches/development dependencies.
- Full requirement-to-evidence matrix and operational verification runbook.

Executed scripts/verify.py successfully: all 13 gates PASS, including backend
178 tests, frontend 15 tests with real FastAPI integration, imports, compilation,
lint/format, frozen installation, production bundle and dependency compatibility.
Machine-readable local evidence: .verification/quality-gates.json (Git-ignored).
Docker build remains BLOCKED by missing Docker executable; container changes have
not been runtime-verified. Hosted CI, deployment, restore drills, performance and
full security acceptance remain incomplete. Next executable package: CI and
documentation consistency audit. No merge or main push authorized/performed.

## Completed this execution

- Verified clean branch and HEAD against the directive.
- Inspected engine implementation, API, frontend, tracked documents and recent history.
- Established project memory and evidence-based requirement inventory.

## Active package

P4: frontend/API integration, following safety hardening. P1 implemented matched confirmed pivots, effective divergence,
volume/sweep/structure settings, rejection confirmation, single-event structure
breaks, closed-prefix handling, and engulfing/conflicting-pattern correction.

## Validation evidence

- Backend: `.venv/Scripts/python -m pytest -o cache_dir=.pytest_cache_execution`:
  **159 passed** (72 existing plus 87 new), 2.40 seconds after API/safety changes.
- Backend: `.venv/Scripts/python -m ruff check .`: PASS.
- Black applied to app/tests; final check will be repeated before delivery.
- Default pytest cache initially produced Windows access-denied warning; an alternate
  project-local cache path ran successfully, without disabling any tests.

## Remaining

P1-P6 in IMPLEMENTATION_PLAN.md. Scope and missing decisions are retained in
PROJECT_SPEC.md. Frontend, safety, historical evaluation, operations, and security
acceptance remain open.

## Genuine external constraints

Approved live-data rights/access, AI provider configuration, administrative role
permissions, and production deployment target have not been established in the
inspected repository. These do not block deterministic fixture development.

## Commits

- c5d091d: integrated advanced methodologies, 48 behavioral tests, project memory.
- 08aafb0: evidence/risk safety and typed fixture API boundary.

## Resumed verification and current continuation point

Resumed from 08aafb0 with all uncommitted historical/frontend work preserved.
P3 now has explicit as-of timeframe snapshots, spot-only execution, adverse-gap
stops, both-sided fees/slippage, chronological OOS checks and reproducible results.
P4 now has React Router/Tailwind, typed runtime-checked contracts, all decision
panels, provenance, confidence labels, safe errors and actual FastAPI integration.

Fresh verification: 178 backend tests passed in 1.62 seconds; Ruff PASS; Black
PASS (64 files); compileall PASS; pip check PASS. Frontend: frozen install PASS;
TypeScript PASS; ESLint PASS; 15 tests PASS (including real backend integration);
build PASS (JS 266.29 kB / gzip 84.69 kB); peers PASS. Formatting found index.html
and README.md; both were corrected and the complete formatter check now PASSES.
Windows dependency-store permissions required
approved elevated execution. No tests were disabled.

Browser inspection confirmed the empty-state desktop layout and 390px mobile
layout, with no horizontal overflow at 390px. Result panels are integration-tested;
full browser interaction/accessibility certification is not claimed.

Remaining executable work: comprehensive operational/CI/deployment acceptance,
broader methodological review of legacy engines, complete documentation consistency
audit, performance/load tests, security hardening beyond the demo boundary and
empirical validation on approved historical data. External decisions remain above.
The next work package is P5 operational/security closure; P6 is partial, not project
acceptance. Docker is not installed in this environment, so Docker build is blocked.

## Safety corrections

- Same-family contradictions now block confluence even when the second finding is
  marked non-independent; duplicate engines do not create votes.
- Invalid numerical/price data is rejected before deterministic calculations.
- Poor structural target reward cannot be replaced by an optimistic projection.
- Final explanations use the safety-rejected decision.
- API requests validate fixture provenance, spot scope, supported timeframes,
  engine settings, and non-weakened risk bounds. Validation errors do not echo input.
- Five legacy tests initially failed because their expectations depended on unsafe
  target fallback or on stale data remaining available. Tests now explicitly check
  rejection, or supply actual structural levels for valid BUY/SELL cases.
