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
            
            updated_account = self.repository.update_company_profile(oauth_sub, profile_data)
            if updated_account:
                # Account 객체를 딕셔너리로 변환
                account_dict = {
                    "id": updated_account.id,
                    "oauth_sub": updated_account.oauth_sub,
                    "email": updated_account.email,
                    "name": updated_account.name,
                    "profile_picture": updated_account.profile_picture,
                    "company_name": updated_account.company_name,
                    "company_type": updated_account.company_type,
                    "industry": updated_account.industry,
                    "business_number": updated_account.business_number,
                    "establishment_date": updated_account.establishment_date,
                    "employee_count": updated_account.employee_count,
                    "annual_revenue": updated_account.annual_revenue,
                    "business_area": updated_account.business_area,
                    "factory_count": updated_account.factory_count,
                    "factory_address": updated_account.factory_address,
                    "production_items": updated_account.production_items,
                    "department": updated_account.department,
                    "phone_number": updated_account.phone_number,
                    "email_verified": updated_account.email_verified,
                    "created_at": updated_account.created_at,
                    "updated_at": updated_account.updated_at
                }
                logger.info("✅ Successfully updated company profile")
                return account_dict
            else:
                raise ValueError("Failed to update company profile")
            
        except Exception as e:
            logger.error(f"❌ Error updating company profile: {str(e)}")
            raise

    def create_company_profile(self, oauth_sub: str, profile_data: CompanyProfile):
        try:
            logger.info(f"📝 Creating company profile for oauth_sub: {oauth_sub}")
            logger.info(f"📨 Profile data: {json.dumps(profile_data.dict(), indent=2)}")
            
            account = self.repository.get_by_oauth_sub(oauth_sub)
            if not account:
                logger.error("❌ Account not found")
                raise ValueError("Account not found")
            
            # 프로필이 이미 존재하는지 확인 (company_name이 null이 아닌 경우)
            if account.get("company_name") and account.get("company_name") != "":
                logger.info("⚠️ Profile already exists, updating instead")
                return self.update_company_profile(oauth_sub, profile_data)
            
            created_account = self.repository.create_company_profile(oauth_sub, profile_data)
            if created_account:
                # Account 객체를 딕셔너리로 변환
                account_dict = {
                    "id": created_account.id,
                    "oauth_sub": created_account.oauth_sub,
                    "email": created_account.email,
                    "name": created_account.name,
                    "profile_picture": created_account.profile_picture,
                    "company_name": created_account.company_name,
                    "company_type": created_account.company_type,
                    "industry": created_account.industry,
                    "business_number": created_account.business_number,
                    "establishment_date": created_account.establishment_date,
                    "employee_count": created_account.employee_count,
                    "annual_revenue": created_account.annual_revenue,
                    "business_area": created_account.business_area,
                    "factory_count": created_account.factory_count,
                    "factory_address": created_account.factory_address,
                    "production_items": created_account.production_items,
                    "department": created_account.department,
                    "phone_number": created_account.phone_number,
                    "email_verified": created_account.email_verified,
                    "created_at": created_account.created_at,
                    "updated_at": created_account.updated_at
                }
                logger.info("✅ Successfully created company profile")
                return account_dict
            else:
                raise ValueError("Failed to create company profile")
            
        except Exception as e:
            logger.error(f"❌ Error creating company profile: {str(e)}")
            raise