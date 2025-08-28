"""
공통 RAG 유틸리티
다른 서비스에서도 재사용 가능한 RAG 기능들
"""
from typing import List, Dict, Any, Optional
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

class RAGUtils:
    """공통 RAG 유틸리티 클래스"""
    
    def __init__(self, collection_name: str = "documents"):
        self.qdrant_client = QdrantClient(
            url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.collection_name = collection_name
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """컬렉션 존재 확인 및 생성"""
        try:
            collections = self.qdrant_client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=384,
                        distance=Distance.COSINE
                    )
                )
        except Exception as e:
            print(f"컬렉션 생성 중 오류: {e}")
    
    def embed_text(self, text_id: str, text: str, metadata: Dict[str, Any] = None):
        """텍스트 임베딩 및 저장"""
        try:
            embedding = self.embedding_model.encode(text)
            
            if metadata is None:
                metadata = {}
            metadata['text_id'] = text_id
            metadata['content'] = text
            
            point = PointStruct(
                id=text_id,
                vector=embedding.tolist(),
                payload=metadata
            )
            
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            return {"status": "success", "text_id": text_id}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def search_similar(self, query: str, limit: int = 5):
        """유사한 텍스트 검색"""
        try:
            query_embedding = self.embedding_model.encode(query)
            
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding.tolist(),
                limit=limit
            )
            
            return [result.payload for result in search_results]
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def generate_with_context(self, query: str, context_documents: List[Dict], 
                            system_prompt: str = "당신은 도움이 되는 AI 어시스턴트입니다."):
        """컨텍스트를 사용한 텍스트 생성"""
        try:
            context = "\n\n".join([doc.get('content', '') for doc in context_documents])
            
            system_message = SystemMessage(content=system_prompt)
            human_message = HumanMessage(content=f"""
쿼리: {query}

참고 문서:
{context}

위 정보를 바탕으로 답변해주세요.
""")
            
            response = self.llm.invoke([system_message, human_message])
            
            return {
                "status": "success",
                "response": response.content,
                "context_documents": context_documents
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def delete_text(self, text_id: str):
        """텍스트 삭제"""
        try:
            self.qdrant_client.delete(
                collection_name=self.collection_name,
                points_selector=[text_id]
            )
            return {"status": "success", "text_id": text_id}
        except Exception as e:
            return {"status": "error", "message": str(e)}
