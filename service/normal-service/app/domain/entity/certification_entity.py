# app/domain/entity/certification_entity.py
"""
Certification Entity - 온실가스 AI 매핑 및 사용자 검토 결과 (Refactored)
- SQLAlchemy 2.x 스타일
- to_dict()의 Date/DateTime 안전 직렬화
- 기존 스키마/타입을 그대로 유지해 마이그레이션 충돌 최소화
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship

# eripotter_common 공통 Base 사용
from eripotter_common.database import Base


def _iso(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat() if dt else None


class CertificationEntity(Base):
    """온실가스 AI 매핑 및 사용자 검토 결과 엔티티"""
    __tablename__ = "certification"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 외래키 (normal 테이블 참조)
    normal_id = Column(
        Integer,
        ForeignKey("normal.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )

    # 회사 정보
    company_id = Column(String(100), nullable=True, index=True)
    company_name = Column(String(255), nullable=True, index=True)

    # 온실가스 원본 정보
    original_gas_name = Column(String(255), nullable=True)  # 사용자 입력명
    original_amount = Column(String(100), nullable=True)    # 사용자 입력 양(문자열 유지)

    # AI 초기 매핑 결과
    ai_mapped_sid = Column(String(100), nullable=True)      # 표준 ID
    ai_mapped_name = Column(String(255), nullable=True)     # 표준명
    ai_confidence_score = Column(Float, nullable=True)      # 신뢰도 (0-1)
    ai_cas_number = Column(String(50), nullable=True)       # CAS 번호

    # 사용자 최종 매핑 결과
    final_mapped_sid = Column(String(100), nullable=True)
    final_mapped_name = Column(String(255), nullable=True)
    final_cas_number = Column(String(50), nullable=True)
    final_standard_unit = Column(String(50), nullable=True)

    # 상태 및 검토 정보
    mapping_status = Column(
        String(50), default="auto_mapped", nullable=True
    )  # auto_mapped, needs_review, user_reviewed, approved
    reviewed_by = Column(String(100), nullable=True)
    review_comment = Column(Text, nullable=True)

    # 타임스탬프
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # 관계 설정 (normal 테이블과의 관계)
    # backref를 사용해 NormalEntity.certifications 자동 생성 (기존 동작 유지)
    normal = relationship("NormalEntity", backref="certifications")

    def __repr__(self) -> str:
        return (
            f"<CertificationEntity(id={self.id}, normal_id={self.normal_id}, "
            f"original_gas_name='{self.original_gas_name}')>"
        )

    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "normal_id": self.normal_id,
            "company_id": self.company_id,
            "company_name": self.company_name,
            "original_gas_name": self.original_gas_name,
            "original_amount": self.original_amount,
            "ai_mapped_sid": self.ai_mapped_sid,
            "ai_mapped_name": self.ai_mapped_name,
            "ai_confidence_score": self.ai_confidence_score,
            "ai_cas_number": self.ai_cas_number,
            "final_mapped_sid": self.final_mapped_sid,
            "final_mapped_name": self.final_mapped_name,
            "final_cas_number": self.final_cas_number,
            "final_standard_unit": self.final_standard_unit,
            "mapping_status": self.mapping_status,
            "reviewed_by": self.reviewed_by,
            "review_comment": self.review_comment,
            "created_at": _iso(self.created_at),
            "updated_at": _iso(self.updated_at),
        }

    # ===== 유틸 메서드 (기존 로직 유지) =====
    def get_mapping_status_display(self) -> str:
        status_map = {
            "auto_mapped": "자동매핑",
            "needs_review": "검토필요",
            "user_reviewed": "사용자검토",
            "approved": "승인완료",
        }
        return status_map.get(self.mapping_status, self.mapping_status or "")

    def is_high_confidence(self) -> bool:
        return bool(self.ai_confidence_score and self.ai_confidence_score >= 0.7)

    def is_needs_review(self) -> bool:
        return bool(self.ai_confidence_score and 0.4 <= self.ai_confidence_score < 0.7)

    def is_low_confidence(self) -> bool:
        return bool(self.ai_confidence_score and self.ai_confidence_score < 0.4)
