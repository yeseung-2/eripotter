"""
Report Entity - 보고서 데이터베이스 모델
"""
from sqlalchemy import Column, String, DateTime, Text, Integer, JSON, UniqueConstraint, Index
from sqlalchemy.sql import func
from eripotter_common.database import Base

class Report(Base):
    __tablename__ = "report"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic = Column(String, nullable=False)           # 지표 ID (예: KBZ-EN22)
    company_name = Column(String, nullable=False)    # 회사명
    report_type = Column(String, nullable=False)     # 보고서 유형 (예: sustainability, indicator, ...)
    title = Column(String, nullable=True)            # 보고서 제목
    content = Column(Text, nullable=True)            # 보고서 내용
    # SQLAlchemy 예약어(metadata) 충돌 회피: 속성명(meta) ↔ 컬럼명("metadata")
    meta = Column("metadata", JSON, nullable=True)   # 메타데이터 (회사 정보, 입력값 등)
    status = Column(String, default="draft", nullable=False)  # draft, completed

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("topic", "company_name", name="uq_report_topic_company"),
        Index("ix_report_topic_company", "topic", "company_name"),
        Index("ix_report_type", "report_type"),
        Index("ix_report_status", "status"),
    )

    class Config:
        from_attributes = True