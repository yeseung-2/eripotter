"""
Sharing Entity - 통합 sharing 테이블 엔티티 정의
협력사 관계 + 데이터 요청/승인 기능 통합
"""
from sqlalchemy import Column, String, DateTime, Text, Enum, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class RequestStatus(enum.Enum):
    """데이터 요청 상태"""
    PENDING = "pending"      # 승인 대기중
    ACTIVE = "active"        # 공유 승인 (활성화)
    REJECTED = "rejected"    # 공유 거부
    COMPLETED = "completed"  # 데이터 수신 (전송완료)
    INACTIVE = "inactive"    # 비활성화

class UrgencyLevel(enum.Enum):
    """긴급도"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"

class PriorityLevel(enum.Enum):
    """우선순위"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class DataType(enum.Enum):
    """데이터 타입"""
    ESG_REPORT = "esg_report"
    SUSTAINABILITY_DATA = "sustainability_data"
    CARBON_FOOTPRINT = "carbon_footprint"
    ENERGY_CONSUMPTION = "energy_consumption"
    WASTE_MANAGEMENT = "waste_management"
    WATER_USAGE = "water_usage"
    SUPPLY_CHAIN = "supply_chain"
    COMPLIANCE_DATA = "compliance_data"
    FINANCIAL_DATA = "financial_data"
    OPERATIONAL_DATA = "operational_data"

class Sharing(Base):
    """협력사 관계 + 데이터 요청 통합 테이블"""
    __tablename__ = "sharing"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 협력사 관계 정보
    parent_company_id = Column(String(100), comment="상위 회사 ID")
    parent_company_name = Column(String(200), comment="상위 회사명")
    child_company_id = Column(String(100), nullable=False, comment="하위 회사 ID")
    child_company_name = Column(String(200), comment="하위 회사명")
    chain_level = Column(Integer, comment="차수 (1차, 2차, 3차...)")
    relationship_type = Column(String(50), default="supplier", comment="관계 타입")
    
    # 핵심 협력사 관리
    is_strategic = Column(Boolean, default=False, comment="핵심 협력사 여부")
    priority_level = Column(String(20), default="medium", comment="우선순위")
    designation_reason = Column(Text, comment="핵심 협력사 지정 사유")
    business_impact_score = Column(Integer, default=0, comment="비즈니스 영향도 점수")
    annual_transaction_volume = Column(String(20), comment="연간 거래량")
    risk_level = Column(String(20), default="medium", comment="리스크 레벨")
    response_rate = Column(Integer, default=0, comment="응답률")
    last_contact_date = Column(DateTime, comment="마지막 연락일")
    strategic_designated_by = Column(String(100), comment="핵심 협력사 지정자")
    strategic_designated_at = Column(DateTime, comment="핵심 협력사 지정일")
    
    # 데이터 요청/승인 정보 (NULL 가능)
    request_id = Column(String(50), unique=True, comment="요청 ID")
    data_type = Column(String(100), default="sustainability", comment="데이터 타입")
    data_category = Column(String(200), comment="데이터 카테고리")
    data_description = Column(Text, comment="데이터 설명")
    requested_fields = Column(Text, comment="요청된 필드 목록 (JSON)")
    purpose = Column(Text, comment="사용 목적")
    usage_period = Column(String(100), comment="사용 기간")
    urgency_level = Column(String(20), default="normal", comment="긴급도")
    status = Column(String(20), default="pending", comment="요청 상태")
    
    # 타임스탬프
    requested_at = Column(DateTime, comment="요청 일시")
    reviewed_at = Column(DateTime, comment="검토 일시")
    approved_at = Column(DateTime, comment="승인 일시")
    completed_at = Column(DateTime, comment="완료 일시")
    
    # 검토자 정보
    reviewer_id = Column(String(100), comment="검토자 ID")
    reviewer_name = Column(String(200), comment="검토자명")
    review_comment = Column(Text, comment="검토 의견")
    
    # 데이터 전송 정보
    data_url = Column(Text, comment="데이터 다운로드 URL")
    expiry_date = Column(DateTime, comment="URL 만료일")
    
    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow, comment="생성일")
    updated_at = Column(DateTime, default=datetime.utcnow, comment="수정일")
    
    def to_dict(self):
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            # 협력사 관계
            "parent_company_id": self.parent_company_id,
            "parent_company_name": self.parent_company_name,
            "child_company_id": self.child_company_id,
            "child_company_name": self.child_company_name,
            "chain_level": self.chain_level,
            "relationship_type": self.relationship_type,
            # 핵심 협력사
            "is_strategic": self.is_strategic,
            "priority_level": self.priority_level,
            "designation_reason": self.designation_reason,
            "business_impact_score": self.business_impact_score,
            "response_rate": self.response_rate,
            "last_contact_date": self.last_contact_date.isoformat() if self.last_contact_date else None,
            "strategic_designated_by": self.strategic_designated_by,
            "strategic_designated_at": self.strategic_designated_at.isoformat() if self.strategic_designated_at else None,
            # 데이터 요청
            "request_id": self.request_id,
            "data_type": self.data_type,
            "data_category": self.data_category,
            "data_description": self.data_description,
            "requested_fields": self.requested_fields,
            "purpose": self.purpose,
            "usage_period": self.usage_period,
            "urgency_level": self.urgency_level,
            "status": self.status,
            "requested_at": self.requested_at.isoformat() if self.requested_at else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "reviewer_id": self.reviewer_id,
            "reviewer_name": self.reviewer_name,
            "review_comment": self.review_comment,
            "data_url": self.data_url,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            # 메타데이터
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def to_request_dict(self):
        """데이터 요청 형태로 변환 (프론트엔드 호환)"""
        if not self.request_id:
            return None
            
        return {
            "id": self.request_id,
            "requester_company_id": self.parent_company_id,
            "requester_company_name": self.parent_company_name,
            "provider_company_id": self.child_company_id,
            "provider_company_name": self.child_company_name,
            "data_type": self.data_type,
            "data_category": self.data_category,
            "data_description": self.data_description,
            "requested_fields": self.requested_fields,
            "purpose": self.purpose,
            "usage_period": self.usage_period,
            "urgency_level": self.urgency_level,
            "status": self.status,
            "requested_at": self.requested_at.isoformat() if self.requested_at else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "reviewer_id": self.reviewer_id,
            "reviewer_name": self.reviewer_name,
            "review_comment": self.review_comment,
            "data_url": self.data_url,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
        }