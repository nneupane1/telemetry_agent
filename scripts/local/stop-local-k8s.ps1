param(
  [string]$ClusterName = "telemetry-local"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command kind -ErrorAction SilentlyContinue)) {
  throw "Required command 'kind' is not installed or not on PATH."
}

Write-Host "Deleting kind cluster '$ClusterName'..." -ForegroundColor Cyan
kind delete cluster --name $ClusterName
Write-Host "Local Kubernetes cluster removed." -ForegroundColor Green
