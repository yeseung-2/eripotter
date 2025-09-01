"""
Solution Controller - Controller Layer
API 엔드포인트 요청 처리 및 Service Layer 호출 담당
"""

import logging
from typing import List
from ..service.solution_service import SolutionService
from ..model.solution_model import SolutionSubmissionResponse

logger = logging.getLogger("solution-service")

class SolutionController:
    def __init__(self, service: SolutionService):
        self.service = service

    def generate_solutions(self, company_name: str) -> List[SolutionSubmissionResponse]:
        """특정 회사의 취약 부문 기반 솔루션 생성"""
        try:
            logger.info(f"📝 솔루션 생성 요청 수신: company_name={company_name}")
            
            # SolutionService의 generate_solutions 호출
            solutions = self.service.generate_solutions(company_name)
            
            logger.info(f"✅ 솔루션 생성 완료: company_name={company_name}, count={len(solutions)}")
            return solutions
            
        except Exception as e:
            logger.error(f"❌ 솔루션 생성 실패: company_name={company_name}, error={e}")
            # 예외를 다시 발생시켜서 상위 FastAPI 라우터에서 처리하도록 함
            raise

    def get_solutions(self, company_name: str) -> List[SolutionSubmissionResponse]:
        """특정 회사의 솔루션 목록 조회"""
        try:
            logger.info(f"📝 솔루션 목록 조회 요청 수신: company_name={company_name}")
            
            # SolutionService의 get_solutions 호출
            solutions = self.service.get_solutions(company_name)
            
            logger.info(f"✅ 솔루션 목록 조회 완료: company_name={company_name}, count={len(solutions)}")
            return solutions
            
        except Exception as e:
            logger.error(f"❌ 솔루션 목록 조회 실패: company_name={company_name}, error={e}")
            # 예외를 다시 발생시켜서 상위 FastAPI 라우터에서 처리하도록 함
            raise
