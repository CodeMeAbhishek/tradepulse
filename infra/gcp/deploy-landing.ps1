# Deploy TradePulse Landing to Cloud Run (GCP)
# Usage (from repo root):
#   .\infra\gcp\deploy-landing.ps1
#
# Mirrors deploy-web.ps1. The landing page is static marketing: it calls no
# API, so there is no CORS step and no API URL to resolve. It only needs to
# know where the review desk lives, which defaults to the deployed web service.

$ErrorActionPreference = "Stop"
$ProjectId = if ($env:GCP_PROJECT) { $env:GCP_PROJECT } else { "tradepulse-demo" }
$Region = if ($env:GCP_REGION) { $env:GCP_REGION } else { "asia-south1" }
$Repo = "tradepulse"
$ImageName = "landing"
$Service = "tradepulse-landing"
$ImageTag = "latest"
$WebService = "tradepulse-web"

gcloud config set project $ProjectId | Out-Null

# Point the call to action at the deployed workbench unless told otherwise.
$DeskUrl = $env:REVIEW_DESK_URL
if (-not $DeskUrl) {
  $WebUrl = (gcloud run services describe $WebService --project=$ProjectId --region=$Region --format="value(status.url)" 2>$null)
  if ($WebUrl) { $DeskUrl = "$($WebUrl.Trim())/workbench" }
}
if (-not $DeskUrl) { throw "Set REVIEW_DESK_URL or deploy apps/web first" }

$Registry = "$Region-docker.pkg.dev/$ProjectId/$Repo"
$ImageUri = "${Registry}/${ImageName}:${ImageTag}"

Write-Host "Project=$ProjectId Desk=$DeskUrl"

cmd /c "gcloud artifacts repositories describe $Repo --location=$Region --project=$ProjectId >nul 2>&1"
if ($LASTEXITCODE -ne 0) { throw "Artifact Registry missing - run deploy-api.ps1 first" }

gcloud auth configure-docker "$Region-docker.pkg.dev" --quiet

Write-Host "Building landing image with local Docker..."
docker build -f apps/landing/Dockerfile `
  --build-arg "NEXT_PUBLIC_REVIEW_DESK_URL=$DeskUrl" `
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

if ($LASTEXITCODE -ne 0) { throw "Cloud Run landing deploy failed" }

$LandingUrl = (gcloud run services describe $Service --project=$ProjectId --region=$Region --format="value(status.url)").Trim()

Write-Host ""
Write-Host "LANDING URL: $LandingUrl"
Write-Host "REVIEW DESK: $DeskUrl"
