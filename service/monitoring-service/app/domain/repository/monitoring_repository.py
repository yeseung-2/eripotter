from pydantic import BaseModel
from typing import List, Optional, Dict, Union
from datetime import datetime

# ===== Pydantic Base Models =====

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

    def to_dict(self) -> Dict[str, Union[str, int, float, List[Dict[str, Union[str, int]]], Dict[str, Union[str, int, float, bool]], None]]:
        """엔티티를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'classification': self.classification,
            'domain': self.domain,
            'category': self.category,
            'item_name': self.item_name,
            'item_desc': self.item_desc,
            'metric_desc': self.metric_desc,
            'data_source': self.data_source,
            'data_period': self.data_period,
            'data_method': self.data_method,
            'data_detail': self.data_detail,
            'question_type': self.question_type,
            'levels_json': self.levels_json,
            'choices_json': self.choices_json,
            'scoring_json': self.scoring_json,
            'weight': self.weight
        }


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

    def to_dict(self) -> Dict[str, Union[str, int, datetime, List[int], None]]:
        """엔티티를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'company_name': self.company_name,
            'question_id': self.question_id,
            'question_type': self.question_type,
            'level_no': self.level_no,
            'choice_ids': self.choice_ids,
            'score': self.score,
            'timestamp': self.timestamp
        }


class SolutionEntity(BaseModel):
    """Solution 테이블 엔티티"""
    id: int
    company_name: str
    question_id: int
    sol: str
    timestamp: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Union[str, int, datetime, None]]:
        """엔티티를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'company_name': self.company_name,
            'question_id': self.question_id,
            'sol': self.sol,
            'timestamp': self.timestamp
        }


class CompanyEntity(BaseModel):
    """Company 테이블 엔티티 - 회사 및 Tier 1 협력사 정보"""
    id: int
    company_name: str
    tier1: Optional[str] = None

    def to_dict(self) -> Dict[str, Union[str, int, None]]:
        """엔티티를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'company_name': self.company_name,
            'tier1': self.tier1
        }


# ===== Repository Class =====

class MonitoringRepository:
    def __init__(self):
        pass




#### 테스트용 Mock!!!!!

class MonitoringRepository:
    def __init__(self):
        # === Mock Company Data (공급망 샘플) ===
        self._companies = [
            {"id": 1, "company_name": "LG에너지솔루션", "tier1": "에코프로비엠"},
            {"id": 2, "company_name": "에코프로비엠", "tier1": "포스코퓨처엠"},
            {"id": 3, "company_name": "포스코퓨처엠", "tier1": "포스코인터내셔널"},
        ]

        # === Mock Vulnerability Data (score=0 사례) ===
        self._vulnerabilities = {
            "에코프로비엠": [
                {
                    "id": 101,
                    "company_name": "에코프로비엠",
                    "question_id": 1,
                    "question_type": "five_level",
                    "level_no": 1,
                    "choice_ids": None,
                    "score": 0,
                    "timestamp": datetime.now(),
                    "item_name": "환경정책 수립",
                    "item_desc": "환경정책 및 정량적 목표가 수립되지 않음",
                    "classification": "E-1-3",
                    "domain": "환경",
                    "category": "환경경영",
                    "levels_json": None,
                    "choices_json": None,
                    "weight": 1.0
                }
            ],
            "포스코인터내셔널": [
                {
                    "id": 201,
                    "company_name": "포스코인터내셔널",
                    "question_id": 2,
                    "question_type": "five_choice",
                    "level_no": None,
                    "choice_ids": [1],
                    "score": 0,
                    "timestamp": datetime.now(),
                    "item_name": "윤리경영 체계",
                    "item_desc": "비윤리 행위 방지 체계 구축 여부",
                    "classification": "G-1-1",
                    "domain": "지배구조",
                    "category": "윤리경영",
                    "levels_json": None,
                    "choices_json": [{"id": 1, "text": "ISO37001 인증"}],
                    "weight": 1.0
                }
            ]
        }

    # === Mock Methods ===
    def get_all_companies(self):
        return self._companies

    def get_tier1_companies(self, company_name: str):
        return [c["tier1"] for c in self._companies if c["company_name"] == company_name]

    def get_company_vulnerable_sections(self, company_name: str):
        return self._vulnerabilities.get(company_name, [])

    def get_company_assessment_results(self, company_name: str):
        # Vulnerability mock을 그대로 assessment 결과로도 리턴
        return self._vulnerabilities.get(company_name, [])

    def get_company_solutions(self, company_name: str):
        # 솔루션은 테스트용으로 빈 리스트
        return []
