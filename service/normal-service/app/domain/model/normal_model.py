"""
Normal Service Models - Pydantic 모델 정의
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

# ===== 기본 모델 =====

class ValidationIssue(BaseModel):
    """검증 이슈 모델"""
    field: str
    message: str
    severity: str = "error"  # error, warning, info

class ValidationResult(BaseModel):
    """검증 결과 모델"""
    is_valid: bool
    issues: List[ValidationIssue] = []
    standardized_data: Dict[str, Any] = {}
    esg_score: int = 0
    completion_rate: int = 0

# ===== 협력사 ESG 데이터 모델 =====

class ESGCategory(str, Enum):
    """ESG 카테고리"""
    ENVIRONMENTAL = "environmental"
    SOCIAL = "social"
    GOVERNANCE = "governance"

class ESGData(BaseModel):
    """ESG 데이터 모델"""
    environmental: Dict[str, Any] = Field(default_factory=dict, description="환경 데이터")
    social: Dict[str, Any] = Field(default_factory=dict, description="사회 데이터")
    governance: Dict[str, Any] = Field(default_factory=dict, description="지배구조 데이터")

class PartnerUploadRequest(BaseModel):
    """협력사 파일 업로드 요청"""
    company_id: str = Field(..., description="협력사 ID")
    file_type: str = Field(..., description="파일 타입")
    description: Optional[str] = Field(None, description="파일 설명")

class PartnerUploadResponse(BaseModel):
    """협력사 파일 업로드 응답"""
    upload_id: str
    filename: str
    size: int
    company_id: str
    upload_time: datetime
    status: str
    validation_status: str = "pending"

class PartnerDashboardData(BaseModel):
    """협력사 대시보드 데이터"""
    company_id: str
    esg_score: int
    completion_rate: int
    improvement_items: int
    next_deadline: str
    categories: Dict[str, Dict[str, Any]]

class ESGReportRequest(BaseModel):
    """ESG 보고서 생성 요청"""
    report_type: str = Field(..., description="보고서 타입")
    company_id: str = Field(..., description="협력사 ID")
    format: str = Field("pdf", description="보고서 형식")

class ESGReportResponse(BaseModel):
    """ESG 보고서 생성 응답"""
    report_id: str
    company_id: str
    report_type: str
    generated_at: datetime
    download_url: Optional[str] = None
    content: Dict[str, Any]

class ESGSchemaResponse(BaseModel):
    """ESG 스키마 응답"""
    industry: str
    schema: Dict[str, List[str]]
    version: str = "1.0"
    last_updated: datetime

# ===== 파일 업로드 관련 모델 =====

class FileUploadStatus(str, Enum):
    """파일 업로드 상태"""
    UPLOADING = "uploading"
    VALIDATING = "validating"
    SUCCESS = "success"
    ERROR = "error"

class FileInfo(BaseModel):
    """파일 정보"""
    id: str
    name: str
    size: int
    type: str
    status: FileUploadStatus
    progress: int = 0
    validation_result: Optional[ValidationResult] = None
    uploaded_at: datetime
    company_id: Optional[str] = None

# ===== API 응답 모델 =====

class APIResponse(BaseModel):
    """API 응답 기본 모델"""
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class PartnerDataValidationRequest(BaseModel):
    """협력사 데이터 검증 요청"""
    data: ESGData
    company_id: str
    industry: Optional[str] = "general"

class PartnerDataValidationResponse(BaseModel):
    """협력사 데이터 검증 응답"""
    validation_result: ValidationResult
    recommendations: List[str] = []
    next_steps: List[str] = []
