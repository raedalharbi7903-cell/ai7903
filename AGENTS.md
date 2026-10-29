# Engineering execution rules

- Work only on `feature/crypto-analysis-validation`. Never merge or push to main.
- Preserve the FastAPI / Pydantic / SQLAlchemy backend, sequential AnalysisService
  pipeline, and React / TypeScript / Vite frontend. Reuse existing components.
- Spot-only analytical scope; no automatic trading, order execution, leverage, or
  unsupported profitability claims. SELL is analytical direction, not short execution.
- Synthetic fixtures must remain explicitly labeled. Never fabricate live data,
  metrics, or validation evidence. No unlicensed commercial data integration.
- Confidence is uncalibrated analytical quality until independent validation supports
  calibration. AI narratives cannot override deterministic validation or safety.
- Use only closed candles available at the decision time. Test historical prefixes,
  pivot confirmation, evidence-family independence, and risk rejection.
- Never hide failing checks. Distinguish project defects from environment limitations.
- Update PROJECT_SPEC.md, IMPLEMENTATION_PLAN.md, and PROGRESS.md as evidence changes.
- Keep changes scoped; preserve unrelated working-tree changes.
- Unknown product permissions, providers, and administrative roles remain Decision
  Required, not invented requirements.
- Backend (from backend): `.venv/Scripts/python -m pytest`,
  `.venv/Scripts/python -m ruff check .`,
  `.venv/Scripts/python -m black --check .`,
  `.venv/Scripts/python -m compileall -q app`.
- Frontend (from frontend): `pnpm install --frozen-lockfile`,
  `pnpm exec tsc --noEmit`, `pnpm build`, `pnpm lint`,
  `pnpm format:check`; run test scripts once available.
- A passing build is not product acceptance. Report tested behavior and remaining
  requirements before requesting CTO review.
