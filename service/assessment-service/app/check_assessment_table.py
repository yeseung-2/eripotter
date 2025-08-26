import os
import logging
from sqlalchemy import create_engine, text

logger = logging.getLogger("check-assessment-table")

def check_assessment_table():
    """assessment 테이블 구조 확인"""
    try:
        # DATABASE_URL 환경변수에서 데이터베이스 연결 정보 가져오기
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        
        # 데이터베이스 엔진 생성
        engine = create_engine(database_url)
        
        # 테이블 구조 확인
        with engine.connect() as conn:
            # assessment 테이블 존재 여부 확인
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'assessment'
                );
            """))
            assessment_exists = result.scalar()
            
            if not assessment_exists:
                logger.error("❌ assessment 테이블이 존재하지 않습니다.")
                return
            
            logger.info("✅ assessment 테이블이 존재합니다.")
            
            # assessment 테이블 컬럼 정보 확인
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'assessment' 
                ORDER BY ordinal_position;
            """))
            
            logger.info("📋 assessment 테이블 컬럼 정보:")
            for row in result:
                logger.info(f"  - {row.column_name}: {row.data_type} (nullable: {row.is_nullable})")
            
            # assessment 테이블의 제약조건 확인
            result = conn.execute(text("""
                SELECT tc.constraint_name, tc.constraint_type, kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu 
                    ON tc.constraint_name = kcu.constraint_name
                WHERE tc.table_name = 'assessment';
            """))
            
            logger.info("🔒 assessment 테이블 제약조건:")
            for row in result:
                logger.info(f"  - {row.constraint_name}: {row.constraint_type} on {row.column_name}")
            
            # 인덱스 확인
            result = conn.execute(text("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'assessment';
            """))
            
            logger.info("📊 assessment 테이블 인덱스:")
            for row in result:
                logger.info(f"  - {row.indexname}: {row.indexdef}")
                
    except Exception as e:
        logger.error(f"❌ 오류 발생: {e}")
        raise

if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 테이블 구조 확인
    check_assessment_table()
