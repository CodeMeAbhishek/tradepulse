# Deploy TradePulse API to Cloud Run (GCP)
# Usage (from repo root):  .\infra\gcp\deploy-api.ps1

$ErrorActionPreference = "Stop"
$ProjectId = if ($env:GCP_PROJECT) { $env:GCP_PROJECT } else { "tradepulse-demo" }
$Region = if ($env:GCP_REGION) { $env:GCP_REGION } else { "asia-south1" }
$VertexLocation = if ($env:VERTEX_LOCATION) { $env:VERTEX_LOCATION } else { "us-central1" }
$Repo = "tradepulse"
$ImageName = "api"
$Service = "tradepulse-api"
$ImageTag = "latest"

gcloud config set project $ProjectId | Out-Null
$ProjectNumber = (gcloud projects describe $ProjectId --format="value(projectNumber)").Trim()
if (-not $ProjectNumber) { throw "Could not resolve project number" }
$Bucket = "tradepulse-docs-$ProjectNumber"
$Registry = "$Region-docker.pkg.dev/$ProjectId/$Repo"
$ImageUri = "${Registry}/${ImageName}:${ImageTag}"
$RuntimeSa = "$ProjectNumber-compute@developer.gserviceaccount.com"

Write-Host "Project=$ProjectId Number=$ProjectNumber Region=$Region"

Write-Host "Ensuring Artifact Registry..."
cmd /c "gcloud artifacts repositories describe $Repo --location=$Region --project=$ProjectId >nul 2>&1"
if ($LASTEXITCODE -ne 0) {
  gcloud artifacts repositories create $Repo `
    --repository-format=docker `
    --location=$Region `
    --description="TradePulse images" `
    --project=$ProjectId
  if ($LASTEXITCODE -ne 0) { throw "Failed to create Artifact Registry" }
}

Write-Host "Ensuring GCS bucket gs://$Bucket ..."
cmd /c "gcloud storage buckets describe gs://$Bucket --project=$ProjectId >nul 2>&1"
if ($LASTEXITCODE -ne 0) {
  gcloud storage buckets create "gs://$Bucket" `
    --project=$ProjectId `
    --location=$Region `
    --uniform-bucket-level-access
  if ($LASTEXITCODE -ne 0) { throw "Failed to create GCS bucket" }
}

Write-Host "Granting runtime SA storage + Vertex + Document AI roles..."
gcloud projects add-iam-policy-binding $ProjectId `
  --member="serviceAccount:$RuntimeSa" `
  --role="roles/aiplatform.user" `
  --condition=None | Out-Null
gcloud projects add-iam-policy-binding $ProjectId `
  --member="serviceAccount:$RuntimeSa" `
  --role="roles/documentai.apiUser" `
  --condition=None | Out-Null
gcloud storage buckets add-iam-policy-binding "gs://$Bucket" `
  --member="serviceAccount:$RuntimeSa" `
  --role="roles/storage.objectAdmin" | Out-Null

$DocAiProcessorId = if ($env:DOCUMENT_AI_PROCESSOR_ID) { $env:DOCUMENT_AI_PROCESSOR_ID } else { "4e82a553ae8ab8b1" }
$DocAiLocation = if ($env:DOCUMENT_AI_LOCATION) { $env:DOCUMENT_AI_LOCATION } else { "us" }
$WebUrlDefault = "https://tradepulse-web-gk63mqpoca-el.a.run.app"

Write-Host "Building + pushing API image via Cloud Build..."
$CbFile = Join-Path $env:TEMP "tradepulse-api-cloudbuild.yaml"
@"
steps:
  - name: gcr.io/cloud-builders/docker
    args:
      - build
      - -f
      - apps/api/Dockerfile
      - -t
      - $ImageUri
      - .
images:
  - $ImageUri
timeout: 1200s
"@ | Set-Content -Path $CbFile -Encoding utf8

gcloud builds submit `
  --project=$ProjectId `
  --config=$CbFile `
  --timeout=1200s `
  .
if ($LASTEXITCODE -ne 0) { throw "Cloud Build failed" }

# Optional OpenSanctions key from local apps/api/.env (not committed)
$OpenSanctionsKey = ""
$EnvFile = Join-Path $PSScriptRoot "..\..\apps\api\.env"
if (Test-Path $EnvFile) {
  Get-Content $EnvFile | ForEach-Object {
    if ($_ -match '^\s*OPENSANCTIONS_API_KEY=(.+)$') {
      $OpenSanctionsKey = $Matches[1].Trim().Trim('"')
    }
  }
}

$Cors = if ($env:CORS_ORIGINS) { $env:CORS_ORIGINS } else { "$WebUrlDefault,http://localhost:3000,http://127.0.0.1:3000" }

$EnvFilePath = Join-Path $env:TEMP "tradepulse-api-env.yaml"
$EnvLines = @(
  "APP_ENV: production",
  "LLM_PROVIDER: vertex",
  "LLM_PROMPT_VERSION: invoice-extract-vertex@1.0.0",
  "VERTEX_MODEL_ID: gemini-2.0-flash-001",
  "GCP_PROJECT: $ProjectId",
  "GCP_REGION: $VertexLocation",
  "DOCUMENT_STORAGE_BACKEND: gcs",
  "GCS_DOCUMENTS_BUCKET: $Bucket",
  "GCS_DOCUMENTS_PREFIX: tradepulse/docs/",
  "TEXT_EXTRACT_MODE: document_ai",
  "DOCUMENT_AI_PROCESSOR_ID: $DocAiProcessorId",
  "DOCUMENT_AI_LOCATION: $DocAiLocation",
  "GLEIF_MODE: live",
  "GLEIF_BASE_URL: https://api.gleif.org/api/v1",
  "VLEI_VERIFIER_MODE: fixture",
  "SCREENING_SOURCE_MODE: live",
  "PRICE_SOURCE_MODE: live",
  "CORS_ORIGINS: `"$Cors`""
)
if ($OpenSanctionsKey) {
  $EnvLines += "OPENSANCTIONS_API_KEY: $OpenSanctionsKey"
  $EnvLines += "OPENSANCTIONS_BASE_URL: https://api.opensanctions.org"
  $EnvLines += "OPENSANCTIONS_DATASET: sanctions"
}
$EnvLines | Set-Content -Path $EnvFilePath -Encoding utf8

Write-Host "Deploying Cloud Run service $Service ..."
gcloud run deploy $Service `
  --project=$ProjectId `
  --region=$Region `
  --image=$ImageUri `
  --platform=managed `
  --allow-unauthenticated `
  --port=8000 `
  --memory=1Gi `
  --cpu=1 `
  --timeout=300 `
  --max-instances=3 `
  --env-vars-file=$EnvFilePath

if ($LASTEXITCODE -ne 0) { throw "Cloud Run deploy failed" }

$ApiUrl = (gcloud run services describe $Service --project=$ProjectId --region=$Region --format="value(status.url)").Trim()
Write-Host ""
Write-Host "API URL: $ApiUrl"
Write-Host "Ready:   $ApiUrl/readyz"
Write-Host "OpenAPI: $ApiUrl/docs"
Write-Host "Bucket:  gs://$Bucket"
Write-Host "DocAI:   $DocAiProcessorId ($DocAiLocation)"
Write-Host ""
Write-Host "Next: `$env:API_URL='$ApiUrl'; .\infra\gcp\deploy-web.ps1"
