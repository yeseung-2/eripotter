"""
Report Service main ㅡ MSA 프랙탈 구조
"""
import logging, sys, traceback, os
import threading  # 🔥 워밍업용

# ---------- Logging ----------
logging.basicConfig(
    level=logging.DEBUG,  # DEBUG 레벨로 변경
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)
logger = logging.getLogger("report-service")

logger.info("🚀 Report Service 시작 중...")

# ---------- .env ----------
logger.info("📁 .env 파일 로드 시도...")
try:
    from dotenv import load_dotenv, find_dotenv
    if os.getenv("RAILWAY_ENVIRONMENT") != "true":
        load_dotenv(find_dotenv())
    logger.info("✅ .env 로드 완료")
except Exception as e:
    logger.warning(f"⚠️ .env 로드 실패: {e}")
    logger.warning(traceback.format_exc())

# ---------- FastAPI ----------
logger.info("🔧 FastAPI import 시도...")
try:
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    logger.info("✅ FastAPI import 완료")
except Exception as e:
    logger.error(f"❌ FastAPI import 실패: {e}")
    logger.error(traceback.format_exc())
    raise

logger.info("🏗️ FastAPI 앱 생성 중...")
app = FastAPI(title="Report Service API", description="Report 서비스", version="1.0.0")

logger.info("🔒 CORS 미들웨어 설정 중...")
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
logger.info("✅ CORS 미들웨어 설정 완료")

# ---------- Import Routers ----------
try:
    from .router.report_router import router as report_router
    logger.info("✅ 라우터 import 완료")
except Exception as e:
    logger.error(f"❌ 라우터 import 실패: {e}")
    raise

# ---------- Database Initialization ----------
logger.info("🗄️ 데이터베이스 초기화 시도...")
try:
    logger.info("📦 eripotter_common.database.base import 시도...")
    from eripotter_common.database.base import Base
    logger.info("✅ Base import 완료")
    
    logger.info("🔧 engine import 시도...")
    from eripotter_common.database.base import engine
    logger.info("✅ engine import 완료")
    
    logger.info("🏗️ 테이블 생성 시도...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ 데이터베이스 초기화 완료")
except Exception as e:
    logger.warning(f"⚠️ 데이터베이스 초기화 실패: {e}")
    logger.warning(traceback.format_exc())

# ---------- Include Routers ----------
app.include_router(report_router)

# ---------- RAG Embedder Warm-up (콜드스타트 제거) ----------
def _warmup_rag_embedder():
    """
    RAG 임베더(bge-m3/openai) 콜드스타트 제거용 워밍업.
    실패해도 서비스는 계속 동작한다.
    """
    try:
        logger.info("🔥 RAG embedder warm-up 시작...")
        from .domain.service.rag_utils import RAGUtils
        rag = RAGUtils(collection_name="esg_manual")  # Qdrant 차원 기반으로 임베더 자동 선택
        _ = rag.encode(["warmup ping"])               # 임베더 로딩 트리거
        logger.info("✅ RAG embedder warm-up completed")
    except Exception as e:
        # 워밍업 실패해도 치명적이지 않으므로 경고만 남긴다.
        logger.warning(f"⚠️ RAG warm-up skipped: {e}")
        logger.debug("Warm-up stacktrace:", exc_info=True)

@app.on_event("startup")
async def warmup_on_startup():
    # 필요 시 비활성화: DISABLE_RAG_WARMUP=1
    if os.getenv("DISABLE_RAG_WARMUP") == "1":
        logger.info("⏭️ RAG warm-up disabled via env.")
        return
    # 논블로킹 백그라운드로 워밍업 실행 (부팅/헬스체크 지연 없음)
    threading.Thread(target=_warmup_rag_embedder, daemon=True).start()

# ---------- Root Route ----------
logger.info("🏠 Root Route 설정 중...")
@app.get("/", summary="Root")
def root():
    logger.info("📡 Root 엔드포인트 호출됨")
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
            
            # 지표 관리 API
            "GET /indicators",
            "GET /indicators/category/{category}",
            "GET /indicators/{indicator_id}/fields",
            "POST /indicators/{indicator_id}/enhanced-draft",
            
            # 헬스체크
            "GET /reports/health"
        ]
    }

# 테스트용 간단한 엔드포인트
@app.get("/health", summary="Health Check")
def health():
    logger.info("📡 Health Check 엔드포인트 호출됨")
    return {"status": "healthy", "service": "report-service"}

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
logger.info("🎯 Entrypoint 설정 완료")
if __name__ == "__main__":
    logger.info("🚀 직접 실행 모드 시작...")
    try:
        import uvicorn
        
        # 포트 정보 상세 로깅
        raw_port = os.getenv("PORT")
        logger.info(f"🔍 환경변수 PORT: {raw_port}")
        
        port = int(os.getenv("PORT", "8007"))
        logger.info(f"💻 서비스 시작 - 포트: {port}")
        logger.info(f"🌐 서비스 URL: http://0.0.0.0:{port}")
        
        uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info", access_log=True)
    except Exception as e:
        logger.error(f"❌ 서비스 시작 실패: {e}")
        logger.error(traceback.format_exc())
        raise
