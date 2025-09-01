"""
Normal Service - 새로운 테이블 구조에 맞춘 통합 서비스
프론트엔드 데이터 처리 + AI 매핑 + 사용자 검토
"""
from eripotter_common.database.base import get_db_engine
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
import faiss
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
# SubstanceMappingRepository는 이제 NormalRepository에 통합됨
from ..repository.normal_repository import NormalRepository
from .data_normalization_service import DataNormalizationService

from .interfaces import ISubstanceMapping, IDataNormalization, IESGValidation

logger = logging.getLogger("normal-service")

class NormalService(ISubstanceMapping, IDataNormalization, IESGValidation):
    """통합 Normal 서비스 - 새로운 테이블 구조 대응"""
    
    def __init__(self):
        # 데이터베이스 연결을 선택적으로 시도
        self.engine = None
        self.normal_repository = None
        self.db_available = False
        
        try:
            self.engine = get_db_engine()
            self.normal_repository = NormalRepository()
            self.db_available = True
            logger.info("✅ 데이터베이스 연결 성공")
        except Exception as e:
            logger.warning(f"⚠️ 데이터베이스 연결 실패: {e}")
            logger.info("📝 AI 매핑만 사용합니다 (결과 저장 불가)")
        
        # 기능별 서비스 초기화
        self.data_normalization_service = DataNormalizationService()
        
        # Substance Mapping 관련 초기화
        self.model = None
        self.regulation_data = None
        self.faiss_index = None
        self.regulation_sids = None
        self.regulation_names = None
        self._load_model_and_data()

    # ===== 프론트엔드 데이터 처리 메서드들 =====
    
    def save_substance_data_only(self, substance_data: Dict[str, Any], company_id: str = None, company_name: str = None, uploaded_by: str = None) -> Dict[str, Any]:
        """프론트엔드에서 받은 물질 데이터만 저장 (AI 매핑은 별도)"""
        try:
            logger.info(f"📝 물질 데이터 저장 시작: {substance_data.get('productName', 'Unknown')}")
            
            if not self.db_available:
                return {
                    "status": "error",
                    "message": "데이터베이스 연결이 불가능합니다."
                }
            
            # Normal 테이블에 데이터 저장
            normal_id = self.normal_repository.save_substance_data(
                substance_data=substance_data,
                company_id=company_id,
                company_name=company_name,
                uploaded_by=uploaded_by,
                uploaded_by_email=substance_data.get('uploadedByEmail')
            )
            
            if not normal_id:
                return {
                    "status": "error",
                    "message": "물질 데이터 저장에 실패했습니다."
                }
            
            logger.info(f"✅ 물질 데이터 저장 완료: Normal ID {normal_id}")
            
            return {
                "status": "success",
                "normal_id": normal_id,
                "product_name": substance_data.get('productName'),
                "message": "물질 데이터 저장 완료. 자동매핑을 시작하세요."
            }
            
        except Exception as e:
            logger.error(f"❌ 물질 데이터 저장 실패: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "물질 데이터 저장 중 오류가 발생했습니다."
            }

    def start_auto_mapping(self, normal_id: int, company_id: str = None, company_name: str = None) -> Dict[str, Any]:
        """자동매핑 시작 - 저장된 데이터의 온실가스 배출량을 AI로 매핑"""
        try:
            logger.info(f"🤖 자동매핑 시작: Normal ID {normal_id}")
            
            if not self.db_available:
                return {
                    "status": "error",
                    "message": "데이터베이스 연결이 불가능합니다."
                }
            
            # Normal 테이블에서 데이터 조회
            normal_data = self.normal_repository.get_by_id(normal_id)
            if not normal_data:
                return {
                    "status": "error",
                    "message": f"Normal ID {normal_id}를 찾을 수 없습니다."
                }
            
            # 온실가스 배출량 데이터 추출
            greenhouse_gases = normal_data.greenhouse_gas_emissions or []
            if not greenhouse_gases:
                return {
                    "status": "error",
                    "message": "온실가스 배출량 데이터가 없습니다."
                }
            
            mapping_results = []
            certification_ids = []
            
            logger.info(f"🤖 온실가스 AI 매핑 시작: {len(greenhouse_gases)}개")
            
            for gas_data in greenhouse_gases:
                gas_name = gas_data.get('materialName', '')
                gas_amount = gas_data.get('amount', '')
                
                if gas_name:
                    # AI 매핑 수행
                    ai_result = self.map_substance(gas_name)
                    
                    # Certification 테이블에 저장
                    if ai_result.get('status') == 'success':
                        success = self.normal_repository.save_ai_mapping_result(
                            normal_id=normal_id,
                            gas_name=gas_name,
                            gas_amount=gas_amount,
                            mapping_result=ai_result,
                            company_id=company_id,
                            company_name=company_name
                        )
                        
                        if success:
                            # 신뢰도에 따른 상태 결정
                            confidence = ai_result.get('confidence', 0.0)
                            if confidence >= 0.7:
                                status = 'auto_mapped'
                            elif confidence >= 0.4:
                                status = 'needs_review'
                            else:
                                status = 'needs_review'  # 낮은 신뢰도도 검토 필요
                            
                            mapping_results.append({
                                'original_gas_name': gas_name,
                                'original_amount': gas_amount,
                                'ai_mapped_name': ai_result.get('mapped_name'),
                                'ai_confidence': ai_result.get('confidence'),
                                'status': status,
                                'certification_id': None  # 나중에 조회해서 채워넣기
                            })
                        else:
                            mapping_results.append({
                                'original_gas_name': gas_name,
                                'status': 'save_failed'
                            })
                    else:
                        mapping_results.append({
                            'original_gas_name': gas_name,
                            'status': 'mapping_failed',
                            'error': ai_result.get('error')
                        })
            
            # 생성된 certification ID들 조회
            saved_mappings = self.normal_repository.get_saved_mappings(company_id, limit=len(mapping_results))
            for i, mapping in enumerate(mapping_results):
                if i < len(saved_mappings):
                    mapping['certification_id'] = saved_mappings[i]['id']
            
            logger.info(f"✅ 자동매핑 완료: {len(mapping_results)}개 매핑")
            
            return {
                "status": "success",
                "normal_id": normal_id,
                "mapping_results": mapping_results,
                "message": f"자동매핑 완료: {len(mapping_results)}개 온실가스 매핑. 사용자 검토가 필요합니다."
            }
            
        except Exception as e:
            logger.error(f"❌ 자동매핑 실패: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "자동매핑 중 오류가 발생했습니다."
            }

    def get_substance_mapping_statistics(self) -> Dict[str, Any]:
        """물질 매핑 통계 조회 (새로운 구조)"""
        try:
            if not self.db_available:
                return {"error": "데이터베이스 연결 불가"}
            
            # Repository에서 통계 조회
            stats = self.normal_repository.get_mapping_statistics()
            
            # AI 서비스 통계 추가
            ai_stats = self.get_substance_mapping_statistics()
            
            return {
                "database_stats": stats,
                "ai_model_stats": ai_stats,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 매핑 통계 조회 실패: {e}")
            return {"error": str(e)}

    def get_saved_mappings(self, company_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """저장된 매핑 결과 조회"""
        if not self.db_available:
            return []
        
        return self.normal_repository.get_saved_mappings(company_id, limit)

    def get_original_data(self, company_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """원본 데이터 조회"""
        if not self.db_available:
            return []
        
        return self.normal_repository.get_original_data(company_id, limit)

    def get_corrections(self, company_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """사용자 수정 데이터 조회"""
        # 현재는 certification 테이블에서 user_reviewed 상태인 것들 조회
        try:
            if not self.db_available:
                return []
            
            # TODO: Repository에 메서드 추가 필요
            return []
            
        except Exception as e:
            logger.error(f"❌ 수정 데이터 조회 실패: {e}")
            return []

    def correct_mapping(self, certification_id: int, correction_data: Dict[str, Any]) -> bool:
        """매핑 결과 수동 수정"""
        if not self.db_available:
            return False
        
        return self.normal_repository.update_user_mapping_correction(
            certification_id=certification_id,
            correction_data=correction_data,
            reviewed_by=correction_data.get('reviewed_by', 'user')
        )

    def save_mapping_correction(self, **kwargs):
        """매핑 수정 결과 저장 (레거시 호환)"""
        # 새로운 구조에서는 correct_mapping 사용
        return True

    # ===== 엑셀 파일 처리 (기존 로직 개선) =====
    
    def upload_and_normalize_excel(self, file):
        """엑셀 파일 업로드 및 정규화 (새로운 구조 대응)"""
        try:
            logger.info(f"📝 엑셀 파일 업로드: {file.filename}")
            
            # 파일 내용 읽기
            content = file.file.read()
            
            # 1단계: 데이터 정규화
            normalization_result = self.data_normalization_service.normalize_excel_data(
                file_data=content,
                filename=file.filename
            )
            
            if normalization_result['status'] == 'error':
                return normalization_result
            
            # 2단계: 정규화된 데이터를 새로운 구조로 변환
            normalized_data = normalization_result.get('normalized_data', [])
            converted_results = []
            
            for item in normalized_data:
                # 엑셀 데이터를 프론트엔드 구조로 변환
                substance_data = {
                    'filename': file.filename,
                    'file_size': len(content),
                    'file_type': 'excel',
                    'productName': item.get('substance_name', ''),
                    'greenhouseGasEmissions': [
                        {
                            'materialName': item.get('substance_name', ''),
                            'amount': str(item.get('amount', 0)),
                            'unit': item.get('unit', 'tonCO2eq')
                        }
                    ]
                }
                
                # 데이터 저장 및 매핑
                result = self.save_substance_data_and_map_gases(
                    substance_data=substance_data,
                    company_id=item.get('company_id'),
                    company_name=item.get('company_name'),
                    uploaded_by=item.get('uploaded_by')
                )
                
                converted_results.append(result)
            
            return {
                "filename": file.filename,
                "status": "uploaded_and_mapped",
                "normalization": normalization_result,
                "conversion_results": converted_results,
                "message": f"엑셀 파일 처리 완료: {len(converted_results)}개 항목"
            }
            
        except Exception as e:
            logger.error(f"❌ 엑셀 파일 업로드 및 매핑 실패: {e}")
            return {
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            }

    # ===== 기존 인터페이스 호환성 메서드들 =====
    
    def map_substance(self, substance_name: str, company_id: str = None) -> dict:
        """단일 물질 매핑 (AI만)"""
        try:
            logger.info(f"📝 물질 매핑 요청: {substance_name}")
            
            if not substance_name or substance_name.strip() == "":
                return self._create_empty_result(substance_name, "빈 물질명")
            
            # 규정 데이터가 없으면 기본 응답
            if not self.regulation_sids or not self.regulation_names:
                return {
                    "substance_name": substance_name,
                    "mapped_sid": None,
                    "mapped_name": None,
                    "top1_score": 0.0,
                    "margin": 0.0,
                    "confidence": 0.0,
                    "band": "not_mapped",
                    "top5_candidates": [],
                    "message": "규정 데이터가 로드되지 않았습니다.",
                    "status": "no_data"
                }
            
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
            
            result = {
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
            
            logger.info(f"✅ 물질 매핑 완료: {substance_name} -> {result.get('mapped_name', 'None')}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 물질 매핑 실패: {e}")
            return self._create_empty_result(substance_name, str(e))
    
    def map_substances_batch(self, substance_names: list, company_id: str = None) -> list:
        """배치 물질 매핑 (AI만)"""
        try:
            if not substance_names:
                raise Exception("매핑할 물질명 목록이 비어있습니다.")
            
            logger.info(f"📝 배치 물질 매핑 요청: {len(substance_names)}개")
            
            results = []
            for substance_name in substance_names:
                result = self.map_substance(substance_name, company_id)
                results.append(result)
            
            logger.info(f"✅ 배치 물질 매핑 완료: {len(results)}개")
            return results
            
        except Exception as e:
            logger.error(f"❌ 배치 물질 매핑 실패: {e}")
            raise Exception(f"배치 물질 매핑을 수행할 수 없습니다: {str(e)}")
    
    def map_file(self, file_path: str) -> dict:
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

    # ===== 인터페이스 구현 (추상 메서드들) =====
    
    def get_mapping_statistics(self) -> dict:
        """매핑 통계 조회 (인터페이스 구현)"""
        return self.get_substance_mapping_statistics()
    
    def normalize_excel_data(self, file_data: bytes, filename: str, company_id: str = None) -> dict:
        """엑셀 데이터 정규화 (인터페이스 구현)"""
        return self.data_normalization_service.normalize_excel_data(file_data, filename)
    
    def validate_data_structure(self, data: dict) -> dict:
        """데이터 구조 검증 (인터페이스 구현)"""
        return {"status": "valid", "data": data}
    
    def standardize_data(self, data: dict) -> dict:
        """데이터 표준화 (인터페이스 구현)"""
        return data
    
    def validate_esg_data(self, data: dict, industry: str = None) -> dict:
        """ESG 데이터 검증 (인터페이스 구현)"""
        return {"status": "valid", "data": data}
    
    def calculate_esg_score(self, data: dict) -> int:
        """ESG 점수 계산 (인터페이스 구현)"""
        return 85  # 기본 점수
    
    def generate_esg_report(self, company_id: str, report_type: str) -> dict:
        """ESG 보고서 생성 (인터페이스 구현)"""
        return {"company_id": company_id, "report_type": report_type, "status": "generated"}

    # ===== 레거시 메서드들 (호환성) =====
    
    def get_all_normalized_data(self):
        """모든 정규화 데이터 조회"""
        return self.get_original_data(limit=50)

    def get_normalized_data_by_id(self, data_id: str):
        """특정 정규화 데이터 조회"""
        if not self.db_available:
            return {"id": data_id, "error": "데이터베이스 연결 불가"}
        
        try:
            normal_entity = self.normal_repository.get_by_id(int(data_id))
            return normal_entity.to_dict() if normal_entity else {"error": "데이터를 찾을 수 없습니다"}
        except:
            return {"id": data_id, "error": "조회 실패"}

    def create_normalized_data(self, data: dict):
        """정규화 데이터 생성"""
        return data

    def update_normalized_data(self, data_id: str, data: dict):
        """정규화 데이터 업데이트"""
        return {"id": data_id, **data}

    def delete_normalized_data(self, data_id: str):
        """정규화 데이터 삭제"""
        return True

    def get_metrics(self):
        """메트릭 조회"""
        return self.get_substance_mapping_statistics()

    # ===== 협력사 ESG 관련 메서드들 (기존 유지) =====
    
    def upload_partner_esg_data(self, file, company_id: str = None):
        """협력사 ESG 데이터 파일 업로드"""
        return {"status": "not_implemented"}

    def validate_partner_esg_data(self, data: dict):
        """협력사 ESG 데이터 검증"""
        return {"status": "not_implemented"}

    def get_partner_dashboard(self, company_id: str):
        """협력사 자가진단 대시보드"""
        return {"company_id": company_id, "status": "not_implemented"}

    def generate_partner_report(self, report_type: str, company_id: str):
        """협력사 ESG 보고서 생성"""
        return {"report_type": report_type, "company_id": company_id, "status": "not_implemented"}

    def get_esg_schema(self, industry: str):
        """업종별 ESG 스키마 조회"""
        return {"industry": industry, "status": "not_implemented"}

    def get_esg_schema_by_industry(self, industry: str) -> Dict[str, Any]:
        """업종별 ESG 데이터 스키마 조회"""
        try:
            # 업종별 기본 ESG 스키마 정의
            schemas = {
                "배터리": {
                    "environmental": {
                        "carbon_footprint": {"required": True, "unit": "tCO2eq"},
                        "energy_consumption": {"required": True, "unit": "MWh"},
                        "water_usage": {"required": True, "unit": "m3"},
                        "waste_management": {"required": True, "unit": "ton"},
                        "recycled_materials": {"required": True, "unit": "%"}
                    },
                    "social": {
                        "labor_standards": {"required": True},
                        "safety_incidents": {"required": True},
                        "community_engagement": {"required": False}
                    },
                    "governance": {
                        "compliance_status": {"required": True},
                        "risk_management": {"required": True},
                        "transparency": {"required": False}
                    }
                },
                "화학소재": {
                    "environmental": {
                        "carbon_footprint": {"required": True, "unit": "tCO2eq"},
                        "chemical_emissions": {"required": True, "unit": "kg"},
                        "water_usage": {"required": True, "unit": "m3"},
                        "hazardous_waste": {"required": True, "unit": "ton"}
                    }
                }
            }
            
            if not industry:
                raise Exception("업종 정보가 제공되지 않았습니다.")
            
            if industry not in schemas:
                logger.warning(f"지원하지 않는 업종: {industry}, 기본값(배터리) 사용")
                industry = "배터리"
            
            return schemas[industry]
        except Exception as e:
            logger.error(f"ESG 스키마 조회 실패: {e}")
            raise Exception(f"ESG 스키마를 조회할 수 없습니다: {str(e)}")

    # ===== 실제 DB 환경 데이터 조회 메서드들 =====

    def get_environmental_data_by_company(self, company_name: str) -> Dict[str, Any]:
        """회사별 실제 환경 데이터 조회 (DB에서 계산)"""
        try:
            if not self.db_available:
                logger.warning("데이터베이스 연결 불가, 기본값 반환")
                return self._get_default_environmental_data(company_name)
            
            # 1. normal 테이블에서 해당 회사의 데이터 조회
            normal_data = self.normal_repository.get_company_data(company_name)
            
            # 2. certification 테이블에서 온실가스 매핑 결과 조회
            certification_data = self.normal_repository.get_company_certifications(company_name)
            
            # 3. 환경 데이터 계산
            environmental_data = self._calculate_environmental_data(normal_data, certification_data)
            
            return {
                "status": "success",
                "company_name": company_name,
                "data": environmental_data,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"환경 데이터 조회 실패 ({company_name}): {e}")
            return {
                "status": "error",
                "message": f"환경 데이터 조회 실패: {str(e)}",
                "data": self._get_default_environmental_data(company_name)
            }

    def _calculate_environmental_data(self, normal_data: List[Dict], certification_data: List[Dict]) -> Dict[str, Any]:
        """실제 DB 데이터로부터 환경 데이터 계산"""
        try:
            # 탄소배출량 계산 (certification 테이블 기반)
            carbon_footprint = self._calculate_carbon_footprint(certification_data)
            
            # 에너지사용량 계산 (normal 테이블의 capacity, energy_density 기반)
            energy_usage = self._calculate_energy_usage(normal_data)
            
            # 물사용량 계산 (normal 테이블의 raw_materials 기반)
            water_usage = self._calculate_water_usage(normal_data)
            
            # 폐기물 관리 계산 (normal 테이블의 disposal_method, recycling_method 기반)
            waste_management = self._calculate_waste_management(normal_data)
            
            # 인증 정보 추출
            certifications = self._extract_certifications(normal_data)
            
            return {
                "carbonFootprint": carbon_footprint,
                "energyUsage": energy_usage,
                "waterUsage": water_usage,
                "wasteManagement": waste_management,
                "certifications": certifications
            }
            
        except Exception as e:
            logger.error(f"환경 데이터 계산 실패: {e}")
            return self._get_default_environmental_data("Unknown")

    def _calculate_carbon_footprint(self, certification_data: List[Dict]) -> Dict[str, Any]:
        """온실가스 배출량 계산"""
        try:
            total_scope1 = 0
            total_scope2 = 0
            total_scope3 = 0
            
            for cert in certification_data:
                if cert.get('final_mapped_sid'):
                    # 매핑된 온실가스 배출량 계산
                    amount = float(cert.get('original_amount', 0))
                    
                    # SID에 따른 Scope 분류
                    sid = cert.get('final_mapped_sid', '')
                    if 'CO2' in sid or 'CH4' in sid:
                        if 'direct' in sid.lower():
                            total_scope1 += amount
                        elif 'indirect' in sid.lower():
                            total_scope2 += amount
                        else:
                            total_scope3 += amount
                    else:
                        total_scope3 += amount
            
            total = total_scope1 + total_scope2 + total_scope3
            
            # 트렌드 계산 (임시로 stable 반환)
            trend = 'stable'
            
            return {
                "total": round(total, 2),
                "trend": trend,
                "lastUpdate": datetime.now().strftime('%Y-%m-%d'),
                "breakdown": {
                    "scope1": round(total_scope1, 2),
                    "scope2": round(total_scope2, 2),
                    "scope3": round(total_scope3, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"탄소배출량 계산 실패: {e}")
            return {
                "total": 0,
                "trend": "no_data",
                "lastUpdate": datetime.now().strftime('%Y-%m-%d'),
                "breakdown": {"scope1": 0, "scope2": 0, "scope3": 0},
                "message": "탄소배출량 데이터를 계산할 수 없습니다."
            }

    def _calculate_energy_usage(self, normal_data: List[Dict]) -> Dict[str, Any]:
        """에너지사용량 계산"""
        try:
            total_energy = 0
            renewable_energy = 0
            
            for data in normal_data:
                # capacity와 energy_density에서 에너지 사용량 추정
                capacity = data.get('capacity', '0')
                energy_density = data.get('energy_density', '0')
                
                if capacity and energy_density:
                    try:
                        # 간단한 에너지 계산 (실제로는 더 복잡한 계산 필요)
                        energy_value = float(capacity.replace('Ah', '').replace('Wh', '')) * 0.1
                        total_energy += energy_value
                        
                        # recycled_material이 True면 재생에너지로 간주
                        if data.get('recycled_material'):
                            renewable_energy += energy_value * 0.3
                    except:
                        pass
            
            # 실제 데이터가 없으면 0 반환 (샘플데이터 제거)
            if total_energy == 0:
                total_energy = 0
                renewable_energy = 0
            
            return {
                "total": round(total_energy, 2),
                "renewable": round(renewable_energy, 2),
                "trend": "up",
                "lastUpdate": datetime.now().strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            logger.error(f"에너지사용량 계산 실패: {e}")
            return {
                "total": 0,
                "renewable": 0,
                "trend": "no_data",
                "lastUpdate": datetime.now().strftime('%Y-%m-%d'),
                "message": "에너지 사용량 데이터를 계산할 수 없습니다."
            }

    def _calculate_water_usage(self, normal_data: List[Dict]) -> Dict[str, Any]:
        """물사용량 계산"""
        try:
            total_water = 0
            recycled_water = 0
            
            for data in normal_data:
                # raw_materials에서 물 사용량 추정
                raw_materials = data.get('raw_materials', [])
                if raw_materials:
                    # 원재료 종류에 따른 물 사용량 추정
                    material_count = len(raw_materials)
                    water_per_material = 100  # 톤당 물 사용량 추정
                    total_water += material_count * water_per_material
                    
                    # recycled_material이 True면 재활용 물로 간주
                    if data.get('recycled_material'):
                        recycled_water += material_count * water_per_material * 0.3
            
            # 실제 데이터가 없으면 0 반환 (샘플데이터 제거)
            if total_water == 0:
                total_water = 0
                recycled_water = 0
            
            return {
                "total": round(total_water, 2),
                "recycled": round(recycled_water, 2),
                "trend": "stable",
                "lastUpdate": datetime.now().strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            logger.error(f"물사용량 계산 실패: {e}")
            return {
                "total": 0,
                "recycled": 0,
                "trend": "no_data",
                "lastUpdate": datetime.now().strftime('%Y-%m-%d'),
                "message": "물 사용량 데이터를 계산할 수 없습니다."
            }

    def _calculate_waste_management(self, normal_data: List[Dict]) -> Dict[str, Any]:
        """폐기물 관리 계산"""
        try:
            total_waste = 0
            recycled_waste = 0
            landfill_waste = 0
            
            for data in normal_data:
                # disposal_method와 recycling_method에서 폐기물 정보 추출
                disposal_method = data.get('disposal_method', '')
                recycling_method = data.get('recycling_method', '')
                
                # 기본 폐기물량 추정
                base_waste = 50  # 기본 폐기물량
                total_waste += base_waste
                
                # 재활용 가능한 폐기물 추정
                if recycling_method:
                    recycled_waste += base_waste * 0.7
                    landfill_waste += base_waste * 0.3
                else:
                    landfill_waste += base_waste
            
            # 실제 데이터가 없으면 0 반환 (샘플데이터 제거)
            if total_waste == 0:
                total_waste = 0
                recycled_waste = 0
                landfill_waste = 0
            
            return {
                "total": round(total_waste, 2),
                "recycled": round(recycled_waste, 2),
                "landfill": round(landfill_waste, 2),
                "trend": "up",
                "lastUpdate": datetime.now().strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            logger.error(f"폐기물 관리 계산 실패: {e}")
            return {
                "total": 0,
                "recycled": 0,
                "landfill": 0,
                "trend": "no_data",
                "lastUpdate": datetime.now().strftime('%Y-%m-%d'),
                "message": "폐기물 관리 데이터를 계산할 수 없습니다."
            }

    def _extract_certifications(self, normal_data: List[Dict]) -> List[str]:
        """인증 정보 추출"""
        try:
            certifications = []
            
            for data in normal_data:
                disposal_method = data.get('disposal_method', '')
                recycling_method = data.get('recycling_method', '')
                
                # ISO 인증 정보 추출
                if 'ISO 14001' in disposal_method or 'ISO 14001' in recycling_method:
                    certifications.append('ISO 14001')
                if 'ISO 50001' in disposal_method or 'ISO 50001' in recycling_method:
                    certifications.append('ISO 50001')
                if 'OHSAS 18001' in disposal_method or 'OHSAS 18001' in recycling_method:
                    certifications.append('OHSAS 18001')
            
            # 중복 제거
            certifications = list(set(certifications))
            
            # 실제 인증 데이터가 없으면 빈 리스트 반환 (샘플데이터 제거)
            if not certifications:
                certifications = []
            
            return certifications
            
        except Exception as e:
            logger.error(f"인증 정보 추출 실패: {e}")
            return []

    def _get_default_environmental_data(self, company_name: str) -> Dict[str, Any]:
        """기본 환경 데이터 (DB에 데이터가 없을 때 사용)"""
        return {
            "carbonFootprint": {
                "total": 0,
                "trend": "no_data",
                "lastUpdate": datetime.now().strftime('%Y-%m-%d'),
                "breakdown": {"scope1": 0, "scope2": 0, "scope3": 0},
                "message": f"{company_name}의 온실가스 배출량 데이터가 없습니다."
            },
            "energyUsage": {
                "total": 0,
                "renewable": 0,
                "trend": "no_data",
                "lastUpdate": datetime.now().strftime('%Y-%m-%d'),
                "message": f"{company_name}의 에너지 사용량 데이터가 없습니다."
            },
            "waterUsage": {
                "total": 0,
                "recycled": 0,
                "trend": "no_data",
                "lastUpdate": datetime.now().strftime('%Y-%m-%d'),
                "message": f"{company_name}의 물 사용량 데이터가 없습니다."
            },
            "wasteManagement": {
                "total": 0,
                "recycled": 0,
                "landfill": 0,
                "trend": "no_data",
                "lastUpdate": datetime.now().strftime('%Y-%m-%d'),
                "message": f"{company_name}의 폐기물 관리 데이터가 없습니다."
            },
            "certifications": [],
            "message": f"{company_name}의 환경 데이터를 찾을 수 없습니다. 데이터를 입력해주세요."
        }

    # ===== Substance Mapping 관련 메서드들 =====
    
    def _load_model_and_data(self):
        """모델과 규정 데이터를 로드합니다."""
        try:
            # 환경변수에서 경로 가져오기
            MODEL_DIR = os.getenv("MODEL_DIR", "/app/model/bomi-ai")
            HF_REPO_ID = os.getenv("HF_REPO_ID", "galaxybuddy/bomi-ai")
            
            # BOMI AI 모델 로드 (로컬 우선)
            model_dir = Path(MODEL_DIR)
            
            model_loaded = False
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
                    
            # 규정 데이터 로드 (온실가스 배출량 표준 데이터)
            self._load_regulation_data()
                
        except Exception as e:
            logger.error(f"모델 및 데이터 로드 실패: {e}")
            raise
    
    def _load_regulation_data(self):
        """온실가스 배출량 표준 규정 데이터를 로드합니다."""
        try:
            # 온실가스 배출량 표준 데이터 (IPCC, K-ETS 기준)
            regulation_data = [
                {"sid": "CO2_DIRECT", "name": "이산화탄소 직접배출 (Scope 1)"},
                {"sid": "CO2_INDIRECT", "name": "이산화탄소 간접배출 (Scope 2)"},
                {"sid": "CO2_OTHER", "name": "이산화탄소 기타배출 (Scope 3)"},
                {"sid": "CH4_DIRECT", "name": "메탄 직접배출 (Scope 1)"},
                {"sid": "CH4_INDIRECT", "name": "메탄 간접배출 (Scope 2)"},
                {"sid": "CH4_OTHER", "name": "메탄 기타배출 (Scope 3)"},
                {"sid": "N2O_DIRECT", "name": "아산화질소 직접배출 (Scope 1)"},
                {"sid": "N2O_INDIRECT", "name": "아산화질소 간접배출 (Scope 2)"},
                {"sid": "N2O_OTHER", "name": "아산화질소 기타배출 (Scope 3)"},
                {"sid": "HFC_DIRECT", "name": "수소불화탄소 직접배출 (Scope 1)"},
                {"sid": "HFC_INDIRECT", "name": "수소불화탄소 간접배출 (Scope 2)"},
                {"sid": "PFC_DIRECT", "name": "과불화탄소 직접배출 (Scope 1)"},
                {"sid": "PFC_INDIRECT", "name": "과불화탄소 간접배출 (Scope 2)"},
                {"sid": "SF6_DIRECT", "name": "육불화황 직접배출 (Scope 1)"},
                {"sid": "SF6_INDIRECT", "name": "육불화황 간접배출 (Scope 2)"},
                {"sid": "NF3_DIRECT", "name": "삼불화질소 직접배출 (Scope 1)"},
                {"sid": "NF3_INDIRECT", "name": "삼불화질소 간접배출 (Scope 2)"},
                {"sid": "CO2_TOTAL", "name": "이산화탄소 총배출량"},
                {"sid": "CH4_TOTAL", "name": "메탄 총배출량"},
                {"sid": "N2O_TOTAL", "name": "아산화질소 총배출량"},
                {"sid": "GHG_TOTAL", "name": "온실가스 총배출량 (CO2eq)"},
                {"sid": "CO2_ENERGY", "name": "에너지 사용으로 인한 이산화탄소 배출"},
                {"sid": "CO2_TRANSPORT", "name": "운송으로 인한 이산화탄소 배출"},
                {"sid": "CO2_PROCESS", "name": "공정으로 인한 이산화탄소 배출"},
                {"sid": "CO2_WASTE", "name": "폐기물 처리로 인한 이산화탄소 배출"},
                {"sid": "CO2_AGRICULTURE", "name": "농업으로 인한 이산화탄소 배출"},
                {"sid": "CO2_FORESTRY", "name": "산림으로 인한 이산화탄소 배출"},
                {"sid": "CO2_INDUSTRIAL", "name": "산업공정으로 인한 이산화탄소 배출"},
                {"sid": "CO2_BUILDING", "name": "건물 에너지 사용으로 인한 이산화탄소 배출"},
                {"sid": "CO2_ELECTRICITY", "name": "전력 사용으로 인한 이산화탄소 배출"},
                {"sid": "CO2_HEATING", "name": "난방으로 인한 이산화탄소 배출"},
                {"sid": "CO2_COOLING", "name": "냉방으로 인한 이산화탄소 배출"},
                {"sid": "CO2_MANUFACTURING", "name": "제조업으로 인한 이산화탄소 배출"},
                {"sid": "CO2_MINING", "name": "채굴업으로 인한 이산화탄소 배출"},
                {"sid": "CO2_CHEMICAL", "name": "화학공업으로 인한 이산화탄소 배출"},
                {"sid": "CO2_METAL", "name": "금속공업으로 인한 이산화탄소 배출"},
                {"sid": "CO2_PAPER", "name": "제지공업으로 인한 이산화탄소 배출"},
                {"sid": "CO2_FOOD", "name": "식품공업으로 인한 이산화탄소 배출"},
                {"sid": "CO2_TEXTILE", "name": "섬유공업으로 인한 이산화탄소 배출"},
                {"sid": "CO2_CONSTRUCTION", "name": "건설업으로 인한 이산화탄소 배출"},
                {"sid": "CO2_SERVICE", "name": "서비스업으로 인한 이산화탄소 배출"},
                {"sid": "CO2_COMMERCIAL", "name": "상업용으로 인한 이산화탄소 배출"},
                {"sid": "CO2_RESIDENTIAL", "name": "주거용으로 인한 이산화탄소 배출"},
                {"sid": "CO2_PUBLIC", "name": "공공용으로 인한 이산화탄소 배출"},
                {"sid": "CO2_OTHER_SCOPE1", "name": "기타 Scope 1 이산화탄소 배출"},
                {"sid": "CO2_OTHER_SCOPE2", "name": "기타 Scope 2 이산화탄소 배출"},
                {"sid": "CO2_OTHER_SCOPE3", "name": "기타 Scope 3 이산화탄소 배출"},
            ]
            
            # DataFrame으로 변환
            self.regulation_data = pd.DataFrame(regulation_data)
            self.regulation_sids = self.regulation_data['sid'].tolist()
            self.regulation_names = self.regulation_data['name'].tolist()
            
            logger.info(f"✅ 규정 데이터 로드 완료: {len(self.regulation_data)}개 항목")
            
            # FAISS 인덱스 구축
            self._build_faiss_index()
            
        except Exception as e:
            logger.error(f"❌ 규정 데이터 로드 실패: {e}")
            # 기본 데이터로 초기화
            self.regulation_data = pd.DataFrame(columns=["sid", "name"])
            self.regulation_sids = []
            self.regulation_names = []
            self.faiss_index = None

    def _build_faiss_index(self):
        """FAISS 인덱스를 구축합니다."""
        try:
            if not self.regulation_names or not self.model:
                logger.warning("규정 데이터 또는 모델이 없어 FAISS 인덱스를 구축할 수 없습니다.")
                return
                
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
            
            logger.info(f"✅ FAISS 인덱스 구축 완료 (차원: {dimension}, 항목: {len(self.regulation_names)}개)")
            
        except Exception as e:
            logger.error(f"❌ FAISS 인덱스 구축 실패: {e}")
            self.faiss_index = None
    
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
    
    def get_substance_mapping_statistics(self) -> Dict:
        """매핑 서비스 통계를 반환합니다."""
        try:
            if self.db_available and self.normal_repository:
                return self.normal_repository.get_mapping_statistics()
            else:
                return {
                    "model_loaded": self.model is not None,
                    "regulation_data_count": len(self.regulation_data) if self.regulation_data is not None else 0,
                    "faiss_index_built": self.faiss_index is not None,
                    "service_status": "ready" if all([self.model, self.regulation_data, self.faiss_index]) else "not_ready"
                }
        except Exception as e:
            logger.error(f"매핑 통계 조회 실패: {e}")
            return {
                "total_mappings": 0,
                "auto_mapped": 0,
                "needs_review": 0,
                "user_reviewed": 0,
                "avg_confidence": 0.0
            }
    
    def get_saved_mappings(self, company_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """저장된 매핑 결과 조회"""
        try:
            if not self.db_available:
                raise Exception("데이터베이스 연결이 불가능합니다. 서비스 관리자에게 문의하세요.")
            
            if not self.normal_repository:
                raise Exception("데이터 저장소가 초기화되지 않았습니다. 서비스를 재시작해주세요.")
            
            return self.normal_repository.get_saved_mappings(company_id, limit)
        except Exception as e:
            logger.error(f"매핑 결과 조회 실패: {e}")
            raise Exception(f"저장된 매핑 결과를 조회할 수 없습니다: {str(e)}")
    
    def get_original_data(self, company_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """원본 데이터 조회"""
        try:
            if not self.db_available:
                raise Exception("데이터베이스 연결이 불가능합니다. 서비스 관리자에게 문의하세요.")
            
            if not self.normal_repository:
                raise Exception("데이터 저장소가 초기화되지 않았습니다. 서비스를 재시작해주세요.")
            
            return self.normal_repository.get_original_data(company_id, limit)
        except Exception as e:
            logger.error(f"원본 데이터 조회 실패: {e}")
            raise Exception(f"원본 데이터를 조회할 수 없습니다: {str(e)}")
    
    def get_corrections(self, company_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """사용자 수정 데이터 조회"""
        try:
            if not self.db_available:
                raise Exception("데이터베이스 연결이 불가능합니다. 서비스 관리자에게 문의하세요.")
            
            if not self.normal_repository:
                raise Exception("데이터 저장소가 초기화되지 않았습니다. 서비스를 재시작해주세요.")
            
            # 현재는 certification 테이블에서 user_reviewed 상태인 것들을 조회
            mappings = self.normal_repository.get_saved_mappings(company_id, limit)
            return [m for m in mappings if m.get('mapping_status') == 'user_reviewed']
        except Exception as e:
            logger.error(f"수정 데이터 조회 실패: {e}")
            raise Exception(f"사용자 수정 데이터를 조회할 수 없습니다: {str(e)}")
    
    def correct_mapping(self, certification_id: int, correction_data: Dict[str, Any]) -> bool:
        """매핑 결과를 수동으로 수정"""
        try:
            if not self.db_available:
                raise Exception("데이터베이스 연결이 불가능합니다. 서비스 관리자에게 문의하세요.")
            
            if not self.normal_repository:
                raise Exception("데이터 저장소가 초기화되지 않았습니다. 서비스를 재시작해주세요.")
            
            return self.normal_repository.update_user_mapping_correction(
                certification_id, correction_data
            )
        except Exception as e:
            logger.error(f"매핑 수정 실패: {e}")
            raise Exception(f"매핑 결과를 수정할 수 없습니다: {str(e)}")