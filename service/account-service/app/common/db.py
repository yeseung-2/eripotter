"""
데이터베이스 연결 및 엔진 생성 유틸리티
"""
from urllib.parse import urlparse
from sqlalchemy import create_engine
from .config import settings
import logging

logger = logging.getLogger("db")

def get_database_url() -> str:
    """데이터베이스 URL 반환"""
    if not settings.DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set")
    return settings.DATABASE_URL

def get_db_engine():
    """데이터베이스 엔진 생성"""
    url = get_database_url()
    parsed = urlparse(url)
    logger.info(f"DB → {parsed.scheme}://{parsed.hostname}:{parsed.port}/{parsed.path.lstrip('/')}")
    connect_args = {}
    # Railway Postgres일 때 sslmode=require 자동 부여(이미 붙어있으면 생략)
    if "sslmode=" not in url and (
        (parsed.hostname or "").endswith("proxy.rlwy.net")
        or (parsed.hostname or "").endswith("railway.app")
    ):
        connect_args["sslmode"] = "require"
    return create_engine(url, pool_pre_ping=True, connect_args=connect_args)
