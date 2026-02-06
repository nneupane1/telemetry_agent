$ErrorActionPreference = "Stop"

$root = (Resolve-Path "$PSScriptRoot\..\..").Path
Set-Location $root

Write-Host "Starting local test stack (add-on overlay)..." -ForegroundColor Cyan
docker compose `
  -f deployments/docker-compose.yaml `
  -f deployments/docker-compose.local-test.yaml `
  up -d --build

Write-Host ""
Write-Host "Local test stack is up." -ForegroundColor Green
Write-Host "React UI:     http://localhost:3001"
Write-Host "Streamlit UI: http://localhost:8502"
Write-Host "Backend API:  http://localhost:8000"
Write-Host ""
Write-Host "K8s logic is untouched. Stop this overlay via scripts/local/stop-local-test.ps1."
