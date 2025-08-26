import os
import shutil
from typing import List, Optional, Dict, Any
from loguru import logger
from app.common.config import settings
from app.domain.entity.model_entity import ModelEntity
from app.domain.repository.model_repository import ModelRepository
from app.domain.model.llm_model import ModelInfoResponse, ModelType

class ModelManager:
    """모델 관리 서비스"""
    
    def __init__(self):
        self.model_repository = ModelRepository()
        
    async def register_model(self, model_info: Dict[str, Any]) -> ModelInfoResponse:
        """모델 등록"""
        try:
            # 모델 경로 확인
            model_path = model_info.get("model_path")
            if not os.path.exists(model_path):
                raise ValueError(f"모델 경로가 존재하지 않습니다: {model_path}")
            
            # 모델 엔티티 생성
            model_entity = ModelEntity(
                name=model_info["name"],
                version=model_info["version"],
                model_type=model_info["model_type"],
                base_model=model_info.get("base_model"),
                model_path=model_path,
                config_path=model_info.get("config_path"),
                tokenizer_path=model_info.get("tokenizer_path"),
                description=model_info.get("description"),
                parameters=model_info.get("parameters"),
                max_length=model_info.get("max_length", 512)
            )
            
            # 데이터베이스에 저장
            saved_model = await self.model_repository.create_model(model_entity)
            
            return ModelInfoResponse(
                id=saved_model.id,
                name=saved_model.name,
                version=saved_model.version,
                model_type=ModelType(saved_model.model_type),
                base_model=saved_model.base_model,
                description=saved_model.description,
                parameters=saved_model.parameters,
                is_active=saved_model.is_active,
                created_at=saved_model.created_at
            )
            
        except Exception as e:
            logger.error(f"모델 등록 실패: {str(e)}")
            raise Exception(f"모델 등록 실패: {str(e)}")
    
    async def get_model_info(self, model_name: str) -> Optional[ModelEntity]:
        """모델 정보 조회"""
        try:
            return await self.model_repository.get_model_by_name(model_name)
        except Exception as e:
            logger.error(f"모델 정보 조회 실패: {model_name}, {str(e)}")
            return None
    
    async def get_all_models(self) -> List[ModelInfoResponse]:
        """모든 모델 목록 조회"""
        try:
            models = await self.model_repository.get_all_models()
            return [
                ModelInfoResponse(
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
                for model in models
            ]
        except Exception as e:
            logger.error(f"모델 목록 조회 실패: {str(e)}")
            return []
    
    async def update_model(self, model_name: str, update_data: Dict[str, Any]) -> bool:
        """모델 정보 업데이트"""
        try:
            return await self.model_repository.update_model(model_name, update_data)
        except Exception as e:
            logger.error(f"모델 업데이트 실패: {model_name}, {str(e)}")
            return False
    
    async def delete_model(self, model_name: str) -> bool:
        """모델 삭제"""
        try:
            # 모델 정보 조회
            model = await self.model_repository.get_model_by_name(model_name)
            if not model:
                return False
            
            # 모델 파일 삭제
            if os.path.exists(model.model_path):
                if os.path.isdir(model.model_path):
                    shutil.rmtree(model.model_path)
                else:
                    os.remove(model.model_path)
            
            # 데이터베이스에서 삭제
            return await self.model_repository.delete_model(model_name)
            
        except Exception as e:
            logger.error(f"모델 삭제 실패: {model_name}, {str(e)}")
            return False
    
    async def activate_model(self, model_name: str) -> bool:
        """모델 활성화"""
        try:
            return await self.model_repository.update_model(model_name, {"is_active": True})
        except Exception as e:
            logger.error(f"모델 활성화 실패: {model_name}, {str(e)}")
            return False
    
    async def deactivate_model(self, model_name: str) -> bool:
        """모델 비활성화"""
        try:
            return await self.model_repository.update_model(model_name, {"is_active": False})
        except Exception as e:
            logger.error(f"모델 비활성화 실패: {model_name}, {str(e)}")
            return False
    
    async def get_active_models(self) -> List[ModelInfoResponse]:
        """활성 모델 목록 조회"""
        try:
            models = await self.model_repository.get_active_models()
            return [
                ModelInfoResponse(
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
                for model in models
            ]
        except Exception as e:
            logger.error(f"활성 모델 목록 조회 실패: {str(e)}")
            return []
    
    async def validate_model(self, model_name: str) -> Dict[str, Any]:
        """모델 유효성 검사"""
        try:
            model = await self.model_repository.get_model_by_name(model_name)
            if not model:
                return {"valid": False, "error": "모델을 찾을 수 없습니다."}
            
            # 모델 파일 존재 확인
            if not os.path.exists(model.model_path):
                return {"valid": False, "error": "모델 파일이 존재하지 않습니다."}
            
            # 토크나이저 파일 확인
            if model.tokenizer_path and not os.path.exists(model.tokenizer_path):
                return {"valid": False, "error": "토크나이저 파일이 존재하지 않습니다."}
            
            # 설정 파일 확인
            if model.config_path and not os.path.exists(model.config_path):
                return {"valid": False, "error": "설정 파일이 존재하지 않습니다."}
            
            return {"valid": True, "model": model}
            
        except Exception as e:
            logger.error(f"모델 유효성 검사 실패: {model_name}, {str(e)}")
            return {"valid": False, "error": str(e)}
    
    async def get_model_statistics(self) -> Dict[str, Any]:
        """모델 통계 정보"""
        try:
            all_models = await self.model_repository.get_all_models()
            active_models = await self.model_repository.get_active_models()
            
            # 모델 타입별 통계
            model_types = {}
            for model in all_models:
                model_type = model.model_type
                if model_type not in model_types:
                    model_types[model_type] = {"total": 0, "active": 0}
                model_types[model_type]["total"] += 1
                if model.is_active:
                    model_types[model_type]["active"] += 1
            
            return {
                "total_models": len(all_models),
                "active_models": len(active_models),
                "model_types": model_types
            }
            
        except Exception as e:
            logger.error(f"모델 통계 조회 실패: {str(e)}")
            return {}
