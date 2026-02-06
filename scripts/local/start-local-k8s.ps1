param(
  [ValidateSet("sample", "databricks")]
  [string]$DataSource = "sample",
  [string]$ClusterName = "telemetry-local"
)

$ErrorActionPreference = "Stop"

function Require-Command {
  param([string]$Name)
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
    throw "Required command '$Name' is not installed or not on PATH."
  }
}

function Get-DotEnvValue {
  param(
    [string]$Path,
    [string]$Key
  )

  if (-not (Test-Path $Path)) {
    return $null
  }

  $line = Select-String -Path $Path -Pattern "^\s*$Key\s*=\s*(.*)$" | Select-Object -Last 1
  if (-not $line) {
    return $null
  }

  $value = $line.Matches[0].Groups[1].Value.Trim()
  if (
    ($value.StartsWith('"') -and $value.EndsWith('"')) -or
    ($value.StartsWith("'") -and $value.EndsWith("'"))
  ) {
    if ($value.Length -ge 2) {
      $value = $value.Substring(1, $value.Length - 2)
    }
  }

  if ($value -eq "") {
    return $null
  }

  return $value
}

function Ensure-DatabricksSecret {
  param([string]$Root)

  $dotenvPath = Join-Path $Root ".env"
  if (-not (Test-Path $dotenvPath)) {
    throw "Databricks mode requires .env file at repo root."
  }

  $required = @(
    "DATABRICKS_HOST",
    "DATABRICKS_HTTP_PATH",
    "DATABRICKS_TOKEN"
  )

  $values = @{}
  foreach ($key in $required) {
    $val = Get-DotEnvValue -Path $dotenvPath -Key $key
    if (-not $val -or ($val -match "<.*>")) {
      throw "Missing valid $key in .env for Databricks mode."
    }
    $values[$key] = $val
  }

  $optional = @(
    "OPENAI_API_KEY",
    "OPENAI_MODEL",
    "OPENAI_TEMPERATURE",
    "OPENAI_MAX_TOKENS"
  )

  foreach ($key in $optional) {
    $val = Get-DotEnvValue -Path $dotenvPath -Key $key
    if ($val) {
      $values[$key] = $val
    }
  }

  $secretArgs = @(
    "create", "secret", "generic", "telemetry-secrets",
    "-n", "telemetry-agent",
    "--dry-run=client",
    "-o", "yaml"
  )

  foreach ($entry in $values.GetEnumerator()) {
    $secretArgs += "--from-literal=$($entry.Key)=$($entry.Value)"
  }

  kubectl apply -f deployments/k8s/base/namespace.yaml | Out-Null
  kubectl @secretArgs | kubectl apply -f - | Out-Null
}

$root = (Resolve-Path "$PSScriptRoot\..\..").Path
Set-Location $root

Require-Command docker
Require-Command kind
Require-Command kubectl

$context = "kind-$ClusterName"
$clusters = (kind get clusters 2>$null)
if (-not ($clusters -contains $ClusterName)) {
  Write-Host "Creating kind cluster '$ClusterName'..." -ForegroundColor Cyan
  kind create cluster --name $ClusterName --config deployments/k8s/kind/cluster-config.yaml
} else {
  Write-Host "kind cluster '$ClusterName' already exists." -ForegroundColor Yellow
}

kubectl config use-context $context | Out-Null

Write-Host "Building local images..." -ForegroundColor Cyan
docker build -t telemetry-backend:local apps/backend-api
docker build -t telemetry-react:local apps/dashboard-react
docker build -t telemetry-streamlit:local apps/dashboard-streamlit

Write-Host "Loading images into kind..." -ForegroundColor Cyan
kind load docker-image telemetry-backend:local --name $ClusterName
kind load docker-image telemetry-react:local --name $ClusterName
kind load docker-image telemetry-streamlit:local --name $ClusterName

if ($DataSource -eq "databricks") {
  Write-Host "Preparing Databricks secret from .env..." -ForegroundColor Cyan
  Ensure-DatabricksSecret -Root $root
  $overlay = "deployments/k8s/overlays/local-kind-databricks"
} else {
  $overlay = "deployments/k8s/overlays/local-kind-sample"
}

Write-Host "Deploying Kubernetes manifests ($DataSource mode)..." -ForegroundColor Cyan
kubectl apply -k $overlay

Write-Host "Waiting for rollouts..." -ForegroundColor Cyan
kubectl -n telemetry-agent rollout status deployment/telemetry-backend --timeout=300s
kubectl -n telemetry-agent rollout status deployment/telemetry-react --timeout=300s
kubectl -n telemetry-agent rollout status deployment/telemetry-streamlit --timeout=300s

Write-Host ""
Write-Host "Local Kubernetes deployment is ready." -ForegroundColor Green
Write-Host "Backend API:  http://localhost:8000/health"
Write-Host "React UI:     http://localhost:3000"
Write-Host "Streamlit UI: http://localhost:8501"
Write-Host ""
Write-Host "Mode: $DataSource"
Write-Host "Cluster: $ClusterName"
