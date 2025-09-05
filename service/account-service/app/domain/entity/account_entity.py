from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, Enum
from sqlalchemy.sql import func
from eripotter_common.database import Base
import enum

# DB에 이미 존재하는 enum type 이름이 companytype 이라면 name="companytype"으로 매핑해야 해.
class CompanyType(enum.Enum):
    STARTUP = "startup"
    SME = "sme"      # 중소기업
    LARGE = "large"  # 대기업
    PUBLIC = "public"
    OTHER = "other"

class Account(Base):
    __tablename__ = "account"

    # 기본 식별자 및 인증 정보
    id = Column(Integer, primary_key=True)
    oauth_sub = Column(String, unique=True, nullable=False)  # Google OAuth ID
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    profile_picture = Column(String, nullable=True)

    # 기업 기본 정보 - 초기에는 비어있을 수 있음
    company_name = Column(String, nullable=True)  # citext로 변경되어 있어도 String 매핑으로 동작함
    # 기존 DB enum 과 충돌 없도록 name="companytype" 지정 (새 enum 생성 방지)
    company_type = Column(Enum(CompanyType, name="companytype"), nullable=True)
    industry = Column(String, nullable=True)
    business_number = Column(String, nullable=True)

    # 기업 상세 정보
    establishment_date = Column(String, nullable=True)  # 설립일
    employee_count = Column(Integer, nullable=True)     # 종업원 수
    annual_revenue = Column(String, nullable=True)
    business_area = Column(String, nullable=True)

    # 생산공장 정보
    factory_count = Column(Integer, nullable=True)
    factory_address = Column(String, nullable=True)
    production_items = Column(Text, nullable=True)

    # 담당자 정보
    department = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)

    # 시스템 필드
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
