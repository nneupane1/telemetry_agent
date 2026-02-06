# GenAI Predictive Interpreter Platform

## What This Project Solves
Control-room teams already have predictive model outputs and dashboards, but interpretation is still repetitive and inconsistent.

This platform adds a dedicated interpretation layer that:
- reads MH / MP / FIM telemetry from Unity Catalog marts,
- converts signals into auditable narratives,
- produces action-ready recommendations and reports,
- supports approvals and explainability chat.

## Architecture Summary
### 1) Data Layer (Databricks Unity Catalog)
- Source telemetry tables stay in Databricks.
- The app reads from mart views (VIN and cohort level).

### 2) Reference Layer
- YAML dictionaries map signal codes to human terms and families:
  - `data/reference/ref_hi_catalog.yaml`
  - `data/reference/ref_hi_family_map.yaml`
  - `data/reference/ref_confidence_map.yaml`

### 3) Agent Workflow Layer
- Agent orchestration lives in `apps/backend-api/app/workflows/graph_runner.py`.
- Runtime behavior:
  - Uses LangGraph state graphs when available and enabled.
  - Falls back to deterministic orchestration if LangGraph runtime is unavailable.
- Narrative helpers use LangChain prompt patterns via `apps/backend-api/app/workflows/narrative.py`.

### 4) API Layer (FastAPI)
`apps/backend-api/app/main.py` exposes:
- `GET /health`
- `GET /vin/{vin}`
- `GET /cohort/{cohort_id}`
- `POST /action-pack/`
- `POST /chat`
- `POST /export/pdf`
- `POST /approval`
- `GET /approval`

### 5) Dashboard Layer
- Business dashboard: Next.js/React (`apps/dashboard-react`)
- Operator console: Streamlit (`apps/dashboard-streamlit`)

## Repository Structure
```
apps/
  backend-api/
  dashboard-react/
  dashboard-streamlit/
data/
  marts/
  reference/
  sample/
deployments/
  docker-compose.yaml
  k8s/
  terraform/
docs/
scripts/
tests/
```

## Running Locally
### Option A: Sample Mode (no Databricks required)
1. Copy `.env.example` to `.env`.
2. Keep `DATA_SOURCE=sample`.
3. Start services:
   - `docker compose -f deployments/docker-compose.yaml up --build`

### Option B: Databricks Mode (Unity Catalog)
1. Copy `.env.example` to `.env`.
2. Set:
   - `DATA_SOURCE=databricks`
   - `DATABRICKS_HOST`
   - `DATABRICKS_HTTP_PATH`
   - `DATABRICKS_TOKEN`
   - `DATABRICKS_CATALOG`
   - `DATABRICKS_SCHEMA`
3. Optional LLM settings:
   - `OPENAI_API_KEY`
   - `FEATURE_LANGGRAPH=true`
4. Start backend and dashboards.

## Backend Development Commands
From `apps/backend-api`:
- Run unit tests: `py -3 -m pytest app/tests -q`
- Verify config: `py -3 ../../scripts/utils/verify_config.py`
- Build reference cache: `py -3 ../../scripts/data_ingest/load_reference_data.py`

## Deployment Artifacts
- Docker Compose: `deployments/docker-compose.yaml`
- Kubernetes baseline: `deployments/k8s/api-deployment.yaml`
- Terraform starter: `deployments/terraform/main.tf`
- Local test add-on overlay (no K8s changes): `deployments/docker-compose.local-test.yaml`
- Local helper scripts: `scripts/local/*` (see `docs/local-test-addon.md`)

## Current Design Guarantees
- Interpretation is deterministic and auditable even without live LLM runtime.
- Data ownership stays in Databricks marts.
- Agent workflow supports graph orchestration with explicit fallback behavior.
- Dashboards are API-first and role-specific (business vs operations).

## Known Operational Notes
- `reportlab` is required for PDF export endpoint.
- `langgraph` and `langchain` are optional at runtime; if unavailable, deterministic fallback remains active.
- For production, set `APP_ENV=prod` with `DATA_SOURCE=databricks`.
