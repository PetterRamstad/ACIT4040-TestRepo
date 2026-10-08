# ACIT4040 AI Interior Design: Approved Architecture

## Goal

Build a modular AI-assisted interior-design system where user preference feedback becomes a measurable preference state, real furniture is retrieved and ranked, valid layouts are generated, and the result is rendered as an inspectable interactive 3D scene.

## Constraints

- Furniture IDs are the source of truth for furniture.
- Generated images must not determine which furniture exists in the final room.
- Initial preference round contains five images, but the system supports repeated adaptive rounds.
- Adaptive selection starts with configurable 70% likely-preference candidates and 30% exploratory candidates.
- Preference stopping is based on configurable stability rather than a fixed number of rounds.
- Retrieval is metadata filtering, vector similarity, then compatibility/ranking.
- Layout starts with deterministic constraints before advanced optimization.
- The agent orchestrates deterministic services and does not replace preference mathematics, vector retrieval, or geometry validation.
- Dataset/model setup is idempotent and reuses compatible artifacts.
- Large datasets are not downloaded during normal application startup or CI.
- Demo mode works with small local fixtures.
- CPU API/web workloads are separated conceptually from GPU inference workloads.
- PostgreSQL stores application state; Qdrant stores embeddings; files/object storage stores large artifacts.

## Architecture

```text
React + R3F
    -> FastAPI API
        -> Preference service
        -> Retrieval service -> Qdrant
        -> Compatibility service
        -> Layout service
        -> Agent orchestration
        -> PostgreSQL

Dataset/model manager
    -> manifests
    -> cached models
    -> processed artifacts
    -> embeddings/indexes

GPU-capable inference adapters remain replaceable and are not required for demo CI.
```

## Vertical delivery strategy

1. Repository/infrastructure health.
2. Dataset registry and idempotent setup.
3. Preference learning vertical slice.
4. Furniture catalog and retrieval vertical slice.
5. Room/layout vertical slice.
6. 3D scene and furniture inspector.
7. Full feedback loop.
8. Research evaluation and experiment logging.
9. Agent orchestration.
10. Production hardening and CI/CD.

## Key interfaces

- `PreferenceEngine.update(feedback) -> PreferenceState`
- `PreferenceEngine.next_candidates(state, candidates) -> list[PreferenceCandidate]`
- `PreferenceEngine.is_stable(state) -> bool`
- `FurnitureRepository.search(filters) -> list[FurnitureItem]`
- `FurnitureRetriever.retrieve(preference, filters, limit) -> list[RankedFurniture]`
- `CompatibilityService.score(items, room) -> list[RankedFurniture]`
- `LayoutEngine.generate(room, furniture) -> Layout`
- `LayoutValidator.validate(room, layout) -> LayoutValidation`
- `EmbeddingProvider.embed_images(images) -> list[Vector]`
- `AgentOrchestrator.next_action(context) -> AgentAction`

## Demo implementation policy

The first implementation uses deterministic local fixtures and an embedding adapter that can operate without downloading a foundation model. A SigLIP2 adapter is added behind the same interface. Real datasets are connected through dataset-provider adapters only after access/format validation. This preserves reproducibility and makes CI independent of large external downloads.
