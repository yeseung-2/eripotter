"""
Account Service - MSA 프랙탈 구조
"""
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging, sys, traceback, os
from eripotter_common.database.base import get_db_engine

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)
logger = logging.getLogger("account-service")

# 상세한 오류 로깅을 위한 함수
def log_error_with_context(error: Exception, context: str = "", **kwargs):
    """상세한 오류 정보를 로그로 남김"""
    error_info = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
        **kwargs
    }
    
    logger.error(f"❌ 오류 발생: {error_info}")
    
    # 스택 트레이스 로깅
    import traceback
    logger.error(f"📋 스택 트레이스:\n{traceback.format_exc()}")
    
    return error_info

# ---------- .env ----------
if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv(find_dotenv())

# ---------- FastAPI ----------
app = FastAPI(title="Account Service API", description="Account 서비스", version="1.0.0")

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

# ---------- Database Connection Test ----------
from sqlalchemy import text

# 서비스 시작 시 데이터베이스 연결 테스트
try:
    engine = get_db_engine()
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    logger.info("✅ 데이터베이스 연결 성공")
except Exception as e:
    if "DATABASE_URL is not set" in str(e):
        logger.warning("⚠️ DATABASE_URL이 설정되지 않았습니다. 로컬 개발 환경에서는 .env 파일을 확인하세요.")
        logger.warning("⚠️ 도커 환경에서는 DATABASE_URL 환경 변수를 설정하세요.")
    else:
        log_error_with_context(
            error=e,
            context="데이터베이스 연결 테스트",
            service="account-service",
            operation="startup_db_test"
        )

# ---------- Import Routers ----------
from .router.account_router import account_router

# ---------- Include Routers ----------
app.include_router(account_router)

# ---------- Root Route ----------
@app.get("/", summary="Root")
def root():
    return {
        "status": "ok", 
        "service": "account-service", 
        "endpoints": ["/login", "/signup", "/logout", "/profile"]
    }

# ---------- Middleware ----------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    logger.info(f"📥 요청: {request.method} {request.url.path} (클라이언트: {client_ip}, UA: {user_agent[:50]}...)")
    
    try:
        response = await call_next(request)
        logger.info(f"📤 응답: {response.status_code} - {request.method} {request.url.path}")
        return response
    except Exception as e:
        log_error_with_context(
            error=e,
            context="HTTP 요청 처리",
            service="account-service",
            operation="request_processing",
            request_method=request.method,
            request_path=str(request.url.path),
            client_ip=client_ip,
            user_agent=user_agent,
            headers=dict(request.headers)
        )
        raise

# ---------- Entrypoint ----------
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8001"))
    logger.info(f"💻 서비스 시작 - 포트: {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info", access_log=True)
