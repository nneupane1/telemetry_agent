# Local Kubernetes (Option B)

This project supports a full local Kubernetes deployment for POC and early validation.

You run:
- Docker
- a local Kubernetes cluster (`kind`)
- the repository Kubernetes manifests

This is real Kubernetes on your machine (pods, services, deployments, manifests), not a mock.

## Prerequisites
- Docker Desktop or Docker Engine
- `kind`
- `kubectl`

## Start Local Kubernetes
Sample mode (no Databricks dependency):
```powershell
.\scripts\local\start-local-k8s.ps1 -DataSource sample
```

Databricks mode (Unity Catalog tables):
```powershell
.\scripts\local\start-local-k8s.ps1 -DataSource databricks
```

Databricks mode reads credentials from repo root `.env`:
- `DATABRICKS_HOST`
- `DATABRICKS_HTTP_PATH`
- `DATABRICKS_TOKEN`

## Endpoints
- Backend API: `http://localhost:8000`
- React dashboard: `http://localhost:3000`
- Streamlit dashboard: `http://localhost:8501`

## Stop Local Kubernetes
```powershell
.\scripts\local\stop-local-k8s.ps1
```

## Manifests Used
- Base manifests: `deployments/k8s/base`
- Local sample overlay: `deployments/k8s/overlays/local-kind-sample`
- Local Databricks overlay: `deployments/k8s/overlays/local-kind-databricks`
- kind cluster config: `deployments/k8s/kind/cluster-config.yaml`

## Notes
- Existing cloud/K8s baseline logic is preserved.
- Local setup uses overlays, so switching back is immediate.
- Ingress manifest is included in base, but local access uses NodePort mappings through kind by default.
