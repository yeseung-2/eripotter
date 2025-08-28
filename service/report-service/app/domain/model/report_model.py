from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class DocumentEmbedRequest(BaseModel):
    document_id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class DocumentEmbedResponse(BaseModel):
    success: bool
    document_id: str
    message: str

class DocumentSearchRequest(BaseModel):
    query: str
    limit: int = 5

class DocumentSearchResponse(BaseModel):
    success: bool
    documents: List[Dict[str, Any]]
    message: str

class ReportGenerateRequest(BaseModel):
    query: str
    context_documents: Optional[List[Dict[str, Any]]] = None

class ReportGenerateResponse(BaseModel):
    success: bool
    report_draft: str
    context_documents: List[Dict[str, Any]]
    message: str

class ReportBase(BaseModel):
    title: str
    content: str
    author: str
    status: str = "draft"

class ReportCreate(ReportBase):
    pass

class ReportUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None

class Report(ReportBase):
    id: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
