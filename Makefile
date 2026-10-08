PYTEST=python -m pytest

lint:
	python -m ruff check .

typecheck:
	python -m mypy apps/api packages --ignore-missing-imports

test:
	$(PYTEST)

test-unit:
	$(PYTEST) tests/unit apps/api/tests -q

build:
	cd apps/frontend && npm install && npm run build

setup:
	python scripts/data/registry.py ensure furniture-fixture

validate-data:
	python scripts/data/verify.py

evaluate:
	python scripts/evaluation/experiment.py

e2e:
	$(PYTEST) tests/e2e -q

pipeline:
	python scripts/pipeline.py full

pipeline-dry-run:
	python scripts/pipeline.py full --dry-run

production-check:
	python scripts/pipeline.py production-check --profile production
