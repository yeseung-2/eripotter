"""
Service Interfaces - 기능별 서비스 계약 정의
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime


class ISubstanceMapping(ABC):
    """물질 매핑 서비스 인터페이스"""
    
    @abstractmethod
    def map_substance(self, substance_name: str, company_id: str = None) -> Dict:
        """단일 물질 매핑"""
        pass
    
    @abstractmethod
    def map_substances_batch(self, substance_names: List[str], company_id: str = None) -> List[Dict]:
        """배치 물질 매핑"""
        pass
    
    @abstractmethod
    def map_file(self, file_path: str, company_id: str = None) -> Dict:
        """파일 기반 물질 매핑"""
        pass
    
    @abstractmethod
    def get_mapping_statistics(self) -> Dict:
        """매핑 통계 조회"""
        pass


class IDataNormalization(ABC):
    """데이터 정규화 서비스 인터페이스"""
    
    @abstractmethod
    def normalize_excel_data(self, file_data: bytes, filename: str, company_id: str = None) -> Dict:
        """엑셀 데이터 정규화"""
        pass
    
    @abstractmethod
    def validate_data_structure(self, data: Dict) -> Dict:
        """데이터 구조 검증"""
        pass
    
    @abstractmethod
    def standardize_data(self, data: Dict) -> Dict:
        """데이터 표준화"""
        pass


class IESGValidation(ABC):
    """ESG 검증 서비스 인터페이스"""
    
    @abstractmethod
    def validate_esg_data(self, data: Dict, industry: str = None) -> Dict:
        """ESG 데이터 검증"""
        pass
    
    @abstractmethod
    def calculate_esg_score(self, data: Dict) -> int:
        """ESG 점수 계산"""
        pass
    
    @abstractmethod
    def generate_esg_report(self, company_id: str, report_type: str) -> Dict:
        """ESG 보고서 생성"""
        pass


class IDataRepository(ABC):
    """데이터 저장소 인터페이스"""
    
    @abstractmethod
    def save_original_data(self, data: Dict) -> bool:
        """원본 데이터 저장"""
        pass
    
    @abstractmethod
    def save_mapping_result(self, mapping_data: Dict) -> bool:
        """매핑 결과 저장"""
        pass
    
    @abstractmethod
    def save_correction(self, correction_data: Dict) -> bool:
        """수정 사항 저장"""
        pass
    
    @abstractmethod
    def get_statistics(self) -> Dict:
        """통계 조회"""
        pass
