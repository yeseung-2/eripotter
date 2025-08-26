import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger("assessment-migration")

def create_assessment_table():
    """assessment 테이블 생성"""
    try:
        # DATABASE_URL 환경변수에서 데이터베이스 연결 정보 가져오기
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        
        # 데이터베이스 엔진 생성
        engine = create_engine(database_url)
        
        # SQL 스크립트 읽기
        sql_file_path = os.path.join(
            os.path.dirname(__file__), 
            "create_assessment_table.sql"
        )
        
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_script = file.read()
        
        # SQL 스크립트 실행
        with engine.connect() as conn:
            # 트랜잭션 시작
            trans = conn.begin()
            try:
                # auth 테이블의 중복 company_id 처리
                logger.info("auth 테이블의 중복 company_id 처리 중...")
                conn.execute(text("""
                    DELETE FROM auth 
                    WHERE user_id NOT IN (
                        SELECT MIN(user_id) 
                        FROM auth 
                        GROUP BY company_id
                    );
                """))
                
                # auth 테이블의 company_id에 unique constraint 추가 (없는 경우)
                logger.info("auth 테이블의 company_id에 unique constraint 추가 중...")
                conn.execute(text("""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.table_constraints 
                            WHERE table_name = 'auth' 
                            AND constraint_name = 'auth_company_id_unique'
                            AND constraint_type = 'UNIQUE'
                        ) THEN
                            ALTER TABLE auth ADD CONSTRAINT auth_company_id_unique UNIQUE (company_id);
                        END IF;
                    END $$;
                """))
                
                # 기존 assessment 테이블 삭제
                logger.info("기존 assessment 테이블 삭제 중...")
                conn.execute(text("DROP TABLE IF EXISTS assessment;"))
                
                # 새로운 assessment 테이블 생성
                logger.info("새로운 assessment 테이블 생성 중...")
                conn.execute(text("""
                    CREATE TABLE assessment (
                        id SERIAL PRIMARY KEY,
                        company_id TEXT NOT NULL REFERENCES auth(company_id),
                        question_id INT NOT NULL REFERENCES kesg(id),
                        question_type TEXT NOT NULL,
                        level_no INT,
                        choice_ids INT[],
                        score INT NOT NULL,
                        timestamp TIMESTAMP DEFAULT now()
                    );
                """))
                
                # 인덱스 생성
                logger.info("인덱스 생성 중...")
                conn.execute(text("CREATE INDEX idx_assessment_company_id ON assessment(company_id);"))
                conn.execute(text("CREATE INDEX idx_assessment_question_id ON assessment(question_id);"))
                conn.execute(text("CREATE INDEX idx_assessment_timestamp ON assessment(timestamp);"))
                
                # 트랜잭션 커밋
                trans.commit()
                logger.info("✅ assessment 테이블 생성 완료")
                
            except Exception as e:
                # 오류 발생 시 롤백
                trans.rollback()
                logger.error(f"❌ assessment 테이블 생성 실패: {e}")
                raise
                
    except SQLAlchemyError as e:
        logger.error(f"❌ 데이터베이스 오류: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ 예상치 못한 오류: {e}")
        raise

if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 테이블 생성 실행
    create_assessment_table()
