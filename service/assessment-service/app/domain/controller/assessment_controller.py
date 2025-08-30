import logging
from typing import List, Dict, Union
from ..service.assessment_service import AssessmentService
from ..model.assessment_model import AssessmentRequest, AssessmentSubmissionResponse

logger = logging.getLogger("assessment-controller")

class AssessmentController:
    def __init__(self, service: AssessmentService):
        self.service = service
    
    def get_kesg_items(self) -> List[Dict[str, Union[str, int, List[int], None]]]:
        """kesg 테이블의 모든 항목 조회"""
        try:
            logger.info("📝 kesg 항목 조회 컨트롤러 요청")
            return self.service.get_kesg_items()
        except Exception as e:
            logger.error(f"❌ kesg 항목 조회 컨트롤러 오류: {e}")
            raise
    
    def get_kesg_item_by_id(self, item_id: int) -> Dict[str, Union[str, int, List[int], None]]:
        """특정 ID의 kesg 항목 조회"""
        try:
            logger.info(f"📝 kesg 항목 조회 컨트롤러 요청: ID {item_id}")
            return self.service.get_kesg_item_by_id(item_id)
        except Exception as e:
            logger.error(f"❌ kesg 항목 조회 컨트롤러 오류: {e}")
            raise
    
    def submit_assessment(self, request: AssessmentRequest) -> List[AssessmentSubmissionResponse]:
        """자가진단 응답 제출"""
        try:
            logger.info(f"📝 자가진단 응답 제출 컨트롤러 요청: company_name={request.company_name}")
            return self.service.submit_assessment(request.company_name, request.responses)
        except Exception as e:
            logger.error(f"❌ 자가진단 응답 제출 컨트롤러 오류: {e}")
            raise
    
    def get_company_results(self, company_name: str) -> List[Dict[str, Union[str, int, List[int], None]]]:
        """특정 회사의 자가진단 결과 조회"""
        try:
            logger.info(f"📝 회사별 결과 조회 컨트롤러 요청: company_name={company_name}")
            return self.service.get_company_results(company_name)
        except Exception as e:
            logger.error(f"❌ 회사별 결과 조회 컨트롤러 오류: {e}")
            raise
    
    def get_assessment_results(self, company_name: str) -> List[Dict[str, Union[str, int, List[int], None]]]:
        """특정 회사의 자가진단 결과 조회 (상세 정보 포함)"""
        try:
            logger.info(f"📝 자가진단 결과 조회 컨트롤러 요청: company_name={company_name}")
            return self.service.get_assessment_results(company_name)
        except Exception as e:
            logger.error(f"❌ 자가진단 결과 조회 컨트롤러 오류: {e}")
            raise
    
    def get_vulnerable_sections(self, company_name: str) -> List[Dict[str, Union[str, int, List[int], None]]]:
        """특정 회사의 취약 부문 조회 (score가 0인 문항)"""
        try:
            logger.info(f"📝 취약 부문 조회 컨트롤러 요청: company_name={company_name}")
            return self.service.get_vulnerable_sections(company_name)
        except Exception as e:
            logger.error(f"❌ 취약 부문 조회 컨트롤러 오류: {e}")
            raise
