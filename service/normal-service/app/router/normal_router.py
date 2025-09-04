# app/router/normal_router.py
"""
Normal Router - API 엔드포인트 및 의존성 주입 (Refactored)
- NormalService 싱글톤 주입: 모델/DB 초기화를 매 요청마다 반복하지 않음
- 매핑 응답을 Pydantic 모델에 맞게 변환하는 어댑터 추가
- 파일 확장자/크기·예외 처리 보강
"""

from __future__ import annotations

import logging
import os
import tempfile
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

# Domain imports
from ..domain.service.normal_service import NormalService
from ..domain.controller.normal_controller import NormalController
from ..domain.model.normal_model import (
    SubstanceMappingRequest,
    SubstanceMappingBatchRequest,
    SubstanceMappingResponse,
    SubstanceMappingBatchResponse,
    SubstanceMappingFileResponse,
    SubstanceMappingResult,
)

logger = logging.getLogger("normal-router")

# ---------- DI: 서비스/컨트롤러 싱글톤 ----------
_service_singleton = NormalService()
_controller_singleton = NormalController(_service_singleton)


def get_normal_service() -> NormalService:
    return _service_singleton


def get_normal_controller() -> NormalController:
    return _controller_singleton


# 라우터 생성
normal_router = APIRouter(prefix="/api/normal", tags=["normal"])

# ---------- 어댑터: 서비스 결과 → Pydantic 모델 ----------
def _to_mapping_result(data: Dict[str, Any]) -> SubstanceMappingResult:
    return SubstanceMappingResult(
        original_name=data.get("substance_name"),
        mapped_id=data.get("mapped_sid"),
        mapped_name=data.get("mapped_name"),
        confidence=float(data.get("confidence", 0.0) or 0.0),
        status=data.get("status") or data.get("band") or "unknown",
        error_message=data.get("error"),
    )


# ---------- Health ----------
@normal_router.get("/health", summary="서비스 상태 확인")
async def health_check(service: NormalService = Depends(get_normal_service)):
    return {
        "status": "healthy",
        "service": "normal-service",
        "timestamp": datetime.now().isoformat(),
        "message": "Normal service is running",
        "db_available": service.db_available,
        "repository_available": service.normal_repository is not None,
    }


# ---------- Normal CRUD ----------
@normal_router.get("/", summary="모든 정규화 데이터 조회")
async def get_all_normalized_data(controller: NormalController = Depends(get_normal_controller)):
    return controller.get_all_normalized_data()


@normal_router.get("/{data_id}", summary="특정 정규화 데이터 조회")
async def get_normalized_data_by_id(data_id: str, controller: NormalController = Depends(get_normal_controller)):
    return controller.get_normalized_data_by_id(data_id)


@normal_router.post("/upload", summary="엑셀/CSV 파일 업로드 및 정규화")
async def upload_excel_file(
    file: UploadFile = File(...),
    company_id: Optional[str] = None,
    company_name: Optional[str] = None,
    uploaded_by: Optional[str] = None,
    uploaded_by_email: Optional[str] = None,
    controller: NormalController = Depends(get_normal_controller),
):
    try:
        # 현재 controller.upload_and_normalize_excel은 service로 위임
        # company_id 등은 엑셀 표에 들어있는 경우 service에서 활용
        result = controller.upload_and_normalize_excel(file)
        return result
    except Exception as e:
        logger.error(f"파일 업로드 실패: {e}")
        raise HTTPException(status_code=500, detail=f"파일 업로드 중 오류가 발생했습니다: {str(e)}")


@normal_router.post("/", summary="새로운 정규화 데이터 생성")
async def create_normalized_data(data: dict, controller: NormalController = Depends(get_normal_controller)):
    return controller.create_normalized_data(data)


@normal_router.put("/{data_id}", summary="정규화 데이터 업데이트")
async def update_normalized_data(data_id: str, data: dict, controller: NormalController = Depends(get_normal_controller)):
    return controller.update_normalized_data(data_id, data)


@normal_router.delete("/{data_id}", summary="정규화 데이터 삭제")
async def delete_normalized_data(data_id: str, controller: NormalController = Depends(get_normal_controller)):
    return controller.delete_normalized_data(data_id)


@normal_router.get("/metrics", summary="서비스 메트릭 조회")
async def get_metrics(controller: NormalController = Depends(get_normal_controller)):
    return controller.get_metrics()


# ---------- 환경 데이터 ----------
@normal_router.get("/environmental/{company_name}", summary="회사별 환경 데이터 조회")
async def get_environmental_data(company_name: str, controller: NormalController = Depends(get_normal_controller)):
    return controller.get_environmental_data(company_name)


# ---------- 협력사 ESG (미구현 스텁 유지) ----------
@normal_router.post("/partner/upload", summary="협력사 ESG 데이터 파일 업로드")
async def upload_partner_esg_data(
    file: UploadFile = File(...), company_id: Optional[str] = None, controller: NormalController = Depends(get_normal_controller)
):
    return controller.upload_partner_esg_data(file, company_id)


@normal_router.post("/partner/validate", summary="협력사 ESG 데이터 검증")
async def validate_partner_esg_data(data: dict, controller: NormalController = Depends(get_normal_controller)):
    return controller.validate_partner_esg_data(data)


@normal_router.get("/partner/dashboard/{company_id}", summary="협력사 자가진단 대시보드")
async def get_partner_dashboard(company_id: str, controller: NormalController = Depends(get_normal_controller)):
    return controller.get_partner_dashboard(company_id)


@normal_router.post("/partner/report/generate", summary="협력사 ESG 보고서 생성")
async def generate_partner_report(report_type: str, company_id: str, controller: NormalController = Depends(get_normal_controller)):
    return controller.generate_partner_report(report_type, company_id)


@normal_router.get("/partner/schema/{industry}", summary="업종별 ESG 스키마 조회")
async def get_esg_schema(industry: str, controller: NormalController = Depends(get_normal_controller)):
    return controller.get_esg_schema(industry)


# ---------- 물질 매핑 ----------
@normal_router.post("/substance/map", summary="단일 물질 매핑")
async def map_single_substance(request: SubstanceMappingRequest, service: NormalService = Depends(get_normal_service)):
    try:
        if not request.substance_name or not request.substance_name.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": "물질명이 제공되지 않았습니다.",
                    "timestamp": datetime.now().isoformat(),
                    "error_type": "invalid_request",
                },
            )

        raw = service.map_substance(request.substance_name)
        # Pydantic 응답으로 매핑
        return SubstanceMappingResponse(
            status="success",
            data=_to_mapping_result(raw),
            timestamp=datetime.now().isoformat(),
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
                "error_type": "mapping_failed",
            },
        )


@normal_router.post("/substance/map-batch", summary="배치 물질 매핑")
async def map_substances_batch(request: SubstanceMappingBatchRequest, service: NormalService = Depends(get_normal_service)):
    try:
        if not request.substance_names:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": "매핑할 물질명 목록이 비어있습니다.",
                    "timestamp": datetime.now().isoformat(),
                    "error_type": "invalid_request",
                },
            )

        raws = service.map_substances_batch(request.substance_names)
        results = [_to_mapping_result(r) for r in raws]
        success_count = sum(1 for r in results if r.status == "success" or r.status == "mapped")
        error_count = len(results) - success_count

        return SubstanceMappingBatchResponse(
            status="success",
            data=results,
            total_count=len(results),
            success_count=success_count,
            error_count=error_count,
            timestamp=datetime.now().isoformat(),
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
                "error_type": "batch_mapping_failed",
            },
        )


@normal_router.post("/substance/map-file", summary="파일 기반 물질 매핑")
async def map_substances_from_file(file: UploadFile = File(...), service: NormalService = Depends(get_normal_service)):
    try:
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": "파일명이 제공되지 않았습니다.",
                    "timestamp": datetime.now().isoformat(),
                    "error_type": "invalid_request",
                },
            )

        allowed_extensions = [".xlsx", ".xls", ".csv"]
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": f"지원하지 않는 파일 형식입니다. 지원 형식: {', '.join(allowed_extensions)}",
                    "timestamp": datetime.now().isoformat(),
                    "error_type": "invalid_file_format",
                },
            )

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        result = service.map_file(temp_file_path)
        os.unlink(temp_file_path)

        if result.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "error",
                    "message": f"파일 처리 중 오류가 발생했습니다: {result.get('error', '알 수 없는 오류')}",
                    "timestamp": datetime.now().isoformat(),
                    "error_type": "file_processing_failed",
                },
            )

        # 파일 매핑 결과를 Pydantic 모델로 변환
        results = [_to_mapping_result(r) for r in result.get("mapping_results", [])]

        return SubstanceMappingFileResponse(
            status="success",
            data=results,
            original_filename=file.filename,
            processed_count=result.get("total_substances", 0),
            timestamp=datetime.now().isoformat(),
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
                "error_type": "file_mapping_failed",
            },
        )


@normal_router.get("/substance/status", summary="매핑 서비스 상태 확인")
async def get_substance_mapping_status(service: NormalService = Depends(get_normal_service)):
    try:
        stats = service.get_substance_mapping_statistics()
        return {
            "status": "success",
            "data": stats,
            "timestamp": datetime.now().isoformat(),
            "message": "매핑 서비스 상태 조회 완료",
        }
    except Exception as e:
        logger.error(f"매핑 서비스 상태 조회 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"매핑 서비스 상태를 조회할 수 없습니다: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "error_type": "service_unavailable",
            },
        )


@normal_router.get("/substance/mappings", summary="저장된 매핑 결과 조회")
async def get_saved_mappings(
    company_id: Optional[str] = None,
    limit: int = 10,
    service: NormalService = Depends(get_normal_service),
):
    try:
        mappings = service.get_saved_mappings(company_id, limit)
        return {
            "status": "success",
            "data": mappings,
            "total_count": len(mappings),
            "timestamp": datetime.now().isoformat(),
            "message": f"매핑 결과 {len(mappings)}개 조회 완료",
        }
    except Exception as e:
        logger.error(f"매핑 결과 조회 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"저장된 매핑 결과를 조회할 수 없습니다: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "error_type": "data_retrieval_failed",
            },
        )


@normal_router.get("/substance/original-data", summary="원본 데이터 조회")
async def get_original_data(
    company_id: Optional[str] = None,
    limit: int = 10,
    service: NormalService = Depends(get_normal_service),
):
    try:
        data = service.get_original_data(company_id, limit)
        return {
            "status": "success",
            "data": data,
            "total_count": len(data),
            "timestamp": datetime.now().isoformat(),
            "message": f"원본 데이터 {len(data)}개 조회 완료",
        }
    except Exception as e:
        logger.error(f"원본 데이터 조회 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"원본 데이터를 조회할 수 없습니다: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "error_type": "data_retrieval_failed",
            },
        )


@normal_router.get("/substance/corrections", summary="사용자 수정 데이터 조회")
async def get_corrections(
    company_id: Optional[str] = None,
    limit: int = 10,
    service: NormalService = Depends(get_normal_service),
):
    try:
        corrections = service.get_corrections(company_id, limit)
        return {
            "status": "success",
            "data": corrections,
            "total_count": len(corrections),
            "timestamp": datetime.now().isoformat(),
            "message": f"사용자 수정 데이터 {len(corrections)}개 조회 완료",
        }
    except Exception as e:
        logger.error(f"수정 데이터 조회 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"사용자 수정 데이터를 조회할 수 없습니다: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "error_type": "data_retrieval_failed",
            },
        )


@normal_router.post("/substance/correct/{certification_id}", summary="매핑 결과 수동 수정")
async def correct_substance_mapping(
    certification_id: int, correction_data: dict, service: NormalService = Depends(get_normal_service)
):
    try:
        if not correction_data:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": "수정할 데이터가 제공되지 않았습니다.",
                    "timestamp": datetime.now().isoformat(),
                    "error_type": "invalid_request",
                },
            )

        success = service.correct_mapping(certification_id, correction_data)
        return {
            "status": "success",
            "message": f"매핑 결과 (ID: {certification_id})가 성공적으로 수정되었습니다.",
            "timestamp": datetime.now().isoformat(),
            "data": {"certification_id": certification_id, "updated": bool(success)},
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
                "error_type": "update_failed",
            },
        )


# ---------- 프론트엔드 연동용 새로운 엔드포인트들 ----------

@normal_router.post("/substance/save-and-map", summary="데이터 저장 및 자동매핑 시작")
async def save_and_map_substance(
    data: dict,
    company_id: Optional[str] = None,
    company_name: Optional[str] = None,
    uploaded_by: Optional[str] = None,
    service: NormalService = Depends(get_normal_service),
):
    try:
        if not data:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": "요청 데이터가 제공되지 않았습니다.",
                    "timestamp": datetime.now().isoformat(),
                    "error_type": "invalid_request",
                },
            )

        # 요청 바디 유연화: 중첩/평평한 형태 모두 허용
        payload = data or {}
        substance = payload.get("substance_data") or payload  # ✅ 중첩/평평 둘 다 허용
        
        if not substance:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": "물질 데이터가 제공되지 않았습니다.",
                    "timestamp": datetime.now().isoformat(),
                    "error_type": "invalid_request",
                },
            )

        logger.info(f"📝 요청 바디 처리: substance_data={bool(payload.get('substance_data'))}, 직접={bool(payload != substance)}")
        logger.info(f"📝 최종 substance 데이터: {substance.get('productName', 'Unknown')}")

        result = service.save_substance_data_and_map_gases(
            substance_data=substance,
            company_id=company_id,
            company_name=company_name,
            uploaded_by=uploaded_by,
        )
        
        return {
            "status": result.get("status", "success"),
            "normal_id": result.get("normal_id"),
            "message": result.get("message", "데이터 저장 및 자동매핑이 완료되었습니다."),
            "timestamp": datetime.now().isoformat(),
            "data": result,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"데이터 저장 및 자동매핑 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"데이터 저장 및 자동매핑을 수행할 수 없습니다: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "error_type": "save_and_map_failed",
            },
        )


@normal_router.get("/substance/{normal_id}", summary="특정 normal 데이터 조회")
async def get_substance_by_id(
    normal_id: int,
    service: NormalService = Depends(get_normal_service),
):
    try:
        if not service.db_available or not service.normal_repository:
            raise HTTPException(
                status_code=503,
                detail={
                    "status": "error",
                    "message": "데이터베이스 연결이 불가능합니다.",
                    "timestamp": datetime.now().isoformat(),
                    "error_type": "database_unavailable",
                },
            )

        normal_data = service.normal_repository.get_by_id(normal_id)
        if not normal_data:
            raise HTTPException(
                status_code=404,
                detail={
                    "status": "error",
                    "message": f"Normal ID {normal_id}를 찾을 수 없습니다.",
                    "timestamp": datetime.now().isoformat(),
                    "error_type": "not_found",
                },
            )

        return {
            "status": "success",
            "data": {
                "id": normal_data.id,
                "product_name": normal_data.product_name,
                "supplier": normal_data.supplier,
                "manufacturing_date": normal_data.manufacturing_date,
                "greenhouse_gas_emissions": normal_data.greenhouse_gas_emissions or [],
            },
            "timestamp": datetime.now().isoformat(),
            "message": f"Normal ID {normal_id} 데이터 조회 완료",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Normal 데이터 조회 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"Normal 데이터를 조회할 수 없습니다: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "error_type": "data_retrieval_failed",
            },
        )


@normal_router.get("/substance/mapping-results/{normal_id}", summary="매핑 결과 조회")
async def get_mapping_results(
    normal_id: int,
    service: NormalService = Depends(get_normal_service),
):
    try:
        if not service.db_available or not service.normal_repository:
            raise HTTPException(
                status_code=503,
                detail={
                    "status": "error",
                    "message": "데이터베이스 연결이 불가능합니다.",
                    "timestamp": datetime.now().isoformat(),
                    "error_type": "database_unavailable",
                },
            )

        # Normal 데이터 존재 확인
        normal_data = service.normal_repository.get_by_id(normal_id)
        if not normal_data:
            raise HTTPException(
                status_code=404,
                detail={
                    "status": "error",
                    "message": f"Normal ID {normal_id}를 찾을 수 없습니다.",
                    "timestamp": datetime.now().isoformat(),
                    "error_type": "not_found",
                },
            )

        # 해당 normal_id의 매핑 결과 조회
        with service.normal_repository.Session() as session:
            from ..domain.entity import CertificationEntity
            
            certifications = session.query(CertificationEntity).filter(
                CertificationEntity.normal_id == normal_id
            ).all()
            
            mapping_results = []
            for cert in certifications:
                # 프론트엔드에서 기대하는 형식으로 변환
                mapping_results.append({
                    "original_gas_name": cert.original_gas_name or "",
                    "original_amount": cert.original_amount or "",
                    "ai_mapped_name": cert.ai_mapped_name or "",
                    "ai_confidence": float(cert.ai_confidence_score or 0.0),
                    "status": cert.mapping_status or "needs_review",
                    "certification_id": cert.id,
                    "error": None  # 오류가 있으면 여기에 추가
                })
        
        return {
            "status": "success",
            "data": mapping_results,
            "timestamp": datetime.now().isoformat(),
            "message": f"Normal ID {normal_id} 매핑 결과 {len(mapping_results)}개 조회 완료",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"매핑 결과 조회 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"매핑 결과를 조회할 수 없습니다: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "error_type": "data_retrieval_failed",
            },
        )


@normal_router.post("/substance/save-corrections", summary="수정사항 저장")
async def save_corrections(
    normal_id: int,
    corrections: List[dict],
    service: NormalService = Depends(get_normal_service),
):
    try:
        if not corrections:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": "수정할 데이터가 제공되지 않았습니다.",
                    "timestamp": datetime.now().isoformat(),
                    "error_type": "invalid_request",
                },
            )

        if not service.db_available or not service.normal_repository:
            raise HTTPException(
                status_code=503,
                detail={
                    "status": "error",
                    "message": "데이터베이스 연결이 불가능합니다.",
                    "timestamp": datetime.now().isoformat(),
                    "error_type": "database_unavailable",
                },
            )

        # 수정사항 저장 (실제 구현에 따라 수정 필요)
        success_count = 0
        for correction in corrections:
            certification_id = correction.get("certification_id")
            correction_data = correction.get("correction_data", {})
            reviewed_by = correction.get("reviewed_by", "user")
            
            if certification_id and correction_data:
                success = service.correct_mapping(certification_id, correction_data)
                if success:
                    success_count += 1

        return {
            "status": "success",
            "message": f"수정사항 {success_count}개가 성공적으로 저장되었습니다.",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "normal_id": normal_id,
                "total_corrections": len(corrections),
                "success_count": success_count,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"수정사항 저장 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"수정사항을 저장할 수 없습니다: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "error_type": "save_failed",
            },
        )
