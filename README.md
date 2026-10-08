# ACIT4040 AI Interior Design

A modular AI-assisted interior-design demo built around known furniture IDs, adaptive preference learning, vector retrieval, deterministic layout constraints, a thin orchestration agent, and reproducible DevOps workflows.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python -m uvicorn apps.api.app.main:app --reload
```

Frontend: `cd apps/frontend && npm install && npm run dev`

The demo uses deterministic local fixtures. Large research datasets and ML models are optional and must be provisioned through the manifest system.

## Architecture

- `apps/api`: FastAPI transport layer and application services
- `packages/preference`: adaptive preference state and candidate selection
- `packages/retrieval`: furniture catalog, embeddings, Qdrant adapter and ranking
- `packages/layout`: deterministic room constraints and layout generation
- `packages/agents`: orchestration over deterministic tools
- `scripts/data`: idempotent dataset/model setup
- `scripts/evaluation`: reproducible research metrics
- `apps/frontend`: React/Vite user experience

See `docs/architecture/overview.md` and the approved build plan.

## Important scope note

This repository is an executable foundation/demo, not a claim that every production integration in the approved plan is complete. The deterministic fixture path is intentionally runnable without research datasets or heavyweight ML downloads. See `docs/agent-handoff-protocol.md` and the implementation plan for the remaining production hardening boundaries.
