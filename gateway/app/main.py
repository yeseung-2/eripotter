from fastapi import FastAPI, Request, HTTPException, Path
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import httpx
import os
import logging
from typing import Dict
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 로거 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 콘솔 출력
        logging.FileHandler('gateway.log')  # 파일 출력
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MSA API Gateway",
    description="마이크로서비스 아키텍처를 위한 API 게이트웨이",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI URL
    redoc_url="/redoc"  # ReDoc UI URL
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영환경에서는 구체적인 도메인을 지정해야 합니다
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="MSA API Gateway",
        version="1.0.0",
        description="마이크로서비스 아키텍처를 위한 API 게이트웨이",
        routes=app.routes,
    )
    
    # 서버 정보 추가
    openapi_schema["servers"] = [
        {"url": "http://localhost:8080", "description": "Development server"},
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# 서비스 URL 매핑 (환경 변수에서 가져옴)
SERVICE_REGISTRY: Dict[str, str] = {
    "user": os.getenv("USER_SERVICE_URL", "http://localhost:8001"),
    "product": os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8002"),
    "order": os.getenv("ORDER_SERVICE_URL", "http://localhost:8003"),
}

# 데이터베이스 연결 함수
def get_database_url():
    return os.getenv("DATABASE_URL", "postgresql://postgres:liyjJKKLWfrWOMFvdgPsWpJvcFdBUsks@postgres.railway.internal:5432/railway")

def get_db_engine():
    database_url = get_database_url()
    return create_engine(database_url)

@app.get("/health", summary="Health Check")
async def health_check():
    logger.info("👌👌👌Health check requested")
    return {"status": "healthy", "service": "gateway"}

@app.get("/health/db", summary="Database Health Check")
async def db_health_check():
    """
    데이터베이스 연결 상태를 확인합니다.
    """
    logger.info("🎸🎸🎸Database health check requested")
    try:
        engine = get_db_engine()
        with engine.connect() as connection:
            # auth 테이블 존재 여부 확인
            result = connection.execute(text("SELECT COUNT(*) FROM auth"))
            count = result.scalar()
            
        logger.info(f"🎸🎸🎸Database health check successful - auth table count: {count}")
        return {
            "status": "healthy",
            "database": "connected",
            "auth_table_count": count,
            "message": "Database connection successful"
        }
    except SQLAlchemyError as e:
        logger.error(f"🎸🎸🎸Database connection failed: {str(e)}")
        raise HTTPException(
            status_code=503, 
            detail=f"Database connection failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"🎸🎸🎸Unexpected error in database health check: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Unexpected error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)