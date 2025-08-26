from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.sql import func
from app.common.db import Base
from datetime import datetime

class ModelEntity(Base):
    """모델 정보를 저장하는 엔티티"""
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    version = Column(String(50), nullable=False)
    model_type = Column(String(100), nullable=False)  # gpt, bert, t5 등
    base_model = Column(String(255), nullable=True)
    model_path = Column(String(500), nullable=False)
    config_path = Column(String(500), nullable=True)
    tokenizer_path = Column(String(500), nullable=True)
    
    # 모델 메타데이터
    description = Column(Text, nullable=True)
    parameters = Column(Integer, nullable=True)  # 모델 파라미터 수
    max_length = Column(Integer, default=512)
    
    # 훈련 정보
    is_fine_tuned = Column(Boolean, default=False)
    training_data_size = Column(Integer, nullable=True)
    training_epochs = Column(Integer, nullable=True)
    training_loss = Column(Float, nullable=True)
    
    # 상태 정보
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ModelEntity(id={self.id}, name='{self.name}', version='{self.version}')>"
