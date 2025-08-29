import os
import uuid
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    TrainingArguments, 
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
from loguru import logger
from app.domain.model.llm_model import TrainingRequest, TrainingJobResponse, TrainingStatus
from app.domain.entity.training_entity import TrainingJobEntity
from app.domain.repository.training_repository import TrainingRepository

class TrainingService:
    """모델 훈련 서비스"""
    
    def __init__(self):
        self.training_repository = TrainingRepository()
        self.active_jobs: Dict[str, asyncio.Task] = {}
        
    async def start_training(self, request: TrainingRequest) -> TrainingJobResponse:
        """훈련 작업 시작"""
        try:
            # 작업 ID 생성
            job_id = str(uuid.uuid4())
            
            # 훈련 작업 엔티티 생성
            training_job = TrainingJobEntity(
                job_id=job_id,
                model_name=request.model_name,
                base_model=request.base_model,
                training_config=request.training_config,
                data_path=request.data_path,
                output_path=request.output_path,
                total_epochs=request.training_config.get("num_epochs", 3),
                status=TrainingStatus.PENDING.value
            )
            
            # 데이터베이스에 저장
            await self.training_repository.create_training_job(training_job)
            
            # 비동기 훈련 작업 시작
            training_task = asyncio.create_task(
                self._run_training(job_id, request)
            )
            self.active_jobs[job_id] = training_task
            
            return TrainingJobResponse(
                job_id=job_id,
                status=TrainingStatus.PENDING,
                progress=0.0,
                message="훈련 작업이 시작되었습니다.",
                created_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"훈련 작업 시작 실패: {str(e)}")
            raise Exception(f"훈련 시작 실패: {str(e)}")
    
    async def _run_training(self, job_id: str, request: TrainingRequest):
        """실제 훈련 실행"""
        try:
            # 작업 상태를 실행 중으로 업데이트
            await self._update_job_status(job_id, TrainingStatus.RUNNING.value, 0.0)
            
            # 데이터 로드
            dataset = await self._load_training_data(request.data_path)
            
            # 토크나이저 로드
            tokenizer = AutoTokenizer.from_pretrained(request.base_model)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # 모델 로드
            model = AutoModelForCausalLM.from_pretrained(
                request.base_model,
                torch_dtype=torch.float16 if settings.DEVICE == "cuda" else torch.float32
            )
            
            # 데이터 전처리
            tokenized_dataset = await self._tokenize_dataset(dataset, tokenizer, request.training_config)
            
            # 훈련 인수 설정
            training_args = TrainingArguments(
                output_dir=request.output_path,
                num_train_epochs=request.training_config.get("num_epochs", 3),
                per_device_train_batch_size=request.training_config.get("batch_size", 4),
                learning_rate=request.training_config.get("learning_rate", 5e-5),
                warmup_steps=request.training_config.get("warmup_steps", 500),
                logging_steps=request.training_config.get("logging_steps", 100),
                save_steps=request.training_config.get("save_steps", 1000),
                evaluation_strategy="no",
                save_strategy="epoch",
                load_best_model_at_end=False,
                remove_unused_columns=False,
                dataloader_pin_memory=False,
                report_to=None,  # wandb 등 외부 로깅 비활성화
            )
            
            # 데이터 콜레이터 설정
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=tokenizer,
                mlm=False
            )
            
            # 커스텀 콜백 생성
            custom_callback = CustomTrainingCallback(job_id, self._update_job_progress)
            
            # 트레이너 생성 및 훈련 실행
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=tokenized_dataset,
                data_collator=data_collator,
                callbacks=[custom_callback]
            )
            
            # 훈련 실행
            trainer.train()
            
            # 모델 저장
            trainer.save_model()
            tokenizer.save_pretrained(request.output_path)
            
            # 작업 완료 상태로 업데이트
            await self._update_job_status(
                job_id, 
                TrainingStatus.COMPLETED.value, 
                1.0,
                final_loss=trainer.state.log_history[-1].get("loss", 0.0) if trainer.state.log_history else None
            )
            
            logger.info(f"훈련 완료: {job_id}")
            
        except Exception as e:
            logger.error(f"훈련 실행 중 오류: {job_id}, {str(e)}")
            await self._update_job_status(
                job_id, 
                TrainingStatus.FAILED.value, 
                0.0,
                error_message=str(e)
            )
        finally:
            # 작업 목록에서 제거
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]
    
    async def _load_training_data(self, data_path: str) -> Dataset:
        """훈련 데이터 로드"""
        try:
            if data_path.endswith('.json'):
                with open(data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return Dataset.from_list(data)
            elif data_path.endswith('.csv'):
                return Dataset.from_csv(data_path)
            else:
                raise ValueError(f"지원하지 않는 데이터 형식: {data_path}")
        except Exception as e:
            logger.error(f"데이터 로드 실패: {str(e)}")
            raise
    
    async def _tokenize_dataset(self, dataset: Dataset, tokenizer, config: Dict[str, Any]) -> Dataset:
        """데이터셋 토크나이징"""
        def tokenize_function(examples):
            # 텍스트 필드 확인
            text_column = config.get("text_column", "text")
            if text_column not in examples:
                raise ValueError(f"텍스트 컬럼을 찾을 수 없습니다: {text_column}")
            
            # 토크나이징
            tokenized = tokenizer(
                examples[text_column],
                truncation=True,
                padding=True,
                max_length=config.get("max_length", 512),
                return_tensors=None
            )
            
            return tokenized
        
        return dataset.map(tokenize_function, batched=True)
    
    async def _update_job_status(self, job_id: str, status: str, progress: float, 
                               final_loss: Optional[float] = None, 
                               error_message: Optional[str] = None):
        """작업 상태 업데이트"""
        try:
            update_data = {
                "status": status,
                "progress": progress
            }
            
            if final_loss is not None:
                update_data["final_loss"] = final_loss
            
            if error_message is not None:
                update_data["error_message"] = error_message
            
            if status == TrainingStatus.RUNNING.value:
                update_data["started_at"] = datetime.now()
            elif status in [TrainingStatus.COMPLETED.value, TrainingStatus.FAILED.value]:
                update_data["completed_at"] = datetime.now()
            
            await self.training_repository.update_training_job(job_id, update_data)
            
        except Exception as e:
            logger.error(f"작업 상태 업데이트 실패: {job_id}, {str(e)}")
    
    async def _update_job_progress(self, job_id: str, progress: float, current_epoch: int):
        """작업 진행률 업데이트"""
        try:
            await self.training_repository.update_training_job(job_id, {
                "progress": progress,
                "current_epoch": current_epoch
            })
        except Exception as e:
            logger.error(f"진행률 업데이트 실패: {job_id}, {str(e)}")
    
    async def get_training_status(self, job_id: str) -> Optional[TrainingJobResponse]:
        """훈련 작업 상태 조회"""
        try:
            job = await self.training_repository.get_training_job(job_id)
            if not job:
                return None
            
            return TrainingJobResponse(
                job_id=job.job_id,
                status=TrainingStatus(job.status),
                progress=job.progress,
                message=f"현재 에포크: {job.current_epoch}/{job.total_epochs}",
                created_at=job.created_at
            )
        except Exception as e:
            logger.error(f"훈련 상태 조회 실패: {job_id}, {str(e)}")
            return None
    
    async def cancel_training(self, job_id: str) -> bool:
        """훈련 작업 취소"""
        try:
            if job_id in self.active_jobs:
                self.active_jobs[job_id].cancel()
                del self.active_jobs[job_id]
            
            await self._update_job_status(job_id, TrainingStatus.CANCELLED.value, 0.0)
            return True
        except Exception as e:
            logger.error(f"훈련 취소 실패: {job_id}, {str(e)}")
            return False

class CustomTrainingCallback:
    """커스텀 훈련 콜백"""
    
    def __init__(self, job_id: str, progress_callback):
        self.job_id = job_id
        self.progress_callback = progress_callback
        self.total_steps = 0
        self.current_step = 0
    
    def on_train_begin(self, args, state, control, **kwargs):
        """훈련 시작 시 호출"""
        self.total_steps = state.max_steps
    
    def on_step_end(self, args, state, control, **kwargs):
        """각 스텝 완료 시 호출"""
        self.current_step = state.global_step
        progress = self.current_step / self.total_steps if self.total_steps > 0 else 0.0
        
        # 비동기로 진행률 업데이트
        asyncio.create_task(
            self.progress_callback(self.job_id, progress, state.epoch)
        )
