"""
Sharing Router - API 엔드포인트 및 의존성 주입
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
import logging

# Domain imports
from ..domain.service.sharing_service import SharingService
from ..domain.controller.sharing_controller import SharingController
from ..domain.model.sharing_model import SharingRequestCreate, ReviewRequest

logger = logging.getLogger("sharing-router")

# DI 함수들
def get_sharing_service() -> SharingService:
    """Sharing Service 인스턴스 생성"""
    return SharingService()

def get_sharing_controller(service: SharingService = Depends(get_sharing_service)) -> SharingController:
    """Sharing Controller 인스턴스 생성"""
    return SharingController(service)

# 라우터 생성
sharing_router = APIRouter(prefix="/sharing", tags=["sharing"])

@sharing_router.get("/health", summary="서비스 상태 확인")
async def health_check():
    """서비스 상태 확인 엔드포인트"""
    return {
        "status": "healthy",
        "service": "sharing-service",
        "timestamp": datetime.now().isoformat(),
        "message": "Sharing service is running"
    }

@sharing_router.get("/", summary="모든 데이터 공유 요청 목록 조회")
async def get_all_sharing_requests(
    controller: SharingController = Depends(get_sharing_controller)
):
    """모든 데이터 공유 요청 목록 조회"""
    return controller.get_all_sharing_requests()

@sharing_router.get("/companies", summary="회사 목록 조회")
async def get_companies(
    controller: SharingController = Depends(get_sharing_controller)
):
    """전체 회사 목록 조회"""
    return controller.get_companies()

@sharing_router.get("/{request_id}", summary="특정 데이터 공유 요청 조회")
async def get_sharing_request_by_id(
    request_id: str,
    controller: SharingController = Depends(get_sharing_controller)
):
    """특정 데이터 공유 요청 조회"""
    return controller.get_sharing_request_by_id(request_id)

@sharing_router.get("/provider/{provider_company_id}", summary="협력사별 데이터 공유 요청 목록 조회")
async def get_sharing_requests_by_provider(
    provider_company_id: str,
    status: Optional[str] = None,
    controller: SharingController = Depends(get_sharing_controller)
):
    """협력사별 데이터 공유 요청 목록 조회"""
    return controller.get_sharing_requests_by_provider(provider_company_id, status)

@sharing_router.get("/requester/{requester_company_id}", summary="요청사별 데이터 공유 요청 목록 조회")
async def get_sharing_requests_by_requester(
    requester_company_id: str,
    status: Optional[str] = None,
    controller: SharingController = Depends(get_sharing_controller)
):
    """요청사별 데이터 공유 요청 목록 조회"""
    return controller.get_sharing_requests_by_requester(requester_company_id, status)

@sharing_router.get("/provider/{provider_company_id}/pending-count", summary="대기중인 요청 수 조회")
async def get_pending_requests_count(
    provider_company_id: str,
    controller: SharingController = Depends(get_sharing_controller)
):
    """대기중인 요청 수 조회"""
    return controller.get_pending_requests_count(provider_company_id)

@sharing_router.get("/stats/{company_id}", summary="데이터 공유 통계 조회")
async def get_sharing_stats(
    company_id: str,
    days: int = 30,
    controller: SharingController = Depends(get_sharing_controller)
):
    """데이터 공유 통계 조회"""
    return controller.get_sharing_stats(company_id, days)

@sharing_router.post("/", summary="새로운 데이터 공유 요청 생성")
async def create_sharing_request(
    request_data: SharingRequestCreate,
    controller: SharingController = Depends(get_sharing_controller)
):
    """새로운 데이터 공유 요청 생성"""
    return controller.create_sharing_request(request_data)

@sharing_router.put("/{request_id}/review", summary="데이터 공유 요청 검토")
async def review_sharing_request(
    request_id: str,
    review_data: ReviewRequest,
    controller: SharingController = Depends(get_sharing_controller)
):
    """데이터 공유 요청 검토 (승인/거부)"""
    return controller.review_sharing_request(request_id, review_data)

@sharing_router.put("/{request_id}/approve", summary="데이터 공유 요청 승인")
async def approve_sharing_request(
    request_id: str,
    reviewer_id: str,
    reviewer_name: str,
    comment: str = "",
    controller: SharingController = Depends(get_sharing_controller)
):
    """데이터 공유 요청 승인"""
    return controller.approve_sharing_request(request_id, reviewer_id, reviewer_name, comment)

@sharing_router.put("/{request_id}/reject", summary="데이터 공유 요청 거부")
async def reject_sharing_request(
    request_id: str,
    reviewer_id: str,
    reviewer_name: str,
    comment: str = "",
    controller: SharingController = Depends(get_sharing_controller)
):
    """데이터 공유 요청 거부"""
    return controller.reject_sharing_request(request_id, reviewer_id, reviewer_name, comment)

@sharing_router.post("/{request_id}/send", summary="승인된 데이터 전송")
async def send_approved_data(
    request_id: str,
    data_url: str,
    controller: SharingController = Depends(get_sharing_controller)
):
    """승인된 데이터 전송"""
    return controller.send_approved_data(request_id, data_url)

@sharing_router.get("/chain/{chain_level}", summary="특정 차수 협력사 체인 조회")
async def get_supplier_chain(
    chain_level: int,
    controller: SharingController = Depends(get_sharing_controller)
):
    """특정 차수 협력사 체인 조회"""
    return controller.get_supplier_chain(chain_level)

@sharing_router.get("/metrics", summary="서비스 메트릭 조회")
async def get_metrics(
    controller: SharingController = Depends(get_sharing_controller)
):
    """서비스 메트릭 조회"""
    return controller.get_metrics()

@sharing_router.put("/suppliers/{supplier_id}/strategic", summary="핵심 협력사 지정/해제")
async def toggle_strategic_supplier(
    supplier_id: str,
    is_strategic: bool,
    controller: SharingController = Depends(get_sharing_controller)
):
    """핵심 협력사 지정/해제"""
    return controller.toggle_strategic_supplier(supplier_id, is_strategic)

@sharing_router.get("/suppliers/strategic", summary="핵심 협력사 목록 조회")
async def get_strategic_suppliers(
    company_id: str,
    controller: SharingController = Depends(get_sharing_controller)
):
    """핵심 협력사 목록 조회"""
    return controller.get_strategic_suppliers(company_id)
