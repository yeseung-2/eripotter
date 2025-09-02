"""
Monitoring Repository - Database Repository Layer
실제 Railway PostgreSQL 데이터베이스와 연결
"""

import logging
from sqlalchemy import text
from typing import List, Optional, Dict, Union
from datetime import datetime
from eripotter_common.database import get_session
from ..entity.monitoring_entity import KesgEntity, AssessmentEntity, SolutionEntity, CompanyEntity

logger = logging.getLogger("monitoring-repository")

# ===== Repository Class =====

class MonitoringRepository:
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

    def get_all_companies(self) -> List[Dict[str, Union[str, int, None]]]:
        """company 테이블에서 모든 회사 조회"""
        try:
            with get_session() as db:
                companies = db.query(CompanyEntity).all()
                result = [company.to_dict() for company in companies]
                logger.info(f"✅ 회사 목록 조회 성공: {len(result)}개 회사")
                return result
        except Exception as e:
            logger.error(f"❌ 회사 목록 조회 중 오류: {e}")
            return []

    def get_tier1_companies(self, company_name: str) -> List[str]:
        """company 테이블에서 특정 회사의 tier1 협력사 조회"""
        try:
            with get_session() as db:
                companies = db.query(CompanyEntity).filter(
                    CompanyEntity.company_name == company_name
                ).all()
                tier1_list = [company.tier1 for company in companies if company.tier1]
                logger.info(f"✅ Tier1 협력사 조회 성공: {company_name} - {len(tier1_list)}개")
                return tier1_list
        except Exception as e:
            logger.error(f"❌ Tier1 협력사 조회 중 오류: {e}")
            return []

    def get_company_vulnerable_sections(self, company_name: str) -> List[Dict[str, Union[str, int, float, List[Dict[str, Union[str, int]]], Dict[str, int], None]]]:
        """assessment와 kesg 테이블을 조인하여 특정 회사의 취약부문(score=0) 조회"""
        try:
            with get_session() as db:
                # assessment와 kesg 테이블 조인하여 score=0인 항목 조회
                query = text("""
                    SELECT 
                        a.id, a.company_name, a.question_id, a.question_type, 
                        a.level_no, a.choice_ids, a.score, a.timestamp,
                        k.item_name, k.item_desc, k.classification, k.domain, k.category,
                        k.levels_json, k.choices_json, k.weight
                    FROM assessment a
                    JOIN kesg k ON a.question_id = k.id
                    WHERE a.company_name = :company_name AND a.score = 0
                    ORDER BY k.classification, k.domain, k.category
                """)
                
                result = db.execute(query, {"company_name": company_name})
                vulnerable_sections = []
                
                for row in result:
                    section = {
                        "id": row.id,
                        "company_name": row.company_name,
                        "question_id": row.question_id,
                        "question_type": row.question_type,
                        "level_no": row.level_no,
                        "choice_ids": row.choice_ids,
                        "score": row.score,
                        "timestamp": row.timestamp,
                        "item_name": row.item_name,
                        "item_desc": row.item_desc,
                        "classification": row.classification,
                        "domain": row.domain,
                        "category": row.category,
                        "levels_json": row.levels_json,
                        "choices_json": row.choices_json,
                        "weight": row.weight
                    }
                    vulnerable_sections.append(section)
                
                logger.info(f"✅ 취약부문 조회 성공: {company_name} - {len(vulnerable_sections)}개")
                return vulnerable_sections
                
        except Exception as e:
            logger.error(f"❌ 취약부문 조회 중 오류: {e}")
            return []

    def get_company_assessment_results(self, company_name: str) -> List[Dict[str, Union[str, int, float, List[Dict[str, Union[str, int]]], Dict[str, int], None]]]:
        """assessment와 kesg 테이블을 조인하여 특정 회사의 assessment 결과 조회"""
        try:
            with get_session() as db:
                # assessment와 kesg 테이블 조인하여 모든 결과 조회
                query = text("""
                    SELECT 
                        a.id, a.company_name, a.question_id, a.question_type, 
                        a.level_no, a.choice_ids, a.score, a.timestamp,
                        k.item_name, k.item_desc, k.classification, k.domain, k.category,
                        k.levels_json, k.choices_json, k.weight
                    FROM assessment a
                    JOIN kesg k ON a.question_id = k.id
                    WHERE a.company_name = :company_name
                    ORDER BY k.classification, k.domain, k.category
                """)
                
                result = db.execute(query, {"company_name": company_name})
                assessment_results = []
                
                for row in result:
                    result_item = {
                        "id": row.id,
                        "company_name": row.company_name,
                        "question_id": row.question_id,
                        "question_type": row.question_type,
                        "level_no": row.level_no,
                        "choice_ids": row.choice_ids,
                        "score": row.score,
                        "timestamp": row.timestamp,
                        "item_name": row.item_name,
                        "item_desc": row.item_desc,
                        "classification": row.classification,
                        "domain": row.domain,
                        "category": row.category,
                        "levels_json": row.levels_json,
                        "choices_json": row.choices_json,
                        "weight": row.weight
                    }
                    assessment_results.append(result_item)
                
                logger.info(f"✅ Assessment 결과 조회 성공: {company_name} - {len(assessment_results)}개")
                return assessment_results
                
        except Exception as e:
            logger.error(f"❌ Assessment 결과 조회 중 오류: {e}")
            return []

    def get_company_solutions(self, company_name: str) -> List[Dict[str, Union[str, int, datetime, None]]]:
        """solution과 kesg 테이블을 조인하여 특정 회사의 솔루션 조회"""
        try:
            with get_session() as db:
                # solution과 kesg 테이블 조인하여 솔루션 조회
                query = text("""
                    SELECT 
                        s.id, s.company_name, s.question_id, s.sol, s.timestamp,
                        k.item_name, k.item_desc, k.classification, k.domain, k.category
                    FROM solution s
                    JOIN kesg k ON s.question_id = k.id
                    WHERE s.company_name = :company_name
                    ORDER BY k.classification, k.domain, k.category
                """)
                
                result = db.execute(query, {"company_name": company_name})
                solutions = []
                
                for row in result:
                    solution = {
                        "id": row.id,
                        "company_name": row.company_name,
                        "question_id": row.question_id,
                        "sol": row.sol,
                        "timestamp": row.timestamp,
                        "item_name": row.item_name,
                        "item_desc": row.item_desc,
                        "classification": row.classification,
                        "domain": row.domain,
                        "category": row.category
                    }
                    solutions.append(solution)
                
                logger.info(f"✅ 솔루션 조회 성공: {company_name} - {len(solutions)}개")
                return solutions
                
        except Exception as e:
            logger.error(f"❌ 솔루션 조회 중 오류: {e}")
            return []
