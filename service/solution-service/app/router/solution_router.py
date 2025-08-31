"""
Solution Router - API 엔드포인트 및 의존성 주입
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
import logging

# Domain imports
from ..domain.repository.solution_repository import SolutionRepository
from ..domain.service.solution_service import SolutionService
from ..domain.controller.solution_controller import SolutionController
from ..domain.model.solution_model import SolutionSubmissionResponse

logger = logging.getLogger("solution-router")

# DI 함수들
def get_solution_repository() -> SolutionRepository:
    """Solution Repository 인스턴스 생성"""
    return SolutionRepository()

def get_solution_service(repository: SolutionRepository = Depends(get_solution_repository)) -> SolutionService:
    """Solution Service 인스턴스 생성"""
    return SolutionService(repository)

def get_solution_controller(service: SolutionService = Depends(get_solution_service)) -> SolutionController:
    """Solution Controller 인스턴스 생성"""
    return SolutionController(service)

# 라우터 생성
solution_router = APIRouter(prefix="/solution", tags=["solution"])

@solution_router.get("/health", summary="서비스 상태 확인")
async def health_check():
    """서비스 상태 확인 엔드포인트"""
    return {
        "status": "healthy",
        "service": "solution-service",
        "timestamp": datetime.now().isoformat(),
        "message": "Solution service is running"
    }

@solution_router.post("/generate/{company_name}", summary="특정 회사의 취약 부문 기반 솔루션 생성", response_model=List[SolutionSubmissionResponse])
async def generate_solutions(
    company_name: str,
    controller: SolutionController = Depends(get_solution_controller)
) -> List[SolutionSubmissionResponse]:
    """특정 회사의 취약 부문 기반 솔루션 생성"""
    try:
        return controller.generate_solutions(company_name)
    except Exception as e:
        logger.error(f"❌ 솔루션 생성 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"솔루션 생성 중 오류가 발생했습니다: {str(e)}")

@solution_router.get("/{company_name}", summary="특정 회사의 솔루션 목록 조회", response_model=List[SolutionSubmissionResponse])
async def get_solutions(
    company_name: str,
    controller: SolutionController = Depends(get_solution_controller)
) -> List[SolutionSubmissionResponse]:
    """특정 회사의 솔루션 목록 조회"""
    try:
        return controller.get_solutions(company_name)
    except Exception as e:
        logger.error(f"❌ 솔루션 목록 조회 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"솔루션 목록 조회 중 오류가 발생했습니다: {str(e)}")
