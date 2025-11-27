"""Application configuration settings"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List
import os
import json


# Remove os.environ DATABASE_URL para forçar uso do .env
if "DATABASE_URL" in os.environ:
    if "schema=" in os.environ.get("DATABASE_URL", ""):
        del os.environ["DATABASE_URL"]


class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "TelecomTools Suite"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Sistema de Análise de Telecomunicações e RF"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "sqlite:///./telecom.db"
    
    # Security
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_USE_SECURE_KEY"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External APIs
    OPENCELLID_API_KEY: Optional[str] = None
    ANATEL_API_URL: Optional[str] = "https://sistemas.anatel.gov.br/se/public/view/b/licenciamento.php"
    
    # CORS - Aceita tanto List[str] quanto str (será parseado)
    BACKEND_CORS_ORIGINS: str | List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173",
    ]
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins de string JSON ou CSV para lista"""
        if isinstance(v, list):
            return v
        
        if isinstance(v, str):
            # Tenta parsear como JSON
            if v.startswith("["):
                try:
                    parsed = json.loads(v)
                    print(f"[CORS] Parsed JSON origins: {parsed}")
                    return parsed
                except json.JSONDecodeError as e:
                    print(f"⚠️ [CORS] Erro ao parsear JSON: {e}")
                    print(f"⚠️ [CORS] Valor recebido: {v}")
                    # Retorna localhost como fallback seguro
                    return ["http://localhost:3000"]
            
            # Tenta parsear como CSV
            if "," in v:
                origins = [origin.strip() for origin in v.split(",") if origin.strip()]
                print(f"[CORS] Parsed CSV origins: {origins}")
                return origins
            
            # String única
            print(f"[CORS] Single origin: {v}")
            return [v]
        
        print(f"⚠️ [CORS] Tipo inesperado: {type(v)}, usando padrão")
        return ["http://localhost:3000"]
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 1000
    
    # File uploads
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

print(f"[CONFIG] Database: {settings.DATABASE_URL[:50]}...")
print(f"[CONFIG] CORS Origins: {settings.BACKEND_CORS_ORIGINS}")
print(f"[CONFIG] Environment: {settings.ENVIRONMENT}")
