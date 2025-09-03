from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union
from pydantic import field_validator


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/ecommerce"
    
    # JWT
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: Union[str, List[str]] = ["http://localhost:3000", "http://localhost:8000"]
    
    # App
    app_name: str = "E-commerce API"
    debug: bool = True
    
    @field_validator('allowed_origins', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            elif "," in v:
                return [origin.strip() for origin in v.split(",")]
            else:
                return [v]
        return v
    
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
