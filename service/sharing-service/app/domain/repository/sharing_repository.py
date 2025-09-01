"""
Sharing Repository - 데이터 공유 관련 데이터베이스 작업
"""
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, and_, or_, desc, text
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

# eripotter_common database import
from eripotter_common.database import engine

from ..entity.sharing_entity import Sharing, RequestStatus

logger = logging.getLogger("sharing-repository")

class SharingRepository:
    def __init__(self):
        # eripotter_common engine 사용
        self.engine = engine
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self):
        """데이터베이스 세션 생성"""
        return self.SessionLocal()
    
    def create_sharing_request(self, request_data: dict) -> Sharing:
        """데이터 공유 요청 생성 또는 업데이트"""
        session = self.get_session()
        try:
            # Pydantic 모델 필드를 Entity 필드로 매핑
            mapped_data = self._map_request_fields(request_data)
            
            # 기존 협력사 관계가 있는지 확인
            existing_sharing = session.query(Sharing).filter(
                Sharing.child_company_id == mapped_data["child_company_id"]
            ).first()
            
            if existing_sharing:
                # 기존 행에 데이터 요청 정보 업데이트
                for key, value in mapped_data.items():
                    if key not in ["id", "created_at"] and value is not None:
                        setattr(existing_sharing, key, value)
                
                session.commit()
                session.refresh(existing_sharing)
                logger.info(f"✅ 기존 협력사 관계에 데이터 요청 업데이트: {existing_sharing.request_id}")
                return existing_sharing
            else:
                # 새로운 협력사 관계 + 데이터 요청 생성
                sharing_request = Sharing(**mapped_data)
                session.add(sharing_request)
                session.commit()
                session.refresh(sharing_request)
                logger.info(f"✅ 새로운 데이터 공유 요청 생성: {sharing_request.request_id}")
                return sharing_request
                
        except Exception as e:
            session.rollback()
            logger.error(f"❌ 데이터 공유 요청 생성 실패: {e}")
            raise
        finally:
            session.close()
    
    def _map_request_fields(self, request_data: dict) -> dict:
        """Pydantic 모델 필드를 Entity 필드로 매핑"""
        import uuid
        from datetime import datetime
        
        mapped_data = {
            # 기본 필드 매핑
            "parent_company_id": request_data.get("requester_company_id"),
            "parent_company_name": request_data.get("requester_company_name"),
            "child_company_id": request_data.get("provider_company_id"),
            "child_company_name": request_data.get("provider_company_name"),
            
            # 데이터 요청 관련 필드
            "request_id": str(uuid.uuid4()),
            "data_type": self._map_data_type(request_data.get("data_type")),
            "data_category": request_data.get("data_category"),
            "data_description": request_data.get("data_description"),
            "requested_fields": request_data.get("requested_fields"),
            "purpose": request_data.get("purpose"),
            "usage_period": request_data.get("usage_period"),
            "urgency_level": request_data.get("urgency_level", "normal"),
            
            # 기본 상태 설정
            "status": "pending",
            "requested_at": datetime.utcnow(),
            
            # 협력사 관계 기본값
            "chain_level": 1,
            "relationship_type": "supplier",
            "is_strategic": False,
            "priority_level": "medium",  # DB enum에 맞는 소문자 값
            "risk_level": "medium",      # 기본 리스크 레벨
            "response_rate": 0,          # 기본 응답률
            "business_impact_score": 0,  # 기본 비즈니스 영향도
        }
        
        logger.info(f"🔄 필드 매핑 완료: {request_data.get('requester_company_id')} → {request_data.get('provider_company_id')}")
        return mapped_data
    
    def _map_data_type(self, pydantic_data_type: str) -> str:
        """Pydantic DataType을 Entity DataType으로 매핑"""
        mapping = {
            "sustainability": "sustainability_data",
            "financial": "financial_data", 
            "operational": "operational_data",
            "compliance": "compliance_data"
        }
        return mapping.get(pydantic_data_type, "sustainability_data")
    
    def get_sharing_request_by_id(self, request_id: str) -> Optional[Sharing]:
        """ID로 데이터 공유 요청 조회"""
        session = self.get_session()
        try:
            request = session.query(Sharing).filter(Sharing.request_id == request_id).first()
            return request
        except Exception as e:
            logger.error(f"❌ 데이터 공유 요청 조회 실패: {e}")
            raise
        finally:
            session.close()
    
    def get_sharing_requests_by_provider(self, child_company_id: str, status: Optional[RequestStatus] = None) -> List[Sharing]:
        """협력사별 데이터 공유 요청 목록 조회"""
        session = self.get_session()
        try:
            query = session.query(Sharing).filter(
                Sharing.child_company_id == child_company_id,
                Sharing.request_id.isnot(None)  # 요청 데이터가 있는 것만
            )
            
            if status:
                query = query.filter(Sharing.status == status)
            
            requests = query.order_by(desc(Sharing.requested_at)).all()
            return requests
        except Exception as e:
            logger.error(f"❌ 협력사별 데이터 공유 요청 조회 실패: {e}")
            raise
        finally:
            session.close()
    
    def get_sharing_requests_by_requester(self, requester_company_id: str, status: Optional[RequestStatus] = None) -> List[Sharing]:
        """요청사별 데이터 공유 요청 목록 조회"""
        session = self.get_session()
        try:
            query = session.query(Sharing).filter(
                Sharing.parent_company_id == requester_company_id,
                Sharing.request_id.isnot(None)  # 요청 데이터가 있는 것만
            )
            
            if status:
                query = query.filter(Sharing.status == status)
            
            requests = query.order_by(desc(Sharing.requested_at)).all()
            return requests
        except Exception as e:
            logger.error(f"❌ 요청사별 데이터 공유 요청 조회 실패: {e}")
            raise
        finally:
            session.close()
    
    def get_all_sharing_requests(self, limit: int = 100, offset: int = 0) -> List[Sharing]:
        """모든 데이터 공유 요청 목록 조회"""
        session = self.get_session()
        try:
            requests = session.query(Sharing)\
                .filter(Sharing.request_id.isnot(None))\
                .order_by(desc(Sharing.requested_at))\
                .limit(limit)\
                .offset(offset)\
                .all()
            return requests
        except Exception as e:
            logger.error(f"❌ 전체 데이터 공유 요청 조회 실패: {e}")
            raise
        finally:
            session.close()
    
    def update_sharing_request(self, request_id: str, update_data: dict) -> Optional[Sharing]:
        """데이터 공유 요청 업데이트"""
        session = self.get_session()
        try:
            request = session.query(Sharing).filter(Sharing.request_id == request_id).first()
            if not request:
                return None
            
            for key, value in update_data.items():
                if hasattr(request, key):
                    setattr(request, key, value)
            
            # 상태별 타임스탬프 업데이트
            if 'status' in update_data:
                if update_data['status'] == "approved":
                    request.approved_at = datetime.utcnow()
                elif update_data['status'] == "rejected":
                    request.reviewed_at = datetime.utcnow()
                elif update_data['status'] == "completed":
                    request.completed_at = datetime.utcnow()
            
            session.commit()
            session.refresh(request)
            logger.info(f"✅ 데이터 공유 요청 업데이트 완료: {request_id}")
            return request
        except Exception as e:
            session.rollback()
            logger.error(f"❌ 데이터 공유 요청 업데이트 실패: {e}")
            raise
        finally:
            session.close()
    
    def get_pending_requests_count(self, child_company_id: str) -> int:
        """대기중인 요청 수 조회"""
        session = self.get_session()
        try:
            count = session.query(Sharing)\
                .filter(and_(
                    Sharing.child_company_id == child_company_id,
                    Sharing.status == "pending"
                )).count()
            return count
        except Exception as e:
            logger.error(f"❌ 대기중인 요청 수 조회 실패: {e}")
            return 0
        finally:
            session.close()
    
    def get_sharing_stats(self, company_id: str, days: int = 30) -> dict:
        """데이터 공유 통계 조회"""
        session = self.get_session()
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # 전체 요청 수
            total_requests = session.query(Sharing)\
                .filter(and_(
                    Sharing.child_company_id == company_id,
                    Sharing.requested_at >= start_date
                )).count()
            
            # 상태별 요청 수
            pending_requests = session.query(Sharing)\
                .filter(and_(
                    Sharing.child_company_id == company_id,
                    Sharing.status == "pending",
                    Sharing.requested_at >= start_date
                )).count()
            
            approved_requests = session.query(Sharing)\
                .filter(and_(
                    Sharing.child_company_id == company_id,
                    Sharing.status == "approved",
                    Sharing.requested_at >= start_date
                )).count()
            
            rejected_requests = session.query(Sharing)\
                .filter(and_(
                    Sharing.child_company_id == company_id,
                    Sharing.status == "rejected",
                    Sharing.requested_at >= start_date
                )).count()
            
            completed_requests = session.query(Sharing)\
                .filter(and_(
                    Sharing.child_company_id == company_id,
                    Sharing.status == "completed",
                    Sharing.requested_at >= start_date
                )).count()
            
            return {
                "total_requests": total_requests,
                "pending_requests": pending_requests,
                "approved_requests": approved_requests,
                "rejected_requests": rejected_requests,
                "completed_requests": completed_requests,
                "avg_response_time_hours": 0.0  # TODO: 실제 응답 시간 계산
            }
        except Exception as e:
            logger.error(f"❌ 데이터 공유 통계 조회 실패: {e}")
            return {}
        finally:
            session.close()
    
    def get_company_chain(self, parent_company_id: str, chain_level: Optional[int] = None) -> List[Sharing]:
        """협력사 체인 조회 (sharing 테이블에서)"""
        session = self.get_session()
        try:
            # sharing 테이블에서 협력사 관계 조회
            query = session.query(Sharing).filter(Sharing.requester_company_id == parent_company_id)
            
            if chain_level:
                query = query.filter(Sharing.chain_level == chain_level)
            
            chains = query.order_by(Sharing.chain_level).all()
            return chains
        except Exception as e:
            logger.error(f"❌ 협력사 체인 조회 실패: {e}")
            raise
        finally:
            session.close()
    
    def update_strategic_supplier(self, supplier_id: str, is_strategic: bool) -> bool:
        """핵심 협력사 지정/해제"""
        session = self.get_session()
        try:
            # sharing 테이블에서 해당 협력사 관계 찾아서 업데이트
            sharing_record = session.query(Sharing).filter(
                Sharing.child_company_id == supplier_id
            ).first()
            
            if sharing_record:
                sharing_record.is_strategic = is_strategic
                session.commit()
                logger.info(f"✅ 핵심 협력사 상태 업데이트: {supplier_id} -> {is_strategic}")
                return True
            else:
                logger.warning(f"⚠️ 협력사 관계를 찾을 수 없음: {supplier_id}")
                return False
                
        except Exception as e:
            session.rollback()
            logger.error(f"❌ 핵심 협력사 상태 업데이트 실패: {e}")
            raise
        finally:
            session.close()
    
    def get_strategic_suppliers(self, company_id: str) -> List[Sharing]:
        """핵심 협력사 목록 조회"""
        session = self.get_session()
        try:
            suppliers = session.query(Sharing).filter(
                Sharing.requester_company_id == company_id,
                Sharing.is_strategic == True
            ).distinct(Sharing.child_company_id).all()
            
            return suppliers
            
        except Exception as e:
            logger.error(f"❌ 핵심 협력사 목록 조회 실패: {e}")
            raise
        finally:
            session.close()

    def get_companies(self) -> List[Dict]:
        """전체 회사 목록 조회"""
        session = self.get_session()
        try:
            logger.info("🔍 company 테이블에서 회사 목록 조회 시작")
            result = session.execute(text("""
                SELECT DISTINCT company_name, tier1 
                FROM company 
                ORDER BY company_name
            """))
            
            companies = []
            for row in result:
                company_data = {
                    "name": row[0],
                    "tier1": row[1] if row[1] else "LG에너지솔루션"
                }
                companies.append(company_data)
                logger.debug(f"📋 회사 추가: {company_data}")
            
            logger.info(f"✅ 회사 목록 조회 완료: {len(companies)}개")
            return companies
            
        except Exception as e:
            logger.error(f"❌ 회사 목록 조회 실패: {type(e).__name__}: {e}")
            logger.error(f"📍 오류 발생 위치: get_companies 메서드")
            # 빈 리스트 반환하는 대신 예외를 다시 발생시켜 상위에서 처리
            raise Exception(f"회사 목록 조회 중 오류 발생: {e}")
        finally:
            session.close()

    def get_sharing_statistics_by_company(self, company_name: str) -> Dict[str, Any]:
        """회사별 데이터 공유 통계 조회"""
        try:
            session = self.get_session()
            
            # 해당 회사가 provider인 요청들 조회
            provider_requests = session.query(Sharing).filter(
                Sharing.child_company_name == company_name
            ).all()
            
            # 통계 계산
            total_requests = len(provider_requests)
            approved_requests = len([req for req in provider_requests if req.status == RequestStatus.APPROVED])
            pending_requests = len([req for req in provider_requests if req.status == RequestStatus.PENDING])
            rejected_requests = len([req for req in provider_requests if req.status == RequestStatus.REJECTED])
            
            # 최근 공유 날짜 찾기
            approved_requests_with_date = [req for req in provider_requests if req.status == RequestStatus.APPROVED]
            last_shared = None
            if approved_requests_with_date:
                last_shared = max(req.updated_at for req in approved_requests_with_date)
            
            session.close()
            
            return {
                "totalRequests": total_requests,
                "approved": approved_requests,
                "pending": pending_requests,
                "rejected": rejected_requests,
                "lastShared": last_shared.strftime('%Y-%m-%d') if last_shared else datetime.now().strftime('%Y-%m-%d'),
                "approvalRate": round((approved_requests / total_requests * 100) if total_requests > 0 else 0, 2)
            }
            
        except Exception as e:
            logger.error(f"데이터 공유 통계 조회 실패 ({company_name}): {e}")
            return {
                "totalRequests": 0,
                "approved": 0,
                "pending": 0,
                "rejected": 0,
                "lastShared": datetime.now().strftime('%Y-%m-%d'),
                "approvalRate": 0
            }