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

logger = logging.getLogger("account_controller")

class AccountController:
    def __init__(self):
        self.router = APIRouter(prefix="/accounts", tags=["accounts"])
        self.service = AccountService()
        self.setup_routes()

    def setup_routes(self):
        @self.router.post("/auth/google", response_model=TokenResponse)
        async def google_auth(auth_data: GoogleAuthData):
            """Google OAuth 인증 처리 및 JWT 토큰 발급"""
            try:
                logger.info(f"🔵 Received Google auth request: sub={auth_data.sub}")
                result = self.service.process_google_auth(auth_data)
                logger.info("✅ Successfully processed Google auth")
                return result
            except Exception as e:
                logger.error(f"❌ Error in google_auth: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to process Google OAuth"
                )

        @self.router.get("/me", response_model=AccountResponse)
        async def get_my_account(oauth_sub: str):
            """현재 로그인한 사용자의 계정 정보 조회"""
            try:
                logger.info(f"🔍 Fetching account for oauth_sub: {oauth_sub}")
                result = self.service.get_account_by_oauth_sub(oauth_sub)
                return result
            except ValueError as e:
                logger.warning(f"❌ Account not found: {str(e)}")
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
                logger.info(f"📝 Profile data received: {profile_data.dict()}")
                result = self.service.create_company_profile(oauth_sub, profile_data)
                logger.info("✅ Profile created successfully")
                return result
            except ValueError as e:
                logger.warning(f"❌ Error creating profile: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
            except Exception as e:
                logger.error(f"❌ Unexpected error in create_company_profile: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error"
                )

        @self.router.put("/profile", response_model=AccountResponse)
        async def update_company_profile(
            profile_data: CompanyProfile,
            oauth_sub: str
        ):
            """기업 프로필 정보 업데이트"""
            try:
                logger.info(f"📝 Updating profile for oauth_sub: {oauth_sub}")
                logger.info(f"📝 Profile data received: {profile_data.dict()}")
                result = self.service.update_company_profile(oauth_sub, profile_data)
                logger.info("✅ Profile updated successfully")
                return result
            except ValueError as e:
                logger.warning(f"❌ Error updating profile: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
            except Exception as e:
                logger.error(f"❌ Unexpected error in update_company_profile: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error"
                )
