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
    """
    EMBEDDER=bge-m3|minilm|openai
    - bge-m3: 1024차원 (SentenceTransformer 필요)
    - minilm: 384차원 (SentenceTransformer 필요)
    - openai: 1536차원 (OpenAI Embeddings)
    """
    emb = os.getenv("EMBEDDER", "bge-m3").lower()  # 기본값 bge-m3 (Qdrant 1024과 일치 가정)

    # sentence-transformers 설치 여부 확인
    try:
        import sentence_transformers  # noqa: F401
        logger.info("✅ sentence-transformers 설치됨")
        sentence_transformers_available = True
    except ImportError:
        logger.warning("❌ sentence-transformers 설치되지 않음")
        sentence_transformers_available = False

    if emb == "bge-m3":
        # ⚠️ bge-m3 사용 시에는 반드시 sentence-transformers(+torch)가 필요
        if not sentence_transformers_available:
            raise RuntimeError(
                "EMBEDDER=bge-m3 이지만 sentence-transformers 미설치. "
                "pip install sentence-transformers torch transformers "
                "또는 컬렉션을 1536차원으로 재색인 후 EMBEDDER=openai 사용."
            )
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("🔧 bge-m3 임베더 초기화 중...")
            m = SentenceTransformer("BAAI/bge-m3")
            dim = 1024
            def encode(texts: List[str]) -> List[List[float]]:
                # bge-m3 권장: 쿼리 접두어
                return m.encode([f"query: {t}" for t in texts], normalize_embeddings=True).tolist()
            logger.info("✅ bge-m3 임베더 초기화 완료")
            return encode, dim, "bge-m3"
        except Exception as e:
            logger.error(f"❌ bge-m3 임베더 초기화 실패: {e}")
            raise

    elif emb == "minilm":
        if not sentence_transformers_available:
            raise RuntimeError("EMBEDDER=minilm 이지만 sentence-transformers 미설치.")
        try:
            from sentence_transformers import SentenceTransformer
            m = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            dim = 384
            def encode(texts: List[str]) -> List[List[float]]:
                return m.encode(texts, normalize_embeddings=True).tolist()
            return encode, dim, "minilm"
        except Exception as e:
            logger.error(f"❌ minilm 임베더 초기화 실패: {e}")
            raise

    elif emb == "openai":
        return _get_openai_embedder()

    else:
        logger.warning(f"Unknown EMBEDDER: {emb}, falling back to openai")
        return _get_openai_embedder()


def _get_openai_embedder():
    """OpenAI 임베더 설정 (1536차원)."""
    # ✅ 방어: 혹시 남아 있을지 모르는 프록시 ENV 무시
    for k in ("OPENAI_PROXY", "HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY"):
        os.environ.pop(k, None)

    from openai import OpenAI
    try:
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")  # 1536차원
        dim = 1536
        def encode(texts: List[str]) -> List[List[float]]:
            out = client.embeddings.create(model=model, input=texts)
            return [e.embedding for e in out.data]
        return encode, dim, "openai"
    except Exception as e:
        logger.error(f"OpenAI 임베더 초기화 실패: {e}")
        raise


# ===== LLM (선택) =====
def _get_llm():
    from langchain_openai import ChatOpenAI
    # ✅ 방어: 프록시 ENV 무시 (OpenAI 1.x 'proxies' 인자 미지원 이슈 회피)
    for k in ("OPENAI_PROXY", "HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY"):
        os.environ.pop(k, None)

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    try:
        # 명시적으로 허용된 파라미터만 전달
        llm_params = {
            "model": model,
            "temperature": 0.7,
            "openai_api_key": os.getenv("OPENAI_API_KEY")
        }
        
        return ChatOpenAI(**llm_params)
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
            host=p.hostname,
            port=p.port or (443 if p.scheme == "https" else 80),
            https=(p.scheme == "https"),
            api_key=key,
            prefer_grpc=False,
            timeout=60,
        )

        # 임베더는 필요할 때만 초기화
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

            # 차원 검증 & 컬렉션 차원에 맞게 EMBEDDER 강제
            actual = None
            try:
                # Qdrant 버전에 따라 vectors가 단일/멀티일 수 있음
                vectors = info.config.params.vectors
                if hasattr(vectors, "size"):
                    actual = vectors.size
                elif isinstance(vectors, dict):
                    first = next(iter(vectors.values()))
                    actual = getattr(first, "size", None)
            except Exception:
                pass

            if actual:
                logger.info(f"📊 컬렉션 벡터 차원: {actual}")
                if actual == 1024:
                    os.environ["EMBEDDER"] = "bge-m3"
                    logger.info("🔧 EMBEDDER를 bge-m3로 설정 (1024차원)")
                elif actual == 1536:
                    os.environ["EMBEDDER"] = "openai"
                    logger.info("🔧 EMBEDDER를 openai로 설정 (1536차원)")
                else:
                    logger.warning(f"⚠️ 알 수 없는 차원: {actual} (지원: 1024=bge-m3, 1536=openai)")

                # 기대 차원과 다르면 경고 (이 시점에서 self.dim은 강제된 EMBEDDER 기준)
                try:
                    expected = self.dim
                    if expected and expected != actual:
                        logger.error(f"❌ 벡터 차원 불일치: Qdrant={actual}, Embedder={expected}")
                        logger.error("💡 해결: EMBEDDER를 컬렉션 차원과 일치(1024=bge-m3, 1536=openai)시키세요.")
                except RuntimeError as e:
                    # 예: bge-m3인데 sentence-transformers 미설치
                    logger.warning(f"⚠️ 차원 검증 중 오류: {e}")
                except Exception as e:
                    logger.warning(f"⚠️ 차원 검증 중 예외: {e}")

        except Exception as e:
            logger.warning(f"⚠️ 컬렉션 확인 실패: {e}")
            # 컬렉션 미존재 시 생성 (현재 EMBEDDER 기준 차원)
            try:
                dim = self.dim
                logger.info(f"🔨 컬렉션 생성 시작: '{self.collection_name}', 차원={dim}")
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
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
                payload=payload,
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
                with_vectors=False,
            )

            logger.info(f"✅ Qdrant 검색 완료: {len(res)} 개 결과")
            for i, r in enumerate(res):
                logger.info(
                    f"  {i+1}. Score: {r.score:.3f}, "
                    f"Payload keys: {list(r.payload.keys()) if r.payload else []}"
                )

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
                with_vectors=False,
            )
            return [{"score": r.score, **(r.payload or {})} for r in res]
        except Exception as e:
            logger.error(f"검색 실패: {e}")
            return []

    def generate_with_context(
        self,
        query: str,
        context_documents: List[Dict[str, Any]],
        system_prompt: str = "당신은 도움이 되는 AI 어시스턴트입니다.",
    ):
        try:
            if self._llm is None:
                self._llm = _get_llm()

            parts = []
            for i, doc in enumerate(context_documents, 1):
                title = doc.get("title", "")
                content = doc.get("content", "")
                pages = doc.get("pages", [])
                part = f"[참고 문서 {i}]"
                if title:
                    part += f"\n제목: {title}"
                if pages:
                    part += f"\n페이지: {pages}"
                part += f"\n내용:\n{content}\n"
                parts.append(part)
            context = "\n".join(parts)

            from langchain.schema import HumanMessage, SystemMessage
            msgs = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"쿼리: {query}\n\n참고 문서:\n{context}\n\n위 정보를 바탕으로 답변해주세요."),
            ]
            resp = self._llm.invoke(msgs)
            return {"status": "success", "response": resp.content, "context_documents": context_documents}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def delete_text(self, text_id: str):
        try:
            pid = self._uuid_from_text_id(text_id)
            self.qdrant_client.delete(
                collection_name=self.collection_name,
                points_selector=PointIdsList(points=[pid]),
                wait=True,
            )
            return {"status": "success", "text_id": text_id}
        except Exception as e:
            return {"status": "error", "message": str(e)}
