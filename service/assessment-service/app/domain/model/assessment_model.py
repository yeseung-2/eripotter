from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class KesgItem(BaseModel):
    id: int
    item_name: str
    question_text: Optional[str] = None
    question_type: Optional[str] = None
    choices: Optional[Any] = None  # levels_json 또는 choices_json (리스트 또는 딕셔너리)
    category: Optional[str] = None
    weight: Optional[int] = 1

class KesgResponse(BaseModel):
    items: List[KesgItem]
    total_count: int

class AssessmentRequest(BaseModel):
    company_id: str
    responses: List[Dict[str, Any]]

class AssessmentResponse(BaseModel):
    id: str
    company_id: str
    created_at: datetime
    status: str

class AssessmentSubmission(BaseModel):
    company_id: str
    question_id: int
    question_type: str
    level_no: Optional[int] = None
    choice_ids: Optional[List[int]] = None
    score: int
