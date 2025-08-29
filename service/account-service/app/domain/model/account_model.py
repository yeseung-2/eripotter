from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

class CompanyType(str, Enum):
    STARTUP = "startup"
    SME = "sme"
    LARGE = "large"
    PUBLIC = "public"
    OTHER = "other"

class GoogleAuthData(BaseModel):
    """Google OAuth 인증 데이터"""
    sub: str
    email: str
    name: str
    picture: Optional[str] = None
    hd: Optional[str] = None  # Google Workspace 도메인
    email_verified: Optional[bool] = None

class AccountCreate(BaseModel):
    """OAuth 로그인 후 최초 계정 생성"""
    oauth_sub: str
    email: EmailStr
    name: str
    profile_picture: Optional[str] = None
    email_verified: Optional[bool] = None

class CompanyProfile(BaseModel):
    """기업 프로필 정보 입력/수정"""
    company_name: Optional[str] = None
    company_type: Optional[CompanyType] = None
    industry: Optional[str] = None
    business_number: Optional[str] = None
    establishment_date: Optional[str] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[str] = None
    business_area: Optional[str] = None
    factory_count: Optional[int] = None
    factory_address: Optional[str] = None
    production_items: Optional[str] = None
    department: Optional[str] = None
    phone_number: Optional[str] = None
    

class AccountResponse(BaseModel):
    """계정 정보 응답"""
    id: int
    email: str
    name: str
    access_token: Optional[str] = None  # JWT 토큰
    profile_picture: Optional[str] = None
    company_name: Optional[str] = None
    company_type: Optional[CompanyType] = None
    industry: Optional[str] = None
    business_number: Optional[str] = None
    establishment_date: Optional[str] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[str] = None
    business_area: Optional[str] = None
    factory_count: Optional[int] = None
    factory_address: Optional[str] = None
    production_items: Optional[str] = None
    department: Optional[str] = None
    phone_number: Optional[str] = None
    email_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

class TokenResponse(BaseModel):
    """JWT 토큰 응답"""
    access_token: str
    token_type: str = "bearer"

class APIResponse(BaseModel):
    """API 응답 래퍼"""
    status: str
    message: str
    data: Optional[AccountResponse] = None

    