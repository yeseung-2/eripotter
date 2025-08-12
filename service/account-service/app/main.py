from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel
import uvicorn
import logging
import traceback
import os
from dotenv import load_dotenv, find_dotenv


from app.router.sme_router import auth_router

# 로거 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 콘솔 출력만 사용
    ]
)
logger = logging.getLogger("account-service")

# .env 로딩
if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv(find_dotenv())


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

# 라우터 등록
app.include_router(auth_router)

# 데이터베이스 연결
def get_database_url():
    url = os.getenv("DATABASE_URL")
    if not url:
        # 디버깅을 쉽게 하려면 명확히 실패시키는 게 좋음
        raise RuntimeError("DATABASE_URL is not set")
    return url

def get_db_engine():
    url = get_database_url()

    # Public Network(URL이 proxy.rlwy.net/railway.app/containers-... 등)면 SSL 필요
    connect_args = {}
    if "sslmode=" not in url and (
        "proxy.rlwy.net" in url or "railway.app" in url
    ):
        connect_args["sslmode"] = "require"

    return create_engine(url, connect_args=connect_args if connect_args else {})

# 로그인 데이터 모델
class LoginData(BaseModel):
    user_id: str
    user_pw: str

# 회원가입 데이터 모델
class SignupData(BaseModel):
    user_id: str
    user_pw: str
    company_id: str

@app.get("/health", summary="Health Check")
async def health_check():
    logger.info("👌👌👌Health check requested for account service")
    return {"status": "healthy", "service": "account-service"}

@app.get("/health/db", summary="Database Health Check")
async def db_health_check():
    """
    데이터베이스 연결 상태를 확인합니다.
    """
    logger.info("🎸🎸🎸Database health check requested for account service")
    try:
        engine = get_db_engine()
        with engine.connect() as connection:
            # auth 테이블 존재 여부 확인
            result = connection.execute(text("SELECT COUNT(*) FROM auth"))
            count = result.scalar()
            
        logger.info(f"🎸🎸🎸Database health check successful for account service - auth table count: {count}")
        return {
            "status": "healthy",
            "database": "connected",
            "auth_table_count": count,
            "message": "Database connection successful"
        }
    except SQLAlchemyError as e:
        logger.error(f"🎸🎸🎸Database connection failed for account service: {str(e)}")
        raise HTTPException(
            status_code=503, 
            detail=f"Database connection failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"🎸🎸🎸Unexpected error in account service database health check: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Unexpected error: {str(e)}"
        )

@app.post("/login", summary="Login")
async def login(login_data: LoginData):
    """
    로그인 처리를 담당합니다.
    """
    logger.info(f"🗝️🗝️🗝️Login request received for user_id: {login_data.user_id}")
    
    try:
        # 데이터베이스 연결
        engine = get_db_engine()
        
        # 비밀번호를 해시하여 정수로 변환
        password_hash = hash(login_data.user_pw) % (2**63)  # bigint 범위 내로 제한
        
        logger.debug(f"Password hashed for user_id: {login_data.user_id}")
        
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
    회원가입 처리를 담당합니다.
    """
    logger.info(f"🗝️🗝️🗝️🔓🔓🔓Signup request received for user_id: {signup_data.user_id}, company_id: {signup_data.company_id}")
    
    try:
        # 데이터베이스 연결
        engine = get_db_engine()
        
        # 비밀번호를 해시하여 정수로 변환
        password_hash = hash(signup_data.user_pw) % (2**63)  # bigint 범위 내로 제한
        
        logger.debug(f"Password hashed for user_id: {signup_data.user_id}")
        
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

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"📥 요청: {request.method} {request.url.path} (클라이언트: {request.client.host})")
    try:
        response = await call_next(request)
        logger.info(f"📤 응답: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"❌ 요청 처리 중 오류: {str(e)}")
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    logger.info(f"💻 서비스 시작 - 포트: {port}")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )