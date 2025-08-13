from urllib.parse import urlparse
from sqlalchemy import create_engine
from .config import settings
import logging
from ..domain.repository.account_repository import AccountRepository

logger = logging.getLogger("account-service")

def get_database_url() -> str:
    if not settings.DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set")
    return settings.DATABASE_URL

def get_db_engine():
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

def get_account_repository() -> AccountRepository:
    """Account Repository 인스턴스 생성"""
    engine = get_db_engine()
    return AccountRepository(engine)
