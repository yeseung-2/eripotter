"""
LLM Service - 로컬 LLM 훈련 및 추론 서비스
"""
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging, sys, traceback, os

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)
logger = logging.getLogger("llm-service")

# ---------- .env ----------
if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv(find_dotenv())

# ---------- FastAPI ----------
app = FastAPI(
    title="LLM Service API", 
    description="로컬 LLM 훈련 및 추론 서비스", 
    version="1.0.0"
)

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
from .router.llm_router import llm_router
from .router.training_router import training_router
from .router.model_router import model_router

# ---------- Include Routers ----------
app.include_router(llm_router, prefix="/api/v1/llm", tags=["LLM"])
app.include_router(training_router, prefix="/api/v1/training", tags=["Training"])
app.include_router(model_router, prefix="/api/v1/model", tags=["Model"])

# ---------- Root Route ----------
@app.get("/", summary="Root")
def root():
    return {
        "status": "ok", 
        "service": "llm-service", 
        "endpoints": ["/api/v1/llm", "/api/v1/training", "/api/v1/model", "/health"]
    }

@app.get("/health", summary="Health Check")
def health_check():
    return {
        "status": "healthy",
        "service": "llm-service",
        "version": "1.0.0"
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
    port = int(os.getenv("PORT", "8005"))
    logger.info(f"💻 LLM 서비스 시작 - 포트: {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info", access_log=True)
