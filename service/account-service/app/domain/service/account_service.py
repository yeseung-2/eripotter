from datetime import datetime, timedelta
import jwt
import os
from ..model.account_model import (
    GoogleAuthData,
    TokenResponse,
    CompanyProfile,
    AccountResponse
)
from ..repository.account_repository import AccountRepository

class AccountService:
    def __init__(self):
        self.repository = AccountRepository()
        self.jwt_secret = os.getenv("JWT_SECRET_KEY")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    def create_jwt_token(self, data: dict) -> str:
        """JWT 토큰 생성"""
        expire = datetime.utcnow() + timedelta(minutes=self.token_expire_minutes)
        to_encode = data.copy()
        to_encode.update({"exp": expire})
        
        return jwt.encode(
            to_encode,
            self.jwt_secret,
            algorithm=self.jwt_algorithm
        )

    def process_google_auth(self, auth_data: GoogleAuthData) -> TokenResponse:
        """Google OAuth 인증 처리"""
        # 1. 사용자 조회 또는 생성
        account = self.repository.get_by_oauth_sub(auth_data.sub)
        if not account:
            account = self.repository.create_account({
                "oauth_sub": auth_data.sub,
                "email": auth_data.email,
                "name": auth_data.name,
                "profile_picture": auth_data.picture
            })

        # 2. JWT 토큰 생성
        token = self.create_jwt_token({
            "sub": account.oauth_sub,
            "email": account.email,
            "name": account.name
        })

        # 3. 마지막 로그인 시간 업데이트
        self.repository.update_last_login(account.oauth_sub)

        return TokenResponse(
            access_token=token,
            token_type="bearer"
        )

    def get_account_by_oauth_sub(self, oauth_sub: str) -> AccountResponse:
        """OAuth sub로 계정 정보 조회"""
        account = self.repository.get_by_oauth_sub(oauth_sub)
        if not account:
            raise ValueError("Account not found")
        return AccountResponse.from_orm(account)

    def update_company_profile(self, oauth_sub: str, profile_data: CompanyProfile) -> AccountResponse:
        """기업 프로필 정보 업데이트"""
        # 1. 사업자 번호 중복 확인
        existing = self.repository.get_by_business_number(profile_data.business_number)
        if existing and existing.oauth_sub != oauth_sub:
            raise ValueError("Business number already registered")
        
        # 2. 프로필 업데이트
        account = self.repository.update_company_profile(oauth_sub, profile_data)
        if not account:
            raise ValueError("Account not found")
        
        return AccountResponse.from_orm(account)