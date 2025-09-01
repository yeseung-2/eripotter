"""
Assessment Repository - Database Repository Layer
실제 Railway PostgreSQL 데이터베이스와 연결
"""

import logging
from sqlalchemy import text
from typing import List, Optional, Dict, Union
from datetime import datetime
from eripotter_common.database import get_session
from ..entity.assessment_entity import KesgEntity, AssessmentEntity




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
        """assessment 테이블에 응답 데이터 저장"""
        try:
            with get_session() as db:
                for submission in submissions:
                    assessment_entity = AssessmentEntity(
                        company_name=submission["company_name"],
                        question_id=submission["question_id"],
                        question_type=submission["question_type"],
                        level_no=submission.get("level_no"),
                        choice_ids=submission.get("choice_ids") if submission.get("choice_ids") else None,
                        score=submission["score"]
                    )
                    db.add(assessment_entity)
                db.commit()
                logger.info(f"✅ Assessment 응답 저장 성공: {len(submissions)}개 응답")
                return True
        except Exception as e:
            logger.error(f"❌ Assessment 저장 중 오류: {e}")
            return False

    def get_company_results(self, company_name: str) -> List[Dict[str, Union[str, int, List[int], None]]]:
        """assessment 테이블에서 특정 회사의 결과 조회"""
        try:
            with get_session() as db:
                results = db.query(AssessmentEntity).filter(
                    AssessmentEntity.company_name == company_name
                ).all()
                result_list = [result.to_dict() for result in results]
                logger.info(f"✅ 회사 결과 조회 성공: {company_name} - {len(result_list)}개 결과")
                return result_list
        except Exception as e:
            logger.error(f"❌ 회사 결과 조회 중 오류: {e}")
            return []
