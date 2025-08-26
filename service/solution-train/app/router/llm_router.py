from fastapi import APIRouter, HTTPException, Depends
from typing import List
from loguru import logger
from app.domain.model.llm_model import ChatRequest, ChatResponse
from app.domain.service.llm_service import LLMService

router = APIRouter()

# LLM 서비스 인스턴스 생성
llm_service = LLMService()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """채팅 추론 API"""
    try:
        logger.info(f"채팅 요청: 모델={request.model_name}, 메시지 길이={len(request.message)}")
        
        response = await llm_service.chat(request)
        
        logger.info(f"채팅 응답 완료: 토큰 수={response.tokens_used}, 처리 시간={response.processing_time:.2f}초")
        
        return response
        
    except Exception as e:
        logger.error(f"채팅 추론 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"추론 실패: {str(e)}")

@router.get("/models/loaded")
async def get_loaded_models():
    """로드된 모델 목록 조회"""
    try:
        models = await llm_service.get_loaded_models()
        return {"loaded_models": models}
    except Exception as e:
        logger.error(f"로드된 모델 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"조회 실패: {str(e)}")

@router.post("/models/{model_name}/unload")
async def unload_model(model_name: str):
    """모델 언로드"""
    try:
        await llm_service.unload_model(model_name)
        return {"message": f"모델 '{model_name}' 언로드 완료"}
    except Exception as e:
        logger.error(f"모델 언로드 실패: {model_name}, {str(e)}")
        raise HTTPException(status_code=500, detail=f"언로드 실패: {str(e)}")

@router.get("/health")
async def health_check():
    """LLM 서비스 헬스 체크"""
    try:
        loaded_models = await llm_service.get_loaded_models()
        return {
            "status": "healthy",
            "service": "llm-inference",
            "loaded_models_count": len(loaded_models),
            "loaded_models": loaded_models
        }
    except Exception as e:
        logger.error(f"헬스 체크 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"헬스 체크 실패: {str(e)}")
