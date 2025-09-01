# app/main.py
"""
Normal Service - MSA 프랙탈 구조 main.py (Refactored)
- Base/엔티티 등록 순서 보장 (create_all 전에 엔티티 임포트)
- CORS/로그/헬스 그대로 유지
- Router 포함
"""

from __future__ import annotations

import logging
import os
import sys
import traceback
from datetime import datetime

import uvicorn
from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)
logger = logging.getLogger("normal-service")

logger.info("🚀 Normal Service 시작 중...")
logger.info("📊 Railway PostgreSQL 데이터베이스 연결 설정 준비")

# ---------- .env ----------
if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv(find_dotenv())

# ---------- Database ----------
from eripotter_common.database import get_session

# 엔티티 등록 (create_all 전에 반드시 모듈 임포트)
from .domain.entity import normal_entity as _normal_entity  # noqa: F401
from .domain.entity import certification_entity as _cert_entity  # noqa: F401
from .domain.entity.normal_entity import Base

# 데이터베이스 테이블 생성
try:
    # get_session을 통해 engine에 접근하여 테이블 생성
    with get_session() as db:
        Base.metadata.create_all(bind=db.bind)
    logger.info("✅ 데이터베이스 연결 및 테이블 생성 완료")
except Exception as e:
    logger.error(f"❌ 데이터베이스 연결/테이블 생성 실패: {e}")
    raise

# ---------- FastAPI ----------
app = FastAPI(title="Normal Service API", description="Normal 서비스", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://eripotter.com",
        "https://www.eripotter.com",
        # 개발용 필요 시 주석 해제
        "http://localhost:3000",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Routers ----------
from .router.normal_router import normal_router  # noqa: E402

app.include_router(normal_router)

# ---------- Root/Health ----------
@app.get("/", summary="Root")
def root():
    return {"status": "ok", "service": "normal-service", "endpoints": ["/api/normal", "/health", "/metrics"]}


@app.get("/health", summary="Health Check")
def health_check():
    return {"status": "healthy", "service": "normal-service", "timestamp": datetime.now().isoformat()}


# ---------- Middleware ----------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(
        f"📥 요청: {request.method} {request.url.path} (클라이언트: {request.client.host if request.client else '-'})"
    )
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
    logger.info(f"💻 Normal Service 시작 - 포트: {port}")
    logger.info("🎯 Railway 배포 준비 완료 - 데이터베이스 연결 설정됨")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info", access_log=True)
