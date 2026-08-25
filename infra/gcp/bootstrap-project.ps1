# Bootstrap TradePulse GCP project (create + billing + APIs)
# Usage (from repo root):  .\infra\gcp\bootstrap-project.ps1

$ErrorActionPreference = "Stop"
$ProjectId = if ($env:GCP_PROJECT) { $env:GCP_PROJECT } else { "tradepulse-demo" }
$ProjectName = "TradePulse Demo"
$BillingAccount = if ($env:GCP_BILLING_ACCOUNT) { $env:GCP_BILLING_ACCOUNT } else { "011A54-11D5BC-4E4D29" }
$Region = if ($env:GCP_REGION) { $env:GCP_REGION } else { "asia-south1" }

Write-Host "Ensuring project $ProjectId ..."
$exists = $false
cmd /c "gcloud projects describe $ProjectId >nul 2>&1"
if ($LASTEXITCODE -eq 0) { $exists = $true }

if (-not $exists) {
  gcloud projects create $ProjectId --name="$ProjectName"
  if ($LASTEXITCODE -ne 0) { throw "Failed to create project $ProjectId" }
}

gcloud billing projects link $ProjectId --billing-account=$BillingAccount
if ($LASTEXITCODE -ne 0) { throw "Failed to link billing" }

gcloud config set project $ProjectId
Write-Host "Enabling APIs..."
gcloud services enable `
  run.googleapis.com `
  artifactregistry.googleapis.com `
  storage.googleapis.com `
  aiplatform.googleapis.com `
  cloudbuild.googleapis.com `
  iam.googleapis.com `
  secretmanager.googleapis.com `
  --project=$ProjectId

Write-Host ""
Write-Host "Project ready: $ProjectId"
Write-Host "Region default: $Region"
Write-Host "Next: .\infra\gcp\deploy-api.ps1"
