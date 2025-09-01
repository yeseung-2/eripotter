"""
Normal Repository - Normal 테이블 전용 Repository
ESG 원본 데이터 관리
"""
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import text

# eripotter_common database import
from eripotter_common.database import engine

# Entity import
from ..entity import NormalEntity

logger = logging.getLogger("normal-repository")

class NormalRepository:
    def __init__(self):
        self.engine = engine
        self.Session = sessionmaker(bind=engine)
    
    def create(self, substance_data: Dict[str, Any]) -> Optional[NormalEntity]:
        """새로운 Normal 데이터 생성"""
        try:
            session = self.Session()
            
            normal_entity = NormalEntity(**substance_data)
            session.add(normal_entity)
            session.commit()
            
            # 생성된 객체 반환 (ID 포함)
            session.refresh(normal_entity)
            result = normal_entity
            session.close()
            
            logger.info(f"✅ Normal 데이터 생성 완료: ID {result.id}")
            return result
            
        except SQLAlchemyError as e:
            if 'session' in locals():
                session.rollback()
                session.close()
            logger.error(f"❌ Normal 데이터 생성 실패: {e}")
            return None
    
    def get_by_id(self, normal_id: int) -> Optional[NormalEntity]:
        """ID로 Normal 데이터 조회"""
        try:
            session = self.Session()
            
            result = session.query(NormalEntity).filter_by(id=normal_id).first()
            session.close()
            
            return result
            
        except SQLAlchemyError as e:
            if 'session' in locals():
                session.close()
            logger.error(f"❌ Normal 데이터 조회 실패 (ID: {normal_id}): {e}")
            return None
    
    def get_by_company(self, company_id: str, limit: int = 10, offset: int = 0) -> List[NormalEntity]:
        """회사별 Normal 데이터 조회"""
        try:
            session = self.Session()
            
            results = session.query(NormalEntity)\
                .filter_by(company_id=company_id)\
                .order_by(NormalEntity.created_at.desc())\
                .limit(limit)\
                .offset(offset)\
                .all()
            
            session.close()
            return results
            
        except SQLAlchemyError as e:
            if 'session' in locals():
                session.close()
            logger.error(f"❌ 회사별 Normal 데이터 조회 실패 (company_id: {company_id}): {e}")
            return []
    
    def get_all(self, limit: int = 50, offset: int = 0) -> List[NormalEntity]:
        """모든 Normal 데이터 조회"""
        try:
            session = self.Session()
            
            results = session.query(NormalEntity)\
                .order_by(NormalEntity.created_at.desc())\
                .limit(limit)\
                .offset(offset)\
                .all()
            
            session.close()
            return results
            
        except SQLAlchemyError as e:
            if 'session' in locals():
                session.close()
            logger.error(f"❌ 전체 Normal 데이터 조회 실패: {e}")
            return []
    
    def update(self, normal_id: int, update_data: Dict[str, Any]) -> bool:
        """Normal 데이터 업데이트"""
        try:
            session = self.Session()
            
            normal_entity = session.query(NormalEntity).filter_by(id=normal_id).first()
            
            if not normal_entity:
                logger.error(f"❌ Normal ID {normal_id}를 찾을 수 없습니다.")
                session.close()
                return False
            
            # 업데이트 데이터 적용
            for key, value in update_data.items():
                if hasattr(normal_entity, key):
                    setattr(normal_entity, key, value)
            
            normal_entity.updated_at = datetime.now()
            session.commit()
            session.close()
            
            logger.info(f"✅ Normal 데이터 업데이트 완료: ID {normal_id}")
            return True
            
        except SQLAlchemyError as e:
            if 'session' in locals():
                session.rollback()
                session.close()
            logger.error(f"❌ Normal 데이터 업데이트 실패 (ID: {normal_id}): {e}")
            return False
    
    def delete(self, normal_id: int) -> bool:
        """Normal 데이터 삭제"""
        try:
            session = self.Session()
            
            normal_entity = session.query(NormalEntity).filter_by(id=normal_id).first()
            
            if not normal_entity:
                logger.error(f"❌ Normal ID {normal_id}를 찾을 수 없습니다.")
                session.close()
                return False
            
            session.delete(normal_entity)
            session.commit()
            session.close()
            
            logger.info(f"✅ Normal 데이터 삭제 완료: ID {normal_id}")
            return True
            
        except SQLAlchemyError as e:
            if 'session' in locals():
                session.rollback()
                session.close()
            logger.error(f"❌ Normal 데이터 삭제 실패 (ID: {normal_id}): {e}")
            return False
    
    def count_by_company(self, company_id: str) -> int:
        """회사별 데이터 개수 조회"""
        try:
            session = self.Session()
            
            count = session.query(NormalEntity).filter_by(company_id=company_id).count()
            session.close()
            
            return count
            
        except SQLAlchemyError as e:
            if 'session' in locals():
                session.close()
            logger.error(f"❌ 회사별 데이터 개수 조회 실패 (company_id: {company_id}): {e}")
            return 0

    def get_all_normalized_data(self) -> List[Dict[str, Any]]:
        """모든 정규화 데이터 조회"""
        try:
            if not self.engine:
                return []
            
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM normal ORDER BY created_at DESC"))
                return [dict(row) for row in result]
        except Exception as e:
            logger.error(f"정규화 데이터 조회 실패: {e}")
            return []

    def get_normalized_data_by_id(self, data_id: str) -> Optional[Dict[str, Any]]:
        """특정 정규화 데이터 조회"""
        try:
            if not self.engine:
                return None
            
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT * FROM normal WHERE id = :data_id"),
                    {"data_id": data_id}
                )
                row = result.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"정규화 데이터 조회 실패 (ID: {data_id}): {e}")
            return None

    def get_company_data(self, company_name: str) -> List[Dict[str, Any]]:
        """회사별 데이터 조회"""
        try:
            if not self.engine:
                return []
            
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT * FROM normal WHERE company_name = :company_name ORDER BY created_at DESC"),
                    {"company_name": company_name}
                )
                return [dict(row) for row in result]
        except Exception as e:
            logger.error(f"회사 데이터 조회 실패 ({company_name}): {e}")
            return []
