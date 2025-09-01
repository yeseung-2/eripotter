"""
Certification Entity - 온실가스 AI 매핑 및 사용자 검토 결과 테이블
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# normal_entity에서 Base를 import해서 같은 Base 사용
from .normal_entity import Base

class CertificationEntity(Base):
    """온실가스 AI 매핑 및 사용자 검토 결과 엔티티"""
    __tablename__ = 'certification'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 외래키 (normal 테이블 참조)
    normal_id = Column(Integer, ForeignKey('normal.id', ondelete='CASCADE'))
    
    # 회사 정보
    company_id = Column(String(100))
    company_name = Column(String(255))
    
    # 온실가스 원본 정보
    original_gas_name = Column(String(255))  # 사용자 입력: "CO₂", "메탄", "이산화탄소" 등
    original_amount = Column(String(100))    # 사용자 입력 양
    
    # AI 초기 매핑 결과
    ai_mapped_sid = Column(String(100))      # 표준 ID: "GHG-CO2"
    ai_mapped_name = Column(String(255))     # 표준명: "Carbon dioxide"
    ai_confidence_score = Column(Float)      # 신뢰도 (0-1)
    ai_cas_number = Column(String(50))       # CAS 번호: "124-38-9"
    
    # 사용자 최종 매핑 결과
    final_mapped_sid = Column(String(100))
    final_mapped_name = Column(String(255))
    final_cas_number = Column(String(50))
    final_standard_unit = Column(String(50))
    
    # 상태 및 검토 정보
    mapping_status = Column(String(50), default='auto_mapped')  # 'auto_mapped', 'needs_review', 'user_reviewed', 'approved'
    reviewed_by = Column(String(100))
    review_comment = Column(Text)
    
    # 타임스탬프
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # 관계 설정 (normal 테이블과의 관계)
    normal = relationship("NormalEntity", backref="certifications")
    
    def __repr__(self):
        return f"<CertificationEntity(id={self.id}, normal_id={self.normal_id}, original_gas_name='{self.original_gas_name}')>"
    
    def to_dict(self):
        """엔티티를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'normal_id': self.normal_id,
            'company_id': self.company_id,
            'company_name': self.company_name,
            'original_gas_name': self.original_gas_name,
            'original_amount': self.original_amount,
            'ai_mapped_sid': self.ai_mapped_sid,
            'ai_mapped_name': self.ai_mapped_name,
            'ai_confidence_score': self.ai_confidence_score,
            'ai_cas_number': self.ai_cas_number,
            'final_mapped_sid': self.final_mapped_sid,
            'final_mapped_name': self.final_mapped_name,
            'final_cas_number': self.final_cas_number,
            'final_standard_unit': self.final_standard_unit,
            'mapping_status': self.mapping_status,
            'reviewed_by': self.reviewed_by,
            'review_comment': self.review_comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_mapping_status_display(self):
        """매핑 상태를 한국어로 반환"""
        status_map = {
            'auto_mapped': '자동매핑',
            'needs_review': '검토필요',
            'user_reviewed': '사용자검토',
            'approved': '승인완료'
        }
        return status_map.get(self.mapping_status, self.mapping_status)
    
    def is_high_confidence(self):
        """고신뢰도 매핑인지 확인 (70% 이상)"""
        return self.ai_confidence_score and self.ai_confidence_score >= 0.7
    
    def is_needs_review(self):
        """검토가 필요한지 확인 (40-70%)"""
        return (self.ai_confidence_score and 
                0.4 <= self.ai_confidence_score < 0.7)
    
    def is_low_confidence(self):
        """저신뢰도 매핑인지 확인 (40% 미만)"""
        return self.ai_confidence_score and self.ai_confidence_score < 0.4
