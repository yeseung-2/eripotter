"""
Monitoring Service - FastAPI Application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging, sys, traceback, os
from datetime import datetime
from fastapi.responses import JSONResponse

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("monitoring-service")

# ---------- FastAPI App ----------
app = FastAPI(
    title="Monitoring Service",
    description="공급망 모니터링 서비스",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ---------- CORS 설정 ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# ---------- Main Monitoring Endpoint ----------
@app.get("/monitoring", summary="Monitoring Service Root")
async def monitoring_root():
    """Monitoring Service 루트 엔드포인트"""
    try:
        return {
            "service": "monitoring-service",
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "endpoints": [
                "/monitoring/companies",
                "/monitoring/vulnerabilities", 
                "/monitoring/supply-chain/vulnerabilities",
                "/monitoring/assessments",
                "/monitoring/solutions"
            ]
        }
    except Exception as e:
        logger.error(f"Monitoring root 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Monitoring service error",
                "detail": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

# ---------- Middleware ----------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """요청/응답 로깅 미들웨어"""
    start_time = datetime.now()
    
    # 요청 로깅
    logger.info(f"📥 요청: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        
        # 응답 로깅
        process_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"📤 응답: {request.method} {request.url} - {response.status_code} ({process_time:.3f}s)")
        
        return response
        
    except Exception as e:
        # 오류 로깅
        process_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"❌ 오류: {request.method} {request.url} - {str(e)} ({process_time:.3f}s)")
        logger.error(f"❌ 스택 트레이스: {traceback.format_exc()}")
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

# ---------- Router 등록 ----------
@app.on_event("startup")
async def startup_event():
    """서비스 시작 시 실행"""
    logger.info("🚀 Monitoring Service 시작")
    
    # 라우터 등록
    try:
        from .router.monitoring_router import monitoring_router
        app.include_router(monitoring_router)
        logger.info("✅ Monitoring Router 등록 완료")
    except Exception as e:
        logger.error(f"❌ Monitoring Router 등록 실패: {e}")
        logger.error(f"❌ 스택 트레이스: {traceback.format_exc()}")

@app.on_event("shutdown")
async def shutdown_event():
    """서비스 종료 시 실행"""
    logger.info("🛑 Monitoring Service 종료")

# ---------- Main ----------
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info"
    )
