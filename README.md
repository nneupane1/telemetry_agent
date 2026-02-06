# GenAI Predictive Interpreter Platform

## Overview
This project is an interpretation layer for predictive maintenance telemetry.

Control-room teams often already have:
- model outputs (MH / MP / FIM),
- marts that make those outputs queryable,
- dashboards that visualize trends and alerts.

What remains manual is interpretation at scale:
- which signals matter for a VIN,
- how to explain risk consistently,
- how to provide auditable evidence behind recommendations,
- how to summarize fleet-level patterns without ad hoc analysis every time.

This platform addresses that gap by combining:
- deterministic agent logic,
- optional LangGraph orchestration,
- optional LangChain + OpenAI narrative generation,
- API-first delivery to React and Streamlit dashboards.

## What This Project Solves
At a practical level, the system automates:
- VIN-level explanation from MH / MP / FIM marts,
- cohort/fleet anomaly summaries,
- evidence consolidation by source model and confidence,
- action-pack generation for operator workflows,
- PDF export,
- approval capture and retrieval.

## What This Project Does Not Do
- It does not retrain predictive models.
- It does not replace Databricks as the data source of truth.
- It does not make autonomous maintenance decisions.
- It does not require live LLM availability to function.

## Architecture At A Glance
```text
Databricks Unity Catalog marts (or sample JSON)
                |
                v
           MartLoader
                |
                v
  GraphRunner (LangGraph if available, deterministic fallback otherwise)
        |                    |                       |
        v                    v                       v
VinExplainerAgent     CohortBriefAgent        EvidenceAgent
        \                    |                      /
         \                   |                     /
          +---- NarrativeComposer (LangChain/OpenAI optional) ----+
                                  |
                                  v
                           FastAPI Endpoints
                                  |
                   +--------------+--------------+
                   |                             |
                   v                             v
            React Dashboard               Streamlit Console
```

## Architecture Tree
```text
telemetry_agent/
|- apps/
|  |- backend-api/
|  |  |- app/
|  |  |  |- agents/
|  |  |  |  |- vin_explainer_agent.py
|  |  |  |  |- cohort_brief_agent.py
|  |  |  |  |- evidence_agent.py
|  |  |  |- workflows/
|  |  |  |  |- graph_runner.py
|  |  |  |  |- narrative.py
|  |  |  |- services/
|  |  |  |  |- genai_interpreter.py
|  |  |  |  |- mart_loader.py
|  |  |  |  |- reference_loader.py
|  |  |  |  |- approval_store.py
|  |  |  |  |- pdf_exporter.py
|  |  |  |- routers/
|  |  |  |  |- vin.py
|  |  |  |  |- cohort.py
|  |  |  |  |- action_pack.py
|  |  |  |  |- chat.py
|  |  |  |  |- export.py
|  |  |  |  |- approval.py
|  |  |  |- models/
|  |  |  |- utils/
|  |  |- app/tests/
|  |  |- Dockerfile
|  |  |- requirements.txt
|  |- dashboard-react/
|  |- dashboard-streamlit/
|- data/
|  |- marts/
|  |- reference/
|  |- sample/
|- deployments/
|  |- docker-compose.yaml
|  |- docker-compose.local-test.yaml
|  |- k8s/
|  |  |- api-deployment.yaml
|  |  |- base/
|  |  |- overlays/
|  |  |- kind/
|  |- terraform/
|- docs/
|- scripts/
|  |- local/
|  |- data_ingest/
|  |- db_migration/
|  |- utils/
|- tests/
```

## Core Backend Flow
1. `MartLoader` pulls VIN/cohort telemetry from:
   - Unity Catalog marts when `DATA_SOURCE=databricks`, or
   - sample JSON fixtures when `DATA_SOURCE=sample`.
2. `ReferenceLoader` merges domain dictionaries from:
   - `data/reference/ref_hi_catalog.yaml`
   - `data/reference/ref_hi_family_map.yaml`
   - `data/reference/ref_confidence_map.yaml`
3. `GraphRunner` executes orchestration stages:
   - VIN: evidence -> summary -> recommendations -> evidence consolidation -> interpretation
   - Cohort: metrics/anomalies -> summary -> interpretation
4. `NarrativeComposer` generates text:
   - via LangChain/OpenAI when configured and available,
   - deterministic templates otherwise.
5. FastAPI routers return typed responses to dashboards, export, and approval flows.

## API Surface
Backend entrypoint: `apps/backend-api/app/main.py`

- `GET /health`
- `GET /vin/{vin}`
- `GET /cohort/{cohort_id}`
- `POST /action-pack/`
- `POST /chat`
- `POST /export/pdf`
- `POST /approval`
- `GET /approval`

## Runtime Modes
### 1) Sample Mode
Use for local validation without Databricks credentials.
- `APP_ENV=local`
- `DATA_SOURCE=sample`

### 2) Databricks Mode
Use for real Unity Catalog marts.
- `DATA_SOURCE=databricks`
- required values:
  - `DATABRICKS_HOST`
  - `DATABRICKS_HTTP_PATH`
  - `DATABRICKS_TOKEN`
  - `DATABRICKS_CATALOG`
  - `DATABRICKS_SCHEMA`

### 3) Optional LLM Mode
Enable richer narrative generation when available.
- `OPENAI_API_KEY`
- `OPENAI_MODEL` (default `gpt-4.1-mini`)
- `FEATURE_LANGGRAPH=true`

If LLM/LangGraph runtimes are unavailable, the system still runs with deterministic behavior.

## Local Run Options
### Option A: Docker Compose
Simple containerized run.

1. Copy `.env.example` to `.env`.
2. Choose `DATA_SOURCE` (`sample` or `databricks`).
3. Start:
```bash
docker compose -f deployments/docker-compose.yaml up --build
```

### Option B: Local Kubernetes On `kind`
Full Kubernetes execution on your machine using real manifests.

Prerequisites:
- Docker
- `kind`
- `kubectl`

Start sample mode:
```powershell
.\scripts\local\start-local-k8s.ps1 -DataSource sample
```

Start Databricks mode:
```powershell
.\scripts\local\start-local-k8s.ps1 -DataSource databricks
```

Stop:
```powershell
.\scripts\local\stop-local-k8s.ps1
```

Detailed runbook: `docs/local-k8s-kind.md`

### Option C: Compose Local-Test Overlay Add-On
Useful for quick local test cycles while preserving baseline deployment logic.

```powershell
.\scripts\local\start-local-test.ps1
.\scripts\local\test-backend-local-mode.ps1
.\scripts\local\stop-local-test.ps1
```

Details: `docs/local-test-addon.md`

## Environment Configuration
Use `.env.example` as the source of truth.

Key variables:
- app/runtime:
  - `APP_ENV`
  - `LOG_LEVEL`
  - `DATA_SOURCE`
- data/marts:
  - `REFERENCE_DIR`
  - `SAMPLE_DATA_FILE`
  - `MART_MH_TABLE`
  - `MART_MP_TABLE`
  - `MART_FIM_TABLE`
  - `MART_COHORT_METRICS_TABLE`
  - `MART_COHORT_ANOMALIES_TABLE`
- Databricks:
  - `DATABRICKS_HOST`
  - `DATABRICKS_HTTP_PATH`
  - `DATABRICKS_TOKEN`
  - `DATABRICKS_CATALOG`
  - `DATABRICKS_SCHEMA`
- LLM features:
  - `OPENAI_API_KEY`
  - `OPENAI_MODEL`
  - `OPENAI_TEMPERATURE`
  - `OPENAI_MAX_TOKENS`
  - `FEATURE_GENAI`
  - `FEATURE_LANGGRAPH`
  - `FEATURE_PDF`
  - `FEATURE_EMAIL`

## Development Commands
From repo root:

```bash
py -3 -m pytest -q
py -3 scripts/utils/verify_config.py
py -3 scripts/data_ingest/load_reference_data.py
py -3 scripts/db_migration/upgrade_schema.py --dry-run
```

From `apps/backend-api`:
```bash
py -3 -m pytest app/tests -q
uvicorn app.main:app --reload
```

From `apps/dashboard-react`:
```bash
npm install
npm run dev
```

From `apps/dashboard-streamlit`:
```bash
pip install -r requirements.txt
streamlit run app/main.py
```

## Deployment Artifacts
- Compose stack: `deployments/docker-compose.yaml`
- Compose test overlay: `deployments/docker-compose.local-test.yaml`
- Kubernetes baseline file: `deployments/k8s/api-deployment.yaml`
- Kubernetes full base manifests: `deployments/k8s/base/*`
- Kubernetes local overlays: `deployments/k8s/overlays/*`
- kind cluster config: `deployments/k8s/kind/cluster-config.yaml`
- Terraform starter: `deployments/terraform/main.tf`

## Operational Guarantees
- Interpretation remains available without live GenAI runtime.
- Evidence summary is explicit and model-source aware.
- Data stays in Databricks marts for real mode.
- Approval records provide traceability for operator decisions.
- API-first design supports multiple UIs on the same backend contract.

## Known Notes
- `reportlab` is required for `/export/pdf`.
- `langgraph` and `langchain` are optional runtime dependencies.
- Production expectation is `APP_ENV=prod` with `DATA_SOURCE=databricks`.
- Local kind workflow requires `kind` and `kubectl` installed on host.

## Documentation Index
- Architecture: `docs/architecture.md`
- Onboarding: `docs/onboarding.md`
- Local Kubernetes: `docs/local-k8s-kind.md`
- Local test overlay: `docs/local-test-addon.md`
- API specification: `docs/api-spec.yaml`
- UI styleguide: `docs/ui-styleguide.md`
- Changelog: `docs/changelog.md`

## License
See `LICENSE`.
