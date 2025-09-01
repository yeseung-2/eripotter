# app/domain/repository/normal_repository.py
"""
Normal Repository - Normal 테이블 전용 Repository (Refactored)
- 세션 컨텍스트 일원화, 롤백/커밋/클로즈 안전
- SQLAlchemy 2.x 호환(Row → dict 변환 개선)
- 기존 인터페이스/반환값 유지
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, date

from sqlalchemy import text, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

# 공용 엔진(현 구조 유지)
from eripotter_common.database import engine

# Entity import (현재 패키지 __init__ 에서 export 된다고 가정)
from ..entity import NormalEntity, CertificationEntity

logger = logging.getLogger("normal-repository")


class NormalRepository:
    def __init__(self, _engine=None):
        # 현 구조 유지: 공용 engine 사용 (MSA 분리 전환은 서비스 레벨에서 조정)
        self.engine = _engine or engine
        # expire_on_commit=False: commit 후 객체 접근(to_dict) 안정화
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False, autoflush=False)

    # ===== CRUD (Normal) =====

    def create(self, substance_data: Dict[str, Any]) -> Optional[NormalEntity]:
        """새로운 Normal 데이터 생성"""
        try:
            with self.Session() as session:
                normal_entity = NormalEntity(**substance_data)
                session.add(normal_entity)
                session.commit()
                session.refresh(normal_entity)
                logger.info("✅ Normal 데이터 생성 완료: ID %s", normal_entity.id)
                return normal_entity
        except SQLAlchemyError as e:
            logger.error("❌ Normal 데이터 생성 실패: %s", e)
            return None

    def get_by_id(self, normal_id: int) -> Optional[NormalEntity]:
        """ID로 Normal 데이터 조회"""
        try:
            with self.Session() as session:
                return session.query(NormalEntity).filter_by(id=normal_id).first()
        except SQLAlchemyError as e:
            logger.error("❌ Normal 데이터 조회 실패 (ID: %s): %s", normal_id, e)
            return None

    def get_by_company(self, company_id: str, limit: int = 10, offset: int = 0) -> List[NormalEntity]:
        """회사별 Normal 데이터 조회"""
        try:
            with self.Session() as session:
                return (
                    session.query(NormalEntity)
                    .filter_by(company_id=company_id)
                    .order_by(NormalEntity.created_at.desc())
                    .limit(limit)
                    .offset(offset)
                    .all()
                )
        except SQLAlchemyError as e:
            logger.error("❌ 회사별 Normal 데이터 조회 실패 (company_id: %s): %s", company_id, e)
            return []

    def get_all(self, limit: int = 50, offset: int = 0) -> List[NormalEntity]:
        """모든 Normal 데이터 조회"""
        try:
            with self.Session() as session:
                return (
                    session.query(NormalEntity)
                    .order_by(NormalEntity.created_at.desc())
                    .limit(limit)
                    .offset(offset)
                    .all()
                )
        except SQLAlchemyError as e:
            logger.error("❌ 전체 Normal 데이터 조회 실패: %s", e)
            return []

    def update(self, normal_id: int, update_data: Dict[str, Any]) -> bool:
        """Normal 데이터 업데이트"""
        try:
            with self.Session() as session:
                normal_entity = session.query(NormalEntity).filter_by(id=normal_id).first()
                if not normal_entity:
                    logger.error("❌ Normal ID %s 를 찾을 수 없습니다.", normal_id)
                    return False

                for key, value in (update_data or {}).items():
                    if hasattr(normal_entity, key):
                        setattr(normal_entity, key, value)

                # DB 서버 타임스탬프를 쓰지만, 애플리케이션 레벨에서도 갱신 표시
                normal_entity.updated_at = datetime.now()
                session.commit()
                logger.info("✅ Normal 데이터 업데이트 완료: ID %s", normal_id)
                return True
        except SQLAlchemyError as e:
            logger.error("❌ Normal 데이터 업데이트 실패 (ID: %s): %s", normal_id, e)
            return False

    def delete(self, normal_id: int) -> bool:
        """Normal 데이터 삭제"""
        try:
            with self.Session() as session:
                normal_entity = session.query(NormalEntity).filter_by(id=normal_id).first()
                if not normal_entity:
                    logger.error("❌ Normal ID %s 를 찾을 수 없습니다.", normal_id)
                    return False

                session.delete(normal_entity)
                session.commit()
                logger.info("✅ Normal 데이터 삭제 완료: ID %s", normal_id)
                return True
        except SQLAlchemyError as e:
            logger.error("❌ Normal 데이터 삭제 실패 (ID: %s): %s", normal_id, e)
            return False

    def count_by_company(self, company_id: str) -> int:
        """회사별 데이터 개수 조회"""
        try:
            with self.Session() as session:
                return session.query(NormalEntity).filter_by(company_id=company_id).count()
        except SQLAlchemyError as e:
            logger.error("❌ 회사별 데이터 개수 조회 실패 (company_id: %s): %s", company_id, e)
            return 0

    # ===== Raw/Dict helpers (SQLAlchemy 2.x) =====

    def _rows_to_dicts(self, result) -> List[Dict[str, Any]]:
        """Result → List[dict] (SQLAlchemy 2.x 안전변환)"""
        try:
            # 2.x: use mappings() for dict-like rows
            return [dict(row) for row in result.mappings().all()]
        except Exception:
            # fallback for 1.4: row._mapping
            return [dict(row._mapping) for row in result.fetchall()]

    def _row_to_dict(self, row) -> Optional[Dict[str, Any]]:
        if not row:
            return None
        try:
            return dict(row)  # mappings() 사용 시 row는 이미 dict-like
        except Exception:
            return dict(row._mapping)

    def get_all_normalized_data(self) -> List[Dict[str, Any]]:
        """모든 정규화 데이터 조회 (raw SQL)"""
        try:
            if not self.engine:
                return []
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM normal ORDER BY created_at DESC"))
                return self._rows_to_dicts(result)
        except Exception as e:
            logger.error("정규화 데이터 조회 실패: %s", e)
            return []

    def get_normalized_data_by_id(self, data_id: str) -> Optional[Dict[str, Any]]:
        """특정 정규화 데이터 조회 (raw SQL)"""
        try:
            if not self.engine:
                return None
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM normal WHERE id = :data_id"), {"data_id": data_id})
                row = result.first()
                return self._row_to_dict(row)
        except Exception as e:
            logger.error("정규화 데이터 조회 실패 (ID: %s): %s", data_id, e)
            return None

    def get_company_data(self, company_name: str) -> List[Dict[str, Any]]:
        """회사별 데이터 조회 (raw SQL)"""
        try:
            if not self.engine:
                return []
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT * FROM normal WHERE company_name = :company_name ORDER BY created_at DESC"),
                    {"company_name": company_name},
                )
                return self._rows_to_dicts(result)
        except Exception as e:
            logger.error("회사 데이터 조회 실패 (%s): %s", company_name, e)
            return []

    # ===== Substance Mapping =====

    def save_substance_data(
        self,
        substance_data: Dict[str, Any],
        company_id: str = None,
        company_name: str = None,
        uploaded_by: str = None,
        uploaded_by_email: str = None,
    ) -> Optional[int]:
        """프론트엔드에서 받은 물질 데이터를 normal 테이블에 저장"""
        try:
            logger.info("🔍 Repository: 데이터 저장 시작 - %s", substance_data.get("productName", "Unknown"))
            logger.info("🔍 Repository: Company ID: %s, Company Name: %s", company_id, company_name)

            with self.Session() as session:
                normal_entity = NormalEntity(
                    company_id=company_id,
                    company_name=company_name,
                    uploaded_by=uploaded_by,
                    uploaded_by_email=uploaded_by_email,
                    # 파일 정보
                    filename=substance_data.get("filename"),
                    file_size=substance_data.get("file_size", 0),
                    file_type=substance_data.get("file_type", "manual"),  # 'manual' or 'excel'
                    # 제품 기본 정보
                    product_name=substance_data.get("productName"),
                    supplier=substance_data.get("supplier"),
                    manufacturing_date=self._parse_date(substance_data.get("manufacturingDate")),
                    manufacturing_number=substance_data.get("manufacturingNumber"),
                    safety_information=substance_data.get("safetyInformation"),
                    recycled_material=substance_data.get("recycledMaterial", False),
                    # 제품 스펙
                    capacity=substance_data.get("capacity"),
                    energy_density=substance_data.get("energyDensity"),
                    # 위치 정보
                    manufacturing_country=substance_data.get("manufacturingCountry"),
                    production_plant=substance_data.get("productionPlant"),
                    # 처리 방법
                    disposal_method=substance_data.get("disposalMethod"),
                    recycling_method=substance_data.get("recyclingMethod"),
                    # 원재료 정보 (JSON)
                    raw_materials=substance_data.get("rawMaterials", []),
                    raw_material_sources=substance_data.get("rawMaterialSources", []),
                    # 온실가스 배출량 (JSON)
                    greenhouse_gas_emissions=substance_data.get("greenhouseGasEmissions", []),
                    # 화학물질 구성
                    chemical_composition=substance_data.get("chemicalComposition"),
                )

                logger.info("🔍 Repository: NormalEntity 객체 생성 완료")
                session.add(normal_entity)
                session.commit()
                normal_id = normal_entity.id
                logger.info("✅ 물질 데이터 저장 완료: %s - %s (ID: %s)", company_name, substance_data.get("productName"), normal_id)
                return normal_id
        except SQLAlchemyError as e:
            logger.error("❌ 물질 데이터 저장 실패: %s", e)
            return None
        except Exception as e:
            logger.error("❌ 물질 데이터 저장 중 예상치 못한 오류: %s", e)
            return None

    def save_ai_mapping_result(
        self,
        normal_id: int,
        gas_name: str,
        gas_amount: str,
        mapping_result: Dict[str, Any],
        company_id: str = None,
        company_name: str = None,
    ) -> bool:
        """AI 매핑 결과를 certification 테이블에 저장"""
        try:
            with self.Session() as session:
                confidence = float(mapping_result.get("confidence", 0.0) or 0.0)
                if confidence >= 0.7:
                    mapping_status = "auto_mapped"
                elif confidence >= 0.4:
                    mapping_status = "needs_review"
                else:
                    mapping_status = "needs_review"

                certification_entity = CertificationEntity(
                    normal_id=normal_id,
                    company_id=company_id,
                    company_name=company_name,
                    # 온실가스 원본 정보
                    original_gas_name=gas_name,
                    original_amount=gas_amount,
                    # AI 매핑 결과
                    ai_mapped_sid=mapping_result.get("mapped_sid"),
                    ai_mapped_name=mapping_result.get("mapped_name"),
                    ai_confidence_score=confidence,
                    ai_cas_number=mapping_result.get("cas_number"),
                    # 초기 최종값 = AI 결과 (사용자 수정 가능)
                    final_mapped_sid=mapping_result.get("mapped_sid"),
                    final_mapped_name=mapping_result.get("mapped_name"),
                    final_cas_number=mapping_result.get("cas_number"),
                    final_standard_unit="tonCO2eq",
                    mapping_status=mapping_status,
                )

                session.add(certification_entity)
                session.commit()
                logger.info(
                    "✅ AI 매핑 결과 저장 완료: %s -> %s (신뢰도: %.1f%%)",
                    gas_name,
                    mapping_result.get("mapped_name"),
                    confidence * 100.0,
                )
                return True
        except SQLAlchemyError as e:
            logger.error("❌ AI 매핑 결과 저장 실패: %s", e)
            return False

    def update_user_mapping_correction(
        self,
        certification_id: int,
        correction_data: Dict[str, Any],
        reviewed_by: str = None,
    ) -> bool:
        """사용자가 매핑을 수정한 결과를 certification 테이블에 업데이트"""
        try:
            with self.Session() as session:
                certification = session.query(CertificationEntity).filter_by(id=certification_id).first()
                if not certification:
                    logger.error("❌ certification ID %s 를 찾을 수 없습니다.", certification_id)
                    return False

                certification.final_mapped_sid = correction_data.get("corrected_sid", certification.final_mapped_sid)
                certification.final_mapped_name = correction_data.get("corrected_name", certification.final_mapped_name)
                certification.final_cas_number = correction_data.get("corrected_cas_number", certification.final_cas_number)
                certification.final_standard_unit = correction_data.get("corrected_unit", certification.final_standard_unit)

                certification.mapping_status = "user_reviewed"
                certification.reviewed_by = reviewed_by
                certification.review_comment = correction_data.get("review_comment")
                certification.updated_at = datetime.now()

                session.commit()
                logger.info("✅ 사용자 매핑 수정 완료: ID %s - %s", certification_id, reviewed_by)
                return True
        except SQLAlchemyError as e:
            logger.error("❌ 사용자 매핑 수정 실패: %s", e)
            return False

    def get_saved_mappings(self, company_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """저장된 매핑 결과 조회"""
        try:
            with self.Session() as session:
                query = session.query(CertificationEntity).join(NormalEntity)
                if company_id:
                    query = query.filter(CertificationEntity.company_id == company_id)

                results = query.order_by(CertificationEntity.created_at.desc()).limit(limit).all()

                mappings: List[Dict[str, Any]] = []
                for cert in results:
                    mappings.append(
                        {
                            "id": cert.id,
                            "normal_id": cert.normal_id,
                            "company_id": cert.company_id,
                            "company_name": cert.company_name,
                            "original_gas_name": cert.original_gas_name,
                            "original_amount": cert.original_amount,
                            "ai_mapped_name": cert.ai_mapped_name,
                            "ai_confidence_score": cert.ai_confidence_score,
                            "final_mapped_name": cert.final_mapped_name,
                            "mapping_status": cert.mapping_status,
                            "created_at": cert.created_at.isoformat() if cert.created_at else None,
                        }
                    )

                logger.info("✅ 매핑 결과 조회 완료: %s개 (회사: %s)", len(mappings), company_id or "전체")
                return mappings
        except SQLAlchemyError as e:
            logger.error("❌ 매핑 결과 조회 실패 (회사: %s): %s", company_id or "전체", e)
            raise Exception(f"데이터베이스에서 매핑 결과를 조회하는 중 오류가 발생했습니다: {str(e)}")

    def get_original_data(self, company_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """원본 데이터 조회"""
        try:
            with self.Session() as session:
                query = session.query(NormalEntity)
                if company_id:
                    query = query.filter(NormalEntity.company_id == company_id)

                results = query.order_by(NormalEntity.created_at.desc()).limit(limit).all()
                data = [normal.to_dict() for normal in results]
                logger.info("✅ 원본 데이터 조회 완료: %s개 (회사: %s)", len(data), company_id or "전체")
                return data
        except SQLAlchemyError as e:
            logger.error("❌ 원본 데이터 조회 실패 (회사: %s): %s", company_id or "전체", e)
            raise Exception(f"데이터베이스에서 원본 데이터를 조회하는 중 오류가 발생했습니다: {str(e)}")

    def get_mapping_statistics(self) -> Dict[str, Any]:
        """매핑 통계 조회"""
        try:
            with self.Session() as session:
                total_mappings = session.query(CertificationEntity).count()
                auto_mapped = session.query(CertificationEntity).filter(CertificationEntity.mapping_status == "auto_mapped").count()
                needs_review = session.query(CertificationEntity).filter(CertificationEntity.mapping_status == "needs_review").count()
                user_reviewed = session.query(CertificationEntity).filter(CertificationEntity.mapping_status == "user_reviewed").count()

                avg_confidence_result = session.query(func.avg(CertificationEntity.ai_confidence_score)).filter(
                    CertificationEntity.ai_confidence_score.isnot(None)
                ).scalar()

                avg_confidence = float(avg_confidence_result) if avg_confidence_result else 0.0

                stats = {
                    "total_mappings": total_mappings,
                    "auto_mapped": auto_mapped,
                    "needs_review": needs_review,
                    "user_reviewed": user_reviewed,
                    "avg_confidence": avg_confidence,
                }

                logger.info("✅ 매핑 통계 조회 완료: 총 %s 개", total_mappings)
                return stats
        except SQLAlchemyError as e:
            logger.error("❌ 매핑 통계 조회 실패: %s", e)
            raise Exception(f"데이터베이스에서 매핑 통계를 조회하는 중 오류가 발생했습니다: {str(e)}")

    def get_company_products(self, company_name: str) -> List[Dict[str, Any]]:
        """회사별 제품 목록 조회 (product_name 기준)"""
        try:
            with self.Session() as session:
                query = text("""
                    SELECT DISTINCT 
                        product_name,
                        supplier,
                        manufacturing_date,
                        capacity,
                        recycled_material,
                        created_at,
                        updated_at
                    FROM normal 
                    WHERE company_name = :company_name 
                    AND product_name IS NOT NULL 
                    AND product_name != ''
                    ORDER BY created_at DESC
                """)
                
                result = session.execute(query, {"company_name": company_name})
                rows = result.fetchall()
                
                return [dict(row._mapping) for row in rows]
        except SQLAlchemyError as e:
            logger.error("❌ 회사별 제품 목록 조회 실패: %s", e)
            return []

    def get_company_certifications(self, company_name: str) -> List[Dict[str, Any]]:
        """회사별 인증 데이터 조회 (raw SQL)"""
        try:
            if not self.engine:
                return []
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT * FROM certification WHERE company_name = :company_name ORDER BY created_at DESC"),
                    {"company_name": company_name},
                )
                return self._rows_to_dicts(result)
        except Exception as e:
            logger.error("회사 인증 데이터 조회 실패 (%s): %s", company_name, e)
            return []

    # ===== Utils =====

    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """날짜 문자열을 datetime.date 객체로 변환"""
        if not date_str:
            return None
        s = str(date_str).strip()
        try:
            # ISO-8601
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
            return dt.date()
        except Exception:
            pass
        try:
            # YYYY-MM-DD
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            logger.warning("날짜 파싱 실패: %s", date_str)
            return None
