"""
Monitoring Router - API 엔드포인트 정의
"""
from fastapi import APIRouter, Depends, HTTPException, Header
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

# 사용자 인증 정보 추출 (임시 - 실제로는 JWT 토큰 검증 필요)
async def get_current_user_company(authorization: Optional[str] = Header(None)) -> str:
    """현재 로그인한 사용자의 회사명 추출"""
    # TODO: 실제 JWT 토큰 검증 및 사용자 회사 정보 추출
    # 현재는 임시로 헤더에서 회사명을 받음
    if not authorization:
        raise HTTPException(status_code=401, detail="인증 정보가 필요합니다")
    
    # 임시: Authorization 헤더에서 회사명 추출
    # 실제로는 JWT 토큰을 디코딩하여 사용자 정보 추출
    company_name = authorization.replace("Bearer ", "").strip()
    if not company_name:
        raise HTTPException(status_code=401, detail="유효하지 않은 인증 정보입니다")
    
    logger.info(f"🔐 인증된 사용자 회사: {company_name}")
    return company_name

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
    controller: MonitoringController = Depends(get_monitoring_controller),
    company_name: str = Depends(get_current_user_company)
):
    """로그인한 사용자 회사의 취약부문 조회"""
    try:
        result = controller.get_company_vulnerabilities(company_name)
        logger.info(f"✅ 취약부문 조회 성공: {company_name} - {len(result.vulnerabilities)}개 취약부문")
        return result
    except Exception as e:
        logger.error(f"❌ 취약부문 조회 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"취약부문 조회 중 오류가 발생했습니다: {str(e)}")

@monitoring_router.get("/supply-chain/vulnerabilities", summary="공급망 취약부문 조회")
async def get_supply_chain_vulnerabilities(
    controller: MonitoringController = Depends(get_monitoring_controller),
    company_name: str = Depends(get_current_user_company)
):
    """로그인한 사용자 회사의 공급망 취약부문 조회"""
    try:
        result = controller.get_supply_chain_vulnerabilities(company_name)
        logger.info(f"✅ 공급망 취약부문 조회 성공: {company_name} - root_company={result.root_company}")
        return result
    except Exception as e:
        logger.error(f"❌ 공급망 취약부문 조회 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"공급망 취약부문 조회 중 오류가 발생했습니다: {str(e)}")

@monitoring_router.get("/assessments", summary="Assessment 결과 조회")
async def get_assessments(
    controller: MonitoringController = Depends(get_monitoring_controller),
    company_name: str = Depends(get_current_user_company)
):
    """로그인한 사용자 회사의 Assessment 결과 조회"""
    try:
        result = controller.get_company_assessment(company_name)
        logger.info(f"✅ Assessment 결과 조회 성공: {company_name} - {len(result.assessments)}개 결과")
        return result
    except Exception as e:
        logger.error(f"❌ Assessment 결과 조회 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"Assessment 결과 조회 중 오류가 발생했습니다: {str(e)}")

@monitoring_router.get("/solutions", summary="솔루션 조회")
async def get_solutions(
    controller: MonitoringController = Depends(get_monitoring_controller),
    company_name: str = Depends(get_current_user_company)
):
    """로그인한 사용자 회사의 솔루션 조회"""
    try:
        result = controller.get_company_solutions(company_name)
        logger.info(f"✅ 솔루션 조회 성공: {company_name} - {len(result.solutions)}개 솔루션")
        return result
    except Exception as e:
        logger.error(f"❌ 솔루션 조회 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"솔루션 조회 중 오류가 발생했습니다: {str(e)}")
