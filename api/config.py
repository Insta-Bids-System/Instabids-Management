import os
from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # Supabase - Force correct values
    supabase_url: str = os.getenv(
        "SUPABASE_URL", "https://lmbpvkfcfhdfaihigfdu.supabase.co"
    )
    supabase_anon_key: str = os.getenv(
        "SUPABASE_ANON_KEY",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxtYnB2a2ZjZmhkZmFpaGlnZmR1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxMjgzNTIsImV4cCI6MjA3MzcwNDM1Mn0.WH4-iA_FnW1EqGTl-hcpotzqBGgeCutKWBBMaa6Tnmg",
    )
    supabase_service_key: str = os.getenv("SUPABASE_SERVICE_KEY", "")

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_env: str = "development"

    # JWT
    jwt_secret_key: str = "dev-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 30

    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 3600

    # OpenAI / SmartScope
    openai_api_key: str = ""
    smartscope_model: str = "gpt-4-vision-preview"
    smartscope_max_output_tokens: int = 1200
    smartscope_temperature: float = 0.2
    smartscope_confidence_threshold: float = 0.75

    # OpenAI / SmartScope
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    smartscope_model: str = os.getenv("SMARTSCOPE_MODEL", "gpt-4.1-mini")
    smartscope_max_output_tokens: int = int(
        os.getenv("SMARTSCOPE_MAX_OUTPUT_TOKENS", "1200")
    )
    smartscope_temperature: float = float(os.getenv("SMARTSCOPE_TEMPERATURE", "0.2"))
    smartscope_confidence_threshold: float = float(
        os.getenv("SMARTSCOPE_CONFIDENCE_THRESHOLD", "0.75")
    )

    class Config:
        env_file = ".env"


settings = Settings()
