import pandas as pd
import numpy as np
import faiss
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple, Optional, Any
import logging
from datetime import datetime

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
            # 환경변수에서 경로 가져오기
            MODEL_DIR = os.getenv("MODEL_DIR", "/app/model/bomi-ai")
            DATA_DIR = os.getenv("DATA_DIR", "/app/data")
            HF_REPO_ID = os.getenv("HF_REPO_ID", "galaxybuddy/bomi-ai")
            
            # BOMI AI 모델 로드 (로컬 우선)
            model_dir = Path(MODEL_DIR)
            
            model_loaded = False  # 초기화 추가
            if model_dir.exists() and any(model_dir.glob("*.safetensors")):
                # 로컬 모델이 있으면 사용
                try:
                    self.model = SentenceTransformer(str(model_dir), local_files_only=True)
                    logger.info(f"BOMI AI 모델 로드 성공 (로컬): {model_dir}")
                    model_loaded = True
                except Exception as e:
                    logger.warning(f"로컬 모델 로드 실패: {e}")
                    model_loaded = False
            
            if not model_loaded:
                # 로컬 모델이 없으면 Hugging Face에서 다운로드
                try:
                    logger.info(f"Hugging Face에서 모델 다운로드 시도: {HF_REPO_ID}")
                    self.model = SentenceTransformer(HF_REPO_ID)
                    logger.info(f"BOMI AI 모델 로드 성공 (Hugging Face): {HF_REPO_ID}")
                    model_loaded = True
                except Exception as e:
                    logger.error(f"Hugging Face 모델 로드 실패: {e}")
                    raise Exception(f"BOMI AI 모델을 로드할 수 없습니다. 로컬: {MODEL_DIR}, Hugging Face: {HF_REPO_ID}")
                  
                    
            
            # 규정 데이터 로드
            reg_paths = [
                Path(f"{DATA_DIR}/reg_test1.xlsx"),  # 환경변수 사용
            ]
            
            reg_loaded = False
            for reg_path in reg_paths:
                if reg_path.exists():
                    self.regulation_data = pd.read_excel(reg_path).fillna("")
                    self.regulation_data.columns = [c.strip().lower() for c in self.regulation_data.columns]
                    self.regulation_data = self.regulation_data[["sid", "name"]].drop_duplicates()
                    
                    # nan 값 제거 (안전한 방법으로 수정)
                    # 안전한 DataFrame 체크 (DataFrame boolean 평가 방지)
                    if self.regulation_data is not None and not self.regulation_data.empty:
                        # name 컬럼이 존재하고 비어있지 않은 경우에만 처리
                        if self.regulation_data.columns is not None and "name" in self.regulation_data.columns:
                            # 빈 문자열과 nan 값 제거
                            self.regulation_data = self.regulation_data[
                                (self.regulation_data["name"].notna()) & 
                                (self.regulation_data["name"].astype(str).str.strip() != "")
                            ]
                            
                            # sid 컬럼도 확인
                            if self.regulation_data.columns is not None and "sid" in self.regulation_data.columns:
                                self.regulation_data = self.regulation_data[
                                    (self.regulation_data["sid"].notna()) & 
                                    (self.regulation_data["sid"].astype(str).str.strip() != "")
                                ]
                    
                    # 리스트로 변환 (안전하게)
                    if self.regulation_data is not None and not self.regulation_data.empty:
                        self.regulation_sids = self.regulation_data["sid"].astype(str).tolist()
                        self.regulation_names = self.regulation_data["name"].astype(str).tolist()
                        
                        # FAISS 인덱스 구축
                        if len(self.regulation_names) > 0:
                            self._build_faiss_index()
                            logger.info(f"규정 데이터 로드 성공: {len(self.regulation_data)}개 항목")
                            reg_loaded = True
                        else:
                            logger.warning("규정 데이터가 비어있습니다.")
                    else:
                        logger.warning("규정 데이터를 읽을 수 없습니다.")
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
            # 데이터 유효성 검사
            if self.regulation_data is None or self.regulation_data.empty:
                logger.warning("규정 데이터가 비어있어 FAISS 인덱스를 구축할 수 없습니다.")
                return
                
            if self.model is None:
                logger.warning("모델이 로드되지 않아 FAISS 인덱스를 구축할 수 없습니다.")
                return
                
            if len(self.regulation_names) == 0:
                logger.warning("규정 이름이 비어있어 FAISS 인덱스를 구축할 수 없습니다.")
                return
            
            # 규정 데이터 임베딩 생성
            passage_texts = [f"passage: {name}" for name in self.regulation_names]
            embeddings = self.model.encode(
                passage_texts, 
                normalize_embeddings=True, 
                batch_size=32, 
                show_progress_bar=False
            ).astype("float32")
            
            # FAISS 인덱스 생성 (L2 거리 사용)
            dimension = embeddings.shape[1]
            self.faiss_index = faiss.IndexFlatL2(dimension)
            self.faiss_index.add(embeddings)
            
            logger.info(f"FAISS 인덱스 구축 완료 (차원: {dimension}, L2 거리)")
            
        except Exception as e:
            logger.error(f"FAISS 인덱스 구축 실패: {e}")
            self.faiss_index = None
            # 오류가 발생해도 서비스는 계속 작동하도록 함
    
    def map_substance(self, substance_name: str) -> Dict[str, Any]:
        """물질명을 표준 물질 ID로 매핑"""
        try:
            # 안전한 상태 체크 (DataFrame boolean 평가 방지)
            model_ready = self.model is not None
            regulation_ready = self.regulation_data is not None and not self.regulation_data.empty if self.regulation_data is not None else False
            
            if not model_ready or not regulation_ready:
                return {
                    "status": "error",
                    "message": "모델 또는 규정 데이터가 로드되지 않았습니다."
                }
            
            # 물질명 임베딩 생성
            substance_embedding = self.model.encode([substance_name])[0]
            
            # FAISS 인덱스로 유사도 검색
            if self.faiss_index:
                D, I = self.faiss_index.search(substance_embedding.reshape(1, -1), k=5)
                
                # 가장 유사한 규정 찾기
                best_match_idx = I[0][0]
                best_match_distance = D[0][0]
                
                # L2 거리를 유사도 점수로 변환 (0-1 범위, 거리가 가까울수록 높은 점수)
                # L2 거리는 0에 가까울수록 유사함, 1에 가까울수록 유사하지 않음
                max_distance = 2.0  # 정규화된 임베딩의 최대 L2 거리
                confidence_score = max(0.0, min(1.0, 1.0 - (best_match_distance / max_distance)))
                
                # 매핑 결과 반환
                mapped_sid = self.regulation_sids[best_match_idx]
                mapped_name = self.regulation_names[best_match_idx]
                
                return {
                    "status": "success",
                    "original_substance": substance_name,
                    "mapped_sid": mapped_sid,
                    "mapped_name": mapped_name,
                    "confidence_score": confidence_score,
                    "top_matches": [
                        {
                            "sid": self.regulation_sids[i],
                            "name": self.regulation_names[i],
                            "similarity": max(0.0, min(1.0, 1.0 - (d / max_distance)))
                        }
                        for i, d in zip(I[0], D[0])
                    ]
                }
            else:
                return {
                    "status": "error",
                    "message": "FAISS 인덱스가 초기화되지 않았습니다."
                }
                
        except Exception as e:
            logger.error(f"물질 매핑 실패: {e}")
            return {
                "status": "error",
                "message": f"매핑 중 오류 발생: {str(e)}"
            }

    def check_model_status(self) -> Dict[str, Any]:
        """모델 상태 확인"""
        try:
            return {
                "model_loaded": self.model is not None,
                "regulation_data_loaded": self.regulation_data is not None and not self.regulation_data.empty if self.regulation_data is not None else False,
                "faiss_index_ready": self.faiss_index is not None,
                "model_path": os.getenv("MODEL_DIR", "/app/model/bomi-ai"),
                "data_path": os.getenv("DATA_DIR", "/app/data"),
                "total_regulations": len(self.regulation_sids) if self.regulation_sids else 0,
                "model_type": "SentenceTransformer (BGE-M3)",
                "last_check": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"모델 상태 확인 실패: {e}")
            return {
                "model_loaded": False,
                "regulation_data_loaded": False,
                "faiss_index_ready": False,
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }

    def get_model_info(self) -> Dict[str, Any]:
        """모델 상세 정보 조회"""
        try:
            model_info = {
                "model_loaded": self.model is not None,
                "regulation_data_loaded": self.regulation_data is not None and not self.regulation_data.empty if self.regulation_data is not None else False,
                "faiss_index_ready": self.faiss_index is not None,
                "model_path": os.getenv("MODEL_DIR", "/app/model/bomi-ai"),
                "data_path": os.getenv("DATA_DIR", "/app/data"),
                "total_regulations": len(self.regulation_sids) if self.regulation_sids else 0,
                "model_type": "SentenceTransformer (BGE-M3)",
                "environment_variables": {
                    "MODEL_DIR": os.getenv("MODEL_DIR"),
                    "DATA_DIR": os.getenv("DATA_DIR"),
                    "HF_REPO_ID": os.getenv("HF_REPO_ID")
                }
            }
            
            # 모델이 로드된 경우 추가 정보
            if self.model:
                model_info.update({
                    "model_parameters": {
                        "max_seq_length": getattr(self.model, 'max_seq_length', 'unknown'),
                        "embedding_dimension": getattr(self.model, 'get_sentence_embedding_dimension', lambda: 'unknown')(),
                        "device": str(self.model.device) if hasattr(self.model, 'device') else 'unknown'
                    }
                })
            
            return model_info
            
        except Exception as e:
            logger.error(f"모델 정보 조회 실패: {e}")
            return {
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
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
            mapped_count = sum(1 for r in mapping_results if r['status'] == 'success')
            review_count = sum(1 for r in mapping_results if r['status'] == 'error' and r['message'].startswith('매핑 중 오류 발생:'))
            not_mapped_count = total_count - mapped_count - review_count
            
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
        # 안전한 상태 체크 (DataFrame boolean 평가 방지)
        model_ready = self.model is not None
        regulation_ready = self.regulation_data is not None and not self.regulation_data.empty if self.regulation_data is not None else False
        faiss_ready = self.faiss_index is not None
        
        return {
            "model_loaded": model_ready,
            "regulation_data_count": len(self.regulation_data) if self.regulation_data is not None else 0,
            "faiss_index_built": faiss_ready,
            "service_status": "ready" if all([model_ready, regulation_ready, faiss_ready]) else "not_ready"
        }
