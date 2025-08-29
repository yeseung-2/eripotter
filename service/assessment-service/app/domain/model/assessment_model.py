from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

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

class AssessmentSubmissionRequest(BaseModel):
    """사용자가 제출하는 요청 데이터 - score는 백엔드에서 계산"""
    question_id: int
    question_type: str
    level_no: Optional[int] = None
    choice_ids: Optional[List[int]] = None

class AssessmentSubmissionResponse(BaseModel):
    """DB에 저장된 응답을 나타내는 응답 데이터"""
    id: int
    company_name: str
    question_id: int
    question_type: str
    level_no: Optional[int] = None
    choice_ids: Optional[List[int]] = None
    score: int
    timestamp: Optional[datetime] = None

class AssessmentRequest(BaseModel):
    """자가진단 응답 제출 요청"""
    company_name: str
    responses: List[AssessmentSubmissionRequest]

class AssessmentResponse(BaseModel):
    """자가진단 응답 제출 결과"""
    id: str
    company_name: str
    created_at: datetime
    status: str


