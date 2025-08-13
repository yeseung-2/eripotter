"""
Account Service - 비즈니스 로직 및 보안 처리
"""
from fastapi import HTTPException
import logging
from typing import Dict, Any
from ..repository.account_repository import AccountRepository
from ..model.account_model import LoginData, SignupData, AccountResponse
from ...common.security import hash_password, verify_password

logger = logging.getLogger("account-service")

class AccountService:
    def __init__(self, account_repository: AccountRepository):
        self.account_repository = account_repository
    
    def signup(self, signup_data: SignupData) -> AccountResponse:
        """회원가입 서비스"""
        logger.info(f"Signup request: user_id={signup_data.user_id}, company_id={signup_data.company_id}")
        
        try:
            # 비밀번호 해시화
            hashed_password = hash_password(signup_data.user_pw)
            
            success = self.account_repository.create_user(
                signup_data.user_id, 
                hashed_password, 
                signup_data.company_id
            )
            
            if success:
                return AccountResponse(
                    status="success",
                    message="회원가입 성공",
                    user_id=signup_data.user_id,
                    company_id=signup_data.company_id
                )
            else:
                raise HTTPException(status_code=409, detail="이미 존재하는 사용자 ID입니다.")
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Signup service error: {e}")
            raise HTTPException(status_code=500, detail=f"회원가입 실패: {str(e)}")
    
    def login(self, login_data: LoginData) -> AccountResponse:
        """로그인 서비스"""
        logger.info(f"Login request: user_id={login_data.user_id}")
        
        try:
            user = self.account_repository.get_user(login_data.user_id)
            
            if not user:
                raise HTTPException(status_code=401, detail="로그인 실패: 사용자 ID 또는 비밀번호가 올바르지 않습니다.")
            
            # 비밀번호 검증
            if verify_password(login_data.user_pw, user["user_pw"]):
                return AccountResponse(
                    status="success",
                    message="로그인 성공",
                    user_id=user["user_id"],
                    company_id=user["company_id"]
                )
            else:
                raise HTTPException(status_code=401, detail="로그인 실패: 사용자 ID 또는 비밀번호가 올바르지 않습니다.")
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login service error: {e}")
            raise HTTPException(status_code=500, detail=f"로그인 실패: {str(e)}")
    
    def get_user_count(self) -> int:
        """사용자 수 조회"""
        try:
            return self.account_repository.get_user_count()
        except Exception as e:
            logger.error(f"Get user count error: {e}")
            raise
