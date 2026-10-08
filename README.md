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

## Automated local pipeline

On Windows PowerShell:

```powershell
.\scripts\pipeline.ps1 -Command full
```

On macOS/Linux:

```bash
./scripts/pipeline.sh
```

The pipeline is safe and resumable. It validates the local toolchain, reuses the
fixture data, runs backend/frontend checks, and verifies API health when the API
is already running. Use `--dry-run` to inspect commands without executing them
and `--resume` to reuse completed steps:

```powershell
.\scripts\pipeline.ps1 -Command full -DryRun
.\scripts\pipeline.ps1 -Command full -Resume
```

The production roadmap includes external credentials, PostgreSQL, Qdrant,
object storage, real datasets, and model downloads. Those are intentionally not
provisioned by the local fixture pipeline.

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
