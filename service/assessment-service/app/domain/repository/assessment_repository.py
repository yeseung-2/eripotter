"""
Assessment Repository - Database Repository Layer
실제 Railway PostgreSQL 데이터베이스와 연결
"""

import logging
from sqlalchemy import text, func
from typing import List, Optional, Dict, Union
from datetime import datetime
from eripotter_common.database import get_session
from ..entity.assessment_entity import KesgEntity, AssessmentEntity

logger = logging.getLogger("assessment-repository")




# Database Repository 클래스
class AssessmentRepository:
    def __init__(self):
        """Repository 초기화 시 데이터베이스 연결 테스트"""
        try:
            with get_session() as db:
                # 간단한 연결 테스트
                db.execute(text("SELECT 1"))
                logger.info("✅ 데이터베이스 연결 테스트 성공")
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 테스트 실패: {e}")
            raise
    def get_kesg_items(self) -> List[Dict[str, Union[str, int, float, List[Dict[str, Union[str, int]]], Dict[str, int], None]]]:
        """kesg 테이블에서 모든 문항 조회"""
        try:
            with get_session() as db:
                kesg_items = db.query(KesgEntity).all()
                result = [item.to_dict() for item in kesg_items]
                logger.info(f"✅ KESG 항목 조회 성공: {len(result)}개 항목")
                return result
        except Exception as e:
            logger.error(f"❌ KESG 항목 조회 중 오류: {e}")
            return []

    def get_kesg_item_by_id(self, item_id: int) -> Optional[Dict[str, Union[str, int, float, List[Dict[str, Union[str, int]]], Dict[str, int], None]]]:
        """kesg 테이블에서 특정 ID의 문항 조회"""
        try:
            with get_session() as db:
                item = db.query(KesgEntity).filter(KesgEntity.id == item_id).first()
                return item.to_dict() if item else None
        except Exception as e:
            logger.error(f"❌ KESG 항목 조회 중 오류: {e}")
            return None

    def get_kesg_scoring_data(self, question_ids: List[int]) -> Dict[int, Dict[str, Union[str, int, float, List[Dict[str, Union[str, int]]], Dict[str, int], None]]]:
        """kesg 테이블에서 여러 문항의 점수 데이터 조회"""
        try:
            with get_session() as db:
                items = db.query(KesgEntity).filter(KesgEntity.id.in_(question_ids)).all()
                return {item.id: item.to_dict() for item in items}
        except Exception as e:
            logger.error(f"❌ KESG 점수 데이터 조회 중 오류: {e}")
            return {}

    def save_assessment_responses(self, submissions: List[Dict[str, Union[str, int, List[int], None]]]) -> bool:
        """assessment 테이블에 응답 데이터 저장 (같은 문항은 덮어쓰기) - 배치 UPSERT 방식"""
        try:
            with get_session() as db:
                # 회사명과 문항 ID로 그룹화하여 중복 제거
                unique_submissions = {}
                for submission in submissions:
                    key = (submission["company_name"], submission["question_id"])
                    unique_submissions[key] = submission
                
                if not unique_submissions:
                    logger.warning("⚠️ 저장할 응답 데이터가 없습니다.")
                    return True
                
                # 배치 UPSERT 쿼리 실행
                batch_upsert_query = text("""
                    INSERT INTO assessment (company_name, question_id, question_type, level_no, choice_ids, score, timestamp)
                    VALUES (:company_name, :question_id, :question_type, :level_no, :choice_ids, :score, NOW())
                    ON CONFLICT (company_name, question_id) 
                    DO UPDATE SET
                        question_type = EXCLUDED.question_type,
                        level_no = EXCLUDED.level_no,
                        choice_ids = EXCLUDED.choice_ids,
                        score = EXCLUDED.score,
                        timestamp = NOW()
                """)
                
                # executemany를 사용하여 배치로 실행
                db.executemany(batch_upsert_query, [
                    {
                        'company_name': submission["company_name"],
                        'question_id': submission["question_id"],
                        'question_type': submission["question_type"],
                        'level_no': submission.get("level_no"),
                        'choice_ids': submission.get("choice_ids") if submission.get("choice_ids") else None,
                        'score': submission["score"]
                    }
                    for submission in unique_submissions.values()
                ])
                
                db.commit()
                logger.info(f"✅ Assessment 응답 배치 UPSERT 성공: {len(unique_submissions)}개 응답")
                return True
        except Exception as e:
            logger.error(f"❌ Assessment 배치 UPSERT 중 오류: {e}")
            if 'db' in locals():
                db.rollback()
            return False

    def get_company_results(self, company_name: str) -> List[Dict[str, Union[str, int, List[int], None]]]:
        """assessment 테이블에서 특정 회사의 결과 조회"""
        try:
            with get_session() as db:
                results = db.query(AssessmentEntity).filter(
                    AssessmentEntity.company_name == company_name
                ).order_by(AssessmentEntity.question_id).all()
                result_list = [result.to_dict() for result in results]
                logger.info(f"✅ 회사 결과 조회 성공: {company_name} - {len(result_list)}개 결과")
                return result_list
        except Exception as e:
            logger.error(f"❌ 회사 결과 조회 중 오류: {e}")
            return []

    def get_assessment_by_company_and_question(self, company_name: str, question_id: int) -> Optional[Dict[str, Union[str, int, List[int], None]]]:
        """특정 회사의 특정 문항에 대한 응답 조회"""
        try:
            with get_session() as db:
                result = db.query(AssessmentEntity).filter(
                    AssessmentEntity.company_name == company_name,
                    AssessmentEntity.question_id == question_id
                ).first()
                return result.to_dict() if result else None
        except Exception as e:
            logger.error(f"❌ 특정 응답 조회 중 오류: {e}")
            return None

    def delete_company_assessments(self, company_name: str) -> bool:
        """특정 회사의 모든 자가진단 응답 삭제"""
        try:
            with get_session() as db:
                deleted_count = db.query(AssessmentEntity).filter(
                    AssessmentEntity.company_name == company_name
                ).delete()
                db.commit()
                logger.info(f"✅ 회사 자가진단 응답 삭제 성공: {company_name} - {deleted_count}개 삭제")
                return True
        except Exception as e:
            logger.error(f"❌ 회사 자가진단 응답 삭제 중 오류: {e}")
            if 'db' in locals():
                db.rollback()
            return False
