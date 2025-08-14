"""
Monitoring Router - API 엔드포인트 및 의존성 주입
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
import logging

# Domain imports
from ..domain.service.monitoring_service import MonitoringService
from ..domain.controller.monitoring_controller import MonitoringController

logger = logging.getLogger("monitoring-router")

# DI 함수들
def get_monitoring_service() -> MonitoringService:
    """Monitoring Service 인스턴스 생성"""
    return MonitoringService()

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

@monitoring_router.get("/", summary="모든 모니터링 데이터 조회")
async def get_all_monitoring_data(
    controller: MonitoringController = Depends(get_monitoring_controller)
):
    """모든 모니터링 데이터 조회"""
    return controller.get_all_monitoring_data()

@monitoring_router.get("/{company_id}", summary="특정 회사 모니터링 데이터 조회")
async def get_company_monitoring_data(
    company_id: str,
    controller: MonitoringController = Depends(get_monitoring_controller)
):
    """특정 회사 모니터링 데이터 조회"""
    return controller.get_company_monitoring_data(company_id)

@monitoring_router.post("/", summary="새로운 모니터링 데이터 생성")
async def create_monitoring_data(
    monitoring_data: dict,
    controller: MonitoringController = Depends(get_monitoring_controller)
):
    """새로운 모니터링 데이터 생성"""
    return controller.create_monitoring_data(monitoring_data)

@monitoring_router.put("/{company_id}", summary="모니터링 데이터 업데이트")
async def update_monitoring_data(
    company_id: str,
    monitoring_data: dict,
    controller: MonitoringController = Depends(get_monitoring_controller)
):
    """모니터링 데이터 업데이트"""
    return controller.update_monitoring_data(company_id, monitoring_data)

@monitoring_router.delete("/{company_id}", summary="모니터링 데이터 삭제")
async def delete_monitoring_data(
    company_id: str,
    controller: MonitoringController = Depends(get_monitoring_controller)
):
    """모니터링 데이터 삭제"""
    return controller.delete_monitoring_data(company_id)

@monitoring_router.get("/metrics", summary="서비스 메트릭 조회")
async def get_metrics(
    controller: MonitoringController = Depends(get_monitoring_controller)
):
    """서비스 메트릭 조회"""
    return controller.get_metrics()
