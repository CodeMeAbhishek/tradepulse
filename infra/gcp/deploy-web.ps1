# Deploy TradePulse Web to Cloud Run (GCP)
# Usage (from repo root):
#   $env:API_URL = "https://tradepulse-api-....run.app"
#   .\infra\gcp\deploy-web.ps1

$ErrorActionPreference = "Stop"
$ProjectId = if ($env:GCP_PROJECT) { $env:GCP_PROJECT } else { "tradepulse-demo" }
$Region = if ($env:GCP_REGION) { $env:GCP_REGION } else { "asia-south1" }
$Repo = "tradepulse"
$ImageName = "web"
$Service = "tradepulse-web"
$ImageTag = "latest"
$ApiService = "tradepulse-api"

gcloud config set project $ProjectId | Out-Null

$ApiUrl = $env:API_URL
if (-not $ApiUrl) {
  $ApiUrl = (gcloud run services describe $ApiService --project=$ProjectId --region=$Region --format="value(status.url)" 2>$null).Trim()
}
if (-not $ApiUrl) { throw "Set API_URL or deploy API first" }
$ApiBase = "$ApiUrl/api/v1"
$Registry = "$Region-docker.pkg.dev/$ProjectId/$Repo"
$ImageUri = "${Registry}/${ImageName}:${ImageTag}"

Write-Host "Project=$ProjectId API=$ApiBase"

cmd /c "gcloud artifacts repositories describe $Repo --location=$Region --project=$ProjectId >nul 2>&1"
if ($LASTEXITCODE -ne 0) { throw "Artifact Registry missing - run deploy-api.ps1 first" }

gcloud auth configure-docker "$Region-docker.pkg.dev" --quiet

Write-Host "Building web image with local Docker..."
docker build -f apps/web/Dockerfile `
  --build-arg "NEXT_PUBLIC_API_BASE_URL=$ApiBase" `
  --build-arg "NEXT_PUBLIC_DATA_MODE=api" `
  -t "${ImageName}:${ImageTag}" .
if ($LASTEXITCODE -ne 0) { throw "docker build failed" }
docker tag "${ImageName}:${ImageTag}" $ImageUri
docker push $ImageUri
if ($LASTEXITCODE -ne 0) { throw "docker push failed" }

Write-Host "Deploying Cloud Run service $Service ..."
gcloud run deploy $Service `
  --project=$ProjectId `
  --region=$Region `
  --image=$ImageUri `
  --platform=managed `
  --allow-unauthenticated `
  --port=3000 `
  --memory=512Mi `
  --cpu=1 `
  --timeout=60 `
  --max-instances=3

if ($LASTEXITCODE -ne 0) { throw "Cloud Run web deploy failed" }

$WebUrl = (gcloud run services describe $Service --project=$ProjectId --region=$Region --format="value(status.url)").Trim()

Write-Host "Updating API CORS for web origin..."
gcloud run services update $ApiService `
  --project=$ProjectId `
  --region=$Region `
  --update-env-vars="CORS_ORIGINS=$WebUrl,http://localhost:3000,http://127.0.0.1:3000" | Out-Null

Write-Host ""
Write-Host "WEB URL: $WebUrl"
Write-Host "API URL: $ApiUrl"
Write-Host "Health:  $ApiUrl/healthz"
