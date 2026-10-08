# ACIT4040 AI Interior Design
## Build-from-Scratch Project Specification

> Status: Build specification / target architecture  
> Purpose: Provide one concrete target for rebuilding the project from an empty repository.  
> Primary principle: **reuse existing data first, download only what is missing, preprocess only what is necessary, and make every setup step idempotent.**

---

# 1. Project Goal

Build an AI-assisted interior-design system that learns a user's interior-design preferences and uses those preferences to recommend and arrange real furniture assets inside a room.

The system should not simply generate an attractive picture. The important distinction is:

**User preference -> measurable preference representation -> real furniture retrieval -> compatibility/ranking -> room layout -> interactive 3D scene -> user feedback -> updated preference**

The generated room should therefore be explainable and inspectable.

A user should be able to:

1. Create an account.
2. Complete an initial preference round using room images.
3. Like, dislike, or rate images.
4. Have the system learn a preference representation.
5. Define a room.
6. Receive furniture recommendations based on the learned preference.
7. Generate a room using actual furniture assets.
8. Inspect individual furniture items.
9. See why an item was selected.
10. Replace, remove, or keep furniture.
11. Give feedback on the generated design.
12. Generate an improved version.

The research system should additionally support:

- repeated preference rounds
- adaptive image selection
- preference uncertainty
- held-out evaluation
- retrieval evaluation
- layout evaluation
- experiment arms/baselines
- reproducible datasets and model versions
- logs and experiment history

---

# 2. Core Architecture

The complete system is divided into these stages:

```text
                    ┌──────────────────────┐
                    │       Frontend       │
                    │ React + TypeScript   │
                    │ Three.js / R3F       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       API Layer      │
                    │       FastAPI        │
                    └──────────┬───────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Preference      │  │ Furniture       │  │ Room/Layout     │
│ Learning        │  │ Retrieval       │  │ Planning        │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌───────────────────────────────────────────────────────────┐
│                    Data / ML Layer                        │
│                                                           │
│ Room images | Furniture metadata | 3D assets | Embeddings│
└───────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌───────────────────────────────────────────────────────────┐
│                    Persistent Storage                      │
│ PostgreSQL | Qdrant | Files/Object Storage | Manifests    │
└───────────────────────────────────────────────────────────┘
```

---

# 3. Most Important Architectural Rule

## Do not make the image generator the source of truth for furniture

The system should retrieve known furniture objects.

A generated image may be useful later for visualization, but it must not determine which furniture exists in the final room.

The source of truth should be:

```text
Furniture ID
    |
    +-- metadata
    +-- image(s)
    +-- dimensions
    +-- material
    +-- colour
    +-- style
    +-- category
    +-- 3D model
    +-- embedding
```

The 3D scene then references the furniture ID.

Example:

```json
{
  "furniture_id": "chair_000123",
  "position": {
    "x": 1.2,
    "y": 0.0,
    "z": 2.4
  },
  "rotation": {
    "y": 1.57
  }
}
```

The frontend resolves `chair_000123` to the corresponding GLB/GLTF asset.

---

# 4. Repository Structure

Start from an empty repository with this structure:

```text
acit4040/
│
├── apps/
│   ├── api/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── config.py
│   │   │   ├── dependencies.py
│   │   │   │
│   │   │   ├── auth/
│   │   │   ├── users/
│   │   │   ├── preferences/
│   │   │   ├── furniture/
│   │   │   ├── rooms/
│   │   │   ├── layouts/
│   │   │   ├── feedback/
│   │   │   └── admin/
│   │   │
│   │   └── tests/
│   │
│   └── frontend/
│       ├── src/
│       │   ├── app/
│       │   ├── components/
│       │   │   ├── layout/
│       │   │   ├── preference/
│       │   │   ├── furniture/
│       │   │   ├── room/
│       │   │   ├── scene/
│       │   │   ├── feedback/
│       │   │   └── common/
│       │   ├── features/
│       │   │   ├── preference-learning/
│       │   │   └── room-design/
│       │   ├── hooks/
│       │   ├── lib/
│       │   ├── services/
│       │   ├── types/
│       │   └── main.tsx
│       └── tests/
│
├── packages/
│   ├── preference/
│   ├── retrieval/
│   ├── compatibility/
│   ├── layout/
│   ├── scene/
│   ├── datasets/
│   └── agents/
│
├── data/
│   ├── raw/
│   │   ├── room_images/
│   │   ├── 3d_front/
│   │   ├── 3d_future/
│   │   ├── ade20k/
│   │   └── objaverse/
│   │
│   ├── processed/
│   │   ├── room_images/
│   │   ├── furniture/
│   │   └── layouts/
│   │
│   ├── embeddings/
│   │   ├── rooms/
│   │   ├── furniture/
│   │   └── objects/
│   │
│   ├── indexes/
│   │   └── qdrant/
│   │
│   └── manifests/
│
├── models/
│   ├── downloaded/
│   └── manifests/
│
├── scripts/
│   ├── data/
│   │   ├── check.py
│   │   ├── download.py
│   │   ├── verify.py
│   │   ├── preprocess.py
│   │   ├── manifest.py
│   │   └── registry.py
│   │
│   ├── models/
│   ├── embeddings/
│   ├── indexes/
│   └── evaluation/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── data/
│   ├── e2e/
│   └── research/
│
├── docs/
│   ├── architecture/
│   ├── datasets/
│   ├── research/
│   ├── operations/
│   └── superpowers/
│
├── docker/
│   ├── api/
│   ├── frontend/
│   ├── workers/
│   └── qdrant/
│
├── .github/
│   └── workflows/
│
├── docker-compose.yml
├── Makefile
├── pyproject.toml
├── .env.example
├── .gitignore
└── README.md
```

Keep modules small. A file should normally have one clear responsibility.

---

# 5. Technology Stack

## Frontend

Use:

- React
- TypeScript
- Vite
- React Three Fiber
- Three.js
- `@react-three/drei`
- a small state-management solution only where necessary
- standard CSS or a small UI styling system

Avoid putting business logic directly inside large React components.

The frontend should mostly:

- display state
- collect user input
- call API services
- render 3D scenes
- display loading/error/success states

---

# 6. Backend

Use:

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Qdrant
- PyTorch
- Hugging Face Transformers

Optional:

- Redis
- Celery/RQ or another job queue
- object storage

Do not introduce infrastructure that is not needed for the MVP.

---

# 7. ML Components

The initial implementation should use established pretrained models.

Potential model responsibilities:

### Room-image embedding

Use a vision-language embedding model such as:

- SigLIP/SigLIP2
- CLIP-compatible model

Purpose:

```text
room image -> vector
```

### Furniture-image embedding

```text
furniture image -> vector
```

The same embedding family should be preferred when comparing room preferences with furniture appearance, unless experiments show a better alternative.

### Object detection / segmentation

For optional furniture extraction from room images:

- Grounding DINO
- SAM/SAM2

These are useful for identifying furniture objects in images.

They should not be required for the first MVP if the dataset already contains sufficient structured furniture information.

### Text embeddings

Optional:

- Sentence Transformers

Useful for:

- style descriptions
- material descriptions
- textual product metadata
- semantic explanations

---

# 8. Dataset Strategy

Dataset handling is a first-class subsystem.

The project must never assume that a dataset is already present.

At the same time, it must never blindly download a dataset that already exists.

The rule is:

```text
CHECK
  ↓
VALIDATE
  ↓
REUSE IF COMPATIBLE
  ↓
DOWNLOAD IF MISSING
  ↓
PREPROCESS IF NECESSARY
  ↓
VERIFY
  ↓
CREATE MANIFEST
```

This applies to:

- datasets
- pretrained models
- processed data
- embeddings
- vector indexes
- generated assets

---

# 9. Primary Existing Room Dataset

Use the existing preprocessed room-image dataset already associated with the project as the primary room-image source.

Source currently documented by the project:

```text
https://drive.google.com/file/d/1WE0fgRKybEdBSbu9UXOgeBikWNGBDV-Q/view
```

Do not rebuild the entire room-image preprocessing pipeline unless validation shows that the dataset is incompatible with the new project.

The first setup process should:

1. Check whether the dataset directory exists.
2. Check its manifest.
3. Check file count.
4. Check required metadata.
5. Check checksums where available.
6. Check dataset version.
7. Check preprocessing version.
8. Reuse it if compatible.
9. Otherwise explain what is missing or incompatible.

The exact original schema, licensing, size, and preprocessing implementation must be verified before treating them as fixed facts.

---

# 10. Additional Data Required

The project needs more than room images.

## 10.1 3D-FRONT

Purpose:

- furnished room layouts
- room structure
- semantic room information
- relationships between furniture and rooms
- research/evaluation of layouts

Use it primarily as a research and layout dataset.

Do not commit it to Git.

Do not place it inside Docker images.

The dataset manager should support downloading it when permitted.

---

# 11. 3D-FUTURE

Purpose:

- realistic furniture assets
- furniture categories
- 3D geometry
- furniture appearance
- dimensions and related metadata

This is particularly important for the 3D furniture pipeline.

The pipeline should convert compatible assets into the project's normalized format.

Target:

```text
dataset asset
    ↓
validate
    ↓
normalize metadata
    ↓
validate geometry
    ↓
normalize model
    ↓
generate thumbnail
    ↓
generate embedding
    ↓
store furniture record
```

---

# 12. Optional ADE20K

ADE20K can be used for:

- semantic segmentation experiments
- room/object segmentation experiments
- computer-vision baselines

It should be optional.

Do not make it a mandatory runtime dependency if the core project does not need it.

The setup command should clearly report:

```text
ADE20K: optional
Status: not installed
Reason: not required for MVP
```

---

# 13. Optional Objaverse

Objaverse can be used as a secondary 3D asset source.

Do not download the entire dataset automatically.

Instead:

```text
Objaverse
    ↓
metadata filtering
    ↓
furniture category filtering
    ↓
license filtering
    ↓
format filtering
    ↓
geometry validation
    ↓
selected assets only
```

This avoids enormous downloads and avoids blindly accepting incompatible or unusable assets.

---

# 14. Commercial Furniture Catalog

A separate commercial catalog should eventually be supported.

Examples could include:

- IKEA
- other furniture providers
- a project-owned catalog

Do not automatically scrape commercial websites.

Instead define a provider interface:

```python
class FurnitureProvider(Protocol):
    def list_items(self) -> list[FurnitureItem]:
        ...

    def get_item(self, item_id: str) -> FurnitureItem:
        ...

    def get_asset(self, item_id: str) -> FurnitureAsset:
        ...
```

Then each provider can have its own approved import mechanism.

This keeps research datasets separate from real commercial inventory.

---

# 15. Dataset Registry

Create a central dataset registry.

Example:

```yaml
datasets:
  room_images:
    required: true
    source: existing_project_dataset
    version: "v1"
    preprocessing_version: "v1"

  3d_front:
    required: true
    source: official_dataset
    version: "v1"

  3d_future:
    required: true
    source: official_dataset
    version: "v1"

  ade20k:
    required: false
    source: official_dataset

  objaverse:
    required: false
    source: official_dataset
```

The exact versions should be pinned after dataset validation.

---

# 16. Dataset Manifest

Every processed dataset should have a manifest.

Example:

```json
{
  "dataset": "room_images",
  "version": "v1",
  "source": "project_room_dataset",
  "preprocessing_version": "v1",
  "created_at": "2026-01-01T00:00:00Z",
  "file_count": 1000,
  "valid_file_count": 1000,
  "checksum": "..."
}
```

The manifest determines whether an artifact can be reused.

---

# 17. Automatic Setup

The main command should be:

```bash
make setup
```

It should perform:

```text
make setup
    |
    +-- Check environment
    |
    +-- Check datasets
    |      |
    |      +-- valid -> reuse
    |      +-- missing -> download
    |      +-- invalid -> repair/reprocess
    |
    +-- Check models
    |      |
    |      +-- present -> reuse
    |      +-- missing -> download
    |
    +-- Check preprocessing
    |      |
    |      +-- current -> reuse
    |      +-- missing/outdated -> preprocess
    |
    +-- Check embeddings
    |      |
    |      +-- current -> reuse
    |      +-- missing/outdated -> generate
    |
    +-- Check vector indexes
    |      |
    |      +-- current -> reuse
    |      +-- missing/outdated -> build
    |
    +-- Validate everything
    |
    +-- Produce setup report
```

---

# 18. Setup Must Be Idempotent

Running:

```bash
make setup
```

twice must not rebuild everything.

Example:

```text
$ make setup

Room dataset:
  found
  version: v1
  valid: yes
  action: reuse

3D-FRONT:
  found
  version: v1
  valid: yes
  action: reuse

3D-FUTURE:
  found
  version: v1
  valid: yes
  action: reuse

SigLIP:
  found
  checksum: valid
  action: reuse

Room embeddings:
  found
  model_version: siglip-v1
  action: reuse

Furniture index:
  found
  compatible: yes
  action: reuse

Setup complete.
```

---

# 19. Do Not Automatically Download Large Data During Normal Startup

This distinction is important.

Use:

```bash
make setup
```

for:

- datasets
- models
- preprocessing
- embeddings
- indexes

Use:

```bash
make dev
```

or:

```bash
docker compose up
```

for starting the application.

This prevents a simple application restart from unexpectedly downloading hundreds of gigabytes.

---

# 20. Data Download States

The downloader should support four states:

### Missing

```text
download
```

### Present and valid

```text
reuse
```

### Present but incompatible

```text
explain
reprocess/update
```

### Requires manual acceptance/credentials

```text
stop
explain exact manual step
```

Never silently fail.

---

# 21. Preprocessing Pipeline

Every preprocessing step should have a version.

Example:

```text
raw data
   ↓
validate_raw()
   ↓
normalize_metadata()
   ↓
normalize_images()
   ↓
normalize_models()
   ↓
generate_metadata()
   ↓
generate_embeddings()
   ↓
build_index()
```

Each output should know which input version produced it.

---

# 22. Room Image Preprocessing

For each room image:

1. Verify file.
2. Verify image format.
3. Normalize orientation.
4. Resize according to model requirements.
5. Preserve original image.
6. Generate stable room ID.
7. Store metadata.
8. Generate embedding.
9. Add to manifest.

Never overwrite raw files.

---

# 23. Furniture Preprocessing

For each furniture item:

1. Validate metadata.
2. Validate image.
3. Validate model.
4. Validate geometry.
5. Determine category.
6. Determine dimensions.
7. Normalize coordinate system.
8. Normalize scale.
9. Generate preview.
10. Generate embedding.
11. Store normalized furniture record.
12. Add to manifest.

---

# 24. Furniture Data Model

Minimum:

```python
FurnitureItem(
    id: str,
    source: str,
    source_id: str,
    name: str | None,
    category: str,
    room_types: list[str],
    style: list[str],
    colors: list[str],
    materials: list[str],
    width: float,
    depth: float,
    height: float,
    image_path: str,
    model_path: str | None,
    embedding_id: str | None,
)
```

Do not require every field to be known.

Unknown metadata should be represented explicitly rather than invented.

---

# 25. Preference Representation

The preference model should have two parts:

```text
Preference State
├── embedding
├── interpretable attributes
├── confidence
├── uncertainty
├── history
└── round information
```

Example:

```json
{
  "embedding": "...",
  "styles": {
    "modern": 0.82,
    "minimal": 0.73,
    "traditional": 0.12
  },
  "colors": {
    "neutral": 0.81,
    "dark": 0.45
  },
  "materials": {
    "wood": 0.70,
    "metal": 0.40
  },
  "uncertainty": 0.18,
  "round": 4
}
```

The embedding is the main retrieval representation.

The metadata exists for:

- explanation
- filtering
- evaluation
- debugging
- research

---

# 26. Initial Preference Learning

Start with five room images.

The UI should present something similar to:

```text
Which rooms match your taste?

[ Image A ] [ Image B ] [ Image C ]
[ Image D ] [ Image E ]

Like     Neutral     Dislike
```

The user submits feedback.

The backend updates the preference state.

---

# 27. Multiple Preference Rounds

The system should support:

```text
Round 1
  ↓
learn preference
  ↓
select informative images
  ↓
Round 2
  ↓
learn preference
  ↓
...
  ↓
stable preference
```

Do not permanently hard-code exactly five images.

Five should be the initial round.

---

# 28. Adaptive Candidate Selection

The next preference images should not simply be random.

Candidate selection should consider:

```text
Preference uncertainty
+
candidate diversity
+
expected information gain
+
exploration
+
current preference similarity
```

The exact algorithm can initially be simple.

A strong MVP can use:

```text
70% likely-preference candidates
30% exploratory candidates
```

The ratio should later become configurable.

---

# 29. Preference Stopping

Do not force users through unnecessary rounds.

The system should calculate preference stability.

Example:

```text
Round 1 -> unstable
Round 2 -> unstable
Round 3 -> improving
Round 4 -> stable
```

Then show:

```text
Your preferences are stable enough to start designing.
```

The threshold must be configurable and evaluated experimentally.

---

# 30. Furniture Retrieval

Pipeline:

```text
Preference vector
       |
       ▼
Metadata filters
       |
       ▼
Candidate pool
       |
       ▼
Vector similarity
       |
       ▼
Top 50
       |
       ▼
Compatibility ranking
       |
       ▼
Top 10
```

Use Qdrant for vector retrieval.

Suggested collection:

```text
interior_furniture_v1
```

---

# 31. Retrieval Filters

Before vector similarity, filter where possible:

- category
- room type
- dimensions
- availability
- source
- model availability
- license
- material
- style
- colour

This reduces irrelevant candidates.

---

# 32. Furniture Ranking

A furniture score can combine:

```text
score =
    preference_similarity
  + style_compatibility
  + color_compatibility
  + material_compatibility
  + room_compatibility
  + scale_compatibility
  - constraint_penalties
```

Weights must be configurable.

Do not hide them inside random code.

---

# 33. Explainability

For every selected item, the API should be able to produce:

```json
{
  "furniture_id": "chair_000123",
  "reason": [
    "Matches your preference for modern furniture",
    "Uses a neutral colour palette",
    "Fits the requested room size",
    "Compatible with the selected table"
  ]
}
```

Do not show raw vector similarity values to normal users.

---

# 34. Room Representation

Minimum:

```python
Room(
    id: str,
    type: str,
    width: float,
    length: float,
    height: float,
    doors: list[Door],
    windows: list[Window],
)
```

Furniture placement:

```python
Placement(
    furniture_id: str,
    x: float,
    y: float,
    z: float,
    rotation_y: float,
)
```

---

# 35. Layout Planning

Start with deterministic constraints.

Required constraints:

- furniture inside room
- no furniture collisions
- door clearance
- window clearance where required
- walkable paths
- minimum spacing
- functional relationships
- reasonable orientation

Only after this works should the project introduce more complex optimization.

---

# 36. Layout Objective

A layout can be scored with:

```text
layout_score =
      preference_score
    + style_score
    + functionality_score
    + accessibility_score
    + visual_quality_score
    - collision_penalty
    - boundary_penalty
    - door_penalty
    - path_penalty
```

Keep every weight configurable.

---

# 37. Layout Optimization

Initial implementation:

```text
Generate candidate layouts
        ↓
Validate constraints
        ↓
Score layouts
        ↓
Keep best
```

Possible algorithms:

- random search
- simulated annealing
- genetic algorithm
- constraint optimization

Do not start with an LLM agent controlling geometry.

---

# 38. 3D Scene

The scene should be deterministic.

```text
Room
  |
  +-- walls
  +-- floor
  +-- ceiling
  +-- doors
  +-- windows
  +-- furniture
       |
       +-- GLB/GLTF
       +-- position
       +-- rotation
       +-- scale
```

React Three Fiber renders the result.

---

# 39. Furniture Inspector

Clicking furniture should open an inspector.

Show:

```text
Name
Brand/source
Category
Dimensions
Material
Colour
Style
Price, if known
Asset source
Why selected
```

Actions:

```text
Keep
Replace
Remove
Like
Dislike
```

---

# 40. Provenance

The UI must clearly distinguish:

```text
Research dataset asset
```

from:

```text
Commercial catalog item
```

Never imply that a research dataset item can be purchased if it cannot.

---

# 41. Frontend User Flow

The main flow should be:

```text
Landing
  ↓
Login / Register
  ↓
Discover your style
  ↓
Preference round 1
  ↓
Preference refinement
  ↓
Preference stable
  ↓
Define room
  ↓
Generate design
  ↓
Interactive 3D room
  ↓
Inspect furniture
  ↓
Replace / remove / keep
  ↓
Feedback
  ↓
Improve design
```

---

# 42. Frontend Design Principles

The frontend should be:

- simple
- spacious
- readable
- responsive
- accessible
- visually calm
- consistent
- predictable

Avoid:

- excessive gradients
- excessive animations
- tiny controls
- unexplained icons
- displaying technical ML information
- large walls of text
- unnecessary modal dialogs

---

# 43. Loading Behaviour

Every async operation needs a clear state.

Required states:

```text
idle
loading
success
error
retry
```

Example:

```text
Generating your room...

[ progress / spinner ]

This may take a little while.
```

Never leave the user staring at a frozen button.

---

# 44. Error Behaviour

Errors should be actionable.

Bad:

```text
Failed to fetch
```

Better:

```text
We could not connect to the design service.

Check that the backend is running and try again.

[Retry]
```

Technical errors should be logged for developers while the user sees a readable message.

---

# 45. API Structure

Suggested endpoints:

```text
POST   /auth/register
POST   /auth/login
GET    /auth/me

GET    /preferences/state
POST   /preferences/rounds
POST   /preferences/feedback
GET    /preferences/history
POST   /preferences/next-candidates

POST   /rooms
GET    /rooms/{room_id}

POST   /designs/generate
GET    /designs/{design_id}

GET    /furniture
GET    /furniture/{id}
POST   /furniture/{id}/feedback

POST   /layouts/generate
POST   /layouts/validate

GET    /health
GET    /ready
```

Keep API schemas separate from internal ML classes.

---

# 46. Database

PostgreSQL should store application state.

Core tables:

```text
users
preference_sessions
preference_rounds
preference_feedback
preference_states
rooms
designs
design_items
furniture_feedback
experiments
jobs
```

Do not store large binary datasets directly in PostgreSQL.

---

# 47. Qdrant

Qdrant stores embeddings.

Collections should be versioned.

Examples:

```text
room_embeddings_v1
furniture_embeddings_v1
object_embeddings_v1
```

The collection name should correspond to the embedding pipeline version.

---

# 48. File Storage

Large files belong in:

```text
data/
models/
assets/
```

or object storage.

Do not store large models or datasets in Git.

Do not bake large datasets into application Docker images.

---

# 49. Job System

Expensive tasks should be asynchronous.

Examples:

```text
dataset preprocessing
embedding generation
3D processing
layout generation
large retrieval jobs
model inference
```

The API should return a job ID where appropriate.

Example:

```json
{
  "job_id": "job_123",
  "status": "queued"
}
```

Frontend states:

```text
queued
running
completed
failed
```

---

# 50. GPU Architecture

Separate CPU web/API workloads from GPU workloads.

Recommended:

```text
CPU server
  |
  +-- frontend
  +-- API
  +-- PostgreSQL
  +-- Qdrant
  |
  +---- GPU worker
           |
           +-- PyTorch
           +-- SigLIP
           +-- DINO
           +-- SAM2
```

The GPU worker can later run on a GPU machine or RunPod-style infrastructure.

For local development, it should also be possible to run everything locally where hardware permits.

---

# 51. Docker

Use Docker for:

- API
- frontend
- PostgreSQL
- Qdrant
- workers

Do not use Docker as the mechanism for downloading the entire research dataset during every build.

Use mounted persistent volumes.

---

# 52. Docker Compose Profiles

Recommended:

```text
default
demo
ml
gpu
```

Example:

```bash
docker compose --profile demo up --build
```

Demo mode should work without the complete ML dataset.

Full mode should use:

```bash
make setup
docker compose --profile ml up --build
```

---

# 53. Makefile

The project should provide a simple command interface.

Required:

```bash
make setup
make dev
make test
make lint
make format
make typecheck
make build
make e2e
make clean
make reset-data
```

Additional:

```bash
make setup-status
make validate-data
make rebuild-index
make evaluate
```

---

# 54. Exact Build Order

Do not build everything at once.

Build in this order.

## Phase 1: Repository

Create:

```text
apps/
packages/
scripts/
tests/
docs/
data/
models/
```

Add:

- Git
- Python environment
- Node environment
- `.env.example`
- Makefile
- README

Test:

```bash
make lint
make test
```

---

## Phase 2: Infrastructure

Start:

- PostgreSQL
- Qdrant

Add:

```text
/health
/ready
```

Test:

```bash
docker compose up
curl http://localhost:8000/health
```

---

## Phase 3: Dataset Manager

Implement:

```text
check
download
verify
preprocess
manifest
registry
```

First support the existing room dataset.

Then add 3D-FRONT.

Then add 3D-FUTURE.

Test idempotency.

Run:

```bash
make setup
make setup
```

The second execution should mostly reuse existing artifacts.

---

## Phase 4: Model Manager

Add model registry.

Example:

```yaml
models:
  room_embedder:
    name: ...
    version: v1

  furniture_embedder:
    name: ...
    version: v1
```

Check local cache before downloading.

---

## Phase 5: Room Embeddings

Implement:

```text
image
  ↓
model
  ↓
embedding
  ↓
stored vector
```

Create deterministic tests with small fixtures.

---

## Phase 6: Preference Learning

Implement:

```text
initial candidates
feedback
preference update
uncertainty
next candidate selection
stopping condition
```

Do not connect the frontend yet.

Test the complete preference pipeline from Python.

---

## Phase 7: Furniture Pipeline

Implement:

```text
metadata
images
3D models
normalization
embeddings
Qdrant
```

Create:

```text
interior_furniture_v1
```

Test retrieval with known fixtures.

---

## Phase 8: Retrieval

Implement:

```text
preference
  ↓
filters
  ↓
Qdrant
  ↓
compatibility
  ↓
ranked furniture
```

Evaluate:

- Recall@K
- Precision@K
- NDCG
- MRR

---

## Phase 9: Room and Layout

Implement room models.

Then:

```text
candidate furniture
  ↓
layout generation
  ↓
constraint validation
  ↓
layout scoring
```

Test:

- collisions
- boundaries
- door clearance
- path clearance
- functional constraints

---

## Phase 10: 3D Scene

Implement:

```text
room model -> Three.js scene
furniture ID -> GLB
placement -> transform
```

First make a static scene.

Then add interactions.

---

## Phase 11: Backend API

Expose the working Python systems through FastAPI.

Do not start by writing dozens of endpoints.

Expose only the completed capabilities.

---

## Phase 12: Frontend

Build in this order:

1. app shell
2. authentication
3. preference screen
4. preference rounds
5. room setup
6. design generation
7. 3D scene
8. furniture inspector
9. replacement/removal
10. feedback

---

# 55. MVP Definition

The first working version is:

```text
5 room images
      ↓
user ratings
      ↓
preference vector
      ↓
Qdrant furniture retrieval
      ↓
top furniture
      ↓
rule-based layout
      ↓
Three.js room
```

The user can:

- complete preference selection
- create a room
- generate a design
- inspect furniture
- remove furniture
- replace furniture
- give feedback

Do not add an autonomous agent before this works.

---

# 56. Agent Architecture

The agent is an orchestration layer.

It should not replace:

- vector retrieval
- geometry validation
- layout constraints
- preference mathematics

Potential tools:

```text
get_user_preference_state
get_preference_uncertainty
select_preference_candidates
record_preference_feedback
update_preference_model
evaluate_preference_stability

retrieve_furniture
rank_furniture_candidates
check_furniture_compatibility

generate_room_layout
evaluate_layout

request_more_preference_data
finish_preference_learning
```

The agent decides what should happen next.

Specialized deterministic services perform the actual work.

---

# 57. Testing Strategy

Use several levels.

## Unit

Test:

- preference calculations
- similarity
- metadata filtering
- ranking
- compatibility
- geometry
- layout constraints
- manifest validation

## Integration

Test:

```text
API -> PostgreSQL
API -> Qdrant
preference -> retrieval
retrieval -> layout
```

## Data tests

Test:

- dataset manifest
- missing files
- corrupted files
- duplicate IDs
- invalid metadata
- incompatible versions

## E2E

Test:

```text
register
  ↓
preference round
  ↓
room
  ↓
generate
  ↓
inspect
  ↓
feedback
```

---

# 58. Research Evaluation

Preference learning:

- pairwise accuracy
- Spearman correlation
- Kendall correlation
- NDCG
- preference stability

Retrieval:

- Recall@K
- Precision@K
- NDCG
- MRR

Layout:

- collision rate
- boundary violations
- door violations
- path violations
- functional validity

User evaluation:

- perceived preference match
- perceived usefulness
- explainability
- ease of use
- satisfaction

---

# 59. Experimental Baselines

At minimum compare:

```text
Baseline 1
Fixed questionnaire

Baseline 2
Random preference images

Baseline 3
Adaptive preference selection

Baseline 4
Adaptive selection + preference model

Baseline 5
Adaptive + retrieval + layout
```

This makes it possible to demonstrate whether each system component contributes value.

---

# 60. Versioning

Version independently:

```text
code version
dataset version
preprocessing version
model version
embedding version
index version
experiment version
```

Example:

```text
code: v0.4.0
room dataset: v1
furniture dataset: v1
preprocessing: v2
SigLIP: model-x
embedding: room-siglip-v1
index: furniture-index-v3
```

Never silently mix incompatible artifacts.

---

# 61. Logging

Every important operation should have:

```text
timestamp
request_id
user_id where appropriate
job_id where appropriate
operation
status
duration
model_version
dataset_version
error
```

Do not log sensitive user information unnecessarily.

---

# 62. Observability

Track:

- API latency
- job duration
- failed jobs
- model inference time
- GPU utilization
- GPU memory
- dataset processing duration
- embedding generation duration
- Qdrant latency
- database errors

Research-specific metrics:

- preference round count
- preference stability
- retrieval quality
- layout validity

---

# 63. Admin Interface

Admin functionality should include:

```text
System health
Dataset status
Model status
Worker status
Job queue
Failed jobs
User studies
Experiment status
Evaluation results
```

The admin should not expose sensitive user information unnecessarily.

---

# 64. Security

Implement:

- password hashing
- authentication
- authorization
- secure environment variables
- input validation
- CORS configuration
- rate limiting where appropriate
- safe file handling
- no secrets in Git

Production deployment should use HTTPS.

---

# 65. CI/CD

Pull requests should run:

```text
Python lint
Python type check
Python tests
Frontend lint
Frontend type check
Frontend build
Frontend tests
Docker build
Data fixture validation
```

CI must not download the complete research datasets.

Use small test fixtures.

---

# 66. Deployment

Development:

```bash
make setup
make dev
```

Production should use:

```text
frontend
api
postgres
qdrant
worker
reverse proxy
```

GPU workers can be deployed separately.

Use immutable image tags such as:

```text
service:git-sha
```

Do not deploy only `latest`.

---

# 67. Backups

Back up:

- PostgreSQL
- experiment state
- user preference state where required
- dataset manifests
- configuration
- important generated metadata

Datasets themselves should be reproducibly downloadable rather than treated as database backups.

---

# 68. README Quick Start

The README should start with this.

```bash
# 1. Clone
git clone <repository-url>
cd acit4040

# 2. Configure
cp .env.example .env

# 3. Prepare datasets, models and indexes
make setup

# 4. Start development services
make dev

# 5. Run tests
make test
```

Then provide:

```text
Frontend:
http://localhost:5173

API:
http://localhost:8000

API docs:
http://localhost:8000/docs

Qdrant:
http://localhost:6333
```

The actual ports should come from the project's `.env` and Docker Compose configuration rather than being duplicated throughout the codebase.

---

# 69. README Troubleshooting

Include common cases.

## Dataset missing

```text
make setup
```

## Dataset requires acceptance

Explain:

1. Which dataset is blocked.
2. Why it is blocked.
3. Where to obtain access.
4. Where to place the files.
5. Which validation command to run.

## Model missing

```bash
make setup
```

## Qdrant unavailable

```bash
docker compose up qdrant
```

## API unavailable

```bash
docker compose logs api
```

## Frontend cannot connect

Check:

```text
VITE_API_URL
CORS
API health endpoint
network
```

## GPU unavailable

Run the CPU-compatible development/demo pipeline where possible.

---

# 70. Environment Variables

Use `.env.example`.

Example categories:

```text
APP_ENV
API_HOST
API_PORT

DATABASE_URL

QDRANT_URL

DATA_ROOT
MODEL_ROOT

ROOM_DATASET_PATH
FURNITURE_DATASET_PATH

HF_HOME
TRANSFORMERS_CACHE

GPU_ENABLED

VITE_API_URL
```

Do not hard-code local paths.

---

# 71. Coding Standards

Python:

- type hints
- Pydantic models
- small functions
- explicit error handling
- Ruff
- pytest
- mypy or equivalent

TypeScript:

- strict TypeScript
- explicit domain types
- ESLint
- small components
- no `any` unless justified

General:

- descriptive names
- no unexplained magic numbers
- configuration instead of constants
- no dead code
- no duplicated business logic
- tests for important behaviour
- comments should explain why, not what

---

# 72. Git Workflow

Use small commits.

Examples:

```text
feat: add dataset registry
feat: add room image validation
feat: add preference state
feat: add furniture retrieval
feat: add layout constraints

fix: handle missing furniture assets
test: add preference stability tests
docs: add dataset setup guide
```

Avoid:

```text
update stuff
changes
final
new version
```

Pull requests should explain:

- what changed
- why
- how it was tested
- whether data/model versions changed

---

# 73. Development Commands

Target command interface:

```bash
make setup
make setup-status

make dev
make build

make test
make test-unit
make test-integration
make e2e

make lint
make typecheck
make format

make validate-data
make rebuild-index
make evaluate

make clean
make reset-data
```

Dangerous commands such as `reset-data` should require an explicit confirmation.

---

# 74. What Not to Build First

Do not begin with:

- autonomous agents
- complex multi-agent systems
- automatic web scraping
- commercial product purchasing
- photorealistic rendering
- perfect room generation
- massive Objaverse downloads
- custom foundation models
- unnecessary microservices

First prove:

```text
preference
→ retrieval
→ layout
→ 3D
```

---

# 75. Recommended Milestones

## Milestone 1

Repository + Docker + API + frontend skeleton.

Definition:

```text
make dev
```

starts successfully.

---

## Milestone 2

Dataset manager.

Definition:

```text
make setup
```

detects, validates and reuses existing data.

---

## Milestone 3

Preference learning.

Definition:

User feedback produces a stable preference representation.

---

## Milestone 4

Furniture retrieval.

Definition:

Preference produces relevant furniture candidates.

---

## Milestone 5

Layout.

Definition:

Furniture is placed without invalid collisions or room-boundary violations.

---

## Milestone 6

3D frontend.

Definition:

The actual retrieved furniture appears in the interactive scene.

---

## Milestone 7

Feedback loop.

Definition:

User feedback changes the next generated design.

---

## Milestone 8

Research evaluation.

Definition:

Baselines and metrics can be executed reproducibly.

---

## Milestone 9

Agent orchestration.

Definition:

The agent can coordinate the already-tested services.

---

# 76. Definition of Done

The project is considered functionally complete when:

- [ ] user can register/login
- [ ] user can complete preference rounds
- [ ] preference state is stored
- [ ] preference uncertainty is available
- [ ] room dimensions can be configured
- [ ] furniture is retrieved from known assets
- [ ] furniture compatibility is evaluated
- [ ] a valid room layout can be generated
- [ ] furniture is rendered in 3D
- [ ] user can inspect furniture
- [ ] user can replace furniture
- [ ] user can remove furniture
- [ ] user can provide feedback
- [ ] feedback affects subsequent recommendations
- [ ] datasets can be prepared automatically
- [ ] existing datasets are reused
- [ ] preprocessing is versioned
- [ ] models are cached and reused
- [ ] embeddings are cached and reused
- [ ] indexes are versioned
- [ ] unit tests exist
- [ ] integration tests exist
- [ ] E2E flow works
- [ ] CI passes
- [ ] README contains full setup instructions
- [ ] dataset licenses and access requirements are documented
- [ ] research evaluation can be reproduced

---

# 77. First Implementation Sprint

If starting tomorrow, implement only these items first:

### Step 1

Create repository structure.

### Step 2

Create Python and TypeScript projects.

### Step 3

Create Docker Compose with:

```text
api
frontend
postgres
qdrant
```

### Step 4

Create:

```text
GET /health
GET /ready
```

### Step 5

Create the dataset registry.

### Step 6

Implement:

```bash
make setup
```

with only the existing room dataset initially.

### Step 7

Implement room-image validation.

### Step 8

Implement room-image manifest.

### Step 9

Implement room-image embeddings.

### Step 10

Implement the first preference-learning API.

### Step 11

Connect the existing frontend preference UI.

### Step 12

Add furniture data and retrieval.

### Step 13

Add room layout.

### Step 14

Add 3D furniture.

### Step 15

Add feedback loop.

Only after these work should the system be expanded.

---

# 78. Final Target Architecture

The final project should look conceptually like:

```text
                           USER
                            |
                            ▼
                    ┌───────────────┐
                    │ React Frontend│
                    └───────┬───────┘
                            |
                            ▼
                    ┌───────────────┐
                    │    FastAPI    │
                    └───────┬───────┘
                            |
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
   Preference Engine   Retrieval Engine   Layout Engine
          │                 │                 │
          ▼                 ▼                 ▼
   Room Embeddings    Furniture Vectors   Constraints
          │                 │                 │
          └─────────────────┼─────────────────┘
                            ▼
                    ┌───────────────┐
                    │  3D Scene     │
                    │ GLB / GLTF    │
                    └───────────────┘

Persistent systems:

PostgreSQL
    ├── users
    ├── preference state
    ├── rooms
    ├── designs
    └── experiments

Qdrant
    ├── room embeddings
    └── furniture embeddings

Data storage
    ├── raw
    ├── processed
    ├── embeddings
    └── manifests

Model storage
    └── versioned model cache

Dataset manager
    ├── check
    ├── download
    ├── verify
    ├── preprocess
    ├── manifest
    └── reuse

GPU workers
    ├── embeddings
    ├── vision models
    ├── segmentation
    └── expensive inference
```

---

# 79. The Most Important Development Rule

Build vertically, not horizontally.

Do not build:

```text
all frontend
+
all backend
+
all ML
+
all 3D
```

before testing anything.

Instead build one complete vertical slice:

```text
one dataset
    ↓
one model
    ↓
one preference calculation
    ↓
one API endpoint
    ↓
one frontend screen
    ↓
one result
```

Then expand.

This makes the project much easier to debug and gives the team a working system at every major milestone.

---

# 80. Final Build Philosophy

The project should optimize for:

```text
Correctness
    >
Reproducibility
    >
Explainability
    >
Maintainability
    >
Visual quality
    >
Complexity
```

A simple deterministic system that can be tested and explained is more valuable for this project than a complicated autonomous system that cannot be reproduced.

The final research contribution should be demonstrable as a pipeline:

```text
User preference
       ↓
Adaptive preference learning
       ↓
Preference representation
       ↓
Real furniture retrieval
       ↓
Furniture compatibility
       ↓
Constraint-aware room layout
       ↓
Interactive 3D scene
       ↓
User feedback
       ↓
Updated preference
```

That is the core system to build first.
