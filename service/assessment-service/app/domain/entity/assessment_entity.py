"""
Assessment Service - Entity Models
"""

from sqlalchemy import (
    Column,
    Integer,
    Text,
    Float,
    JSON,
    BigInteger,
    TIMESTAMP,
    ARRAY
)

from eripotter_common.database import Base
from sqlalchemy.sql import func
from typing import Dict

class KesgEntity(Base):
    """KESG 테이블 엔티티 - Railway PostgreSQL 구조와 동일"""
    __tablename__ = "kesg"

    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="KESG 항목 ID")

    # 분류 정보
    classification = Column(Text, nullable=True, comment="분류")
    domain = Column(Text, nullable=True, comment="도메인")
    category = Column(Text, nullable=True, comment="카테고리")

    # 항목 정보
    item_name = Column(Text, nullable=True, comment="항목명")
    item_desc = Column(Text, nullable=True, comment="항목 설명")
    metric_desc = Column(Text, nullable=True, comment="지표 설명")

    # 데이터 정보
    data_source = Column(Text, nullable=True, comment="데이터 소스")
    data_period = Column(Text, nullable=True, comment="데이터 기간")
    data_method = Column(Text, nullable=True, comment="데이터 수집 방법")
    data_detail = Column(Text, nullable=True, comment="데이터 상세 정보")

    # 질문 타입 및 선택지
    question_type = Column(Text, nullable=True, comment="질문 타입 (three_level, five_level, five_choice)")
    levels_json = Column(JSON, nullable=True, comment="레벨 정보 JSON (3단계형, 5단계형용)")
    choices_json = Column(JSON, nullable=True, comment="선택지 정보 JSON (5선택형용)")
    scoring_json = Column(JSON, nullable=True, comment="점수 정보 JSON")

    # 가중치
    weight = Column(Float, nullable=True, comment="가중치")

    def __repr__(self):
        return f"<KesgEntity(id={self.id}, item_name='{self.item_name}', question_type='{self.question_type}')>"

    def to_dict(self) -> Dict[str, object]:
        """엔티티를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'classification': self.classification,
            'domain': self.domain,
            'category': self.category,
            'item_name': self.item_name,
            'item_desc': self.item_desc,
            'metric_desc': self.metric_desc,
            'data_source': self.data_source,
            'data_period': self.data_period,
            'data_method': self.data_method,
            'data_detail': self.data_detail,
            'question_type': self.question_type,
            'levels_json': self.levels_json,
            'choices_json': self.choices_json,
            'scoring_json': self.scoring_json,
            'weight': self.weight
        }


class AssessmentEntity(Base):
    """Assessment 테이블 엔티티"""
    __tablename__ = "assessment"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True, comment="Assessment ID")

    # Foreign Keys / 식별자
    company_name = Column(Text, nullable=False, index=True, comment="회사명")
    question_id = Column(Integer, nullable=False, index=True, comment="KESG 문항 ID")

    # 응답 정보
    question_type = Column(Text, nullable=False, comment="질문 타입")
    level_no = Column(Integer, nullable=True, comment="선택된 레벨 번호 (3단계형, 5단계형용)")
    choice_ids = Column(ARRAY(Integer), nullable=True, comment="선택된 선택지 ID 배열 (5선택형용)")
    score = Column(Integer, nullable=False, comment="점수")

    # 타임스탬프
    timestamp = Column(TIMESTAMP, nullable=True, server_default=func.now(), comment="제출 시간 (기본값 now())")

    def __repr__(self):
        return f"<AssessmentEntity(id={self.id}, company_name='{self.company_name}', question_id={self.question_id}, score={self.score})>"

    def to_dict(self) -> Dict[str, object]:
        """엔티티를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'company_name': self.company_name,
            'question_id': self.question_id,
            'question_type': self.question_type,
            'level_no': self.level_no,
            'choice_ids': self.choice_ids,
            'score': self.score,
            'timestamp': self.timestamp
        }