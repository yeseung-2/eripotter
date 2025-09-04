from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union
from datetime import datetime

# ===== Base Entity Models (Pydantic Version) =====

class KesgEntity(BaseModel):
    """KESG 테이블 엔티티 - Railway PostgreSQL 구조와 동일"""
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
    levels_json: Optional[List[Dict[str, Union[str, int]]]] = None
    choices_json: Optional[List[Dict[str, Union[str, int]]]] = None
    scoring_json: Optional[Dict[str, Union[str, int, float, bool]]] = None
    weight: Optional[float] = None


class AssessmentEntity(BaseModel):
    """Assessment 테이블 엔티티"""
    id: int
    company_name: str
    question_id: int
    question_type: str
    level_no: Optional[int] = None
    choice_ids: Optional[List[int]] = None
    score: int
    timestamp: Optional[datetime] = None


class SolutionEntity(BaseModel):
    """Solution 테이블 엔티티"""
    id: int
    company_name: str
    question_id: int
    sol: str
    timestamp: Optional[datetime] = None


class CompanyEntity(BaseModel):
    """Company 테이블 엔티티 - 회사 및 Tier 1 협력사 정보"""
    id: int
    company_name: str
    tier1: Optional[str] = None


# ===== Supply Chain Models =====

class CompanyRelation(BaseModel):
    """회사 관계 모델 - company_name과 tier1 리스트만 포함하는 단순 관계"""
    company_name: str
    tier1s: List[str] = Field(default_factory=list, description="Tier 1 협력사 리스트")


class SupplyChainNode(BaseModel):
    """공급망 노드 모델 - 재귀적 구조로 공급망 트리 표현"""
    company_name: str
    tier1s: List[str] = Field(default_factory=list, description="Tier 1 협력사 리스트")
    children: List['SupplyChainNode'] = Field(default_factory=list, description="하위 공급망 노드들")


# 재귀적 참조를 위한 forward reference 해결
SupplyChainNode.model_rebuild()


# ===== Vulnerability Models =====

class VulnerableSection(BaseModel):
    """취약부문 모델 - Assessment + Kesg 조인 결과 (score=0 대상)"""
    # Assessment 정보
    id: int
    company_name: str
    question_id: int
    question_type: str
    level_no: Optional[int] = None
    choice_ids: Optional[List[int]] = None
    score: int
    timestamp: Optional[datetime] = None
    
    # Kesg 정보
    item_name: Optional[str] = None
    item_desc: Optional[str] = None
    classification: Optional[str] = None
    domain: Optional[str] = None
    category: Optional[str] = None
    levels_json: Optional[List[Dict[str, Union[str, int]]]] = None
    choices_json: Optional[List[Dict[str, Union[str, int]]]] = None
    weight: Optional[float] = None


class CompanyVulnerabilityResponse(BaseModel):
    """특정 회사의 취약부문 리스트 응답"""
    status: str = "success"
    company_name: str
    vulnerable_sections: List[VulnerableSection] = Field(default_factory=list)
    total_count: int = 0
    message: Optional[str] = None


class SupplyChainVulnerabilityNode(BaseModel):
    """공급망 내 특정 회사의 취약부문 정보"""
    company_name: str
    tier1s: List[str] = Field(default_factory=list)
    vulnerable_sections: List[VulnerableSection] = Field(default_factory=list)
    vulnerability_count: int = 0
    children: List['SupplyChainVulnerabilityNode'] = Field(default_factory=list)


# 재귀적 참조를 위한 forward reference 해결
SupplyChainVulnerabilityNode.model_rebuild()


class SupplyChainVulnerabilityResponse(BaseModel):
    """공급망 전체 취약부문 응답 - 루트 회사 + 모든 하위 협력사들의 취약부문"""
    status: str = "success"
    root_company: str
    supply_chain_tree: SupplyChainVulnerabilityNode
    total_companies: int = 0
    total_vulnerabilities: int = 0
    message: Optional[str] = None


# ===== Assessment Result Models =====

class AssessmentResult(BaseModel):
    """Assessment 결과 모델 - Assessment + Kesg 조인 결과"""
    # Assessment 정보
    id: int
    company_name: str
    question_id: int
    question_type: str
    level_no: Optional[int] = None
    choice_ids: Optional[List[int]] = None
    score: int
    timestamp: Optional[datetime] = None
    
    # Kesg 정보
    item_name: Optional[str] = None
    item_desc: Optional[str] = None
    classification: Optional[str] = None
    domain: Optional[str] = None
    category: Optional[str] = None
    levels_json: Optional[List[Dict[str, Union[str, int]]]] = None
    choices_json: Optional[List[Dict[str, Union[str, int]]]] = None
    weight: Optional[float] = None


class CompanyAssessmentResponse(BaseModel):
    """특정 회사의 Assessment 결과 응답"""
    status: str = "success"
    company_name: str
    assessment_results: List[AssessmentResult] = Field(default_factory=list)
    total_count: int = 0
    total_score: float = 0.0
    max_possible_score: float = 0.0
    achievement_rate: float = 0.0
    message: Optional[str] = None


# ===== Solution Models =====

class SolutionWithDetails(BaseModel):
    """솔루션 상세 모델 - Solution + Kesg 조인 결과"""
    # Solution 정보
    id: int
    company_name: str
    question_id: int
    sol: str
    timestamp: Optional[datetime] = None
    
    # Kesg 정보
    item_name: Optional[str] = None
    item_desc: Optional[str] = None
    classification: Optional[str] = None
    domain: Optional[str] = None
    category: Optional[str] = None


class CompanySolutionResponse(BaseModel):
    """특정 회사의 솔루션 리스트 응답"""
    status: str = "success"
    company_name: str
    solutions: List[SolutionWithDetails] = Field(default_factory=list)
    total_count: int = 0
    message: Optional[str] = None


# ===== Supply Chain Assessment Models =====

class SupplyChainAssessmentNode(BaseModel):
    """공급망 내 특정 회사의 Assessment 정보"""
    company_name: str
    tier1s: List[str] = Field(default_factory=list)
    assessment_results: List[AssessmentResult] = Field(default_factory=list)
    total_score: float = 0.0
    max_possible_score: float = 0.0
    achievement_rate: float = 0.0
    children: List['SupplyChainAssessmentNode'] = Field(default_factory=list)


# 재귀적 참조를 위한 forward reference 해결
SupplyChainAssessmentNode.model_rebuild()


class SupplyChainAssessmentResponse(BaseModel):
    """공급망 전체 Assessment 결과 응답"""
    status: str = "success"
    root_company: str
    supply_chain_tree: SupplyChainAssessmentNode
    total_companies: int = 0
    average_achievement_rate: float = 0.0
    message: Optional[str] = None


# ===== Company Management Models =====

class CompanyListResponse(BaseModel):
    """회사 목록 응답"""
    status: str = "success"
    companies: List[CompanyEntity] = Field(default_factory=list)
    total_count: int = 0
    message: Optional[str] = None


# ===== Assessment Company Models =====

class AssessmentCompanySummary(BaseModel):
    """Assessment 테이블의 기업별 요약 정보"""
    company_name: str
    total_questions: int = 0
    total_score: int = 0
    max_possible_score: int = 0
    achievement_rate: float = 0.0
    last_assessment_date: Optional[datetime] = None
    vulnerable_count: int = 0  # score가 0 또는 25인 문항 수


class AssessmentCompanyListResponse(BaseModel):
    """Assessment 테이블의 모든 기업 목록 응답"""
    status: str = "success"
    companies: List[AssessmentCompanySummary] = Field(default_factory=list)
    total_count: int = 0
    average_achievement_rate: float = 0.0
    message: Optional[str] = None


class CompanyAssessmentDashboard(BaseModel):
    """기업별 Assessment 대시보드 데이터"""
    company_name: str
    assessment_summary: AssessmentCompanySummary
    assessment_results: List[AssessmentResult] = Field(default_factory=list)
    vulnerable_sections: List[VulnerableSection] = Field(default_factory=list)
    domain_summary: Dict[str, Dict[str, Union[int, float]]] = Field(default_factory=dict)  # 도메인별 요약


class CompanyAssessmentDashboardResponse(BaseModel):
    """기업별 Assessment 대시보드 응답"""
    status: str = "success"
    dashboard: CompanyAssessmentDashboard
    message: Optional[str] = None


# ===== Error Response Models =====

class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    status: str = "error"
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Union[str, int, float, bool, List[str], Dict[str, Union[str, int, float, bool]]]]] = None
