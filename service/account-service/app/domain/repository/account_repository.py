from sqlalchemy import or_, text
from typing import Optional, List, Dict, Any
from eripotter_common.database import get_session
from ..entity.account_entity import Account, CompanyType
from ..model.account_model import CompanyProfile, AccountCreate
from datetime import datetime

def _normalize_company_name(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    # 다중 공백 → 단일 공백, 앞뒤 공백 제거
    return " ".join(s.split()).strip()

def _to_dict(a: Account) -> Dict[str, Any]:
    return {
        "id": a.id,
        "oauth_sub": a.oauth_sub,
        "email": a.email,
        "name": a.name,
        "profile_picture": a.profile_picture,
        "company_name": a.company_name,
        "company_type": (a.company_type.value if a.company_type else None),
        "industry": a.industry,
        "business_number": a.business_number,
        "establishment_date": a.establishment_date,
        "employee_count": a.employee_count,
        "annual_revenue": a.annual_revenue,
        "business_area": a.business_area,
        "factory_count": a.factory_count,
        "factory_address": a.factory_address,
        "production_items": a.production_items,
        "department": a.department,
        "phone_number": a.phone_number,
        "is_active": a.is_active,
        "email_verified": a.email_verified,
        "created_at": a.created_at,
        "updated_at": a.updated_at,
        "last_login": a.last_login,
    }

class AccountRepository:
    def get_by_oauth_sub(self, oauth_sub: str) -> Optional[dict]:
        """OAuth sub로 계정 조회 - 딕셔너리 반환"""
        with get_session() as db:
            a = db.query(Account).filter(Account.oauth_sub == oauth_sub).first()
            return _to_dict(a) if a else None

    def get_by_email(self, email: str) -> Optional[dict]:
        """이메일로 계정 조회 - 딕셔너리 반환"""
        with get_session() as db:
            a = db.query(Account).filter(Account.email == email).first()
            return _to_dict(a) if a else None

    def get_id_by_company_name(self, company_name: str) -> Optional[int]:
        """회사명으로 id 조회 (citext면 대소문자 무시 매칭)"""
        company_name = _normalize_company_name(company_name)
        with get_session() as db:
            row = db.execute(
                text("SELECT id FROM account WHERE company_name = :cn LIMIT 1"),
                {"cn": company_name}
            ).fetchone()
            return int(row[0]) if row else None

    def create_account(self, account_data: AccountCreate) -> dict:
        """OAuth 로그인 후 최초 계정 생성 - 딕셔너리 반환"""
        with get_session() as db:
            a = Account(
                oauth_sub=account_data.oauth_sub,
                email=account_data.email,
                name=account_data.name,
                profile_picture=account_data.profile_picture,
                email_verified=account_data.email_verified
            )
            db.add(a)
            db.commit()
            db.refresh(a)
            return _to_dict(a)

    def update_company_profile(self, oauth_sub: str, profile_data: CompanyProfile) -> Optional[dict]:
        """기업 프로필 정보 업데이트 - 딕셔너리 반환"""
        with get_session() as db:
            a = db.query(Account).filter(Account.oauth_sub == oauth_sub).first()
            if not a:
                return None

            payload = profile_data.dict()
            # company_name 정규화
            if payload.get("company_name") is not None:
                payload["company_name"] = _normalize_company_name(payload["company_name"])

            for field, value in payload.items():
                if value is not None:
                    if field == "company_type" and isinstance(value, str):
                        try:
                            value = CompanyType(value)
                        except Exception:
                            continue
                    setattr(a, field, value)

            a.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(a)
            return _to_dict(a)

    def create_company_profile(self, oauth_sub: str, profile_data: CompanyProfile) -> Optional[dict]:
        """기업 프로필 정보 생성 - 딕셔너리 반환"""
        with get_session() as db:
            a = db.query(Account).filter(Account.oauth_sub == oauth_sub).first()
            if not a:
                return None

            payload = profile_data.dict()
            if payload.get("company_name") is not None:
                payload["company_name"] = _normalize_company_name(payload["company_name"])

            for field, value in payload.items():
                if value is not None:
                    if field == "company_type" and isinstance(value, str):
                        try:
                            value = CompanyType(value)
                        except Exception:
                            continue
                    setattr(a, field, value)

            a.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(a)
            return _to_dict(a)

    def search_companies(self, query: str) -> List[dict]:
        """기업명, 업종으로 회사 검색 - 딕셔너리 리스트 반환"""
        q = f"%{query}%"
        with get_session() as db:
            rows = db.query(Account).filter(
                or_(
                    Account.company_name.ilike(q),
                    Account.industry.ilike(q)
                )
            ).all()
            return [{"id": r.id, "company_name": r.company_name, "industry": r.industry} for r in rows]

    def get_by_business_number(self, business_number: str) -> Optional[dict]:
        """사업자 등록 번호로 계정 조회 - 딕셔너리 반환"""
        with get_session() as db:
            a = db.query(Account).filter(Account.business_number == business_number).first()
            return _to_dict(a) if a else None

    def update_profile_picture(self, oauth_sub: str, profile_picture_url: str) -> Optional[dict]:
        """프로필 사진 URL 업데이트 - 딕셔너리 반환"""
        with get_session() as db:
            a = db.query(Account).filter(Account.oauth_sub == oauth_sub).first()
            if not a:
                return None
            a.profile_picture = profile_picture_url
            a.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(a)
            return _to_dict(a)

    def update_last_login(self, account_id: int) -> Optional[dict]:
        """마지막 로그인 시간 업데이트 - 딕셔너리 반환"""
        with get_session() as db:
            a = db.query(Account).filter(Account.id == account_id).first()
            if not a:
                return None
            a.last_login = datetime.utcnow()
            db.commit()
            db.refresh(a)
            return _to_dict(a)
