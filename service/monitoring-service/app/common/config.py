import os
from dotenv import load_dotenv, find_dotenv

# Railway가 아니면 .env 로드
if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv(find_dotenv())

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    ALLOW_ORIGINS = [
        "https://sme.eripotter.com",
        "http://localhost:3000",
        "http://localhost:8080",
    ]
    SERVICE_NAME = "monitoring-service"
    PORT = int(os.getenv("PORT", "8004"))

settings = Settings()
