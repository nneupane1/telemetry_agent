$ErrorActionPreference = "Stop"

$root = (Resolve-Path "$PSScriptRoot\..\..").Path
$backend = Join-Path $root "apps\backend-api"

$oldAppEnv = [Environment]::GetEnvironmentVariable("APP_ENV", "Process")
$oldDataSource = [Environment]::GetEnvironmentVariable("DATA_SOURCE", "Process")
$oldLanggraph = [Environment]::GetEnvironmentVariable("FEATURE_LANGGRAPH", "Process")

try {
  [Environment]::SetEnvironmentVariable("APP_ENV", "local", "Process")
  [Environment]::SetEnvironmentVariable("DATA_SOURCE", "sample", "Process")
  [Environment]::SetEnvironmentVariable("FEATURE_LANGGRAPH", "false", "Process")

  Set-Location $root
  Write-Host "Running repo tests in local test mode..." -ForegroundColor Cyan
  py -3 -m pytest -q

  Set-Location $backend
  Write-Host "Checking API import in local test mode..." -ForegroundColor Cyan
  py -3 -c "from app.main import app; print('backend-import-ok')"

  Write-Host "Local mode tests completed." -ForegroundColor Green
}
finally {
  [Environment]::SetEnvironmentVariable("APP_ENV", $oldAppEnv, "Process")
  [Environment]::SetEnvironmentVariable("DATA_SOURCE", $oldDataSource, "Process")
  [Environment]::SetEnvironmentVariable("FEATURE_LANGGRAPH", $oldLanggraph, "Process")
  Set-Location $root
  Write-Host "Process environment restored (ready for normal K8s workflow)." -ForegroundColor Yellow
}
