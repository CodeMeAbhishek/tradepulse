# TradePulse GCP deploy (demo)

Project: `tradepulse-demo` · Region: `asia-south1` · Account: `guptanayan312@gmail.com`

## Live URLs

| Service | URL |
|---------|-----|
| Web UI | https://tradepulse-web-gk63mqpoca-el.a.run.app |
| API | https://tradepulse-api-gk63mqpoca-el.a.run.app |
| Ready | https://tradepulse-api-gk63mqpoca-el.a.run.app/readyz |
| OpenAPI | https://tradepulse-api-gk63mqpoca-el.a.run.app/docs |

Prefer `/readyz` for health checks (Cloud Run edge returns Google HTML 404 for `/healthz`, which also breaks browser CORS).

## Mapping

| Capability | GCP service |
|------------|-------------|
| API + Web containers | Cloud Run |
| Images | Artifact Registry (`asia-south1-docker.pkg.dev/tradepulse-demo/tradepulse`) |
| Documents | Cloud Storage (`gs://tradepulse-docs-425653466131`) |
| LLM | Vertex AI Gemini (`gemini-2.0-flash-001`, location `us-central1`) |
| OCR | Document AI OCR processor `tradepulse-ocr` (`4e82a553ae8ab8b1`, location `us`) — local PDF fallback if OCR fails |

## Bootstrap (once)

```powershell
.\infra\gcp\bootstrap-project.ps1
```

## Redeploy

```powershell
$env:GCP_PROJECT = "tradepulse-demo"
.\infra\gcp\deploy-api.ps1
.\infra\gcp\deploy-web.ps1
```

API image builds via Cloud Build; web image uses local Docker (Docker Desktop must be running).
