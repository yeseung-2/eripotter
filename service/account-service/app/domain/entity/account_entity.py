from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, Enum
from sqlalchemy.sql import func
from eripotter_common.database import Base
import enum

class CompanyType(enum.Enum):
    STARTUP = "startup"
    SME = "sme"  # 중소기업
    LARGE = "large"  # 대기업
    PUBLIC = "public"  # 공공기관
    OTHER = "other"

class Account(Base):
    __tablename__ = "account"
    
    # 기본 식별자 및 인증 정보
    id = Column(Integer, primary_key=True)
    oauth_sub = Column(String, unique=True, nullable=False)  # Google OAuth ID
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    profile_picture = Column(String, nullable=True)
    
    # 기업 기본 정보
    company_name = Column(String, nullable=False)  # 기업명
    company_type = Column(Enum(CompanyType), nullable=False)  # 기업 구분
    industry = Column(String, nullable=False)  # 업종
    business_number = Column(String, nullable=False)  # 사업자 등록 번호
    
    # 기업 상세 정보
    establishment_date = Column(String, nullable=True)  # 설립일
    employee_count = Column(Integer, nullable=True)  # 종업원 수
    annual_revenue = Column(String, nullable=True)  # 연간 매출액
    business_area = Column(String, nullable=True)  # 사업 분야
    
    # 생산공장 정보
    factory_count = Column(Integer, nullable=True)  # 생산공장 수
    factory_address = Column(String, nullable=True)  # 주요 생산공장 위치
    production_items = Column(Text, nullable=True)  # 주요 생산품목
    
    # 담당자 정보
    department = Column(String, nullable=False)  # 부서/직책
    phone_number = Column(String, nullable=False)  # 연락처
    
    # 시스템 필드
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)