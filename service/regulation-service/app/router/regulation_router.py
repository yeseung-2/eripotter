"""
Regulation Router - API 엔드포인트 및 의존성 주입
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
import logging

# Domain imports
from ..domain.service.regulation_service import RegulationService
from ..domain.controller.regulation_controller import RegulationController

logger = logging.getLogger("regulation-router")

# DI 함수들
def get_regulation_service() -> RegulationService:
    """Regulation Service 인스턴스 생성"""
    return RegulationService()

def get_regulation_controller(service: RegulationService = Depends(get_regulation_service)) -> RegulationController:
    """Regulation Controller 인스턴스 생성"""
    return RegulationController(service)

# 라우터 생성
regulation_router = APIRouter(prefix="/regulation", tags=["regulation"])

@regulation_router.get("/health", summary="서비스 상태 확인")
async def health_check():
    """서비스 상태 확인 엔드포인트"""
    return {
        "status": "healthy",
        "service": "regulation-service",
        "timestamp": datetime.now().isoformat(),
        "message": "Regulation service is running"
    }

@regulation_router.get("/", summary="모든 규정안 목록 조회")
async def get_all_regulations(
    controller: RegulationController = Depends(get_regulation_controller)
):
    """모든 규정안 목록 조회"""
    return controller.get_all_regulations()

@regulation_router.get("/{regulation_id}", summary="특정 규정안 조회")
async def get_regulation_by_id(
    regulation_id: str,
    controller: RegulationController = Depends(get_regulation_controller)
):
    """특정 규정안 조회"""
    return controller.get_regulation_by_id(regulation_id)

@regulation_router.post("/", summary="새로운 규정안 생성")
async def create_regulation(
    regulation_data: dict,
    controller: RegulationController = Depends(get_regulation_controller)
):
    """새로운 규정안 생성"""
    return controller.create_regulation(regulation_data)

@regulation_router.put("/{regulation_id}", summary="규정안 업데이트")
async def update_regulation(
    regulation_id: str,
    regulation_data: dict,
    controller: RegulationController = Depends(get_regulation_controller)
):
    """규정안 업데이트"""
    return controller.update_regulation(regulation_id, regulation_data)

@regulation_router.delete("/{regulation_id}", summary="규정안 삭제")
async def delete_regulation(
    regulation_id: str,
    controller: RegulationController = Depends(get_regulation_controller)
):
    """규정안 삭제"""
    return controller.delete_regulation(regulation_id)

@regulation_router.get("/metrics", summary="서비스 메트릭 조회")
async def get_metrics(
    controller: RegulationController = Depends(get_regulation_controller)
):
    """서비스 메트릭 조회"""
    return controller.get_metrics()
