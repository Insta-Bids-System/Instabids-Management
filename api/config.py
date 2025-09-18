from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Supabase
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY", "")
    supabase_service_key: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    
    # API
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_env: str = os.getenv("API_ENV", "development")
    
    # JWT
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_access_token_expire_minutes: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    jwt_refresh_token_expire_days: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "30"))
    
    # CORS
    cors_origins: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    
    # Rate Limiting
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    rate_limit_period: int = int(os.getenv("RATE_LIMIT_PERIOD", "3600"))

    # OpenAI / SmartScope
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    smartscope_model: str = os.getenv("SMARTSCOPE_MODEL", "gpt-4.1-mini")
    smartscope_max_output_tokens: int = int(os.getenv("SMARTSCOPE_MAX_OUTPUT_TOKENS", "1200"))
    smartscope_temperature: float = float(os.getenv("SMARTSCOPE_TEMPERATURE", "0.2"))
    smartscope_confidence_threshold: float = float(os.getenv("SMARTSCOPE_CONFIDENCE_THRESHOLD", "0.75"))

    class Config:
        env_file = ".env"

settings = Settings()