# ===== Base =====
FROM python:3.11-slim

# Basic env
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    LANG=C.UTF-8

# Hugging Face caches & model path (build+run 공통)
ENV HF_HOME=/opt/hf \
    TRANSFORMERS_CACHE=/opt/hf \
    SENTENCE_TRANSFORMERS_HOME=/opt/hf \
    MODEL_DIR=/opt/models/bomi-ai \
    MODEL_NAME=/opt/models/bomi-ai

WORKDIR /app

# ===== System deps =====
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      libgomp1 \
      ca-certificates \
   && rm -rf /var/lib/apt/lists/*

# ===== Python deps =====
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

# ===== Prebake model into the image =====
# (빌드 시 1회 다운로드; private repo면 --build-arg HF_TOKEN=<token> 전달)
ARG HF_REPO_ID=galaxybuddy/bomi-ai
ARG HF_REV=main
ARG HF_TOKEN
RUN mkdir -p "${MODEL_DIR}" && \
    echo "⬇️  Download model: ${HF_REPO_ID}@${HF_REV}" && \
    HF_HUB_OFFLINE=0 TRANSFORMERS_OFFLINE=0 HF_HUB_ENABLE_HF_TRANSFER=1 \
    huggingface-cli download "${HF_REPO_ID}" --revision "${HF_REV}" \
      --local-dir "${MODEL_DIR}" --local-dir-use-symlinks False \
      ${HF_TOKEN:+--token "${HF_TOKEN}"} && \
    test -f "${MODEL_DIR}/config.json" && \
    ls -lah "${MODEL_DIR}"

# ===== Build-time smoke test (fail-fast) =====
RUN python - <<'PY'
import os
from sentence_transformers import SentenceTransformer
p = os.environ.get("MODEL_DIR", "/opt/models/bomi-ai")
m = SentenceTransformer(p, local_files_only=True, device="cpu")
print("✅ Model load OK at:", p, "| test:", m.encode(["ping"], normalize_embeddings=True).shape)
PY

# ===== App code =====
COPY ./app ./app
# (옵션) 데이터/리소스가 따로 있으면 여기서 COPY

# ===== Slim final image =====
RUN apt-get purge -y build-essential && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# ===== Runtime: fully offline =====
ENV TRANSFORMERS_OFFLINE=1 \
    HF_HUB_OFFLINE=1 \
    HF_HUB_ENABLE_HF_TRANSFER=1

EXPOSE 8005
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005"]
