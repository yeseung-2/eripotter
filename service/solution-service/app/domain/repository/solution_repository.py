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
Solution Repository - Assessment Service 연동
실제 assessment 데이터를 기반으로 취약 부문 조회
"""

import requests
import os
import logging
from typing import List, Dict, Union, Optional
from datetime import datetime

logger = logging.getLogger("solution-service")

class SolutionRepository:
    def __init__(self):
        # Gateway URL (환경변수로 주입)
        # 예) https://gateway-production-5d19.up.railway.app
        self.gateway_url = os.getenv("GATEWAY_URL", "http://localhost:8080")
    
    # === Repository 메서드 ===
    def get_vulnerable_sections(self, company_name: str) -> List[Dict[str, Union[str, int, None]]]:
        """assessment에서 score=0 또는 score=25인 항목 + kesg 데이터 join"""
        try:
            # 1. Assessment Service에서 실제 assessment 데이터 조회
            assessment_results = self._get_assessment_results_from_service(company_name)
            
            # 2. score=0 또는 score=25인 항목 필터링 (취약 부문)
            vulnerable = [a for a in assessment_results if a.get("score", 1) == 0 or a.get("score", 1) == 25]
            
            logger.info(f"📝 취약 부문 조회: {len(vulnerable)}개 score=0 또는 score=25 항목 발견")
            
            # 3. KESG 데이터 조회
            kesg_data = self._get_kesg_data_from_service()
            
            # 4. KESG 데이터와 조인
            kesg_map = {k["id"]: k for k in kesg_data}
            results = []
            
            for v in vulnerable:
                # score=0 또는 score=25 조건을 한번 더 확인
                if v.get("score", 1) not in [0, 25]:
                    logger.warning(f"⚠️ score가 0 또는 25가 아닌 항목 발견: {v}")
                    continue
                    
                kesg_item = kesg_map.get(v["question_id"])
                if kesg_item:
                    results.append({**v, **{
                        "item_name": kesg_item["item_name"],
                        "item_desc": kesg_item["item_desc"],
                        "classification": kesg_item["classification"],
                        "domain": kesg_item["domain"]
                    }})
                else:
                    logger.warning(f"⚠️ KESG 데이터를 찾을 수 없음: question_id={v['question_id']}")
            
            logger.info(f"✅ 취약 부문 조회 완료: {len(results)}개 항목")
            return results
            
        except Exception as e:
            logger.error(f"❌ 취약 부문 조회 실패: {e}")
            # Mock fallback 금지: 상위로 예외 전달
            raise
    
    def _get_assessment_results_from_service(self, company_name: str) -> List[Dict[str, Union[str, int, None]]]:
        """Gateway를 통해 Assessment 결과 조회"""
        try:
            url = f"{self.gateway_url}/api/assessment/assessment-results/{company_name}"
            logger.info(f"📡 Gateway 경유 Assessment 호출: {url}")
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            assessment_results = data.get("assessment_results", [])
            
            logger.info(f"✅ Assessment Service 응답: {len(assessment_results)}개 결과")
            return assessment_results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Assessment Service 호출 실패: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Assessment Service 응답 파싱 실패: {e}")
            raise
    
    def _get_kesg_data_from_service(self) -> List[Dict[str, Union[str, int, None]]]:
        """Gateway를 통해 KESG 데이터 조회"""
        try:
            url = f"{self.gateway_url}/api/assessment/kesg"
            logger.info(f"📡 Gateway 경유 KESG 호출: {url}")
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            kesg_items = data.get("items", [])
            
            logger.info(f"✅ KESG Service 응답: {len(kesg_items)}개 항목")
            return kesg_items
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ KESG Service 호출 실패: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ KESG Service 응답 파싱 실패: {e}")
            raise

    def save_solution(self, company_name: str, question_id: int, sol: str) -> Dict[str, Union[str, int, datetime]]:
        """새로운 솔루션 저장 (임시 메모리 저장 - 실제로는 DB 연동 필요)"""
        # 임시 ID 생성 (실제로는 DB에서 auto increment)
        import time
        new_id = int(time.time() * 1000)  # timestamp 기반 ID
        
        new_solution = {
            "id": new_id,
            "company_name": company_name,
            "question_id": question_id,
            "sol": sol,
            "timestamp": datetime.now()
        }
        
        logger.info(f"💾 솔루션 저장: id={new_id}, company={company_name}, question_id={question_id}")
        return new_solution

    def get_solutions(self, company_name: str) -> List[Dict[str, Union[str, int, datetime]]]:
        """특정 회사의 솔루션 목록 반환 (임시 빈 배열 반환 - 실제로는 DB 연동 필요)"""
        logger.info(f"📝 솔루션 목록 조회: company={company_name}")
        # 실제로는 DB에서 조회해야 함
        return []


