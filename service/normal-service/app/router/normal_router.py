"""
Normal Router - API 엔드포인트 및 의존성 주입
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List, Optional
from datetime import datetime
import logging

# Domain imports
from ..domain.service.normal_service import NormalService
from ..domain.controller.normal_controller import NormalController

logger = logging.getLogger("normal-router")

# DI 함수들
def get_normal_service() -> NormalService:
    """Normal Service 인스턴스 생성"""
    return NormalService()

def get_normal_controller(service: NormalService = Depends(get_normal_service)) -> NormalController:
    """Normal Controller 인스턴스 생성"""
    return NormalController(service)

# 라우터 생성
normal_router = APIRouter(prefix="/normal", tags=["normal"])

@normal_router.get("/health", summary="서비스 상태 확인")
async def health_check():
    """서비스 상태 확인 엔드포인트"""
    return {
        "status": "healthy",
        "service": "normal-service",
        "timestamp": datetime.now().isoformat(),
        "message": "Normal service is running"
    }

@normal_router.get("/", summary="모든 정규화 데이터 조회")
async def get_all_normalized_data(
    controller: NormalController = Depends(get_normal_controller)
):
    """모든 정규화 데이터 조회"""
    return controller.get_all_normalized_data()

@normal_router.get("/{data_id}", summary="특정 정규화 데이터 조회")
async def get_normalized_data_by_id(
    data_id: str,
    controller: NormalController = Depends(get_normal_controller)
):
    """특정 정규화 데이터 조회"""
    return controller.get_normalized_data_by_id(data_id)

@normal_router.post("/upload", summary="엑셀 파일 업로드 및 정규화")
async def upload_excel_file(
    file: UploadFile = File(...),
    controller: NormalController = Depends(get_normal_controller)
):
    """엑셀 파일 업로드 및 데이터 정규화"""
    return controller.upload_and_normalize_excel(file)

@normal_router.post("/", summary="새로운 정규화 데이터 생성")
async def create_normalized_data(
    data: dict,
    controller: NormalController = Depends(get_normal_controller)
):
    """새로운 정규화 데이터 생성"""
    return controller.create_normalized_data(data)

@normal_router.put("/{data_id}", summary="정규화 데이터 업데이트")
async def update_normalized_data(
    data_id: str,
    data: dict,
    controller: NormalController = Depends(get_normal_controller)
):
    """정규화 데이터 업데이트"""
    return controller.update_normalized_data(data_id, data)

@normal_router.delete("/{data_id}", summary="정규화 데이터 삭제")
async def delete_normalized_data(
    data_id: str,
    controller: NormalController = Depends(get_normal_controller)
):
    """정규화 데이터 삭제"""
    return controller.delete_normalized_data(data_id)

@normal_router.get("/metrics", summary="서비스 메트릭 조회")
async def get_metrics(
    controller: NormalController = Depends(get_normal_controller)
):
    """서비스 메트릭 조회"""
    return controller.get_metrics()
