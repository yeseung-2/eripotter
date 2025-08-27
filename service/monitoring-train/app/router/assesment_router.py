"""
Assessment Router - API 엔드포인트 및 의존성 주입
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
import logging

# Domain imports
from ..domain.service.assessment_service import AssessmentService
from ..domain.controller.assessment_controller import AssessmentController

logger = logging.getLogger("assessment-router")

# DI 함수들
def get_assessment_service() -> AssessmentService:
    """Assessment Service 인스턴스 생성"""
    return AssessmentService()

def get_assessment_controller(service: AssessmentService = Depends(get_assessment_service)) -> AssessmentController:
    """Assessment Controller 인스턴스 생성"""
    return AssessmentController(service)

# 라우터 생성
assessment_router = APIRouter(prefix="/assessment", tags=["assessment"])

@assessment_router.get("/health", summary="서비스 상태 확인")
async def health_check():
    """서비스 상태 확인 엔드포인트"""
    return {
        "status": "healthy",
        "service": "assessment-service",
        "timestamp": datetime.now().isoformat(),
        "message": "Assessment service is running"
    }

@assessment_router.get("/", summary="모든 assessment 목록 조회")
async def get_assessments(
    controller: AssessmentController = Depends(get_assessment_controller)
):
    """모든 assessment 목록 조회"""
    return controller.get_all_assessments()

@assessment_router.get("/{assessment_id}", summary="특정 assessment 조회")
async def get_assessment_by_id(
    assessment_id: str,
    controller: AssessmentController = Depends(get_assessment_controller)
):
    """특정 assessment 조회"""
    return controller.get_assessment_by_id(assessment_id)

@assessment_router.post("/", summary="새로운 assessment 생성")
async def create_assessment(
    assessment_data: dict,
    controller: AssessmentController = Depends(get_assessment_controller)
):
    """새로운 assessment 생성"""
    return controller.create_assessment(assessment_data)

@assessment_router.put("/{assessment_id}", summary="assessment 업데이트")
async def update_assessment(
    assessment_id: str,
    assessment_data: dict,
    controller: AssessmentController = Depends(get_assessment_controller)
):
    """assessment 업데이트"""
    return controller.update_assessment(assessment_id, assessment_data)

@assessment_router.delete("/{assessment_id}", summary="assessment 삭제")
async def delete_assessment(
    assessment_id: str,
    controller: AssessmentController = Depends(get_assessment_controller)
):
    """assessment 삭제"""
    return controller.delete_assessment(assessment_id)

@assessment_router.get("/metrics", summary="서비스 메트릭 조회")
async def get_metrics(
    controller: AssessmentController = Depends(get_assessment_controller)
):
    """서비스 메트릭 조회"""
    return controller.get_metrics()
