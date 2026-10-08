# Production Readiness Status

## Local fixture profile

The local pipeline is automated through:

```powershell
.\scripts\pipeline.ps1 -Command full
```

or:

```bash
./scripts/pipeline.sh
```

It validates the local toolchain, reuses fixture data, runs backend and frontend
tests/checks, builds the frontend, and verifies API health. Pipeline state and
logs are stored under `.pipeline/` and are intentionally ignored by Git.

## Automated status

- Environment and local dependency checks: **AUTOMATED**
- Fixture dataset setup and validation: **AUTOMATED**
- Fixture model/embedding/index stages: **AUTOMATED / REUSED**
- Python tests, Ruff, and mypy: **AUTOMATED**
- Frontend typecheck, tests, and build: **AUTOMATED**
- Temporary local API startup and `/health`/`/ready` checks: **AUTOMATED**
- Dry-run, resume, and force flags: **AUTOMATED**

## Not provisioned by the local profile

The following remain outside the fixture profile and require infrastructure,
credentials, licensing decisions, or separate implementation work:

- PostgreSQL migrations and production persistence
- Production authentication and secrets
- Managed Qdrant and object storage
- Licensed research datasets and heavyweight model downloads
- Production embeddings and catalog indexing
- Cloud deployment, DNS, billing, backups, and disaster recovery
- Human visual, 3D usability, licensing, and UX review

These are reported as **BLOCKED**, **HUMAN_REQUIRED**, or
**SKIPPED_OPTIONAL**, rather than being represented as successful local checks.
