import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ---------- 프로젝트 루트 경로 설정 (eripotter 프로젝트 구조에 맞게 수정) ----------
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # service/rag-service/app/config -> eripotter 루트
DEFAULT_FAISS_DIR = PROJECT_ROOT / "service" / "rag-service" / "vectordb"

faiss_dir_env = os.getenv("FAISS_DIR")
if not faiss_dir_env:
    # 기본값으로 프로젝트 내 vectordb 경로 사용
    FAISS_DIR = DEFAULT_FAISS_DIR
    print(f"[config] FAISS_DIR 환경변수가 없어 기본값 사용: {FAISS_DIR}")
else:
    FAISS_DIR = Path(faiss_dir_env)

# 지속가능경영보고서 컬렉션으로 변경
SR_COLLECTION = os.getenv("SR_COLLECTION", "sustainability_reports")
STD_COLLECTION = os.getenv("STD_COLLECTION", "standards")

EMBED_MODEL_NAME = os.getenv("EMBED_MODEL_NAME", "intfloat/multilingual-e5-base")
EMBED_DEVICE = os.getenv("EMBED_DEVICE", "cuda")
EMBED_BATCH_SIZE = int(os.getenv("EMBED_BATCH_SIZE", "16"))

LLM_BACKEND = os.getenv("LLM_BACKEND", "hf")  # "hf" | "openai"
BASE_MODEL = os.getenv("BASE_MODEL", "EleutherAI/polyglot-ko-3.8b")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

QUANTIZE = os.getenv("QUANTIZE", "").lower()  # "8bit" | "4bit" | ""
