# Architecture

## Core Principle
The system does not replace predictive models. It interprets their outputs consistently at scale.

## Forensic Requirements
1. Input provenance must stay explicit (MH / MP / FIM source lineage).
2. Every recommendation must include evidence and confidence.
3. Narrative generation must be bounded to provided telemetry.
4. Approval decisions must be captured with actor, timestamp, and comment.

## Runtime Layers
### Data acquisition
- `MartLoader` (`apps/backend-api/app/services/mart_loader.py`) reads:
  - Databricks Unity Catalog marts (production)
  - sample JSON fallback (development)

### Semantic mapping
- `ReferenceLoader` (`apps/backend-api/app/services/reference_loader.py`) merges catalog/family/confidence mappings.

### Agentic workflow
- `GraphRunner` (`apps/backend-api/app/workflows/graph_runner.py`):
  - VIN graph nodes: evidence -> summary -> recommendations -> consolidation -> interpretation
  - Cohort graph nodes: metrics/anomalies -> summary -> interpretation
- If LangGraph runtime is missing, sequential fallback executes the same logical stages.

### Narrative composition
- `NarrativeComposer` (`apps/backend-api/app/workflows/narrative.py`) uses LangChain prompt templates.
- If LLM provider/runtime is unavailable, deterministic templates are used.

### API and delivery
- FastAPI routers return interpretation JSON.
- PDF export uses ReportLab.
- Approval endpoints provide operational traceability.

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
- Optional LLM keys configured
- health endpoint monitored (`/health`)
- approval and export workflows validated
