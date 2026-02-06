# Architecture

## Core Principle
The platform does not replace predictive models. It interprets MH/MP/FIM outputs consistently, with auditable evidence and bounded narratives.

## Forensic Requirements
1. Input provenance must stay explicit (MH / MP / FIM source lineage).
2. Recommendations must include evidence and confidence.
3. Narrative generation must remain grounded to provided telemetry.
4. Approval decisions must capture actor, timestamp, and comment.

## Runtime Layers
### Data acquisition and schema validation
- `MartLoader` (`apps/backend-api/app/services/mart_loader.py`) reads:
  - Databricks Unity Catalog marts (`DATA_SOURCE=databricks`)
  - sample JSON fixtures (`DATA_SOURCE=sample`)
- Ingestion is schema-validated before agents consume data.
- Validation behavior:
  - non-strict mode: invalid rows are dropped and logged
  - strict mode (`APP_ENV=prod`): invalid rows raise errors

### Cohort registry
- Cohort selectors are backend-driven through `GET /cohort/list`.
- `MartLoader.list_cohorts()` sources cohort IDs from:
  - sample `cohorts` array in sample mode
  - union of cohort IDs in cohort metrics/anomalies marts in databricks mode

### Semantic mapping
- `ReferenceLoader` (`apps/backend-api/app/services/reference_loader.py`) merges:
  - `ref_hi_catalog.yaml`
  - `ref_hi_family_map.yaml`
  - `ref_confidence_map.yaml`

### Agentic workflow orchestration
- `GraphRunner` (`apps/backend-api/app/workflows/graph_runner.py`) is LangGraph-first:
  - VIN graph: evidence -> summary -> recommendations -> consolidation -> interpretation
  - Cohort graph: metrics/anomalies -> summary -> interpretation

### Narrative composition
- `NarrativeComposer` (`apps/backend-api/app/workflows/narrative.py`) uses LangChain prompt templates and an LLM chain when available.
- Chat with VIN/cohort context is hybrid:
  - deterministic baseline from bounded agent response
  - optional LLM candidate
  - heuristic selector returns the safer/higher-scoring answer

### API and delivery
- FastAPI routers return typed interpretation payloads.
- Chat transport:
  - REST primary: `POST /chat`
  - WebSocket fallback: `WS /chat/ws`
- PDF export uses ReportLab.
- Approval endpoints provide operational traceability.

## Technology Stack
### Backend
- FastAPI, Pydantic, Databricks SQL connector, ReportLab.

### Orchestration and AI
- LangGraph for workflow orchestration.
- LangChain + `langchain-openai` for optional LLM narratives.
- OpenAI-compatible providers supported through `LLM_BASE_URL`.

### Frontend and dashboards
- Next.js + React + TailwindCSS for executive/operator web dashboards.
- Framer Motion for staged transitions and reveal effects.
- React Three Fiber + Drei + Three.js for cinematic telemetry scenes.
- ECharts for operational charting (plus Recharts in selected components).
- Zustand for client-side dashboard state.
- Streamlit for fast operator console workflows.

## Fallback and Reliability Rules
### LangGraph fallback rules
- `FEATURE_LANGGRAPH=true` is the default and expected mode.
- Deterministic orchestration is used only when `FEATURE_ALLOW_DETERMINISTIC_FALLBACK=true` and:
  - LangGraph runtime/package is unavailable, or
  - graph execution raises an exception.
- If fallback is disabled and LangGraph cannot run, the service fails fast.

### LangChain/LLM fallback rules
- Deterministic narratives are used when any of the following is true:
  - no LLM key configured
  - `LLM_PROVIDER=none`
  - provider unsupported
  - LangChain runtime packages unavailable
  - LLM invocation fails at runtime

### Chat transport fallback rules (frontend)
- REST is primary by default.
- If REST latency breaches threshold repeatedly, client switches preference to WebSocket.
- If REST fails, client attempts WebSocket.
- If WebSocket fails while preferred, client resets to REST.

## UI Direction
- Visual language: cinematic control-room look, neon cyan/amber accents, glass panels, high-contrast data surfaces.
- UX intent: executive narrative at top, evidence and actionability immediately below, bounded explainability chat.

## Data Contracts
- VIN: `apps/backend-api/app/models/vin.py`
- Cohort: `apps/backend-api/app/models/cohort.py`
- Action Pack: `apps/backend-api/app/models/action_pack.py`

## Deployment Path
1. Local compose (`deployments/docker-compose.yaml`)
2. Local Kubernetes on kind (`scripts/local/start-local-k8s.ps1`)
3. Kubernetes manifests (`deployments/k8s/base` + `deployments/k8s/overlays`)
4. Terraform bootstrap (`deployments/terraform/main.tf`)

## Production Checklist
- `APP_ENV=prod`
- `DATA_SOURCE=databricks`
- Databricks secrets configured
- LLM settings configured only if narrative LLM mode is required
- health endpoint monitored (`/health`)
- approval/export workflows validated
- schema contract tests and dashboard E2E checks passing
