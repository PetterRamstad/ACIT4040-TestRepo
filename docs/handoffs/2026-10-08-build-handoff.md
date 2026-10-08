# Task 1-21 consolidated handoff

## What was implemented
- Monorepo skeleton with FastAPI API, React/Vite frontend, Python domain packages, data manifests/fixtures, Docker and GitHub Actions.
- Five-image initial preference round with adaptive selection defaults of 70% likely-preference and 30% exploration.
- Preference uncertainty, confidence, history and stability state.
- Deterministic embedding provider plus isolated SigLIP2 adapter contract.
- Furniture IDs remain authoritative and fixture catalog preserves unknown metadata.
- Retrieval abstraction with metadata filtering, ranking and an in-memory Qdrant-compatible adapter.
- Deterministic room layout generation and collision/boundary validation.
- Agent orchestration layer that requests more preference data while unstable and proceeds to retrieval once stable.
- FastAPI endpoints for health, readiness, preference, furniture, rooms, layouts, agent and admin status.
- Frontend shell, preference cards, auth placeholders, room scene/inspector components and typed API helper.
- Dataset manifest/verification scripts, evaluation fixture, Dockerfiles and CI workflow.

## What was learned
- The demo must remain dependency-light so CI does not need research datasets or heavyweight ML models.
- The 70/30 split for a five-item round yields two exploratory candidates when the likely count is floor(0.70 * 5)=3.
- Fixture layout generation must place items incrementally; placing all items at the room center immediately creates deterministic collisions.
- The local environment could run Python tests but could not complete npm dependency installation within the available network/time window.

## Decisions and rationale
- Used local fixture providers as the executable baseline. Production adapters are replaceable and require explicit provisioning.
- Kept agent orchestration thin and deterministic. Geometry and furniture identity are never invented by the agent.
- Used in-memory Qdrant-compatible behavior for the demo while keeping the Qdrant interface explicit.
- Kept PostgreSQL-compatible persistence as a future integration boundary rather than claiming a live database migration was verified in this environment.

## Interfaces for downstream work
- Preference: `PreferenceEngine.initial_candidates`, `update`, `next_candidates`, `is_stable`.
- Retrieval: `FurnitureRetriever.retrieve`, `QdrantVectorStore.ensure_collection/upsert/search`.
- Layout: `LayoutEngine.generate`, `LayoutValidator.validate`, `LayoutScorer.score`.
- Agent: `AgentOrchestrator.next_action`.
- API: `/health`, `/ready`, `/preferences/*`, `/furniture/*`, `/rooms/*`, `/layouts/*`, `/agent/next`, `/admin/status`.

## Tests and verification
- `python -m pytest -q`: 21 passed.
- `python scripts/data/verify.py`: fixture validation ok.
- `python scripts/evaluation/experiment.py`: deterministic fixture metrics emitted.
- `python -m compileall -q apps packages scripts tests`: passed.
- `npm --prefix apps/frontend install --no-audit --no-fund`: timed out in this environment.
- `npm --prefix apps/frontend run build`: not validly verifiable without installed dependencies and therefore not claimed as passing.

## Known limitations
- PostgreSQL persistence, real Qdrant service integration, production authentication, R3F/Three.js rendering, and real ML model execution are scaffolded or abstracted, not production-complete.
- Frontend dependencies were not installed in the build environment.
- No research dataset was downloaded by CI or local setup.

## Next-agent instructions
Treat this report as the current implementation baseline. Preserve furniture-ID authority, adaptive preference behavior, deterministic layout validation, and the no-large-data-in-repository rule. Before productionizing, replace fixture persistence/providers incrementally and add integration tests against PostgreSQL/Qdrant in an environment where those services and frontend dependencies are available.
