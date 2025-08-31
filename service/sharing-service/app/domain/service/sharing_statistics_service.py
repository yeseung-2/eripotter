"""
Sharing Statistics Service - 데이터 공유 통계 전용 서비스
"""
from typing import Dict
from datetime import datetime, timedelta
import logging

from ..repository.sharing_repository import SharingRepository
from .interfaces import ISharingStatistics

logger = logging.getLogger("sharing-statistics-service")


class SharingStatisticsService(ISharingStatistics):
    """데이터 공유 통계 서비스"""
    
    def __init__(self):
        self.repository = SharingRepository()
        self.db_available = True
        
        try:
            # 데이터베이스 연결 테스트
            self.repository.get_session()
        except Exception as e:
            logger.warning(f"⚠️ 데이터베이스 연결 실패, 모킹 모드로 동작: {e}")
            self.db_available = False
    
    def get_sharing_stats(self, company_id: str, days: int = 30) -> Dict:
        """데이터 공유 통계 조회"""
        try:
            if not self.db_available:
                return self._mock_get_sharing_stats(company_id, days)
            
            stats_data = self.repository.get_sharing_stats(company_id, days)
            
            # 응답 시간 메트릭 추가
            response_metrics = self.calculate_response_time_metrics(company_id, days)
            stats_data.update(response_metrics)
            
            logger.info(f"✅ 데이터 공유 통계 조회 완료: {company_id} ({days}일)")
            return stats_data
            
        except Exception as e:
            logger.error(f"❌ 데이터 공유 통계 조회 실패: {e}")
            return self._mock_get_sharing_stats(company_id, days)
    
    def get_pending_requests_count(self, provider_company_id: str) -> int:
        """대기중인 요청 수 조회"""
        try:
            if not self.db_available:
                return self._mock_get_pending_count(provider_company_id)
            
            count = self.repository.get_pending_requests_count(provider_company_id)
            logger.info(f"✅ 대기중인 요청 수 조회: {provider_company_id} - {count}건")
            return count
            
        except Exception as e:
            logger.error(f"❌ 대기중인 요청 수 조회 실패: {e}")
            return 0
    
    def calculate_response_time_metrics(self, company_id: str, days: int = 30) -> Dict:
        """응답 시간 메트릭 계산"""
        try:
            if not self.db_available:
                return self._mock_response_time_metrics()
            
            # TODO: 실제 응답 시간 계산 로직 구현
            # 요청일시와 검토일시 차이 계산
            
            # 임시로 기본값 반환
            return {
                "avg_response_time_hours": 24.5,
                "median_response_time_hours": 18.0,
                "fastest_response_hours": 2.5,
                "slowest_response_hours": 72.0
            }
            
        except Exception as e:
            logger.error(f"❌ 응답 시간 메트릭 계산 실패: {e}")
            return self._mock_response_time_metrics()
    
    def get_company_performance_metrics(self, company_id: str, days: int = 30) -> Dict:
        """회사별 성과 메트릭 조회"""
        try:
            stats = self.get_sharing_stats(company_id, days)
            
            # 승인율 계산
            total_reviewed = stats.get('approved_requests', 0) + stats.get('rejected_requests', 0)
            approval_rate = (stats.get('approved_requests', 0) / total_reviewed * 100) if total_reviewed > 0 else 0
            
            # 완료율 계산
            completion_rate = (stats.get('completed_requests', 0) / stats.get('approved_requests', 1) * 100) if stats.get('approved_requests', 0) > 0 else 0
            
            performance_metrics = {
                "approval_rate_percent": round(approval_rate, 2),
                "completion_rate_percent": round(completion_rate, 2),
                "total_requests": stats.get('total_requests', 0),
                "response_efficiency": "높음" if stats.get('avg_response_time_hours', 48) < 24 else "보통" if stats.get('avg_response_time_hours', 48) < 48 else "낮음"
            }
            
            logger.info(f"✅ 회사별 성과 메트릭 조회 완료: {company_id}")
            return performance_metrics
            
        except Exception as e:
            logger.error(f"❌ 회사별 성과 메트릭 조회 실패: {e}")
            return {
                "approval_rate_percent": 0,
                "completion_rate_percent": 0,
                "total_requests": 0,
                "response_efficiency": "알 수 없음"
            }
    
    def get_data_type_distribution(self, company_id: str, days: int = 30) -> Dict:
        """데이터 타입별 요청 분포 조회"""
        try:
            if not self.db_available:
                return self._mock_data_type_distribution()
            
            # TODO: 실제 데이터 타입별 분포 계산
            return {
                "sustainability": 45,
                "financial": 25,
                "operational": 20,
                "compliance": 10
            }
            
        except Exception as e:
            logger.error(f"❌ 데이터 타입별 분포 조회 실패: {e}")
            return self._mock_data_type_distribution()
    
    # Mock 메서드들
    def _mock_get_sharing_stats(self, company_id: str, days: int) -> Dict:
        """모킹: 데이터 공유 통계"""
        mock_stats = {
            "total_requests": 15,
            "pending_requests": 3,
            "approved_requests": 8,
            "rejected_requests": 2,
            "completed_requests": 7,
            "avg_response_time_hours": 18.5
        }
        
        logger.info(f"🔧 모킹 모드: 데이터 공유 통계 - {company_id}")
        return mock_stats
    
    def _mock_get_pending_count(self, provider_company_id: str) -> int:
        """모킹: 대기중인 요청 수"""
        logger.info(f"🔧 모킹 모드: 대기중인 요청 수 - {provider_company_id}")
        return 3
    
    def _mock_response_time_metrics(self) -> Dict:
        """모킹: 응답 시간 메트릭"""
        return {
            "avg_response_time_hours": 24.5,
            "median_response_time_hours": 18.0,
            "fastest_response_hours": 2.5,
            "slowest_response_hours": 72.0
        }
    
    def _mock_data_type_distribution(self) -> Dict:
        """모킹: 데이터 타입별 분포"""
        return {
            "sustainability": 45,
            "financial": 25,
            "operational": 20,
            "compliance": 10
        }
