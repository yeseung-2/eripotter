import logging
from typing import List, Dict, Union
from ..service.monitoring_service import MonitoringService
from ..model.monitoring_model import (
    CompanyListResponse,
    CompanyVulnerabilityResponse,
    SupplyChainVulnerabilityResponse,
    CompanyAssessmentResponse,
    SupplyChainAssessmentResponse,
    CompanySolutionResponse
)

logger = logging.getLogger("monitoring-controller")

class MonitoringController:
    def __init__(self, service: MonitoringService):
        self.service = service
    
    def get_company_list(self) -> CompanyListResponse:
        """회사 목록 조회"""
        try:
            logger.info("📝 회사 목록 조회 컨트롤러 요청")
            return self.service.get_company_list()
        except Exception as e:
            logger.error(f"❌ 회사 목록 조회 컨트롤러 오류: {e}")
            raise
    
    def get_company_vulnerabilities(self, company_name: str) -> CompanyVulnerabilityResponse:
        """특정 회사 취약부문(score=0) 조회"""
        try:
            logger.info(f"📝 회사 취약부문 조회 컨트롤러 요청: {company_name}")
            return self.service.get_company_vulnerabilities(company_name)
        except Exception as e:
            logger.error(f"❌ 회사 취약부문 조회 컨트롤러 오류: {e}")
            raise
    
    def get_supply_chain_vulnerabilities(self, company_name: str) -> SupplyChainVulnerabilityResponse:
        """공급망 전체 취약부문 조회"""
        try:
            logger.info(f"📝 공급망 취약부문 조회 컨트롤러 요청: {company_name}")
            return self.service.get_supply_chain_vulnerabilities(company_name)
        except Exception as e:
            logger.error(f"❌ 공급망 취약부문 조회 컨트롤러 오류: {e}")
            raise
    
    def get_company_assessment(self, company_name: str) -> CompanyAssessmentResponse:
        """특정 회사 assessment 결과 조회"""
        try:
            logger.info(f"📝 회사 assessment 결과 조회 컨트롤러 요청: {company_name}")
            return self.service.get_company_assessment(company_name)
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
    
    def get_company_solutions(self, company_name: str) -> CompanySolutionResponse:
        """특정 회사 솔루션 목록 조회"""
        try:
            logger.info(f"📝 회사 솔루션 목록 조회 컨트롤러 요청: {company_name}")
            return self.service.get_company_solutions(company_name)
        except Exception as e:
            logger.error(f"❌ 회사 솔루션 목록 조회 컨트롤러 오류: {e}")
            raise
