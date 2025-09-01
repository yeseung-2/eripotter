# Assessment Service

Assessment Service는 KESG 자가진단 기능을 제공하는 마이크로서비스입니다.

## 🚀 Railway 배포 준비 완료 ✅

**데이터베이스 연결 및 프론트엔드 연동이 완료되었습니다!**

이 서비스는 Railway PostgreSQL 데이터베이스와 연결되어 있으며, 배포 시 자동으로 데이터베이스 연결이 설정됩니다.

### 주요 변경사항

- ✅ Mock Repository → 실제 데이터베이스 Repository로 변경
- ✅ eripotter-common 모듈을 통한 Railway PostgreSQL 연결
- ✅ KESG 및 Assessment 테이블 자동 생성
- ✅ 데이터베이스 연결 테스트 및 오류 처리 개선
- ✅ 로깅 시스템 개선
- ✅ 하드코딩된 데이터 제거 및 동적 데이터 처리
- ✅ 프론트엔드 연동 개선

### 데이터베이스 연결

- **Database Module**: `eripotter-common==0.1.4`
- **Connection**: Railway PostgreSQL 자동 연결
- **Tables**: 
  - `kesg` - KESG 문항 데이터
  - `assessment` - 자가진단 응답 데이터

### 환경 변수

Railway에서 자동으로 설정되는 환경 변수:
- `DATABASE_URL` - PostgreSQL 연결 문자열
- `PORT` - 서비스 포트 (기본값: 8002)

### API 엔드포인트

- `GET /health` - 서비스 상태 확인
- `GET /assessment/kesg` - KESG 문항 목록 조회
- `GET /assessment/kesg/{item_id}` - 특정 KESG 문항 조회
- `POST /assessment/` - 자가진단 응답 제출
- `GET /assessment/assessment-results/{company_name}` - 회사별 결과 조회

### 배포

```bash
# Railway CLI를 사용한 배포
railway up

# 또는 Docker를 사용한 로컬 테스트
docker build -t assessment-service .
docker run -p 8002:8002 assessment-service
```

**배포 후 확인사항:**
1. `/health` 엔드포인트로 서비스 상태 확인
2. `/assessment/kesg` 엔드포인트로 KESG 문항 조회 확인
3. 프론트엔드에서 자가진단 기능 테스트

### 로컬 개발

```bash
# 의존성 설치
pip install -r requirements.txt

# 서비스 실행
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### 데이터베이스 스키마

#### KESG 테이블
- `id` (BigInteger, PK) - KESG 항목 ID
- `classification` (Text) - 분류
- `domain` (Text) - 도메인
- `category` (Text) - 카테고리
- `item_name` (Text) - 항목명
- `item_desc` (Text) - 항목 설명
- `metric_desc` (Text) - 지표 설명
- `data_source` (Text) - 데이터 소스
- `data_period` (Text) - 데이터 기간
- `data_method` (Text) - 데이터 수집 방법
- `data_detail` (Text) - 데이터 상세 정보
- `question_type` (Text) - 질문 타입
- `levels_json` (JSON) - 레벨 정보
- `choices_json` (JSON) - 선택지 정보
- `scoring_json` (JSON) - 점수 정보
- `weight` (Float) - 가중치

#### Assessment 테이블
- `id` (Integer, PK) - Assessment ID
- `company_name` (Text) - 회사명
- `question_id` (Integer) - KESG 문항 ID
- `question_type` (Text) - 질문 타입
- `level_no` (Integer) - 선택된 레벨 번호
- `choice_ids` (JSON) - 선택된 선택지 ID 배열
- `score` (Integer) - 점수
- `timestamp` (TIMESTAMP) - 제출 시간

### 로깅

서비스는 다음 로그 레벨을 제공합니다:
- `INFO` - 일반적인 작업 로그
- `ERROR` - 오류 및 예외 상황
- `WARNING` - 경고 상황

### 프론트엔드 연동

프론트엔드에서는 다음 API 엔드포인트를 사용합니다:

- **KESG 문항 조회**: `GET /assessment/kesg`
- **자가진단 응답 제출**: `POST /assessment/`
- **결과 조회**: `GET /assessment/assessment-results/{company_name}`

회사명은 `localStorage.getItem('companyName')`에서 가져오며, 기본값은 '테스트회사'입니다.

### 헬스체크

서비스는 `/health` 엔드포인트를 통해 상태를 확인할 수 있습니다:

```bash
curl http://localhost:8002/health
```

응답:
```json
{
  "status": "healthy",
  "service": "assessment-service",
  "timestamp": "2024-01-01T00:00:00"
}
```
