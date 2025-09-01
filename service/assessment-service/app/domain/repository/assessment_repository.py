"""
Assessment Repository - Mock Repository Layer
DB 연결 없이 임시 데이터 반환
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Union
from datetime import datetime

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
    scoring_json: Optional[Dict[str, int]] = None
    weight: Optional[float] = None

    def to_dict(self) -> Dict[str, Union[str, int, float, List[Dict[str, Union[str, int]]], Dict[str, int], None]]:
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

    def to_dict(self) -> Dict[str, Union[str, int, List[int], datetime, None]]:
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


# Mock Repository 클래스
class AssessmentRepository:
    # 클래스 변수로 변경하여 인스턴스 간에도 데이터 유지
    _storage: List[Dict[str, Union[str, int, List[int], None]]] = []
    
    def __init__(self):
        # 인스턴스 변수는 제거하고 클래스 변수 사용
        pass

    def get_kesg_items(self) -> List[Dict[str, Union[str, int, float, List[Dict[str, Union[str, int]]], Dict[str, int], None]]]:
        """하드코딩된 kesg 문항 리스트"""
        return [
            {
                "id": 1,
                "classification": "E-1-3",
                "domain": "환경",
                "category": "환경경영 체계",
                "item_name": "환경정책 수립",
                "item_desc": "조직의 고유한 제품, 생산 및 서비스 활동에 의해 필연적으로 발생되는 부정적인 환경영향을 최소화하기 위한 정책",
                "metric_desc": "환경경영을 위한 조직의 중장기 환경정책에 따른 실천적 목표와 세부적인 계획",
                "data_source": "환경경영시스템, 중장기 환경정책, 연간 환경정책 관련 계획 및 보고서",
                "data_period": "직전 회계연도 기준",
                "data_method": "N/A",
                "data_detail": "N/A",
                "question_type": "five_level",
                "levels_json": [
                    {
                        "level_no": 1,
                        "label": "1단계",
                        "desc": "환경경영을 추진하기 위한 연간 환경정책, 정량적 환경목표가 수립되어 있지 않음",
                        "score": 0
                    },
                    {
                        "level_no": 2,
                        "label": "2단계",
                        "desc": "연간 환경정책, 정량적 환경목표 및 환경경영계획은 수립되어 있으나 방침 및 목표, 계획에 대한 관련 근거가 없이 형식적으로 수립되어 있음",
                        "score": 25
                    },
                    {
                        "level_no": 3,
                        "label": "3단계",
                        "desc": "연간 환경정책, 정량적 환경목표 및 추진계획은 조직의 외부 및 내부 이슈를 고려하여 체계적으로 수립되어 있으며 모니터링, 측정, 분석 및 평가하고 있음",
                        "score": 50
                    },
                    {
                        "level_no": 4,
                        "label": "4단계",
                        "desc": "예산을 반영한 중장기 환경정책, 정량적 환경목표 및 추진계획이 체계적으로 수립되어 있으며 정기적으로 모니터링, 측정, 분석 및 평가하여 피드백을 통한 환경성과 및 개선활동 실적을 보유하고 있음",
                        "score": 75
                    },
                    {
                        "level_no": 5,
                        "label": "5단계",
                        "desc": "4단계 + 조직의 영향력과 통제력 범위에 있는 사업장(자회사, 종속법인, 연결실체)까지를 포함",
                        "score": 100
                    }
                ],
                "choices_json": None,
                "scoring_json": None,
                "weight": 1.0
            },
            {
                "id": 2,
                "classification": "G-1-1",
                "domain": "지배구조",
                "category": "윤리경영",
                "item_name": "윤리경영 체계",
                "item_desc": "비윤리 행위 방지 체계 구축 여부",
                "metric_desc": "윤리경영 방침 및 내부 통제 시스템",
                "data_source": "내부 규정, 윤리경영 보고서",
                "data_period": "직전 회계연도 기준",
                "data_method": "N/A",
                "data_detail": "N/A",
                "question_type": "five_choice",
                "levels_json": None,
                "choices_json": [
                    {"id": 1, "text": "ISO37001(부패방지경영시스템) 인증을 받은 경우"},
                    {"id": 2, "text": "비윤리 행위에 대한 내부신고 및 모니터링 체계를 갖추고 있는 경우"},
                    {"id": 3, "text": "비윤리 행위 예방을 위한 교육 및 훈련이 이루어지고 있는 경우"},
                    {"id": 4, "text": "비윤리 행위 발생 시 징계 등 조치 및 개선을 위한 프로세스를 갖추고 있는 경우"},
                    {"id": 5, "text": "비윤리 행위 발생 및 사후조치에 관한 정보공개 체계를 갖추고 있는 경우"}
                ],
                "scoring_json": 
                    {
                    "1": 0,
                    "2": 25,
                    "3": 50,
                    "4": 75,
                    "5": 100
                    },
                "weight": 1.0
            }
        ]

    def get_kesg_item_by_id(self, item_id: int) -> Optional[Dict[str, Union[str, int, float, List[Dict[str, Union[str, int]]], Dict[str, int], None]]]:
        return next((i for i in self.get_kesg_items() if i["id"] == item_id), None)

    def get_kesg_scoring_data(self, question_ids: List[int]) -> Dict[int, Dict[str, Union[str, int, float, List[Dict[str, Union[str, int]]], Dict[str, int], None]]]:
        return {item["id"]: item for item in self.get_kesg_items() if item["id"] in question_ids}

    def save_assessment_responses(self, submissions: List[Dict[str, Union[str, int, List[int], None]]]) -> bool:
        print(f"🔍 Mock Repository: 저장할 데이터: {submissions}")
        self._storage.extend(submissions)
        print(f"🔍 Mock Repository: 현재 저장된 데이터: {self._storage}")
        return True

    def get_company_results(self, company_name: str) -> List[Dict[str, Union[str, int, List[int], None]]]:
        print(f"🔍 Mock Repository: 조회 요청 company_name: '{company_name}'")
        print(f"🔍 Mock Repository: 저장된 모든 데이터: {self._storage}")
        results = [s for s in self._storage if s["company_name"] == company_name]
        print(f"🔍 Mock Repository: 조회 결과: {results}")
        return results
