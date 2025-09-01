FROM python:3.11-slim
WORKDIR /app

# sys deps
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libgomp1 ca-certificates && rm -rf /var/lib/apt/lists/*

# py deps
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
    pip install --no-cache-dir -r requirements.txt

# 경로/캐시 통일
ENV HF_HOME=/app/.hf \
    TRANSFORMERS_CACHE=/app/.hf \
    SENTENCE_TRANSFORMERS_HOME=/app/.hf \
    MODEL_DIR=/app/model/bomi-ai \
    MODEL_NAME=/app/model/bomi-ai \
    PYTHONUNBUFFERED=1

# 앱
COPY ./app ./app
COPY app/domain/model/data/reg_test1.xlsx /app/data/

# --- 빌드 시 모델 내려받아 이미지에 굽기 ---
ARG HF_REPO_ID=galaxybuddy/bomi-ai
ARG HF_REV=main
ARG HF_TOKEN
RUN mkdir -p ${MODEL_DIR} && \
    huggingface-cli download "$HF_REPO_ID" --revision "$HF_REV" \
      --local-dir ${MODEL_DIR} --local-dir-use-symlinks False \
      ${HF_TOKEN:+--token "$HF_TOKEN"} && \
    test -f ${MODEL_DIR}/config.json && ls -lah ${MODEL_DIR}

# 스모크 테스트 (실패시 빌드 중단)
RUN python - <<'PY'
import os
from sentence_transformers import SentenceTransformer
p=os.environ["MODEL_DIR"]
m=SentenceTransformer(p, local_files_only=True, device="cpu")
print("✅ Model load OK:", p, m.encode(["ping"], normalize_embeddings=True).shape)
PY

# 런타임 완전 오프라인
ENV TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1 HF_HUB_ENABLE_HF_TRANSFER=1

EXPOSE 8005
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8005"]
