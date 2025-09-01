"""
Sharing Model - 데이터 공유 관련 Pydantic 모델
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class RequestStatus(str, Enum):
    """데이터 요청 상태"""
    PENDING = "pending"
    ACTIVE = "active"
    REJECTED = "rejected"
    COMPLETED = "completed"
    INACTIVE = "inactive"

class DataType(str, Enum):
    """데이터 타입"""
    SUSTAINABILITY = "sustainability"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"

class UrgencyLevel(str, Enum):
    """긴급도"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"

class SharingRequestCreate(BaseModel):
    """데이터 공유 요청 생성 모델"""
    requester_company_id: str = Field(..., description="요청 회사 ID")
    requester_company_name: str = Field(..., description="요청 회사명")
    provider_company_id: str = Field(..., description="제공 회사 ID")
    provider_company_name: str = Field(..., description="제공 회사명")
    data_type: DataType = Field(..., description="데이터 타입")
    data_category: str = Field(..., description="데이터 카테고리")
    data_description: str = Field(..., description="데이터 설명")
    requested_fields: Optional[str] = Field(None, description="요청된 필드 목록")
    purpose: str = Field(..., description="사용 목적")
    usage_period: Optional[str] = Field(None, description="사용 기간")
    urgency_level: UrgencyLevel = Field(UrgencyLevel.NORMAL, description="긴급도")

class SharingRequestUpdate(BaseModel):
    """데이터 공유 요청 업데이트 모델"""
    status: Optional[RequestStatus] = None
    reviewer_id: Optional[str] = None
    reviewer_name: Optional[str] = None
    review_comment: Optional[str] = None
    data_url: Optional[str] = None

class SharingRequestResponse(BaseModel):
    """데이터 공유 요청 응답 모델"""
    id: str
    requester_company_id: str
    requester_company_name: str
    provider_company_id: str
    provider_company_name: str
    data_type: str
    data_category: str
    data_description: str
    requested_fields: Optional[str]
    purpose: str
    usage_period: Optional[str]
    urgency_level: str
    status: str
    requested_at: Optional[str]
    reviewed_at: Optional[str]
    approved_at: Optional[str]
    completed_at: Optional[str]
    reviewer_id: Optional[str]
    reviewer_name: Optional[str]
    review_comment: Optional[str]
    data_url: Optional[str]
    expiry_date: Optional[str]

class ReviewRequest(BaseModel):
    """검토 요청 모델"""
    reviewer_id: str = Field(..., description="검토자 ID")
    reviewer_name: str = Field(..., description="검토자명")
    review_comment: Optional[str] = Field(None, description="검토 의견")
    action: str = Field(..., description="액션 (approve/reject)")

class CompanyChainResponse(BaseModel):
    """협력사 체인 응답 모델"""
    id: str
    parent_company_id: str
    child_company_id: str
    chain_level: int
    relationship_type: str
    created_at: Optional[str]

class DataSharingStats(BaseModel):
    """데이터 공유 통계 모델"""
    total_requests: int = 0
    pending_requests: int = 0
    approved_requests: int = 0
    rejected_requests: int = 0
    completed_requests: int = 0
    avg_response_time_hours: float = 0.0

class ApiResponse(BaseModel):
    """공통 API 응답 모델"""
    status: str = "success"
    message: Optional[str] = None
    data: Optional[dict] = None
    error: Optional[str] = None
