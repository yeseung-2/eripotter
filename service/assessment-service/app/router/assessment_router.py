"""
Assessment Router - API 엔드포인트 및 의존성 주입
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
import logging

# Domain imports
from ..domain.repository.assessment_repository import AssessmentRepository
from ..domain.service.assessment_service import AssessmentService
from ..domain.controller.assessment_controller import AssessmentController
from ..domain.model.assessment_model import AssessmentRequest, KesgResponse, KesgItem, AssessmentSubmissionResponse

logger = logging.getLogger("assessment-router")

# DI 함수들
def get_assessment_repository() -> AssessmentRepository:
    """Assessment Repository 인스턴스 생성"""
    return AssessmentRepository()

def get_assessment_service(repository: AssessmentRepository = Depends(get_assessment_repository)) -> AssessmentService:
    """Assessment Service 인스턴스 생성"""
    return AssessmentService(repository)

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

@assessment_router.get("/kesg", summary="kesg 테이블의 모든 항목 조회", response_model=KesgResponse)
async def get_kesg_items(
    controller: AssessmentController = Depends(get_assessment_controller)
) -> KesgResponse:
    """kesg 테이블에서 모든 항목 조회"""
    try:
        return controller.get_kesg_items()
    except Exception as e:
        logger.error(f"❌ kesg 항목 조회 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"kesg 항목 조회 중 오류가 발생했습니다: {str(e)}")

@assessment_router.get("/kesg/{item_id}", summary="특정 kesg 항목 조회", response_model=KesgItem)
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

@assessment_router.post("/", summary="자가진단 응답 제출", response_model=List[AssessmentSubmissionResponse])
async def submit_assessment(
    request: AssessmentRequest,
    controller: AssessmentController = Depends(get_assessment_controller)
) -> List[AssessmentSubmissionResponse]:
    """자가진단 응답 제출 및 저장"""
    try:
        return controller.submit_assessment(request)
    except Exception as e:
        logger.error(f"❌ 자가진단 응답 제출 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"자가진단 응답 제출 중 오류가 발생했습니다: {str(e)}")

@assessment_router.get("/assessment-results/{company_name}", summary="특정 회사의 자가진단 결과 조회 (상세)")
async def get_assessment_results(
    company_name: str,
    controller: AssessmentController = Depends(get_assessment_controller)
):
    """특정 회사의 자가진단 결과 조회 (상세 정보 포함)"""
    try:
        results = controller.get_assessment_results(company_name)
        return {
            "status": "success",
            "company_name": company_name,
            "assessment_results": results,
            "total_count": len(results)
        }
    except Exception as e:
        logger.error(f"❌ 자가진단 결과 조회 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"자가진단 결과 조회 중 오류가 발생했습니다: {str(e)}")

@assessment_router.get("/vulnerable-sections/{company_name}", summary="특정 회사의 취약 부문 조회")
async def get_vulnerable_sections(
    company_name: str,
    controller: AssessmentController = Depends(get_assessment_controller)
):
    """특정 회사의 취약 부문 조회 (score가 0인 문항)"""
    try:
        vulnerable_sections = controller.get_vulnerable_sections(company_name)
        return {
            "status": "success",
            "company_name": company_name,
            "vulnerable_sections": vulnerable_sections,
            "total_count": len(vulnerable_sections)
        }
    except Exception as e:
        logger.error(f"❌ 취약 부문 조회 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"취약 부문 조회 중 오류가 발생했습니다: {str(e)}")
