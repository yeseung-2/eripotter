import time
import torch
from typing import List, Optional, Dict, Any
from transformers import AutoTokenizer, AutoModelForCausalLM
from loguru import logger
from app.domain.model.llm_model import ChatRequest, ChatResponse
from app.domain.service.model_manager import ModelManager

class LLMService:
    """LLM 추론 서비스"""
    
    def __init__(self):
        self.model_manager = ModelManager()
        self.loaded_models: Dict[str, Any] = {}
        self.tokenizers: Dict[str, Any] = {}
        
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """채팅 추론 수행"""
        start_time = time.time()
        
        try:
            # 모델 로드 확인
            if request.model_name not in self.loaded_models:
                await self._load_model(request.model_name)
            
            # 토크나이저와 모델 가져오기
            tokenizer = self.tokenizers[request.model_name]
            model = self.loaded_models[request.model_name]
            
            # 입력 텍스트 준비
            if request.context:
                # 컨텍스트가 있는 경우 대화 형식으로 구성
                input_text = self._format_conversation(request.context, request.message)
            else:
                input_text = request.message
            
            # 토큰화
            inputs = tokenizer(
                input_text,
                return_tensors="pt",
                max_length=request.max_length,
                truncation=True,
                padding=True
            )
            
            # GPU 사용 여부 확인
            device = torch.device(settings.DEVICE)
            inputs = {k: v.to(device) for k, v in inputs.items()}
            model = model.to(device)
            
            # 생성 파라미터 설정
            generation_config = {
                "max_length": request.max_length,
                "temperature": request.temperature,
                "top_p": request.top_p,
                "do_sample": True,
                "pad_token_id": tokenizer.eos_token_id
            }
            
            # 텍스트 생성
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    **generation_config
                )
            
            # 응답 디코딩
            response_text = tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:],
                skip_special_tokens=True
            )
            
            # 사용된 토큰 수 계산
            tokens_used = len(outputs[0])
            processing_time = time.time() - start_time
            
            return ChatResponse(
                response=response_text.strip(),
                model_name=request.model_name,
                tokens_used=tokens_used,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"채팅 추론 중 오류 발생: {str(e)}")
            raise Exception(f"추론 실패: {str(e)}")
    
    async def _load_model(self, model_name: str):
        """모델 로드"""
        try:
            logger.info(f"모델 로드 중: {model_name}")
            
            # 모델 정보 가져오기
            model_info = await self.model_manager.get_model_info(model_name)
            if not model_info:
                raise Exception(f"모델을 찾을 수 없습니다: {model_name}")
            
            # 토크나이저 로드
            tokenizer = AutoTokenizer.from_pretrained(
                model_info.model_path,
                trust_remote_code=True
            )
            
            # 모델 로드
            model = AutoModelForCausalLM.from_pretrained(
                model_info.model_path,
                trust_remote_code=True,
                torch_dtype=torch.float16 if settings.DEVICE == "cuda" else torch.float32,
                device_map="auto" if settings.DEVICE == "cuda" else None
            )
            
            # 모델을 평가 모드로 설정
            model.eval()
            
            # 캐시에 저장
            self.tokenizers[model_name] = tokenizer
            self.loaded_models[model_name] = model
            
            logger.info(f"모델 로드 완료: {model_name}")
            
        except Exception as e:
            logger.error(f"모델 로드 실패: {model_name}, 오류: {str(e)}")
            raise Exception(f"모델 로드 실패: {str(e)}")
    
    def _format_conversation(self, context: List[str], message: str) -> str:
        """대화 컨텍스트를 모델 입력 형식으로 변환"""
        # 간단한 대화 형식으로 구성
        formatted = ""
        for i, ctx in enumerate(context):
            if i % 2 == 0:
                formatted += f"User: {ctx}\n"
            else:
                formatted += f"Assistant: {ctx}\n"
        
        formatted += f"User: {message}\nAssistant:"
        return formatted
    
    async def unload_model(self, model_name: str):
        """모델 언로드"""
        if model_name in self.loaded_models:
            del self.loaded_models[model_name]
            del self.tokenizers[model_name]
            torch.cuda.empty_cache()  # GPU 메모리 정리
            logger.info(f"모델 언로드 완료: {model_name}")
    
    async def get_loaded_models(self) -> List[str]:
        """로드된 모델 목록 반환"""
        return list(self.loaded_models.keys())
