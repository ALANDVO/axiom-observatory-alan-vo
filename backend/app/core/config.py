import os
from pydantic import BaseModel

class Settings(BaseModel):
    app_name: str = "Axiom Observatory"
    version: str = "1.0.0"
    environment: str = os.getenv("ENVIRONMENT", "development")
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8000"))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./axiom_observatory.db")
    auth_mode: str = os.getenv("AUTH_MODE", "demo")
    oidc_issuer_url: str = os.getenv("OIDC_ISSUER_URL", "http://127.0.0.1:8080/realms/axiom")
    oidc_client_id: str = os.getenv("OIDC_CLIENT_ID", "axiom-observatory")
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai-compatible")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")

settings = Settings()
