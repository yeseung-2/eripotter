"""
Report Controller - ESG 매뉴얼 기반 보고서 API 엔드포인트 처리 (세션-안전 리팩토링)
"""
from typing import Dict, Any, Optional
from fastapi import HTTPException
import logging

from eripotter_common.database import get_session
from ..repository.report_repository import ReportRepository
from ..model.report_model import (
    ReportCreateRequest, ReportCreateResponse,
    ReportGetRequest, ReportGetResponse,
    ReportUpdateRequest, ReportUpdateResponse,
    ReportDeleteRequest, ReportDeleteResponse,
    ReportListResponse, ReportCompleteRequest, ReportCompleteResponse,
    IndicatorListResponse, IndicatorInputFieldResponse, IndicatorDraftResponse
)
from ..service.report_service import ReportService

logger = logging.getLogger(__name__)


class ReportController:
    """ESG 매뉴얼 기반 보고서 API 컨트롤러"""

    def __init__(self):
        # 서비스는 요청 단위로 세션을 열어 생성 (여기서는 보관하지 않음)
        pass

    # ===== 기본 CRUD =====
    def create_report(self, request: ReportCreateRequest) -> ReportCreateResponse:
        try:
            with get_session() as db:
                service = ReportService(db)
                return service.create_report(request)
        except Exception as e:
            logger.error(f"보고서 생성 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"보고서 생성 중 오류가 발생했습니다: {str(e)}")

    def get_report(self, topic: str, company_name: str) -> ReportGetResponse:
        try:
            with get_session() as db:
                service = ReportService(db)
                req = ReportGetRequest(topic=topic, company_name=company_name)
                return service.get_report(req)
        except ValueError as e:
            # 서비스에서 미존재 등으로 ValueError를 던지면 404로 매핑
            logger.warning(f"보고서 조회 404: {e}")
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error(f"보고서 조회 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"보고서 조회 중 오류가 발생했습니다: {str(e)}")

    def update_report(self, request: ReportUpdateRequest) -> ReportUpdateResponse:
        try:
            with get_session() as db:
                service = ReportService(db)
                return service.update_report(request)
        except Exception as e:
            logger.error(f"보고서 업데이트 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"보고서 업데이트 중 오류가 발생했습니다: {str(e)}")

    def delete_report(self, topic: str, company_name: str) -> ReportDeleteResponse:
        try:
            with get_session() as db:
                service = ReportService(db)
                req = ReportDeleteRequest(topic=topic, company_name=company_name)
                return service.delete_report(req)
        except Exception as e:
            logger.error(f"보고서 삭제 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"보고서 삭제 중 오류가 발생했습니다: {str(e)}")

    def get_reports_by_company(self, company_name: str) -> ReportListResponse:
        try:
            with get_session() as db:
                service = ReportService(db)
                return service.get_reports_by_company(company_name)
        except Exception as e:
            logger.error(f"회사별 보고서 목록 조회 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"보고서 목록 조회 중 오류가 발생했습니다: {str(e)}")

    def get_reports_by_type(self, company_name: str, report_type: str) -> ReportListResponse:
        try:
            with get_session() as db:
                service = ReportService(db)
                return service.get_reports_by_type(company_name, report_type)
        except Exception as e:
            logger.error(f"유형별 보고서 목록 조회 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"보고서 목록 조회 중 오류가 발생했습니다: {str(e)}")

    def complete_report(self, topic: str, company_name: str) -> ReportCompleteResponse:
        try:
            with get_session() as db:
                service = ReportService(db)
                req = ReportCompleteRequest(topic=topic, company_name=company_name)
                return service.complete_report(req)
        except Exception as e:
            logger.error(f"보고서 완료 처리 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"보고서 완료 처리 중 오류가 발생했습니다: {str(e)}")

    def get_report_status(self, company_name: str) -> Dict[str, str]:
        try:
            with get_session() as db:
                service = ReportService(db)
                return service.get_report_status(company_name)
        except Exception as e:
            logger.error(f"보고서 상태 조회 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"보고서 상태 조회 중 오류가 발생했습니다: {str(e)}")

    # ===== ESG 매뉴얼 기반 지표 =====
    def get_indicator_summary(self, indicator_id: str) -> str:
        try:
            with get_session() as db:
                service = ReportService(db)
                return service.get_indicator_summary(indicator_id)
        except Exception as e:
            logger.error(f"지표 요약 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"지표 요약 생성 중 오류가 발생했습니다: {str(e)}")

    def generate_input_fields(self, indicator_id: str) -> Dict[str, Any]:
        try:
            with get_session() as db:
                service = ReportService(db)
                return service.generate_input_fields(indicator_id)
        except Exception as e:
            logger.error(f"입력 필드 생성 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"입력 필드 생성 중 오류가 발생했습니다: {str(e)}")

    def generate_indicator_draft(self, indicator_id: str, company_name: str, inputs: Dict[str, Any]) -> str:
        try:
            with get_session() as db:
                service = ReportService(db)
                return service.generate_indicator_draft(indicator_id, company_name, inputs)
        except Exception as e:
            logger.error(f"지표 초안 생성 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"지표 초안 생성 중 오류가 발생했습니다: {str(e)}")

    def save_indicator_data(self, indicator_id: str, company_name: str, inputs: Dict[str, Any]) -> bool:
        try:
            with get_session() as db:
                service = ReportService(db)
                return service.save_indicator_data(indicator_id, company_name, inputs)
        except Exception as e:
            logger.error(f"지표 데이터 저장 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"지표 데이터 저장 중 오류가 발생했습니다: {str(e)}")

    def get_indicator_data(self, indicator_id: str, company_name: str) -> Optional[Dict[str, Any]]:
        try:
            with get_session() as db:
                service = ReportService(db)
                return service.get_indicator_data(indicator_id, company_name)
        except Exception as e:
            logger.error(f"지표 데이터 조회 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"지표 데이터 조회 중 오류가 발생했습니다: {str(e)}")

    # ===== 지표 관리 =====
    def get_all_indicators(self) -> IndicatorListResponse:
        try:
            with get_session() as db:
                service = ReportService(db)
                return service.get_all_indicators()
        except Exception as e:
            logger.error(f"지표 목록 조회 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"지표 목록 조회 중 오류가 발생했습니다: {str(e)}")

    def get_indicators_by_category(self, category: str) -> IndicatorListResponse:
        try:
            with get_session() as db:
                service = ReportService(db)
                return service.get_indicators_by_category(category)
        except Exception as e:
            logger.error(f"카테고리별 지표 조회 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"카테고리별 지표 조회 중 오류가 발생했습니다: {str(e)}")

    def get_indicator_with_recommended_fields(self, indicator_id: str) -> IndicatorInputFieldResponse:
        try:
            with get_session() as db:
                service = ReportService(db)
                return service.get_indicator_with_recommended_fields(indicator_id)
        except Exception as e:
            logger.error(f"지표 정보 조회 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"지표 정보 조회 중 오류가 발생했습니다: {str(e)}")

    def generate_enhanced_draft(self, indicator_id: str, company_name: str, inputs: Dict[str, Any]) -> IndicatorDraftResponse:
        try:
            with get_session() as db:
                service = ReportService(db)
                return service.generate_enhanced_draft(indicator_id, company_name, inputs)
        except Exception as e:
            logger.error(f"향상된 초안 생성 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"향상된 초안 생성 중 오류가 발생했습니다: {str(e)}")


def get_report_controller() -> ReportController:
    return ReportController()
