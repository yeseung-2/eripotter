"""
Report Service main ㅡ MSA 프랙탈 구조
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
logger = logging.getLogger("report-service")

# ---------- .env ----------
if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv(find_dotenv())

# ---------- FastAPI ----------
app = FastAPI(title="Report Service API", description="Report 서비스", version="1.0.0")

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
from .router.report_router import report_router

# ---------- Database Initialization ----------
from eripotter_common.database import engine, Base
Base.metadata.create_all(bind=engine)

# ---------- Include Routers ----------
app.include_router(report_router)

# ---------- Root Route ----------
@app.get("/", summary="Root")
def root():
    return {
        "status": "ok", 
        "service": "report-service", 
        "endpoints": [
            # 기본 CRUD
            "POST /reports",
            "GET /reports/{topic}/{company_name}",
            "PUT /reports", 
            "DELETE /reports/{topic}/{company_name}",
            "POST /reports/complete",
            
            # 목록 조회
            "GET /reports/company/{company_name}",
            "GET /reports/company/{company_name}/type/{report_type}",
            "GET /reports/status/{company_name}",
            
            # ESG 매뉴얼 기반 지표 API
            "GET /reports/indicator/{indicator_id}/summary",
            "GET /reports/indicator/{indicator_id}/input-fields",
            "POST /reports/indicator/{indicator_id}/draft",
            "POST /reports/indicator/{indicator_id}/save",
            "GET /reports/indicator/{indicator_id}/data",
            
            # 헬스체크
            "GET /reports/health"
        ]
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
    port = int(os.getenv("PORT", "8007"))
    logger.info(f"💻 서비스 시작 - 포트: {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info", access_log=True)
