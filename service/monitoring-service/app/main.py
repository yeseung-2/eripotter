"""
Monitoring Service - MSA 프랙탈 구조
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
logger = logging.getLogger("monitoring-service")

# ---------- .env ----------
if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv(find_dotenv())

# ---------- FastAPI ----------
app = FastAPI(title="Monitoring Service API", description="Monitoring 서비스", version="1.0.0")

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
from .router.monitoring_router import monitoring_router

# ---------- Include Routers ----------
app.include_router(monitoring_router)

# ---------- Root Route ----------
@app.get("/", summary="Root")
def root():
    return {
        "status": "ok", 
        "service": "monitoring-service", 
        "endpoints": ["/monitoring", "/health", "/metrics"]
    }

# ---------- Health Check Route ----------
@app.get("/health", summary="Health Check")
async def health_check():
    """서비스 상태 확인 엔드포인트"""
    try:
        return {
            "status": "healthy",
            "service": "monitoring-service",
            "timestamp": datetime.now().isoformat(),
            "message": "Monitoring service is running",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check 오류: {e}")
        return {
            "status": "unhealthy",
            "service": "monitoring-service",
            "message": f"Health check failed: {str(e)}"
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
    port = int(os.getenv("PORT", "8004"))
    logger.info(f"💻 서비스 시작 - 포트: {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info", access_log=True)
