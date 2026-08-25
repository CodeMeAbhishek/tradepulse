"""Application settings. Secrets never logged."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    app_name: str = "tradepulse-api"
    app_version: str = "0.1.0"
    database_url: str = "sqlite:///./tradepulse.db"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Adapter modes: fixture | live (live wired in later phases)
    gleif_mode: str = "fixture"
    gleif_base_url: str = ""
    vlei_verifier_mode: str = "fixture"
    screening_source_mode: str = "fixture"
    opensanctions_api_key: str = ""
    opensanctions_base_url: str = "https://api.opensanctions.org"
    opensanctions_dataset: str = "sanctions"
    opensanctions_match_threshold: float = 0.85
    # live = Yahoo Finance futures (no key); static_demo = labeled offline map only
    price_source_mode: str = "live"
    llm_provider: str = "fixture"
    llm_api_key: str = ""
    llm_prompt_version: str = "invoice-extract-bedrock@1.2.0"
    bedrock_model_id: str = "apac.amazon.nova-lite-v1:0"
    bedrock_max_tokens: int = 3000

    # AWS (leave blank in ECS to use the task role; set AWS_PROFILE locally)
    aws_profile: str = ""
    aws_region: str = "ap-south-1"
    document_storage_backend: str = "memory"
    s3_documents_bucket: str = ""
    s3_documents_prefix: str = "tradepulse/docs/"
    # GCP (Cloud Run / Vertex / GCS)
    gcp_project: str = ""
    gcp_region: str = "asia-south1"
    gcs_documents_bucket: str = ""
    gcs_documents_prefix: str = "tradepulse/docs/"
    vertex_model_id: str = "gemini-2.0-flash-001"
    # local | textract | document_ai (falls back to local)
    text_extract_mode: str = "local"
    textract_poll_seconds: float = 1.0
    textract_max_polls: int = 60
    document_ai_processor_id: str = ""
    document_ai_location: str = "us"


@lru_cache
def get_settings() -> Settings:
    return Settings()
