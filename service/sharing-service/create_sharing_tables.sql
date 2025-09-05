-- Railway sharing 테이블에 데이터 요청/승인 기능 통합
-- sharing 테이블에 협력사 관계 + 데이터 요청/승인 모든 기능 포함

-- 기존 테이블 삭제 (데이터 초기화)
DROP TABLE IF EXISTS sharing_requests CASCADE;
DROP TABLE IF EXISTS company_chains CASCADE;
DROP TABLE IF EXISTS sharing CASCADE;

-- Enum 타입 생성 (기존 타입 삭제 후 재생성)
DROP TYPE IF EXISTS priority_level CASCADE;
DROP TYPE IF EXISTS request_status CASCADE;
DROP TYPE IF EXISTS urgency_level CASCADE;

CREATE TYPE priority_level AS ENUM ('high', 'medium', 'low');
CREATE TYPE request_status AS ENUM ('pending', 'active', 'rejected', 'completed', 'inactive');
CREATE TYPE urgency_level AS ENUM ('low', 'normal', 'high');

-- sharing 테이블 생성 (기존에 없다면)
CREATE TABLE IF NOT EXISTS sharing (
    id SERIAL PRIMARY KEY,
    parent_company_id VARCHAR(100),
    parent_company_name VARCHAR(200),
    child_company_id VARCHAR(100) NOT NULL UNIQUE,
    child_company_name VARCHAR(200),
    chain_level INTEGER,
    relationship_type VARCHAR(50) DEFAULT 'supplier',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- sharing 테이블에 핵심 협력사 관련 컬럼 추가
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS is_strategic BOOLEAN DEFAULT FALSE;
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS priority_level priority_level DEFAULT 'medium';
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS designation_reason TEXT;
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS business_impact_score INTEGER DEFAULT 0;
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS annual_transaction_volume DECIMAL(15,2);
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS risk_level VARCHAR(20) DEFAULT 'medium';
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS response_rate INTEGER DEFAULT 0;
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS last_contact_date TIMESTAMP;
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS strategic_designated_by VARCHAR(100);
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS strategic_designated_at TIMESTAMP;

-- sharing 테이블에 데이터 요청/승인 관련 컬럼 추가
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS request_id VARCHAR(50) UNIQUE;
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS data_type VARCHAR(100) DEFAULT 'sustainability';
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS data_category VARCHAR(200);
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS data_description TEXT;
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS requested_fields TEXT;
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS purpose TEXT;
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS usage_period VARCHAR(100);
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS urgency_level urgency_level DEFAULT 'normal';
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS status request_status DEFAULT 'pending';
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS requested_at TIMESTAMP;
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMP;
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP;
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP;
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS reviewer_id VARCHAR(100);
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS reviewer_name VARCHAR(200);
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS review_comment TEXT;
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS data_url TEXT;
ALTER TABLE sharing ADD COLUMN IF NOT EXISTS expiry_date TIMESTAMP;

-- 인덱스 추가 (핵심 협력사 + 데이터 요청 관련)
CREATE INDEX IF NOT EXISTS idx_sharing_is_strategic ON sharing (is_strategic);
CREATE INDEX IF NOT EXISTS idx_sharing_priority_level ON sharing (priority_level);
CREATE INDEX IF NOT EXISTS idx_sharing_strategic_parent ON sharing (parent_company_id, is_strategic) WHERE parent_company_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_sharing_request_id ON sharing (request_id) WHERE request_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_sharing_status ON sharing (status) WHERE status IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_sharing_urgency ON sharing (urgency_level) WHERE urgency_level IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_sharing_requested_at ON sharing (requested_at) WHERE requested_at IS NOT NULL;

-- 협력사 관계 샘플 데이터 삽입 (기존 데이터가 없다면)
-- 데이터 요청은 API를 통해 별도로 생성
INSERT INTO sharing (
    parent_company_id, parent_company_name, child_company_id, child_company_name, 
    chain_level, relationship_type, is_strategic, priority_level, designation_reason, 
    business_impact_score, risk_level, response_rate, last_contact_date, 
    strategic_designated_by, strategic_designated_at
) VALUES
-- 핵심 협력사들
('TIER1_A', '1차사 A', 'TIER2_L2MAN', 'L2 MAN', 2, '핵심공정',
 TRUE, 'high', '핵심 제조 공정을 담당하는 주요 협력사로 생산량의 60% 차지', 
 95, 'high', 95, '2025-01-13 10:00:00', 'admin', '2025-01-01 09:00:00'),

('TIER1_A', '1차사 A', 'TIER2_CONVERTER', '컨버터', 2, '변환공정',
 TRUE, 'high', '원자재 변환 공정의 유일한 공급업체로 대체 불가능', 
 88, 'medium', 88, '2025-01-06 14:30:00', 'admin', '2025-01-01 09:00:00'),

-- 일반 협력사들
('TIER1_A', '1차사 A', 'TIER2_COATING', '코팅업체', 2, '표면처리',
 FALSE, 'medium', NULL, 75, 'medium', 78, '2025-01-10 16:20:00', NULL, NULL),

('TIER1_A', '1차사 A', 'TIER2_LOGISTICS', '물류업체', 2, '운송',
 FALSE, 'low', NULL, 45, 'low', 82, '2025-01-08 11:15:00', NULL, NULL),

('TIER1_A', '1차사 A', 'TIER2_PACKAGING', '포장업체', 2, '포장재',
 FALSE, 'low', NULL, 35, 'low', 65, '2025-01-05 09:45:00', NULL, NULL),

('TIER1_A', '1차사 A', 'TIER2_QUALITY', '품질검사', 2, '품질관리',
 FALSE, 'medium', NULL, 60, 'medium', 92, '2025-01-12 13:30:00', NULL, NULL)
ON CONFLICT (child_company_id) DO NOTHING;

-- 기존 데이터가 있다면 핵심 협력사 정보 업데이트
UPDATE sharing SET 
    is_strategic = TRUE,
    priority_level = 'high',
    designation_reason = '핵심 제조 공정을 담당하는 주요 협력사로 생산량의 60% 차지',
    business_impact_score = 95,
    risk_level = 'high',
    response_rate = 95,
    last_contact_date = '2025-01-13 10:00:00'::timestamp,
    strategic_designated_by = 'admin',
    strategic_designated_at = '2025-01-01 09:00:00'::timestamp
WHERE child_company_name = 'L2 MAN' OR child_company_id LIKE '%L2MAN%';

UPDATE sharing SET 
    is_strategic = TRUE,
    priority_level = 'high',
    designation_reason = '원자재 변환 공정의 유일한 공급업체로 대체 불가능',
    business_impact_score = 88,
    risk_level = 'medium',
    response_rate = 88,
    last_contact_date = '2025-01-06 14:30:00'::timestamp,
    strategic_designated_by = 'admin',
    strategic_designated_at = '2025-01-01 09:00:00'::timestamp
WHERE child_company_name = '컨버터' OR child_company_id LIKE '%CONVERTER%';

-- 일반 협력사들의 기본 정보 설정
UPDATE sharing SET 
    response_rate = CASE 
        WHEN child_company_name = '코팅업체' THEN 78
        WHEN child_company_name = '물류업체' THEN 82
        WHEN child_company_name = '포장업체' THEN 65
        WHEN child_company_name = '품질검사' THEN 92
        ELSE 70
    END,
    last_contact_date = CASE 
        WHEN child_company_name = '코팅업체' THEN '2025-01-10 16:20:00'::timestamp
        WHEN child_company_name = '물류업체' THEN '2025-01-08 11:15:00'::timestamp
        WHEN child_company_name = '포장업체' THEN '2025-01-05 09:45:00'::timestamp
        WHEN child_company_name = '품질검사' THEN '2025-01-12 13:30:00'::timestamp
        ELSE '2025-01-10 12:00:00'::timestamp
    END,
    business_impact_score = CASE 
        WHEN child_company_name = '코팅업체' THEN 75
        WHEN child_company_name = '물류업체' THEN 45
        WHEN child_company_name = '포장업체' THEN 35
        WHEN child_company_name = '품질검사' THEN 60
        ELSE 50
    END
WHERE is_strategic = FALSE OR is_strategic IS NULL;
