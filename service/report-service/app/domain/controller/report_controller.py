from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Dict, Any, Optional
from ..service.report_service import ReportService
from ..model.report_model import (
    DocumentEmbedRequest, 
    DocumentEmbedResponse,
    ReportGenerateRequest,
    ReportGenerateResponse,
    DocumentSearchRequest,
    DocumentSearchResponse
)
import uuid

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])
report_service = ReportService()

@router.post("/embed-document", response_model=DocumentEmbedResponse)
async def embed_document(
    document_id: str = Form(...),
    content: str = Form(...),
    metadata: Optional[str] = Form(None)
):
    """문서를 벡터화하여 저장"""
    try:
        # 메타데이터 파싱
        parsed_metadata = None
        if metadata:
            import json
            parsed_metadata = json.loads(metadata)
        
        result = report_service.embed_document(document_id, content, parsed_metadata)
        
        if result["status"] == "success":
            return DocumentEmbedResponse(
                success=True,
                document_id=result["document_id"],
                message="문서가 성공적으로 임베딩되었습니다."
            )
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search-documents", response_model=DocumentSearchResponse)
async def search_documents(request: DocumentSearchRequest):
    """유사한 문서 검색"""
    try:
        documents = report_service.search_similar_documents(
            request.query, 
            request.limit
        )
        
        return DocumentSearchResponse(
            success=True,
            documents=documents,
            message=f"{len(documents)}개의 유사한 문서를 찾았습니다."
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-draft", response_model=ReportGenerateResponse)
async def generate_report_draft(request: ReportGenerateRequest):
    """RAG를 사용하여 보고서 초안 생성"""
    try:
        result = report_service.generate_report_draft(
            request.query,
            request.context_documents
        )
        
        if result["status"] == "success":
            return ReportGenerateResponse(
                success=True,
                report_draft=result["report_draft"],
                context_documents=result["context_documents"],
                message="보고서 초안이 성공적으로 생성되었습니다."
            )
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """문서 삭제"""
    try:
        result = report_service.delete_document(document_id)
        
        if result["status"] == "success":
            return {"success": True, "message": "문서가 삭제되었습니다."}
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """서비스 상태 확인"""
    return {"status": "healthy", "service": "report-service"}
