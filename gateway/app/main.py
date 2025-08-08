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
    프론트엔드에서 전송된 로그인 데이터를 처리합니다.
    """
    logger.info(f"🗝️🗝️🗝️Login request received for user_id: {login_data.user_id}")
    
    try:
        # 데이터베이스 연결
        engine = get_db_engine()
        
        # 비밀번호를 해시하여 정수로 변환
        password_hash = hash(login_data.user_pw) % (2**63)  # bigint 범위 내로 제한
        
        logger.debug(f"🗝️🗝️🗝️Password hashed for user_id: {login_data.user_id}")
        
        # auth 테이블에서 사용자 정보 확인
        with engine.connect() as connection:
            select_query = text("""
                SELECT user_id, company_id FROM auth 
                WHERE user_id = :user_id AND user_pw = :user_pw
            """)
            
            result = connection.execute(select_query, {
                "user_id": login_data.user_id,
                "user_pw": password_hash
            })
            
            user = result.fetchone()
            
            if user:
                logger.info(f"🗝️🗝️🗝️Login successful for user_id: {login_data.user_id}, company_id: {user.company_id}")
                return {
                    "status": "success", 
                    "message": "로그인 성공",
                    "user_id": user.user_id,
                    "company_id": user.company_id
                }
            else:
                logger.warning(f"🗝️🗝️🗝️Login failed for user_id: {login_data.user_id} - invalid credentials")
                raise HTTPException(
                    status_code=401, 
                    detail="로그인 실패: 사용자 ID 또는 비밀번호가 올바르지 않습니다."
                )
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"🗝️🗝️🗝️Database error during login for user_id {login_data.user_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"로그인 실패: 데이터베이스 오류 - {str(e)}"
        )
    except Exception as e:
        logger.error(f"🗝️🗝️🗝️Unexpected error during login for user_id {login_data.user_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"로그인 실패: {str(e)}"
        )

@app.post("/signup", summary="Signup")
async def signup(signup_data: SignupData):
    """
    프론트엔드에서 전송된 회원가입 데이터를 처리합니다.
    """
    logger.info(f"🗝️🗝️🗝️🔓🔓🔓Signup request received for user_id: {signup_data.user_id}, company_id: {signup_data.company_id}")
    
    try:
        # 데이터베이스 연결
        engine = get_db_engine()
        
        # 비밀번호를 해시하여 정수로 변환
        password_hash = hash(signup_data.user_pw) % (2**63)  # bigint 범위 내로 제한
        
        logger.debug(f"🗝️🗝️🗝️🔓🔓🔓Password hashed for user_id: {signup_data.user_id}")
        
        # auth 테이블에 사용자 정보 삽입
        with engine.connect() as connection:
            insert_query = text("""
                INSERT INTO auth (user_id, user_pw, company_id) 
                VALUES (:user_id, :user_pw, :company_id)
            """)
            
            connection.execute(insert_query, {
                "user_id": signup_data.user_id,
                "user_pw": password_hash,
                "company_id": signup_data.company_id
            })
            
            connection.commit()
        
        logger.info(f"🗝️🗝️🗝️🔓🔓🔓Signup successful for user_id: {signup_data.user_id}, company_id: {signup_data.company_id}")
        
        return {
            "status": "success", 
            "message": "회원가입 성공",
            "user_id": signup_data.user_id,
            "company_id": signup_data.company_id
        }
        
    except SQLAlchemyError as e:
        logger.error(f"🗝️🗝️🗝️🔓🔓🔓Database error during signup for user_id {signup_data.user_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"회원가입 실패: 데이터베이스 오류 - {str(e)}"
        )
    except Exception as e:
        logger.error(f"🗝️🗝️🗝️🔓🔓🔓Unexpected error during signup for user_id {signup_data.user_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"회원가입 실패: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)