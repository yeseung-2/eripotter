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
