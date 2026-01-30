from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # Database
    database_url: str = "sqlite:///./health_kiosk.db"
    
    # Gemini API
    gemini_api_key: str
    
    # Face Recognition
    face_similarity_threshold: float = 0.6
    
    # Application
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """설정 싱글톤 인스턴스 반환"""
    return Settings()
