# Account Service

Railway PostgreSQL의 `auth` 테이블과 연동하는 계정 관리 서비스입니다.

## 🗄️ 데이터베이스 구조

### auth 테이블
```sql
CREATE TABLE auth (
    user_id VARCHAR(255) PRIMARY KEY,
    user_pw VARCHAR(255) NOT NULL,
    company_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 환경 변수 설정

### Railway 배포 시
Railway에서 자동으로 `DATABASE_URL` 환경 변수가 설정됩니다.

### 로컬 개발 시
`.env` 파일을 생성하고 다음을 설정하세요:

```env
DATABASE_URL=postgresql://username:password@host:port/database
PORT=8001
```

## 🚀 실행 방법

### 도커로 실행
```bash
# 서비스 빌드
docker-compose build account-service

# 서비스 실행
docker-compose up account-service -d
```

### 로컬 실행
```bash
# 의존성 설치
pip install -r requirements.txt

# 서비스 실행
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## 📡 API 엔드포인트

### POST /login
사용자 로그인
```json
{
    "user_id": "test_user",
    "user_pw": "password123"
}
```

### POST /signup
사용자 회원가입
```json
{
    "user_id": "new_user",
    "user_pw": "password123",
    "company_id": "company_001"
}
```

### GET /profile/{user_id}
사용자 프로필 조회

### GET /health
서비스 상태 확인

## 🔐 보안 기능

- **비밀번호 해시화**: bcrypt를 사용한 안전한 비밀번호 저장
- **SQL Injection 방지**: SQLAlchemy의 파라미터화된 쿼리 사용
- **CORS 설정**: 허용된 도메인에서만 접근 가능

## 🗃️ 데이터베이스 연결

서비스 시작 시 Railway PostgreSQL의 `auth` 테이블과 연결을 테스트합니다. 기존 `auth` 테이블을 사용합니다.

## 📊 모니터링 및 로깅

- **로그 레벨**: INFO
- **요청/응답 로깅**: 클라이언트 IP, User-Agent, 요청 경로 포함
- **데이터베이스 연결 상태**: 서비스 시작 시 연결 테스트
- **상세 오류 로깅**: 오류 타입, 메시지, 컨텍스트, 스택 트레이스 포함
- **보안 로깅**: 로그인/회원가입 시도, 성공/실패 기록
