# app/domain/entity/normal_entity.py
"""
Normal Entity - ESG 원본 데이터 저장 테이블 (Refactored)
- SQLAlchemy 2.x 스타일로 정리 (eripotter_common.database.Base 사용)
- 서버타임스탬프 func.now() 사용
- to_dict() 안전성 향상 (Date/DateTime None/타입 보호)
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB

# eripotter_common 공통 Base 사용
from eripotter_common.database import Base


def _iso(dt: Optional[datetime | date]) -> Optional[str]:
    """datetime/date -> ISO8601 (None-safe)"""
    if not dt:
        return None
    # Date/DateTime 모두 isoformat 지원
    return dt.isoformat()


class NormalEntity(Base):
    """ESG 원본 데이터 저장 엔티티"""
    __tablename__ = "normal"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 회사 정보
    company_id = Column(String(100), nullable=True, index=True)
    company_name = Column(String(255), nullable=True, index=True)
    uploaded_by = Column(String(100), nullable=True)
    uploaded_by_email = Column(String(255), nullable=True)

    # 파일 정보
    filename = Column(String(255), nullable=True)
    file_size = Column(BigInteger, nullable=True)
    file_type = Column(String(50), nullable=True)  # 'manual', 'excel'

    # 제품 기본 정보
    product_name = Column(String(255), nullable=True)
    supplier = Column(String(100), nullable=True)  # 원청, 1차, 2차, ..., 10차
    manufacturing_date = Column(Date, nullable=True)
    manufacturing_number = Column(String(100), nullable=True)
    safety_information = Column(Text, nullable=True)
    recycled_material = Column(Boolean, nullable=True)

    # 제품 스펙
    capacity = Column(String(100), nullable=True)         # 용량 (Ah, Wh 등)
    energy_density = Column(String(100), nullable=True)   # 에너지밀도

    # 위치 정보
    manufacturing_country = Column(String(100), nullable=True)
    production_plant = Column(String(255), nullable=True)

    # 처리 방법
    disposal_method = Column(Text, nullable=True)   # 폐기 방법 및 인증
    recycling_method = Column(Text, nullable=True)  # 재활용 방법 및 인증

    # 원재료 정보 (JSON 저장, 매핑 안 함)
    raw_materials = Column(JSONB, nullable=True)          # ['리튬', '니켈', '코발트', ...]
    raw_material_sources = Column(JSONB, nullable=True)   # [{material, sourceType, address/country}, ...]

    # 온실가스 배출량 (AI 매핑 대상)
    greenhouse_gas_emissions = Column(JSONB, nullable=True)  # [{materialName, amount, unit}, ...]

    # 화학물질 구성
    chemical_composition = Column(Text, nullable=True)

    # 타임스탬프
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<NormalEntity(id={self.id}, company_id='{self.company_id}', "
            f"product_name='{self.product_name}')>"
        )

    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환 (Date/DateTime 안전 변환)"""
        return {
            "id": self.id,
            "company_id": self.company_id,
            "company_name": self.company_name,
            "uploaded_by": self.uploaded_by,
            "uploaded_by_email": self.uploaded_by_email,
            "filename": self.filename,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "product_name": self.product_name,
            "supplier": self.supplier,
            "manufacturing_date": _iso(self.manufacturing_date),
            "manufacturing_number": self.manufacturing_number,
            "safety_information": self.safety_information,
            "recycled_material": self.recycled_material,
            "capacity": self.capacity,
            "energy_density": self.energy_density,
            "manufacturing_country": self.manufacturing_country,
            "production_plant": self.production_plant,
            "disposal_method": self.disposal_method,
            "recycling_method": self.recycling_method,
            "raw_materials": self.raw_materials,
            "raw_material_sources": self.raw_material_sources,
            "greenhouse_gas_emissions": self.greenhouse_gas_emissions,
            "chemical_composition": self.chemical_composition,
            "created_at": _iso(self.created_at),
            "updated_at": _iso(self.updated_at),
        }
