from fastapi import APIRouter
from ..domain.controller.account_controller import AccountController

logger = logging.getLogger("account-router")

# 라우터 생성
router = APIRouter(
    prefix="/api/v1/accounts",
    tags=["accounts"]
)

# 컨트롤러 인스턴스 생성 및 라우터 등록
account_controller = AccountController()
router.include_router(account_controller.router)
