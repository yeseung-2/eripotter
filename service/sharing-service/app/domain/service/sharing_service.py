"""
Sharing Service - 통합 데이터 공유 서비스 
프론트엔드 데이터 공유 요청 + AI 기반 매칭 + 사용자 검토
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from ..repository.sharing_repository import SharingRepository
from ..entity.sharing_entity import RequestStatus, DataType
from ..model.sharing_model import (
    SharingRequestCreate, SharingRequestResponse, 
    ReviewRequest, DataSharingStats, ApiResponse
)

# 개별 서비스 클래스들 import
from .sharing_request_service import SharingRequestService
from .sharing_review_service import SharingReviewService
from .sharing_statistics_service import SharingStatisticsService

# 인터페이스들 import
from .interfaces import (
    ISharingRequestManagement, ISharingRequestReview, 
    ISharingStatistics, ISharingDataTransfer
)

logger = logging.getLogger("sharing-service")

class SharingService(ISharingRequestManagement, ISharingRequestReview, ISharingStatistics, ISharingDataTransfer):
    """통합 Sharing 서비스 - Normal Service 구조 적용"""
    
    def __init__(self):
        # 데이터베이스 연결을 선택적으로 시도
        self.repository = None
        self.db_available = False
        
        try:
            self.repository = SharingRepository()
            self.repository.get_session()  # 연결 테스트
            self.db_available = True
            logger.info("✅ 데이터베이스 연결 성공")
        except Exception as e:
            logger.warning(f"⚠️ 데이터베이스 연결 실패, 모킹 모드로 동작: {e}")
            self.db_available = False
        
        # 개별 서비스 인스턴스 생성
        self.request_service = SharingRequestService()
        self.review_service = SharingReviewService()
        self.statistics_service = SharingStatisticsService()
        
        logger.info("🚀 Sharing Service 초기화 완료")

    # ISharingRequestManagement 인터페이스 구현 - 개별 서비스로 위임
    def get_all_sharing_requests(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """모든 데이터 공유 요청 목록 조회"""
        return self.request_service.get_all_sharing_requests(limit, offset)

    def get_sharing_request_by_id(self, request_id: str) -> Optional[Dict]:
        """특정 데이터 공유 요청 조회"""
        return self.request_service.get_sharing_request_by_id(request_id)

    def get_sharing_requests_by_provider(self, provider_company_id: str, status: Optional[RequestStatus] = None) -> List[Dict]:
        """협력사별 데이터 공유 요청 목록 조회"""
        return self.request_service.get_sharing_requests_by_provider(provider_company_id, status)

    def get_sharing_requests_by_requester(self, requester_company_id: str, status: Optional[RequestStatus] = None) -> List[Dict]:
        """요청사별 데이터 공유 요청 목록 조회"""
        return self.request_service.get_sharing_requests_by_requester(requester_company_id, status)

    def create_sharing_request(self, request_data: Dict) -> Dict:
        """데이터 공유 요청 생성"""
        return self.request_service.create_sharing_request(request_data)

    # ISharingRequestReview 인터페이스 구현 - 개별 서비스로 위임
    def review_sharing_request(self, request_id: str, review_data: Dict) -> Optional[Dict]:
        """데이터 공유 요청 검토 (승인/거부)"""
        return self.review_service.review_sharing_request(request_id, review_data)

    def approve_sharing_request(self, request_id: str, reviewer_id: str, reviewer_name: str, comment: str = "") -> Optional[Dict]:
        """데이터 공유 요청 승인"""
        return self.review_service.approve_sharing_request(request_id, reviewer_id, reviewer_name, comment)

    def reject_sharing_request(self, request_id: str, reviewer_id: str, reviewer_name: str, comment: str = "") -> Optional[Dict]:
        """데이터 공유 요청 거부"""
        return self.review_service.reject_sharing_request(request_id, reviewer_id, reviewer_name, comment)

    # ISharingStatistics 인터페이스 구현 - 개별 서비스로 위임
    def get_sharing_stats(self, company_id: str, days: int = 30) -> Dict:
        """데이터 공유 통계 조회"""
        return self.statistics_service.get_sharing_stats(company_id, days)

    def get_pending_requests_count(self, provider_company_id: str) -> int:
        """대기중인 요청 수 조회"""
        return self.statistics_service.get_pending_requests_count(provider_company_id)

    def calculate_response_time_metrics(self, company_id: str, days: int = 30) -> Dict:
        """응답 시간 메트릭 계산"""
        return self.statistics_service.calculate_response_time_metrics(company_id, days)

    # ISharingDataTransfer 인터페이스 구현
    def send_approved_data(self, request_id: str, data_url: str) -> Optional[Dict]:
        """승인된 데이터 전송"""
        try:
            if not self.db_available:
                return self._mock_send_approved_data(request_id, data_url)
            
                        # 승인된 요청인지 확인
            existing_request = self.repository.get_sharing_request_by_id(request_id)
            if not existing_request or existing_request.status != "approved":
                return None

            # 데이터 URL 및 완료 상태 업데이트
            update_data = {
                'status': "completed",
                'data_url': data_url,
                'completed_at': datetime.utcnow(),
                'expiry_date': datetime.utcnow().replace(hour=23, minute=59, second=59)  # 당일 만료
            }
            
            updated_request = self.repository.update_sharing_request(request_id, update_data)
            
            if updated_request:
                logger.info(f"✅ 데이터 전송 완료: {request_id}")
                return updated_request.to_dict()
            
            return None
        except Exception as e:
            logger.error(f"❌ 데이터 전송 실패: {e}")
            raise

    def generate_data_download_url(self, request_id: str, data_content: bytes) -> str:
        """데이터 다운로드 URL 생성"""
        # TODO: 실제 파일 저장 및 URL 생성 로직
        return f"https://data.example.com/download/{request_id}"

    def validate_data_access(self, request_id: str, user_id: str) -> bool:
        """데이터 접근 권한 검증"""
        # TODO: 실제 권한 검증 로직
        return True

    # 추가 유틸리티 메서드들
    def get_supplier_chain(self, parent_company_id: str, chain_level: Optional[int] = None):
        """협력사 체인 조회"""
        try:
            if not self.db_available:
                return self._mock_get_supplier_chain(parent_company_id, chain_level)
            
            chains = self.repository.get_company_chain(parent_company_id, chain_level)
            return [chain.to_dict() for chain in chains]
        except Exception as e:
            logger.error(f"❌ 협력사 체인 조회 실패: {e}")
            return []

    def get_metrics(self):
        """서비스 메트릭 조회"""
        try:
            return {
                "service": "sharing-service",
                "status": "healthy" if self.db_available else "degraded",
                "db_available": self.db_available,
                "timestamp": datetime.utcnow().isoformat(),
                "components": {
                    "request_service": "active",
                    "review_service": "active", 
                    "statistics_service": "active"
                }
            }
        except Exception as e:
            logger.error(f"❌ 메트릭 조회 실패: {e}")
            return {"service": "sharing-service", "status": "error", "error": str(e)}

    # 레거시 호환성을 위한 래퍼 메서드들
    def get_all_sharing_requests_legacy(self, limit: int = 100, offset: int = 0) -> List[SharingRequestResponse]:
        """레거시 호환성: 모든 데이터 공유 요청 목록 조회"""
        requests_data = self.get_all_sharing_requests(limit, offset)
        return [SharingRequestResponse(**req) for req in requests_data]

    def get_sharing_request_by_id_legacy(self, request_id: str) -> Optional[SharingRequestResponse]:
        """레거시 호환성: 특정 데이터 공유 요청 조회"""
        request_data = self.get_sharing_request_by_id(request_id)
        return SharingRequestResponse(**request_data) if request_data else None

    def create_sharing_request_legacy(self, request_data: SharingRequestCreate) -> SharingRequestResponse:
        """레거시 호환성: 데이터 공유 요청 생성"""
        request_dict = request_data.dict()
        created_data = self.create_sharing_request(request_dict)
        return SharingRequestResponse(**created_data)

    def get_sharing_stats_legacy(self, company_id: str, days: int = 30) -> DataSharingStats:
        """레거시 호환성: 데이터 공유 통계 조회"""
        stats_data = self.get_sharing_stats(company_id, days)
        return DataSharingStats(**stats_data)

    # Mock 메서드들
    def _mock_send_approved_data(self, request_id: str, data_url: str) -> Dict:
        """모킹: 승인된 데이터 전송"""
        mock_result = {
            "id": request_id,
            "status": "completed",
            "data_url": data_url,
            "completed_at": datetime.utcnow().isoformat(),
            "expiry_date": datetime.utcnow().replace(hour=23, minute=59, second=59).isoformat()
        }
        logger.info(f"🔧 모킹 모드: 데이터 전송 - {request_id}")
        return mock_result

    def _mock_get_supplier_chain(self, parent_company_id: str, chain_level: Optional[int]) -> List[Dict]:
        """모킹: 협력사 체인 조회"""
        mock_chains = [
            {
                "id": "chain-1",
                "parent_company_id": parent_company_id,
                "child_company_id": "COMPANY_003",
                "child_company_name": "협력사 C",
                "chain_level": 2,
                "relationship_type": "supplier"
            },
            {
                "id": "chain-2",
                "parent_company_id": parent_company_id,
                "child_company_id": "COMPANY_004", 
                "child_company_name": "협력사 D",
                "chain_level": 2,
                "relationship_type": "supplier"
            }
        ]
        
        if chain_level:
            mock_chains = [chain for chain in mock_chains if chain['chain_level'] == chain_level]
        
        logger.info(f"🔧 모킹 모드: 협력사 체인 조회 - {parent_company_id}")
        return mock_chains

    def toggle_strategic_supplier(self, supplier_id: str, is_strategic: bool) -> bool:
        """핵심 협력사 지정/해제"""
        try:
            if not self.db_available:
                return self._mock_toggle_strategic_supplier(supplier_id, is_strategic)
            
            # DB에서 해당 협력사 관계 찾기 및 업데이트
            result = self.repository.update_strategic_supplier(supplier_id, is_strategic)
            
            logger.info(f"✅ 핵심 협력사 {'지정' if is_strategic else '해제'} 완료: {supplier_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 핵심 협력사 지정/해제 실패: {e}")
            return False

    def get_strategic_suppliers(self, company_id: str) -> List[Dict]:
        """핵심 협력사 목록 조회"""
        try:
            if not self.db_available:
                return self._mock_get_strategic_suppliers(company_id)
            
            suppliers = self.repository.get_strategic_suppliers(company_id)
            return [supplier.to_dict() for supplier in suppliers]
            
        except Exception as e:
            logger.error(f"❌ 핵심 협력사 목록 조회 실패: {e}")
            return []

    def _mock_toggle_strategic_supplier(self, supplier_id: str, is_strategic: bool) -> bool:
        """모킹: 핵심 협력사 지정/해제"""
        # 실제로는 성공한 것처럼 반환
        logger.info(f"🎭 Mock: 핵심 협력사 {'지정' if is_strategic else '해제'} - {supplier_id}")
        return True

    def _mock_get_strategic_suppliers(self, company_id: str) -> List[Dict]:
        """모킹: 핵심 협력사 목록 조회"""
        mock_suppliers = [
            {
                "id": "supplier-001",
                "provider_company_id": "SUPPLIER_001",
                "provider_company_name": "LG에너지솔루션",
                "is_strategic": True,
                "created_at": "2024-01-15T09:00:00Z"
            },
            {
                "id": "supplier-002", 
                "provider_company_id": "SUPPLIER_002",
                "provider_company_name": "SK온",
                "is_strategic": True,
                "created_at": "2024-01-20T14:30:00Z"
            }
        ]
        logger.info(f"🎭 Mock: 핵심 협력사 목록 조회 - {company_id}")
        return mock_suppliers

    def get_companies(self) -> List[Dict]:
        """전체 회사 목록 조회"""
        try:
            logger.info("🔄 Service: Repository에서 회사 목록 조회 시작")
            companies = self.repository.get_companies()
            logger.info(f"✅ Service: 회사 목록 조회 성공 - {len(companies)}개")
            return companies
        except Exception as e:
            logger.error(f"❌ Service: 회사 목록 조회 실패 - {type(e).__name__}: {e}")
            # 빈 리스트 대신 예외를 다시 발생시켜서 Controller에서 error 응답 생성
            raise Exception(f"회사 목록 조회 중 서비스 레벨 오류: {e}")