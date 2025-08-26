"""
Account Repository - 순수한 데이터 접근 로직
"""
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("account-repository")

class AccountRepository:
    def __init__(self, engine):
        self.engine = engine
    
    def create_user(self, user_id: str, hashed_password: str, company_id: str) -> bool:
        """사용자 생성 (해시된 비밀번호를 받음)"""
        try:
            with self.engine.connect() as conn:
                conn.execute(
                    text("""INSERT INTO auth (user_id, user_pw, company_id)
                            VALUES (:user_id, :user_pw, :company_id)"""),
                    {"user_id": user_id, "user_pw": hashed_password, "company_id": company_id},
                )
                conn.commit()
            logger.info(f"✅ 사용자 생성 성공: {user_id}")
            return True
        except IntegrityError as e:
            logger.warning(f"⚠️ 사용자 이미 존재: {user_id} | 오류: {e}")
            return False
        except SQLAlchemyError as e:
            logger.error(f"❌ 사용자 생성 중 데이터베이스 오류: {e}")
            logger.error(f"📋 상세 정보: user_id={user_id}, company_id={company_id}")
            raise
        except Exception as e:
            logger.error(f"❌ 사용자 생성 중 예상치 못한 오류: {e}")
            logger.error(f"📋 상세 정보: user_id={user_id}, company_id={company_id}")
            raise
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """사용자 조회"""
        try:
            with self.engine.connect() as conn:
                row = conn.execute(
                    text("""SELECT user_id, company_id, user_pw
                            FROM auth WHERE user_id = :user_id"""),
                    {"user_id": user_id},
                ).fetchone()
            
            if row:
                logger.info(f"✅ 사용자 조회 성공: {user_id}")
                return {
                    "user_id": row.user_id,
                    "company_id": row.company_id,
                    "user_pw": row.user_pw
                }
            logger.info(f"ℹ️ 사용자 없음: {user_id}")
            return None
        except SQLAlchemyError as e:
            logger.error(f"❌ 사용자 조회 중 데이터베이스 오류: {e}")
            logger.error(f"📋 상세 정보: user_id={user_id}")
            raise
        except Exception as e:
            logger.error(f"❌ 사용자 조회 중 예상치 못한 오류: {e}")
            logger.error(f"📋 상세 정보: user_id={user_id}")
            raise
    
    def get_user_count(self) -> int:
        """사용자 수 조회"""
        try:
            with self.engine.connect() as conn:
                count = conn.execute(text("SELECT COUNT(*) FROM auth")).scalar()
            logger.info(f"✅ 사용자 수 조회 성공: {count}명")
            return count
        except SQLAlchemyError as e:
            logger.error(f"❌ 사용자 수 조회 중 데이터베이스 오류: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ 사용자 수 조회 중 예상치 못한 오류: {e}")
            raise
