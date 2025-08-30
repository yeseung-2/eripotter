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
    emb = os.getenv("EMBEDDER", "bge-m3").lower()  # 기본값을 bge-m3로 변경 (Qdrant 데이터와 일치)
    if emb == "bge-m3":
        try:
            from sentence_transformers import SentenceTransformer
            m = SentenceTransformer("BAAI/bge-m3")
            dim = 1024
            def encode(texts: List[str]) -> List[List[float]]:
                return m.encode([f"query: {t}" for t in texts], normalize_embeddings=True).tolist()
            return encode, dim, "bge-m3"
        except ImportError:
            logger.warning("sentence-transformers not installed, falling back to openai")
            return _get_openai_embedder()
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
            return _get_openai_embedder()
    elif emb == "openai":
        return _get_openai_embedder()
    else:
        logger.warning(f"Unknown EMBEDDER: {emb}, falling back to openai")
        return _get_openai_embedder()

def _get_openai_embedder():
    """OpenAI 임베더 설정 (bge-m3 fallback용)"""
    from openai import OpenAI
    
    try:
        # 기본 설정으로 OpenAI 클라이언트 초기화 (http_client 제거)
        client = OpenAI(
            api_key=os.environ["OPENAI_API_KEY"]
        )
        
        # bge-m3 fallback 시에는 1024 차원 유지 (Qdrant 데이터와 일치)
        model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")  # 1536차원으로 변경
        dim = 1536  # bge-m3(1024)와 가장 가까운 차원
        
        def encode(texts: List[str]) -> List[List[float]]:
            out = client.embeddings.create(model=model, input=texts)
            return [e.embedding for e in out.data]
        return encode, dim, "openai-fallback"
    except Exception as e:
        logger.error(f"OpenAI 임베더 초기화 실패: {e}")
        raise

# ===== LLM (선택) =====
def _get_llm():
    from langchain_openai import ChatOpenAI
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    try:
        # 기본 설정으로 ChatOpenAI 초기화 (http_client 제거)
        return ChatOpenAI(
            model=model, 
            temperature=0.7, 
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
    except Exception as e:
        logger.error(f"ChatOpenAI 초기화 실패: {e}")
        raise

# ===== 유틸 본체 =====
class RAGUtils:
    def __init__(self, collection_name: Optional[str] = None):
        qurl = os.getenv("QDRANT_URL", "https://qdrant-production-1efa.up.railway.app")
        # ✅ 키 이름 호환 (Railway 환경변수와 매칭)
        key = os.getenv("QDRANT_API_KEY") or os.getenv("QDRANT_SERVICE_API_KEY") or os.getenv("QDRANT__SERVICE__API_KEY")
        p = urlparse(qurl)
        self.qdrant_client = QdrantClient(
            host=p.hostname, port=p.port or (443 if p.scheme == "https" else 80),
            https=(p.scheme == "https"),
            api_key=key, prefer_grpc=False, timeout=60
        )

        # 임베더는 필요할 때만 초기화 (sentence_transformers 방지)
        self._encode = None
        self._dim = None
        self._embedder_name = None
        self.collection_name = collection_name or os.getenv("QDRANT_COLLECTION", "documents")
        self._ensure_collection_exists()
        self._llm = None
    
    @property
    def encode(self):
        """임베더 lazy loading"""
        if self._encode is None:
            self._encode, self._dim, self._embedder_name = _get_embedder()
        return self._encode
    
    @property
    def dim(self):
        """임베더 차원 lazy loading"""
        if self._dim is None:
            self._encode, self._dim, self._embedder_name = _get_embedder()
        return self._dim
    
    @property
    def embedder_name(self):
        """임베더 이름 lazy loading"""
        if self._embedder_name is None:
            self._encode, self._dim, self._embedder_name = _get_embedder()
        return self._embedder_name

    def _ensure_collection_exists(self):
        try:
            logger.info(f"🔍 Qdrant 컬렉션 확인: '{self.collection_name}'")
            info = self.qdrant_client.get_collection(self.collection_name)
            logger.info(f"✅ 컬렉션 존재 확인: '{self.collection_name}'")
            
            # 차원 검증 강화
            try:
                actual = info.config.params.vectors.size
                expected = self.dim
                embedder = self.embedder_name
                
                logger.info(f"📊 벡터 차원 검증: 실제={actual}, 예상={expected}, 임베더={embedder}")
                
                if actual and actual != expected:
                    error_msg = f"[{self.collection_name}] 벡터 차원 불일치: 실제={actual} != 예상={expected} (임베더={embedder})"
                    logger.error(f"❌ {error_msg}")
                    
                    # 차원 불일치 시 상세 정보 제공
                    if embedder == "openai-fallback":
                        logger.error("💡 해결 방법: EMBEDDER=bge-m3 환경변수 설정 또는 sentence-transformers 설치")
                    elif embedder == "bge-m3":
                        logger.error("💡 해결 방법: Qdrant 컬렉션 재생성 또는 다른 임베더 사용")
                    
                    raise ValueError(error_msg)
                    
            except AttributeError:
                logger.warning("⚠️ 벡터 차원 정보를 가져올 수 없음 (Qdrant 버전 호환성)")
            except Exception as e:
                logger.warning(f"⚠️ 차원 검증 중 오류: {e}")
                
        except Exception as e:
            logger.warning(f"⚠️ 컬렉션 확인 실패: {e}")
            # 컬렉션 생성 시에만 임베더 초기화
            try:
                dim = self.dim
                logger.info(f"🔨 컬렉션 생성 시작: '{self.collection_name}', 차원={dim}")
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
                )
                logger.info(f"✅ 컬렉션 생성 완료: '{self.collection_name}'")
            except Exception as create_error:
                logger.error(f"❌ 컬렉션 생성 실패: {create_error}")
                # Qdrant 연결 실패 시에도 서비스가 계속 작동하도록 함
                pass

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
            logger.info(f"🔍 Qdrant 검색 시작: 쿼리='{query}', 컬렉션='{self.collection_name}', limit={limit}")
            
            qvec = self.encode([query])[0]
            logger.info(f"📊 임베딩 완료: 벡터 차원 = {len(qvec)}")
            
            qf = None
            if filters:
                qf = Filter(must=[FieldCondition(key=k, match=MatchValue(value=v)) for k, v in filters.items()])
                logger.info(f"🔧 필터 적용: {filters}")
            
            res = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=qvec,
                limit=limit,
                query_filter=qf,
                with_payload=True,
                with_vectors=False
            )
            
            logger.info(f"✅ Qdrant 검색 완료: {len(res)} 개 결과")
            for i, r in enumerate(res):
                logger.info(f"  {i+1}. Score: {r.score:.3f}, Payload keys: {list(r.payload.keys()) if r.payload else []}")
            
            return [{"score": r.score, **(r.payload or {})} for r in res]
        except Exception as e:
            logger.error(f"❌ Qdrant 검색 실패: {e}")
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
