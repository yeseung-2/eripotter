"""
Monitoring Router - API 엔드포인트 및 의존성 주입
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
import logging

# Domain imports
from ..domain.repository.monitoring_repository import MonitoringRepository
from ..domain.service.monitoring_service import MonitoringService
from ..domain.controller.monitoring_controller import MonitoringController
from ..domain.model.monitoring_model import (
    CompanyListResponse,
    CompanyVulnerabilityResponse,
    SupplyChainVulnerabilityResponse,
    CompanyAssessmentResponse,
    SupplyChainAssessmentResponse,
    CompanySolutionResponse
)

logger = logging.getLogger("monitoring-router")

# DI 함수들
def get_monitoring_repository() -> MonitoringRepository:
    """Monitoring Repository 인스턴스 생성"""
    return MonitoringRepository()

def get_monitoring_service(repository: MonitoringRepository = Depends(get_monitoring_repository)) -> MonitoringService:
    """Monitoring Service 인스턴스 생성"""
    return MonitoringService(repository)

def get_monitoring_controller(service: MonitoringService = Depends(get_monitoring_service)) -> MonitoringController:
    """Monitoring Controller 인스턴스 생성"""
    return MonitoringController(service)

# 라우터 생성
monitoring_router = APIRouter(prefix="/monitoring", tags=["monitoring"])

@monitoring_router.get("/health", summary="서비스 상태 확인")
async def health_check():
    """서비스 상태 확인 엔드포인트"""
    return {
        "status": "healthy",
        "service": "monitoring-service",
        "timestamp": datetime.now().isoformat(),
        "message": "Monitoring service is running"
    }

@monitoring_router.get("/companies", summary="회사 목록 조회", response_model=CompanyListResponse)
async def get_company_list(
    controller: MonitoringController = Depends(get_monitoring_controller)
) -> CompanyListResponse:
    """회사 목록 조회"""
    try:
        return controller.get_company_list()
    except Exception as e:
        logger.error(f"❌ 회사 목록 조회 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"회사 목록 조회 중 오류가 발생했습니다: {str(e)}")

@monitoring_router.get("/vulnerabilities", summary="특정 회사의 취약부문 조회", response_model=CompanyVulnerabilityResponse)
async def get_company_vulnerabilities(
    controller: MonitoringController = Depends(get_monitoring_controller)
) -> CompanyVulnerabilityResponse:
    """특정 회사의 취약부문(score=0) 조회"""
    try:
        return controller.get_company_vulnerabilities()
    except Exception as e:
        logger.error(f"❌ 회사 취약부문 조회 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"회사 취약부문 조회 중 오류가 발생했습니다: {str(e)}")

@monitoring_router.get("/supply-chain/vulnerabilities", summary="공급망 전체 취약부문 조회", response_model=SupplyChainVulnerabilityResponse)
async def get_supply_chain_vulnerabilities(
    controller: MonitoringController = Depends(get_monitoring_controller)
) -> SupplyChainVulnerabilityResponse:
    """공급망 전체 취약부문 조회"""
    try:
        return controller.get_supply_chain_vulnerabilities()
    except Exception as e:
        logger.error(f"❌ 공급망 취약부문 조회 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"공급망 취약부문 조회 중 오류가 발생했습니다: {str(e)}")

@monitoring_router.get("/assessments", summary="특정 회사 Assessment 결과 조회", response_model=CompanyAssessmentResponse)
async def get_company_assessment(
    controller: MonitoringController = Depends(get_monitoring_controller)
) -> CompanyAssessmentResponse:
    """특정 회사의 Assessment 결과 조회"""
    try:
        return controller.get_company_assessment()
    except Exception as e:
        logger.error(f"❌ 회사 Assessment 결과 조회 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"회사 Assessment 결과 조회 중 오류가 발생했습니다: {str(e)}")

@monitoring_router.get("/supply-chain/assessments", summary="공급망 전체 Assessment 결과 조회", response_model=SupplyChainAssessmentResponse)
async def get_supply_chain_assessment(
    controller: MonitoringController = Depends(get_monitoring_controller)
) -> SupplyChainAssessmentResponse:
    """공급망 전체 Assessment 결과 조회"""
    try:
        return controller.get_supply_chain_assessment()
    except Exception as e:
        logger.error(f"❌ 공급망 Assessment 결과 조회 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"공급망 Assessment 결과 조회 중 오류가 발생했습니다: {str(e)}")

@monitoring_router.get("/solutions", summary="특정 회사 솔루션 목록 조회", response_model=CompanySolutionResponse)
async def get_company_solutions(
    controller: MonitoringController = Depends(get_monitoring_controller)
) -> CompanySolutionResponse:
    """특정 회사의 솔루션 목록 조회"""
    try:
        return controller.get_company_solutions()
    except Exception as e:
        logger.error(f"❌ 회사 솔루션 목록 조회 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"회사 솔루션 목록 조회 중 오류가 발생했습니다: {str(e)}")
