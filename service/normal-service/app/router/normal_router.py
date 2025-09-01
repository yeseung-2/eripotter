"""
Normal Router - API 엔드포인트 및 의존성 주입
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List, Optional
from datetime import datetime
import logging
import os

# Domain imports
from ..domain.service.normal_service import NormalService
from ..domain.controller.normal_controller import NormalController
from ..domain.model.normal_model import (
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

@normal_router.post("/substance-data", summary="프론트엔드 물질 데이터 저장")
async def save_substance_data(
    substance_data: dict,
    company_id: str = None,
    company_name: str = None,
    uploaded_by: str = None,
    service: NormalService = Depends(get_normal_service)
):
    """프론트엔드에서 받은 물질 데이터 저장 (AI 매핑은 별도)"""
    try:
        result = service.save_substance_data_only(
            substance_data=substance_data,
            company_id=company_id,
            company_name=company_name,
            uploaded_by=uploaded_by
        )
        
        if result.get('status') == 'error':
            raise HTTPException(status_code=500, detail=result.get('message', '저장 실패'))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"물질 데이터 저장 실패: {e}")
        raise HTTPException(status_code=500, detail=f"물질 데이터 저장 중 오류가 발생했습니다: {str(e)}")

@normal_router.post("/auto-mapping/{normal_id}", summary="자동매핑 시작")
async def start_auto_mapping(
    normal_id: int,
    company_id: str = None,
    company_name: str = None,
    service: NormalService = Depends(get_normal_service)
):
    """저장된 데이터의 온실가스 배출량을 AI로 자동 매핑"""
    try:
        result = service.start_auto_mapping(
            normal_id=normal_id,
            company_id=company_id,
            company_name=company_name
        )
        
        if result.get('status') == 'error':
            raise HTTPException(status_code=500, detail=result.get('message', '자동매핑 실패'))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"자동매핑 실패: {e}")
        raise HTTPException(status_code=500, detail=f"자동매핑 중 오류가 발생했습니다: {str(e)}")

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
        if not request.substance_name or not request.substance_name.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": "물질명이 제공되지 않았습니다.",
                    "timestamp": datetime.now().isoformat(),
                    "error_type": "invalid_request"
                }
            )
        
        # AI 매핑 수행
        result = service.map_substance(request.substance_name)
        
        return SubstanceMappingResponse(
            status="success",
            data=result,
            timestamp=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"물질 매핑 실패: {e}")
        raise HTTPException(
            status_code=500, 
            detail={
                "status": "error",
                "message": f"물질 매핑을 수행할 수 없습니다: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "error_type": "mapping_failed"
            }
        )

@normal_router.post("/substance/map-batch", summary="배치 물질 매핑")
async def map_substances_batch(
    request: SubstanceMappingBatchRequest,
    service: NormalService = Depends(get_substance_mapping_service)
):
    """여러 물질명을 배치로 매핑"""
    try:
        if not request.substance_names or len(request.substance_names) == 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": "매핑할 물질명 목록이 비어있습니다.",
                    "timestamp": datetime.now().isoformat(),
                    "error_type": "invalid_request"
                }
            )
        
        # AI 배치 매핑 수행
        results = service.map_substances_batch(request.substance_names)
        
        success_count = sum(1 for r in results if r.get('status') == 'success')
        error_count = len(results) - success_count
        
        return SubstanceMappingBatchResponse(
            status="success",
            data=results,
            total_count=len(results),
            success_count=success_count,
            error_count=error_count,
            timestamp=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"배치 매핑 실패: {e}")
        raise HTTPException(
            status_code=500, 
            detail={
                "status": "error",
                "message": f"배치 물질 매핑을 수행할 수 없습니다: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "error_type": "batch_mapping_failed"
            }
        )

@normal_router.post("/substance/map-file", summary="파일 기반 물질 매핑")
async def map_substances_from_file(
    file: UploadFile = File(...),
    service: NormalService = Depends(get_substance_mapping_service)
):
    """업로드된 파일에서 물질명을 추출하여 매핑"""
    try:
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": "파일명이 제공되지 않았습니다.",
                    "timestamp": datetime.now().isoformat(),
                    "error_type": "invalid_request"
                }
            )
        
        # 파일 확장자 검증
        allowed_extensions = ['.xlsx', '.xls', '.csv']
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": f"지원하지 않는 파일 형식입니다. 지원 형식: {', '.join(allowed_extensions)}",
                    "timestamp": datetime.now().isoformat(),
                    "error_type": "invalid_file_format"
                }
            )
        
        # 임시 파일로 저장
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # 매핑 수행
        result = service.map_file(temp_file_path)
        
        # 임시 파일 삭제
        os.unlink(temp_file_path)
        
        if result.get('status') == 'error':
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "error",
                    "message": f"파일 처리 중 오류가 발생했습니다: {result.get('error', '알 수 없는 오류')}",
                    "timestamp": datetime.now().isoformat(),
                    "error_type": "file_processing_failed"
                }
            )
        
        return SubstanceMappingFileResponse(
            status="success",
            data=result.get('mapping_results', []),
            original_filename=file.filename,
            processed_count=result.get('total_substances', 0),
            timestamp=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"파일 매핑 실패: {e}")
        raise HTTPException(
            status_code=500, 
            detail={
                "status": "error",
                "message": f"파일 매핑을 수행할 수 없습니다: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "error_type": "file_mapping_failed"
            }
        )

@normal_router.get("/substance/status", summary="매핑 서비스 상태 확인")
async def get_substance_mapping_status(
    service: NormalService = Depends(get_substance_mapping_service)
):
    """물질 매핑 서비스 상태 및 통계 조회"""
    try:
        stats = service.get_substance_mapping_statistics()
        return {
            "status": "success",
            "data": stats,
            "timestamp": datetime.now().isoformat(),
            "message": "매핑 서비스 상태 조회 완료"
        }
    except Exception as e:
        logger.error(f"매핑 서비스 상태 조회 실패: {e}")
        raise HTTPException(
            status_code=500, 
            detail={
                "status": "error",
                "message": f"매핑 서비스 상태를 조회할 수 없습니다: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "error_type": "service_unavailable"
            }
        )

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
            "timestamp": datetime.now().isoformat(),
            "message": f"매핑 결과 {len(mappings)}개 조회 완료"
        }
    except Exception as e:
        logger.error(f"매핑 결과 조회 실패: {e}")
        raise HTTPException(
            status_code=500, 
            detail={
                "status": "error",
                "message": f"저장된 매핑 결과를 조회할 수 없습니다: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "error_type": "data_retrieval_failed"
            }
        )

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
            "timestamp": datetime.now().isoformat(),
            "message": f"원본 데이터 {len(data)}개 조회 완료"
        }
    except Exception as e:
        logger.error(f"원본 데이터 조회 실패: {e}")
        raise HTTPException(
            status_code=500, 
            detail={
                "status": "error",
                "message": f"원본 데이터를 조회할 수 없습니다: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "error_type": "data_retrieval_failed"
            }
        )

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
            "timestamp": datetime.now().isoformat(),
            "message": f"사용자 수정 데이터 {len(corrections)}개 조회 완료"
        }
    except Exception as e:
        logger.error(f"수정 데이터 조회 실패: {e}")
        raise HTTPException(
            status_code=500, 
            detail={
                "status": "error",
                "message": f"사용자 수정 데이터를 조회할 수 없습니다: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "error_type": "data_retrieval_failed"
            }
        )

@normal_router.post("/substance/correct/{certification_id}", summary="매핑 결과 수동 수정")
async def correct_substance_mapping(
    certification_id: int,
    correction_data: dict,
    service: NormalService = Depends(get_substance_mapping_service)
):
    """매핑 결과를 수동으로 수정 (certification 테이블 업데이트)"""
    try:
        if not correction_data:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": "수정할 데이터가 제공되지 않았습니다.",
                    "timestamp": datetime.now().isoformat(),
                    "error_type": "invalid_request"
                }
            )
        
        # 매핑 수정 수행
        success = service.correct_mapping(certification_id, correction_data)
        
        return {
            "status": "success", 
            "message": f"매핑 결과 (ID: {certification_id})가 성공적으로 수정되었습니다.",
            "timestamp": datetime.now().isoformat(),
            "data": {"certification_id": certification_id, "updated": True}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"매핑 결과 수정 실패: {e}")
        raise HTTPException(
            status_code=500, 
            detail={
                "status": "error",
                "message": f"매핑 결과를 수정할 수 없습니다: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "error_type": "update_failed"
            }
        )
