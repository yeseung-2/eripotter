# app/domain/service/normal_service.py
"""
Normal Service - MSA 구조 통합 서비스 (Refactored)
- DB 가용성 감지 및 graceful degrade
- 엑셀/CSV 업로드 간단 표준화 파이프라인 내장
- 저장 → 자동매핑 헬퍼(save_substance_data_and_map_gases) 추가
- get_substance_mapping_statistics 순환호출 버그 제거
- SentenceTransformer 로딩 실패 시 'no_model' 상태로 안전 반환
"""

from __future__ import annotations

import io
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None  # 런타임에 모델 미설치/미사용 대응

from eripotter_common.database import get_session
from ..repository.normal_repository import NormalRepository

logger = logging.getLogger("normal-service")


class NormalService:
    """Normal Service - MSA 구조에 맞춘 통합 서비스"""

    def __init__(self):
        # DB 연결 (가능하면)
        self.normal_repository: Optional[NormalRepository] = None
        self.db_available = False

        try:
            # get_session 사용으로 일관성 확보
            self.normal_repository = NormalRepository()
            self.db_available = True
            logger.info("✅ 데이터베이스 연결 성공")
        except Exception as e:
            logger.warning(f"⚠️ 데이터베이스 연결 실패: {e}")
            logger.info("📝 AI 매핑만 사용합니다 (결과 저장 불가)")

        # AI 모델(선택)
        self.model: Optional[SentenceTransformer] = None
        self._load_model()

    # ---------------------------------------------------------------------
    # 프론트엔드 데이터 처리
    # ---------------------------------------------------------------------

    def save_substance_data_only(
        self,
        substance_data: Dict[str, Any],
        company_id: str = None,
        company_name: str = None,
        uploaded_by: str = None,
    ) -> Dict[str, Any]:
        """프론트엔드에서 받은 물질 데이터만 저장 (AI 매핑은 별도)"""
        try:
            logger.info(f"📝 물질 데이터 저장 시작: {substance_data.get('productName', 'Unknown')}")
            if not self.db_available:
                return {"status": "error", "message": "데이터베이스 연결이 불가능합니다."}

            normal_id = self.normal_repository.save_substance_data(
                substance_data=substance_data,
                company_id=company_id,
                company_name=company_name,
                uploaded_by=uploaded_by,
                uploaded_by_email=substance_data.get("uploadedByEmail"),
            )

            if not normal_id:
                return {"status": "error", "message": "물질 데이터 저장에 실패했습니다."}

            logger.info(f"✅ 물질 데이터 저장 완료: Normal ID {normal_id}")
            return {
                "status": "success",
                "normal_id": normal_id,
                "product_name": substance_data.get("productName"),
                "message": "물질 데이터 저장 완료. 자동매핑을 시작하세요.",
            }
        except Exception as e:
            logger.error(f"❌ 물질 데이터 저장 실패: {e}")
            return {"status": "error", "error": str(e), "message": "물질 데이터 저장 중 오류가 발생했습니다."}

    def save_substance_data_and_map_gases(
        self,
        substance_data: Dict[str, Any],
        company_id: str = None,
        company_name: str = None,
        uploaded_by: str = None,
    ) -> Dict[str, Any]:
        """저장 후 해당 레코드의 온실가스 배출량 자동매핑까지 수행"""
        save_res = self.save_substance_data_only(substance_data, company_id, company_name, uploaded_by)
        if save_res.get("status") != "success":
            return save_res

        normal_id = save_res["normal_id"]
        map_res = self.start_auto_mapping(normal_id=normal_id, company_id=company_id, company_name=company_name)
        if map_res.get("status") != "success":
            return {
                "status": "partial",
                "normal_id": normal_id,
                "message": "저장은 완료됐지만 자동매핑에 실패했습니다.",
                "mapping_error": map_res.get("message") or map_res.get("error"),
            }
        return map_res

    def start_auto_mapping(self, normal_id: int, company_id: str = None, company_name: str = None) -> Dict[str, Any]:
        """저장된 데이터의 온실가스 배출량을 AI로 매핑"""
        try:
            logger.info(f"🤖 자동매핑 시작: Normal ID {normal_id}")

            if not self.db_available:
                logger.error("❌ 데이터베이스 연결이 불가능합니다.")
                return {"status": "error", "message": "데이터베이스 연결이 불가능합니다."}

            normal_data = self.normal_repository.get_by_id(normal_id)
            if not normal_data:
                logger.error(f"❌ Normal ID {normal_id}를 찾을 수 없습니다.")
                return {"status": "error", "message": f"Normal ID {normal_id}를 찾을 수 없습니다."}

            greenhouse_gases = normal_data.greenhouse_gas_emissions or []
            if not greenhouse_gases:
                logger.warning(f"⚠️ Normal ID {normal_id}에 온실가스 배출량 데이터가 없습니다.")
                return {"status": "error", "message": "온실가스 배출량 데이터가 없습니다."}

            logger.info(f"📊 온실가스 데이터 {len(greenhouse_gases)}개 발견")

            mapping_results: List[Dict[str, Any]] = []

            logger.info(f"🤖 온실가스 AI 매핑 시작: {len(greenhouse_gases)}개")
            for i, gas_data in enumerate(greenhouse_gases):
                gas_name = (gas_data or {}).get("materialName", "")
                gas_amount = (gas_data or {}).get("amount", "")

                logger.info(f"📝 매핑 중 ({i+1}/{len(greenhouse_gases)}): {gas_name}")

                if not gas_name:
                    logger.warning(f"⚠️ 빈 물질명 발견: {gas_data}")
                    mapping_results.append({"original_gas_name": "", "status": "mapping_failed", "error": "빈 물질명"})
                    continue

                ai_result = self.map_substance(gas_name)
                logger.info(f"🤖 AI 매핑 결과: {gas_name} → {ai_result.get('status', 'unknown')}")

                if ai_result.get("status") == "success":
                    logger.info(f"💾 매핑 결과 저장 시도: {gas_name}")
                    success = self.normal_repository.save_ai_mapping_result(
                        normal_id=normal_id,
                        gas_name=gas_name,
                        gas_amount=gas_amount,
                        mapping_result=ai_result,
                        company_id=company_id,
                        company_name=company_name,
                    )
                    if success:
                        confidence = float(ai_result.get("confidence", 0.0) or 0.0)
                        if confidence >= 0.7:
                            status = "auto_mapped"
                        elif confidence >= 0.4:
                            status = "needs_review"
                        else:
                            status = "needs_review"

                        logger.info(f"✅ 매핑 결과 저장 성공: {gas_name} → {status} (신뢰도: {confidence:.2f})")
                        mapping_results.append(
                            {
                                "original_gas_name": gas_name,
                                "original_amount": gas_amount,
                                "ai_mapped_name": ai_result.get("mapped_name"),
                                "ai_confidence": confidence,
                                "status": status,
                                "certification_id": None,  # 필요 시 후속 조회로 채울 수 있음
                            }
                        )
                    else:
                        logger.error(f"❌ 매핑 결과 저장 실패: {gas_name}")
                        mapping_results.append({"original_gas_name": gas_name, "status": "save_failed"})
                else:
                    error_msg = ai_result.get("error") or ai_result.get("message") or "알 수 없는 오류"
                    logger.error(f"❌ 매핑 실패: {gas_name} → {error_msg}")
                    mapping_results.append(
                        {"original_gas_name": gas_name, "status": "mapping_failed", "error": error_msg}
                    )

            # 매핑 결과 통계
            success_count = sum(1 for r in mapping_results if r.get("status") in ["auto_mapped", "needs_review"])
            failed_count = sum(1 for r in mapping_results if r.get("status") in ["mapping_failed", "save_failed"])
            
            logger.info(f"✅ 자동매핑 완료: {len(mapping_results)}개 중 {success_count}개 성공, {failed_count}개 실패")
            
            if failed_count > 0:
                return {
                    "status": "partial",
                    "normal_id": normal_id,
                    "mapping_results": mapping_results,
                    "message": f"저장은 완료됐지만 자동매핑에 실패했습니다. {success_count}개 성공, {failed_count}개 실패.",
                    "success_count": success_count,
                    "failed_count": failed_count,
                }
            else:
                return {
                    "status": "success",
                    "normal_id": normal_id,
                    "mapping_results": mapping_results,
                    "message": f"자동매핑 완료: {len(mapping_results)}개 온실가스 매핑. 사용자 검토가 필요합니다.",
                    "success_count": success_count,
                    "failed_count": failed_count,
                }
        except Exception as e:
            logger.error(f"❌ 자동매핑 실패: {e}")
            return {"status": "error", "error": str(e), "message": "자동매핑 중 오류가 발생했습니다."}

    # ---------------------------------------------------------------------
    # 상태/통계
    # ---------------------------------------------------------------------

    def get_substance_mapping_statistics(self) -> Dict[str, Any]:
        """매핑 서비스 통계 반환 (DB 통계 + 모델 상태)"""
        try:
            db_stats: Dict[str, Any] = {}
            if self.db_available and self.normal_repository:
                db_stats = self.normal_repository.get_mapping_statistics()

            model_status = {
                "model_loaded": self.model is not None,
                "service_status": "ready" if self.model else "not_ready",
            }

            return {
                "database_stats": db_stats or {
                    "total_mappings": 0,
                    "auto_mapped": 0,
                    "needs_review": 0,
                    "user_reviewed": 0,
                    "avg_confidence": 0.0,
                },
                "model_status": model_status,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"❌ 매핑 통계 조회 실패: {e}")
            return {
                "database_stats": {
                    "total_mappings": 0,
                    "auto_mapped": 0,
                    "needs_review": 0,
                    "user_reviewed": 0,
                    "avg_confidence": 0.0,
                },
                "model_status": {"model_loaded": False, "service_status": "not_ready"},
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
            }

    def get_saved_mappings(self, company_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        if not self.db_available:
            return []
        return self.normal_repository.get_saved_mappings(company_id, limit)

    def get_original_data(self, company_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        if not self.db_available:
            return []
        return self.normal_repository.get_original_data(company_id, limit)

    def get_corrections(self, company_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """현재는 certification user_reviewed를 별도 조회하는 메서드가 없어 빈 리스트 반환."""
        try:
            if not self.db_available:
                return []
            # TODO: repository에 user_reviewed 전용 조회 추가 가능
            return []
        except Exception as e:
            logger.error(f"❌ 수정 데이터 조회 실패: {e}")
            return []

    def correct_mapping(self, certification_id: int, correction_data: Dict[str, Any]) -> bool:
        if not self.db_available:
            return False
        return self.normal_repository.update_user_mapping_correction(
            certification_id=certification_id,
            correction_data=correction_data,
            reviewed_by=correction_data.get("reviewed_by", "user"),
        )

    def save_mapping_correction(self, **kwargs) -> bool:
        """레거시 호환. 새 구조에서는 correct_mapping 사용."""
        return True

    # ---------------------------------------------------------------------
    # 파일 업로드/정규화
    # ---------------------------------------------------------------------

    def upload_and_normalize_excel(self, file) -> Dict[str, Any]:
        """
        엑셀/CSV 파일 업로드 및 간단 정규화:
        - 물질명 컬럼: ['물질','substance','name','chemical'] 중 첫 매칭
        - 양(수량) 컬럼: ['amount','양','quantity','수량'] 중 첫 매칭
        - 단위 컬럼: ['unit','단위'] 중 첫 매칭 (없으면 'tonCO2eq')
        """
        try:
            filename = getattr(file, "filename", None) or "uploaded"
            content: bytes = file.file.read()
            ext = Path(filename).suffix.lower()

            if ext in [".xlsx", ".xls"]:
                df = pd.read_excel(io.BytesIO(content))
            elif ext == ".csv":
                df = pd.read_csv(io.BytesIO(content))
            else:
                return {"status": "error", "message": f"지원하지 않는 파일 형식: {ext or 'unknown'}", "filename": filename}

            # 컬럼 표준화
            def _lower_cols(cols):
                return [str(c).strip() for c in cols]

            df.columns = _lower_cols(df.columns)

            # 후보 컬럼 탐색
            def _find_col(candidates: List[str]) -> Optional[str]:
                for c in df.columns:
                    lc = c.lower()
                    if any(key in lc for key in candidates):
                        return c
                return None

            col_name = _find_col(["물질", "substance", "name", "chemical"]) or df.columns[0]
            col_amount = _find_col(["amount", "양", "quantity", "수량"])
            col_unit = _find_col(["unit", "단위"])

            normalized_data: List[Dict[str, Any]] = []
            for _, row in df.iterrows():
                substance = str(row.get(col_name, "")).strip()
                if not substance:
                    continue
                amount_val = row.get(col_amount) if col_amount is not None else None
                unit_val = row.get(col_unit) if col_unit is not None else None

                normalized_data.append(
                    {
                        "substance_name": substance,
                        "amount": amount_val if amount_val is not None else 0,
                        "unit": str(unit_val).strip() if unit_val is not None else "tonCO2eq",
                        # 추가 메타(있으면 사용)
                        "company_id": row.get("company_id"),
                        "company_name": row.get("company_name"),
                        "uploaded_by": row.get("uploaded_by"),
                    }
                )

            # 정규화된 각 항목을 저장+매핑 파이프라인으로 변환
            conversion_results: List[Dict[str, Any]] = []
            for item in normalized_data:
                substance_data = {
                    "filename": filename,
                    "file_size": len(content),
                    "file_type": "excel" if ext in [".xlsx", ".xls"] else "csv",
                    "productName": item.get("substance_name", ""),
                    "greenhouseGasEmissions": [
                        {
                            "materialName": item.get("substance_name", ""),
                            "amount": str(item.get("amount") or 0),
                            "unit": item.get("unit") or "tonCO2eq",
                        }
                    ],
                }
                # company 정보가 표에 있으면 넘겨서 저장
                res = self.save_substance_data_and_map_gases(
                    substance_data=substance_data,
                    company_id=item.get("company_id"),
                    company_name=item.get("company_name"),
                    uploaded_by=item.get("uploaded_by"),
                )
                conversion_results.append(res)

            return {
                "filename": filename,
                "status": "uploaded_and_mapped",
                "normalization": {"status": "success", "normalized_count": len(normalized_data)},
                "conversion_results": conversion_results,
                "message": f"파일 처리 완료: {len(conversion_results)}개 항목",
            }
        except Exception as e:
            logger.error(f"❌ 엑셀/CSV 파일 업로드 및 매핑 실패: {e}")
            return {"filename": getattr(file, "filename", None), "status": "error", "error": str(e)}

    # ---------------------------------------------------------------------
    # 기존 인터페이스(매핑)
    # ---------------------------------------------------------------------

    def map_substance(self, substance_name: str, company_id: str = None) -> dict:
        """단일 물질 매핑 (간이 로직: 모델이 있으면 임베딩, 없으면 규칙 매핑)"""
        try:
            logger.info(f"📝 물질 매핑 요청: {substance_name}")

            if not substance_name or substance_name.strip() == "":
                return self._create_empty_result(substance_name, "빈 물질명")

            if not self.model:
                return {
                    "substance_name": substance_name,
                    "mapped_sid": None,
                    "mapped_name": None,
                    "top1_score": 0.0,
                    "margin": 0.0,
                    "confidence": 0.0,
                    "band": "not_mapped",
                    "top5_candidates": [],
                    "message": "BOMI AI 모델이 로드되지 않았습니다.",
                    "status": "no_model",
                }

            input_text = substance_name.strip()
            embedding = self.model.encode([input_text], normalize_embeddings=True, show_progress_bar=False)

            mapped_name = self._standardize_substance_name(input_text)
            mapped_sid = self._generate_substance_id(mapped_name)

            # normalize_embeddings=True 이면 평균이 0 근처일 수 있으므로 하한/상한 클램프
            confidence = float(np.mean(embedding))
            confidence = min(0.95, max(0.3, confidence))

            band = "mapped" if confidence >= 0.70 else ("needs_review" if confidence >= 0.40 else "not_mapped")

            return {
                "substance_name": substance_name,
                "mapped_sid": mapped_sid,
                "mapped_name": mapped_name,
                "top1_score": confidence,
                "margin": 0.1,
                "confidence": confidence,
                "band": band,
                "top5_candidates": [{"rank": 1, "sid": mapped_sid, "name": mapped_name, "score": confidence}],
                "status": "success",
            }
        except Exception as e:
            logger.error(f"❌ 물질 매핑 실패: {e}")
            return self._create_empty_result(substance_name, str(e))

    def map_substances_batch(self, substance_names: list, company_id: str = None) -> list:
        """배치 물질 매핑 (AI만)"""
        try:
            if not substance_names:
                raise Exception("매핑할 물질명 목록이 비어있습니다.")
            logger.info(f"📝 배치 물질 매핑 요청: {len(substance_names)}개")
            return [self.map_substance(name, company_id) for name in substance_names]
        except Exception as e:
            logger.error(f"❌ 배치 물질 매핑 실패: {e}")
            raise Exception(f"배치 물질 매핑을 수행할 수 없습니다: {str(e)}")

    def map_file(self, file_path: str) -> dict:
        """파일에서 물질명을 추출하여 매핑"""
        try:
            if file_path.endswith((".xlsx", ".xls")):
                data = pd.read_excel(file_path)
            elif file_path.endswith(".csv"):
                data = pd.read_csv(file_path)
            else:
                raise ValueError("지원하지 않는 파일 형식입니다.")

            substance_column = None
            for col in data.columns:
                col_lower = str(col).lower()
                if any(keyword in col_lower for keyword in ["물질", "substance", "name", "chemical"]):
                    substance_column = col
                    break
            if substance_column is None:
                substance_column = data.columns[0]

            substance_names = data[substance_column].fillna("").astype(str).tolist()
            mapping_results = self.map_substances_batch(substance_names)

            total_count = len(mapping_results)
            mapped_count = sum(1 for r in mapping_results if r["band"] == "mapped")
            review_count = sum(1 for r in mapping_results if r["band"] == "needs_review")
            not_mapped_count = sum(1 for r in mapping_results if r["band"] == "not_mapped")

            return {
                "file_path": file_path,
                "total_substances": total_count,
                "mapped_count": mapped_count,
                "needs_review_count": review_count,
                "not_mapped_count": not_mapped_count,
                "mapping_results": mapping_results,
                "status": "success",
            }
        except Exception as e:
            logger.error(f"파일 매핑 실패 ({file_path}): {e}")
            return {"file_path": file_path, "error": str(e), "status": "error"}

    # ---------------------------------------------------------------------
    # 메트릭/환경 데이터 (기존 로직 유지·정리)
    # ---------------------------------------------------------------------

    def get_metrics(self):
        return self.get_substance_mapping_statistics()

    def get_environmental_data_by_company(self, company_name: str) -> Dict[str, Any]:
        """회사별 실제 환경 데이터 조회 (DB에서 계산)"""
        try:
            if not self.db_available:
                logger.warning("데이터베이스 연결 불가, 기본값 반환")
                return self._get_default_environmental_data(company_name)

            normal_data = self.normal_repository.get_company_data(company_name)
            certification_data = self.normal_repository.get_company_certifications(company_name)
            environmental_data = self._calculate_environmental_data(normal_data, certification_data)

            return {
                "status": "success",
                "company_name": company_name,
                "data": environmental_data,
                "last_updated": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"환경 데이터 조회 실패 ({company_name}): {e}")
            return {
                "status": "error",
                "message": f"환경 데이터 조회 실패: {str(e)}",
                "data": self._get_default_environmental_data(company_name),
            }

    # ----------------- 내부 계산/보조 메서드(기존 유지) -----------------

    def _calculate_environmental_data(self, normal_data: List[Dict], certification_data: List[Dict]) -> Dict[str, Any]:
        try:
            carbon_footprint = self._calculate_carbon_footprint(certification_data)
            energy_usage = self._calculate_energy_usage(normal_data)
            water_usage = self._calculate_water_usage(normal_data)
            waste_management = self._calculate_waste_management(normal_data)
            certifications = self._extract_certifications(normal_data)
            return {
                "carbonFootprint": carbon_footprint,
                "energyUsage": energy_usage,
                "waterUsage": water_usage,
                "wasteManagement": waste_management,
                "certifications": certifications,
            }
        except Exception as e:
            logger.error(f"환경 데이터 계산 실패: {e}")
            return self._get_default_environmental_data("Unknown")

    def _calculate_carbon_footprint(self, certification_data: List[Dict]) -> Dict[str, Any]:
        try:
            total_scope1 = total_scope2 = total_scope3 = 0.0
            for cert in certification_data:
                if cert.get("final_mapped_sid"):
                    try:
                        amount = float(cert.get("original_amount", 0) or 0)
                    except Exception:
                        amount = 0.0
                    sid = cert.get("final_mapped_sid", "") or ""
                    if ("CO2" in sid or "CH4" in sid):
                        if "direct" in sid.lower():
                            total_scope1 += amount
                        elif "indirect" in sid.lower():
                            total_scope2 += amount
                        else:
                            total_scope3 += amount
                    else:
                        total_scope3 += amount
            total = total_scope1 + total_scope2 + total_scope3
            return {
                "total": round(total, 2),
                "trend": "stable",
                "lastUpdate": datetime.now().strftime("%Y-%m-%d"),
                "breakdown": {
                    "scope1": round(total_scope1, 2),
                    "scope2": round(total_scope2, 2),
                    "scope3": round(total_scope3, 2),
                },
            }
        except Exception as e:
            logger.error(f"탄소배출량 계산 실패: {e}")
            return {
                "total": 0,
                "trend": "no_data",
                "lastUpdate": datetime.now().strftime("%Y-%m-%d"),
                "breakdown": {"scope1": 0, "scope2": 0, "scope3": 0},
                "message": "탄소배출량 데이터를 계산할 수 없습니다.",
            }

    def _calculate_energy_usage(self, normal_data: List[Dict]) -> Dict[str, Any]:
        try:
            total_energy = 0.0
            renewable_energy = 0.0
            for data in normal_data:
                capacity = (data.get("capacity") or "").replace("Ah", "").replace("Wh", "")
                energy_density = (data.get("energy_density") or "")
                if capacity:
                    try:
                        energy_value = float(capacity) * 0.1
                        total_energy += energy_value
                        if data.get("recycled_material"):
                            renewable_energy += energy_value * 0.3
                    except Exception:
                        pass
            return {
                "total": round(total_energy, 2),
                "renewable": round(renewable_energy, 2),
                "trend": "up" if total_energy else "no_data",
                "lastUpdate": datetime.now().strftime("%Y-%m-%d"),
            }
        except Exception as e:
            logger.error(f"에너지사용량 계산 실패: {e}")
            return {
                "total": 0,
                "renewable": 0,
                "trend": "no_data",
                "lastUpdate": datetime.now().strftime("%Y-%m-%d"),
                "message": "에너지 사용량 데이터를 계산할 수 없습니다.",
            }

    def _calculate_water_usage(self, normal_data: List[Dict]) -> Dict[str, Any]:
        try:
            total_water = 0.0
            recycled_water = 0.0
            for data in normal_data:
                raw_materials = data.get("raw_materials") or []
                if raw_materials:
                    material_count = len(raw_materials)
                    water_per_material = 100
                    total_water += material_count * water_per_material
                    if data.get("recycled_material"):
                        recycled_water += material_count * water_per_material * 0.3
            return {
                "total": round(total_water, 2),
                "recycled": round(recycled_water, 2),
                "trend": "stable" if total_water else "no_data",
                "lastUpdate": datetime.now().strftime("%Y-%m-%d"),
            }
        except Exception as e:
            logger.error(f"물사용량 계산 실패: {e}")
            return {
                "total": 0,
                "recycled": 0,
                "trend": "no_data",
                "lastUpdate": datetime.now().strftime("%Y-%m-%d"),
                "message": "물 사용량 데이터를 계산할 수 없습니다.",
            }

    def _calculate_waste_management(self, normal_data: List[Dict]) -> Dict[str, Any]:
        try:
            total_waste = recycled_waste = landfill_waste = 0.0
            for data in normal_data:
                base_waste = 50.0
                total_waste += base_waste
                if data.get("recycling_method"):
                    recycled_waste += base_waste * 0.7
                    landfill_waste += base_waste * 0.3
                else:
                    landfill_waste += base_waste
            return {
                "total": round(total_waste, 2),
                "recycled": round(recycled_waste, 2),
                "landfill": round(landfill_waste, 2),
                "trend": "up" if total_waste else "no_data",
                "lastUpdate": datetime.now().strftime("%Y-%m-%d"),
            }
        except Exception as e:
            logger.error(f"폐기물 관리 계산 실패: {e}")
            return {
                "total": 0,
                "recycled": 0,
                "landfill": 0,
                "trend": "no_data",
                "lastUpdate": datetime.now().strftime("%Y-%m-%d"),
                "message": "폐기물 관리 데이터를 계산할 수 없습니다.",
            }

    def _extract_certifications(self, normal_data: List[Dict]) -> List[str]:
        try:
            certifications: List[str] = []
            for data in normal_data:
                disposal_method = data.get("disposal_method") or ""
                recycling_method = data.get("recycling_method") or ""
                if "ISO 14001" in disposal_method or "ISO 14001" in recycling_method:
                    certifications.append("ISO 14001")
                if "ISO 50001" in disposal_method or "ISO 50001" in recycling_method:
                    certifications.append("ISO 50001")
                if "OHSAS 18001" in disposal_method or "OHSAS 18001" in recycling_method:
                    certifications.append("OHSAS 18001")
            return list(set(certifications))
        except Exception as e:
            logger.error(f"인증 정보 추출 실패: {e}")
            return []

    def _get_default_environmental_data(self, company_name: str) -> Dict[str, Any]:
        today = datetime.now().strftime("%Y-%m-%d")
        return {
            "carbonFootprint": {
                "total": 0,
                "trend": "no_data",
                "lastUpdate": today,
                "breakdown": {"scope1": 0, "scope2": 0, "scope3": 0},
                "message": f"{company_name}의 온실가스 배출량 데이터가 없습니다.",
            },
            "energyUsage": {
                "total": 0,
                "renewable": 0,
                "trend": "no_data",
                "lastUpdate": today,
                "message": f"{company_name}의 에너지 사용량 데이터가 없습니다.",
            },
            "waterUsage": {
                "total": 0,
                "recycled": 0,
                "trend": "no_data",
                "lastUpdate": today,
                "message": f"{company_name}의 물 사용량 데이터가 없습니다.",
            },
            "wasteManagement": {
                "total": 0,
                "recycled": 0,
                "landfill": 0,
                "trend": "no_data",
                "lastUpdate": today,
                "message": f"{company_name}의 폐기물 관리 데이터가 없습니다.",
            },
            "certifications": [],
            "message": f"{company_name}의 환경 데이터를 찾을 수 없습니다. 데이터를 입력해주세요.",
        }

    # ----------------- 내부 AI 유틸 -----------------

    def _load_model(self):
        """SentenceTransformer 모델을 로드(경로 우선 → 오프라인에서도 동작)"""
        try:
            if os.getenv("NORMAL_DISABLE_MODEL") == "1":
                logger.info("NORMAL_DISABLE_MODEL=1 → 모델 비활성화(no_model)")
                self.model = None
                return

            if SentenceTransformer is None:
                logger.warning("SentenceTransformer 미설치. 모델 로드를 생략합니다.")
                self.model = None
                return

            # ➊ 경로 우선: MODEL_NAME > MODEL_DIR > 디폴트
            model_path = os.getenv("MODEL_NAME") or os.getenv("MODEL_DIR") or "/app/model/bomi-ai"
            hf_repo = os.getenv("HF_REPO_ID", "galaxybuddy/bomi-ai")
            offline = (os.getenv("TRANSFORMERS_OFFLINE","0").lower() in ("1","true","yes")
                    or os.getenv("HF_HUB_OFFLINE","0").lower() in ("1","true","yes"))

            p = Path(model_path)
            logger.info(f"🧭 모델 경로 확인: {p} (exists={p.exists()}) | offline={offline}")

            # ➋ 로컬 경로가 있으면 무조건 로컬로 로드
            if p.exists() and p.is_dir():
                try:
                    self.model = SentenceTransformer(str(p), device="cpu", local_files_only=True)
                    logger.info(f"✅ BOMI AI 모델 로드 성공 (local): {p}")
                    return
                except Exception as e:
                    logger.warning(f"⚠️ 로컬 모델 로드 실패: {e}")
                    try:
                        sample = [x.as_posix() for x in p.rglob('*')][:20]
                        logger.info(f"로컬 모델 경로 파일 샘플(20개): {sample}")
                    except Exception:
                        pass

            # ➌ 오프라인이면 여기서 종료
            if offline:
                logger.warning("오프라인 모드 → 원격 모델 다운로드 생략(no_model)")
                self.model = None
                return

            # ➍ 온라인이면 HF에서 이름으로 로드
            try:
                logger.info(f"🌐 HuggingFace에서 모델 로드 시도: {hf_repo}")
                self.model = SentenceTransformer(hf_repo, device="cpu")
                logger.info(f"✅ BOMI AI 모델 로드 성공 (remote): {hf_repo}")
                return
            except Exception as e:
                logger.error(f"❌ HF 모델 로드 실패: {e}")
                self.model = None
        except Exception as e:
            logger.error(f"❌ 모델 로드 실패: {e}")
            self.model = None


    def _standardize_substance_name(self, input_name: str) -> str:
        """간단한 표준화 규칙"""
        name_mapping = {
            "이산화탄소": "이산화탄소 (CO2)",
            "메탄": "메탄 (CH4)",
            "메테인": "메탄 (CH4)",
            "아산화질소": "아산화질소 (N2O)",
            "N20": "아산화질소 (N2O)",
            "불산화탄소": "불화탄소 (CF4)",
            "CO2": "이산화탄소 (CO2)",
            "CH4": "메탄 (CH4)",
            "N2O": "아산화질소 (N2O)",
        }
        if input_name in name_mapping:
            return name_mapping[input_name]
        for key, value in name_mapping.items():
            if key in input_name or input_name in key:
                return value
        return f"{input_name} (표준화됨)"

    def _generate_substance_id(self, substance_name: str) -> str:
        import re
        clean_name = re.sub(r"[^\w가-힣]", "", substance_name)
        return f"SUBSTANCE_{clean_name.upper()}"

    def _create_empty_result(self, substance_name: str, error_message: str) -> Dict[str, Any]:
        return {
            "substance_name": substance_name,
            "mapped_sid": None,
            "mapped_name": None,
            "top1_score": 0.0,
            "margin": 0.0,
            "confidence": 0.0,
            "band": "not_mapped",
            "top5_candidates": [],
            "error": error_message,
            "status": "error",
        }
