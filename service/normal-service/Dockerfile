# Python 3.11
FROM python:3.11-slim

# 기본 환경
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    LANG=C.UTF-8

# 캐시/모델 경로 (오프라인 플래그는 '다운로드 이후'에 설정)
ENV HF_HOME=/opt/hf \
    TRANSFORMERS_CACHE=/opt/hf \
    SENTENCE_TRANSFORMERS_HOME=/opt/hf \
    MODEL_DIR=/opt/models/bomi-ai

WORKDIR /app

# 시스템 패키지 (torch CPU용 OpenMP 포함)
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libgomp1 && \
    rm -rf /var/lib/apt/lists/*

# 파이썬 의존성
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.4.1 && \
    pip install --no-cache-dir \
        "transformers==4.44.2" \
        "sentence-transformers==5.1.0" \
        "huggingface-hub>=0.23" \
        "safetensors>=0.4.2" \
        "accelerate>=0.28" \
        "huggingface_hub[cli]" \
        hf_transfer && \
    pip install --no-cache-dir -r requirements.txt && \
    python - <<'PY'
import torch, transformers, sentence_transformers
print("✅ Deps OK:", torch.__version__, transformers.__version__, sentence_transformers.__version__)
PY

# 모델 프리베이크 (빌드 시 1회 다운로드)
ARG HF_REPO_ID=galaxybuddy/bomi-ai
ARG HF_REV=main
ARG HF_TOKEN
RUN mkdir -p "${MODEL_DIR}" && \
    echo "⬇️  Download model: ${HF_REPO_ID}@${HF_REV}" && \
    HF_HUB_OFFLINE=0 TRANSFORMERS_OFFLINE=0 HF_HUB_ENABLE_HF_TRANSFER=1 \
    hf download "${HF_REPO_ID}" \
      --repo-type model \
      --revision "${HF_REV}" \
      --local-dir "${MODEL_DIR}" \
      ${HF_TOKEN:+--token "${HF_TOKEN}"} && \
    test -f "${MODEL_DIR}/config.json" && \
    ls -lah "${MODEL_DIR}"

# (선택) 모델 로드 스모크 테스트 - 빌드 타임에 로컬 로딩 검증
RUN python - <<'PY'
import os
from sentence_transformers import SentenceTransformer
p = os.environ.get("MODEL_DIR", "/opt/models/bomi-ai")
m = SentenceTransformer(p, local_files_only=True)
print("✅ Model load OK at:", p, " | test embedding:", m.encode(["ping"], normalize_embeddings=True).shape)
PY

# 빌드용 패키지 정리로 슬림화
RUN apt-get purge -y build-essential && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# 애플리케이션 코드
COPY ./app ./app

# 런타임 오프라인 모드 (이제부터 네트워크 없이 로컬만 사용)
ENV TRANSFORMERS_OFFLINE=1 \
    HF_HUB_OFFLINE=1 \
    HF_HUB_ENABLE_HF_TRANSFER=1

EXPOSE 8005
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005"]
