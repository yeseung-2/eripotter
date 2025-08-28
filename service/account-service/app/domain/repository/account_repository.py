from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from contextlib import contextmanager
from eripotter_common.database import get_session
from ..entity.account_entity import Account
from ..model.account_model import CompanyProfile, AccountCreate

class AccountRepository:
    @contextmanager
    def get_db(self) -> Session:
        with get_session() as session:
            yield session

    def get_by_oauth_sub(self, oauth_sub: str) -> Optional[Account]:
        """OAuth sub로 계정 조회"""
        with self.get_db() as db:
            return db.query(Account).filter(Account.oauth_sub == oauth_sub).first()

    def get_by_email(self, email: str) -> Optional[Account]:
        """이메일로 계정 조회"""
        with self.get_db() as db:
            return db.query(Account).filter(Account.email == email).first()

    def create_account(self, account_data: AccountCreate) -> Account:
        """OAuth 로그인 후 최초 계정 생성"""
        with self.get_db() as db:
            account = Account(
                oauth_sub=account_data.oauth_sub,
                email=account_data.email,
                name=account_data.name,
                profile_picture=account_data.profile_picture,
                email_verified=account_data.email_verified
            )
            db.add(account)
            db.commit()
            db.refresh(account)
            return account

    def update_company_profile(self, oauth_sub: str, profile_data: CompanyProfile) -> Optional[Account]:
        """기업 프로필 정보 업데이트"""
        with self.get_db() as db:
            account = db.query(Account).filter(Account.oauth_sub == oauth_sub).first()
            if not account:
                return None
            
            # 모델의 모든 필드를 업데이트
            for field, value in profile_data.dict().items():
                setattr(account, field, value)
            
            db.commit()
            db.refresh(account)
            return account

    def search_companies(self, query: str) -> List[Account]:
        """기업명, 업종으로 회사 검색"""
        with self.get_db() as db:
            return db.query(Account).filter(
                or_(
                    Account.company_name.ilike(f"%{query}%"),
                    Account.industry.ilike(f"%{query}%")
                )
            ).all()

    def get_by_business_number(self, business_number: str) -> Optional[Account]:
        """사업자 등록 번호로 계정 조회"""
        with self.get_db() as db:
            return db.query(Account).filter(Account.business_number == business_number).first()

    def update_profile_picture(self, oauth_sub: str, profile_picture_url: str) -> Optional[Account]:
        """프로필 사진 URL 업데이트"""
        with self.get_db() as db:
            account = db.query(Account).filter(Account.oauth_sub == oauth_sub).first()
            if not account:
                return None
            
            account.profile_picture = profile_picture_url
            db.commit()
            db.refresh(account)
            return account

    def update_last_login(self, account_id: int) -> Optional[Account]:
        """마지막 로그인 시간 업데이트"""
        with self.get_db() as db:
            account = db.query(Account).filter(Account.id == account_id).first()
            if not account:
                return None
            
            from datetime import datetime
            account.last_login = datetime.utcnow()
            db.commit()
            db.refresh(account)
            return account