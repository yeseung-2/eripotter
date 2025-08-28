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
import json
from datetime import datetime, timedelta

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("account_service")

class AccountService:
    def __init__(self):
        self.repository = AccountRepository()
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")

    def create_access_token(self, data: dict) -> str:
        try:
            logger.info("🔑 Creating access token")
            logger.info(f"📨 Token data: {json.dumps(data, indent=2)}")
            
            to_encode = data.copy()
            expire = datetime.utcnow() + timedelta(minutes=30)
            to_encode.update({"exp": expire})
            
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm="HS256")
            logger.info("✅ Successfully created access token")
            return encoded_jwt
            
        except Exception as e:
            logger.error(f"❌ Error creating access token: {str(e)}")
            raise

    def process_google_auth(self, auth_data: GoogleAuthData) -> TokenResponse:
        try:
            logger.info("🔵 Processing Google auth")
            logger.info(f"📨 Auth data: {json.dumps(auth_data.dict(), indent=2)}")
            
            # 1. 기존 계정 확인 또는 새 계정 생성
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
                logger.info("✅ New account created")
            else:
                logger.info("✅ Found existing account")
            
            # 2. JWT 토큰 생성
            token_data = {
                "sub": str(account["id"]),
                "email": account["email"],
                "oauth_sub": auth_data.sub
            }
            access_token = self.create_access_token(token_data)
            
            # 3. 마지막 로그인 시간 업데이트는 일단 건너뛰기 (세션 문제 해결 후 추가)
            logger.info("⏭️ Skipping last login update for now")
            
            return TokenResponse(access_token=access_token)
            
        except Exception as e:
            logger.error(f"❌ Error in process_google_auth: {str(e)}")
            logger.error(f"❌ Error type: {type(e)}")
            raise

    def get_account_by_oauth_sub(self, oauth_sub: str):
        try:
            logger.info(f"🔍 Getting account by oauth_sub: {oauth_sub}")
            account = self.repository.get_by_oauth_sub(oauth_sub)
            
            if not account:
                logger.error("❌ Account not found")
                raise ValueError("Account not found")
                
            logger.info("✅ Successfully retrieved account")
            return account
            
        except Exception as e:
            logger.error(f"❌ Error getting account: {str(e)}")
            raise

    def update_company_profile(self, oauth_sub: str, profile_data: CompanyProfile):
        try:
            logger.info(f"📝 Updating company profile for oauth_sub: {oauth_sub}")
            logger.info(f"📨 Profile data: {json.dumps(profile_data.dict(), indent=2)}")
            
            account = self.repository.get_by_oauth_sub(oauth_sub)
            if not account:
                logger.error("❌ Account not found")
                raise ValueError("Account not found")
            
            updated_account = self.repository.update_company_profile(account.id, profile_data)
            logger.info("✅ Successfully updated company profile")
            return updated_account
            
        except Exception as e:
            logger.error(f"❌ Error updating company profile: {str(e)}")
            raise