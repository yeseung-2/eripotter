"""
공통 RAG 유틸리티 (서비스 내 재사용)
- EMBEDDER, OPENAI_MODEL 등 환경변수로 동작 제어
- Qdrant는 URL을 host/port로 파싱해 HTTPS + HTTP만(prefer_grpc=False)
- 포인트 ID는 UUIDv5로 안정 생성
"""
from typing import List, Dict, Any, Optional
import os
import logging
from urllib.parse import urlparse
from uuid import uuid5, NAMESPACE_URL

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, PointIdsList

logger = logging.getLogger(__name__)

# ===== 임베더 선택 =====
def _get_embedder():
    emb = os.getenv("EMBEDDER", "bge-m3").lower()  # "bge-m3" | "minilm" | "openai"
    if emb == "bge-m3":
        from sentence_transformers import SentenceTransformer
        m = SentenceTransformer("BAAI/bge-m3")
        dim = 1024
        def encode(texts: List[str]) -> List[List[float]]:
            return m.encode([f"query: {t}" for t in texts], normalize_embeddings=True).tolist()
        return encode, dim, "bge-m3"
    elif emb == "minilm":
        try:
            from sentence_transformers import SentenceTransformer
            m = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            dim = 384
            def encode(texts: List[str]) -> List[List[float]]:
                return m.encode(texts, normalize_embeddings=True).tolist()
            return encode, dim, "minilm"
        except ImportError:
            logger.warning("sentence-transformers not installed, falling back to openai")
            # fallback to openai
            from openai import OpenAI
            client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-large")
            dim = 3072
            def encode(texts: List[str]) -> List[List[float]]:
                out = client.embeddings.create(model=model, input=texts)
                return [e.embedding for e in out.data]
            return encode, dim, "openai"
    elif emb == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-large")  # 3072차원
        dim = 3072
        def encode(texts: List[str]) -> List[List[float]]:
            out = client.embeddings.create(model=model, input=texts)
            return [e.embedding for e in out.data]
        return encode, dim, "openai"
    else:
        raise ValueError(f"Unknown EMBEDDER: {emb}")

# ===== LLM (선택) =====
def _get_llm():
    from langchain_openai import ChatOpenAI
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    return ChatOpenAI(model=model, temperature=0.7, openai_api_key=os.getenv("OPENAI_API_KEY"))

# ===== 유틸 본체 =====
class RAGUtils:
    def __init__(self, collection_name: Optional[str] = None):
        qurl = os.getenv("QDRANT_URL", "https://qdrant-production-1efa.up.railway.app")
        key = os.getenv("QDRANT__SERVICE__API_KEY")  # Railway 실제 변수명에 맞게 수정
        p = urlparse(qurl)
        self.qdrant_client = QdrantClient(
            host=p.hostname, port=p.port or (443 if p.scheme == "https" else 80),
            https=(p.scheme == "https"),
            api_key=key, prefer_grpc=False, timeout=60
        )

        self.encode, self.dim, self.embedder_name = _get_embedder()
        self.collection_name = collection_name or os.getenv("QDRANT_COLLECTION", "documents")
        self._ensure_collection_exists()
        self._llm = None

    def _ensure_collection_exists(self):
        try:
            info = self.qdrant_client.get_collection(self.collection_name)
            try:
                actual = info.config.params.vectors.size
                if actual and actual != self.dim:
                    raise ValueError(
                        f"[{self.collection_name}] vector size mismatch: {actual} != {self.dim} "
                        f"(embedder={self.embedder_name})"
                    )
            except Exception:
                pass
        except Exception:
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.dim, distance=Distance.COSINE)
            )

    @staticmethod
    def _uuid_from_text_id(text_id: str) -> str:
        return str(uuid5(NAMESPACE_URL, str(text_id)))

    def embed_text(self, text_id: str, text: str, metadata: Optional[Dict[str, Any]] = None):
        try:
            vec = self.encode([text])[0]
            payload = dict(metadata or {})
            payload["text_id"] = str(text_id)
            payload["content"] = text

            point = PointStruct(
                id=self._uuid_from_text_id(text_id),
                vector=vec,
                payload=payload
            )
            self.qdrant_client.upsert(collection_name=self.collection_name, points=[point], wait=True)
            return {"status": "success", "text_id": text_id}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def search_similar(self, query: str, limit: int = 5, filters: Optional[Dict[str, Any]] = None):
        try:
            qvec = self.encode([query])[0]
            qf = None
            if filters:
                qf = Filter(must=[FieldCondition(key=k, match=MatchValue(value=v)) for k, v in filters.items()])
            res = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=qvec,
                limit=limit,
                query_filter=qf,
                with_payload=True,
                with_vectors=False
            )
            return [{"score": r.score, **(r.payload or {})} for r in res]
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def search(self, query: str, limit: int = 5, score_threshold: float = 0.0):
        """검색 메서드 (score_threshold 지원)"""
        try:
            qvec = self.encode([query])[0]
            res = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=qvec,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False
            )
            return [{"score": r.score, **(r.payload or {})} for r in res]
        except Exception as e:
            logger.error(f"검색 실패: {e}")
            return []

    def generate_with_context(self, query: str, context_documents: List[Dict[str, Any]],
                              system_prompt: str = "당신은 도움이 되는 AI 어시스턴트입니다."):
        try:
            if self._llm is None:
                self._llm = _get_llm()

            parts = []
            for i, doc in enumerate(context_documents, 1):
                title = doc.get("title", "")
                content = doc.get("content", "")
                pages = doc.get("pages", [])
                part = f"[참고 문서 {i}]"
                if title: part += f"\n제목: {title}"
                if pages: part += f"\n페이지: {pages}"
                part += f"\n내용:\n{content}\n"
                parts.append(part)
            context = "\n".join(parts)

            from langchain.schema import HumanMessage, SystemMessage
            msgs = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"쿼리: {query}\n\n참고 문서:\n{context}\n\n위 정보를 바탕으로 답변해주세요.")
            ]
            resp = self._llm.invoke(msgs)
            return {"status": "success", "response": resp.content, "context_documents": context_documents}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def delete_text(self, text_id: str):
        try:
            pid = self._uuid_from_text_id(text_id)
            self.qdrant_client.delete(collection_name=self.collection_name, points_selector=PointIdsList(points=[pid]), wait=True)
            return {"status": "success", "text_id": text_id}
        except Exception as e:
            return {"status": "error", "message": str(e)}
