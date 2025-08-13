"""
Account Controller - 순수한 비즈니스 로직 처리
"""
import logging
from ..model.account_model import LoginData, SignupData, AccountResponse
from ..service.account_service import AccountService

logger = logging.getLogger("account-controller")

class AccountController:
    def __init__(self, account_service: AccountService):
        self.account_service = account_service
    
    def signup(self, signup_data: SignupData) -> AccountResponse:
        """회원가입 처리"""
        return self.account_service.signup(signup_data)
    
    def login(self, login_data: LoginData) -> AccountResponse:
        """로그인 처리"""
        return self.account_service.login(login_data)
