-- 기존 assessment 테이블 삭제 (존재하는 경우)
DROP TABLE IF EXISTS assessment;

-- auth 테이블의 company_id에 unique constraint 추가 (없는 경우)
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

-- 새로운 assessment 테이블 생성
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

-- 인덱스 생성 (성능 최적화)
CREATE INDEX idx_assessment_company_id ON assessment(company_id);
CREATE INDEX idx_assessment_question_id ON assessment(question_id);
CREATE INDEX idx_assessment_timestamp ON assessment(timestamp);

-- 테이블 생성 확인을 위한 주석
COMMENT ON TABLE assessment IS '기업 자가진단 응답 데이터';
COMMENT ON COLUMN assessment.company_id IS '기업 ID (auth 테이블 참조)';
COMMENT ON COLUMN assessment.question_id IS '문항 ID (kesg 테이블 참조)';
COMMENT ON COLUMN assessment.question_type IS '문항 타입 (three_level, five_level, five_choice)';
COMMENT ON COLUMN assessment.level_no IS '선택된 레벨 번호 (three_level, five_level용)';
COMMENT ON COLUMN assessment.choice_ids IS '선택된 선택지 ID 배열 (five_choice용)';
COMMENT ON COLUMN assessment.score IS '선택된 점수';
COMMENT ON COLUMN assessment.timestamp IS '제출 시간';
