"""
Report Router - API 엔드포인트 및 의존성 주입
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
import logging

# Domain imports
from ..domain.service.report_service import ReportService
from ..domain.controller.report_controller import ReportController

logger = logging.getLogger("report-router")

# DI 함수들
def get_report_service() -> ReportService:
    """Report Service 인스턴스 생성"""
    return ReportService()

def get_report_controller(service: ReportService = Depends(get_report_service)) -> ReportController:
    """Report Controller 인스턴스 생성"""
    return ReportController(service)

# 라우터 생성
report_router = APIRouter(prefix="/report", tags=["report"])

@report_router.get("/health", summary="서비스 상태 확인")
async def health_check():
    """서비스 상태 확인 엔드포인트"""
    return {
        "status": "healthy",
        "service": "report-service",
        "timestamp": datetime.now().isoformat(),
        "message": "Report service is running"
    }

@report_router.get("/", summary="모든 보고서 목록 조회")
async def get_all_reports(
    controller: ReportController = Depends(get_report_controller)
):
    """모든 보고서 목록 조회"""
    return controller.get_all_reports()

@report_router.get("/{report_id}", summary="특정 보고서 조회")
async def get_report_by_id(
    report_id: str,
    controller: ReportController = Depends(get_report_controller)
):
    """특정 보고서 조회"""
    return controller.get_report_by_id(report_id)

@report_router.post("/", summary="새로운 보고서 초안 생성")
async def create_report_draft(
    report_data: dict,
    controller: ReportController = Depends(get_report_controller)
):
    """새로운 보고서 초안 생성"""
    return controller.create_report_draft(report_data)

@report_router.put("/{report_id}", summary="보고서 업데이트")
async def update_report(
    report_id: str,
    report_data: dict,
    controller: ReportController = Depends(get_report_controller)
):
    """보고서 업데이트"""
    return controller.update_report(report_id, report_data)

@report_router.delete("/{report_id}", summary="보고서 삭제")
async def delete_report(
    report_id: str,
    controller: ReportController = Depends(get_report_controller)
):
    """보고서 삭제"""
    return controller.delete_report(report_id)

@report_router.post("/{report_id}/generate", summary="AI를 통한 보고서 초안 생성")
async def generate_report_with_ai(
    report_id: str,
    controller: ReportController = Depends(get_report_controller)
):
    """AI를 통한 보고서 초안 생성"""
    return controller.generate_report_with_ai(report_id)

@report_router.get("/metrics", summary="서비스 메트릭 조회")
async def get_metrics(
    controller: ReportController = Depends(get_report_controller)
):
    """서비스 메트릭 조회"""
    return controller.get_metrics()
