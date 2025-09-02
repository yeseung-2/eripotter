from ..repository.account_repository import AccountRepository 
from ..model.account_model import (
    AccountCreate,
    CompanyProfile,
    GoogleAuthData,
    TokenResponse
)
import jwt
import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger("account_service")

class AccountService:
    def __init__(self):
        self.repository = AccountRepository()
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
        self.jwt_issuer = os.getenv("JWT_ISSUER", "account-service")
        self.jwt_expires_minutes = int(os.getenv("JWT_EXPIRES_MINUTES", "120"))

    def _create_access_token(self, data: dict) -> str:
        now = datetime.utcnow()
        to_encode = {
            **data,
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(minutes=self.jwt_expires_minutes),
            "iss": self.jwt_issuer,
        }
        return jwt.encode(to_encode, self.secret_key, algorithm="HS256")

    def process_google_auth(self, auth_data: GoogleAuthData) -> TokenResponse:
        try:
            # 민감정보 최소 로깅
            logger.info(f"🔵 Google auth start: sub={auth_data.sub}, email_verified={auth_data.email_verified}")

            # 1) 계정 조회/생성
            account = self.repository.get_by_oauth_sub(auth_data.sub)
            if not account:
                logger.info("📝 Creating new account")
                account_data = AccountCreate(
                    oauth_sub=auth_data.sub,
                    email=auth_data.email,
                    name=auth_data.name,
                    profile_picture=auth_data.picture,
                    email_verified=auth_data.email_verified
                )
                account = self.repository.create_account(account_data)
                logger.info(f"✅ New account created (id={account['id']})")
            else:
                logger.info(f"✅ Found existing account (id={account['id']})")

            # 2) JWT 토큰 생성(프론트 미사용이어도 스펙 유지)
            token_data = {
                "sub": str(account["id"]),
                "email": account["email"],
                "oauth_sub": auth_data.sub
            }
            access_token = self._create_access_token(token_data)

            # 3) 마지막 로그인 시간 업데이트
            try:
                self.repository.update_last_login(account["id"])
            except Exception as e:
                logger.warning(f"⚠️ last_login update failed: {e}")

            logger.info("✅ Google auth done")
            return TokenResponse(access_token=access_token)

        except Exception as e:
            logger.error(f"❌ process_google_auth error: {e}")
            raise

    def get_account_by_oauth_sub(self, oauth_sub: str):
        try:
            logger.info(f"🔍 get_account_by_oauth_sub: sub={oauth_sub}")
            account = self.repository.get_by_oauth_sub(oauth_sub)
            if not account:
                raise ValueError("Account not found")
            return account
        except Exception as e:
            logger.error(f"❌ get_account_by_oauth_sub error: {e}")
            raise

    def update_company_profile(self, oauth_sub: str, profile_data: CompanyProfile):
        try:
            logger.info(f"📝 update_company_profile: sub={oauth_sub}")
            account = self.repository.get_by_oauth_sub(oauth_sub)
            if not account:
                raise ValueError("Account not found")

            # 빈 문자열을 None으로 변환
            cleaned_data = self._clean_profile_data(profile_data)

            updated_account = self.repository.update_company_profile(oauth_sub, cleaned_data)
            if not updated_account:
                raise ValueError("Failed to update company profile")
            logger.info("✅ company profile updated")
            return updated_account
        except Exception as e:
            logger.error(f"❌ update_company_profile error: {e}")
            raise

    def create_company_profile(self, oauth_sub: str, profile_data: CompanyProfile):
        try:
            logger.info(f"📝 create_company_profile: sub={oauth_sub}")
            account = self.repository.get_by_oauth_sub(oauth_sub)
            if not account:
                raise ValueError("Account not found")

            # 빈 문자열을 None으로 변환
            cleaned_data = self._clean_profile_data(profile_data)

            # 이미 존재하면 업데이트로 전환
            if account.get("company_name"):
                logger.info("⚠️ Profile exists, updating instead")
                return self.update_company_profile(oauth_sub, cleaned_data)

            created_account = self.repository.create_company_profile(oauth_sub, cleaned_data)
            if not created_account:
                raise ValueError("Failed to create company profile")
            logger.info("✅ company profile created")
            return created_account
        except Exception as e:
            logger.error(f"❌ create_company_profile error: {e}")
            raise

    def _clean_profile_data(self, profile_data: CompanyProfile) -> CompanyProfile:
        """프로필 데이터에서 빈 문자열을 None으로 변환"""
        cleaned_data = {}
        for field, value in profile_data.dict().items():
            if isinstance(value, str) and value.strip() == "":
                cleaned_data[field] = None
            else:
                cleaned_data[field] = value
        return CompanyProfile(**cleaned_data)
