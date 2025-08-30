"""
Data Normalization Service - 데이터 정규화 전용 서비스
"""
import pandas as pd
import io
import logging
from typing import Dict, List, Optional
from datetime import datetime
from .interfaces import IDataNormalization

logger = logging.getLogger("data-normalization-service")


class DataNormalizationService(IDataNormalization):
    """데이터 정규화 전용 서비스"""
    
    def __init__(self):
        self.supported_formats = ['.xlsx', '.xls', '.csv']
        self.required_columns = ['substance_name', 'usage_amount']
        self.optional_columns = ['usage_unit', 'company_id', 'company_name']
    
    def normalize_excel_data(self, file_data: bytes, filename: str, company_id: str = None) -> Dict:
        """엑셀 데이터 정규화"""
        try:
            logger.info(f"📝 엑셀 데이터 정규화 시작: {filename}")
            
            # 파일 형식 검증
            if not self._validate_file_format(filename):
                return {
                    "status": "error",
                    "error": f"지원하지 않는 파일 형식입니다. 지원 형식: {', '.join(self.supported_formats)}"
                }
            
            # 파일 읽기
            df = pd.read_excel(io.BytesIO(file_data))
            
            # 데이터 구조 검증
            validation_result = self.validate_data_structure(df.to_dict('records'))
            if not validation_result['is_valid']:
                return {
                    "status": "error",
                    "error": "데이터 구조가 올바르지 않습니다",
                    "validation_issues": validation_result['issues']
                }
            
            # 데이터 표준화
            normalized_data = self.standardize_data(df.to_dict('records'))
            
            # 메타데이터 추가
            result = {
                "status": "success",
                "filename": filename,
                "file_size": len(file_data),
                "rows": len(df),
                "columns": list(df.columns),
                "normalized_data": normalized_data,
                "company_id": company_id,
                "processed_at": datetime.now().isoformat()
            }
            
            logger.info(f"✅ 엑셀 데이터 정규화 완료: {len(normalized_data)}개 행")
            return result
            
        except Exception as e:
            logger.error(f"❌ 엑셀 데이터 정규화 실패: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def validate_data_structure(self, data: List[Dict]) -> Dict:
        """데이터 구조 검증"""
        issues = []
        
        if not data:
            issues.append("데이터가 비어있습니다")
            return {"is_valid": False, "issues": issues}
        
        # 첫 번째 행으로 컬럼 구조 확인
        first_row = data[0]
        
        # 필수 컬럼 확인
        for required_col in self.required_columns:
            if required_col not in first_row:
                issues.append(f"필수 컬럼이 누락되었습니다: {required_col}")
        
        # 데이터 타입 검증
        for i, row in enumerate(data):
            if 'usage_amount' in row and not self._is_numeric(row['usage_amount']):
                issues.append(f"행 {i+1}: usage_amount가 숫자가 아닙니다")
            
            if 'substance_name' in row and not row['substance_name']:
                issues.append(f"행 {i+1}: substance_name이 비어있습니다")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues
        }
    
    def standardize_data(self, data: List[Dict]) -> List[Dict]:
        """데이터 표준화"""
        standardized_data = []
        
        for row in data:
            standardized_row = {}
            
            # 기본 필드 표준화
            standardized_row['substance_name'] = str(row.get('substance_name', '')).strip()
            standardized_row['usage_amount'] = self._standardize_amount(row.get('usage_amount', 0))
            standardized_row['usage_unit'] = self._standardize_unit(row.get('usage_unit', 'kg'))
            
            # 회사 정보 표준화
            if 'company_id' in row:
                standardized_row['company_id'] = str(row['company_id']).strip()
            if 'company_name' in row:
                standardized_row['company_name'] = str(row['company_name']).strip()
            
            # 빈 행 제외
            if standardized_row['substance_name']:
                standardized_data.append(standardized_row)
        
        return standardized_data
    
    def _validate_file_format(self, filename: str) -> bool:
        """파일 형식 검증"""
        return any(filename.lower().endswith(fmt) for fmt in self.supported_formats)
    
    def _is_numeric(self, value) -> bool:
        """숫자 여부 확인"""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def _standardize_amount(self, amount) -> float:
        """사용량 표준화"""
        try:
            return float(amount) if amount else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def _standardize_unit(self, unit: str) -> str:
        """단위 표준화"""
        unit_mapping = {
            'kg': 'kg', 'kilograms': 'kg', '킬로그램': 'kg',
            'g': 'g', 'grams': 'g', '그램': 'g',
            'mg': 'mg', 'milligrams': 'mg', '밀리그램': 'mg',
            'ton': 'ton', 'tons': 'ton', '톤': 'ton',
            'l': 'l', 'liters': 'l', '리터': 'l',
            'ml': 'ml', 'milliliters': 'ml', '밀리리터': 'ml'
        }
        
        unit_lower = str(unit).lower().strip()
        return unit_mapping.get(unit_lower, 'kg')  # 기본값: kg
