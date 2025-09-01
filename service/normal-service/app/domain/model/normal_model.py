# app/domain/model/normal_model.py
"""
Normal Service Models - Pydantic 모델 정의 (Refactored)
- 기존 스키마 유지
- Optional/기본값 명확화, default_factory 활용
- 타임스탬프는 ISO 문자열(str)로 일관 (라우터 응답과 일치)
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ===== 기본 모델 =====

class ValidationIssue(BaseModel):
    """검증 이슈 모델"""
    field: str
    message: str
    severity: str = "error"  # error, warning, info


class ValidationResult(BaseModel):
    """검증 결과 모델"""
    is_valid: bool
    issues: List[ValidationIssue] = Field(default_factory=list)
    standardized_data: Dict[str, Any] = Field(default_factory=dict)
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
    recommendations: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)


# ===== 물질 매핑 관련 모델 =====

class SubstanceMappingRequest(BaseModel):
    """단일 물질 매핑 요청"""
    substance_name: str = Field(..., description="매핑할 물질명")
    company_id: Optional[str] = Field(None, description="회사 ID")
    confidence_threshold: float = Field(0.7, description="신뢰도 임계값")


class SubstanceMappingBatchRequest(BaseModel):
    """배치 물질 매핑 요청"""
    substance_names: List[str] = Field(..., description="매핑할 물질명 목록")
    company_id: Optional[str] = Field(None, description="회사 ID")
    confidence_threshold: float = Field(0.7, description="신뢰도 임계값")


class SubstanceMappingResult(BaseModel):
    """물질 매핑 결과"""
    original_name: str = Field(..., description="원본 물질명")
    mapped_id: Optional[str] = Field(None, description="매핑된 표준 물질 ID")
    mapped_name: Optional[str] = Field(None, description="매핑된 표준 물질명")
    confidence: float = Field(0.0, description="매핑 신뢰도")
    status: str = Field("pending", description="매핑 상태")
    error_message: Optional[str] = Field(None, description="오류 메시지")


class SubstanceMappingResponse(BaseModel):
    """단일 물질 매핑 응답"""
    status: str = Field(..., description="응답 상태")
    data: SubstanceMappingResult = Field(..., description="매핑 결과")
    timestamp: str = Field(..., description="처리 시간 (ISO 문자열)")


class SubstanceMappingBatchResponse(BaseModel):
    """배치 물질 매핑 응답"""
    status: str = Field(..., description="응답 상태")
    data: List[SubstanceMappingResult] = Field(default_factory=list, description="매핑 결과 목록")
    total_count: int = Field(..., description="총 처리 개수")
    success_count: int = Field(0, description="성공 개수")
    error_count: int = Field(0, description="실패 개수")
    timestamp: str = Field(..., description="처리 시간 (ISO 문자열)")


class SubstanceMappingFileResponse(BaseModel):
    """파일 기반 물질 매핑 응답"""
    status: str = Field(..., description="응답 상태")
    data: List[SubstanceMappingResult] = Field(default_factory=list, description="매핑 결과 목록")
    original_filename: str = Field(..., description="원본 파일명")
    processed_count: int = Field(0, description="처리된 물질 개수")
    timestamp: str = Field(..., description="처리 시간 (ISO 문자열)")


class SubstanceMappingStatistics(BaseModel):
    """물질 매핑 통계"""
    total_mappings: int = Field(0, description="총 매핑 수")
    successful_mappings: int = Field(0, description="성공한 매핑 수")
    failed_mappings: int = Field(0, description="실패한 매핑 수")
    average_confidence: float = Field(0.0, description="평균 신뢰도")
    last_updated: datetime = Field(default_factory=datetime.now, description="마지막 업데이트 시간")
    service_status: str = Field("active", description="서비스 상태")


class SavedMapping(BaseModel):
    """저장된 매핑 데이터"""
    id: int = Field(..., description="매핑 ID")
    company_id: Optional[str] = Field(None, description="회사 ID")
    original_substance: str = Field(..., description="원본 물질명")
    mapped_substance_id: Optional[str] = Field(None, description="매핑된 물질 ID")
    mapped_substance_name: Optional[str] = Field(None, description="매핑된 물질명")
    confidence: float = Field(0.0, description="신뢰도")
    created_at: datetime = Field(..., description="생성 시간")
    updated_at: datetime = Field(..., description="수정 시간")


class OriginalData(BaseModel):
    """원본 데이터"""
    id: int = Field(..., description="데이터 ID")
    company_id: Optional[str] = Field(None, description="회사 ID")
    substance_name: str = Field(..., description="물질명")
    quantity: Optional[float] = Field(None, description="수량")
    unit: Optional[str] = Field(None, description="단위")
    created_at: datetime = Field(..., description="생성 시간")


class CorrectionData(BaseModel):
    """수정 데이터"""
    id: int = Field(..., description="수정 ID")
    certification_id: int = Field(..., description="인증서 ID")
    original_mapping: str = Field(..., description="원본 매핑")
    corrected_mapping: str = Field(..., description="수정된 매핑")
    corrected_by: Optional[str] = Field(None, description="수정자")
    correction_reason: Optional[str] = Field(None, description="수정 사유")
    created_at: datetime = Field(..., description="수정 시간")


class MappingCorrectionRequest(BaseModel):
    """매핑 수정 요청"""
    corrected_substance_id: str = Field(..., description="수정된 물질 ID")
    corrected_substance_name: str = Field(..., description="수정된 물질명")
    correction_reason: Optional[str] = Field(None, description="수정 사유")
    corrected_by: Optional[str] = Field(None, description="수정자")
