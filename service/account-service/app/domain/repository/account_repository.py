from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from eripotter_common.database import get_session
from ..entity.account_entity import Account
from ..model.account_model import CompanyProfile, AccountCreate

class AccountRepository:
    def get_by_oauth_sub(self, oauth_sub: str) -> Optional[dict]:
        """OAuth sub로 계정 조회 - 딕셔너리 반환"""
        with get_session() as db:
            account = db.query(Account).filter(Account.oauth_sub == oauth_sub).first()
            if account:
                return {
                    "id": account.id,
                    "oauth_sub": account.oauth_sub,
                    "email": account.email,
                    "name": account.name,
                    "profile_picture": account.profile_picture,
                    "company_name": account.company_name,
                    "company_type": account.company_type,
                    "industry": account.industry,
                    "business_number": account.business_number,
                    "establishment_date": account.establishment_date,
                    "employee_count": account.employee_count,
                    "annual_revenue": account.annual_revenue,
                    "business_area": account.business_area,
                    "factory_count": account.factory_count,
                    "factory_address": account.factory_address,
                    "production_items": account.production_items,
                    "department": account.department,
                    "phone_number": account.phone_number,
                    "email_verified": account.email_verified,
                    "created_at": account.created_at,
                    "updated_at": account.updated_at
                }
            return None

    def get_by_email(self, email: str) -> Optional[Account]:
        """이메일로 계정 조회"""
        with get_session() as db:
            return db.query(Account).filter(Account.email == email).first()

    def create_account(self, account_data: AccountCreate) -> dict:
        """OAuth 로그인 후 최초 계정 생성 - 딕셔너리 반환"""
        with get_session() as db:
            account = Account(
                oauth_sub=account_data.oauth_sub,
                email=account_data.email,
                name=account_data.name,
                profile_picture=account_data.profile_picture,
                email_verified=account_data.email_verified
            )
            db.add(account)
            db.commit()
            # 딕셔너리로 반환하여 세션 바인딩 문제 해결
            return {
                "id": account.id,
                "oauth_sub": account.oauth_sub,
                "email": account.email,
                "name": account.name,
                "profile_picture": account.profile_picture,
                "email_verified": account.email_verified
            }

    def update_company_profile(self, oauth_sub: str, profile_data: CompanyProfile) -> Optional[dict]:
        """기업 프로필 정보 업데이트 - 딕셔너리 반환"""
        with get_session() as db:
            account = db.query(Account).filter(Account.oauth_sub == oauth_sub).first()
            if not account:
                return None
            
            # None이 아닌 필드만 업데이트
            for field, value in profile_data.dict().items():
                if value is not None:
                    setattr(account, field, value)
            
            db.commit()
            db.refresh(account)
            
            # 딕셔너리로 반환하여 세션 바인딩 문제 해결
            return {
                "id": account.id,
                "oauth_sub": account.oauth_sub,
                "email": account.email,
                "name": account.name,
                "profile_picture": account.profile_picture,
                "company_name": account.company_name,
                "company_type": account.company_type,
                "industry": account.industry,
                "business_number": account.business_number,
                "establishment_date": account.establishment_date,
                "employee_count": account.employee_count,
                "annual_revenue": account.annual_revenue,
                "business_area": account.business_area,
                "factory_count": account.factory_count,
                "factory_address": account.factory_address,
                "production_items": account.production_items,
                "department": account.department,
                "phone_number": account.phone_number,
                "email_verified": account.email_verified,
                "created_at": account.created_at,
                "updated_at": account.updated_at
            }

    def create_company_profile(self, oauth_sub: str, profile_data: CompanyProfile) -> Optional[dict]:
        """기업 프로필 정보 생성 - 딕셔너리 반환"""
        with get_session() as db:
            account = db.query(Account).filter(Account.oauth_sub == oauth_sub).first()
            if not account:
                return None
            
            # None이 아닌 필드만 설정
            for field, value in profile_data.dict().items():
                if value is not None:
                    setattr(account, field, value)
            
            db.commit()
            db.refresh(account)
            
            # 딕셔너리로 반환하여 세션 바인딩 문제 해결
            return {
                "id": account.id,
                "oauth_sub": account.oauth_sub,
                "email": account.email,
                "name": account.name,
                "profile_picture": account.profile_picture,
                "company_name": account.company_name,
                "company_type": account.company_type,
                "industry": account.industry,
                "business_number": account.business_number,
                "establishment_date": account.establishment_date,
                "employee_count": account.employee_count,
                "annual_revenue": account.annual_revenue,
                "business_area": account.business_area,
                "factory_count": account.factory_count,
                "factory_address": account.factory_address,
                "production_items": account.production_items,
                "department": account.department,
                "phone_number": account.phone_number,
                "email_verified": account.email_verified,
                "created_at": account.created_at,
                "updated_at": account.updated_at
            }

    def search_companies(self, query: str) -> List[Account]:
        """기업명, 업종으로 회사 검색"""
        with get_session() as db:
            return db.query(Account).filter(
                or_(
                    Account.company_name.ilike(f"%{query}%"),
                    Account.industry.ilike(f"%{query}%")
                )
            ).all()

    def get_by_business_number(self, business_number: str) -> Optional[Account]:
        """사업자 등록 번호로 계정 조회"""
        with get_session() as db:
            return db.query(Account).filter(Account.business_number == business_number).first()

    def update_profile_picture(self, oauth_sub: str, profile_picture_url: str) -> Optional[Account]:
        """프로필 사진 URL 업데이트"""
        with get_session() as db:
            account = db.query(Account).filter(Account.oauth_sub == oauth_sub).first()
            if not account:
                return None
            
            account.profile_picture = profile_picture_url
            db.commit()
            db.refresh(account)
            return account

    def update_last_login(self, account_id: int) -> Optional[Account]:
        """마지막 로그인 시간 업데이트"""
        with get_session() as db:
            account = db.query(Account).filter(Account.id == account_id).first()
            if not account:
                return None
            
            from datetime import datetime
            account.last_login = datetime.utcnow()
            db.commit()
            # 새로운 객체 생성하여 반환
            return Account(
                id=account.id,
                oauth_sub=account.oauth_sub,
                email=account.email,
                name=account.name,
                profile_picture=account.profile_picture,
                company_name=account.company_name,
                company_type=account.company_type,
                industry=account.industry,
                business_number=account.business_number,
                establishment_date=account.establishment_date,
                employee_count=account.employee_count,
                annual_revenue=account.annual_revenue,
                business_area=account.business_area,
                factory_count=account.factory_count,
                factory_address=account.factory_address,
                production_items=account.production_items,
                department=account.department,
                phone_number=account.phone_number,
                is_active=account.is_active,
                email_verified=account.email_verified,
                created_at=account.created_at,
                updated_at=account.updated_at,
                last_login=account.last_login
            )