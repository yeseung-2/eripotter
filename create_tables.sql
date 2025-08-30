-- ===============================================
-- ESG 데이터 관리 시스템 테이블 생성 스크립트
-- ===============================================

-- 기존 테이블 삭제 (데이터 초기화)
DROP TABLE IF EXISTS certification CASCADE;
DROP TABLE IF EXISTS normal CASCADE;

-- 1. normal 테이블 (원본 업로드 데이터)
CREATE TABLE IF NOT EXISTS normal (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(100),
    company_name VARCHAR(255),
    uploaded_by VARCHAR(100),
    uploaded_by_email VARCHAR(255),
    
    -- 파일 정보
    filename VARCHAR(255),
    file_size BIGINT,
    file_type VARCHAR(50), -- 'manual', 'excel'
    
    -- 제품 기본 정보
    product_name VARCHAR(255),
    supplier VARCHAR(100), -- 원청, 1차, 2차, ..., 10차
    manufacturing_date DATE,
    manufacturing_number VARCHAR(100),
    safety_information TEXT,
    recycled_material BOOLEAN,
    
    -- 제품 스펙
    capacity VARCHAR(100), -- 용량 (Ah, Wh)
    energy_density VARCHAR(100), -- 에너지밀도
    
    -- 위치 정보
    manufacturing_country VARCHAR(100),
    production_plant VARCHAR(255),
    
    -- 처리 방법
    disposal_method TEXT, -- 폐기 방법 및 인증
    recycling_method TEXT, -- 재활용 방법 및 인증
    
    -- 원재료 정보 (JSON 저장, 매핑 안 함)
    raw_materials JSONB, -- ['리튬', '니켈', '코발트', ...]
    raw_material_sources JSONB, -- [{material, sourceType, address/country}, ...]
    
    -- 온실가스 배출량 (AI 매핑 대상)
    greenhouse_gas_emissions JSONB, -- [{materialName, amount, unit}, ...]
    
    -- 화학물질 구성
    chemical_composition TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. certification 테이블 (온실가스 AI 매핑 + 사용자 검토)
CREATE TABLE IF NOT EXISTS certification (
    id SERIAL PRIMARY KEY,
    normal_id INTEGER REFERENCES normal(id) ON DELETE CASCADE,
    company_id VARCHAR(100),
    company_name VARCHAR(255),
    
    -- 온실가스 원본 정보
    original_gas_name VARCHAR(255), -- 사용자 입력: "CO₂", "메탄", "이산화탄소" 등
    original_amount VARCHAR(100),   -- 사용자 입력 양
    
    -- AI 초기 매핑 결과
    ai_mapped_sid VARCHAR(100),     -- 표준 ID: "GHG-CO2"
    ai_mapped_name VARCHAR(255),    -- 표준명: "Carbon dioxide"
    ai_confidence_score FLOAT,     -- 신뢰도 (0-1)
    ai_cas_number VARCHAR(50),      -- CAS 번호: "124-38-9"
    
    -- 사용자 최종 매핑 결과
    final_mapped_sid VARCHAR(100),
    final_mapped_name VARCHAR(255),
    final_cas_number VARCHAR(50),
    final_standard_unit VARCHAR(50),
    
    -- 상태 및 검토 정보
    mapping_status VARCHAR(50) DEFAULT 'auto_mapped', -- 'auto_mapped', 'needs_review', 'user_reviewed', 'approved'
    reviewed_by VARCHAR(100),
    review_comment TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_normal_company_id ON normal(company_id);
CREATE INDEX IF NOT EXISTS idx_normal_created_at ON normal(created_at);
CREATE INDEX IF NOT EXISTS idx_certification_normal_id ON certification(normal_id);
CREATE INDEX IF NOT EXISTS idx_certification_company_id ON certification(company_id);
CREATE INDEX IF NOT EXISTS idx_certification_mapping_status ON certification(mapping_status);

-- JSONB 필드 인덱스 (검색 성능 향상)
CREATE INDEX IF NOT EXISTS idx_normal_raw_materials_gin ON normal USING GIN (raw_materials);
CREATE INDEX IF NOT EXISTS idx_normal_greenhouse_gas_gin ON normal USING GIN (greenhouse_gas_emissions);

-- 트리거 함수 (updated_at 자동 업데이트)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 트리거 생성
DROP TRIGGER IF EXISTS update_normal_updated_at ON normal;
CREATE TRIGGER update_normal_updated_at
    BEFORE UPDATE ON normal
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_certification_updated_at ON certification;
CREATE TRIGGER update_certification_updated_at
    BEFORE UPDATE ON certification
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 테이블 설명 추가
COMMENT ON TABLE normal IS 'ESG 원본 데이터 저장 테이블';
COMMENT ON TABLE certification IS '온실가스 AI 매핑 및 사용자 검토 결과 테이블';

-- 완료 메시지
SELECT 'ESG 데이터베이스 테이블 생성 완료!' as status;
