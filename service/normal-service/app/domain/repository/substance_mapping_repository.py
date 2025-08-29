from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("substance-mapping-repository")

class SubstanceMappingRepository:
    def __init__(self, engine):
        self.engine = engine
    
    def save_original_data(self, filename: str, data: list, file_size: int, company_id: str = None, company_name: str = None, uploaded_by: str = None, uploaded_by_email: str = None) -> bool:
        """원본 엑셀 데이터를 데이터베이스에 저장 (normal 테이블 사용)"""
        try:
            from datetime import datetime
            
            # 각 물질을 개별 행으로 저장
            with self.engine.connect() as conn:
                for substance_data in data:
                    # 엑셀 데이터에서 물질 정보 추출
                    substance_name = substance_data.get('name', '')
                    usage_amount = substance_data.get('amount', 0.0)
                    usage_unit = substance_data.get('unit', '')
                    
                    conn.execute(text("""
                        INSERT INTO normal (
                            company_id, company_name, filename, file_size, substance_name,
                            usage_amount, usage_unit, uploaded_by, uploaded_by_email,
                            upload_time, upload_status, created_at, updated_at
                        ) VALUES (
                            :company_id, :company_name, :filename, :file_size, :substance_name,
                            :usage_amount, :usage_unit, :uploaded_by, :uploaded_by_email,
                            :upload_time, :upload_status, :created_at, :updated_at
                        )
                    """), {
                        "company_id": company_id,
                        "company_name": company_name,
                        "filename": filename,
                        "file_size": file_size,
                        "substance_name": substance_name,
                        "usage_amount": usage_amount,
                        "usage_unit": usage_unit,
                        "uploaded_by": uploaded_by,
                        "uploaded_by_email": uploaded_by_email,
                        "upload_time": datetime.now(),
                        "upload_status": "uploaded",
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    })
                
                conn.commit()
            
            logger.info(f"✅ 원본 데이터 저장 완료: {company_name} - {uploaded_by} - {filename} ({len(data)}개 물질)")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"❌ 원본 데이터 저장 실패: {e}")
            return False

    def save_mapping_result(self, mapping_result: Dict[str, Any], company_id: str = None, company_name: str = None) -> bool:
        """AI 매핑 결과를 데이터베이스에 저장 (certification 테이블 사용)"""
        try:
            from datetime import datetime
            
            # 매핑 상태 결정
            confidence = mapping_result.get("confidence", 0.0)
            if confidence >= 0.8:
                mapping_status = "mapped"
            elif confidence >= 0.6:
                mapping_status = "needs_review"
            else:
                mapping_status = "not_mapped"
            
            with self.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO certification (
                        company_id, company_name, substance_name, mapped_sid, mapped_name,
                        confidence_score, mapping_status, mapping_time, created_at, updated_at
                    ) VALUES (
                        :company_id, :company_name, :substance_name, :mapped_sid, :mapped_name,
                        :confidence_score, :mapping_status, :mapping_time, :created_at, :updated_at
                    )
                """), {
                    "company_id": company_id,
                    "company_name": company_name,
                    "substance_name": mapping_result.get("substance_name"),
                    "mapped_sid": mapping_result.get("mapped_sid"),
                    "mapped_name": mapping_result.get("mapped_name"),
                    "confidence_score": confidence,
                    "mapping_status": mapping_status,
                    "mapping_time": datetime.now(),
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                })
                
                conn.commit()
            
            logger.info(f"✅ AI 매핑 결과 저장 완료: {company_name} - {mapping_result.get('substance_name')} (상태: {mapping_status}, 신뢰도: {confidence:.2%})")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"❌ AI 매핑 결과 저장 실패: {e}")
            return False
    
    def save_mapping_correction(self, mapping_id: int, correction_data: Dict[str, Any], company_id: str = None, company_name: str = None) -> bool:
        """사용자 수정 결과를 sharing 테이블에 저장"""
        try:
            from datetime import datetime
            
            with self.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO sharing (
                        company_id, company_name, mapping_id, corrected_sid, corrected_name,
                        correction_reason, corrected_by, correction_time, created_at, updated_at
                    ) VALUES (
                        :company_id, :company_name, :mapping_id, :corrected_sid, :corrected_name,
                        :correction_reason, :corrected_by, :correction_time, :created_at, :updated_at
                    )
                """), {
                    "company_id": company_id,
                    "company_name": company_name,
                    "mapping_id": mapping_id,
                    "corrected_sid": correction_data.get("corrected_sid"),
                    "corrected_name": correction_data.get("corrected_name"),
                    "correction_reason": correction_data.get("correction_reason"),
                    "corrected_by": correction_data.get("corrected_by", "user"),
                    "correction_time": datetime.now(),
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                })
                
                conn.commit()
            
            logger.info(f"✅ 사용자 수정 사항 저장 완료: {company_name} - mapping_id {mapping_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"❌ 사용자 수정 사항 저장 실패: {e}")
            return False
    
    def get_mapping_statistics(self) -> Dict[str, Any]:
        """매핑 통계 조회"""
        try:
            with self.engine.connect() as conn:
                # normal 테이블 통계
                result = conn.execute(text("""
                    SELECT 
                        COUNT(*) as total_mappings,
                        COUNT(CASE WHEN status = 'mapped' THEN 1 END) as successful_mappings,
                        COUNT(CASE WHEN status = 'needs_review' THEN 1 END) as review_needed_mappings,
                        COUNT(CASE WHEN status = 'not_mapped' THEN 1 END) as failed_mappings,
                        AVG(confidence_score) as avg_confidence
                    FROM normal
                """))
                
                row = result.fetchone()
                
                return {
                    'total_mappings': row.total_mappings or 0,
                    'successful_mappings': row.successful_mappings or 0,
                    'review_needed_mappings': row.review_needed_mappings or 0,
                    'failed_mappings': row.failed_mappings or 0,
                    'avg_confidence': float(row.avg_confidence) if row.avg_confidence else 0.0
                }
                
        except SQLAlchemyError as e:
            logger.error(f"❌ 매핑 통계 조회 중 데이터베이스 오류: {e}")
            return {}
        except Exception as e:
            logger.error(f"❌ 매핑 통계 조회 중 예상치 못한 오류: {e}")
            return {}

