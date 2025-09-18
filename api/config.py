from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Supabase
    supabase_url: str = "https://lmbpvkfcfhdfaihigfdu.supabase.co"
    supabase_anon_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxtYnB2a2ZjZmhkZmFpaGlnZmR1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxMjgzNTIsImV4cCI6MjA3MzcwNDM1Mn0.WH4-iA_FnW1EqGTl-hcpotzqBGgeCutKWBBMaa6Tnmg"
    supabase_service_key: str = ""
    
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

    class Config:
        env_file = ".env"

settings = Settings()