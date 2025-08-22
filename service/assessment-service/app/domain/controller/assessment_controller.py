import logging
from typing import List, Dict, Any
from ..service.assessment_service import AssessmentService
from ..model.assessment_model import KesgResponse, KesgItem

logger = logging.getLogger("assessment-controller")

class AssessmentController:
    def __init__(self, service: AssessmentService):
        self.service = service
    
    def get_kesg_items(self) -> KesgResponse:
        """kesg 테이블의 모든 항목 조회"""
        try:
            logger.info("📝 kesg 항목 조회 컨트롤러 요청")
            return self.service.get_kesg_items()
        except Exception as e:
            logger.error(f"❌ kesg 항목 조회 컨트롤러 오류: {e}")
            raise
    
    def get_kesg_item_by_id(self, item_id: int) -> KesgItem:
        """특정 ID의 kesg 항목 조회"""
        try:
            logger.info(f"📝 kesg 항목 조회 컨트롤러 요청: ID {item_id}")
            return self.service.get_kesg_item_by_id(item_id)
        except Exception as e:
            logger.error(f"❌ kesg 항목 조회 컨트롤러 오류: {e}")
            raise
    
    # 기존 메서드들 (더미 구현)
    def get_all_assessments(self):
        return self.service.get_all_assessments()
    
    def get_assessment_by_id(self, assessment_id: str):
        return self.service.get_assessment_by_id(assessment_id)
    
    def create_assessment(self, assessment_data: dict):
        return self.service.create_assessment(assessment_data)
    
    def update_assessment(self, assessment_id: str, assessment_data: dict):
        return self.service.update_assessment(assessment_id, assessment_data)
    
    def delete_assessment(self, assessment_id: str):
        return self.service.delete_assessment(assessment_id)
    
    def get_metrics(self):
        return self.service.get_metrics()
