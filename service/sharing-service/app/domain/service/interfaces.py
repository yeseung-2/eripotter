"""
Sharing Service Interfaces - 데이터 공유 서비스 계약 정의
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime

from ..entity.sharing_entity import RequestStatus, DataType


class ISharingRequestManagement(ABC):
    """데이터 공유 요청 관리 서비스 인터페이스"""
    
    @abstractmethod
    def create_sharing_request(self, request_data: Dict) -> Dict:
        """데이터 공유 요청 생성"""
        pass
    
    @abstractmethod
    def get_sharing_request_by_id(self, request_id: str) -> Optional[Dict]:
        """ID로 데이터 공유 요청 조회"""
        pass
    
    @abstractmethod
    def get_sharing_requests_by_provider(self, provider_company_id: str, status: Optional[RequestStatus] = None) -> List[Dict]:
        """협력사별 데이터 공유 요청 목록 조회"""
        pass
    
    @abstractmethod
    def get_sharing_requests_by_requester(self, requester_company_id: str, status: Optional[RequestStatus] = None) -> List[Dict]:
        """요청사별 데이터 공유 요청 목록 조회"""
        pass
    
    @abstractmethod
    def get_all_sharing_requests(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """모든 데이터 공유 요청 목록 조회"""
        pass


class ISharingRequestReview(ABC):
    """데이터 공유 요청 검토 서비스 인터페이스"""
    
    @abstractmethod
    def review_sharing_request(self, request_id: str, review_data: Dict) -> Optional[Dict]:
        """데이터 공유 요청 검토 (승인/거부)"""
        pass
    
    @abstractmethod
    def approve_sharing_request(self, request_id: str, reviewer_id: str, reviewer_name: str, comment: str = "") -> Optional[Dict]:
        """데이터 공유 요청 승인"""
        pass
    
    @abstractmethod
    def reject_sharing_request(self, request_id: str, reviewer_id: str, reviewer_name: str, comment: str = "") -> Optional[Dict]:
        """데이터 공유 요청 거부"""
        pass


class ISharingDataTransfer(ABC):
    """데이터 전송 서비스 인터페이스"""
    
    @abstractmethod
    def send_approved_data(self, request_id: str, data_url: str) -> Optional[Dict]:
        """승인된 데이터 전송"""
        pass
    
    @abstractmethod
    def generate_data_download_url(self, request_id: str, data_content: bytes) -> str:
        """데이터 다운로드 URL 생성"""
        pass
    
    @abstractmethod
    def validate_data_access(self, request_id: str, user_id: str) -> bool:
        """데이터 접근 권한 검증"""
        pass


class ISharingStatistics(ABC):
    """데이터 공유 통계 서비스 인터페이스"""
    
    @abstractmethod
    def get_sharing_stats(self, company_id: str, days: int = 30) -> Dict:
        """데이터 공유 통계 조회"""
        pass
    
    @abstractmethod
    def get_pending_requests_count(self, provider_company_id: str) -> int:
        """대기중인 요청 수 조회"""
        pass
    
    @abstractmethod
    def calculate_response_time_metrics(self, company_id: str, days: int = 30) -> Dict:
        """응답 시간 메트릭 계산"""
        pass


class ICompanyChainManagement(ABC):
    """협력사 체인 관리 서비스 인터페이스"""
    
    @abstractmethod
    def get_supplier_chain(self, parent_company_id: str, chain_level: Optional[int] = None) -> List[Dict]:
        """협력사 체인 조회"""
        pass
    
    @abstractmethod
    def add_company_to_chain(self, parent_company_id: str, child_company_id: str, chain_level: int) -> bool:
        """협력사 체인에 회사 추가"""
        pass
    
    @abstractmethod
    def remove_company_from_chain(self, parent_company_id: str, child_company_id: str) -> bool:
        """협력사 체인에서 회사 제거"""
        pass


class ISharingRepository(ABC):
    """데이터 공유 저장소 인터페이스"""
    
    @abstractmethod
    def save_sharing_request(self, request_data: Dict) -> bool:
        """데이터 공유 요청 저장"""
        pass
    
    @abstractmethod
    def update_sharing_request(self, request_id: str, update_data: Dict) -> bool:
        """데이터 공유 요청 업데이트"""
        pass
    
    @abstractmethod
    def save_review_history(self, request_id: str, review_data: Dict) -> bool:
        """검토 이력 저장"""
        pass
    
    @abstractmethod
    def get_audit_trail(self, request_id: str) -> List[Dict]:
        """감사 추적 정보 조회"""
        pass


class ISharingNotification(ABC):
    """데이터 공유 알림 서비스 인터페이스"""
    
    @abstractmethod
    def send_request_notification(self, request_id: str, provider_company_id: str) -> bool:
        """요청 알림 전송"""
        pass
    
    @abstractmethod
    def send_approval_notification(self, request_id: str, requester_company_id: str) -> bool:
        """승인 알림 전송"""
        pass
    
    @abstractmethod
    def send_rejection_notification(self, request_id: str, requester_company_id: str, reason: str) -> bool:
        """거부 알림 전송"""
        pass
    
    @abstractmethod
    def send_data_ready_notification(self, request_id: str, requester_company_id: str, download_url: str) -> bool:
        """데이터 준비 완료 알림 전송"""
        pass


class ISharingValidation(ABC):
    """데이터 공유 검증 서비스 인터페이스"""
    
    @abstractmethod
    def validate_request_data(self, request_data: Dict) -> Dict:
        """요청 데이터 검증"""
        pass
    
    @abstractmethod
    def validate_company_relationship(self, requester_id: str, provider_id: str) -> bool:
        """회사 간 관계 검증"""
        pass
    
    @abstractmethod
    def validate_data_access_permission(self, company_id: str, data_type: DataType) -> bool:
        """데이터 접근 권한 검증"""
        pass
    
    @abstractmethod
    def sanitize_sensitive_data(self, data: Dict) -> Dict:
        """민감 데이터 마스킹"""
        pass
