from sqlalchemy import text
from eripotter_common.database import engine
import logging

logger = logging.getLogger(__name__)

def migrate_account_table():
    """Account 테이블 마이그레이션 - company_name을 NULL 허용으로 변경"""
    try:
        with engine.connect() as conn:
            # 트랜잭션 시작
            trans = conn.begin()
            try:
                logger.info("Account 테이블 마이그레이션 시작...")
                
                # company_name 컬럼을 NULL 허용으로 변경
                logger.info("company_name 컬럼을 NULL 허용으로 변경 중...")
                conn.execute(text("""
                    ALTER TABLE account 
                    ALTER COLUMN company_name DROP NOT NULL;
                """))
                
                # company_type 컬럼을 NULL 허용으로 변경
                logger.info("company_type 컬럼을 NULL 허용으로 변경 중...")
                conn.execute(text("""
                    ALTER TABLE account 
                    ALTER COLUMN company_type DROP NOT NULL;
                """))
                
                # industry 컬럼을 NULL 허용으로 변경
                logger.info("industry 컬럼을 NULL 허용으로 변경 중...")
                conn.execute(text("""
                    ALTER TABLE account 
                    ALTER COLUMN industry DROP NOT NULL;
                """))
                
                # business_number 컬럼을 NULL 허용으로 변경
                logger.info("business_number 컬럼을 NULL 허용으로 변경 중...")
                conn.execute(text("""
                    ALTER TABLE account 
                    ALTER COLUMN business_number DROP NOT NULL;
                """))
                
                # department 컬럼을 NULL 허용으로 변경
                logger.info("department 컬럼을 NULL 허용으로 변경 중...")
                conn.execute(text("""
                    ALTER TABLE account 
                    ALTER COLUMN department DROP NOT NULL;
                """))
                
                # phone_number 컬럼을 NULL 허용으로 변경
                logger.info("phone_number 컬럼을 NULL 허용으로 변경 중...")
                conn.execute(text("""
                    ALTER TABLE account 
                    ALTER COLUMN phone_number DROP NOT NULL;
                """))
                
                # 트랜잭션 커밋
                trans.commit()
                logger.info("✅ Account 테이블 마이그레이션 완료")
                
            except Exception as e:
                # 트랜잭션 롤백
                trans.rollback()
                logger.error(f"❌ 마이그레이션 실패: {str(e)}")
                raise
                
    except Exception as e:
        logger.error(f"❌ 데이터베이스 연결 실패: {str(e)}")
        raise

if __name__ == "__main__":
    migrate_account_table()
