"""
Account Service - 비즈니스 로직 및 보안 처리
"""
from fastapi import HTTPException
import logging
from typing import Dict, Any
from ..repository.account_repository import AccountRepository
from ..model.account_model import LoginData, SignupData, AccountResponse

logger = logging.getLogger("account-service")

class AccountService:
    def __init__(self, account_repository: AccountRepository):
        self.account_repository = account_repository
    
    def signup(self, signup_data: SignupData) -> AccountResponse:
        """회원가입 서비스"""
        logger.info(f"📝 회원가입 요청: user_id={signup_data.user_id}, company_id={signup_data.company_id}")
        
        try:
            # 비밀번호 해시화
            hashed_password = hash_password(signup_data.user_pw)
            logger.info(f"🔐 비밀번호 해시화 완료: {signup_data.user_id}")
            
            success = self.account_repository.create_user(
                signup_data.user_id, 
                hashed_password, 
                signup_data.company_id
            )
            
            if success:
                logger.info(f"✅ 회원가입 성공: {signup_data.user_id}")
                return AccountResponse(
                    status="success",
                    message="회원가입 성공",
                    user_id=signup_data.user_id,
                    company_id=signup_data.company_id
                )
            else:
                logger.warning(f"⚠️ 회원가입 실패 - 이미 존재하는 사용자: {signup_data.user_id}")
                raise HTTPException(status_code=409, detail="이미 존재하는 사용자 ID입니다.")
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ 회원가입 서비스 오류: {e}")
            logger.error(f"📋 상세 정보: user_id={signup_data.user_id}, company_id={signup_data.company_id}")
            import traceback
            logger.error(f"📋 스택 트레이스:\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"회원가입 실패: {str(e)}")
    
    def login(self, login_data: LoginData) -> AccountResponse:
        """로그인 서비스"""
        logger.info(f"🔑 로그인 요청: user_id={login_data.user_id}")
        
        try:
            user = self.account_repository.get_user(login_data.user_id)
            
            if not user:
                logger.warning(f"⚠️ 로그인 실패 - 사용자 없음: {login_data.user_id}")
                raise HTTPException(status_code=401, detail="로그인 실패: 사용자 ID 또는 비밀번호가 올바르지 않습니다.")
            
            # 비밀번호 검증
            if verify_password(login_data.user_pw, user["user_pw"]):
                logger.info(f"✅ 로그인 성공: {login_data.user_id}")
                return AccountResponse(
                    status="success",
                    message="로그인 성공",
                    user_id=user["user_id"],
                    company_id=user["company_id"],
                    user_name=user.get("user_name"),
                    user={
                        "user_id": user["user_id"],
                        "company_id": user["company_id"],
                        "user_name": user.get("user_name")
                    }
                )
            else:
                logger.warning(f"⚠️ 로그인 실패 - 비밀번호 불일치: {login_data.user_id}")
                raise HTTPException(status_code=401, detail="로그인 실패: 사용자 ID 또는 비밀번호가 올바르지 않습니다.")
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ 로그인 서비스 오류: {e}")
            logger.error(f"📋 상세 정보: user_id={login_data.user_id}")
            import traceback
            logger.error(f"📋 스택 트레이스:\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"로그인 실패: {str(e)}")
    
    def get_user_count(self) -> int:
        """사용자 수 조회"""
        try:
            count = self.account_repository.get_user_count()
            logger.info(f"📊 사용자 수 조회 성공: {count}명")
            return count
        except Exception as e:
            logger.error(f"❌ 사용자 수 조회 오류: {e}")
            import traceback
            logger.error(f"📋 스택 트레이스:\n{traceback.format_exc()}")
            raise
