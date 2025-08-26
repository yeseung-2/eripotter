import os
from dotenv import load_dotenv, find_dotenv
from typing import Optional

# Railway가 아니면 .env 로드
if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv(find_dotenv())

class Settings:
    # 기본 설정
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    SERVICE_NAME = "llm-service"
    PORT = int(os.getenv("PORT", "8005"))
    
    # CORS 설정
    ALLOW_ORIGINS = [
        "https://eripotter.com",
        "https://www.eripotter.com",
        "http://localhost:3000",
        "http://localhost:8080",
    ]
    
    # 모델 설정
    MODEL_CACHE_DIR: str = os.getenv("MODEL_CACHE_DIR", "./models")
    TRAINING_DATA_DIR: str = os.getenv("TRAINING_DATA_DIR", "./data")
    
    # Hugging Face 설정
    HF_TOKEN: Optional[str] = os.getenv("HF_TOKEN")
    HF_MODEL_NAME: str = os.getenv("HF_MODEL_NAME", "microsoft/DialoGPT-medium")
    
    # 훈련 설정
    MAX_LENGTH: int = int(os.getenv("MAX_LENGTH", "512"))
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "4"))
    LEARNING_RATE: float = float(os.getenv("LEARNING_RATE", "5e-5"))
    NUM_EPOCHS: int = int(os.getenv("NUM_EPOCHS", "3"))
    WARMUP_STEPS: int = int(os.getenv("WARMUP_STEPS", "500"))
    
    # GPU 설정
    USE_GPU: bool = os.getenv("USE_GPU", "false").lower() == "true"
    DEVICE: str = "cuda" if USE_GPU else "cpu"
    
    # Redis 설정 (선택사항)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # 로깅 설정
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "llm_service.log")

settings = Settings()
