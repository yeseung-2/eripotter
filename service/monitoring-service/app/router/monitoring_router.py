"""
Monitoring Router - API 엔드포인트 정의
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# Domain imports
from ..domain.repository.monitoring_repository import MonitoringRepository
from ..domain.service.monitoring_service import MonitoringService
from ..domain.controller.monitoring_controller import MonitoringController

# 로깅 설정
logger = logging.getLogger("monitoring-router")

# 라우터 생성
monitoring_router = APIRouter(prefix="/monitoring", tags=["monitoring"])

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

# ===== 데이터베이스 연동 엔드포인트들 =====

@monitoring_router.get("/companies", summary="회사 목록 조회")
async def get_company_list(
    controller: MonitoringController = Depends(get_monitoring_controller)
):
    """회사 목록 조회"""
    try:
        result = controller.get_company_list()
        logger.info(f"✅ 회사 목록 조회 성공: {len(result.companies)}개 회사")
        return result
    except Exception as e:
        logger.error(f"❌ 회사 목록 조회 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"회사 목록 조회 중 오류가 발생했습니다: {str(e)}")

@monitoring_router.get("/vulnerabilities", summary="회사별 취약부문 조회")
async def get_company_vulnerabilities(
    controller: MonitoringController = Depends(get_monitoring_controller)
):
    """회사별 취약부문 조회"""
    try:
        result = controller.get_company_vulnerabilities()
        logger.info(f"✅ 취약부문 조회 성공: {len(result.vulnerabilities)}개 취약부문")
        return result
    except Exception as e:
        logger.error(f"❌ 취약부문 조회 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"취약부문 조회 중 오류가 발생했습니다: {str(e)}")

@monitoring_router.get("/supply-chain/vulnerabilities", summary="공급망 취약부문 조회")
async def get_supply_chain_vulnerabilities(
    controller: MonitoringController = Depends(get_monitoring_controller)
):
    """공급망 취약부문 조회"""
    try:
        result = controller.get_supply_chain_vulnerabilities()
        logger.info(f"✅ 공급망 취약부문 조회 성공: root_company={result.root_company}")
        return result
    except Exception as e:
        logger.error(f"❌ 공급망 취약부문 조회 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"공급망 취약부문 조회 중 오류가 발생했습니다: {str(e)}")

@monitoring_router.get("/assessments", summary="Assessment 결과 조회")
async def get_assessments(
    controller: MonitoringController = Depends(get_monitoring_controller)
):
    """Assessment 결과 조회"""
    try:
        result = controller.get_company_assessment()
        logger.info(f"✅ Assessment 결과 조회 성공: {len(result.assessments)}개 결과")
        return result
    except Exception as e:
        logger.error(f"❌ Assessment 결과 조회 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"Assessment 결과 조회 중 오류가 발생했습니다: {str(e)}")

@monitoring_router.get("/solutions", summary="솔루션 조회")
async def get_solutions(
    controller: MonitoringController = Depends(get_monitoring_controller)
):
    """솔루션 조회"""
    try:
        result = controller.get_company_solutions()
        logger.info(f"✅ 솔루션 조회 성공: {len(result.solutions)}개 솔루션")
        return result
    except Exception as e:
        logger.error(f"❌ 솔루션 조회 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"솔루션 조회 중 오류가 발생했습니다: {str(e)}")
