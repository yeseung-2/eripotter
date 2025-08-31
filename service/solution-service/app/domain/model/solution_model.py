from pydantic import BaseModel
from typing import List, Optional, Dict, Union
from datetime import datetime

class AssessmentEntity(BaseModel):
    """Assessment 테이블 엔티티 - Repository의 AssessmentEntity와 동일"""
    id: int
    company_name: str
    question_id: int
    question_type: str
    level_no: Optional[int] = None
    choice_ids: Optional[List[int]] = None
    score: int
    timestamp: Optional[datetime] = None

class KesgItem(BaseModel):
    """KESG 항목 1개 - Repository의 KesgEntity 구조와 동일"""
    id: int
    classification: Optional[str] = None
    domain: Optional[str] = None
    category: Optional[str] = None
    item_name: Optional[str] = None
    item_desc: Optional[str] = None
    metric_desc: Optional[str] = None
    data_source: Optional[str] = None
    data_period: Optional[str] = None
    data_method: Optional[str] = None
    data_detail: Optional[str] = None
    question_type: Optional[str] = None
    levels_json: Optional[List[Dict]] = None
    choices_json: Optional[List[Dict]] = None
    scoring_json: Optional[Dict[str, object]] = None
    weight: Optional[float] = None

class KesgResponse(BaseModel):
    """KESG 항목 리스트 응답"""
    items: List[KesgItem]
    total_count: int

class SolutionSubmissionRequest(BaseModel):
    """사용자가 제출하는 솔루션 요청 데이터"""
    question_id: int
    sol: str

class SolutionSubmissionResponse(BaseModel):
    """DB에 저장된 솔루션을 나타내는 응답 데이터"""
    id: int
    company_name: str
    question_id: int
    sol: str
    timestamp: Optional[datetime] = None
    item_name: Optional[str] = None
    item_desc: Optional[str] = None
    classification: Optional[str] = None
    domain: Optional[str] = None

class SolutionRequest(BaseModel):
    """솔루션 제출 요청"""
    company_name: str
    solutions: List[SolutionSubmissionRequest]

class SolutionResponse(BaseModel):
    """솔루션 제출 결과"""
    id: str
    company_name: str
    created_at: datetime
    status: str

class SolutionListResponse(BaseModel):
    """특정 회사의 솔루션 목록 응답"""
    status: str
    company_name: str
    solutions: List[SolutionSubmissionResponse]
    total_count: int

# === Assessment 관련 파생 모델 ===

class VulnerableSection(BaseModel):
    """취약 부문 정보 - Assessment + KESG 조인 결과"""
    id: int
    company_name: str
    question_id: int
    question_type: str
    level_no: Optional[int] = None
    choice_ids: Optional[List[int]] = None
    score: int
    timestamp: Optional[datetime] = None
    # KESG 정보
    item_name: Optional[str] = None
    item_desc: Optional[str] = None
    classification: Optional[str] = None
    domain: Optional[str] = None

class AssessmentResult(BaseModel):
    """Assessment 결과 - score 포함"""
    id: int
    company_name: str
    question_id: int
    question_type: str
    level_no: Optional[int] = None
    choice_ids: Optional[List[int]] = None
    score: int
    timestamp: Optional[datetime] = None
    # KESG 정보
    item_name: Optional[str] = None
    item_desc: Optional[str] = None
    classification: Optional[str] = None
    domain: Optional[str] = None
    levels_json: Optional[List[Dict[str, Union[str, int]]]] = None
    choices_json: Optional[List[Dict[str, Union[str, int]]]] = None

class AssessmentResultsResponse(BaseModel):
    """Assessment 결과 목록 응답"""
    status: str
    company_name: str
    assessment_results: List[AssessmentResult]
    total_count: int

class VulnerableSectionsResponse(BaseModel):
    """취약 부문 목록 응답"""
    status: str
    company_name: str
    vulnerable_sections: List[VulnerableSection]
    total_count: int
