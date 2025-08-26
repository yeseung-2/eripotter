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
from ..domain.model.assessment_model import KesgResponse, KesgItem, AssessmentRequest

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

@assessment_router.get("/kesg", summary="kesg 테이블의 모든 항목 조회")
async def get_kesg_items(
    controller: AssessmentController = Depends(get_assessment_controller)
) -> KesgResponse:
    """kesg 테이블에서 모든 item_name 조회"""
    try:
        return controller.get_kesg_items()
    except Exception as e:
        logger.error(f"❌ kesg 항목 조회 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"kesg 항목 조회 중 오류가 발생했습니다: {str(e)}")

@assessment_router.get("/kesg/{item_id}", summary="특정 kesg 항목 조회")
async def get_kesg_item_by_id(
    item_id: int,
    controller: AssessmentController = Depends(get_assessment_controller)
) -> KesgItem:
    """특정 ID의 kesg 항목 조회"""
    try:
        return controller.get_kesg_item_by_id(item_id)
    except ValueError as e:
        logger.warning(f"⚠️ kesg 항목을 찾을 수 없음: ID {item_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"❌ kesg 항목 조회 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"kesg 항목 조회 중 오류가 발생했습니다: {str(e)}")

@assessment_router.post("/", summary="자가진단 응답 제출")
async def submit_assessment(
    request: AssessmentRequest,
    controller: AssessmentController = Depends(get_assessment_controller)
):
    """자가진단 응답 제출 및 저장"""
    try:
        success = controller.submit_assessment(request.company_id, request.responses)
        if success:
            return {
                "status": "success",
                "message": "자가진단 응답이 성공적으로 저장되었습니다.",
                "company_id": request.company_id,
                "responses_count": len(request.responses)
            }
        else:
            raise HTTPException(status_code=500, detail="자가진단 응답 저장에 실패했습니다.")
    except Exception as e:
        logger.error(f"❌ 자가진단 응답 제출 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"자가진단 응답 제출 중 오류가 발생했습니다: {str(e)}")

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

@assessment_router.get("/results/{company_id}", summary="특정 회사의 자가진단 결과 조회")
async def get_company_results(
    company_id: str,
    controller: AssessmentController = Depends(get_assessment_controller)
):
    """특정 회사의 자가진단 결과 조회"""
    try:
        results = controller.get_company_results(company_id)
        return {
            "status": "success",
            "company_id": company_id,
            "results": results,
            "total_count": len(results)
        }
    except Exception as e:
        logger.error(f"❌ 회사별 결과 조회 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"회사별 결과 조회 중 오류가 발생했습니다: {str(e)}")
