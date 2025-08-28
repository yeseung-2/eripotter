from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from eripotter_common.database import engine
from .domain.entity.account_entity import Base
from .router.account_router import router as account_router

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

# FastAPI 앱 생성
app = FastAPI(
    title="Account Service",
    description="Account management service for EriPotter",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(account_router)

# 헬스체크
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "account"}