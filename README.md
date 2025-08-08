# MSA 프로젝트 - Next.js + FastAPI

## 📋 프로젝트 구조

```
eripotter/
├── frontend/                 # Next.js 프론트엔드
│   ├── src/app/
│   │   ├── page.tsx         # 로그인 페이지
│   │   ├── signup/page.tsx  # 회원가입 페이지
│   │   └── dashboard/page.tsx # 대시보드
├── gateway/                  # FastAPI API Gateway
│   ├── app/main.py          # 메인 애플리케이션
│   └── requirements.txt     # Python 의존성
├── service/                  # 마이크로서비스들
│   ├── assesment-service/   # 평가 서비스
│   ├── chatbot-service/     # 챗봇 서비스
│   ├── monitoring-service/  # 모니터링 서비스
│   ├── report-service/      # 리포트 서비스
│   ├── request-service/     # 요청 서비스
│   └── response-service/    # 응답 서비스
├── docker-compose.yml       # Docker Compose 설정
├── alembic.ini             # Alembic 설정
├── env.example             # 환경 변수 예시
└── README.md              # 프로젝트 문서
```

## 🚀 기술 스택

- **프론트엔드**: Next.js 15, React 19, Tailwind CSS
- **백엔드**: FastAPI, Python 3.9
- **데이터베이스**: PostgreSQL
- **컨테이너**: Docker, Docker Compose
- **마이그레이션**: Alembic
- **배포**: Railway

## 📊 데이터베이스 스키마

### auth 테이블
```sql
CREATE TABLE public.auth (
  user_id text NOT NULL,
  user_pw bigint NOT NULL,
  company_id text NULL,
  CONSTRAINT auth_pkey PRIMARY KEY (user_id)
);
```

## 🔧 설정 방법

### 1. 환경 변수 설정
```bash
# env.example을 복사하여 .env 파일 생성
cp env.example .env

# .env 파일에서 DATABASE_URL 설정
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

### 2. 의존성 설치
```bash
# 프론트엔드
cd frontend
pnpm install

# 백엔드 (각 서비스별로)
cd gateway
pip install -r requirements.txt

cd ../service/assesment-service
pip install -r requirements.txt
```

### 3. 데이터베이스 마이그레이션
```bash
# Alembic 초기화 (최초 1회)
alembic init alembic

# 마이그레이션 생성
alembic revision --autogenerate -m "Create auth table"

# 마이그레이션 실행
alembic upgrade head
```

### 4. 서비스 실행
```bash
# Docker Compose로 모든 서비스 실행
docker-compose up -d

# 또는 개별 실행
# 프론트엔드
cd frontend && pnpm dev

# 게이트웨이
cd gateway && uvicorn app.main:app --host 0.0.0.0 --port 8080

# 평가 서비스
cd service/assesment-service && uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## 🌐 API 엔드포인트

### Gateway (포트: 8080)
- `GET /health` - 헬스 체크
- `GET /health/db` - 데이터베이스 연결 상태
- `POST /login` - 로그인
- `POST /signup` - 회원가입

### Assessment Service (포트: 8001)
- `GET /health` - 헬스 체크
- `GET /health/db` - 데이터베이스 연결 상태

## 🐳 Docker 명령어

```bash
# 모든 서비스 빌드 및 실행
docker-compose up -d

# 특정 서비스만 재시작
docker-compose restart gateway

# 로그 확인
docker-compose logs gateway
docker-compose logs assesment-service

# 서비스 중지
docker-compose down
```

## 📝 개발 가이드

### 새로운 마이크로서비스 추가
1. `service/` 디렉토리에 새 서비스 폴더 생성
2. `Dockerfile`, `requirements.txt`, `app/main.py` 생성
3. `docker-compose.yml`에 서비스 추가
4. 환경 변수에 서비스 URL 추가

### 데이터베이스 스키마 변경
1. 모델 수정
2. 마이그레이션 생성: `alembic revision --autogenerate -m "Description"`
3. 마이그레이션 실행: `alembic upgrade head`

## 🚀 Railway 배포

1. Railway 계정 생성
2. PostgreSQL Add-on 추가
3. GitHub 저장소 연결
4. 환경 변수 설정 (DATABASE_URL)
5. 자동 배포 확인

## 🔍 문제 해결

### DB 연결 오류
- `DATABASE_URL` 환경 변수 확인
- PostgreSQL 서비스 실행 상태 확인
- 방화벽 설정 확인

### Docker 빌드 오류
- Docker 이미지 캐시 정리: `docker system prune`
- 의존성 파일 확인

### 마이그레이션 오류
- 데이터베이스 연결 상태 확인
- 마이그레이션 히스토리 확인: `alembic history`
