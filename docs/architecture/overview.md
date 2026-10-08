# Architecture overview

The system is intentionally layered. Furniture IDs remain authoritative. Preference learning proposes candidates, retrieval finds known furniture, compatibility ranks candidates, deterministic layout validates geometry, and the agent only orchestrates these services.

The demo path uses local fixtures. Production ML adapters are replaceable and require explicit provisioning.

## Preference rounds
The first round contains five known furniture candidates. Subsequent rounds are selected adaptively using a 70% likely-preference and 30% exploratory default until stability is reached.
