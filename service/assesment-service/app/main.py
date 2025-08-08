from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import os
import logging
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 로거 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 콘솔 출력
        logging.FileHandler('assessment.log')  # 파일 출력
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Assessment Service",
    description="평가 관련 마이크로서비스",
    version="1.0.0"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 연결
def get_database_url():
    return os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/dbname")

def get_db_engine():
    database_url = get_database_url()
    return create_engine(database_url)

@app.get("/health", summary="Health Check")
async def health_check():
    logger.info("👌👌👌Health check requested for assessment service")
    return {"status": "healthy", "service": "assessment-service"}

@app.get("/health/db", summary="Database Health Check")
async def db_health_check():
    """
    데이터베이스 연결 상태를 확인합니다.
    """
    logger.info("🎸🎸🎸Database health check requested for assessment service")
    try:
        engine = get_db_engine()
        with engine.connect() as connection:
            # auth 테이블 존재 여부 확인
            result = connection.execute(text("SELECT COUNT(*) FROM auth"))
            count = result.scalar()
            
        logger.info(f"🎸🎸🎸Database health check successful for assessment service - auth table count: {count}")
        return {
            "status": "healthy",
            "database": "connected",
            "auth_table_count": count,
            "message": "Database connection successful"
        }
    except SQLAlchemyError as e:
        logger.error(f"🎸🎸🎸Database connection failed for assessment service: {str(e)}")
        raise HTTPException(
            status_code=503, 
            detail=f"Database connection failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"🎸🎸🎸Unexpected error in assessment service database health check: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Unexpected error: {str(e)}"
        )

@app.get("/", summary="Root")
async def root():
    logger.info("🖊️🖊️🖊️Root endpoint accessed for assessment service")
    return {
        "message": "Assessment Service",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "db_health": "/health/db"
        }
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Assessment Service on port 8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)
