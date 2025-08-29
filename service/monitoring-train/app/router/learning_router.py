"""
학습 기능 API 라우터
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import tempfile
import os

from ..learning import trainer

router = APIRouter(prefix="/learning", tags=["Learning"])

class TrainingDataRequest(BaseModel):
    """학습 데이터 요청"""
    training_data: List[Dict]

class MappingRequest(BaseModel):
    """매핑 예측 요청"""
    input_fields: List[str]
    threshold: float = 0.5

class EvaluationRequest(BaseModel):
    """성능 평가 요청"""
    test_data: List[Dict]

@router.post("/train")
async def train_model(request: TrainingDataRequest):
    """모델 학습"""
    try:
        # 임시 파일에 학습 데이터 저장
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(request.training_data, f, ensure_ascii=False, indent=2)
            temp_path = f.name
        
        # 학습 데이터 로드
        trainer.load_training_data(temp_path)
        
        # 표준 필드 임베딩 생성
        trainer.create_standard_embeddings()
        
        # 임시 파일 삭제
        os.unlink(temp_path)
        
        return {
            "status": "success",
            "message": "모델 학습 완료",
            "standard_fields_count": len(trainer.standard_fields)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"학습 실패: {str(e)}")

@router.post("/predict")
async def predict_mapping(request: MappingRequest):
    """매핑 예측"""
    try:
        if not trainer.standard_embeddings:
            raise HTTPException(status_code=400, detail="모델이 학습되지 않았습니다. 먼저 학습을 진행하세요.")
        
        results = trainer.predict_mapping(
            request.input_fields, 
            request.threshold
        )
        
        return {
            "status": "success",
            "predictions": results,
            "input_count": len(request.input_fields)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"예측 실패: {str(e)}")

@router.post("/evaluate")
async def evaluate_model(request: EvaluationRequest):
    """모델 성능 평가"""
    try:
        if not trainer.standard_embeddings:
            raise HTTPException(status_code=400, detail="모델이 학습되지 않았습니다. 먼저 학습을 진행하세요.")
        
        results = trainer.evaluate_mapping(request.test_data)
        
        return {
            "status": "success",
            "evaluation": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"평가 실패: {str(e)}")

@router.get("/status")
async def get_model_status():
    """모델 상태 확인"""
    return {
        "model_loaded": trainer.model is not None,
        "standard_fields_count": len(trainer.standard_fields),
        "embeddings_created": trainer.standard_embeddings is not None
    }

@router.post("/upload-training-data")
async def upload_training_data(file: UploadFile = File(...)):
    """학습 데이터 파일 업로드"""
    try:
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="JSON 파일만 업로드 가능합니다.")
        
        # 파일 내용 읽기
        content = await file.read()
        training_data = json.loads(content.decode('utf-8'))
        
        # 임시 파일에 저장
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
            temp_path = f.name
        
        # 학습 데이터 로드
        trainer.load_training_data(temp_path)
        
        # 표준 필드 임베딩 생성
        trainer.create_standard_embeddings()
        
        # 임시 파일 삭제
        os.unlink(temp_path)
        
        return {
            "status": "success",
            "message": "학습 데이터 업로드 및 모델 학습 완료",
            "standard_fields_count": len(trainer.standard_fields)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"업로드 실패: {str(e)}")
