from fastapi import APIRouter
from ..controller.report_controller import router as report_controller_router

router = APIRouter()
router.include_router(report_controller_router)
