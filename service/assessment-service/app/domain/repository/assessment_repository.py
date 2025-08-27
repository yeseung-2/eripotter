from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import List, Dict, Any, Optional
from ..model.assessment_model import KesgItem

logger = logging.getLogger("assessment-repository")

class AssessmentRepository:
    def __init__(self, engine):
        self.engine = engine
    
    def get_kesg_items(self) -> List[KesgItem]:
        """kesg 테이블에서 모든 데이터 조회"""
        try:
            with self.engine.connect() as conn:
                query = text("SELECT id, item_name, question_type, levels_json, choices_json FROM kesg ORDER BY id")
                result = conn.execute(query)
                
                items = []
                for row in result:
                    # question_type에 따라 적절한 choices 데이터 설정
                    choices_data = None
                    if row.question_type in ['three_level', 'five_level']:
                        choices_data = row.levels_json
                    elif row.question_type == 'five_choice':
                        choices_data = row.choices_json
                    
                    items.append(KesgItem(
                        id=row.id,
                        item_name=row.item_name,
                        question_type=row.question_type,
                        choices=choices_data,
                        category="자가진단"
                    ))
                
                logger.info(f"✅ kesg 테이블에서 {len(items)}개 항목 조회 성공")
                return items
                
        except SQLAlchemyError as e:
            logger.error(f"❌ kesg 테이블 조회 중 데이터베이스 오류: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ kesg 테이블 조회 중 예상치 못한 오류: {e}")
            raise
    
    def get_kesg_item_by_id(self, item_id: int) -> Optional[KesgItem]:
        """특정 ID의 kesg 항목 조회"""
        try:
            with self.engine.connect() as conn:
                query = text("SELECT id, item_name, question_type, levels_json, choices_json FROM kesg WHERE id = :item_id")
                result = conn.execute(query, {"item_id": item_id})
                row = result.fetchone()
                
                if row:
                    # question_type에 따라 적절한 choices 데이터 설정
                    choices_data = None
                    if row.question_type in ['three_level', 'five_level']:
                        choices_data = row.levels_json
                    elif row.question_type == 'five_choice':
                        choices_data = row.choices_json
                    
                    return KesgItem(
                        id=row.id,
                        item_name=row.item_name,
                        question_type=row.question_type,
                        choices=choices_data,
                        category="자가진단"
                    )
                return None
                
        except SQLAlchemyError as e:
            logger.error(f"❌ kesg 항목 조회 중 데이터베이스 오류: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ kesg 항목 조회 중 예상치 못한 오류: {e}")
            raise
    
    def save_assessment_responses(self, submissions: List[Dict[str, Any]]) -> bool:
        """assessment 테이블에 응답 데이터 저장"""
        try:
            with self.engine.connect() as conn:
                # 트랜잭션 시작
                trans = conn.begin()
                try:
                    for submission in submissions:
                        query = text("""
                            INSERT INTO assessment (
                                company_id, question_id, question_type, 
                                level_no, choice_ids, score, timestamp
                            ) VALUES (
                                :company_id, :question_id, :question_type,
                                :level_no, :choice_ids, :score, NOW()
                            )
                        """)
                        
                        conn.execute(query, {
                            'company_id': submission['company_id'],
                            'question_id': submission['question_id'],
                            'question_type': submission['question_type'],
                            'level_no': submission.get('level_no'),
                            'choice_ids': submission.get('choice_ids'),
                            'score': submission['score']
                        })
                    
                    # 트랜잭션 커밋
                    trans.commit()
                    logger.info(f"✅ {len(submissions)}개 응답 데이터 저장 완료")
                    return True
                    
                except Exception as e:
                    # 오류 발생 시 롤백
                    trans.rollback()
                    logger.error(f"❌ 응답 데이터 저장 실패: {e}")
                    raise
                    
        except SQLAlchemyError as e:
            logger.error(f"❌ 데이터베이스 오류: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ 예상치 못한 오류: {e}")
            raise
    
    def calculate_score(self, question_id: int, question_type: str, selected_value: Any) -> int:
        """점수 계산"""
        try:
            with self.engine.connect() as conn:
                # kesg 테이블에서 해당 문항의 levels_json 또는 scoring_json 조회
                query = text("""
                    SELECT levels_json, scoring_json 
                    FROM kesg 
                    WHERE id = :question_id
                """)
                result = conn.execute(query, {'question_id': question_id})
                row = result.fetchone()
                
                if not row:
                    logger.warning(f"⚠️ question_id {question_id}에 해당하는 kesg 데이터가 없습니다.")
                    return 0
                
                if question_type in ['three_level', 'five_level']:
                    # 단계형: levels_json에서 점수 계산
                    levels_json = row.levels_json
                    if isinstance(levels_json, list) and isinstance(selected_value, int):
                        for level in levels_json:
                            if level.get('level_no') == selected_value:
                                return level.get('score', 0)
                    return 0
                    
                elif question_type == 'five_choice':
                    # 선택형: scoring_json에서 점수 계산
                    scoring_json = row.scoring_json
                    if isinstance(scoring_json, list) and isinstance(selected_value, list):
                        total_score = 0
                        for choice_id in selected_value:
                            for choice in scoring_json:
                                if choice.get('id') == choice_id:
                                    total_score += choice.get('score', 0)
                        return total_score
                    return 0
                    
                else:
                    logger.warning(f"⚠️ 알 수 없는 question_type: {question_type}")
                    return 0
                    
        except SQLAlchemyError as e:
            logger.error(f"❌ 점수 계산 중 데이터베이스 오류: {e}")
            return 0
        except Exception as e:
            logger.error(f"❌ 점수 계산 중 예상치 못한 오류: {e}")
            return 0
    
    def calculate_scores_batch(self, submissions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """배치로 점수 계산 (성능 최적화)"""
        try:
            # 모든 question_id 수집
            question_ids = [submission['question_id'] for submission in submissions]
            
            with self.engine.connect() as conn:
                # 한 번의 쿼리로 모든 kesg 데이터 조회
                query = text("""
                    SELECT id, levels_json, scoring_json 
                    FROM kesg 
                    WHERE id = ANY(:question_ids)
                """)
                result = conn.execute(query, {'question_ids': question_ids})
                kesg_data = {row.id: {'levels_json': row.levels_json, 'scoring_json': row.scoring_json} for row in result}
                
                # 각 submission에 대해 점수 계산
                for submission in submissions:
                    question_id = submission['question_id']
                    question_type = submission['question_type']
                    selected_value = submission.get('level_no') or submission.get('choice_ids')
                    
                    if question_id not in kesg_data:
                        logger.warning(f"⚠️ question_id {question_id}에 해당하는 kesg 데이터가 없습니다.")
                        submission['score'] = 0
                        continue
                    
                    kesg_item = kesg_data[question_id]
                    
                    if question_type in ['three_level', 'five_level']:
                        # 단계형: levels_json에서 점수 계산
                        levels_json = kesg_item['levels_json']
                        if isinstance(levels_json, list) and isinstance(selected_value, int):
                            for level in levels_json:
                                if level.get('level_no') == selected_value:
                                    submission['score'] = level.get('score', 0)
                                    break
                            else:
                                submission['score'] = 0
                        else:
                            submission['score'] = 0
                            
                    elif question_type == 'five_choice':
                        # 선택형: scoring_json에서 점수 계산
                        scoring_json = kesg_item['scoring_json']
                        if isinstance(scoring_json, list) and isinstance(selected_value, list):
                            total_score = 0
                            for choice_id in selected_value:
                                for choice in scoring_json:
                                    if choice.get('id') == choice_id:
                                        total_score += choice.get('score', 0)
                            submission['score'] = total_score
                        else:
                            submission['score'] = 0
                            
                    else:
                        logger.warning(f"⚠️ 알 수 없는 question_type: {question_type}")
                        submission['score'] = 0
                
                return submissions
                    
        except SQLAlchemyError as e:
            logger.error(f"❌ 배치 점수 계산 중 데이터베이스 오류: {e}")
            # 오류 시 기본 점수 0으로 설정
            for submission in submissions:
                submission['score'] = 0
            return submissions
        except Exception as e:
            logger.error(f"❌ 배치 점수 계산 중 예상치 못한 오류: {e}")
            # 오류 시 기본 점수 0으로 설정
            for submission in submissions:
                submission['score'] = 0
            return submissions
    
    def get_company_results(self, company_id: str) -> List[Dict[str, Any]]:
        """특정 회사의 자가진단 결과 조회"""
        try:
            logger.info(f"📝 회사별 결과 조회 요청: company_id={company_id}")
            
            with self.engine.connect() as conn:
                query = text("""
                    SELECT 
                        id,
                        company_id,
                        question_id,
                        question_type,
                        level_no,
                        choice_ids,
                        score,
                        timestamp
                    FROM assessment 
                    WHERE company_id = :company_id
                    ORDER BY timestamp DESC, question_id ASC
                """)
                
                result = conn.execute(query, {'company_id': company_id})
                results = []
                
                for row in result:
                    results.append({
                        'id': row.id,
                        'company_id': row.company_id,
                        'question_id': row.question_id,
                        'question_type': row.question_type,
                        'level_no': row.level_no,
                        'choice_ids': row.choice_ids,
                        'score': row.score,
                        'timestamp': row.timestamp.isoformat() if row.timestamp else None
                    })
                
                logger.info(f"✅ 회사별 결과 조회 성공: {len(results)}개 결과")
                return results
                
        except SQLAlchemyError as e:
            logger.error(f"❌ 회사별 결과 조회 중 데이터베이스 오류: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ 회사별 결과 조회 중 예상치 못한 오류: {e}")
            raise