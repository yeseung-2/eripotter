from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, JSON
from sqlalchemy.sql import func
from datetime import datetime

class TrainingJobEntity(Base):
    """훈련 작업 정보를 저장하는 엔티티"""
    __tablename__ = "training_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(255), unique=True, index=True, nullable=False)
    model_name = Column(String(255), nullable=False)
    base_model = Column(String(255), nullable=False)
    
    # 훈련 설정
    training_config = Column(JSON, nullable=False)  # 훈련 설정을 JSON으로 저장
    data_path = Column(String(500), nullable=False)
    output_path = Column(String(500), nullable=False)
    
    # 훈련 상태
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    progress = Column(Float, default=0.0)  # 0.0 ~ 1.0
    current_epoch = Column(Integer, default=0)
    total_epochs = Column(Integer, nullable=False)
    
    # 훈련 결과
    final_loss = Column(Float, nullable=True)
    training_metrics = Column(JSON, nullable=True)  # 훈련 중 수집된 메트릭
    error_message = Column(Text, nullable=True)
    
    # 시간 정보
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<TrainingJobEntity(id={self.id}, job_id='{self.job_id}', status='{self.status}')>"

class TrainingDataEntity(Base):
    """훈련 데이터 정보를 저장하는 엔티티"""
    __tablename__ = "training_data"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    data_type = Column(String(50), nullable=False)  # text, conversation, qa 등
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)  # 바이트 단위
    num_samples = Column(Integer, nullable=True)
    
    # 데이터 메타데이터
    format = Column(String(50), nullable=False)  # json, csv, txt 등
    encoding = Column(String(20), default="utf-8")
    schema = Column(JSON, nullable=True)  # 데이터 스키마
    
    # 상태 정보
    is_processed = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<TrainingDataEntity(id={self.id}, name='{self.name}', data_type='{self.data_type}')>"
