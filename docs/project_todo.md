# ACIT4040 Project Todo

This checklist mirrors `docs/project_implementation_steps.json`. Mark items here as work progresses, and keep the JSON tracker in sync for machine-readable handoffs.

- [x] Repository bootstrap and runnable demo shell
- [x] Core domain vertical slices
- [x] API and frontend demo flow
- [ ] Dataset registry, licensing, and safe acquisition status
  - [x] Represent fixture and planned research datasets
  - [x] Report `HUMAN_REQUIRED` and `NEEDS_USER_CONFIRMATION` safely
  - [x] Validate local fixture artifacts with checksums
  - [ ] Validate approved restricted dataset archives
- [ ] Interior dataset inspection and preprocessing
  - [x] Inspect room folders, extensions, and file counts
  - [x] Detect duplicate content hashes
  - [x] Detect corrupt PNG/JPEG files
  - [x] Verify filename split/style patterns
  - [ ] Emit warnings for ambiguous metadata
- [ ] Production persistence with PostgreSQL and migrations
- [ ] Background jobs and object storage
- [ ] Security, admin operations, and observability
- [ ] Full production/research data access
  - [ ] Confirm exact interior-style Kaggle URL
  - [ ] Provide/approve DeepFurniture acquisition settings
  - [ ] Provide approved 3D-FRONT/3D-FUTURE archives or mirrors
  - [ ] Decide production furniture catalog source and rights
- [ ] CI/CD and production deployment
