from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from loguru import logger
from app.domain.entity.model_entity import ModelEntity

class ModelRepository:
    """모델 리포지토리"""
    
    async def create_model(self, model: ModelEntity) -> ModelEntity:
        """모델 생성"""
        try:
            db = next(get_db())
            db.add(model)
            db.commit()
            db.refresh(model)
            return model
        except Exception as e:
            logger.error(f"모델 생성 실패: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()
    
    async def get_model_by_name(self, name: str) -> Optional[ModelEntity]:
        """이름으로 모델 조회"""
        try:
            db = next(get_db())
            return db.query(ModelEntity).filter(ModelEntity.name == name).first()
        except Exception as e:
            logger.error(f"모델 조회 실패: {name}, {str(e)}")
            return None
        finally:
            db.close()
    
    async def get_model_by_id(self, model_id: int) -> Optional[ModelEntity]:
        """ID로 모델 조회"""
        try:
            db = next(get_db())
            return db.query(ModelEntity).filter(ModelEntity.id == model_id).first()
        except Exception as e:
            logger.error(f"모델 조회 실패: {model_id}, {str(e)}")
            return None
        finally:
            db.close()
    
    async def get_all_models(self) -> List[ModelEntity]:
        """모든 모델 조회"""
        try:
            db = next(get_db())
            return db.query(ModelEntity).all()
        except Exception as e:
            logger.error(f"모든 모델 조회 실패: {str(e)}")
            return []
        finally:
            db.close()
    
    async def get_active_models(self) -> List[ModelEntity]:
        """활성 모델 조회"""
        try:
            db = next(get_db())
            return db.query(ModelEntity).filter(ModelEntity.is_active == True).all()
        except Exception as e:
            logger.error(f"활성 모델 조회 실패: {str(e)}")
            return []
        finally:
            db.close()
    
    async def get_models_by_type(self, model_type: str) -> List[ModelEntity]:
        """타입별 모델 조회"""
        try:
            db = next(get_db())
            return db.query(ModelEntity).filter(ModelEntity.model_type == model_type).all()
        except Exception as e:
            logger.error(f"타입별 모델 조회 실패: {model_type}, {str(e)}")
            return []
        finally:
            db.close()
    
    async def update_model(self, name: str, update_data: Dict[str, Any]) -> bool:
        """모델 업데이트"""
        try:
            db = next(get_db())
            result = db.query(ModelEntity).filter(ModelEntity.name == name).update(update_data)
            db.commit()
            return result > 0
        except Exception as e:
            logger.error(f"모델 업데이트 실패: {name}, {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()
    
    async def delete_model(self, name: str) -> bool:
        """모델 삭제"""
        try:
            db = next(get_db())
            result = db.query(ModelEntity).filter(ModelEntity.name == name).delete()
            db.commit()
            return result > 0
        except Exception as e:
            logger.error(f"모델 삭제 실패: {name}, {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()
    
    async def search_models(self, search_term: str) -> List[ModelEntity]:
        """모델 검색"""
        try:
            db = next(get_db())
            return db.query(ModelEntity).filter(
                ModelEntity.name.contains(search_term) |
                ModelEntity.description.contains(search_term)
            ).all()
        except Exception as e:
            logger.error(f"모델 검색 실패: {search_term}, {str(e)}")
            return []
        finally:
            db.close()
    
    async def get_models_by_base_model(self, base_model: str) -> List[ModelEntity]:
        """기본 모델별 파인튜닝된 모델 조회"""
        try:
            db = next(get_db())
            return db.query(ModelEntity).filter(
                and_(
                    ModelEntity.base_model == base_model,
                    ModelEntity.is_fine_tuned == True
                )
            ).all()
        except Exception as e:
            logger.error(f"기본 모델별 모델 조회 실패: {base_model}, {str(e)}")
            return []
        finally:
            db.close()
