from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ModelType(str, Enum):
    GPT = "gpt"
    BERT = "bert"
    T5 = "t5"
    BART = "bart"
    LLAMA = "llama"
    MISTRAL = "mistral"
    CUSTOM = "custom"

class TrainingStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DataType(str, Enum):
    TEXT = "text"
    CONVERSATION = "conversation"
    QA = "qa"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"

# 요청 모델들
class ChatRequest(BaseModel):
    """채팅 요청 모델"""
    message: str = Field(..., description="사용자 메시지")
    model_name: str = Field(..., description="사용할 모델 이름")
    max_length: Optional[int] = Field(100, description="최대 토큰 길이")
    temperature: Optional[float] = Field(0.7, description="생성 다양성 조절")
    top_p: Optional[float] = Field(0.9, description="Top-p 샘플링")
    context: Optional[List[str]] = Field([], description="대화 컨텍스트")

class TrainingRequest(BaseModel):
    """훈련 요청 모델"""
    model_name: str = Field(..., description="훈련할 모델 이름")
    base_model: str = Field(..., description="기본 모델")
    data_path: str = Field(..., description="훈련 데이터 경로")
    output_path: str = Field(..., description="출력 모델 경로")
    training_config: Dict[str, Any] = Field(..., description="훈련 설정")
    description: Optional[str] = Field(None, description="훈련 설명")

class ModelUploadRequest(BaseModel):
    """모델 업로드 요청 모델"""
    name: str = Field(..., description="모델 이름")
    version: str = Field(..., description="모델 버전")
    model_type: ModelType = Field(..., description="모델 타입")
    base_model: Optional[str] = Field(None, description="기본 모델")
    model_path: str = Field(..., description="모델 파일 경로")
    config_path: Optional[str] = Field(None, description="설정 파일 경로")
    tokenizer_path: Optional[str] = Field(None, description="토크나이저 파일 경로")
    description: Optional[str] = Field(None, description="모델 설명")

# 응답 모델들
class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    response: str = Field(..., description="모델 응답")
    model_name: str = Field(..., description="사용된 모델 이름")
    tokens_used: int = Field(..., description="사용된 토큰 수")
    processing_time: float = Field(..., description="처리 시간(초)")

class TrainingJobResponse(BaseModel):
    """훈련 작업 응답 모델"""
    job_id: str = Field(..., description="작업 ID")
    status: TrainingStatus = Field(..., description="작업 상태")
    progress: float = Field(..., description="진행률 (0.0 ~ 1.0)")
    message: str = Field(..., description="상태 메시지")
    created_at: datetime = Field(..., description="생성 시간")

class ModelInfoResponse(BaseModel):
    """모델 정보 응답 모델"""
    id: int = Field(..., description="모델 ID")
    name: str = Field(..., description="모델 이름")
    version: str = Field(..., description="모델 버전")
    model_type: ModelType = Field(..., description="모델 타입")
    base_model: Optional[str] = Field(None, description="기본 모델")
    description: Optional[str] = Field(None, description="모델 설명")
    parameters: Optional[int] = Field(None, description="파라미터 수")
    is_active: bool = Field(..., description="활성 상태")
    created_at: datetime = Field(..., description="생성 시간")

class TrainingMetricsResponse(BaseModel):
    """훈련 메트릭 응답 모델"""
    job_id: str = Field(..., description="작업 ID")
    current_epoch: int = Field(..., description="현재 에포크")
    total_epochs: int = Field(..., description="전체 에포크")
    current_loss: float = Field(..., description="현재 손실")
    learning_rate: float = Field(..., description="학습률")
    progress: float = Field(..., description="진행률")
    estimated_time_remaining: Optional[str] = Field(None, description="예상 남은 시간")

# 상태 모델들
class HealthCheckResponse(BaseModel):
    """헬스 체크 응답 모델"""
    status: str = Field(..., description="서비스 상태")
    service: str = Field(..., description="서비스 이름")
    timestamp: datetime = Field(..., description="체크 시간")
    version: str = Field(..., description="서비스 버전")
