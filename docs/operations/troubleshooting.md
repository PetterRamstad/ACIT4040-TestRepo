# Troubleshooting

## API cannot be reached from the frontend
Set `VITE_API_URL` to the reachable FastAPI origin and ensure the API CORS configuration allows the frontend origin.

## Dataset is missing
Run `make validate-data`. Research datasets must be provisioned explicitly and are never silently fabricated.

## ML models are unavailable
The demo uses deterministic local embeddings. Provision a supported local model before selecting the SigLIP2 adapter.

## Frontend dependencies cannot install
Run `cd apps/frontend && npm install` in a normal networked development environment. The repository intentionally does not commit `node_modules`.
