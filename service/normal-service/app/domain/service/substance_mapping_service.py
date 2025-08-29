import pandas as pd
import numpy as np
import faiss
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class SubstanceMappingService:
    """파인튜닝된 BGE-M3 모델을 사용한 물질 매핑 서비스"""
    
    def __init__(self):
        self.model = None
        self.regulation_data = None
        self.faiss_index = None
        self.regulation_sids = None
        self.regulation_names = None
        self._load_model_and_data()
    
    def _load_model_and_data(self):
        """모델과 규정 데이터를 로드합니다."""
        try:
            # BOMI AI 모델 로드 (볼륨 마운트 경로 사용)
            model_paths = [
                Path("/app/model/bomi-ai"),  # BOMI AI 모델 경로
                Path("/app/llm_bge-m3")
            ]
            
            model_loaded = False
            for model_path in model_paths:
                if model_path.exists():
                    self.model = SentenceTransformer(str(model_path))
                    logger.info(f"BOMI AI 모델 로드 성공: {model_path}")
                    model_loaded = True
                    break
            
            if not model_loaded:
                # BOMI AI 모델이 없으면 베이스 모델 사용
                self.model = SentenceTransformer("BAAI/bge-m3")
                logger.warning("BOMI AI 모델을 찾을 수 없어 베이스 모델을 사용합니다.")
            
            # 규정 데이터 로드 (볼륨 마운트 경로 사용)
            reg_paths = [
                Path("/app/data/reg_test1.xlsx"),
            ]
            
            reg_loaded = False
            for reg_path in reg_paths:
                if reg_path.exists():
                    self.regulation_data = pd.read_excel(reg_path).fillna("")
                    self.regulation_data.columns = [c.strip().lower() for c in self.regulation_data.columns]
                    self.regulation_data = self.regulation_data[["sid", "name"]].drop_duplicates()
                    
                    # nan 값 제거
                    nan_patterns = ["nan", "NaN", "NAN", "Nan", ""]
                    self.regulation_data = self.regulation_data[~self.regulation_data["name"].str.lower().isin(nan_patterns)]
                    self.regulation_data = self.regulation_data[self.regulation_data["name"].str.strip() != ""]
                    
                    self.regulation_sids = self.regulation_data["sid"].tolist()
                    self.regulation_names = self.regulation_data["name"].tolist()
                    
                    # FAISS 인덱스 구축
                    self._build_faiss_index()
                    logger.info(f"규정 데이터 로드 성공: {len(self.regulation_data)}개 항목")
                    reg_loaded = True
                    break
            
            if not reg_loaded:
                logger.error("규정 데이터 파일을 찾을 수 없습니다.")
                # 기본 데이터로 초기화
                self.regulation_data = pd.DataFrame(columns=["sid", "name"])
                self.regulation_sids = []
                self.regulation_names = []
                self.faiss_index = None
                
        except Exception as e:
            logger.error(f"모델 및 데이터 로드 실패: {e}")
            raise
    
    def _build_faiss_index(self):
        """FAISS 인덱스를 구축합니다."""
        try:
            # 규정 데이터 임베딩 생성
            passage_texts = [f"passage: {name}" for name in self.regulation_names]
            embeddings = self.model.encode(
                passage_texts, 
                normalize_embeddings=True, 
                batch_size=32, 
                show_progress_bar=False
            ).astype("float32")
            
            # FAISS 인덱스 생성
            dimension = embeddings.shape[1]
            self.faiss_index = faiss.IndexFlatIP(dimension)
            self.faiss_index.add(embeddings)
            
            logger.info(f"FAISS 인덱스 구축 완료 (차원: {dimension})")
            
        except Exception as e:
            logger.error(f"FAISS 인덱스 구축 실패: {e}")
            raise
    
    def map_substance(self, substance_name: str) -> Dict:
        """단일 물질을 매핑합니다."""
        try:
            if not substance_name or substance_name.strip() == "":
                return self._create_empty_result(substance_name, "빈 물질명")
            
            # 쿼리 임베딩 생성
            query_text = f"query: {substance_name.strip()}"
            query_embedding = self.model.encode(
                [query_text], 
                normalize_embeddings=True,
                show_progress_bar=False
            ).astype("float32")
            
            # FAISS 검색
            scores, indices = self.faiss_index.search(query_embedding, 5)
            
            # 결과 처리
            top1_score = float(scores[0][0])
            top2_score = float(scores[0][1]) if len(scores[0]) > 1 else 0.0
            margin = max(top1_score - top2_score, 0.0)
            
            # 신뢰도 계산
            confidence = 0.85 * top1_score + 0.15 * margin
            
            # 신뢰도 밴드 결정
            if confidence >= 0.70:
                band = "mapped"
            elif confidence >= 0.40:
                band = "needs_review"
            else:
                band = "not_mapped"
            
            # Top-5 후보들
            top5_candidates = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.regulation_sids):
                    top5_candidates.append({
                        "rank": i + 1,
                        "sid": self.regulation_sids[idx],
                        "name": self.regulation_names[idx],
                        "score": float(score)
                    })
            
            return {
                "substance_name": substance_name,
                "mapped_sid": self.regulation_sids[indices[0][0]] if indices[0][0] < len(self.regulation_sids) else None,
                "mapped_name": self.regulation_names[indices[0][0]] if indices[0][0] < len(self.regulation_names) else None,
                "top1_score": top1_score,
                "margin": margin,
                "confidence": confidence,
                "band": band,
                "top5_candidates": top5_candidates,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"물질 매핑 실패 ({substance_name}): {e}")
            return self._create_empty_result(substance_name, str(e))
    
    def map_substances_batch(self, substance_names: List[str]) -> List[Dict]:
        """여러 물질을 배치로 매핑합니다."""
        results = []
        for substance_name in substance_names:
            result = self.map_substance(substance_name)
            results.append(result)
        return results
    
    def map_file(self, file_path: str) -> Dict:
        """파일에서 물질명을 추출하여 매핑합니다."""
        try:
            # 파일 읽기
            if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                data = pd.read_excel(file_path)
            elif file_path.endswith('.csv'):
                data = pd.read_csv(file_path)
            else:
                raise ValueError("지원하지 않는 파일 형식입니다.")
            
            # 물질명 컬럼 찾기 (컬럼명에 '물질', 'substance', 'name' 등이 포함된 것)
            substance_column = None
            for col in data.columns:
                col_lower = str(col).lower()
                if any(keyword in col_lower for keyword in ['물질', 'substance', 'name', 'chemical']):
                    substance_column = col
                    break
            
            if substance_column is None:
                # 첫 번째 컬럼을 물질명으로 가정
                substance_column = data.columns[0]
            
            # 물질명 추출
            substance_names = data[substance_column].fillna("").astype(str).tolist()
            
            # 매핑 수행
            mapping_results = self.map_substances_batch(substance_names)
            
            # 통계 계산
            total_count = len(mapping_results)
            mapped_count = sum(1 for r in mapping_results if r['band'] == 'mapped')
            review_count = sum(1 for r in mapping_results if r['band'] == 'needs_review')
            not_mapped_count = sum(1 for r in mapping_results if r['band'] == 'not_mapped')
            
            return {
                "file_path": file_path,
                "total_substances": total_count,
                "mapped_count": mapped_count,
                "needs_review_count": review_count,
                "not_mapped_count": not_mapped_count,
                "mapping_results": mapping_results,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"파일 매핑 실패 ({file_path}): {e}")
            return {
                "file_path": file_path,
                "error": str(e),
                "status": "error"
            }
    
    def _create_empty_result(self, substance_name: str, error_message: str) -> Dict:
        """에러 발생 시 빈 결과를 생성합니다."""
        return {
            "substance_name": substance_name,
            "mapped_sid": None,
            "mapped_name": None,
            "top1_score": 0.0,
            "margin": 0.0,
            "confidence": 0.0,
            "band": "not_mapped",
            "top5_candidates": [],
            "error": error_message,
            "status": "error"
        }
    
    def get_mapping_statistics(self) -> Dict:
        """매핑 서비스 통계를 반환합니다."""
        return {
            "model_loaded": self.model is not None,
            "regulation_data_count": len(self.regulation_data) if self.regulation_data is not None else 0,
            "faiss_index_built": self.faiss_index is not None,
            "service_status": "ready" if all([self.model, self.regulation_data, self.faiss_index]) else "not_ready"
        }
