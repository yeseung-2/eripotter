"""
데이터 매핑 학습 모듈
BGE-M3 모델을 사용하여 필드 매핑 학습
"""

import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import torch

class FieldMappingTrainer:
    """필드 매핑 학습기"""
    
    def __init__(self, model_path: str = "./bge-m3"):
        """
        Args:
            model_path: BGE-M3 모델 경로
        """
        self.model_path = model_path
        self.model = None
        self.standard_fields = []
        self.standard_embeddings = None
        
    def load_model(self):
        """BGE-M3 모델 로드"""
        try:
            print(f"🔄 BGE-M3 모델 로딩 중: {self.model_path}")
            self.model = SentenceTransformer(self.model_path)
            print("✅ 모델 로딩 완료")
        except Exception as e:
            print(f"❌ 모델 로딩 실패: {e}")
            raise
    
    def load_training_data(self, training_data_path: str):
        """
        학습 데이터 로드 (정답쌍)
        
        Args:
            training_data_path: 학습 데이터 JSON 파일 경로
        """
        try:
            with open(training_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 표준 필드들 추출
            self.standard_fields = []
            for item in data:
                if 'standard_field' in item:
                    self.standard_fields.append(item['standard_field'])
            
            print(f"✅ 학습 데이터 로드 완료: {len(self.standard_fields)}개 표준 필드")
            return data
            
        except Exception as e:
            print(f"❌ 학습 데이터 로드 실패: {e}")
            raise
    
    def create_standard_embeddings(self):
        """표준 필드들의 임베딩 생성"""
        if not self.model:
            self.load_model()
        
        if not self.standard_fields:
            raise ValueError("표준 필드가 없습니다. 학습 데이터를 먼저 로드하세요.")
        
        print("🔄 표준 필드 임베딩 생성 중...")
        self.standard_embeddings = self.model.encode(
            self.standard_fields, 
            convert_to_tensor=True,
            show_progress_bar=True
        )
        print("✅ 표준 필드 임베딩 생성 완료")
    
    def predict_mapping(self, input_fields: List[str], threshold: float = 0.5) -> List[Dict]:
        """
        입력 필드들의 매핑 예측
        
        Args:
            input_fields: 입력 필드 리스트
            threshold: 매핑 신뢰도 임계값
            
        Returns:
            매핑 결과 리스트
        """
        if self.standard_embeddings is None:
            self.create_standard_embeddings()
        
        print(f"🔄 {len(input_fields)}개 필드 매핑 예측 중...")
        
        # 입력 필드 임베딩 생성
        input_embeddings = self.model.encode(
            input_fields, 
            convert_to_tensor=True,
            show_progress_bar=True
        )
        
        # 코사인 유사도 계산
        similarities = cosine_similarity(
            input_embeddings.cpu().numpy(), 
            self.standard_embeddings.cpu().numpy()
        )
        
        results = []
        for i, input_field in enumerate(input_fields):
            # 가장 유사한 표준 필드 찾기
            max_sim_idx = np.argmax(similarities[i])
            max_similarity = similarities[i][max_sim_idx]
            
            result = {
                "input_field": input_field,
                "predicted_mapping": self.standard_fields[max_sim_idx] if max_similarity >= threshold else None,
                "confidence": float(max_similarity),
                "all_candidates": []
            }
            
            # 상위 5개 후보들 추가
            top_indices = np.argsort(similarities[i])[-5:][::-1]
            for idx in top_indices:
                result["all_candidates"].append({
                    "standard_field": self.standard_fields[idx],
                    "similarity": float(similarities[i][idx])
                })
            
            results.append(result)
        
        print("✅ 매핑 예측 완료")
        return results
    
    def evaluate_mapping(self, test_data: List[Dict]) -> Dict:
        """
        매핑 성능 평가
        
        Args:
            test_data: 테스트 데이터 (정답 포함)
            
        Returns:
            평가 결과
        """
        correct = 0
        total = len(test_data)
        
        for item in test_data:
            input_field = item.get('input_field')
            correct_mapping = item.get('correct_mapping')
            
            if input_field and correct_mapping:
                # 단일 필드 예측
                prediction = self.predict_mapping([input_field])[0]
                if prediction['predicted_mapping'] == correct_mapping:
                    correct += 1
        
        accuracy = correct / total if total > 0 else 0
        
        return {
            "accuracy": accuracy,
            "correct": correct,
            "total": total,
            "error_rate": 1 - accuracy
        }

# 전역 인스턴스
trainer = FieldMappingTrainer()
