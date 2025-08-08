"""
Account 서비스 메인 애플리케이션 진입점
"""
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.router.director_router import director_router
from app.router.executive_router import executive_router
from app.router.manager_router import manager_router
from app.router.supervisor_router import supervisor_router
from app.router.worker_router import worker_router
import uvicorn
import logging
import traceback
import os

# 로거 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 콘솔 출력
        logging.FileHandler('account.log')  # 파일 출력
    ]
)
logger = logging.getLogger("account-service")

if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv()

app = FastAPI(
    title="Account Service API",
    description="Account 서비스",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://sme.eripotter.com",  # 프로덕션 도메인만 허용
    ], # 프론트엔드 주소 명시
    allow_credentials=True,  # HttpOnly 쿠키 사용을 위해 필수
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(director_router)
app.include_router(executive_router)
app.include_router(manager_router)
app.include_router(supervisor_router)
app.include_router(worker_router)

@app
.middleware("http")
async def log_requests(request: Request, call_next):
    http://logger.info(f"📥 요청: {request.method} {request.url.path} (클라이언트: {http://request.client.host})")
    try:
        response = await call_next(request)
        http://logger.info(f"📤 응답: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"❌ 요청 처리 중 오류: {str(e)}")
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    http://logger.info(f"💻 개발 모드로 실행 - 포트: 8003")
    http://uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )