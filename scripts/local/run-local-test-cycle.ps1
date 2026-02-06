$ErrorActionPreference = "Stop"

param(
  [switch]$SkipCompose,
  [switch]$KeepStackUp
)

$root = (Resolve-Path "$PSScriptRoot\..\..").Path
Set-Location $root

$composeFiles = @(
  "-f", "deployments/docker-compose.yaml",
  "-f", "deployments/docker-compose.local-test.yaml"
)

function Invoke-LocalCompose {
  param(
    [Parameter(Mandatory = $true)]
    [string[]]$Args
  )
  docker compose @composeFiles @Args
}

try {
  if (-not $SkipCompose) {
    Write-Host "Starting local test overlay stack..." -ForegroundColor Cyan
    Invoke-LocalCompose -Args @("up", "-d", "--build")
  } else {
    Write-Host "SkipCompose enabled: not starting Docker overlay stack." -ForegroundColor Yellow
  }

  Write-Host "Running backend local-mode tests..." -ForegroundColor Cyan
  powershell -ExecutionPolicy Bypass -File "scripts\local\test-backend-local-mode.ps1"

  Write-Host "Local test cycle completed successfully." -ForegroundColor Green
}
catch {
  Write-Host "Local test cycle failed: $($_.Exception.Message)" -ForegroundColor Red
  throw
}
finally {
  if (-not $SkipCompose -and -not $KeepStackUp) {
    Write-Host "Stopping local test overlay stack..." -ForegroundColor Cyan
    try {
      Invoke-LocalCompose -Args @("down")
    }
    catch {
      Write-Host "Warning: unable to stop compose stack cleanly." -ForegroundColor Yellow
    }
  } elseif (-not $SkipCompose -and $KeepStackUp) {
    Write-Host "Overlay stack kept running by request (-KeepStackUp)." -ForegroundColor Yellow
  }
}
