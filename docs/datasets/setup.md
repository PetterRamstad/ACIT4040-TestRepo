# Dataset setup

Run `make setup` to check the local fixture dataset. Compatible fixture artifacts are reused.

Useful commands:

```bash
python scripts/data/registry.py list
python scripts/data/registry.py ensure furniture-fixture
python scripts/data/registry.py ensure interior-style
python scripts/data/verify.py --json
python scripts/data/interior_inspect.py path/to/interior-dataset
```

`furniture-fixture` is the only dataset expected to be available in normal development and CI. Restricted or large research datasets intentionally report `HUMAN_REQUIRED` or `NEEDS_USER_CONFIRMATION` until their source, license terms, and local archive locations are approved.

Research datasets must be provisioned outside CI and must not be committed or baked into images.
