"""Application configuration settings"""

from pydantic_settings import BaseSettings
from typing import Optional, List
import os

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
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173",
    ]
    
    def __init__(self, **data):
        super().__init__(**data)
        # Em produção, adicionar origins customizadas via variável de ambiente
        if self.ENVIRONMENT == "production":
            # Parse custom CORS origins se fornecido
            import json
            cors_env = os.getenv("BACKEND_CORS_ORIGINS")
            if cors_env:
                try:
                    self.BACKEND_CORS_ORIGINS = json.loads(cors_env)
                except:
                    pass  # Manter valores padrão se JSON inválido
    
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

print(f"[CONFIG] Database: {settings.DATABASE_URL[:50]}...")  # Debug

