from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Dict, Any
from loguru import logger
from app.domain.model.llm_model import (
    ModelUploadRequest, 
    ModelInfoResponse, 
    ModelType
)
from app.domain.service.model_manager import ModelManager

router = APIRouter()

# 모델 관리 서비스 인스턴스 생성
model_manager = ModelManager()

@router.post("/register", response_model=ModelInfoResponse)
async def register_model(request: ModelUploadRequest):
    """모델 등록"""
    try:
        logger.info(f"모델 등록: {request.name}, 타입: {request.model_type}")
        
        model_info = {
            "name": request.name,
            "version": request.version,
            "model_type": request.model_type,
            "base_model": request.base_model,
            "model_path": request.model_path,
            "config_path": request.config_path,
            "tokenizer_path": request.tokenizer_path,
            "description": request.description
        }
        
        response = await model_manager.register_model(model_info)
        
        logger.info(f"모델 등록 완료: {request.name}")
        
        return response
        
    except Exception as e:
        logger.error(f"모델 등록 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"모델 등록 실패: {str(e)}")

@router.get("/list", response_model=List[ModelInfoResponse])
async def get_all_models():
    """모든 모델 목록 조회"""
    try:
        models = await model_manager.get_all_models()
        return models
    except Exception as e:
        logger.error(f"모델 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"목록 조회 실패: {str(e)}")

@router.get("/active", response_model=List[ModelInfoResponse])
async def get_active_models():
    """활성 모델 목록 조회"""
    try:
        models = await model_manager.get_active_models()
        return models
    except Exception as e:
        logger.error(f"활성 모델 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"목록 조회 실패: {str(e)}")

@router.get("/{model_name}", response_model=ModelInfoResponse)
async def get_model_info(model_name: str):
    """모델 정보 조회"""
    try:
        model = await model_manager.get_model_info(model_name)
        if not model:
            raise HTTPException(status_code=404, detail="모델을 찾을 수 없습니다.")
        
        return ModelInfoResponse(
            id=model.id,
            name=model.name,
            version=model.version,
            model_type=ModelType(model.model_type),
            base_model=model.base_model,
            description=model.description,
            parameters=model.parameters,
            is_active=model.is_active,
            created_at=model.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"모델 정보 조회 실패: {model_name}, {str(e)}")
        raise HTTPException(status_code=500, detail=f"조회 실패: {str(e)}")

@router.put("/{model_name}/activate")
async def activate_model(model_name: str):
    """모델 활성화"""
    try:
        success = await model_manager.activate_model(model_name)
        if not success:
            raise HTTPException(status_code=404, detail="모델을 찾을 수 없습니다.")
        
        return {"message": f"모델 '{model_name}' 활성화 완료"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"모델 활성화 실패: {model_name}, {str(e)}")
        raise HTTPException(status_code=500, detail=f"활성화 실패: {str(e)}")

@router.put("/{model_name}/deactivate")
async def deactivate_model(model_name: str):
    """모델 비활성화"""
    try:
        success = await model_manager.deactivate_model(model_name)
        if not success:
            raise HTTPException(status_code=404, detail="모델을 찾을 수 없습니다.")
        
        return {"message": f"모델 '{model_name}' 비활성화 완료"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"모델 비활성화 실패: {model_name}, {str(e)}")
        raise HTTPException(status_code=500, detail=f"비활성화 실패: {str(e)}")

@router.delete("/{model_name}")
async def delete_model(model_name: str):
    """모델 삭제"""
    try:
        success = await model_manager.delete_model(model_name)
        if not success:
            raise HTTPException(status_code=404, detail="모델을 찾을 수 없습니다.")
        
        return {"message": f"모델 '{model_name}' 삭제 완료"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"모델 삭제 실패: {model_name}, {str(e)}")
        raise HTTPException(status_code=500, detail=f"삭제 실패: {str(e)}")

@router.get("/{model_name}/validate")
async def validate_model(model_name: str):
    """모델 유효성 검사"""
    try:
        validation_result = await model_manager.validate_model(model_name)
        return validation_result
    except Exception as e:
        logger.error(f"모델 유효성 검사 실패: {model_name}, {str(e)}")
        raise HTTPException(status_code=500, detail=f"유효성 검사 실패: {str(e)}")

@router.get("/statistics")
async def get_model_statistics():
    """모델 통계 정보"""
    try:
        stats = await model_manager.get_model_statistics()
        return stats
    except Exception as e:
        logger.error(f"모델 통계 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")

@router.get("/health")
async def health_check():
    """모델 관리 서비스 헬스 체크"""
    try:
        stats = await model_manager.get_model_statistics()
        return {
            "status": "healthy",
            "service": "model-management",
            "total_models": stats.get("total_models", 0),
            "active_models": stats.get("active_models", 0)
        }
    except Exception as e:
        logger.error(f"모델 관리 서비스 헬스 체크 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"헬스 체크 실패: {str(e)}")
