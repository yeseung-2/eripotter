
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import BaseModel
from passlib.hash import bcrypt
import uvicorn
import logging, sys, traceback, os
from urllib.parse import urlparse

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)
logger = logging.getLogger("account-service")

# ---------- .env ----------
if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv(find_dotenv())

# ---------- FastAPI ----------
app = FastAPI(title="Account Service API", description="Account 서비스", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://sme.eripotter.com",
        # 개발용 필요 시 주석 해제
        # "http://localhost:3000", "http://localhost:5173", "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- DB ----------
def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    return url

def get_db_engine():
    url = get_database_url()
    parsed = urlparse(url)
    logger.info(f"DB → {parsed.scheme}://{parsed.hostname}:{parsed.port}/{parsed.path.lstrip('/')}")
    connect_args = {}
    if "sslmode=" not in url and (
        (parsed.hostname or "").endswith("proxy.rlwy.net")
        or (parsed.hostname or "").endswith("railway.app")
    ):
        connect_args["sslmode"] = "require"
    return create_engine(url, pool_pre_ping=True, connect_args=connect_args)

# ---------- Models ----------
class LoginData(BaseModel):
    user_id: str
    user_pw: str

class SignupData(BaseModel):
    user_id: str
    user_pw: str
    company_id: str

# ---------- Routes ----------
@app.get("/", summary="Root")
def root():
    return {"status": "ok", "service": "account-service", "endpoints": ["/health", "/health/db", "/login", "/signup"]}

@app.get("/health", summary="Health Check")
async def health_check():
    logger.info("👌 Health check requested for account service")
    return {"status": "healthy", "service": "account-service"}

@app.get("/health/db", summary="Database Health Check")
async def db_health_check():
    logger.info("🎸 Database health check requested for account service")
    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM auth")).scalar()
        logger.info(f"🎸 Database health check successful - auth table count: {count}")
        return {"status": "healthy", "database": "connected", "auth_table_count": count, "message": "Database connection successful"}
    except SQLAlchemyError as e:
        logger.error(f"🎸 Database connection failed: {e}")
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")
    except Exception as e:
        logger.error(f"🎸 Unexpected error in DB health: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/signup", summary="Signup")
async def signup(signup_data: SignupData):
    logger.info(f"🔐 Signup request: user_id={signup_data.user_id}, company_id={signup_data.company_id}")
    try:
        engine = get_db_engine()
        hashed_pw = bcrypt.hash(signup_data.user_pw)  # 해시 문자열 저장
        with engine.connect() as conn:
            conn.execute(
                text("""INSERT INTO auth (user_id, user_pw, company_id)
                        VALUES (:user_id, :user_pw, :company_id)"""),
                {"user_id": signup_data.user_id, "user_pw": hashed_pw, "company_id": signup_data.company_id},
            )
            conn.commit()
        return {"status": "success", "message": "회원가입 성공", "user_id": signup_data.user_id, "company_id": signup_data.company_id}
    except IntegrityError:
        raise HTTPException(status_code=409, detail="이미 존재하는 사용자 ID입니다.")
    except SQLAlchemyError as e:
        logger.error(f"DB error during signup: {e}")
        raise HTTPException(status_code=500, detail=f"회원가입 실패: 데이터베이스 오류 - {str(e)}")

@app.post("/login", summary="Login")
async def login(login_data: LoginData):
    logger.info(f"🔑 Login request: user_id={login_data.user_id}")
    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            row = conn.execute(
                text("""SELECT user_id, company_id, user_pw
                        FROM auth WHERE user_id = :user_id"""),
                {"user_id": login_data.user_id},
            ).fetchone()
        if row and bcrypt.verify(login_data.user_pw, row.user_pw):
            return {"status": "success", "message": "로그인 성공", "user_id": row.user_id, "company_id": row.company_id}
        raise HTTPException(status_code=401, detail="로그인 실패: 사용자 ID 또는 비밀번호가 올바르지 않습니다.")
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"DB error during login: {e}")
        raise HTTPException(status_code=500, detail=f"로그인 실패: 데이터베이스 오류 - {str(e)}")

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
    port = int(os.getenv("PORT", "8001"))
    logger.info(f"💻 서비스 시작 - 포트: {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info", access_log=True)
