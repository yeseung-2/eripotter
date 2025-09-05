# Report Service

ESG 매뉴얼 기반 전문 보고서 생성 서비스

## 개요

이 서비스는 Qdrant 벡터 데이터베이스의 `esg_manual` 컬렉션에 저장된 ESG 매뉴얼 문서를 활용하여 전문적인 ESG 보고서를 생성합니다.

## 주요 기능

### 1. 지표별 보고서 생성
- **지표 목록 조회**: 데이터베이스에 저장된 ESG 지표 목록 제공
- **지표별 입력 필드 추천**: Qdrant에서 지표 제목과 매칭되는 정보를 검색하여 입력 필드 추천
- **보고서 초안 생성**: 입력된 데이터를 바탕으로 전문적인 보고서 초안 생성

### 2. ESG 보고서 생성
- **지속가능성 보고서**: 환경, 사회, 지배구조 관점의 종합 보고서
- **ESG 통합 관리 보고서**: ESG 통합 관리 체계 및 성과 측정
- **기후행동 보고서**: 기후변화 대응 및 탄소중립 전략

### 3. 섹션별 내용 생성
- 각 보고서 섹션별 전문적인 내용 생성
- 업계별 특화 가이드라인 적용
- 구체적이고 측정 가능한 지표 포함

### 4. ESG 매뉴얼 검색
- ESG 매뉴얼 컬렉션에서 관련 정보 검색
- 시맨틱 검색을 통한 정확한 매칭
- 문서 제목, 페이지, 테이블, 이미지 정보 포함
- 구조화된 검색 결과 제공

## API 엔드포인트

### 지표별 보고서 생성

#### 지표 목록 조회
```http
GET /indicators
```

**응답 예시:**
```json
{
  "success": true,
  "message": "4개의 지표를 조회했습니다.",
  "indicators": [
    {
      "indicator_id": "KBZ-EN22",
      "title": "온실가스 배출량",
      "category": "Environmental",
      "subcategory": "Climate Change",
      "description": "회사의 온실가스 배출량을 측정하고 보고하는 지표",
      "input_fields": {
        "scope1_emissions": {"type": "number", "description": "Scope 1 온실가스 배출량 (tCO2e)", "required": true},
        "scope2_emissions": {"type": "number", "description": "Scope 2 온실가스 배출량 (tCO2e)", "required": true}
      },
      "status": "active"
    }
  ],
  "total_count": 4
}
```

#### 카테고리별 지표 조회
```http
GET /indicators/category/{category}
```

#### 지표별 입력 필드 추천
```http
GET /indicators/{indicator_id}/fields
```

**응답 예시:**
```json
{
  "success": true,
  "message": "지표 정보와 추천 필드를 성공적으로 조회했습니다.",
  "indicator_id": "KBZ-EN22",
  "title": "온실가스 배출량",
  "input_fields": {
    "scope1_emissions": {"type": "number", "description": "Scope 1 온실가스 배출량 (tCO2e)", "required": true}
  },
  "recommended_fields": [
    {
      "source": "exact_match",
      "title": "온실가스 배출량",
      "content": "탄소중립을 달성하기 위한 노력을 추진하고 있으며...",
      "score": 0.95,
      "suggested_fields": [
        {
          "field_name": "emission_reduction_target",
          "field_type": "number",
          "description": "온실가스 감축 목표 (%)",
          "required": false
        }
      ]
    }
  ]
}
```

#### 향상된 보고서 초안 생성
```http
POST /indicators/{indicator_id}/enhanced-draft
```

**요청 예시:**
```json
{
  "company_name": "테크놀로지 주식회사",
  "inputs": {
    "scope1_emissions": 1500,
    "scope2_emissions": 3000,
    "emission_reduction_target": 30,
    "reduction_measures": "재생에너지 도입, 에너지 효율 개선"
  }
}
```

### ESG 보고서 생성
```http
POST /report/esg/generate
```

**요청 예시:**
```json
{
  "report_type": "sustainability",
  "company_info": {
    "name": "테크놀로지 주식회사",
    "industry": "정보통신업",
    "size": "대기업",
    "location": "서울",
    "description": "AI 및 클라우드 서비스 제공"
  },
  "specific_topics": ["재생에너지 전환", "디지털 포용"],
  "additional_requirements": "GRI 표준 준수"
}
```

### 섹션별 내용 생성
```http
POST /report/esg/section
```

**요청 예시:**
```json
{
  "section_name": "환경(E) 관리 현황",
  "company_info": {
    "name": "테크놀로지 주식회사",
    "industry": "정보통신업"
  },
  "additional_context": "데이터센터 운영으로 인한 전력 소비"
}
```

### ESG 매뉴얼 검색
```http
POST /report/esg/search-manual
```

**요청 예시:**
```json
{
  "query": "정보통신업 ESG 가이드라인",
  "limit": 5
}
```

**응답 예시:**
```json
{
  "success": true,
  "documents": [
    {
      "doc_id": "report",
      "chunk_id": "sec_22_03",
      "title": "KBZ-EN22. 온실가스 및 에너지 (신재생에너지)",
      "content": "탄소중립을 달성하기 위한 노력을 추진하고 있으며...",
      "pages": [65, 66, 67, 68, 69, 70],
      "tables": ["extracted/.../page66_table19_gpt.html"],
      "images": ["extracted/.../page67_img1.jpeg"],
      "order": 94
    }
  ],
  "total_count": 1,
  "query": "정보통신업 ESG 가이드라인",
  "message": "1개의 관련 문서를 찾았습니다."
}
```

### 템플릿 목록 조회
```http
GET /report/esg/templates
```

## 환경 변수

```bash
# Qdrant 설정
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_api_key

# OpenAI 설정
OPENAI_API_KEY=your_openai_api_key

# 서비스 포트
PORT=8007
```

## 설치 및 실행

1. 의존성 설치:
```bash
pip install -r requirements.txt
```

2. 환경 변수 설정:
```bash
export QDRANT_URL=your_qdrant_url
export QDRANT_API_KEY=your_qdrant_api_key
export OPENAI_API_KEY=your_openai_api_key
```

3. 데이터베이스 초기화 및 지표 데이터 생성:
```bash
python seed_indicators.py
```

4. 서비스 실행:
```bash
python -m app.main
```

## 지원하는 보고서 유형

### 1. 지속가능성 보고서 (sustainability)
- 기업 개요 및 지속가능성 비전
- 환경(E) 관리 현황
- 사회(S) 책임 활동
- 지배구조(G) 현황
- 주요 성과 지표
- 향후 계획 및 목표

### 2. ESG 통합 관리 보고서 (esg_integration)
- ESG 통합 관리 체계
- 환경 리스크 관리
- 사회적 가치 창출
- 지배구조 개선 현황
- ESG 성과 측정
- 투자자 커뮤니케이션

### 3. 기후행동 보고서 (climate_action)
- 기후변화 대응 전략
- 탄소중립 로드맵
- 재생에너지 전환 계획
- 기후 리스크 평가
- 기후 관련 재무정보
- 기후 거버넌스

## 기술 스택

- **FastAPI**: 웹 프레임워크
- **Qdrant**: 벡터 데이터베이스
- **Sentence Transformers**: 텍스트 임베딩
- **LangChain**: LLM 통합
- **OpenAI GPT**: 텍스트 생성

## 주요 개선사항

### 1. 구조화된 검색 결과
- 문서 제목, 페이지 번호, 테이블, 이미지 정보 포함
- 검색 결과의 메타데이터 보존
- 더 상세한 컨텍스트 제공

### 2. 향상된 프롬프트 엔지니어링
- ESG 표준 프레임워크 명시 (GRI, SASB, TCFD)
- 업계 모범 사례 참고 지침
- 구조화된 컨텍스트 전달

### 3. 개선된 응답 모델
- 검색 결과 수 카운트
- 원본 쿼리 정보 포함
- 더 상세한 에러 메시지

## 개발 가이드

### 새로운 템플릿 추가
`app/domain/service/report_service.py`의 `esg_templates` 딕셔너리에 새로운 템플릿을 추가할 수 있습니다.

### 프롬프트 커스터마이징
각 메서드의 `system_prompt`를 수정하여 AI의 역할과 출력 형식을 조정할 수 있습니다.

## 라이센스

MIT License
