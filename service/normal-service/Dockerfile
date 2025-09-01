# Python 3.11 베이스 이미지
FROM python:3.11-slim

# ---- 기본 환경 ----
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    LANG=C.UTF-8

# HF/Transformers 캐시 & 오프라인(런타임) 설정
# - 모델은 빌드 때 받아 이미지에 "프리베이크"
# - 런타임에는 네트워크 없이 로컬만 사용
ENV HF_HOME=/opt/hf \
    TRANSFORMERS_CACHE=/opt/hf \
    SENTENCE_TRANSFORMERS_HOME=/opt/hf \
    MODEL_DIR=/opt/models/bomi-ai \
    TRANSFORMERS_OFFLINE=1 \
    HF_HUB_ENABLE_HF_TRANSFER=1

# 작업 디렉토리
WORKDIR /app

# ---- 시스템 패키지 (빌드 전용) ----
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# ---- 파이썬 의존성 ----
COPY requirements.txt .

# 1) torch는 CPU 전용 휠에서 설치 (CUDA 불필요)
# 2) ML 라이브러리 먼저 설치해 레이어 캐시 활용
# 3) hf cli/hf_transfer 설치
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.4.1 && \
    pip install --no-cache-dir \
        "transformers==4.44.2" \
        "sentence-transformers==5.1.0" \
        "huggingface-hub>=0.23" \
        "safetensors>=0.4.2" \
        "accelerate>=0.28" && \
    pip install --no-cache-dir "huggingface_hub[cli]" hf_transfer && \
    pip install --no-cache-dir -r requirements.txt && \
    python - <<'PY'
import torch, transformers, sentence_transformers
print("✅ Deps OK:", torch.__version__, transformers.__version__, sentence_transformers.__version__)
PY

# ---- 모델 프리베이크 (빌드 시 1회 다운로드) ----
ARG HF_REPO_ID=galaxybuddy/bomi-ai
ARG HF_REV=main
ARG HF_TOKEN
RUN mkdir -p "${MODEL_DIR}" && \
    echo "⬇️  Download model: ${HF_REPO_ID}@${HF_REV}" && \
    huggingface-cli download "${HF_REPO_ID}" --revision "${HF_REV}" \
      --local-dir "${MODEL_DIR}" --local-dir-use-symlinks False \
      ${HF_TOKEN:+--token "${HF_TOKEN}"} && \
    test -f "${MODEL_DIR}/config.json" && \
    ls -lah "${MODEL_DIR}"

# ---- 빌드 전용 패키지 정리로 이미지 슬림화 ----
RUN apt-get purge -y build-essential && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# ---- 애플리케이션 코드 (마지막에 복사하여 캐시 최대화) ----
COPY ./app ./app

# 포트
EXPOSE 8005

# 실행 (워커 1개: 모델 메모리 중복 방지)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005"]
