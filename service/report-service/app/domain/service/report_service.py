from typing import List, Dict, Any, Optional
from .rag_utils import RAGUtils

class ReportService:
    def __init__(self):
        # RAG 유틸리티 초기화
        self.rag_utils = RAGUtils(collection_name="reports")
    
    def embed_document(self, document_id: str, content: str, metadata: Dict[str, Any] = None):
        """문서를 벡터화하여 저장"""
        return self.rag_utils.embed_text(document_id, content, metadata)
    
    def search_similar_documents(self, query: str, limit: int = 5):
        """쿼리와 유사한 문서 검색"""
        return self.rag_utils.search_similar(query, limit)
    
    def generate_report_draft(self, query: str, context_documents: List[Dict] = None):
        """RAG를 사용하여 보고서 초안 생성"""
        try:
            # 관련 문서 검색
            if context_documents is None:
                context_documents = self.search_similar_documents(query, limit=5)
            
            # 보고서 작성 전문가 프롬프트
            system_prompt = "당신은 전문적인 보고서 작성자입니다. 주어진 정보를 바탕으로 구조화된 보고서를 작성해주세요."
            
            result = self.rag_utils.generate_with_context(
                query=query,
                context_documents=context_documents,
                system_prompt=system_prompt
            )
            
            if result["status"] == "success":
                return {
                    "status": "success",
                    "report_draft": result["response"],
                    "context_documents": result["context_documents"]
                }
            else:
                return result
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def delete_document(self, document_id: str):
        """문서 삭제"""
        return self.rag_utils.delete_text(document_id)