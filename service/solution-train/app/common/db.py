"""
데이터베이스 연결 및 엔진 생성 유틸리티
"""
from urllib.parse import urlparse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
import logging

logger = logging.getLogger("db")

def get_database_url() -> str:
    """데이터베이스 URL 반환"""
    if not settings.DATABASE_URL:
        # SQLite 기본값 사용
        return "sqlite:///./llm_service.db"
    return settings.DATABASE_URL

def get_db_engine():
    """데이터베이스 엔진 생성"""
    url = get_database_url()
    parsed = urlparse(url)
    logger.info(f"DB → {parsed.scheme}://{parsed.hostname}:{parsed.port}/{parsed.path.lstrip('/')}")
    
    connect_args = {}
    
    # SQLite 연결 설정
    if "sqlite" in url:
        connect_args["check_same_thread"] = False
    
    # Railway Postgres일 때 sslmode=require 자동 부여(이미 붙어있으면 생략)
    elif "sslmode=" not in url and (
        (parsed.hostname or "").endswith("proxy.rlwy.net")
        or (parsed.hostname or "").endswith("railway.app")
    ):
        connect_args["sslmode"] = "require"
    
    return create_engine(url, pool_pre_ping=True, connect_args=connect_args)

# 엔진 생성
engine = get_db_engine()

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 베이스 클래스 생성
Base = declarative_base()

def get_db():
    """데이터베이스 세션을 반환하는 의존성 함수"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
