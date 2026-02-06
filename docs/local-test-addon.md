# Local Test Add-on (No K8s Changes)

This repository includes a local overlay for POC/testing that is separate from Kubernetes deployment logic.
For local Kubernetes execution, see `docs/local-k8s-kind.md`.

## Principle
- Kubernetes manifests and cloud deployment flow remain untouched.
- Local testing is an add-on overlay only.
- Switching back is immediate: stop overlay and use standard K8s commands.

## Start local test stack
```powershell
.\scripts\local\start-local-test.ps1
```

Uses:
- `deployments/docker-compose.yaml`
- `deployments/docker-compose.local-test.yaml` (overlay)

Ports:
- Backend: `http://localhost:8000`
- React: `http://localhost:3001`
- Streamlit: `http://localhost:8502`

## Stop local test stack
```powershell
.\scripts\local\stop-local-test.ps1
```

## Run backend tests in local mode (temporary env only)
```powershell
.\scripts\local\test-backend-local-mode.ps1
```

This script sets process-only env vars, runs tests, then restores environment.
