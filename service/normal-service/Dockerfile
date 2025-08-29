# Python 3.11 베이스 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 필요한 Python 패키지 설치 (단계별 설치)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch==2.1.1 && \
    pip install --no-cache-dir transformers==4.35.0 && \
    pip install --no-cache-dir huggingface-hub==0.19.4 && \
    pip install --no-cache-dir sentence-transformers==5.1.0 && \
    pip install --no-cache-dir -r requirements.txt

# HF CLI 설치
RUN pip install --no-cache-dir "huggingface_hub[cli]"

# 환경 변수 설정
ENV MODEL_DIR=/app/model/bomi-ai \
    HF_HUB_ENABLE_HF_TRANSFER=1

# 애플리케이션 코드 복사
COPY ./app ./app

# BOMI AI 모델 다운로드 (Hugging Face에서)
ARG HF_REPO_ID=galaxybuddy/bomi-ai
ARG HF_REV=main
ARG HF_TOKEN
RUN mkdir -p ${MODEL_DIR} && \
    huggingface-cli download "$HF_REPO_ID" --revision "$HF_REV" \
      --local-dir ${MODEL_DIR} --local-dir-use-symlinks False \
      --include "model.safetensors,config.json,tokenizer.json,tokenizer_config.json,special_tokens_map.json,modules.json,sentence_bert_config.json,config_sentence_transformers.json,1_Pooling/**" \
      ${HF_TOKEN:+--token "$HF_TOKEN"}

# 데이터 파일 복사
COPY app/domain/model/data/reg_test1.xlsx /app/data/

# 빌드 확인용 (나중에 제거 가능)
RUN ls -lah /app/model/bomi-ai

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1

# 서비스 포트 노출
EXPOSE 8005

# 애플리케이션 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005"]
