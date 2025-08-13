from fastapi import APIRouter, HTTPException
import logging
from ..model.account_model import LoginData, SignupData, AccountResponse
from ..service.account_service import AccountService

logger = logging.getLogger("account-controller")

class AccountController:
    def __init__(self, account_service: AccountService):
        self.account_service = account_service
        self.router = APIRouter(prefix="", tags=["account"])
        self._setup_routes()
    
    def _setup_routes(self):
        @self.router.post("/signup", response_model=AccountResponse)
        async def signup(signup_data: SignupData):
            """회원가입"""
            return self.account_service.signup(signup_data)
        
        @self.router.post("/login", response_model=AccountResponse)
        async def login(login_data: LoginData):
            """로그인"""
            return self.account_service.login(login_data)
    
    def get_router(self):
        return self.router
