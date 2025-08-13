"""
보안 관련 유틸리티 함수들
"""
from passlib.hash import bcrypt
import logging

logger = logging.getLogger("security")

def hash_password(plain_password: str) -> str:
    """비밀번호 해시화"""
    return bcrypt.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return bcrypt.verify(plain_password, hashed_password)
