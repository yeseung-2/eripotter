#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAG 임베딩 서비스 (FAISS 전용, 최적화판)
- document/sr, document/tcfd 를 임베딩하여
  service/rag-service/vectordb/<collection> 아래에 FAISS 인덱스 저장
- 임베딩: HuggingFace (E5-base), GPU(CUDA) 기본 / 배치 사이즈 조절 가능
- 거리: 코사인(COSINE) 고정 (정규화된 E5와 최적 조합)
- Chroma / pgvector 코드 없음
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple

import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS, DistanceStrategy
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader


# ---------- 경로 설정 (절대 경로로 명확하게) ----------
PROJECT_ROOT = Path("C:/taezero/auto_sr")                       # 프로젝트 루트
BASE_PATH = PROJECT_ROOT / "document"                            # 문서 루트
SR_DIR = BASE_PATH / "sr"
TCFD_DIR = BASE_PATH / "tcfd"
FAISS_DIR = PROJECT_ROOT / "service" / "rag-service" / "vectordb"
FAISS_DIR.mkdir(parents=True, exist_ok=True)

# ---------- 로깅 ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("rag_faiss")

# ---------- 임베딩 모델 ----------
EMBED_MODEL_NAME = os.environ.get("EMBED_MODEL_NAME", "intfloat/multilingual-e5-base")
# GPU/CPU 전환: 기본은 cuda (GPU). GPU 부족/없다면 EMBED_DEVICE=cpu 로 바꿔 실행하세요.
EMBED_DEVICE = os.environ.get("EMBED_DEVICE", "cuda")  # "cuda" or "cpu"
# 배치 크기(메모리 부족 시 8, 4로 낮추세요)
EMBED_BATCH_SIZE = int(os.environ.get("EMBED_BATCH_SIZE", "16"))

embeddings = HuggingFaceEmbeddings(
    model_name=EMBED_MODEL_NAME,
    model_kwargs={"device": EMBED_DEVICE},
    encode_kwargs={
        "normalize_embeddings": True,   # 코사인과 궁합 최적
        "batch_size": EMBED_BATCH_SIZE,
    },
)

# ---------- 텍스트 분할 ----------
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=150,
    length_function=len,
    separators=["\n## ", "\n#", "\n\n", "\n", " "],
)

# ---------- 유틸 ----------
def extract_company_year(filename: str) -> Tuple[str, str]:
    """파일명 '회사명_연도.pdf' 형태에서 회사/연도 추출"""
    name = filename.replace(".pdf", "")
    parts = name.split("_")
    if len(parts) >= 2:
        return parts[0], parts[-1]
    return name, "unknown"

def load_tcfd_mapping() -> Dict[str, Dict[str, str]]:
    """
    TCFD 매핑: document/TCFD_MAPPING_FINAL.xlsx 를 읽어
    company 키로 대표 레코드를 1개씩 저장.
    필요한 필드만 남기고 컬럼명 정규화.
    """
    xls = BASE_PATH / "TCFD_MAPPING_FINAL.xlsx"
    if not xls.exists():
        logger.info("TCFD 매핑 파일이 없습니다. (건너뜀)")
        return {}
    try:
        df = pd.read_excel(xls)

        # 엑셀에서 잘린 컬럼명 보정 (케이스별 보강)
        rename_map = {
            '...on': 'description',
            'section': 'tcfd_section' if 'tcfd_section' not in df.columns else 'section',
        }
        df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

        # 필요 컬럼 확보
        needed = ['company', 'year', 'pillar', 'section_tag',
                  'tcfd_section', 'requirement_id', 'page_from', 'page_to']
        for col in needed:
            if col not in df.columns:
                df[col] = None

        # 회사별 대표 1행 (여러 개면 마지막)
        df = df.sort_index()
        grouped = df.groupby('company', dropna=True).tail(1)

        mapping: Dict[str, Dict[str, str]] = {}
        for _, r in grouped.iterrows():
            company = str(r.get('company') or '').strip()
            if not company:
                continue
            mapping[company] = {
                'pillar': str(r.get('pillar') or ''),
                'section_tag': str(r.get('section_tag') or ''),
                'tcfd_section': str(r.get('tcfd_section') or ''),
                'requirement_id': str(r.get('requirement_id') or ''),
                'mapped_page_from': str(r.get('page_from') or ''),
                'mapped_page_to': str(r.get('page_to') or ''),
                'mapping_year': str(r.get('year') or ''),
            }
        logger.info(f"TCFD 매핑 로드 완료: {len(mapping)}개 회사")
        return mapping
    except Exception as e:
        logger.error(f"TCFD 매핑 로드 실패: {e}")
        return {}

def load_pdf_dir(pdf_dir: Path) -> List[Any]:
    """PDF 디렉토리를 페이지 단위 Document 리스트로 변환(+메타)"""
    docs: List[Any] = []
    if not pdf_dir.exists():
        logger.error(f"PDF 디렉토리가 존재하지 않습니다: {pdf_dir}")
        return docs

    tcfd_map = load_tcfd_mapping()

    for pdf in sorted(pdf_dir.glob("*.pdf")):
        try:
            logger.info(f"PDF 로딩 중: {pdf.name}")
            pages = PyPDFLoader(str(pdf)).load()
            company, year = extract_company_year(pdf.name)
            for i, page in enumerate(pages):
                meta = {
                    "collection": pdf_dir.name,
                    "source": pdf.name,
                    "company": company,
                    "year": year,
                    "page_from": i + 1,
                    "page_to": i + 1,
                    "type": "pdf",
                }
                # 매핑 정보 병합 (존재 시)
                if company in tcfd_map:
                    meta.update(tcfd_map[company])
                page.metadata.update(meta)
            docs.extend(pages)
            logger.info(f"✅ {pdf.name} 로딩 완료 ({len(pages)} 페이지)")
        except Exception as e:
            logger.error(f"❌ {pdf.name} 로딩 실패: {e}")
    return docs

def split_docs(docs: List[Any]) -> Tuple[List[str], List[Dict[str, Any]]]:
    """LangChain Document 리스트를 청크 텍스트/메타로 변환"""
    texts, metas = [], []
    for d in docs:
        chunks = text_splitter.split_text(d.page_content or "")
        for c in chunks:
            if not c.strip():
                continue
            texts.append(c)
            metas.append(dict(d.metadata))
    return texts, metas

def upsert_faiss(texts: List[str], metadatas: List[Dict[str, Any]], collection_name: str):
    """FAISS 인덱스 생성/추가 저장 (로컬 영속, 코사인 거리)"""
    path = FAISS_DIR / collection_name
    path.mkdir(parents=True, exist_ok=True)
    idx_file, pkl_file = path / "index.faiss", path / "index.pkl"

    if idx_file.exists() and pkl_file.exists():
        store = FAISS.load_local(
            str(path),
            embeddings,
            allow_dangerous_deserialization=True,
            distance_strategy=DistanceStrategy.COSINE,
        )
        store.add_texts(texts, metadatas=metadatas)
        store.save_local(str(path))
        logger.info(f"🔁 FAISS 추가 저장: {collection_name}, +{len(texts)} chunks")
    else:
        store = FAISS.from_texts(
            texts,
            embeddings,
            metadatas=metadatas,
            distance_strategy=DistanceStrategy.COSINE,
        )
        store.save_local(str(path))
        logger.info(f"🆕 FAISS 신규 생성: {collection_name}, chunks={len(texts)}")

def build_collection(pdf_dir: Path, collection_name: str, test_query: str):
    docs = load_pdf_dir(pdf_dir)
    if not docs:
        logger.warning(f"문서가 없습니다: {collection_name}")
        return
    texts, metas = split_docs(docs)
    logger.info(f"✅ {collection_name}: {len(texts)}개 청크 생성")
    if not texts:
        logger.warning(f"{collection_name}: 생성된 청크가 없습니다 (스킵)")
        return

    upsert_faiss(texts, metas, collection_name)

    # 간단 검색 테스트
    try:
        path = FAISS_DIR / collection_name
        store = FAISS.load_local(
            str(path),
            embeddings,
            allow_dangerous_deserialization=True,
            distance_strategy=DistanceStrategy.COSINE,
        )
        results = store.similarity_search(test_query, k=3)
        logger.info(f"[검색] '{collection_name}' top-3 for '{test_query}'")
        for i, r in enumerate(results, 1):
            meta = getattr(r, "metadata", {})
            logger.info(f" {i}. {meta.get('source')} p.{meta.get('page_from')} - {r.page_content[:80]}...")
    except Exception as e:
        logger.warning(f"검색 테스트 실패: {e}")

def main():
    logger.info(f"🚀 FAISS 임베딩 저장 시작 (device={EMBED_DEVICE}, batch_size={EMBED_BATCH_SIZE}, model={EMBED_MODEL_NAME})")
    build_collection(SR_DIR, "sr_corpus", "기후변화")
    build_collection(TCFD_DIR, "standards", "거버넌스")
    logger.info("🎉 완료")
    logger.info(f"📁 인덱스 경로: {FAISS_DIR}\\<collection>\\(index.faiss, index.pkl)")

if __name__ == "__main__":
    main()

