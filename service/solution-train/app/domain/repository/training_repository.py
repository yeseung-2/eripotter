from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from loguru import logger
from app.domain.entity.training_entity import TrainingJobEntity, TrainingDataEntity

class TrainingRepository:
    """훈련 리포지토리"""
    
    # TrainingJob 관련 메서드들
    async def create_training_job(self, job: TrainingJobEntity) -> TrainingJobEntity:
        """훈련 작업 생성"""
        try:
            db = next(get_db())
            db.add(job)
            db.commit()
            db.refresh(job)
            return job
        except Exception as e:
            logger.error(f"훈련 작업 생성 실패: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()
    
    async def get_training_job(self, job_id: str) -> Optional[TrainingJobEntity]:
        """훈련 작업 조회"""
        try:
            db = next(get_db())
            return db.query(TrainingJobEntity).filter(TrainingJobEntity.job_id == job_id).first()
        except Exception as e:
            logger.error(f"훈련 작업 조회 실패: {job_id}, {str(e)}")
            return None
        finally:
            db.close()
    
    async def get_all_training_jobs(self) -> List[TrainingJobEntity]:
        """모든 훈련 작업 조회"""
        try:
            db = next(get_db())
            return db.query(TrainingJobEntity).order_by(desc(TrainingJobEntity.created_at)).all()
        except Exception as e:
            logger.error(f"모든 훈련 작업 조회 실패: {str(e)}")
            return []
        finally:
            db.close()
    
    async def get_training_jobs_by_status(self, status: str) -> List[TrainingJobEntity]:
        """상태별 훈련 작업 조회"""
        try:
            db = next(get_db())
            return db.query(TrainingJobEntity).filter(TrainingJobEntity.status == status).all()
        except Exception as e:
            logger.error(f"상태별 훈련 작업 조회 실패: {status}, {str(e)}")
            return []
        finally:
            db.close()
    
    async def get_training_jobs_by_model(self, model_name: str) -> List[TrainingJobEntity]:
        """모델별 훈련 작업 조회"""
        try:
            db = next(get_db())
            return db.query(TrainingJobEntity).filter(TrainingJobEntity.model_name == model_name).all()
        except Exception as e:
            logger.error(f"모델별 훈련 작업 조회 실패: {model_name}, {str(e)}")
            return []
        finally:
            db.close()
    
    async def update_training_job(self, job_id: str, update_data: Dict[str, Any]) -> bool:
        """훈련 작업 업데이트"""
        try:
            db = next(get_db())
            result = db.query(TrainingJobEntity).filter(TrainingJobEntity.job_id == job_id).update(update_data)
            db.commit()
            return result > 0
        except Exception as e:
            logger.error(f"훈련 작업 업데이트 실패: {job_id}, {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()
    
    async def delete_training_job(self, job_id: str) -> bool:
        """훈련 작업 삭제"""
        try:
            db = next(get_db())
            result = db.query(TrainingJobEntity).filter(TrainingJobEntity.job_id == job_id).delete()
            db.commit()
            return result > 0
        except Exception as e:
            logger.error(f"훈련 작업 삭제 실패: {job_id}, {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()
    
    async def get_running_jobs(self) -> List[TrainingJobEntity]:
        """실행 중인 훈련 작업 조회"""
        try:
            db = next(get_db())
            return db.query(TrainingJobEntity).filter(
                TrainingJobEntity.status.in_(["pending", "running"])
            ).all()
        except Exception as e:
            logger.error(f"실행 중인 훈련 작업 조회 실패: {str(e)}")
            return []
        finally:
            db.close()
    
    # TrainingData 관련 메서드들
    async def create_training_data(self, data: TrainingDataEntity) -> TrainingDataEntity:
        """훈련 데이터 생성"""
        try:
            db = next(get_db())
            db.add(data)
            db.commit()
            db.refresh(data)
            return data
        except Exception as e:
            logger.error(f"훈련 데이터 생성 실패: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()
    
    async def get_training_data(self, data_id: int) -> Optional[TrainingDataEntity]:
        """훈련 데이터 조회"""
        try:
            db = next(get_db())
            return db.query(TrainingDataEntity).filter(TrainingDataEntity.id == data_id).first()
        except Exception as e:
            logger.error(f"훈련 데이터 조회 실패: {data_id}, {str(e)}")
            return None
        finally:
            db.close()
    
    async def get_training_data_by_name(self, name: str) -> Optional[TrainingDataEntity]:
        """이름으로 훈련 데이터 조회"""
        try:
            db = next(get_db())
            return db.query(TrainingDataEntity).filter(TrainingDataEntity.name == name).first()
        except Exception as e:
            logger.error(f"훈련 데이터 조회 실패: {name}, {str(e)}")
            return None
        finally:
            db.close()
    
    async def get_all_training_data(self) -> List[TrainingDataEntity]:
        """모든 훈련 데이터 조회"""
        try:
            db = next(get_db())
            return db.query(TrainingDataEntity).filter(TrainingDataEntity.is_active == True).all()
        except Exception as e:
            logger.error(f"모든 훈련 데이터 조회 실패: {str(e)}")
            return []
        finally:
            db.close()
    
    async def get_training_data_by_type(self, data_type: str) -> List[TrainingDataEntity]:
        """타입별 훈련 데이터 조회"""
        try:
            db = next(get_db())
            return db.query(TrainingDataEntity).filter(
                and_(
                    TrainingDataEntity.data_type == data_type,
                    TrainingDataEntity.is_active == True
                )
            ).all()
        except Exception as e:
            logger.error(f"타입별 훈련 데이터 조회 실패: {data_type}, {str(e)}")
            return []
        finally:
            db.close()
    
    async def update_training_data(self, data_id: int, update_data: Dict[str, Any]) -> bool:
        """훈련 데이터 업데이트"""
        try:
            db = next(get_db())
            result = db.query(TrainingDataEntity).filter(TrainingDataEntity.id == data_id).update(update_data)
            db.commit()
            return result > 0
        except Exception as e:
            logger.error(f"훈련 데이터 업데이트 실패: {data_id}, {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()
    
    async def delete_training_data(self, data_id: int) -> bool:
        """훈련 데이터 삭제"""
        try:
            db = next(get_db())
            result = db.query(TrainingDataEntity).filter(TrainingDataEntity.id == data_id).delete()
            db.commit()
            return result > 0
        except Exception as e:
            logger.error(f"훈련 데이터 삭제 실패: {data_id}, {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()
    
    async def get_processed_training_data(self) -> List[TrainingDataEntity]:
        """처리된 훈련 데이터 조회"""
        try:
            db = next(get_db())
            return db.query(TrainingDataEntity).filter(
                and_(
                    TrainingDataEntity.is_processed == True,
                    TrainingDataEntity.is_active == True
                )
            ).all()
        except Exception as e:
            logger.error(f"처리된 훈련 데이터 조회 실패: {str(e)}")
            return []
        finally:
            db.close()
