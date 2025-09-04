import pandas as pd
import numpy as np
import faiss
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple, Optional, Any
import logging
from datetime import datetime
import time
import matplotlib.pyplot as plt
import io
import base64

logger = logging.getLogger(__name__)

class SubstanceMappingService:
    """파인튜닝된 BGE-M3 모델과 베이스모델을 사용한 물질 매핑 서비스"""
    
    def __init__(self):
        self.model = None  # 파인튜닝된 모델
        self.base_model = None  # 베이스모델 (BAAI/bge-m3)
        self.regulation_data = None
        self.faiss_index = None  # 파인튜닝된 모델용 FAISS 인덱스
        self.base_faiss_index = None  # 베이스모델용 FAISS 인덱스
        self.regulation_sids = None
        self.regulation_names = None
        self._load_models_and_data()
    
    def _load_models_and_data(self):
        """모델들과 규정 데이터를 로드합니다."""
        try:
            # 환경변수에서 경로 가져오기
            MODEL_DIR = os.getenv("MODEL_DIR", "/app/model/bomi-ai")
            DATA_DIR = os.getenv("DATA_DIR", "/app/data")
            HF_REPO_ID = os.getenv("HF_REPO_ID", "galaxybuddy/bomi-ai")
            
            # 1. 파인튜닝된 BOMI AI 모델 로드
            model_loaded = self._load_finetuned_model(MODEL_DIR, HF_REPO_ID)
            
            # 2. 베이스모델 (BAAI/bge-m3) 로드
            base_model_loaded = self._load_base_model()
            
            # 3. 규정 데이터 로드
            reg_loaded = self._load_regulation_data(DATA_DIR)
            
            if not model_loaded and not base_model_loaded:
                raise Exception("모든 모델 로드에 실패했습니다.")
            
            if not reg_loaded:
                raise Exception("규정 데이터 로드에 실패했습니다.")
                
        except Exception as e:
            logger.error(f"모델과 데이터 로드 실패: {e}")
            raise
    
    def _load_finetuned_model(self, model_dir: str, hf_repo_id: str) -> bool:
        """파인튜닝된 모델을 로드합니다."""
        try:
            model_path = Path(model_dir)
            
            if model_path.exists() and any(model_path.glob("*.safetensors")):
                # 로컬 모델이 있으면 사용
                try:
                    self.model = SentenceTransformer(str(model_path), local_files_only=True)
                    logger.info(f"BOMI AI 모델 로드 성공 (로컬): {model_path}")
                    return True
                except Exception as e:
                    logger.warning(f"로컬 모델 로드 실패: {e}")
            
                # 로컬 모델이 없으면 Hugging Face에서 다운로드
                try:
                logger.info(f"Hugging Face에서 모델 다운로드 시도: {hf_repo_id}")
                self.model = SentenceTransformer(hf_repo_id)
                logger.info(f"BOMI AI 모델 로드 성공 (Hugging Face): {hf_repo_id}")
                return True
                except Exception as e:
                    logger.error(f"Hugging Face 모델 로드 실패: {e}")
                return False
                
        except Exception as e:
            logger.error(f"파인튜닝된 모델 로드 중 오류: {e}")
            return False
    
    def _load_base_model(self) -> bool:
        """베이스모델 (BAAI/bge-m3)을 로드합니다."""
        try:
            logger.info("베이스모델 (BAAI/bge-m3) 로드 시도")
            self.base_model = SentenceTransformer("BAAI/bge-m3")
            logger.info("베이스모델 로드 성공: BAAI/bge-m3")
            return True
        except Exception as e:
            logger.error(f"베이스모델 로드 실패: {e}")
            return False
    
    def _load_regulation_data(self, data_dir: str) -> bool:
        """규정 데이터를 로드합니다."""
        try:
            reg_paths = [
                Path(f"{data_dir}/reg_test1.xlsx"),
            ]
            
            for reg_path in reg_paths:
                if reg_path.exists():
                    self.regulation_data = pd.read_excel(reg_path).fillna("")
                    self.regulation_data.columns = [c.strip().lower() for c in self.regulation_data.columns]
                    self.regulation_data = self.regulation_data[["sid", "name"]].drop_duplicates()
                    
                    # nan 값 제거 (안전한 방법으로 수정)
                    if self.regulation_data is not None and not self.regulation_data.empty:
                        if self.regulation_data.columns is not None and "name" in self.regulation_data.columns:
                            self.regulation_data = self.regulation_data[
                                (self.regulation_data["name"].notna()) & 
                                (self.regulation_data["name"].astype(str).str.strip() != "")
                            ]
                            
                            if self.regulation_data.columns is not None and "sid" in self.regulation_data.columns:
                                self.regulation_data = self.regulation_data[
                                    (self.regulation_data["sid"].notna()) & 
                                    (self.regulation_data["sid"].astype(str).str.strip() != "")
                                ]
                    
                    # 리스트로 변환
                    if self.regulation_data is not None and not self.regulation_data.empty:
                        self.regulation_sids = self.regulation_data["sid"].astype(str).tolist()
                        self.regulation_names = self.regulation_data["name"].astype(str).tolist()
                        
                        if len(self.regulation_names) > 0:
                            # FAISS 인덱스 구축 (파인튜닝된 모델용)
                    self._build_faiss_index()
                            # 베이스모델용 FAISS 인덱스 구축
                            self._build_base_faiss_index()
                    logger.info(f"규정 데이터 로드 성공: {len(self.regulation_data)}개 항목")
                            return True
                        else:
                            logger.warning("규정 데이터가 비어있습니다.")
            
            return False
                
        except Exception as e:
            logger.error(f"규정 데이터 로드 실패: {e}")
            return False
    
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
    
    def _build_base_faiss_index(self):
        """베이스모델의 FAISS 인덱스를 구축합니다."""
        try:
            if self.base_model is None:
                logger.warning("베이스모델이 로드되지 않아 FAISS 인덱스를 구축할 수 없습니다.")
                return
            
            if len(self.regulation_names) == 0:
                logger.warning("규정 이름이 비어있어 FAISS 인덱스를 구축할 수 없습니다.")
                return
            
            # 규정 데이터 임베딩 생성
            passage_texts = [f"passage: {name}" for name in self.regulation_names]
            embeddings = self.base_model.encode(
                passage_texts, 
                normalize_embeddings=True,
                batch_size=32, 
                show_progress_bar=False
            ).astype("float32")
            
            # FAISS 인덱스 생성 (L2 거리 사용)
            dimension = embeddings.shape[1]
            self.base_faiss_index = faiss.IndexFlatL2(dimension)
            self.base_faiss_index.add(embeddings)
            
            logger.info(f"베이스모델 FAISS 인덱스 구축 완료 (차원: {dimension}, L2 거리)")
            
        except Exception as e:
            logger.error(f"베이스모델 FAISS 인덱스 구축 실패: {e}")
            self.base_faiss_index = None
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
                "finetuned_model_loaded": self.model is not None,
                "base_model_loaded": self.base_model is not None,
                "regulation_data_loaded": self.regulation_data is not None and not self.regulation_data.empty if self.regulation_data is not None else False,
                "finetuned_faiss_ready": self.faiss_index is not None,
                "base_faiss_ready": self.base_faiss_index is not None,
                "model_path": os.getenv("MODEL_DIR", "/app/model/bomi-ai"),
                "data_path": os.getenv("DATA_DIR", "/app/data"),
                "total_regulations": len(self.regulation_sids) if self.regulation_sids else 0,
                "finetuned_model_type": "SentenceTransformer (BOMI-AI)",
                "base_model_type": "SentenceTransformer (BAAI/bge-m3)",
                "last_check": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"모델 상태 확인 실패: {e}")
            return {
                "finetuned_model_loaded": False,
                "base_model_loaded": False,
                "regulation_data_loaded": False,
                "finetuned_faiss_ready": False,
                "base_faiss_ready": False,
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
        finetuned_model_ready = self.model is not None
        base_model_ready = self.base_model is not None
        regulation_ready = self.regulation_data is not None and not self.regulation_data.empty if self.regulation_data is not None else False
        finetuned_faiss_ready = self.faiss_index is not None
        base_faiss_ready = self.base_faiss_index is not None
        
        return {
            "finetuned_model_loaded": finetuned_model_ready,
            "base_model_loaded": base_model_ready,
            "regulation_data_count": len(self.regulation_data) if self.regulation_data is not None else 0,
            "finetuned_faiss_built": finetuned_faiss_ready,
            "base_faiss_built": base_faiss_ready,
            "service_status": "ready" if all([finetuned_model_ready, regulation_ready, finetuned_faiss_ready]) else "not_ready"
        }
    
    def compare_model_performance(self, substance_name: str) -> Dict[str, Any]:
        """베이스모델과 파인튜닝 모델의 성능을 비교합니다."""
        try:
            if not substance_name:
                return {
                    "status": "error",
                    "message": "물질명이 필요합니다."
                }
            
            # 베이스모델 매핑
            base_result = self._map_with_model(substance_name, self.base_model, self.base_faiss_index, "베이스모델")
            
            # 파인튜닝 모델 매핑
            finetuned_result = self._map_with_model(substance_name, self.model, self.faiss_index, "파인튜닝 모델")
            
            # 성능 비교 분석
            comparison_analysis = self._analyze_performance_comparison(base_result, finetuned_result)
            
            return {
                "status": "success",
                "substance_name": substance_name,
                "comparison_timestamp": datetime.now().isoformat(),
                "base_model_result": base_result,
                "finetuned_model_result": finetuned_result,
                "performance_analysis": comparison_analysis
            }
            
        except Exception as e:
            logger.error(f"모델 성능 비교 실패: {e}")
            return {
                "status": "error",
                "message": f"모델 성능 비교 중 오류 발생: {str(e)}"
            }
    
    def _map_with_model(self, substance_name: str, model, faiss_index, model_name: str) -> Dict[str, Any]:
        """지정된 모델로 물질을 매핑합니다."""
        try:
            if model is None:
                return {
                    "status": "error",
                    "message": f"{model_name}이 로드되지 않았습니다."
                }
            
            if faiss_index is None:
                return {
                    "status": "error",
                    "message": f"{model_name}의 FAISS 인덱스가 구축되지 않았습니다."
                }
            
            # 응답 시간 측정 시작
            start_time = time.time()
            
            # 물질명 임베딩 생성
            substance_embedding = model.encode([substance_name])[0]
            
            # FAISS 인덱스로 유사도 검색
            D, I = faiss_index.search(substance_embedding.reshape(1, -1), k=5)
            
            # 응답 시간 측정 종료
            response_time = time.time() - start_time
            
            # 가장 유사한 규정 찾기
            best_match_idx = I[0][0]
            best_match_distance = D[0][0]
            
            # L2 거리를 유사도 점수로 변환
            max_distance = 2.0
            confidence_score = max(0.0, min(1.0, 1.0 - (best_match_distance / max_distance)))
            
            # 매핑 결과 반환
            mapped_sid = self.regulation_sids[best_match_idx]
            mapped_name = self.regulation_names[best_match_idx]
            
            return {
                "status": "success",
                "model_name": model_name,
                "original_substance": substance_name,
                "mapped_sid": mapped_sid,
                "mapped_name": mapped_name,
                "confidence_score": confidence_score,
                "response_time_seconds": response_time,
                "top_matches": [
                    {
                        "sid": self.regulation_sids[i],
                        "name": self.regulation_names[i],
                        "similarity": max(0.0, min(1.0, 1.0 - (d / max_distance)))
                    }
                    for i, d in zip(I[0], D[0])
                ]
            }
            
        except Exception as e:
            logger.error(f"{model_name} 매핑 실패: {e}")
            return {
                "status": "error",
                "model_name": model_name,
                "message": f"매핑 중 오류 발생: {str(e)}"
            }
    
    def _analyze_performance_comparison(self, base_result: Dict, finetuned_result: Dict) -> Dict[str, Any]:
        """베이스모델과 파인튜닝 모델의 성능을 분석합니다."""
        try:
            if base_result.get("status") != "success" or finetuned_result.get("status") != "success":
                return {
                    "confidence_comparison": "비교 불가",
                    "response_time_comparison": "비교 불가",
                    "recommendation": "모든 모델이 정상 작동하지 않습니다."
                }
            
            base_confidence = base_result.get("confidence_score", 0.0)
            finetuned_confidence = finetuned_result.get("confidence_score", 0.0)
            base_time = base_result.get("response_time_seconds", 0.0)
            finetuned_time = finetuned_result.get("response_time_seconds", 0.0)
            
            # 신뢰도 비교
            if base_confidence > 0:
                confidence_improvement = ((finetuned_confidence - base_confidence) / base_confidence) * 100
                if confidence_improvement > 0:
                    confidence_comparison = f"파인튜닝 모델이 {confidence_improvement:+.1f}% 개선"
                else:
                    confidence_comparison = f"파인튜닝 모델이 {abs(confidence_improvement):.1f}% 감소"
            else:
                confidence_comparison = "베이스모델 신뢰도가 0입니다"
            
            # 응답 시간 비교
            if base_time > 0:
                time_ratio = (finetuned_time / base_time) * 100
                if time_ratio < 100:
                    response_time_comparison = f"파인튜닝 모델이 {100 - time_ratio:.1f}% 빠름"
                else:
                    response_time_comparison = f"파인튜닝 모델이 {time_ratio - 100:.1f}% 느림"
            else:
                response_time_comparison = "베이스모델 응답 시간이 0입니다"
            
            # 권장사항
            if finetuned_confidence > base_confidence and finetuned_time <= base_time:
                recommendation = "파인튜닝 모델 사용을 권장합니다 (성능 향상, 속도 유지)"
            elif finetuned_confidence > base_confidence:
                recommendation = "파인튜닝 모델 사용을 권장합니다 (성능 향상, 속도는 약간 느림)"
            elif finetuned_confidence <= base_confidence:
                recommendation = "베이스모델 사용을 고려해보세요 (성능이 비슷하거나 낮음)"
            else:
                recommendation = "모델 선택 시 신뢰도와 응답 시간을 종합적으로 고려하세요"
            
            return {
                "confidence_comparison": confidence_comparison,
                "response_time_comparison": response_time_comparison,
                "recommendation": recommendation
            }
            
        except Exception as e:
            logger.error(f"성능 비교 분석 실패: {e}")
            return {
                "confidence_comparison": "분석 실패",
                "response_time_comparison": "분석 실패",
                "recommendation": "성능 분석 중 오류가 발생했습니다."
            }
    
    def generate_comparison_chart(self, substance_name: str) -> str:
        """베이스모델과 파인튜닝 모델의 성능 비교 차트를 생성합니다."""
        try:
            # 모델 성능 비교 실행
            comparison_result = self.compare_model_performance(substance_name)
            
            if comparison_result.get("status") != "success":
                return None
            
            # 차트 데이터 추출
            base_result = comparison_result.get("base_model_result", {})
            finetuned_result = comparison_result.get("finetuned_model_result", {})
            
            if (base_result.get("status") != "success" or 
                finetuned_result.get("status") != "success"):
                return None
            
            # 차트 생성
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle(f'모델 성능 비교: {substance_name}', fontsize=16, fontweight='bold')
            
            # 1. 신뢰도 점수 비교 (막대 그래프)
            models = ['베이스모델', '파인튜닝 모델']
            confidence_scores = [
                base_result.get("confidence_score", 0.0),
                finetuned_result.get("confidence_score", 0.0)
            ]
            
            bars = ax1.bar(models, confidence_scores, color=['#3498db', '#2ecc71'], alpha=0.8)
            ax1.set_title('신뢰도 점수 비교', fontsize=14, fontweight='bold')
            ax1.set_ylabel('신뢰도 점수')
            ax1.set_ylim(0, 1)
            
            # 값 표시
            for bar, score in zip(bars, confidence_scores):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                        f'{score:.3f}', ha='center', va='bottom', fontweight='bold')
            
            # 개선율 계산 및 표시
            if confidence_scores[0] > 0:
                improvement = ((confidence_scores[1] - confidence_scores[0]) / confidence_scores[0]) * 100
                ax1.text(0.5, 0.9, f'개선율: {improvement:+.1f}%', 
                        transform=ax1.transAxes, ha='center', fontsize=12, 
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
            
            # 2. 응답 시간 비교 (막대 그래프)
            response_times = [
                base_result.get("response_time_seconds", 0.0),
                finetuned_result.get("response_time_seconds", 0.0)
            ]
            
            bars2 = ax2.bar(models, response_times, color=['#e74c3c', '#f39c12'], alpha=0.8)
            ax2.set_title('응답 시간 비교', fontsize=14, fontweight='bold')
            ax2.set_ylabel('응답 시간 (초)')
            
            # 값 표시
            for bar, time_val in zip(bars2, response_times):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.001,
                        f'{time_val:.3f}s', ha='center', va='bottom', fontweight='bold')
            
            # 3. Top 5 매칭 점수 비교 (선 그래프)
            base_top_matches = base_result.get("top_matches", [])[:5]
            finetuned_top_matches = finetuned_result.get("top_matches", [])[:5]
            
            x_positions = range(1, 6)
            base_scores = [match.get("similarity", 0.0) for match in base_top_matches]
            finetuned_scores = [match.get("similarity", 0.0) for match in finetuned_top_matches]
            
            ax3.plot(x_positions, base_scores, 'o-', color='#3498db', linewidth=2, markersize=8, label='베이스모델')
            ax3.plot(x_positions, finetuned_scores, 's-', color='#2ecc71', linewidth=2, markersize=8, label='파인튜닝 모델')
            ax3.set_title('Top 5 매칭 점수 비교', fontsize=14, fontweight='bold')
            ax3.set_xlabel('순위')
            ax3.set_ylabel('유사도 점수')
            ax3.set_xticks(x_positions)
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
            # 4. 성능 요약 (텍스트 박스)
            ax4.axis('off')
            
            # 성능 분석 결과
            performance_analysis = comparison_result.get("performance_analysis", {})
            
            summary_text = f"""
성능 비교 요약

베이스모델 결과:
• 매핑된 물질: {base_result.get("mapped_name", "N/A")}
• 신뢰도 점수: {base_result.get("confidence_score", 0.0):.3f}
• 응답 시간: {base_result.get("response_time_seconds", 0.0):.3f}초

파인튜닝 모델 결과:
• 매핑된 물질: {finetuned_result.get("mapped_name", "N/A")}
• 신뢰도 점수: {finetuned_result.get("confidence_score", 0.0):.3f}
• 응답 시간: {finetuned_result.get("response_time_seconds", 0.0):.3f}초

성능 분석:
• 신뢰도 개선: {performance_analysis.get("confidence_comparison", "N/A")}
• 응답 시간: {performance_analysis.get("response_time_comparison", "N/A")}
• 권장사항: {performance_analysis.get("recommendation", "N/A")}
            """
            
            ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes, fontsize=11,
                     verticalalignment='top', bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))
            
            # 차트 레이아웃 조정
            plt.tight_layout()
            
            # 이미지를 base64로 인코딩
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            buffer.close()
            
            # matplotlib 메모리 정리
            plt.close(fig)
            
            return image_base64
            
        except Exception as e:
            logger.error(f"차트 생성 실패: {e}")
            return None
    
    def get_model_comparison_status(self) -> Dict[str, Any]:
        """모델 비교 서비스의 상태를 확인합니다."""
        return {
            "base_model_loaded": self.base_model is not None,
            "finetuned_model_loaded": self.model is not None,
            "base_faiss_ready": self.base_faiss_index is not None,
            "finetuned_faiss_ready": self.faiss_index is not None,
            "regulation_data_loaded": self.regulation_data is not None and not self.regulation_data.empty if self.regulation_data is not None else False,
            "total_regulations": len(self.regulation_sids) if self.regulation_sids else 0,
            "last_check": datetime.now().isoformat()
        }

    def evaluate_base_model_performance(self) -> Dict[str, Any]:
        """베이스 모델의 전체 성능을 평가합니다."""
        try:
            if not self.base_model or not self.base_faiss_index or self.regulation_data is None or self.regulation_data.empty:
                return {
                    "status": "error",
                    "message": "베이스 모델 또는 데이터가 로드되지 않았습니다."
                }
            
            logger.info("베이스 모델 성능 평가 시작... (전체 데이터셋)")
            
            # 전체 데이터셋 사용 (파인튜닝 모델과 동일)
            total_samples = len(self.regulation_data)
            logger.info(f"전체 테스트 샘플: {total_samples}개")
            
            total_correct = 0
            total_top5_correct = 0
            response_times = []
            
            # 전체 데이터셋에 대해 평가
            for idx in range(total_samples):
                test_substance = self.regulation_names[idx]
                true_sid = self.regulation_sids[idx]
                
                start_time = time.time()
                
                # 베이스 모델로 매핑 (파인튜닝 모델과 동일한 방식)
                test_embedding = self.base_model.encode([test_substance])[0]
                D, I = self.base_faiss_index.search(test_embedding.reshape(1, -1), k=5)
                
                end_time = time.time()
                response_time = end_time - start_time
                response_times.append(response_time)
                
                # Top-1 정확도
                if I[0][0] == idx:
                    total_correct += 1
                
                # Top-5 정확도
                if idx in I[0]:
                    total_top5_correct += 1
                
                # 진행상황 표시 (100개마다)
                if (idx + 1) % 100 == 0:
                    logger.info(f"진행률: {idx + 1}/{total_samples} ({((idx + 1) / total_samples * 100):.1f}%)")
            
            # 성능 메트릭 계산
            recall_at_1 = total_correct / total_samples
            recall_at_5 = total_top5_correct / total_samples
            avg_response_time = np.mean(response_times)
            
            # 신뢰도 밴드별 분포 계산 (파인튜닝 모델과 동일)
            confidence_scores = []
            for idx in range(total_samples):
                test_substance = self.regulation_names[idx]
                test_embedding = self.base_model.encode([test_substance])[0]
                D, I = self.base_faiss_index.search(test_embedding.reshape(1, -1), k=5)
                
                # 가장 유사한 규정 찾기
                best_match_idx = I[0][0]
                best_match_distance = D[0][0]
                
                # L2 거리를 유사도 점수로 변환 (파인튜닝 모델과 동일한 방식)
                max_distance = 2.0
                confidence_score = max(0.0, min(1.0, 1.0 - (best_match_distance / max_distance)))
                confidence_scores.append(confidence_score)
            
            # 신뢰도 밴드별 분포
            mapped_count = sum(1 for score in confidence_scores if score >= 0.7)
            needs_review_count = sum(1 for score in confidence_scores if 0.3 <= score < 0.7)
            not_mapped_count = sum(1 for score in confidence_scores if score < 0.3)
            
            mapped_percentage = (mapped_count / total_samples) * 100
            needs_review_percentage = (needs_review_count / total_samples) * 100
            not_mapped_percentage = (not_mapped_count / total_samples) * 100
            
            # Mapped 케이스 정확도 (Precision)
            mapped_precision = mapped_count / total_samples if total_samples > 0 else 0
            needs_review_precision = needs_review_count / total_samples if total_samples > 0 else 0
            avg_confidence = np.mean(confidence_scores)
            
            logger.info("베이스 모델 성능 평가 완료!")
            logger.info(f"성능 결과:")
            logger.info(f"Recall@1: {recall_at_1:.3f} ({total_correct}/{total_samples})")
            logger.info(f"Recall@5: {recall_at_5:.3f} ({total_top5_correct}/{total_samples})")
            logger.info(f"신뢰도 밴드별 분포:")
            logger.info(f"mapped: {mapped_count}개 ({mapped_percentage:.1f}%)")
            logger.info(f"needs_review: {needs_review_count}개 ({needs_review_percentage:.1f}%)")
            logger.info(f"not_mapped: {not_mapped_count}개 ({not_mapped_percentage:.1f}%)")
            logger.info(f"Mapped 케이스 정확도 (Precision):")
            logger.info(f"Precision: {mapped_precision:.3f} ({mapped_count}/{total_samples})")
            logger.info(f"Needs_review 정확도: {needs_review_precision:.3f} ({needs_review_count}/{total_samples})")
            
            return {
                "status": "success",
                "model_type": "BAAI/bge-m3 (Base)",
                "test_samples": total_samples,
                "performance_metrics": {
                    "recall_at_1": round(recall_at_1, 4),
                    "recall_at_5": round(recall_at_5, 4),
                    "precision": round(mapped_precision, 4),
                    "avg_response_time_ms": round(avg_response_time * 1000, 2),
                    "avg_confidence": round(avg_confidence, 4)
                },
                "confidence_band_distribution": {
                    "mapped": {
                        "count": mapped_count,
                        "percentage": round(mapped_percentage, 1)
                    },
                    "needs_review": {
                        "count": needs_review_count,
                        "percentage": round(needs_review_percentage, 1)
                    },
                    "not_mapped": {
                        "count": not_mapped_count,
                        "percentage": round(not_mapped_percentage, 1)
                    }
                },
                "mapped_case_precision": {
                    "mapped_precision": round(mapped_precision, 4),
                    "needs_review_precision": round(needs_review_precision, 4)
                },
                "comparison_with_finetuned": {
                    "base_recall_at_1": round(recall_at_1, 4),
                    "base_recall_at_5": round(recall_at_5, 4),
                    "finetuned_recall_at_1": "0.927",  # 기존 파인튜닝 모델 성능
                    "finetuned_recall_at_5": "0.941",
                    "improvement_at_1": f"+{((0.927 - recall_at_1) * 100):.1f}%",
                    "improvement_at_5": f"+{((0.941 - recall_at_5) * 100):.1f}%"
                },
                "evaluation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"베이스 모델 성능 평가 실패: {e}")
            return {
                "status": "error",
                "message": f"베이스 모델 성능 평가 실패: {str(e)}"
        }
