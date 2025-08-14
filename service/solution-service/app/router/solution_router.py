"""
Solution Router - API 엔드포인트 및 의존성 주입
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
import logging

# Domain imports
from ..domain.service.solution_service import SolutionService
from ..domain.controller.solution_controller import SolutionController

logger = logging.getLogger("solution-router")

# DI 함수들
def get_solution_service() -> SolutionService:
    """Solution Service 인스턴스 생성"""
    return SolutionService()

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

@solution_router.get("/", summary="모든 솔루션 목록 조회")
async def get_all_solutions(
    controller: SolutionController = Depends(get_solution_controller)
):
    """모든 솔루션 목록 조회"""
    return controller.get_all_solutions()

@solution_router.get("/{solution_id}", summary="특정 솔루션 조회")
async def get_solution_by_id(
    solution_id: str,
    controller: SolutionController = Depends(get_solution_controller)
):
    """특정 솔루션 조회"""
    return controller.get_solution_by_id(solution_id)

@solution_router.post("/", summary="새로운 솔루션 생성")
async def create_solution(
    solution_data: dict,
    controller: SolutionController = Depends(get_solution_controller)
):
    """새로운 솔루션 생성"""
    return controller.create_solution(solution_data)

@solution_router.put("/{solution_id}", summary="솔루션 업데이트")
async def update_solution(
    solution_id: str,
    solution_data: dict,
    controller: SolutionController = Depends(get_solution_controller)
):
    """솔루션 업데이트"""
    return controller.update_solution(solution_id, solution_data)

@solution_router.delete("/{solution_id}", summary="솔루션 삭제")
async def delete_solution(
    solution_id: str,
    controller: SolutionController = Depends(get_solution_controller)
):
    """솔루션 삭제"""
    return controller.delete_solution(solution_id)

@solution_router.post("/generate", summary="AI를 통한 취약점 기반 솔루션 생성")
async def generate_solution_with_ai(
    assessment_data: dict,
    controller: SolutionController = Depends(get_solution_controller)
):
    """AI를 통한 취약점 기반 솔루션 생성"""
    return controller.generate_solution_with_ai(assessment_data)

@solution_router.get("/vulnerability/{vulnerability_id}", summary="특정 취약점에 대한 솔루션 조회")
async def get_solutions_by_vulnerability(
    vulnerability_id: str,
    controller: SolutionController = Depends(get_solution_controller)
):
    """특정 취약점에 대한 솔루션 조회"""
    return controller.get_solutions_by_vulnerability(vulnerability_id)

@solution_router.get("/metrics", summary="서비스 메트릭 조회")
async def get_metrics(
    controller: SolutionController = Depends(get_solution_controller)
):
    """서비스 메트릭 조회"""
    return controller.get_metrics()
