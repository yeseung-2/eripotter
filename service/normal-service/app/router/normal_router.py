"""
Normal Router - API 엔드포인트 및 의존성 주입
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List, Optional
from datetime import datetime
import logging

# Domain imports
from ..domain.service.normal_service import NormalService
from ..domain.controller.normal_controller import NormalController
from ..domain.model.substance_mapping_model import (
    SubstanceMappingRequest, SubstanceMappingBatchRequest,
    SubstanceMappingResponse, SubstanceMappingBatchResponse,
    SubstanceMappingFileResponse, SubstanceMappingStatistics
)

logger = logging.getLogger("normal-router")

# DI 함수들
def get_normal_service() -> NormalService:
    """Normal Service 인스턴스 생성"""
    return NormalService()

def get_normal_controller(service: NormalService = Depends(get_normal_service)) -> NormalController:
    """Normal Controller 인스턴스 생성"""
    return NormalController(service)

def get_substance_mapping_service() -> NormalService:
    """Substance Mapping Service 인스턴스 생성"""
    return NormalService()

# 라우터 생성
normal_router = APIRouter(prefix="/normal", tags=["normal"])

@normal_router.get("/health", summary="서비스 상태 확인")
async def health_check():
    """서비스 상태 확인 엔드포인트"""
    return {
        "status": "healthy",
        "service": "normal-service",
        "timestamp": datetime.now().isoformat(),
        "message": "Normal service is running"
    }

@normal_router.get("/ai/health", summary="AI 모델 상태 확인")
async def ai_model_health_check(
    controller: NormalController = Depends(get_normal_controller)
):
    """AI 모델 (BOMI AI) 상태 확인 엔드포인트"""
    return controller.check_ai_model_health()

@normal_router.get("/ai/model-info", summary="AI 모델 정보 조회")
async def get_ai_model_info(
    controller: NormalController = Depends(get_normal_controller)
):
    """AI 모델 상세 정보 조회"""
    return controller.get_ai_model_info()

@normal_router.post("/ai/test-mapping", summary="AI 모델 매핑 테스트")
async def test_ai_mapping(
    request: dict,
    controller: NormalController = Depends(get_normal_controller)
):
    """AI 모델 매핑 기능 테스트"""
    substance_name = request.get("substance_name")
    if not substance_name:
        raise HTTPException(status_code=400, detail="substance_name is required")
    
    return controller.test_ai_mapping(substance_name)

@normal_router.get("/", summary="모든 정규화 데이터 조회")
async def get_all_normalized_data(
    controller: NormalController = Depends(get_normal_controller)
):
    """모든 정규화 데이터 조회"""
    return controller.get_all_normalized_data()

@normal_router.get("/{data_id}", summary="특정 정규화 데이터 조회")
async def get_normalized_data_by_id(
    data_id: str,
    controller: NormalController = Depends(get_normal_controller)
):
    """특정 정규화 데이터 조회"""
    return controller.get_normalized_data_by_id(data_id)

@normal_router.post("/upload", summary="엑셀 파일 업로드 및 정규화")
async def upload_excel_file(
    file: UploadFile = File(...),
    company_id: str = None,
    company_name: str = None,
    uploaded_by: str = None,
    uploaded_by_email: str = None,
    controller: NormalController = Depends(get_normal_controller)
):
    """엑셀 파일 업로드 및 데이터 정규화 (새로운 구조)"""
    try:
        result = controller.upload_and_normalize_excel(file)
        return result
    except Exception as e:
        logger.error(f"파일 업로드 실패: {e}")
        raise HTTPException(status_code=500, detail=f"파일 업로드 중 오류가 발생했습니다: {str(e)}")

@normal_router.post("/substance-data", summary="프론트엔드 물질 데이터 처리")
async def process_substance_data(
    substance_data: dict,
    company_id: str = None,
    company_name: str = None,
    uploaded_by: str = None,
    service: NormalService = Depends(get_normal_service)
):
    """프론트엔드에서 받은 물질 데이터 저장 및 온실가스 AI 매핑"""
    try:
        result = service.save_substance_data_and_map_gases(
            substance_data=substance_data,
            company_id=company_id,
            company_name=company_name,
            uploaded_by=uploaded_by
        )
        
        if result.get('status') == 'error':
            raise HTTPException(status_code=500, detail=result.get('message', '처리 실패'))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"물질 데이터 처리 실패: {e}")
        raise HTTPException(status_code=500, detail=f"물질 데이터 처리 중 오류가 발생했습니다: {str(e)}")

@normal_router.post("/", summary="새로운 정규화 데이터 생성")
async def create_normalized_data(
    data: dict,
    controller: NormalController = Depends(get_normal_controller)
):
    """새로운 정규화 데이터 생성"""
    return controller.create_normalized_data(data)

@normal_router.put("/{data_id}", summary="정규화 데이터 업데이트")
async def update_normalized_data(
    data_id: str,
    data: dict,
    controller: NormalController = Depends(get_normal_controller)
):
    """정규화 데이터 업데이트"""
    return controller.update_normalized_data(data_id, data)

@normal_router.delete("/{data_id}", summary="정규화 데이터 삭제")
async def delete_normalized_data(
    data_id: str,
    controller: NormalController = Depends(get_normal_controller)
):
    """정규화 데이터 삭제"""
    return controller.delete_normalized_data(data_id)

@normal_router.get("/metrics", summary="서비스 메트릭 조회")
async def get_metrics(
    controller: NormalController = Depends(get_normal_controller)
):
    """서비스 메트릭 조회"""
    return controller.get_metrics()

# ===== 협력사 ESG 데이터 업로드 전용 API =====

@normal_router.post("/partner/upload", summary="협력사 ESG 데이터 파일 업로드")
async def upload_partner_esg_data(
    file: UploadFile = File(...),
    company_id: str = None,
    controller: NormalController = Depends(get_normal_controller)
):
    """협력사 ESG 데이터 파일 업로드 및 검증"""
    return controller.upload_partner_esg_data(file, company_id)

@normal_router.post("/partner/validate", summary="협력사 ESG 데이터 검증")
async def validate_partner_esg_data(
    data: dict,
    controller: NormalController = Depends(get_normal_controller)
):
    """협력사 ESG 데이터 검증 및 표준화"""
    return controller.validate_partner_esg_data(data)

@normal_router.get("/partner/dashboard/{company_id}", summary="협력사 자가진단 대시보드")
async def get_partner_dashboard(
    company_id: str,
    controller: NormalController = Depends(get_normal_controller)
):
    """협력사 ESG 자가진단 대시보드 데이터 조회"""
    return controller.get_partner_dashboard(company_id)

@normal_router.post("/partner/report/generate", summary="협력사 ESG 보고서 생성")
async def generate_partner_report(
    report_type: str,
    company_id: str,
    controller: NormalController = Depends(get_normal_controller)
):
    """협력사 ESG 보고서 자동 생성"""
    return controller.generate_partner_report(report_type, company_id)

@normal_router.get("/partner/schema/{industry}", summary="업종별 ESG 스키마 조회")
async def get_esg_schema(
    industry: str,
    controller: NormalController = Depends(get_normal_controller)
):
    """업종별 ESG 데이터 스키마 조회"""
    return controller.get_esg_schema(industry)

@normal_router.get("/environmental/{company_name}", summary="회사별 환경 데이터 조회")
async def get_environmental_data(
    company_name: str,
    controller: NormalController = Depends(get_normal_controller)
):
    """회사별 실제 환경 데이터 조회 (DB 기반)"""
    return controller.get_environmental_data(company_name)

# ===== 물질 매핑 API =====

@normal_router.post("/substance/map", summary="단일 물질 매핑")
async def map_single_substance(
    request: SubstanceMappingRequest,
    service: NormalService = Depends(get_substance_mapping_service)
):
    """단일 물질명을 표준 물질 ID로 매핑"""
    try:
        # AI 매핑 수행
        result = service.map_substance(request.substance_name)
        
        return SubstanceMappingResponse(
            status="success",
            data=result,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"물질 매핑 실패: {e}")
        raise HTTPException(status_code=500, detail=f"매핑 처리 중 오류가 발생했습니다: {str(e)}")

@normal_router.post("/substance/map-batch", summary="배치 물질 매핑")
async def map_substances_batch(
    request: SubstanceMappingBatchRequest,
    service: NormalService = Depends(get_substance_mapping_service)
):
    """여러 물질명을 배치로 매핑"""
    try:
        # AI 배치 매핑 수행
        results = service.map_substances_batch(request.substance_names)
        
        return SubstanceMappingBatchResponse(
            status="success",
            data=results,
            total_count=len(results),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"배치 매핑 실패: {e}")
        raise HTTPException(status_code=500, detail=f"배치 매핑 처리 중 오류가 발생했습니다: {str(e)}")

@normal_router.post("/substance/map-file", summary="파일 기반 물질 매핑")
async def map_substances_from_file(
    file: UploadFile = File(...),
    service: NormalService = Depends(get_substance_mapping_service)
):
    """업로드된 파일에서 물질명을 추출하여 매핑"""
    try:
        # 임시 파일로 저장
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # 매핑 수행
        result = service.map_file(temp_file_path)
        
        # 임시 파일 삭제
        os.unlink(temp_file_path)
        
        return SubstanceMappingFileResponse(
            status="success",
            data=result,
            original_filename=file.filename,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"파일 매핑 실패: {e}")
        raise HTTPException(status_code=500, detail=f"파일 매핑 처리 중 오류가 발생했습니다: {str(e)}")

@normal_router.get("/substance/status", summary="매핑 서비스 상태 확인")
async def get_substance_mapping_status(
    service: NormalService = Depends(get_substance_mapping_service)
):
    """물질 매핑 서비스 상태 및 통계 조회"""
    try:
        stats = service.get_substance_mapping_statistics()
        return stats  # 직접 dict 반환 (Pydantic 모델 검증 제거)
    except Exception as e:
        logger.error(f"매핑 서비스 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"서비스 상태 조회 중 오류가 발생했습니다: {str(e)}")

@normal_router.get("/substance/mappings", summary="저장된 매핑 결과 조회")
async def get_saved_mappings(
    company_id: str = None,
    limit: int = 10,
    service: NormalService = Depends(get_substance_mapping_service)
):
    """저장된 매핑 결과 조회"""
    try:
        mappings = service.get_saved_mappings(company_id, limit)
        return {
            "status": "success",
            "data": mappings,
            "total_count": len(mappings),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"매핑 결과 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"매핑 결과 조회 중 오류가 발생했습니다: {str(e)}")

@normal_router.get("/substance/original-data", summary="원본 데이터 조회")
async def get_original_data(
    company_id: str = None,
    limit: int = 10,
    service: NormalService = Depends(get_substance_mapping_service)
):
    """원본 데이터 조회"""
    try:
        data = service.get_original_data(company_id, limit)
        return {
            "status": "success",
            "data": data,
            "total_count": len(data),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"원본 데이터 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"원본 데이터 조회 중 오류가 발생했습니다: {str(e)}")

@normal_router.get("/substance/corrections", summary="사용자 수정 데이터 조회")
async def get_corrections(
    company_id: str = None,
    limit: int = 10,
    service: NormalService = Depends(get_substance_mapping_service)
):
    """사용자 수정 데이터 조회"""
    try:
        corrections = service.get_corrections(company_id, limit)
        return {
            "status": "success",
            "data": corrections,
            "total_count": len(corrections),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"수정 데이터 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"수정 데이터 조회 중 오류가 발생했습니다: {str(e)}")

@normal_router.post("/substance/correct/{certification_id}", summary="매핑 결과 수동 수정")
async def correct_substance_mapping(
    certification_id: int,
    correction_data: dict,
    service: NormalService = Depends(get_substance_mapping_service)
):
    """매핑 결과를 수동으로 수정 (certification 테이블 업데이트)"""
    try:
        # 매핑 수정 수행
        success = service.correct_mapping(certification_id, correction_data)
        
        if success:
            return {"status": "success", "message": "매핑 결과가 수정되었습니다."}
        else:
            raise HTTPException(status_code=400, detail="매핑 결과 수정에 실패했습니다.")
    except Exception as e:
        logger.error(f"매핑 결과 수정 실패: {e}")
        raise HTTPException(status_code=500, detail=f"매핑 결과 수정 중 오류가 발생했습니다: {str(e)}")