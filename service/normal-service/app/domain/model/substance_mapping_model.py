from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class SubstanceMappingResult(BaseModel):
    """물질매핑 결과 모델"""
    substance_name: str
    mapped_sid: Optional[str] = None
    mapped_name: Optional[str] = None
    top1_score: float = 0.0
    margin: float = 0.0
    confidence: float = 0.0
    band: str = "not_mapped"  # 'mapped', 'needs_review', 'not_mapped'
    top5_candidates: List[Dict[str, Any]] = []
    status: str = "success"
    error: Optional[str] = None
    saved_id: Optional[str] = None

class SubstanceMappingRequest(BaseModel):
    """물질매핑 요청 모델"""
    substance_name: str
    company_id: Optional[str] = None
    company_name: Optional[str] = None

class SubstanceMappingBatchRequest(BaseModel):
    """배치물질 매핑 요청 모델"""
    substance_names: List[str]
    company_id: Optional[str] = None
    company_name: Optional[str] = None

class SubstanceMappingResponse(BaseModel):
    """물질매핑 응답 모델"""
    status: str
    data: SubstanceMappingResult
    timestamp: str

class SubstanceMappingBatchResponse(BaseModel):
    """배치 물질 매핑 응답 모델"""
    status: str
    data: List[SubstanceMappingResult]
    total_count: int
    timestamp: str

class SubstanceMappingFileResponse(BaseModel):
    """파일 매핑 응답 모델"""
    status: str
    data: Dict[str, Any]
    original_filename: str
    timestamp: str

class SubstanceMappingStatistics(BaseModel):
    """매핑 통계 모델"""
    model_loaded: bool
    regulation_data_count: int
    faiss_index_built: bool
    service_status: str