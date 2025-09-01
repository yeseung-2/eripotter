"""
Sharing Service - MSA 프랙탈 구조
"""
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging, sys, traceback, os
from datetime import datetime

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)
logger = logging.getLogger("sharing-service")

logger.info("🚀 Sharing Service 시작 중...")
logger.info("📊 Railway PostgreSQL 데이터베이스 연결 설정 완료")

# ---------- .env ----------
if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv(find_dotenv())

# ---------- Database ----------
from eripotter_common.database import engine
from .domain.entity.sharing_entity import Base

# 데이터베이스 테이블 생성
try:
    Base.metadata.create_all(bind=engine)
    logger.info("✅ 데이터베이스 연결 및 테이블 생성 완료")
except Exception as e:
    logger.error(f"❌ 데이터베이스 연결 실패: {e}")
    raise

# ---------- FastAPI ----------
app = FastAPI(title="Sharing Service API", description="Sharing 서비스", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://eripotter.com",
        "https://www.eripotter.com",
        # 개발용 필요 시 주석 해제
        "http://localhost:3000", "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Import Routers ----------
from .router.sharing_router import sharing_router

# ---------- Include Routers ----------
app.include_router(sharing_router)

# ---------- Root Route ----------
@app.get("/", summary="Root")
def root():
    return {
        "status": "ok", 
        "service": "sharing-service", 
        "endpoints": ["/sharing", "/health", "/metrics"]
    }

@app.get("/health", summary="Health Check")
def health_check():
    return {
        "status": "healthy",
        "service": "sharing-service",
        "timestamp": datetime.now().isoformat()
    }

# ---------- Middleware ----------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"📥 요청: {request.method} {request.url.path} (클라이언트: {request.client.host if request.client else '-'})")
    try:
        response = await call_next(request)
        logger.info(f"📤 응답: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"❌ 요청 처리 중 오류: {e}")
        logger.error(traceback.format_exc())
        raise

# ---------- Entrypoint ----------
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8008"))
    logger.info(f"💻 Sharing Service 시작 - 포트: {port}")
    logger.info("🎯 Railway 배포 준비 완료 - 데이터베이스 연결 설정됨")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info", access_log=True)
