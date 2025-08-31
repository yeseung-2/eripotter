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


"""
Solution Repository - Mock Repository Layer
DB 연결 없이 임시 데이터 반환
"""

from typing import List, Dict, Union, Optional
from datetime import datetime

class SolutionRepository:
    # 샘플 DB 역할을 하는 in-memory 스토리지
    _kesg = [
        {
            "id": 1,
            "classification": "E-3-2",
            "domain": "환경",
            "category": "에너지 및 온실가스",
            "item_name": "에너지 사용량",
            "item_desc": "조직 내 에너지 사용 총량 절감 여부",
            "metric_desc": "원단위 기반 에너지 사용량 관리",
            "data_source": "에너지 관리 시스템",
            "data_period": "직전 회계연도",
            "data_method": "실측/집계",
            "data_detail": "전력, 가스, 연료 등",
            "question_type": "five_level",
            "levels_json": None,
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
            "data_source": "윤리경영 보고서",
            "data_period": "직전 회계연도",
            "data_method": "자체 보고",
            "data_detail": "ISO37001 포함",
            "question_type": "five_choice",
            "levels_json": None,
            "choices_json": None,
            "scoring_json": {"1": 0, "2": 25, "3": 50, "4": 75, "5": 100},
            "weight": 1.0
        }
    ]

    _assessments = [
        {
            "id": 101,
            "company_name": "테스트회사",
            "question_id": 1,
            "question_type": "five_level",
            "level_no": 1,
            "choice_ids": None,
            "score": 0,
            "timestamp": datetime.now()
        },
        {
            "id": 102,
            "company_name": "테스트회사",
            "question_id": 2,
            "question_type": "five_choice",
            "level_no": None,
            "choice_ids": [1],
            "score": 0,
            "timestamp": datetime.now()
        }
    ]

    _solutions: List[Dict[str, Union[str, int, datetime]]] = [
        {
            "id": 201,
            "company_name": "테스트회사",
            "question_id": 2,
            "sol": "<p>활동: 윤리경영 헌장 제정</p><p>방법: 행동강령 수립 및 교육</p><p>목표: 윤리경영 체계 정착</p>",
            "timestamp": datetime.now()
        }
    ]

    # === Repository 메서드 ===
    def get_vulnerable_sections(self, company_name: str) -> List[Dict[str, Union[str, int, None]]]:
        """assessment에서 score=0인 항목 + kesg 데이터 join"""
        # 반드시 score == 0인 항목만 필터링
        vulnerable = [a for a in self._assessments if a["company_name"] == company_name and a["score"] == 0]
        kesg_map = {k["id"]: k for k in self._kesg}

        results = []
        for v in vulnerable:
            # score == 0 조건을 한번 더 확인
            if v["score"] != 0:
                continue
                
            kesg_item = kesg_map.get(v["question_id"])
            if kesg_item:
                results.append({**v, **{
                    "item_name": kesg_item["item_name"],
                    "item_desc": kesg_item["item_desc"],
                    "classification": kesg_item["classification"],
                    "domain": kesg_item["domain"]
                }})
        return results

    def save_solution(self, company_name: str, question_id: int, sol: str) -> Dict[str, Union[str, int, datetime]]:
        """새로운 솔루션 저장"""
        new_id = len(self._solutions) + 1 + 200
        new_solution = {
            "id": new_id,
            "company_name": company_name,
            "question_id": question_id,
            "sol": sol,
            "timestamp": datetime.now()
        }
        self._solutions.append(new_solution)
        return new_solution

    def get_solutions(self, company_name: str) -> List[Dict[str, Union[str, int, datetime]]]:
        """특정 회사의 솔루션 목록 반환"""
        return [s for s in self._solutions if s["company_name"] == company_name]


