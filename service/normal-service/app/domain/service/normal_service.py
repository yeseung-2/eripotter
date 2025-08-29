from eripotter_common.database.base import get_db_engine
import logging
from datetime import datetime
from typing import Dict, List
from ..repository.substance_mapping_repository import SubstanceMappingRepository
from .substance_mapping_service import SubstanceMappingService
from .data_normalization_service import DataNormalizationService

from .interfaces import ISubstanceMapping, IDataNormalization, IESGValidation

logger = logging.getLogger("normal-service")

class NormalService(ISubstanceMapping, IDataNormalization, IESGValidation):
    """통합 Normal 서비스 - 기능별 서비스들을 조율"""
    
    def __init__(self):
        # 데이터베이스 연결을 선택적으로 시도
        self.engine = None
        self.substance_mapping_repository = None
        self.db_available = False
        
        try:
            self.engine = get_db_engine()
            self.substance_mapping_repository = SubstanceMappingRepository(self.engine)
            self.db_available = True
            logger.info("✅ 데이터베이스 연결 성공")
        except Exception as e:
            logger.warning(f"⚠️ 데이터베이스 연결 실패: {e}")
            logger.info("📝 AI 매핑만 사용합니다 (결과 저장 불가)")
        
        # 기능별 서비스 초기화
        self.substance_mapping_service = SubstanceMappingService()
        self.data_normalization_service = DataNormalizationService()


    def get_all_normalized_data(self):
        """모든 정규화 데이터 조회"""
        return []

    def get_normalized_data_by_id(self, data_id: str):
        """특정 정규화 데이터 조회"""
        return {"id": data_id}

    def upload_and_normalize_excel(self, file):
        """엑셀 파일 업로드 및 AI 자동 매핑"""
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
            
            # 2단계: 데이터베이스에 원본 데이터 저장
            upload_result = {"status": "database_not_available"}
            if self.db_available:
                try:
                    upload_result = self.substance_mapping_repository.save_original_data(
                        filename=file.filename,
                        data=normalization_result['normalized_data'],
                        file_size=len(content)
                    )
                    logger.info("💾 원본 데이터를 normal 테이블에 저장했습니다")
                except Exception as e:
                    logger.warning(f"⚠️ 원본 데이터 저장 실패: {e}")
                    upload_result = {"error": str(e)}
            
            # 3단계: AI 자동 매핑 수행
            substance_names = [row['substance_name'] for row in normalization_result['normalized_data']]
            mapping_results = []
            
            if substance_names:
                logger.info(f"🤖 AI 자동 매핑 시작: {len(substance_names)}개 물질")
                mapping_results = self.map_substances_batch(substance_names)
                logger.info(f"✅ AI 자동 매핑 완료: {len(mapping_results)}개 결과")
            
            return {
                "filename": file.filename,
                "status": "uploaded_and_mapped",
                "normalization": normalization_result,
                "mapping_results": mapping_results,
                "database_save": upload_result,
                "message": "원본 데이터는 normal 테이블, AI 매핑 결과는 certification 테이블에 저장됩니다"
            }
            
        except Exception as e:
            logger.error(f"❌ 엑셀 파일 업로드 및 매핑 실패: {e}")
            return {
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            }

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
        return {}
    
    # ===== 물질 매핑 관련 메서드들 =====
    
    # ===== ISubstanceMapping 인터페이스 구현 =====
    
    def map_substance(self, substance_name: str, company_id: str = None) -> dict:
        """단일 물질 매핑"""
        try:
            logger.info(f"📝 물질 매핑 요청: {substance_name}")
            
            # AI 매핑 수행
            mapping_result = self.substance_mapping_service.map_substance(substance_name)
            
            # 회사 정보 추가
            if company_id:
                mapping_result['company_id'] = company_id
            
            # 데이터베이스에 결과 저장
            if mapping_result['status'] == 'success' and self.db_available:
                self.substance_mapping_repository.save_mapping_result(mapping_result)
            
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
        """배치 물질 매핑"""
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
            
            # 성공한 매핑 결과들을 데이터베이스에 저장
            if result['status'] == 'success':
                for mapping_result in result.get('mapping_results', []):
                    if mapping_result['status'] == 'success':
                        self.substance_mapping_repository.save_mapping_result(mapping_result)
            
            logger.info(f"✅ 파일 매핑 완료: {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 파일 매핑 실패: {e}")
            return {
                "file_path": file_path,
                "status": "error",
                "error": str(e)
            }
    
    def get_mapping_statistics(self) -> dict:
        """물질 매핑 통계 조회"""
        try:
            # AI 서비스 통계
            ai_stats = self.substance_mapping_service.get_mapping_statistics()
            
            # 데이터베이스 통계
            db_stats = self.substance_mapping_repository.get_mapping_statistics()
            
            # 통합 통계
            combined_stats = {
                "ai_service": ai_stats,
                "database": db_stats,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info("✅ 물질 매핑 통계 조회 완료")
            return combined_stats
            
        except Exception as e:
            logger.error(f"❌ 물질 매핑 통계 조회 실패: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    # ===== IDataNormalization 인터페이스 구현 =====
    
    def normalize_excel_data(self, file_data: bytes, filename: str, company_id: str = None) -> Dict:
        """엑셀 데이터 정규화"""
        return self.data_normalization_service.normalize_excel_data(file_data, filename, company_id)
    
    def validate_data_structure(self, data: Dict) -> Dict:
        """데이터 구조 검증"""
        return self.data_normalization_service.validate_data_structure(data)
    
    def standardize_data(self, data: Dict) -> Dict:
        """데이터 표준화"""
        return self.data_normalization_service.standardize_data(data)
    
    # ===== IESGValidation 인터페이스 구현 =====
    
    def validate_esg_data(self, data: Dict, industry: str = None) -> Dict:
        """ESG 데이터 검증"""
        return self.esg_validation_service.validate_esg_data(data, industry)
    
    def calculate_esg_score(self, data: Dict) -> int:
        """ESG 점수 계산"""
        return self.esg_validation_service.calculate_esg_score(data)
    
    def generate_esg_report(self, company_id: str, report_type: str) -> Dict:
        """ESG 보고서 생성"""
        return self.esg_validation_service.generate_esg_report(company_id, report_type)
    
    def correct_mapping(self, mapping_id: int, correction_data: dict) -> bool:
        """매핑 결과 수동 수정"""
        try:
            logger.info(f"📝 매핑 수정 요청: mapping_id {mapping_id}")
            
            # 수정 데이터 검증
            required_fields = ["corrected_sid", "corrected_name", "correction_reason"]
            for field in required_fields:
                if field not in correction_data:
                    logger.error(f"❌ 필수 필드 누락: {field}")
                    return False
            
            # 수정 결과를 데이터베이스에 저장
            if self.db_available:
                success = self.substance_mapping_repository.save_mapping_correction(mapping_id, correction_data)
                
                if success:
                    logger.info(f"✅ 매핑 수정 완료: mapping_id {mapping_id}")
                    logger.info(f"   - 수정된 SID: {correction_data['corrected_sid']}")
                    logger.info(f"   - 수정된 이름: {correction_data['corrected_name']}")
                    logger.info(f"   - 수정 이유: {correction_data['correction_reason']}")
                else:
                    logger.error(f"❌ 매핑 수정 실패: mapping_id {mapping_id}")
                
                return success
            else:
                logger.warning("⚠️ 데이터베이스 연결 불가로 수정 사항을 저장할 수 없습니다")
                return False
            
        except Exception as e:
            logger.error(f"❌ 매핑 수정 실패: {e}")
            return False

    # ===== 협력사 ESG 데이터 관련 비즈니스 로직 =====

    def upload_partner_esg_file(self, file, company_id: str = None):
        """협력사 ESG 데이터 파일 업로드 처리"""
        import uuid
        
        # 업로드 ID 생성
        upload_id = str(uuid.uuid4())
        
        # 파일 정보 저장 (실제로는 DB에 저장)
        file_info = {
            "upload_id": upload_id,
            "filename": file.filename,
            "size": file.size,
            "company_id": company_id,
            "upload_time": datetime.now().isoformat(),
            "status": "uploaded"
        }
        
        # 파일 내용 읽기 (실제로는 파일 시스템에 저장)
        content = file.file.read()
        
        # 로깅
        logger.info(f"파일 업로드 완료: {file.filename} (크기: {file.size} bytes)")
        
        return file_info

    def validate_partner_esg_data(self, data: dict):
        """협력사 ESG 데이터 검증 및 표준화"""
        validation_result = {
            "is_valid": True,
            "issues": [],
            "standardized_data": {},
            "esg_score": 0,
            "completion_rate": 0
        }
        
        # ESG 데이터 검증 로직
        required_fields = ["environmental", "social", "governance"]
        
        for field in required_fields:
            if field not in data:
                validation_result["is_valid"] = False
                validation_result["issues"].append({
                    "field": field,
                    "message": f"{field} 데이터가 누락되었습니다."
                })
        
        # ESG 점수 계산 (예시)
        if validation_result["is_valid"]:
            validation_result["esg_score"] = self._calculate_esg_score(data)
            validation_result["completion_rate"] = self._calculate_completion_rate(data)
            validation_result["standardized_data"] = self._standardize_esg_data(data)
        
        return validation_result

    def get_partner_dashboard_data(self, company_id: str):
        """협력사 ESG 자가진단 대시보드 데이터 조회"""
        # 실제로는 DB에서 조회
        dashboard_data = {
            "company_id": company_id,
            "esg_score": 87,
            "completion_rate": 80,  # 24/30
            "improvement_items": 6,
            "next_deadline": "2024-02-15",
            "categories": {
                "environmental": {
                    "score": 85,
                    "completed_items": ["탄소 배출량", "폐기물 관리"],
                    "in_progress": ["에너지 효율성"],
                    "not_started": []
                },
                "social": {
                    "score": 75,
                    "completed_items": ["노동 조건"],
                    "in_progress": ["커뮤니티 참여"],
                    "not_started": ["공급망 관리"]
                },
                "governance": {
                    "score": 90,
                    "completed_items": ["이사회 구성", "윤리 경영"],
                    "in_progress": ["투명성"],
                    "not_started": []
                }
            }
        }
        
        return dashboard_data

    def generate_partner_esg_report(self, report_type: str, company_id: str):
        """협력사 ESG 보고서 자동 생성"""
        report_data = {
            "report_id": f"REP_{company_id}_{report_type}_{int(datetime.now().timestamp())}",
            "company_id": company_id,
            "report_type": report_type,
            "generated_at": datetime.now().isoformat(),
            "content": {
                "summary": f"{company_id}의 {report_type} 보고서",
                "esg_score": 87,
                "recommendations": [
                    "공급망 관리 강화 필요",
                    "에너지 효율성 개선 권장",
                    "투명성 제고 방안 검토"
                ]
            }
        }
        
        return report_data

    def get_esg_schema_by_industry(self, industry: str):
        """업종별 ESG 데이터 스키마 조회"""
        schemas = {
            "general": {
                "environmental": ["탄소 배출량", "에너지 사용량", "폐기물 관리", "수자원 관리"],
                "social": ["노동 조건", "안전 관리", "공급망 관리", "커뮤니티 참여"],
                "governance": ["이사회 구성", "윤리 경영", "투명성", "리스크 관리"]
            },
            "battery": {
                "environmental": ["배터리 재활용", "희토류 관리", "에너지 효율성", "탄소 배출량"],
                "social": ["안전 관리", "공급망 투명성", "노동 조건", "지역 사회 기여"],
                "governance": ["이사회 다양성", "윤리 경영", "투명성", "지속가능성 정책"]
            },
            "chemical": {
                "environmental": ["화학 물질 관리", "폐수 처리", "대기 오염 관리", "안전 관리"],
                "social": ["안전 교육", "공급망 관리", "지역 사회 관계", "노동 조건"],
                "governance": ["안전 정책", "윤리 경영", "투명성", "리스크 관리"]
            }
        }
        
        return schemas.get(industry, schemas["general"])

    def _calculate_esg_score(self, data: dict) -> int:
        """ESG 점수 계산"""
        # 간단한 점수 계산 로직 (실제로는 더 복잡한 알고리즘 사용)
        score = 0
        total_items = 0
        
        for category in ["environmental", "social", "governance"]:
            if category in data:
                category_data = data[category]
                if isinstance(category_data, dict):
                    score += len(category_data) * 10
                    total_items += len(category_data)
        
        return min(100, score) if total_items > 0 else 0

    def _calculate_completion_rate(self, data: dict) -> int:
        """완료율 계산"""
        completed = 0
        total = 30  # 총 30개 항목
        
        for category in ["environmental", "social", "governance"]:
            if category in data:
                category_data = data[category]
                if isinstance(category_data, dict):
                    completed += len(category_data)
        
        return min(100, int((completed / total) * 100))

    def _standardize_esg_data(self, data: dict) -> dict:
        """ESG 데이터 표준화"""
        standardized = {}
        
        # 데이터 표준화 로직
        for category, category_data in data.items():
            if isinstance(category_data, dict):
                standardized[category] = {}
                for key, value in category_data.items():
                    # 키 이름 표준화
                    standardized_key = self._standardize_field_name(key)
                    standardized[category][standardized_key] = value
        
        return standardized

    def _standardize_field_name(self, field_name: str) -> str:
        """필드명 표준화"""
        # 간단한 표준화 로직
        field_mapping = {
            "탄소배출량": "carbon_emissions",
            "에너지효율성": "energy_efficiency",
            "폐기물관리": "waste_management",
            "노동조건": "labor_conditions",
            "공급망관리": "supply_chain_management",
            "이사회구성": "board_composition",
            "윤리경영": "ethical_management"
        }
        
        return field_mapping.get(field_name, field_name)