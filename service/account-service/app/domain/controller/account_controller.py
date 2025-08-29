from fastapi import APIRouter, HTTPException, status
from ..service.account_service import AccountService
from ..model.account_model import (
    CompanyProfile,
    AccountResponse,
    APIResponse,
    GoogleAuthData,
    TokenResponse
)
import logging
import json

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("account_controller")

class AccountController:
    def __init__(self):
        self.router = APIRouter(prefix="/accounts")
        self.service = AccountService()
        self.setup_routes()

    def setup_routes(self):
        @self.router.post("/auth/google", response_model=TokenResponse)
        async def google_auth(auth_data: GoogleAuthData):
            """Google OAuth 인증 처리 및 JWT 토큰 발급"""
            try:
                logger.info("🔵 Received Google auth request")
                logger.info(f"📨 Auth data received: {json.dumps(auth_data.dict(), indent=2)}")
                
                result = self.service.process_google_auth(auth_data)
                logger.info("✅ Successfully processed Google auth")
                logger.info(f"🎟 Generated token: {result.access_token[:20]}...")
                
                return result
                
            except Exception as e:
                logger.error(f"❌ Error in google_auth: {str(e)}")
                logger.error(f"❌ Error type: {type(e)}")
                logger.error(f"❌ Auth data that caused error: {json.dumps(auth_data.dict(), indent=2)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e)
                )

        @self.router.get("/me", response_model=AccountResponse)
        async def get_my_account(oauth_sub: str):
            """현재 로그인한 사용자의 계정 정보 조회"""
            try:
                logger.info(f"🔍 Fetching account for oauth_sub: {oauth_sub}")
                result = self.service.get_account_by_oauth_sub(oauth_sub)
                logger.info("✅ Successfully fetched account info")
                return result
            except ValueError as e:
                logger.error(f"❌ Error fetching account: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=str(e)
                )

        @self.router.post("/profile", response_model=AccountResponse)
        async def create_company_profile(
            profile_data: CompanyProfile,
            oauth_sub: str
        ):
            """기업 프로필 정보 생성/저장"""
            try:
                logger.info(f"📝 Creating profile for oauth_sub: {oauth_sub}")
                logger.info(f"📨 Profile data: {json.dumps(profile_data.dict(), indent=2)}")
                
                result = self.service.create_company_profile(oauth_sub, profile_data)
                logger.info("✅ Successfully created company profile")
                return result
                
            except ValueError as e:
                logger.error(f"❌ Error creating profile: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )

        @self.router.put("/profile", response_model=AccountResponse)
        async def update_company_profile(
            profile_data: CompanyProfile,
            oauth_sub: str
        ):
            """기업 프로필 정보 업데이트"""
            try:
                logger.info(f"📝 Updating profile for oauth_sub: {oauth_sub}")
                logger.info(f"📨 Profile data: {json.dumps(profile_data.dict(), indent=2)}")
                
                result = self.service.update_company_profile(oauth_sub, profile_data)
                logger.info("✅ Successfully updated company profile")
                return result
                
            except ValueError as e:
                logger.error(f"❌ Error updating profile: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )