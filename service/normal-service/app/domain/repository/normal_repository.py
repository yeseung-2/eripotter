"""
Normal Repository - Normal 테이블 전용 Repository
ESG 원본 데이터 관리
"""
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import text

# eripotter_common database import
from eripotter_common.database import engine

# Entity import
from ..entity import NormalEntity, CertificationEntity

logger = logging.getLogger("normal-repository")

class NormalRepository:
    def __init__(self):
        self.engine = engine
        self.Session = sessionmaker(bind=engine)
    
    def create(self, substance_data: Dict[str, Any]) -> Optional[NormalEntity]:
        """새로운 Normal 데이터 생성"""
        try:
            session = self.Session()
            
            normal_entity = NormalEntity(**substance_data)
            session.add(normal_entity)
            session.commit()
            
            # 생성된 객체 반환 (ID 포함)
            session.refresh(normal_entity)
            result = normal_entity
            session.close()
            
            logger.info(f"✅ Normal 데이터 생성 완료: ID {result.id}")
            return result
            
        except SQLAlchemyError as e:
            if 'session' in locals():
                session.rollback()
                session.close()
            logger.error(f"❌ Normal 데이터 생성 실패: {e}")
            return None
    
    def get_by_id(self, normal_id: int) -> Optional[NormalEntity]:
        """ID로 Normal 데이터 조회"""
        try:
            session = self.Session()
            
            result = session.query(NormalEntity).filter_by(id=normal_id).first()
            session.close()
            
            return result
            
        except SQLAlchemyError as e:
            if 'session' in locals():
                session.close()
            logger.error(f"❌ Normal 데이터 조회 실패 (ID: {normal_id}): {e}")
            return None
    
    def get_by_company(self, company_id: str, limit: int = 10, offset: int = 0) -> List[NormalEntity]:
        """회사별 Normal 데이터 조회"""
        try:
            session = self.Session()
            
            results = session.query(NormalEntity)\
                .filter_by(company_id=company_id)\
                .order_by(NormalEntity.created_at.desc())\
                .limit(limit)\
                .offset(offset)\
                .all()
            
            session.close()
            return results
            
        except SQLAlchemyError as e:
            if 'session' in locals():
                session.close()
            logger.error(f"❌ 회사별 Normal 데이터 조회 실패 (company_id: {company_id}): {e}")
            return []
    
    def get_all(self, limit: int = 50, offset: int = 0) -> List[NormalEntity]:
        """모든 Normal 데이터 조회"""
        try:
            session = self.Session()
            
            results = session.query(NormalEntity)\
                .order_by(NormalEntity.created_at.desc())\
                .limit(limit)\
                .offset(offset)\
                .all()
            
            session.close()
            return results
            
        except SQLAlchemyError as e:
            if 'session' in locals():
                session.close()
            logger.error(f"❌ 전체 Normal 데이터 조회 실패: {e}")
            return []
    
    def update(self, normal_id: int, update_data: Dict[str, Any]) -> bool:
        """Normal 데이터 업데이트"""
        try:
            session = self.Session()
            
            normal_entity = session.query(NormalEntity).filter_by(id=normal_id).first()
            
            if not normal_entity:
                logger.error(f"❌ Normal ID {normal_id}를 찾을 수 없습니다.")
                session.close()
                return False
            
            # 업데이트 데이터 적용
            for key, value in update_data.items():
                if hasattr(normal_entity, key):
                    setattr(normal_entity, key, value)
            
            normal_entity.updated_at = datetime.now()
            session.commit()
            session.close()
            
            logger.info(f"✅ Normal 데이터 업데이트 완료: ID {normal_id}")
            return True
            
        except SQLAlchemyError as e:
            if 'session' in locals():
                session.rollback()
                session.close()
            logger.error(f"❌ Normal 데이터 업데이트 실패 (ID: {normal_id}): {e}")
            return False
    
    def delete(self, normal_id: int) -> bool:
        """Normal 데이터 삭제"""
        try:
            session = self.Session()
            
            normal_entity = session.query(NormalEntity).filter_by(id=normal_id).first()
            
            if not normal_entity:
                logger.error(f"❌ Normal ID {normal_id}를 찾을 수 없습니다.")
                session.close()
                return False
            
            session.delete(normal_entity)
            session.commit()
            session.close()
            
            logger.info(f"✅ Normal 데이터 삭제 완료: ID {normal_id}")
            return True
            
        except SQLAlchemyError as e:
            if 'session' in locals():
                session.rollback()
                session.close()
            logger.error(f"❌ Normal 데이터 삭제 실패 (ID: {normal_id}): {e}")
            return False
    
    def count_by_company(self, company_id: str) -> int:
        """회사별 데이터 개수 조회"""
        try:
            session = self.Session()
            
            count = session.query(NormalEntity).filter_by(company_id=company_id).count()
            session.close()
            
            return count
            
        except SQLAlchemyError as e:
            if 'session' in locals():
                session.close()
            logger.error(f"❌ 회사별 데이터 개수 조회 실패 (company_id: {company_id}): {e}")
            return 0

    def get_all_normalized_data(self) -> List[Dict[str, Any]]:
        """모든 정규화 데이터 조회"""
        try:
            if not self.engine:
                return []
            
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM normal ORDER BY created_at DESC"))
                return [dict(row) for row in result]
        except Exception as e:
            logger.error(f"정규화 데이터 조회 실패: {e}")
            return []

    def get_normalized_data_by_id(self, data_id: str) -> Optional[Dict[str, Any]]:
        """특정 정규화 데이터 조회"""
        try:
            if not self.engine:
                return None
            
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT * FROM normal WHERE id = :data_id"),
                    {"data_id": data_id}
                )
                row = result.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"정규화 데이터 조회 실패 (ID: {data_id}): {e}")
            return None

    def get_company_data(self, company_name: str) -> List[Dict[str, Any]]:
        """회사별 데이터 조회"""
        try:
            if not self.engine:
                return []
            
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT * FROM normal WHERE company_name = :company_name ORDER BY created_at DESC"),
                    {"company_name": company_name}
                )
                return [dict(row) for row in result]
        except Exception as e:
            logger.error(f"회사 데이터 조회 실패 ({company_name}): {e}")
            return []

    # ===== Substance Mapping 관련 메서드들 =====
    
    def save_substance_data(self, substance_data: Dict[str, Any], company_id: str = None, company_name: str = None, uploaded_by: str = None, uploaded_by_email: str = None) -> Optional[int]:
        """프론트엔드에서 받은 물질 데이터를 normal 테이블에 저장"""
        try:
            logger.info(f"🔍 Repository: 데이터 저장 시작 - {substance_data.get('productName', 'Unknown')}")
            logger.info(f"🔍 Repository: Company ID: {company_id}, Company Name: {company_name}")
            session = self.Session()
            logger.info(f"🔍 Repository: 세션 생성 완료")
            
            # NormalEntity 객체 생성
            normal_entity = NormalEntity(
                company_id=company_id,
                company_name=company_name,
                uploaded_by=uploaded_by,
                uploaded_by_email=uploaded_by_email,
                
                # 파일 정보
                filename=substance_data.get('filename'),
                file_size=substance_data.get('file_size', 0),
                file_type=substance_data.get('file_type', 'manual'),  # 'manual' or 'excel'
                
                # 제품 기본 정보
                product_name=substance_data.get('productName'),
                supplier=substance_data.get('supplier'),
                manufacturing_date=self._parse_date(substance_data.get('manufacturingDate')),
                manufacturing_number=substance_data.get('manufacturingNumber'),
                safety_information=substance_data.get('safetyInformation'),
                recycled_material=substance_data.get('recycledMaterial', False),
                
                # 제품 스펙
                capacity=substance_data.get('capacity'),
                energy_density=substance_data.get('energyDensity'),
                
                # 위치 정보
                manufacturing_country=substance_data.get('manufacturingCountry'),
                production_plant=substance_data.get('productionPlant'),
                
                # 처리 방법
                disposal_method=substance_data.get('disposalMethod'),
                recycling_method=substance_data.get('recyclingMethod'),
                
                # 원재료 정보 (JSON)
                raw_materials=substance_data.get('rawMaterials', []),
                raw_material_sources=substance_data.get('rawMaterialSources', []),
                
                # 온실가스 배출량 (JSON)
                greenhouse_gas_emissions=substance_data.get('greenhouseGasEmissions', []),
                
                # 화학물질 구성
                chemical_composition=substance_data.get('chemicalComposition')
            )
            
            logger.info(f"🔍 Repository: NormalEntity 객체 생성 완료")
            session.add(normal_entity)
            logger.info(f"🔍 Repository: 세션에 엔티티 추가 완료")
            session.commit()
            logger.info(f"🔍 Repository: 커밋 완료")
            
            normal_id = normal_entity.id
            session.close()
            logger.info(f"🔍 Repository: 세션 종료 완료")
            
            logger.info(f"✅ 물질 데이터 저장 완료: {company_name} - {substance_data.get('productName')} (ID: {normal_id})")
            return normal_id
            
        except SQLAlchemyError as e:
            if 'session' in locals():
                session.rollback()
                session.close()
            logger.error(f"❌ 물질 데이터 저장 실패: {e}")
            return None
        except Exception as e:
            if 'session' in locals():
                session.rollback()
                session.close()
            logger.error(f"❌ 물질 데이터 저장 중 예상치 못한 오류: {e}")
            return None

    def save_ai_mapping_result(self, normal_id: int, gas_name: str, gas_amount: str, mapping_result: Dict[str, Any], company_id: str = None, company_name: str = None) -> bool:
        """AI 매핑 결과를 certification 테이블에 저장"""
        try:
            session = self.Session()
            
            # 매핑 상태 결정
            confidence = mapping_result.get("confidence", 0.0)
            if confidence >= 0.7:
                mapping_status = "auto_mapped"
            elif confidence >= 0.4:
                mapping_status = "needs_review"
            else:
                mapping_status = "needs_review"  # 낮은 신뢰도도 검토 필요로 분류
            
            # CertificationEntity 객체 생성
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
                
                # 초기에는 AI 매핑 결과를 최종 결과로 설정 (사용자가 나중에 수정 가능)
                final_mapped_sid=mapping_result.get("mapped_sid"),
                final_mapped_name=mapping_result.get("mapped_name"),
                final_cas_number=mapping_result.get("cas_number"),
                final_standard_unit="tonCO2eq",
                
                mapping_status=mapping_status
            )
            
            session.add(certification_entity)
            session.commit()
            session.close()
            
            logger.info(f"✅ AI 매핑 결과 저장 완료: {gas_name} -> {mapping_result.get('mapped_name')} (신뢰도: {confidence:.1%})")
            return True
            
        except SQLAlchemyError as e:
            if 'session' in locals():
                session.rollback()
                session.close()
            logger.error(f"❌ AI 매핑 결과 저장 실패: {e}")
            return False

    def update_user_mapping_correction(self, certification_id: int, correction_data: Dict[str, Any], reviewed_by: str = None) -> bool:
        """사용자가 매핑을 수정한 결과를 certification 테이블에 업데이트"""
        try:
            session = self.Session()
            
            # 해당 certification 레코드 조회
            certification = session.query(CertificationEntity).filter_by(id=certification_id).first()
            
            if not certification:
                logger.error(f"❌ certification ID {certification_id}를 찾을 수 없습니다.")
                session.close()
                return False
            
            # 사용자 수정 내용 반영
            certification.final_mapped_sid = correction_data.get('corrected_sid', certification.final_mapped_sid)
            certification.final_mapped_name = correction_data.get('corrected_name', certification.final_mapped_name)
            certification.final_cas_number = correction_data.get('corrected_cas_number', certification.final_cas_number)
            certification.final_standard_unit = correction_data.get('corrected_unit', certification.final_standard_unit)
            
            certification.mapping_status = 'user_reviewed'
            certification.reviewed_by = reviewed_by
            certification.review_comment = correction_data.get('review_comment')
            certification.updated_at = datetime.now()
            
            session.commit()
            session.close()
            
            logger.info(f"✅ 사용자 매핑 수정 완료: ID {certification_id} - {reviewed_by}")
            return True
            
        except SQLAlchemyError as e:
            if 'session' in locals():
                session.rollback()
                session.close()
            logger.error(f"❌ 사용자 매핑 수정 실패: {e}")
            return False

    def get_saved_mappings(self, company_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """저장된 매핑 결과 조회"""
        try:
            session = self.Session()
            
            query = session.query(CertificationEntity).join(NormalEntity)
            
            if company_id:
                query = query.filter(CertificationEntity.company_id == company_id)
            
            results = query.order_by(CertificationEntity.created_at.desc()).limit(limit).all()
            
            mappings = []
            for cert in results:
                mappings.append({
                    'id': cert.id,
                    'normal_id': cert.normal_id,
                    'company_id': cert.company_id,
                    'company_name': cert.company_name,
                    'original_gas_name': cert.original_gas_name,
                    'original_amount': cert.original_amount,
                    'ai_mapped_name': cert.ai_mapped_name,
                    'ai_confidence_score': cert.ai_confidence_score,
                    'final_mapped_name': cert.final_mapped_name,
                    'mapping_status': cert.mapping_status,
                    'created_at': cert.created_at.isoformat() if cert.created_at else None
                })
            
            session.close()
            logger.info(f"✅ 매핑 결과 조회 완료: {len(mappings)}개 (회사: {company_id or '전체'})")
            return mappings
            
        except SQLAlchemyError as e:
            if 'session' in locals():
                session.close()
            logger.error(f"❌ 매핑 결과 조회 실패 (회사: {company_id or '전체'}): {e}")
            raise Exception(f"데이터베이스에서 매핑 결과를 조회하는 중 오류가 발생했습니다: {str(e)}")

    def get_original_data(self, company_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """원본 데이터 조회"""
        try:
            session = self.Session()
            
            query = session.query(NormalEntity)
            
            if company_id:
                query = query.filter(NormalEntity.company_id == company_id)
            
            results = query.order_by(NormalEntity.created_at.desc()).limit(limit).all()
            
            data = [normal.to_dict() for normal in results]
            session.close()
            
            logger.info(f"✅ 원본 데이터 조회 완료: {len(data)}개 (회사: {company_id or '전체'})")
            return data
            
        except SQLAlchemyError as e:
            if 'session' in locals():
                session.close()
            logger.error(f"❌ 원본 데이터 조회 실패 (회사: {company_id or '전체'}): {e}")
            raise Exception(f"데이터베이스에서 원본 데이터를 조회하는 중 오류가 발생했습니다: {str(e)}")

    def get_mapping_statistics(self) -> Dict[str, Any]:
        """매핑 통계 조회"""
        try:
            session = self.Session()
            
            # certification 테이블 기준 통계
            total_mappings = session.query(CertificationEntity).count()
            auto_mapped = session.query(CertificationEntity).filter(CertificationEntity.mapping_status == 'auto_mapped').count()
            needs_review = session.query(CertificationEntity).filter(CertificationEntity.mapping_status == 'needs_review').count()
            user_reviewed = session.query(CertificationEntity).filter(CertificationEntity.mapping_status == 'user_reviewed').count()
            
            # 평균 신뢰도 계산
            from sqlalchemy import func
            avg_confidence_result = session.query(
                func.avg(CertificationEntity.ai_confidence_score)
            ).filter(
                CertificationEntity.ai_confidence_score.isnot(None)
            ).scalar()
            
            avg_confidence = float(avg_confidence_result) if avg_confidence_result else 0.0
            
            session.close()
            
            stats = {
                'total_mappings': total_mappings,
                'auto_mapped': auto_mapped,
                'needs_review': needs_review,
                'user_reviewed': user_reviewed,
                'avg_confidence': avg_confidence
            }
            
            logger.info(f"✅ 매핑 통계 조회 완료: 총 {total_mappings}개 매핑")
            return stats
            
        except SQLAlchemyError as e:
            if 'session' in locals():
                session.close()
            logger.error(f"❌ 매핑 통계 조회 실패: {e}")
            raise Exception(f"데이터베이스에서 매핑 통계를 조회하는 중 오류가 발생했습니다: {str(e)}")

    def get_company_certifications(self, company_name: str) -> List[Dict[str, Any]]:
        """회사별 인증 데이터 조회"""
        try:
            if not self.engine:
                return []
            
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT * FROM certification WHERE company_name = :company_name ORDER BY created_at DESC"),
                    {"company_name": company_name}
                )
                return [dict(row) for row in result]
        except Exception as e:
            logger.error(f"회사 인증 데이터 조회 실패 ({company_name}): {e}")
            return []

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """날짜 문자열을 datetime 객체로 변환"""
        if not date_str:
            return None
        
        try:
            # ISO format 시도
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            try:
                # 다른 포맷 시도
                return datetime.strptime(date_str, '%Y-%m-%d')
            except:
                logger.warning(f"날짜 파싱 실패: {date_str}")
                return None
