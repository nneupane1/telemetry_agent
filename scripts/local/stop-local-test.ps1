$ErrorActionPreference = "Stop"

$root = (Resolve-Path "$PSScriptRoot\..\..").Path
Set-Location $root

Write-Host "Stopping local test stack (overlay)..." -ForegroundColor Cyan
docker compose `
  -f deployments/docker-compose.yaml `
  -f deployments/docker-compose.local-test.yaml `
  down

Write-Host "Local test stack stopped." -ForegroundColor Green
Write-Host "You can continue with normal K8s/deployment workflow unchanged."
