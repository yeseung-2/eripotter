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

# ===== Company Partner Management API =====

@monitoring_router.get("/partners", summary="협력사 목록 조회")
async def get_company_partners(
    company_name: str,
    controller: MonitoringController = Depends(get_monitoring_controller)
):
    """특정 회사의 협력사 목록 조회"""
    try:
        result = controller.get_company_partners(company_name)
        logger.info(f"✅ 협력사 목록 조회 성공: {company_name} - {len(result.get('data', []))}개")
        return result
    except Exception as e:
        logger.error(f"❌ 협력사 목록 조회 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"협력사 목록 조회 중 오류가 발생했습니다: {str(e)}")

@monitoring_router.post("/partners", summary="협력사 추가")
async def add_company_partner(
    company_name: str,
    partner_name: str,
    controller: MonitoringController = Depends(get_monitoring_controller)
):
    """새로운 협력사 추가"""
    try:
        result = controller.add_company_partner(company_name, partner_name)
        logger.info(f"✅ 협력사 추가 성공: {company_name} -> {partner_name}")
        return result
    except Exception as e:
        logger.error(f"❌ 협력사 추가 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"협력사 추가 중 오류가 발생했습니다: {str(e)}")

@monitoring_router.put("/partners/{partner_id}", summary="협력사 정보 수정")
async def update_company_partner(
    partner_id: int,
    partner_name: str,
    controller: MonitoringController = Depends(get_monitoring_controller)
):
    """협력사 정보 수정"""
    try:
        result = controller.update_company_partner(partner_id, partner_name)
        logger.info(f"✅ 협력사 수정 성공: ID {partner_id} -> {partner_name}")
        return result
    except Exception as e:
        logger.error(f"❌ 협력사 수정 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"협력사 수정 중 오류가 발생했습니다: {str(e)}")

@monitoring_router.delete("/partners/{partner_id}", summary="협력사 삭제")
async def delete_company_partner(
    partner_id: int,
    controller: MonitoringController = Depends(get_monitoring_controller)
):
    """협력사 삭제"""
    try:
        result = controller.delete_company_partner(partner_id)
        logger.info(f"✅ 협력사 삭제 성공: ID {partner_id}")
        return result
    except Exception as e:
        logger.error(f"❌ 협력사 삭제 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"협력사 삭제 중 오류가 발생했습니다: {str(e)}")

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

# ===== Assessment Company Management Endpoints =====

@monitoring_router.get("/assessment/companies", summary="Assessment 기업 목록 조회")
async def get_assessment_companies(
    controller: MonitoringController = Depends(get_monitoring_controller)
):
    """Assessment 테이블의 모든 기업 목록 조회"""
    try:
        result = controller.get_assessment_companies()
        logger.info(f"✅ Assessment 기업 목록 조회 성공: {len(result.companies)}개 기업")
        return result
    except Exception as e:
        logger.error(f"❌ Assessment 기업 목록 조회 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"Assessment 기업 목록 조회 중 오류가 발생했습니다: {str(e)}")

@monitoring_router.get("/assessment/companies/{company_name}/dashboard", summary="기업별 Assessment 대시보드")
async def get_company_assessment_dashboard(
    company_name: str,
    controller: MonitoringController = Depends(get_monitoring_controller)
):
    """특정 기업의 Assessment 대시보드 데이터 조회"""
    try:
        result = controller.get_company_assessment_dashboard(company_name)
        logger.info(f"✅ 기업 Assessment 대시보드 조회 성공: {company_name}")
        return result
    except Exception as e:
        logger.error(f"❌ 기업 Assessment 대시보드 조회 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"기업 Assessment 대시보드 조회 중 오류가 발생했습니다: {str(e)}")
