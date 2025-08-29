"""
Report Models - 보고서 관련 API 요청/응답 모델
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime

# 기본 응답 모델
class BaseResponse(BaseModel):
    success: bool = True
    message: str = ""

    model_config = ConfigDict(from_attributes=True)

# 보고서 생성 요청/응답
class ReportCreateRequest(BaseModel):
    topic: str = Field(..., description="지표 ID (예: KBZ-EN22)")
    company_name: str = Field(..., description="회사명")
    report_type: str = Field(..., description="보고서 유형")
    title: Optional[str] = Field(None, description="보고서 제목")
    content: Optional[str] = Field(None, description="보고서 내용")
    metadata: Optional[Dict[str, Any]] = Field(None, description="메타데이터")

class ReportCreateResponse(BaseResponse):
    report_id: int
    topic: str
    company_name: str
    report_type: str

# 보고서 조회 요청/응답
class ReportGetRequest(BaseModel):
    topic: str = Field(..., description="지표 ID")
    company_name: str = Field(..., description="회사명")

class ReportGetResponse(BaseResponse):
    id: int
    topic: str
    company_name: str
    report_type: str
    title: Optional[str]
    content: Optional[str]
    metadata: Optional[Dict[str, Any]]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]

# 보고서 업데이트 요청/응답
class ReportUpdateRequest(BaseModel):
    topic: str = Field(..., description="지표 ID")
    company_name: str = Field(..., description="회사명")
    title: Optional[str] = Field(None, description="보고서 제목")
    content: Optional[str] = Field(None, description="보고서 내용")
    metadata: Optional[Dict[str, Any]] = Field(None, description="메타데이터")
    status: Optional[str] = Field(None, description="상태")

class ReportUpdateResponse(BaseResponse):
    report_id: int
    updated_at: datetime

# 보고서 삭제 요청/응답
class ReportDeleteRequest(BaseModel):
    topic: str = Field(..., description="지표 ID")
    company_name: str = Field(..., description="회사명")

class ReportDeleteResponse(BaseResponse):
    deleted: bool

# 보고서 목록 조회 응답
class ReportListResponse(BaseResponse):
    reports: List[ReportGetResponse]
    total_count: int

# 보고서 완료 처리 요청/응답
class ReportCompleteRequest(BaseModel):
    topic: str = Field(..., description="지표 ID")
    company_name: str = Field(..., description="회사명")

class ReportCompleteResponse(BaseResponse):
    completed: bool


# ===== 지표 전용 요청 스키마 (Body 명시) =====

class IndicatorDraftRequest(BaseModel):
    company_name: str
    inputs: Dict[str, Any] = Field(default_factory=dict)

class IndicatorSaveRequest(BaseModel):
    company_name: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
