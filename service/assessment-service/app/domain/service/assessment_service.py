import logging
from typing import List, Dict, Any
from ..repository.assessment_repository import AssessmentRepository
from ..model.assessment_model import KesgItem, KesgResponse
import os

logger = logging.getLogger("assessment-service")

class AssessmentService:
    def __init__(self):
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        self.repository = AssessmentRepository(database_url)
    
    def get_kesg_items(self) -> KesgResponse:
        """kesg 테이블의 모든 항목 조회"""
        try:
            logger.info("📝 kesg 테이블 항목 조회 요청")
            items = self.repository.get_kesg_items()
            
            response = KesgResponse(
                items=items,
                total_count=len(items)
            )
            
            logger.info(f"✅ kesg 테이블 항목 조회 성공: {len(items)}개 항목")
            return response
            
        except Exception as e:
            logger.error(f"❌ kesg 테이블 항목 조회 서비스 오류: {e}")
            raise
    
    def get_kesg_item_by_id(self, item_id: int) -> KesgItem:
        """특정 ID의 kesg 항목 조회"""
        try:
            logger.info(f"📝 kesg 항목 조회 요청: ID {item_id}")
            item = self.repository.get_kesg_item_by_id(item_id)
            
            if not item:
                raise ValueError(f"ID {item_id}에 해당하는 kesg 항목을 찾을 수 없습니다")
            
            logger.info(f"✅ kesg 항목 조회 성공: ID {item_id}")
            return item
            
        except Exception as e:
            logger.error(f"❌ kesg 항목 조회 서비스 오류: {e}")
            raise
    
    # 기존 메서드들 (더미 구현)
    def get_all_assessments(self):
        return {"message": "get_all_assessments - 구현 예정"}
    
    def get_assessment_by_id(self, assessment_id: str):
        return {"message": f"get_assessment_by_id - 구현 예정: {assessment_id}"}
    
    def create_assessment(self, assessment_data: dict):
        return {"message": "create_assessment - 구현 예정", "data": assessment_data}
    
    def update_assessment(self, assessment_id: str, assessment_data: dict):
        return {"message": f"update_assessment - 구현 예정: {assessment_id}", "data": assessment_data}
    
    def delete_assessment(self, assessment_id: str):
        return {"message": f"delete_assessment - 구현 예정: {assessment_id}"}
    
    def get_metrics(self):
        return {"message": "get_metrics - 구현 예정"}
    
    def submit_assessment(self, company_id: str, responses: List[Dict[str, Any]]) -> bool:
        """자가진단 응답 제출 및 저장"""
        try:
            logger.info(f"📝 자가진단 응답 제출 요청: company_id={company_id}, responses_count={len(responses)}")
            
            submissions = []
            for response in responses:
                # submission 데이터 구성
                submission = {
                    'company_id': company_id,
                    'question_id': response['question_id'],
                    'question_type': response['question_type']
                }
                
                # question_type에 따라 적절한 필드 설정
                if response['question_type'] in ['three_level', 'five_level']:
                    submission['level_no'] = response.get('level_id')
                elif response['question_type'] == 'five_choice':
                    submission['choice_ids'] = response.get('choice_ids')
                
                submissions.append(submission)
            
            # 배치로 점수 계산 (성능 최적화)
            submissions_with_scores = self.repository.calculate_scores_batch(submissions)
            
            # 데이터베이스에 저장
            success = self.repository.save_assessment_responses(submissions_with_scores)
            
            if success:
                logger.info(f"✅ 자가진단 응답 제출 성공: {len(submissions)}개 응답 저장")
            else:
                logger.error("❌ 자가진단 응답 제출 실패")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 자가진단 응답 제출 서비스 오류: {e}")
            raise
    
    def get_company_results(self, company_id: str) -> List[Dict[str, Any]]:
        """특정 회사의 자가진단 결과 조회"""
        try:
            logger.info(f"📝 회사별 결과 조회 요청: company_id={company_id}")
            
            results = self.repository.get_company_results(company_id)
            
            logger.info(f"✅ 회사별 결과 조회 성공: {len(results)}개 결과")
            return results
            
        except Exception as e:
            logger.error(f"❌ 회사별 결과 조회 서비스 오류: {e}")
            raise
