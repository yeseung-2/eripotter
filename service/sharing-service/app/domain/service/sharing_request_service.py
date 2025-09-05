"""
Sharing Request Service - 데이터 공유 요청 관리 전용 서비스
"""
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import logging

from ..repository.sharing_repository import SharingRepository
from ..entity.sharing_entity import RequestStatus, DataType, Sharing
from .interfaces import ISharingRequestManagement

logger = logging.getLogger("sharing-request-service")


class SharingRequestService(ISharingRequestManagement):
    """데이터 공유 요청 관리 서비스"""
    
    def __init__(self):
        self.repository = SharingRepository()
        self.db_available = True
        
        try:
            # 데이터베이스 연결 테스트
            self.repository.get_session()
        except Exception as e:
            logger.warning(f"⚠️ 데이터베이스 연결 실패, 모킹 모드로 동작: {e}")
            self.db_available = False
    
    def create_sharing_request(self, request_data: Dict) -> Dict:
        """데이터 공유 요청 생성"""
        try:
            if not self.db_available:
                return self._mock_create_request(request_data)
            
            # 요청 데이터 검증
            validated_data = self._validate_request_data(request_data)
            
            # 요청 생성
            created_request = self.repository.create_sharing_request(validated_data)
            
            logger.info(f"✅ 데이터 공유 요청 생성 완료: {created_request.id}")
            return created_request.to_dict()
            
        except Exception as e:
            logger.error(f"❌ 데이터 공유 요청 생성 실패: {e}")
            raise
    
    def get_sharing_request_by_id(self, request_id: str) -> Optional[Dict]:
        """ID로 데이터 공유 요청 조회"""
        try:
            if not self.db_available:
                return self._mock_get_request_by_id(request_id)
            
            request = self.repository.get_sharing_request_by_id(request_id)
            return request.to_dict() if request else None
            
        except Exception as e:
            logger.error(f"❌ 데이터 공유 요청 조회 실패: {e}")
            raise
    
    def get_sharing_requests_by_provider(self, provider_company_id: str, status: Optional[RequestStatus] = None) -> List[Dict]:
        """협력사별 데이터 공유 요청 목록 조회"""
        try:
            if not self.db_available:
                return self._mock_get_requests_by_provider(provider_company_id, status)
            
            requests = self.repository.get_sharing_requests_by_provider(provider_company_id, status)
            return [request.to_dict() for request in requests]
            
        except Exception as e:
            logger.error(f"❌ 협력사별 데이터 공유 요청 조회 실패: {e}")
            raise
    
    def get_sharing_requests_by_requester(self, requester_company_id: str, status: Optional[RequestStatus] = None) -> List[Dict]:
        """요청사별 데이터 공유 요청 목록 조회"""
        try:
            if not self.db_available:
                return self._mock_get_requests_by_requester(requester_company_id, status)
            
            requests = self.repository.get_sharing_requests_by_requester(requester_company_id, status)
            return [request.to_dict() for request in requests]
            
        except Exception as e:
            logger.error(f"❌ 요청사별 데이터 공유 요청 조회 실패: {e}")
            raise
    
    def get_all_sharing_requests(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """모든 데이터 공유 요청 목록 조회"""
        try:
            if not self.db_available:
                return self._mock_get_all_requests(limit, offset)
            
            requests = self.repository.get_all_sharing_requests(limit, offset)
            return [request.to_dict() for request in requests]
            
        except Exception as e:
            logger.error(f"❌ 전체 데이터 공유 요청 조회 실패: {e}")
            raise
    
    def _validate_request_data(self, request_data: Dict) -> Dict:
        """요청 데이터 검증"""
        required_fields = [
            'requester_company_id', 'requester_company_name',
            'provider_company_id', 'provider_company_name',
            'data_type', 'data_category', 'data_description', 'purpose'
        ]
        
        for field in required_fields:
            if field not in request_data or not request_data[field]:
                raise ValueError(f"필수 필드가 누락되었습니다: {field}")
        
        # 데이터 타입 검증 (Pydantic DataType 값들로 검증)
        valid_data_types = ["sustainability", "financial", "operational", "compliance"]
        if request_data['data_type'] not in valid_data_types:
            raise ValueError(f"잘못된 데이터 타입: {request_data['data_type']}")
        
        # 기본값 설정
        request_data.setdefault('urgency_level', 'normal')
        request_data.setdefault('requested_at', datetime.utcnow())
        
        return request_data
    
    # Mock 메서드들 (데이터베이스 연결 실패 시 사용)
    def _mock_create_request(self, request_data: Dict) -> Dict:
        """모킹: 요청 생성"""
        import uuid
        mock_request = {
            "id": str(uuid.uuid4()),
            "status": "pending",
            "requested_at": datetime.utcnow().isoformat(),
            **request_data
        }
        logger.info(f"🔧 모킹 모드: 데이터 공유 요청 생성 - {mock_request['id']}")
        return mock_request
    
    def _mock_get_request_by_id(self, request_id: str) -> Dict:
        """모킹: ID로 요청 조회"""
        mock_request = {
            "id": request_id,
            "requester_company_name": "원청사 A",
            "provider_company_name": "협력사 A",
            "data_type": "sustainability",
            "data_category": "탄소 배출량 데이터",
            "data_description": "2023년 Scope 1,2,3 탄소 배출량 데이터",
            "purpose": "지속가능성 보고서 작성",
            "status": "pending",
            "urgency_level": "normal",
            "requested_at": datetime.utcnow().isoformat()
        }
        logger.info(f"🔧 모킹 모드: 요청 조회 - {request_id}")
        return mock_request
    
    def _mock_get_requests_by_provider(self, provider_company_id: str, status: Optional[RequestStatus]) -> List[Dict]:
        """모킹: 협력사별 요청 목록"""
        mock_requests = [
            {
                "id": "mock-request-1",
                "requester_company_name": "원청사 A",
                "provider_company_name": "협력사 A",
                "data_type": "sustainability",
                "data_category": "탄소 배출량 데이터",
                "purpose": "지속가능성 보고서 작성",
                "status": "pending",
                "urgency_level": "high",
                "requested_at": datetime.utcnow().isoformat()
            },
            {
                "id": "mock-request-2",
                "requester_company_name": "원청사 A",
                "provider_company_name": "협력사 A",
                "data_type": "operational",
                "data_category": "생산량 데이터",
                "purpose": "공급망 효율성 분석",
                "status": "approved",
                "urgency_level": "normal",
                "requested_at": (datetime.utcnow() - timedelta(days=1)).isoformat()
            }
        ]
        
        if status:
            mock_requests = [req for req in mock_requests if req['status'] == status.value]
        
        logger.info(f"🔧 모킹 모드: 협력사별 요청 목록 - {provider_company_id}")
        return mock_requests
    
    def _mock_get_requests_by_requester(self, requester_company_id: str, status: Optional[RequestStatus]) -> List[Dict]:
        """모킹: 요청사별 요청 목록"""
        mock_requests = [
            {
                "id": "mock-request-3",
                "requester_company_name": "협력사 A",
                "provider_company_name": "협력사 C",
                "data_type": "compliance",
                "data_category": "인증 현황",
                "purpose": "2차 협력사 컴플라이언스 모니터링",
                "status": "completed",
                "urgency_level": "low",
                "requested_at": (datetime.utcnow() - timedelta(days=3)).isoformat(),
                "data_url": "https://mock-data.example.com/download/mock-request-3"
            }
        ]
        
        if status:
            mock_requests = [req for req in mock_requests if req['status'] == status.value]
        
        logger.info(f"🔧 모킹 모드: 요청사별 요청 목록 - {requester_company_id}")
        return mock_requests
    
    def _mock_get_all_requests(self, limit: int, offset: int) -> List[Dict]:
        """모킹: 전체 요청 목록"""
        all_mock_requests = [
            {
                "id": "mock-request-1",
                "requester_company_name": "원청사 A",
                "provider_company_name": "협력사 A",
                "data_type": "sustainability",
                "status": "pending",
                "requested_at": datetime.utcnow().isoformat()
            },
            {
                "id": "mock-request-2", 
                "requester_company_name": "원청사 A",
                "provider_company_name": "협력사 B",
                "data_type": "financial",
                "status": "approved",
                "requested_at": (datetime.utcnow() - timedelta(days=1)).isoformat()
            }
        ]
        
        logger.info(f"🔧 모킹 모드: 전체 요청 목록 - limit: {limit}, offset: {offset}")
        return all_mock_requests[offset:offset+limit]
