---
title: Founder-Controlled Design Foundation
document_id: DOC-FRONTEND-DESIGN-001
version: 1.0.0
status: implemented-foundation-product-incomplete
owner: Engineering
reviewers: Founder
last_updated: 2026-10-30
next_review: 2026-11-30
related_documents: [DOC-PROD-MASTER-GOAL-001]
---

# Founder-controlled design

## Purpose

Make provisional styling replaceable without silently promoting it to approved identity.

## Scope

Section 28 of the approved master directive. No final brand, palette, theme, font,
dashboard/results/chart/Command Center/mobile styling or motion is approved.

## Main content

The existing demo's 45 colors, font stack and dark color-scheme value were moved
without selecting replacements into frontend/src/styles/tokens.css.
Semantic --ui-* variables avoid Tailwind's own token namespaces.
frontend/src/styles.css consumes those variables; responsive layout remains provisional.
The current Inter/system fallback is inherited demo configuration, not a selected
Arabic font. No font download, brand asset or final light/dark strategy was added.

frontend/src/design/approval.ts records ten pending categories and no approval
reference. Layout displays a provisional-design notice. Final visual acceptance
remains blocked until explicit founder decisions and desktop/tablet/mobile testing.
No screenshot, responsive-browser or accessibility certification is claimed by
the source-level/DOM tests.

Before final styling: present a concise proposal with alternatives and accessibility
tradeoffs for all affected categories; obtain a traceable explicit founder decision;
update canonical requirements and tokens; implement and verify all three viewports.
Do not treat temporary values as default founder requirements.
Continue backend/data/workflow work while visual approval remains pending.

Tests: scripts/test_design_tokens.py validates centralized colors and references;
frontend/src/design/tokens.test.ts validates the visible pending notice and
approval categories. Initial raw-CSS tests failed because Vitest strips CSS modules;
a Node-only attempt then exposed missing Node types/non-file import URLs.
The final approach uses Python source tests plus actual DOM tests without adding
a dependency or weakening assertions. TypeScript and focused tests pass.

## Related documents

- [Master directive](../02-product/approved-master-execution-goal.md)
- [Canonical requirements](../02-product/canonical-requirements.json)
- [Frontend setup](../../frontend/README.md)

## Change history

- 1.0.0 — Centralized inherited provisional values and recorded final approval gates.
