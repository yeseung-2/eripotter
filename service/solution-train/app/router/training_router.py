from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any
from loguru import logger
from app.domain.model.llm_model import (
    TrainingRequest, 
    TrainingJobResponse, 
    TrainingStatus,
    TrainingMetricsResponse
)
from app.domain.service.training_service import TrainingService

router = APIRouter()

# 훈련 서비스 인스턴스 생성
training_service = TrainingService()

@router.post("/start", response_model=TrainingJobResponse)
async def start_training(request: TrainingRequest):
    """훈련 작업 시작"""
    try:
        logger.info(f"훈련 작업 시작: 모델={request.model_name}, 기본모델={request.base_model}")
        
        response = await training_service.start_training(request)
        
        logger.info(f"훈련 작업 생성 완료: 작업ID={response.job_id}")
        
        return response
        
    except Exception as e:
        logger.error(f"훈련 작업 시작 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"훈련 시작 실패: {str(e)}")

@router.get("/status/{job_id}", response_model=TrainingJobResponse)
async def get_training_status(job_id: str):
    """훈련 작업 상태 조회"""
    try:
        status = await training_service.get_training_status(job_id)
        if not status:
            raise HTTPException(status_code=404, detail="훈련 작업을 찾을 수 없습니다.")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"훈련 상태 조회 실패: {job_id}, {str(e)}")
        raise HTTPException(status_code=500, detail=f"상태 조회 실패: {str(e)}")

@router.post("/cancel/{job_id}")
async def cancel_training(job_id: str):
    """훈련 작업 취소"""
    try:
        success = await training_service.cancel_training(job_id)
        if not success:
            raise HTTPException(status_code=404, detail="훈련 작업을 찾을 수 없습니다.")
        
        return {"message": f"훈련 작업 '{job_id}' 취소 완료"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"훈련 취소 실패: {job_id}, {str(e)}")
        raise HTTPException(status_code=500, detail=f"훈련 취소 실패: {str(e)}")

@router.get("/jobs")
async def get_all_training_jobs():
    """모든 훈련 작업 목록 조회"""
    try:
        # 실제 구현에서는 페이지네이션을 추가하는 것이 좋습니다
        from app.domain.repository.training_repository import TrainingRepository
        repo = TrainingRepository()
        jobs = await repo.get_all_training_jobs()
        
        return {
            "total_jobs": len(jobs),
            "jobs": [
                {
                    "job_id": job.job_id,
                    "model_name": job.model_name,
                    "base_model": job.base_model,
                    "status": job.status,
                    "progress": job.progress,
                    "current_epoch": job.current_epoch,
                    "total_epochs": job.total_epochs,
                    "created_at": job.created_at,
                    "started_at": job.started_at,
                    "completed_at": job.completed_at
                }
                for job in jobs
            ]
        }
        
    except Exception as e:
        logger.error(f"훈련 작업 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"목록 조회 실패: {str(e)}")

@router.get("/jobs/running")
async def get_running_jobs():
    """실행 중인 훈련 작업 조회"""
    try:
        from app.domain.repository.training_repository import TrainingRepository
        repo = TrainingRepository()
        jobs = await repo.get_running_jobs()
        
        return {
            "running_jobs": len(jobs),
            "jobs": [
                {
                    "job_id": job.job_id,
                    "model_name": job.model_name,
                    "status": job.status,
                    "progress": job.progress,
                    "current_epoch": job.current_epoch,
                    "total_epochs": job.total_epochs,
                    "started_at": job.started_at
                }
                for job in jobs
            ]
        }
        
    except Exception as e:
        logger.error(f"실행 중인 훈련 작업 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"조회 실패: {str(e)}")

@router.get("/jobs/{job_id}/metrics")
async def get_training_metrics(job_id: str):
    """훈련 메트릭 조회"""
    try:
        from app.domain.repository.training_repository import TrainingRepository
        repo = TrainingRepository()
        job = await repo.get_training_job(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="훈련 작업을 찾을 수 없습니다.")
        
        # 실제 구현에서는 더 상세한 메트릭을 제공할 수 있습니다
        return TrainingMetricsResponse(
            job_id=job.job_id,
            current_epoch=job.current_epoch,
            total_epochs=job.total_epochs,
            current_loss=job.final_loss or 0.0,
            learning_rate=job.training_config.get("learning_rate", 5e-5),
            progress=job.progress,
            estimated_time_remaining=None  # 실제 구현에서는 계산 가능
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"훈련 메트릭 조회 실패: {job_id}, {str(e)}")
        raise HTTPException(status_code=500, detail=f"메트릭 조회 실패: {str(e)}")

@router.delete("/jobs/{job_id}")
async def delete_training_job(job_id: str):
    """훈련 작업 삭제"""
    try:
        from app.domain.repository.training_repository import TrainingRepository
        repo = TrainingRepository()
        success = await repo.delete_training_job(job_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="훈련 작업을 찾을 수 없습니다.")
        
        return {"message": f"훈련 작업 '{job_id}' 삭제 완료"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"훈련 작업 삭제 실패: {job_id}, {str(e)}")
        raise HTTPException(status_code=500, detail=f"삭제 실패: {str(e)}")

@router.get("/health")
async def health_check():
    """훈련 서비스 헬스 체크"""
    try:
        from app.domain.repository.training_repository import TrainingRepository
        repo = TrainingRepository()
        running_jobs = await repo.get_running_jobs()
        
        return {
            "status": "healthy",
            "service": "training-service",
            "running_jobs_count": len(running_jobs),
            "active_jobs": [job.job_id for job in running_jobs]
        }
    except Exception as e:
        logger.error(f"훈련 서비스 헬스 체크 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"헬스 체크 실패: {str(e)}")
