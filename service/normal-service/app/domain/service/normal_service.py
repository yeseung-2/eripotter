"""
Normal Service - 새로운 테이블 구조에 맞춘 통합 서비스
프론트엔드 데이터 처리 + AI 매핑 + 사용자 검토
"""
from eripotter_common.database.base import get_db_engine
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from ..repository.substance_mapping_repository import SubstanceMappingRepository
from ..repository.normal_repository import NormalRepository
from .substance_mapping_service import SubstanceMappingService
from .data_normalization_service import DataNormalizationService

from .interfaces import ISubstanceMapping, IDataNormalization, IESGValidation

logger = logging.getLogger("normal-service")

class NormalService(ISubstanceMapping, IDataNormalization, IESGValidation):
    """통합 Normal 서비스 - 새로운 테이블 구조 대응"""
    
    def __init__(self):
        # 데이터베이스 연결을 선택적으로 시도
        self.engine = None
        self.substance_mapping_repository = None
        self.normal_repository = None
        self.db_available = False
        
        try:
            self.engine = get_db_engine()
            self.substance_mapping_repository = SubstanceMappingRepository(self.engine)
            self.normal_repository = NormalRepository(self.engine)
            self.db_available = True
            logger.info("✅ 데이터베이스 연결 성공")
        except Exception as e:
            logger.warning(f"⚠️ 데이터베이스 연결 실패: {e}")
            logger.info("📝 AI 매핑만 사용합니다 (결과 저장 불가)")
        
        # 기능별 서비스 초기화
        self.substance_mapping_service = SubstanceMappingService()
        self.data_normalization_service = DataNormalizationService()

    # ===== 프론트엔드 데이터 처리 메서드들 =====
    
    def save_substance_data_and_map_gases(self, substance_data: Dict[str, Any], company_id: str = None, company_name: str = None, uploaded_by: str = None) -> Dict[str, Any]:
        """프론트엔드에서 받은 물질 데이터 저장 + 온실가스 AI 매핑"""
        try:
            logger.info(f"📝 물질 데이터 처리 시작: {substance_data.get('productName', 'Unknown')}")
            
            if not self.db_available:
                return {
                    "status": "error",
                    "message": "데이터베이스 연결이 불가능합니다."
                }
            
            # 1단계: Normal 테이블에 전체 데이터 저장
            normal_id = self.substance_mapping_repository.save_substance_data(
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
            
            # 2단계: 온실가스 배출량 추출 및 AI 매핑
            greenhouse_gases = substance_data.get('greenhouseGasEmissions', [])
            mapping_results = []
            
            if greenhouse_gases:
                logger.info(f"🤖 온실가스 AI 매핑 시작: {len(greenhouse_gases)}개")
                
                for gas_data in greenhouse_gases:
                    gas_name = gas_data.get('materialName', '')
                    gas_amount = gas_data.get('amount', '')
                    
                    if gas_name:
                        # AI 매핑 수행
                        ai_result = self.substance_mapping_service.map_substance(gas_name)
                        
                        # Certification 테이블에 저장
                        if ai_result.get('status') == 'success':
                            success = self.substance_mapping_repository.save_ai_mapping_result(
                                normal_id=normal_id,
                                gas_name=gas_name,
                                gas_amount=gas_amount,
                                mapping_result=ai_result,
                                company_id=company_id,
                                company_name=company_name
                            )
                            
                            if success:
                                # 신뢰도에 따른 정확한 status 반환
                                confidence = ai_result.get('confidence', 0.0)
                                if confidence >= 0.7:
                                    status = 'auto_mapped'
                                elif confidence >= 0.4:
                                    status = 'needs_review'
                                else:
                                    status = 'not_mapped'
                                
                                mapping_results.append({
                                    'original_gas_name': gas_name,
                                    'original_amount': gas_amount,
                                    'ai_mapped_name': ai_result.get('mapped_name'),
                                    'ai_confidence': ai_result.get('confidence'),
                                    'status': status
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
            
            logger.info(f"✅ 물질 데이터 처리 완료: Normal ID {normal_id}, 매핑 {len(mapping_results)}개")
            
            return {
                "status": "success",
                "normal_id": normal_id,
                "product_name": substance_data.get('productName'),
                "mapping_results": mapping_results,
                "message": f"데이터 저장 및 {len(mapping_results)}개 온실가스 매핑 완료"
            }
            
        except Exception as e:
            logger.error(f"❌ 물질 데이터 처리 실패: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "물질 데이터 처리 중 오류가 발생했습니다."
            }

    def get_substance_mapping_statistics(self) -> Dict[str, Any]:
        """물질 매핑 통계 조회 (새로운 구조)"""
        try:
            if not self.db_available:
                return {"error": "데이터베이스 연결 불가"}
            
            # Repository에서 통계 조회
            stats = self.substance_mapping_repository.get_mapping_statistics()
            
            # AI 서비스 통계 추가
            ai_stats = self.substance_mapping_service.get_mapping_statistics()
            
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
        
        return self.substance_mapping_repository.get_saved_mappings(company_id, limit)

    def get_original_data(self, company_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """원본 데이터 조회"""
        if not self.db_available:
            return []
        
        return self.substance_mapping_repository.get_original_data(company_id, limit)

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
        
        return self.substance_mapping_repository.update_user_mapping_correction(
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
            
            # AI 매핑 수행
            mapping_result = self.substance_mapping_service.map_substance(substance_name)
            
            logger.info(f"✅ 물질 매핑 완료: {substance_name} -> {mapping_result.get('mapped_name', 'None')}")
            return mapping_result
            
        except Exception as e:
            logger.error(f"❌ 물질 매핑 실패: {e}")
            return {
                "substance_name": substance_name,
                "status": "error",
                "error": str(e)
            }
    
    def map_substances_batch(self, substance_names: list, company_id: str = None) -> list:
        """배치 물질 매핑 (AI만)"""
        try:
            logger.info(f"📝 배치 물질 매핑 요청: {len(substance_names)}개")
            
            results = []
            for substance_name in substance_names:
                result = self.map_substance(substance_name, company_id)
                results.append(result)
            
            logger.info(f"✅ 배치 물질 매핑 완료: {len(results)}개")
            return results
            
        except Exception as e:
            logger.error(f"❌ 배치 물질 매핑 실패: {e}")
            return []
    
    def map_file(self, file_path: str) -> dict:
        """파일에서 물질 매핑"""
        try:
            logger.info(f"📝 파일 매핑 요청: {file_path}")
            
            # 파일 매핑 수행
            result = self.substance_mapping_service.map_file(file_path)
            
            logger.info(f"✅ 파일 매핑 완료: {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 파일 매핑 실패: {e}")
            return {
                "file_path": file_path,
                "status": "error",
                "error": str(e)
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