"""
Normal Entity - ESG 원본 데이터 저장 테이블
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, BigInteger, Date, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class NormalEntity(Base):
    """ESG 원본 데이터 저장 엔티티"""
    __tablename__ = 'normal'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 회사 정보
    company_id = Column(String(100))
    company_name = Column(String(255))
    uploaded_by = Column(String(100))
    uploaded_by_email = Column(String(255))
    
    # 파일 정보
    filename = Column(String(255))
    file_size = Column(BigInteger)
    file_type = Column(String(50))  # 'manual', 'excel'
    
    # 제품 기본 정보
    product_name = Column(String(255))
    supplier = Column(String(100))  # 원청, 1차, 2차, ..., 10차
    manufacturing_date = Column(Date)
    manufacturing_number = Column(String(100))
    safety_information = Column(Text)
    recycled_material = Column(Boolean)
    
    # 제품 스펙
    capacity = Column(String(100))  # 용량 (Ah, Wh)
    energy_density = Column(String(100))  # 에너지밀도
    
    # 위치 정보
    manufacturing_country = Column(String(100))
    production_plant = Column(String(255))
    
    # 처리 방법
    disposal_method = Column(Text)  # 폐기 방법 및 인증
    recycling_method = Column(Text)  # 재활용 방법 및 인증
    
    # 원재료 정보 (JSON 저장, 매핑 안 함)
    raw_materials = Column(JSONB)  # ['리튬', '니켈', '코발트', ...]
    raw_material_sources = Column(JSONB)  # [{material, sourceType, address/country}, ...]
    
    # 온실가스 배출량 (AI 매핑 대상)
    greenhouse_gas_emissions = Column(JSONB)  # [{materialName, amount, unit}, ...]
    
    # 화학물질 구성
    chemical_composition = Column(Text)
    
    # 타임스탬프
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    def __repr__(self):
        return f"<NormalEntity(id={self.id}, company_id='{self.company_id}', product_name='{self.product_name}')>"
    
    def to_dict(self):
        """엔티티를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'company_id': self.company_id,
            'company_name': self.company_name,
            'uploaded_by': self.uploaded_by,
            'uploaded_by_email': self.uploaded_by_email,
            'filename': self.filename,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'product_name': self.product_name,
            'supplier': self.supplier,
            'manufacturing_date': self.manufacturing_date.isoformat() if self.manufacturing_date else None,
            'manufacturing_number': self.manufacturing_number,
            'safety_information': self.safety_information,
            'recycled_material': self.recycled_material,
            'capacity': self.capacity,
            'energy_density': self.energy_density,
            'manufacturing_country': self.manufacturing_country,
            'production_plant': self.production_plant,
            'disposal_method': self.disposal_method,
            'recycling_method': self.recycling_method,
            'raw_materials': self.raw_materials,
            'raw_material_sources': self.raw_material_sources,
            'greenhouse_gas_emissions': self.greenhouse_gas_emissions,
            'chemical_composition': self.chemical_composition,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }