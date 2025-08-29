"""
Report Router - ESG 매뉴얼 기반 보고서 API 라우팅
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any, Optional
from ..domain.controller.report_controller import ReportController, get_report_controller
from ..domain.model.report_model import (
    ReportCreateRequest, ReportCreateResponse,
    ReportGetResponse, ReportUpdateRequest, ReportUpdateResponse,
    ReportDeleteResponse, ReportListResponse, ReportCompleteRequest, ReportCompleteResponse,
    IndicatorDraftRequest, IndicatorSaveRequest,
    IndicatorListResponse, IndicatorInputFieldResponse, IndicatorDraftResponse
)

router = APIRouter(tags=["reports"])

# 기본 CRUD
@router.post("/reports", response_model=ReportCreateResponse)
async def create_report(
    request: ReportCreateRequest,
    controller: ReportController = Depends(get_report_controller),
):
    return controller.create_report(request)

@router.get("/reports/{topic}/{company_name}", response_model=ReportGetResponse)
async def get_report(
    topic: str,
    company_name: str,
    controller: ReportController = Depends(get_report_controller),
):
    return controller.get_report(topic, company_name)

@router.put("/reports", response_model=ReportUpdateResponse)
async def update_report(
    request: ReportUpdateRequest,
    controller: ReportController = Depends(get_report_controller),
):
    return controller.update_report(request)

@router.delete("/reports/{topic}/{company_name}", response_model=ReportDeleteResponse)
async def delete_report(
    topic: str,
    company_name: str,
    controller: ReportController = Depends(get_report_controller),
):
    return controller.delete_report(topic, company_name)

@router.post("/reports/complete", response_model=ReportCompleteResponse)
async def complete_report(
    request: ReportCompleteRequest,
    controller: ReportController = Depends(get_report_controller),
):
    return controller.complete_report(request.topic, request.company_name)

# 목록
@router.get("/reports/company/{company_name}", response_model=ReportListResponse)
async def get_reports_by_company(
    company_name: str,
    controller: ReportController = Depends(get_report_controller),
):
    return controller.get_reports_by_company(company_name)

@router.get("/reports/company/{company_name}/type/{report_type}", response_model=ReportListResponse)
async def get_reports_by_type(
    company_name: str,
    report_type: str,
    controller: ReportController = Depends(get_report_controller),
):
    return controller.get_reports_by_type(company_name, report_type)

@router.get("/reports/status/{company_name}")
async def get_report_status(
    company_name: str,
    controller: ReportController = Depends(get_report_controller),
):
    return controller.get_report_status(company_name)

# ESG 매뉴얼 기반 지표 API
@router.get("/reports/indicator/{indicator_id}/summary")
async def get_indicator_summary(
    indicator_id: str,
    controller: ReportController = Depends(get_report_controller),
):
    return controller.get_indicator_summary(indicator_id)

@router.get("/reports/indicator/{indicator_id}/input-fields")
async def generate_input_fields(
    indicator_id: str,
    controller: ReportController = Depends(get_report_controller),
):
    return controller.generate_input_fields(indicator_id)

@router.post("/reports/indicator/{indicator_id}/draft")
async def generate_indicator_draft(
    indicator_id: str,
    body: IndicatorDraftRequest,
    controller: ReportController = Depends(get_report_controller),
):
    """
    Body 예:
    {
      "company_name": "ACME",
      "inputs": { ... }
    }
    """
    return controller.generate_indicator_draft(indicator_id, body.company_name, body.inputs)

@router.post("/reports/indicator/{indicator_id}/save")
async def save_indicator_data(
    indicator_id: str,
    body: IndicatorSaveRequest,
    controller: ReportController = Depends(get_report_controller),
):
    """
    Body 예:
    {
      "company_name": "ACME",
      "inputs": { ... }
    }
    """
    return controller.save_indicator_data(indicator_id, body.company_name, body.inputs)

@router.get("/reports/indicator/{indicator_id}/data")
async def get_indicator_data(
    indicator_id: str,
    company_name: str,
    controller: ReportController = Depends(get_report_controller),
):
    return controller.get_indicator_data(indicator_id, company_name)

# ===== 지표 관리 API =====

@router.get("/indicators", response_model=IndicatorListResponse)
async def get_all_indicators(
    controller: ReportController = Depends(get_report_controller),
):
    """모든 활성 지표 조회"""
    return controller.get_all_indicators()

@router.get("/indicators/category/{category}", response_model=IndicatorListResponse)
async def get_indicators_by_category(
    category: str,
    controller: ReportController = Depends(get_report_controller),
):
    """카테고리별 지표 조회"""
    return controller.get_indicators_by_category(category)

@router.get("/indicators/{indicator_id}/fields", response_model=IndicatorInputFieldResponse)
async def get_indicator_with_recommended_fields(
    indicator_id: str,
    controller: ReportController = Depends(get_report_controller),
):
    """지표 정보와 추천 입력 필드 조회"""
    return controller.get_indicator_with_recommended_fields(indicator_id)

@router.post("/indicators/{indicator_id}/enhanced-draft", response_model=IndicatorDraftResponse)
async def generate_enhanced_draft(
    indicator_id: str,
    body: IndicatorDraftRequest,
    controller: ReportController = Depends(get_report_controller),
):
    """향상된 보고서 초안 생성 (추천 필드 포함)"""
    return controller.generate_enhanced_draft(indicator_id, body.company_name, body.inputs)

# 헬스체크
@router.get("/reports/health")
async def health_check():
    return {"status": "healthy", "service": "report-service"}
