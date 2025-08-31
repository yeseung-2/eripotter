"""
Sharing Controller - 데이터 공유 관련 컨트롤러
"""
from typing import Optional
import logging

from ..model.sharing_model import (
    SharingRequestCreate, ReviewRequest, ApiResponse
)

logger = logging.getLogger("sharing-controller")

class SharingController:
    def __init__(self, service):
        self.service = service

    def get_all_sharing_requests(self, limit: int = 100, offset: int = 0):
        """모든 데이터 공유 요청 목록 조회"""
        try:
            requests = self.service.get_all_sharing_requests(limit, offset)
            return ApiResponse(
                status="success",
                data={"requests": [req.dict() for req in requests], "count": len(requests)}
            ).dict()
        except Exception as e:
            logger.error(f"❌ 전체 요청 목록 조회 실패: {e}")
            return ApiResponse(status="error", error=str(e)).dict()

    def get_sharing_request_by_id(self, request_id: str):
        """특정 데이터 공유 요청 조회"""
        try:
            request = self.service.get_sharing_request_by_id(request_id)
            if request:
                return ApiResponse(status="success", data=request.dict()).dict()
            else:
                return ApiResponse(status="error", error="요청을 찾을 수 없습니다").dict()
        except Exception as e:
            logger.error(f"❌ 요청 조회 실패: {e}")
            return ApiResponse(status="error", error=str(e)).dict()

    def get_sharing_requests_by_provider(self, provider_company_id: str, status: Optional[str] = None):
        """협력사별 데이터 공유 요청 목록 조회"""
        try:
            requests = self.service.get_sharing_requests_by_provider(provider_company_id, status)
            return ApiResponse(
                status="success",
                data={"requests": requests, "count": len(requests)}
            ).dict()
        except Exception as e:
            logger.error(f"❌ 협력사별 요청 목록 조회 실패: {e}")
            return ApiResponse(status="error", error=str(e)).dict()

    def get_sharing_requests_by_requester(self, requester_company_id: str, status: Optional[str] = None):
        """요청사별 데이터 공유 요청 목록 조회"""
        try:
            requests = self.service.get_sharing_requests_by_requester(requester_company_id, status)
            return ApiResponse(
                status="success",
                data={"requests": requests, "count": len(requests)}
            ).dict()
        except Exception as e:
            logger.error(f"❌ 요청사별 요청 목록 조회 실패: {e}")
            return ApiResponse(status="error", error=str(e)).dict()

    def create_sharing_request(self, request_data: SharingRequestCreate):
        """데이터 공유 요청 생성"""
        try:
            # Pydantic 모델을 딕셔너리로 변환
            request_dict = request_data.dict()
            created_request = self.service.create_sharing_request(request_dict)
            return ApiResponse(
                status="success",
                message="데이터 공유 요청이 생성되었습니다",
                data=created_request
            ).dict()
        except Exception as e:
            logger.error(f"❌ 요청 생성 실패: {e}")
            return ApiResponse(status="error", error=str(e)).dict()

    def review_sharing_request(self, request_id: str, review_data: ReviewRequest):
        """데이터 공유 요청 검토"""
        try:
            reviewed_request = self.service.review_sharing_request(request_id, review_data)
            if reviewed_request:
                action_text = "승인" if review_data.action == "approve" else "거부"
                return ApiResponse(
                    status="success",
                    message=f"데이터 공유 요청이 {action_text}되었습니다",
                    data=reviewed_request.dict()
                ).dict()
            else:
                return ApiResponse(status="error", error="요청을 찾을 수 없습니다").dict()
        except Exception as e:
            logger.error(f"❌ 요청 검토 실패: {e}")
            return ApiResponse(status="error", error=str(e)).dict()

    def approve_sharing_request(self, request_id: str, reviewer_id: str, reviewer_name: str, comment: str = ""):
        """데이터 공유 요청 승인"""
        try:
            approved_request = self.service.approve_sharing_request(request_id, reviewer_id, reviewer_name, comment)
            if approved_request:
                return ApiResponse(
                    status="success",
                    message="데이터 공유 요청이 승인되었습니다",
                    data=approved_request.dict()
                ).dict()
            else:
                return ApiResponse(status="error", error="요청을 찾을 수 없습니다").dict()
        except Exception as e:
            logger.error(f"❌ 요청 승인 실패: {e}")
            return ApiResponse(status="error", error=str(e)).dict()

    def reject_sharing_request(self, request_id: str, reviewer_id: str, reviewer_name: str, comment: str = ""):
        """데이터 공유 요청 거부"""
        try:
            rejected_request = self.service.reject_sharing_request(request_id, reviewer_id, reviewer_name, comment)
            if rejected_request:
                return ApiResponse(
                    status="success",
                    message="데이터 공유 요청이 거부되었습니다",
                    data=rejected_request.dict()
                ).dict()
            else:
                return ApiResponse(status="error", error="요청을 찾을 수 없습니다").dict()
        except Exception as e:
            logger.error(f"❌ 요청 거부 실패: {e}")
            return ApiResponse(status="error", error=str(e)).dict()

    def send_approved_data(self, request_id: str, data_url: str):
        """승인된 데이터 전송"""
        try:
            completed_request = self.service.send_approved_data(request_id, data_url)
            if completed_request:
                return ApiResponse(
                    status="success",
                    message="데이터가 성공적으로 전송되었습니다",
                    data=completed_request.dict()
                ).dict()
            else:
                return ApiResponse(status="error", error="승인된 요청을 찾을 수 없습니다").dict()
        except Exception as e:
            logger.error(f"❌ 데이터 전송 실패: {e}")
            return ApiResponse(status="error", error=str(e)).dict()

    def get_pending_requests_count(self, provider_company_id: str):
        """대기중인 요청 수 조회"""
        try:
            count = self.service.get_pending_requests_count(provider_company_id)
            return ApiResponse(
                status="success",
                data={"pending_count": count}
            ).dict()
        except Exception as e:
            logger.error(f"❌ 대기중인 요청 수 조회 실패: {e}")
            return ApiResponse(status="error", error=str(e)).dict()

    def get_sharing_stats(self, company_id: str, days: int = 30):
        """데이터 공유 통계 조회"""
        try:
            stats = self.service.get_sharing_stats(company_id, days)
            return ApiResponse(
                status="success",
                data=stats
            ).dict()
        except Exception as e:
            logger.error(f"❌ 통계 조회 실패: {e}")
            return ApiResponse(status="error", error=str(e)).dict()

    def get_supplier_chain(self, parent_company_id: str, chain_level: Optional[int] = None):
        """협력사 체인 조회"""
        try:
            chains = self.service.get_supplier_chain(parent_company_id, chain_level)
            return ApiResponse(
                status="success",
                data={"chains": chains, "count": len(chains)}
            ).dict()
        except Exception as e:
            logger.error(f"❌ 협력사 체인 조회 실패: {e}")
            return ApiResponse(status="error", error=str(e)).dict()

    def get_metrics(self):
        """메트릭 조회"""
        try:
            metrics = self.service.get_metrics()
            return ApiResponse(status="success", data=metrics).dict()
        except Exception as e:
            logger.error(f"❌ 메트릭 조회 실패: {e}")
            return ApiResponse(status="error", error=str(e)).dict()

    def toggle_strategic_supplier(self, supplier_id: str, is_strategic: bool):
        """핵심 협력사 지정/해제"""
        try:
            result = self.service.toggle_strategic_supplier(supplier_id, is_strategic)
            return ApiResponse(
                status="success",
                data={"supplier_id": supplier_id, "is_strategic": is_strategic, "updated": result}
            ).dict()
        except Exception as e:
            logger.error(f"❌ 핵심 협력사 지정/해제 실패: {e}")
            return ApiResponse(status="error", error=str(e)).dict()

    def get_strategic_suppliers(self, company_id: str):
        """핵심 협력사 목록 조회"""
        try:
            suppliers = self.service.get_strategic_suppliers(company_id)
            return ApiResponse(
                status="success",
                data={"strategic_suppliers": suppliers}
            ).dict()
        except Exception as e:
            logger.error(f"❌ 핵심 협력사 목록 조회 실패: {e}")
            return ApiResponse(status="error", error=str(e)).dict()
    
    def get_companies(self):
        """전체 회사 목록 조회"""
        try:
            companies = self.service.get_companies()
            return ApiResponse(
                status="success",
                data={"companies": companies}
            ).dict()
        except Exception as e:
            logger.error(f"❌ 회사 목록 조회 실패: {e}")
            return ApiResponse(status="error", error=str(e)).dict()
