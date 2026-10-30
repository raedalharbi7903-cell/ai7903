---
title: New Goal — Start Here
document_id: DOC-HANDOVER-START-001
version: 2.0.0
status: verified-scope-product-incomplete
owner: Engineering
reviewers: Founder
last_updated: 2026-10-30
next_review: 2026-11-30
related_documents: [DOC-HANDOVER-001, DOC-HANDOVER-DECISIONS-001]
---

# New Goal start here

## Current continuation point — 2026-10-30

Start with [CURRENT_STATE.md](CURRENT_STATE.md) and the refreshed publication
receipt, not the historical a7f0b72 source checkpoint below. Pending history/audit
work is preserved at 6bf6f3ceecf62efa8500593f882c06bc6a1caae0; no need to rebuild
it. Reinspect the final received feature-branch HEAD and all local changes first.
The complete 31-section approved source and 101 grouped canonical requirements
remain binding; do not narrow the new Goal to history or scaffolding. Reconcile
G01–G20 with the current gap overlay and all 23 customer workflows before writing.
No new Goal or implementation sprint is started by this handover. The founder
controls retirement/replacement. The old full-platform objective is not achieved.

## Purpose

Resume the existing platform without rebuilding completed work or losing approval
history. This file is an instruction package, not creation of a new Goal or task.

## Scope

Continue repository raedalharbi7903-cell/ai7903 on
feature/crypto-analysis-validation only. Never merge, force-push or push main.
Source checkpoint a7f0b722512a47cd8087494f5acd129862ad80ec contains the reviewed
identity work; the receiving handover HEAD also includes these documents.

## Main content

### Required first inspection

1. Read AGENTS.md, PROJECT_SPEC.md, IMPLEMENTATION_PLAN.md and PROGRESS.md.
2. Check branch, HEAD, remote refs, working tree including ignored relevant artifacts,
   conflicts and unpushed commits BEFORE modifying anything. Preserve dirty work.
3. Read PROJECT_HANDOVER.md, FOUNDER_DECISIONS.md, IMPLEMENTATION_STATUS.md,
   REMAINING_WORK.md and the final handover receipt/delivery SHA.
4. Confirm the handover source code and tests have not changed unexpectedly.
   Recover original reviewed work through Git history, not by replacing current files.
5. Treat normalized evidence files and hosted runs as dated/SHA-scoped evidence,
   not a promise that future changes have passed tests.

### Existing foundations to reuse

One AnalysisService/sequential pipeline; immutable input snapshots; registry and
contracts; the 24 canonical components and four extensions; advanced typed output;
fixture-only API guard; strict frontend API parser and real HTTP tests; existing
risk/validation/backtest guards; SQLAlchemy/Alembic foundation; default-deny
identity dependencies; CI/container scripts.
Do not build a second pipeline, duplicate the frontend, restore old unsafe methods
or reimplement completed scaffolding merely because historical prose says future.

### Approval boundaries

All FD01-FD19 requirements are retained. Exactly eleven Command Center sections;
one founder-only administrative identity with MFA; no staff delegation.
AI is subordinate to deterministic safety. No customer-facing chat, automatic
customer opportunity scanning/alerts or trading execution.
Arabic-first and Saudi-first are requirements, not delivered capabilities.
Final pricing is deferred until measured operating cost; 169 SAR is not approved.
PostgreSQL is intended production DB; independent environments required.
No external customer-data AI transfer or paid commitment without founder approval.

Green routine fixes/tests/docs may proceed within the approved scope.
Yellow internal changes must be reported. Public API/decision behavior, major
dependencies, baseline/Manifest/Handbook, sensitive permissions and product
strategy changes need explicit red-level approval. Provider-neutral architecture
does not authorize choosing paid services or customer-data transfers.

### Resume process

Carry G01-G20 and EXT-DATA/AI/AUTH/PAY/INFRA/OPS/REG into the new Goal.
Reconcile older proposed documents using FOUNDER_DECISIONS.md; preserve their
historical content and approval provenance. Resolve unknown contracts, formulas,
provider licenses, permissions, recovery policies and release conditions instead
of inventing final decisions.
Implement approved missing work in dependency-aware packages; update progress,
requirement-to-evidence links, security review and complete delivery reports.
Run relevant tests, repair root causes, preserve nonfinite/prefix/no-repaint/
risk/Option-A regressions and meaningful actual API/frontend integration.
Do not weaken production denial merely to demonstrate login/live behavior.
Do not mark empirical calibration or commercial acceptance from synthetic tests.

### Validation entry points

Root: `backend/.venv/Scripts/python scripts/verify.py` on Windows, or use
backend/.venv/bin/python on Linux. Read scripts/verify.py for exact 17 gate commands.
Use scripts/audit_documents.py for local Markdown file links.
Hosted workflow additionally builds and runs the non-root backend container,
production denial and packaged migration smoke.
No backend type-checker is presently configured. Local Docker is unavailable;
hosted Docker evidence must be inspected by exact SHA.
Treat protected dependency-store permissions as environment issues, not a reason
to skip checks or invent success.

### Recovery and closure

Evidence includes a standalone pack of old unreachable Git objects; do not merge
or restore drafts automatically. Follow evidence/README.md for isolated inspection.
Never delete this handover, original reports, verified tests or the current branch.
Only the founder retires the old execution Goal after the final remote verification.
The handover does not mark the old full-product objective achieved.
No implementation or new documentation sprint was started by this handover.

## Related documents

- [Project handover](PROJECT_HANDOVER.md)
- [Founder requirements](FOUNDER_DECISIONS.md)
- [Inventory](IMPLEMENTATION_STATUS.md)
- [Backlog](REMAINING_WORK.md)
- [Checklist](GOAL_TRANSITION_CHECKLIST.md)
- [Repository rules](../../AGENTS.md)

## Change history

- 2.0.0 — Added current handover overlay; original source/status evidence preserved.

- 1.0.0 — Added source-grounded continuation and safety instructions.
