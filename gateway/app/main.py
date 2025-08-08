from fastapi import FastAPI, Request, HTTPException, Path
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import httpx
import os
from typing import Dict
from pydantic import BaseModel
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

app = FastAPI(
    title="MSA API Gateway",
    description="마이크로서비스 아키텍처를 위한 API 게이트웨이",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI URL
    redoc_url="/redoc"  # ReDoc UI URL
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영환경에서는 구체적인 도메인을 지정해야 합니다
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="MSA API Gateway",
        version="1.0.0",
        description="마이크로서비스 아키텍처를 위한 API 게이트웨이",
        routes=app.routes,
    )
    
    # 서버 정보 추가
    openapi_schema["servers"] = [
        {"url": "http://localhost:8080", "description": "Development server"},
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schemas

app.openapi = custom_openapi

# 서비스 URL 매핑 (환경 변수에서 가져옴)
SERVICE_REGISTRY: Dict[str, str] = {
    "user": os.getenv("USER_SERVICE_URL", "http://localhost:8001"),
    "product": os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8002"),
    "order": os.getenv("ORDER_SERVICE_URL", "http://localhost:8003"),
}

# 데이터베이스 연결
def get_database_url():
    return os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/dbname")

def get_db_engine():
    database_url = get_database_url()
    return create_engine(database_url)

@app.get("/health", summary="Health Check")
async def health_check():
    return {"status": "healthy", "service": "gateway"}

@app.get("/health/db", summary="Database Health Check")
async def db_health_check():
    """
    데이터베이스 연결 상태를 확인합니다.
    """
    try:
        engine = get_db_engine()
        with engine.connect() as connection:
            # auth 테이블 존재 여부 확인
            result = connection.execute(text("SELECT COUNT(*) FROM auth"))
            count = result.scalar()
            
        return {
            "status": "healthy",
            "database": "connected",
            "auth_table_count": count,
            "message": "Database connection successful"
        }
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Database connection failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Unexpected error: {str(e)}"
        )

# 로그인 데이터 모델
class LoginData(BaseModel):
    user_id: str
    user_pw: str

# 회원가입 데이터 모델
class SignupData(BaseModel):
    user_id: str
    user_pw: str
    company_id: str

@app.post("/login", summary="Login")
async def login(login_data: LoginData):
    """
    프론트엔드에서 전송된 로그인 데이터를 처리합니다.
    """
    print("로그인 요청:")
    print(f"사용자 ID: {login_data.user_id}")
    print(f"비밀번호: {login_data.user_pw}")
    
    # 실제 로그인 로직은 여기에 구현
    # 현재는 간단히 성공 응답만 반환
    return {
        "status": "success", 
        "message": "로그인 성공",
        "user_id": login_data.user_id
    }

@app.post("/signup", summary="Signup")
async def signup(signup_data: SignupData):
    """
    프론트엔드에서 전송된 회원가입 데이터를 처리합니다.
    """
    print("회원가입 요청:")
    print(f"사용자 ID: {signup_data.user_id}")
    print(f"비밀번호: {signup_data.user_pw}")
    print(f"회사 ID: {signup_data.company_id}")
    
    # 비밀번호를 해시하여 정수로 변환 (예시)
    # 실제로는 bcrypt나 다른 해시 함수를 사용해야 합니다
    password_hash = hash(signup_data.user_pw) % (2**63)  # bigint 범위 내로 제한
    
    print(f"해시된 비밀번호: {password_hash}")
    
    # 실제 회원가입 로직은 여기에 구현
    # 현재는 간단히 성공 응답만 반환
    return {
        "status": "success", 
        "message": "회원가입 성공",
        "user_id": signup_data.user_id,
        "company_id": signup_data.company_id
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)