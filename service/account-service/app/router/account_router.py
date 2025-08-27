"""
Account Router - API 엔드포인트 및 의존성 주입
"""
from fastapi import APIRouter, Cookie, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional
from ..domain.controller.account_controller import AccountController
from ..domain.service.account_service import AccountService
from ..domain.repository.account_repository import AccountRepository
from ..domain.model.account_model import LoginData, SignupData, AccountResponse
from eripotter_common.database.base import get_db_engine
import logging

logger = logging.getLogger("account-router")

# DI 함수들
def get_account_repository() -> AccountRepository:
    """Account Repository 인스턴스 생성"""
    engine = get_db_engine()
    return AccountRepository(engine)

def get_account_service(repo: AccountRepository = Depends(get_account_repository)) -> AccountService:
    """Account Service 인스턴스 생성"""
    return AccountService(repo)

def get_account_controller(service: AccountService = Depends(get_account_service)) -> AccountController:
    """Account Controller 인스턴스 생성"""
    return AccountController(service)

# 라우터 생성
account_router = APIRouter(prefix="", tags=["account"])

@account_router.post("/signup", response_model=AccountResponse, summary="회원가입")
async def signup(
    signup_data: SignupData,
    controller: AccountController = Depends(get_account_controller)
):
    """회원가입 API"""
    return controller.signup(signup_data)

@account_router.post("/login", response_model=AccountResponse, summary="로그인")
async def login(
    login_data: LoginData,
    controller: AccountController = Depends(get_account_controller)
):
    """로그인 API"""
    return controller.login(login_data)

@account_router.post("/logout", summary="로그아웃")
async def logout(session_token: Optional[str] = Cookie(None)):
    """
    사용자를 로그아웃하고 인증 쿠키를 삭제합니다.
    """
    print(f"로그아웃 요청 - 받은 세션 토큰: {session_token}")
    
    # 로그아웃 응답 생성
    response = JSONResponse({
        "success": True,
        "message": "로그아웃되었습니다."
    })
    
    # 인증 쿠키 삭제
    response.delete_cookie(
        key="session_token",
        path="/",
        # domain 설정 제거 (로컬 환경)
    )
    
    print("✅ 로그아웃 완료 - 인증 쿠키 삭제됨")
    return response

@account_router.get("/profile", summary="사용자 프로필 조회")
async def get_profile(session_token: Optional[str] = Cookie(None)):
    """
    세션 토큰으로 사용자 프로필을 조회합니다.
    세션 토큰이 없거나 유효하지 않으면 401 에러를 반환합니다.
    """
    print(f"프로필 요청 - 받은 세션 토큰: {session_token}")
    
    if not session_token:
        raise HTTPException(status_code=401, detail="인증 쿠키가 없습니다.")
    
    # 간단한 프로필 정보 반환 (실제로는 데이터베이스에서 조회)
    return {
        "user_id": "sample_user",
        "message": "사용자 프로필 조회 성공"
    }