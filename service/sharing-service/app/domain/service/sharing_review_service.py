"""
Sharing Review Service - 데이터 공유 요청 검토 전용 서비스
"""
from typing import Optional, Dict
from datetime import datetime
import logging

from ..repository.sharing_repository import SharingRepository
from ..entity.sharing_entity import RequestStatus
from .interfaces import ISharingRequestReview

logger = logging.getLogger("sharing-review-service")


class SharingReviewService(ISharingRequestReview):
    """데이터 공유 요청 검토 서비스"""
    
    def __init__(self):
        self.repository = SharingRepository()
        self.db_available = True
        
        try:
            # 데이터베이스 연결 테스트
            self.repository.get_session()
        except Exception as e:
            logger.warning(f"⚠️ 데이터베이스 연결 실패, 모킹 모드로 동작: {e}")
            self.db_available = False
    
    def review_sharing_request(self, request_id: str, review_data: Dict) -> Optional[Dict]:
        """데이터 공유 요청 검토 (승인/거부)"""
        try:
            if not self.db_available:
                return self._mock_review_request(request_id, review_data)
            
            # 요청 존재 확인
            existing_request = self.repository.get_sharing_request_by_id(request_id)
            if not existing_request:
                logger.warning(f"⚠️ 존재하지 않는 요청: {request_id}")
                return None
            
            # 이미 검토된 요청인지 확인
            if existing_request.status != "pending":
                logger.warning(f"⚠️ 이미 검토된 요청: {request_id} (현재 상태: {existing_request.status})")
                return existing_request.to_dict()
            
            # 검토 데이터 검증
            validated_review = self._validate_review_data(review_data)
            
            # 상태 업데이트 데이터 준비
            update_data = {
                'reviewer_id': validated_review['reviewer_id'],
                'reviewer_name': validated_review['reviewer_name'],
                'review_comment': validated_review.get('review_comment', ''),
                'reviewed_at': datetime.utcnow()
            }
            
            # 액션에 따른 상태 설정
            if validated_review['action'] == 'approve':
                update_data['status'] = "approved"
                update_data['approved_at'] = datetime.utcnow()
            elif validated_review['action'] == 'reject':
                update_data['status'] = "rejected"
            else:
                raise ValueError(f"잘못된 액션: {validated_review['action']}")
            
            # 요청 업데이트
            updated_request = self.repository.update_sharing_request(request_id, update_data)
            
            if updated_request:
                logger.info(f"✅ 데이터 공유 요청 검토 완료: {request_id} - {validated_review['action']}")
                return updated_request.to_dict()
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 데이터 공유 요청 검토 실패: {e}")
            raise
    
    def approve_sharing_request(self, request_id: str, reviewer_id: str, reviewer_name: str, comment: str = "") -> Optional[Dict]:
        """데이터 공유 요청 승인"""
        review_data = {
            'reviewer_id': reviewer_id,
            'reviewer_name': reviewer_name,
            'review_comment': comment,
            'action': 'approve'
        }
        return self.review_sharing_request(request_id, review_data)
    
    def reject_sharing_request(self, request_id: str, reviewer_id: str, reviewer_name: str, comment: str = "") -> Optional[Dict]:
        """데이터 공유 요청 거부"""
        review_data = {
            'reviewer_id': reviewer_id,
            'reviewer_name': reviewer_name,
            'review_comment': comment,
            'action': 'reject'
        }
        return self.review_sharing_request(request_id, review_data)
    
    def _validate_review_data(self, review_data: Dict) -> Dict:
        """검토 데이터 검증"""
        required_fields = ['reviewer_id', 'reviewer_name', 'action']
        
        for field in required_fields:
            if field not in review_data or not review_data[field]:
                raise ValueError(f"필수 필드가 누락되었습니다: {field}")
        
        # 액션 검증
        valid_actions = ['approve', 'reject']
        if review_data['action'] not in valid_actions:
            raise ValueError(f"잘못된 액션: {review_data['action']}. 유효한 값: {valid_actions}")
        
        # 거부 시 의견 필수 확인 (선택적)
        if review_data['action'] == 'reject' and not review_data.get('review_comment'):
            logger.warning("⚠️ 거부 시 검토 의견이 없습니다.")
        
        return review_data
    
    def _get_review_history(self, request_id: str) -> list:
        """검토 이력 조회"""
        try:
            if not self.db_available:
                return []
            
            # TODO: 검토 이력 테이블이 있다면 조회
            # 현재는 단일 검토만 지원
            return []
            
        except Exception as e:
            logger.error(f"❌ 검토 이력 조회 실패: {e}")
            return []
    
    # Mock 메서드들
    def _mock_review_request(self, request_id: str, review_data: Dict) -> Dict:
        """모킹: 요청 검토"""
        mock_result = {
            "id": request_id,
            "status": "approved" if review_data['action'] == 'approve' else "rejected",
            "reviewer_id": review_data['reviewer_id'],
            "reviewer_name": review_data['reviewer_name'],
            "review_comment": review_data.get('review_comment', ''),
            "reviewed_at": datetime.utcnow().isoformat(),
            "approved_at": datetime.utcnow().isoformat() if review_data['action'] == 'approve' else None
        }
        
        logger.info(f"🔧 모킹 모드: 요청 검토 - {request_id} ({review_data['action']})")
        return mock_result
