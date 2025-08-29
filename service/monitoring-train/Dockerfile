FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지 설치 (AI/ML 모델용 추가 패키지)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 환경 변수 설정
ENV PYTHONPATH=/app
ENV EMBED_MODEL_NAME=/app/bge-m3
ENV EMBED_DEVICE=cuda

# 포트 노출 (8010 포트 사용 - monitoring-train 서비스)
EXPOSE 8010

# 애플리케이션 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8010"]
