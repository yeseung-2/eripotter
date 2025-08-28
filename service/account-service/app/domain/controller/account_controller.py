from fastapi import APIRouter, HTTPException, status
from ..service.account_service import AccountService
from ..model.account_model import (
    CompanyProfile,
    AccountResponse,
    APIResponse,
    GoogleAuthData,
    TokenResponse
)

class AccountController:
    def __init__(self):
        self.router = APIRouter()
        self.service = AccountService()
        self.setup_routes()

    def setup_routes(self):
        @self.router.post("/auth/google", response_model=TokenResponse)
        async def google_auth(auth_data: GoogleAuthData):
            """Google OAuth 인증 처리 및 JWT 토큰 발급"""
            try:
                return self.service.process_google_auth(auth_data)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e)
                )

        @self.router.get("/me", response_model=AccountResponse)
        async def get_my_account(oauth_sub: str):
            """현재 로그인한 사용자의 계정 정보 조회"""
            try:
                return self.service.get_account_by_oauth_sub(oauth_sub)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=str(e)
                )

        @self.router.put("/me/profile", response_model=AccountResponse)
        async def update_company_profile(
            profile_data: CompanyProfile,
            oauth_sub: str
        ):
            """기업 프로필 정보 업데이트"""
            try:
                return self.service.update_company_profile(oauth_sub, profile_data)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )