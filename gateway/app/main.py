from fastapi import FastAPI, Request, HTTPException, Path
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import httpx
import os
import logging
from typing import Dict
from pydantic import BaseModel
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 로거 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 콘솔 출력
        logging.FileHandler('gateway.log')  # 파일 출력
    ]
)
logger = logging.getLogger(__name__)

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

@app.get("/health", summary="Health Check")
async def health_check():
    logger.info("👌👌👌Health check requested")
    return {"status": "healthy", "service": "gateway"}

@app.get("/health/db", summary="Database Health Check")
async def db_health_check():
    """
    데이터베이스 연결 상태를 확인합니다.
    """
    logger.info("🎸🎸🎸Database health check requested")
    try:
        engine = get_db_engine()
        with engine.connect() as connection:
            # auth 테이블 존재 여부 확인
            result = connection.execute(text("SELECT COUNT(*) FROM auth"))
            count = result.scalar()
            
        logger.info(f"🎸🎸🎸Database health check successful - auth table count: {count}")
        return {
            "status": "healthy",
            "database": "connected",
            "auth_table_count": count,
            "message": "Database connection successful"
        }
    except SQLAlchemyError as e:
        logger.error(f"🎸🎸🎸Database connection failed: {str(e)}")
        raise HTTPException(
            status_code=503, 
            detail=f"Database connection failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"🎸🎸🎸Unexpected error in database health check: {str(e)}")
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
    프론트엔드에서 전송된 로그인 데이터를 Account Service로 전달합니다.
    """
    logger.info(f"🗝️🗝️🗝️Login request received for user_id: {login_data.user_id}")
    
    try:
        # Account Service로 로그인 요청 전달
        account_service_url = os.getenv("ACCOUNT_SERVICE_URL", "http://account-service:8001")
        login_url = f"{account_service_url}/login"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                login_url,
                json={
                    "user_id": login_data.user_id,
                    "user_pw": login_data.user_pw
                },
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"🗝️🗝️🗝️Login successful via account service for user_id: {login_data.user_id}")
                return result
            else:
                error_detail = response.json() if response.content else {"detail": "Account service error"}
                logger.warning(f"🗝️🗝️🗝️Login failed via account service for user_id: {login_data.user_id}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_detail.get("detail", "로그인 실패")
                )
        
    except httpx.RequestError as e:
        logger.error(f"🗝️🗝️🗝️Network error during login for user_id {login_data.user_id}: {str(e)}")
        raise HTTPException(
            status_code=503, 
            detail="로그인 서비스에 연결할 수 없습니다."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"🗝️🗝️🗝️Unexpected error during login for user_id {login_data.user_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"로그인 실패: {str(e)}"
        )

@app.post("/signup", summary="Signup")
async def signup(signup_data: SignupData):
    """
    프론트엔드에서 전송된 회원가입 데이터를 Account Service로 전달합니다.
    """
    logger.info(f"🗝️🗝️🗝️🔓🔓🔓Signup request received for user_id: {signup_data.user_id}, company_id: {signup_data.company_id}")
    
    try:
        # Account Service로 회원가입 요청 전달
        account_service_url = os.getenv("ACCOUNT_SERVICE_URL", "http://account-service:8001")
        signup_url = f"{account_service_url}/signup"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                signup_url,
                json={
                    "user_id": signup_data.user_id,
                    "user_pw": signup_data.user_pw,
                    "company_id": signup_data.company_id
                },
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"🗝️🗝️🗝️🔓🔓🔓Signup successful via account service for user_id: {signup_data.user_id}")
                return result
            else:
                error_detail = response.json() if response.content else {"detail": "Account service error"}
                logger.warning(f"🗝️🗝️🗝️🔓🔓🔓Signup failed via account service for user_id: {signup_data.user_id}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_detail.get("detail", "회원가입 실패")
                )
        
    except httpx.RequestError as e:
        logger.error(f"🗝️🗝️🗝️🔓🔓🔓Network error during signup for user_id {signup_data.user_id}: {str(e)}")
        raise HTTPException(
            status_code=503, 
            detail="회원가입 서비스에 연결할 수 없습니다."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"🗝️🗝️🗝️🔓🔓🔓Unexpected error during signup for user_id {signup_data.user_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"회원가입 실패: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)