import logging
from typing import List, Dict, Union
from ..service.monitoring_service import MonitoringService
from ..model.monitoring_model import (
    CompanyListResponse,
    CompanyVulnerabilityResponse,
    SupplyChainVulnerabilityResponse,
    CompanyAssessmentResponse,
    SupplyChainAssessmentResponse,
    CompanySolutionResponse,
    AssessmentCompanyListResponse,
    CompanyAssessmentDashboardResponse
)

logger = logging.getLogger("monitoring-controller")

class MonitoringController:
    def __init__(self, service: MonitoringService):
        self.service = service
    
    # ===== Company Partner Management =====
    
    def get_company_partners(self, company_name: str) -> Dict[str, Union[str, List[Dict[str, Union[str, int, None]]]]]:
        """특정 회사의 협력사 목록 조회"""
        try:
            logger.info(f"📝 협력사 목록 조회 컨트롤러 요청: {company_name}")
            partners = self.service.get_company_partners(company_name)
            return {
                "status": "success",
                "data": partners
            }
        except Exception as e:
            logger.error(f"❌ 협력사 목록 조회 컨트롤러 오류: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def add_company_partner(self, company_name: str, partner_name: str) -> Dict[str, str]:
        """새로운 협력사 추가"""
        try:
            logger.info(f"📝 협력사 추가 컨트롤러 요청: {company_name} -> {partner_name}")
            success = self.service.add_company_partner(company_name, partner_name)
            if success:
                return {
                    "status": "success",
                    "message": "협력사가 성공적으로 추가되었습니다."
                }
            else:
                return {
                    "status": "error",
                    "message": "협력사 추가에 실패했습니다."
                }
        except Exception as e:
            logger.error(f"❌ 협력사 추가 컨트롤러 오류: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def update_company_partner(self, partner_id: int, partner_name: str) -> Dict[str, str]:
        """협력사 정보 수정"""
        try:
            logger.info(f"📝 협력사 수정 컨트롤러 요청: ID {partner_id} -> {partner_name}")
            success = self.service.update_company_partner(partner_id, partner_name)
            if success:
                return {
                    "status": "success",
                    "message": "협력사 정보가 성공적으로 수정되었습니다."
                }
            else:
                return {
                    "status": "error",
                    "message": "협력사 수정에 실패했습니다."
                }
        except Exception as e:
            logger.error(f"❌ 협력사 수정 컨트롤러 오류: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def delete_company_partner(self, partner_id: int) -> Dict[str, str]:
        """협력사 삭제"""
        try:
            logger.info(f"📝 협력사 삭제 컨트롤러 요청: ID {partner_id}")
            success = self.service.delete_company_partner(partner_id)
            if success:
                return {
                    "status": "success",
                    "message": "협력사가 성공적으로 삭제되었습니다."
                }
            else:
                return {
                    "status": "error",
                    "message": "협력사 삭제에 실패했습니다."
                }
        except Exception as e:
            logger.error(f"❌ 협력사 삭제 컨트롤러 오류: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def get_recursive_supply_chain(self, root_company: str = None, max_depth: int = 5) -> Dict[str, Union[str, List, int]]:
        """재귀적 공급망 구조 조회"""
        try:
            logger.info(f"📝 재귀적 공급망 구조 조회 컨트롤러 요청: {root_company or 'LG에너지솔루션'}")
            result = self.service.get_recursive_supply_chain(root_company, max_depth)
            return {
                "status": "success",
                "data": result
            }
        except Exception as e:
            logger.error(f"❌ 재귀적 공급망 구조 조회 컨트롤러 오류: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_company_list(self) -> CompanyListResponse:
        """회사 목록 조회"""
        try:
            logger.info("📝 회사 목록 조회 컨트롤러 요청")
            return self.service.get_company_list()
        except Exception as e:
            logger.error(f"❌ 회사 목록 조회 컨트롤러 오류: {e}")
            raise
    
    def get_company_vulnerabilities(self) -> CompanyVulnerabilityResponse:
        """특정 회사 취약부문(score=0) 조회"""
        try:
            logger.info("📝 회사 취약부문 조회 컨트롤러 요청")
            return self.service.get_company_vulnerabilities()
        except Exception as e:
            logger.error(f"❌ 회사 취약부문 조회 컨트롤러 오류: {e}")
            raise
    
    def get_supply_chain_vulnerabilities(self) -> SupplyChainVulnerabilityResponse:
        """공급망 전체 취약부문 조회"""
        try:
            logger.info("📝 공급망 취약부문 조회 컨트롤러 요청")
            return self.service.get_supply_chain_vulnerabilities()
        except Exception as e:
            logger.error(f"❌ 공급망 취약부문 조회 컨트롤러 오류: {e}")
            raise
    
    def get_company_assessment(self) -> CompanyAssessmentResponse:
        """특정 회사 assessment 결과 조회"""
        try:
            logger.info("📝 회사 assessment 결과 조회 컨트롤러 요청")
            return self.service.get_company_assessment()
        except Exception as e:
            logger.error(f"❌ 회사 assessment 결과 조회 컨트롤러 오류: {e}")
            raise
    
    def get_supply_chain_assessment(self) -> SupplyChainAssessmentResponse:
        """공급망 전체 assessment 결과 조회"""
        try:
            logger.info("📝 공급망 assessment 결과 조회 컨트롤러 요청")
            return self.service.get_supply_chain_assessment()
        except Exception as e:
            logger.error(f"❌ 공급망 assessment 결과 조회 컨트롤러 오류: {e}")
            raise
    
    def get_company_solutions(self) -> CompanySolutionResponse:
        """특정 회사 솔루션 목록 조회"""
        try:
            logger.info("📝 회사 솔루션 목록 조회 컨트롤러 요청")
            return self.service.get_company_solutions()
        except Exception as e:
            logger.error(f"❌ 회사 솔루션 목록 조회 컨트롤러 오류: {e}")
            raise

    # ===== Assessment Company Management =====
    
    def get_assessment_companies(self) -> AssessmentCompanyListResponse:
        """Assessment 테이블의 모든 기업 목록 조회"""
        try:
            logger.info("📝 Assessment 기업 목록 조회 컨트롤러 요청")
            return self.service.get_assessment_companies()
        except Exception as e:
            logger.error(f"❌ Assessment 기업 목록 조회 컨트롤러 오류: {e}")
            raise
    
    def get_company_assessment_dashboard(self, company_name: str) -> CompanyAssessmentDashboardResponse:
        """특정 기업의 Assessment 대시보드 데이터 조회"""
        try:
            logger.info(f"📝 기업 Assessment 대시보드 조회 컨트롤러 요청: company_name={company_name}")
            return self.service.get_company_assessment_dashboard(company_name)
        except Exception as e:
            logger.error(f"❌ 기업 Assessment 대시보드 조회 컨트롤러 오류: {e}")
            raise
