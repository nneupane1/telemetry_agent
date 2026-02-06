# Onboarding

## Prerequisites
- Python 3.11+
- Node.js 20+
- Docker Desktop (optional but recommended)
- Databricks SQL Warehouse credentials for production mode

## First Run
1. Copy `.env.example` to `.env`.
2. Choose mode:
   - `DATA_SOURCE=sample` for local validation.
   - `DATA_SOURCE=databricks` for real telemetry.
3. Choose runtime:
   - Compose: `docker compose -f deployments/docker-compose.yaml up --build`
   - Local Kubernetes (kind): `.\scripts\local\start-local-k8s.ps1 -DataSource sample`
   - Local Kubernetes with Databricks: `.\scripts\local\start-local-k8s.ps1 -DataSource databricks`
4. Stop local Kubernetes when done:
   - `.\scripts\local\stop-local-k8s.ps1`

## Backend Local Loop
From `apps/backend-api`:
1. Install dependencies.
2. Run tests: `py -3 -m pytest app/tests -q`
3. Start API: `uvicorn app.main:app --reload`

## React Dashboard Local Loop
From `apps/dashboard-react`:
1. Install dependencies (`npm install`).
2. Start dev server (`npm run dev`).
3. Ensure `NEXT_PUBLIC_API_BASE_URL` points to backend API.

## Streamlit Local Loop
From `apps/dashboard-streamlit`:
1. Install dependencies.
2. Start app: `streamlit run app/main.py`
3. Ensure `API_BASE_URL` points to backend API.

## Operational Validation
- `GET /health` returns status.
- VIN interpretation endpoint returns recommendations.
- Cohort endpoint returns summary and anomalies.
- Approval endpoint records and retrieves decisions.

## Coding Standards
- Keep LangGraph orchestration as the default execution path.
- Preserve evidence transparency for every recommendation.
- Avoid hardcoding secrets or environment-specific values.
- Keep dashboards mobile-safe and API-driven.
