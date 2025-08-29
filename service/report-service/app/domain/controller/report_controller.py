"""
Report Controller - ESG 매뉴얼 기반 보고서 API 엔드포인트 처리
"""
from typing import Dict, Any, Optional
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from eripotter_common.database import get_session
from ..repository.report_repository import ReportRepository
from ..model.report_model import (
    ReportCreateRequest, ReportCreateResponse,
    ReportGetRequest, ReportGetResponse,
    ReportUpdateRequest, ReportUpdateResponse,
    ReportDeleteRequest, ReportDeleteResponse,
    ReportListResponse, ReportCompleteRequest, ReportCompleteResponse
)
import logging

logger = logging.getLogger(__name__)

class ReportController:
    """ESG 매뉴얼 기반 보고서 API 컨트롤러"""

    def __init__(self):
        pass

    def create_report(self, request: ReportCreateRequest) -> ReportCreateResponse:
        try:
            with get_session() as db:
                repository = ReportRepository(db)
                # 간단한 응답으로 수정
                return ReportCreateResponse(
                    success=True,
                    message="보고서 생성 요청이 처리되었습니다.",
                    report_id=f"{request.topic}_{request.company_name}"
                )
        except Exception as e:
            logger.error(f"보고서 생성 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"보고서 생성 중 오류가 발생했습니다: {str(e)}")

    def get_report(self, topic: str, company_name: str) -> ReportGetResponse:
        try:
            request = ReportGetRequest(topic=topic, company_name=company_name)
            return self.report_service.get_report(request)
        except Exception as e:
            logger.error(f"보고서 조회 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"보고서 조회 중 오류가 발생했습니다: {str(e)}")

    def update_report(self, request: ReportUpdateRequest) -> ReportUpdateResponse:
        try:
            return self.report_service.update_report(request)
        except Exception as e:
            logger.error(f"보고서 업데이트 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"보고서 업데이트 중 오류가 발생했습니다: {str(e)}")

    def delete_report(self, topic: str, company_name: str) -> ReportDeleteResponse:
        try:
            request = ReportDeleteRequest(topic=topic, company_name=company_name)
            return self.report_service.delete_report(request)
        except Exception as e:
            logger.error(f"보고서 삭제 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"보고서 삭제 중 오류가 발생했습니다: {str(e)}")

    def get_reports_by_company(self, company_name: str) -> ReportListResponse:
        try:
            return self.report_service.get_reports_by_company(company_name)
        except Exception as e:
            logger.error(f"회사별 보고서 목록 조회 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"보고서 목록 조회 중 오류가 발생했습니다: {str(e)}")

    def get_reports_by_type(self, company_name: str, report_type: str) -> ReportListResponse:
        try:
            return self.report_service.get_reports_by_type(company_name, report_type)
        except Exception as e:
            logger.error(f"유형별 보고서 목록 조회 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"보고서 목록 조회 중 오류가 발생했습니다: {str(e)}")

    def complete_report(self, topic: str, company_name: str) -> ReportCompleteResponse:
        try:
            request = ReportCompleteRequest(topic=topic, company_name=company_name)
            return self.report_service.complete_report(request)
        except Exception as e:
            logger.error(f"보고서 완료 처리 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"보고서 완료 처리 중 오류가 발생했습니다: {str(e)}")

    def get_report_status(self, company_name: str) -> Dict[str, str]:
        try:
            return self.report_service.get_report_status(company_name)
        except Exception as e:
            logger.error(f"보고서 상태 조회 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"보고서 상태 조회 중 오류가 발생했습니다: {str(e)}")

    # ESG 매뉴얼 기반 지표별 API
    def get_indicator_summary(self, indicator_id: str) -> str:
        try:
            return self.report_service.get_indicator_summary(indicator_id)
        except Exception as e:
            logger.error(f"지표 요약 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"지표 요약 생성 중 오류가 발생했습니다: {str(e)}")

    def generate_input_fields(self, indicator_id: str) -> Dict[str, Any]:
        try:
            return self.report_service.generate_input_fields(indicator_id)
        except Exception as e:
            logger.error(f"입력 필드 생성 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"입력 필드 생성 중 오류가 발생했습니다: {str(e)}")

    def generate_indicator_draft(self, indicator_id: str, company_name: str, inputs: Dict[str, Any]) -> str:
        try:
            return self.report_service.generate_indicator_draft(indicator_id, company_name, inputs)
        except Exception as e:
            logger.error(f"지표 초안 생성 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"지표 초안 생성 중 오류가 발생했습니다: {str(e)}")

    def save_indicator_data(self, indicator_id: str, company_name: str, inputs: Dict[str, Any]) -> bool:
        try:
            return self.report_service.save_indicator_data(indicator_id, company_name, inputs)
        except Exception as e:
            logger.error(f"지표 데이터 저장 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"지표 데이터 저장 중 오류가 발생했습니다: {str(e)}")

    def get_indicator_data(self, indicator_id: str, company_name: str) -> Optional[Dict[str, Any]]:
        try:
            return self.report_service.get_indicator_data(indicator_id, company_name)
        except Exception as e:
            logger.error(f"지표 데이터 조회 API 오류: {e}")
            raise HTTPException(status_code=500, detail=f"지표 데이터 조회 중 오류가 발생했습니다: {str(e)}")


def get_report_controller() -> ReportController:
    return ReportController()
