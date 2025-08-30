"""
Assessment Service - Service Layer
비즈니스 로직 (점수 계산) 담당
"""

import logging
from typing import List, Dict, Union
from ..repository.assessment_repository import AssessmentRepository
from ..model.assessment_model import KesgItem, KesgResponse, AssessmentSubmissionResponse

logger = logging.getLogger("assessment-service")

class AssessmentService:
    def __init__(self, repository: AssessmentRepository):
        self.repository = repository
    
    def get_kesg_items(self) -> KesgResponse:
        """KESG 항목 목록 조회"""
        try:
            logger.info("📝 KESG 항목 목록 조회 요청")
            
            # Repository에서 데이터 조회
            kesg_data_list = self.repository.get_kesg_items()
            
            # Pydantic 모델로 변환
            kesg_items = []
            for kesg_data in kesg_data_list:
                kesg_item = KesgItem(
                    id=kesg_data['id'],
                    classification=kesg_data.get('classification'),
                    domain=kesg_data.get('domain'),
                    category=kesg_data.get('category'),
                    item_name=kesg_data.get('item_name'),
                    item_desc=kesg_data.get('item_desc'),
                    metric_desc=kesg_data.get('metric_desc'),
                    data_source=kesg_data.get('data_source'),
                    data_period=kesg_data.get('data_period'),
                    data_method=kesg_data.get('data_method'),
                    data_detail=kesg_data.get('data_detail'),
                    question_type=kesg_data.get('question_type'),
                    levels_json=kesg_data.get('levels_json'),
                    choices_json=kesg_data.get('choices_json'),
                    scoring_json=kesg_data.get('scoring_json'),
                    weight=kesg_data.get('weight')
                )
                kesg_items.append(kesg_item)
            
            # KesgResponse로 감싸서 반환
            response = KesgResponse(
                items=kesg_items,
                total_count=len(kesg_items)
            )
            
            logger.info(f"✅ KESG 항목 목록 조회 성공: {len(kesg_items)}개 항목")
            return response
            
        except Exception as e:
            logger.error(f"❌ KESG 항목 목록 조회 중 예상치 못한 오류: {e}")
            raise
    
    def get_kesg_item_by_id(self, item_id: int) -> KesgItem:
        """특정 KESG 항목 조회"""
        try:
            logger.info(f"📝 KESG 항목 조회 요청: item_id={item_id}")
            
            # Repository에서 데이터 조회
            kesg_data = self.repository.get_kesg_item_by_id(item_id)
            
            if not kesg_data:
                logger.warning(f"⚠️ KESG 항목을 찾을 수 없음: item_id={item_id}")
                raise ValueError(f"ID {item_id}에 해당하는 KESG 항목을 찾을 수 없습니다.")
            
            # Pydantic 모델로 변환
            kesg_item = KesgItem(
                id=kesg_data['id'],
                classification=kesg_data.get('classification'),
                domain=kesg_data.get('domain'),
                category=kesg_data.get('category'),
                item_name=kesg_data.get('item_name'),
                item_desc=kesg_data.get('item_desc'),
                metric_desc=kesg_data.get('metric_desc'),
                data_source=kesg_data.get('data_source'),
                data_period=kesg_data.get('data_period'),
                data_method=kesg_data.get('data_method'),
                data_detail=kesg_data.get('data_detail'),
                question_type=kesg_data.get('question_type'),
                levels_json=kesg_data.get('levels_json'),
                choices_json=kesg_data.get('choices_json'),
                scoring_json=kesg_data.get('scoring_json'),
                weight=kesg_data.get('weight')
            )
            
            logger.info(f"✅ KESG 항목 조회 성공: item_id={item_id}")
            return kesg_item
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"❌ KESG 항목 조회 중 예상치 못한 오류: {e}")
            raise
    
    def calculate_score(self, question_id: int, question_type: str, selected_value: Union[int, List[int]]) -> int:
        """점수 계산"""
        try:
            # kesg 테이블에서 해당 문항의 levels_json 또는 scoring_json 조회
            kesg_data = self.repository.get_kesg_scoring_data([question_id])
            
            if question_id not in kesg_data:
                logger.warning(f"⚠️ question_id {question_id}에 해당하는 kesg 데이터가 없습니다.")
                return 0
            
            kesg_item = kesg_data[question_id]
            
            if question_type in ['three_level', 'five_level']:
                # 단계형: levels_json에서 점수 계산
                levels_json = kesg_item['levels_json']
                if isinstance(levels_json, list) and isinstance(selected_value, int):
                    for level in levels_json:
                        if level.get('level_no') == selected_value:
                            return level.get('score', 0)
                return 0
                
            elif question_type == 'five_choice':
                # 선택형: scoring_json에서 점수 계산
                scoring_json = kesg_item['scoring_json']
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
                
        except Exception as e:
            logger.error(f"❌ 점수 계산 중 예상치 못한 오류: {e}")
            return 0
    
    def calculate_scores_batch(self, submissions: List[Dict[str, Union[str, int, List[int], None]]]) -> List[Dict[str, Union[str, int, List[int], None]]]:
        """배치로 점수 계산 (성능 최적화)"""
        try:
            # 모든 question_id 수집
            question_ids = [submission['question_id'] for submission in submissions]
            
            # 한 번의 쿼리로 모든 kesg 데이터 조회
            kesg_data = self.repository.get_kesg_scoring_data(question_ids)
            
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
                    # 선택형: 선택 개수에 따라 점수 계산
                    scoring_json = kesg_item['scoring_json']
                    if isinstance(scoring_json, dict) and isinstance(selected_value, list):
                        # 선택된 choice 개수에 따라 점수 계산
                        choice_count = len(selected_value)
                        choice_count_str = str(choice_count)
                        if choice_count_str in scoring_json:
                            submission['score'] = scoring_json[choice_count_str]
                        else:
                            submission['score'] = 0
                    else:
                        submission['score'] = 0
                        
                else:
                    logger.warning(f"⚠️ 알 수 없는 question_type: {question_type}")
                    submission['score'] = 0
            
            return submissions
                
        except Exception as e:
            logger.error(f"❌ 배치 점수 계산 중 예상치 못한 오류: {e}")
            # 오류 시 기본 점수 0으로 설정
            for submission in submissions:
                submission['score'] = 0
            return submissions
    
    def submit_assessment(self, company_name: str, responses: List[Dict[str, Union[str, int, List[int], None]]]) -> List[AssessmentSubmissionResponse]:
        """자가진단 응답 제출"""
        try:
            logger.info(f"📝 자가진단 응답 제출 요청: company_name={company_name}, responses_count={len(responses)}")
            
            # 응답 데이터를 submission 형태로 변환
            submissions = []
            for response in responses:
                # response가 딕셔너리인지 확인
                if isinstance(response, dict):
                    response_data = response
                else:
                    # Pydantic 모델인 경우 dict로 변환
                    response_data = response.dict()
                
                submission = {
                    'company_name': company_name,
                    'question_id': response_data['question_id'],
                    'question_type': response_data['question_type']
                }
                
                # question_type에 따라 적절한 필드 설정
                if response_data['question_type'] in ['three_level', 'five_level']:
                    submission['level_no'] = response_data.get('level_no')
                    submission['choice_ids'] = None
                elif response_data['question_type'] == 'five_choice':
                    submission['level_no'] = None
                    submission['choice_ids'] = response_data.get('choice_ids')
                else:
                    logger.warning(f"⚠️ 알 수 없는 question_type: {response_data['question_type']}")
                    continue
                
                submissions.append(submission)
            
            # 배치로 점수 계산
            submissions_with_scores = self.calculate_scores_batch(submissions)
            
            # 데이터베이스에 저장
            success = self.repository.save_assessment_responses(submissions_with_scores)
            
            if success:
                logger.info(f"✅ 자가진단 응답 제출 성공: company_name={company_name}")
            else:
                logger.error(f"❌ 자가진단 응답 제출 실패: company_name={company_name}")
            
            # AssessmentSubmissionResponse 리스트로 변환하여 반환
            result = []
            for submission in submissions_with_scores:
                response = AssessmentSubmissionResponse(
                    id=0,  # Mock에서는 0으로 설정
                    company_name=submission['company_name'],
                    question_id=submission['question_id'],
                    question_type=submission['question_type'],
                    level_no=submission.get('level_no'),
                    choice_ids=submission.get('choice_ids'),
                    score=submission.get('score', 0),
                    timestamp=None  # Mock에서는 None으로 설정
                )
                result.append(response)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 자가진단 응답 제출 중 예상치 못한 오류: {e}")
            return []
    
    def get_company_results(self, company_name: str) -> List[Dict[str, Union[str, int, List[int], None]]]:
        """회사별 자가진단 결과 조회"""
        try:
            logger.info(f"📝 회사별 결과 조회 요청: company_name={company_name}")
            results = self.repository.get_company_results(company_name)
            logger.info(f"✅ 회사별 결과 조회 성공: {len(results)}개 결과")
            return results
        except Exception as e:
            logger.error(f"❌ 회사별 결과 조회 중 예상치 못한 오류: {e}")
            return []
    
    def get_assessment_results(self, company_name: str) -> List[Dict[str, Union[str, int, List[int], None]]]:
        """특정 회사의 자가진단 결과 조회 (상세 정보 포함)"""
        try:
            logger.info(f"📝 자가진단 결과 조회 요청: company_name={company_name}")
            
            # 기본 결과 조회
            results = self.repository.get_company_results(company_name)
            
            # kesg 데이터와 조인하여 상세 정보 추가
            detailed_results = []
            for result in results:
                question_id = result['question_id']
                kesg_data = self.repository.get_kesg_item_by_id(question_id)
                
                if kesg_data:
                    detailed_result = {
                        **result,
                        'item_name': kesg_data.get('item_name'),
                        'item_desc': kesg_data.get('item_desc'),
                        'classification': kesg_data.get('classification'),
                        'domain': kesg_data.get('domain')
                    }
                else:
                    detailed_result = {
                        **result,
                        'item_name': f'문항 {question_id}',
                        'item_desc': '설명 없음',
                        'classification': 'N/A',
                        'domain': 'N/A'
                    }
                
                detailed_results.append(detailed_result)
            
            logger.info(f"✅ 자가진단 결과 조회 성공: {len(detailed_results)}개 결과")
            return detailed_results
            
        except Exception as e:
            logger.error(f"❌ 자가진단 결과 조회 중 예상치 못한 오류: {e}")
            return []
    
    def get_vulnerable_sections(self, company_name: str) -> List[Dict[str, Union[str, int, List[int], None]]]:
        """특정 회사의 취약 부문 조회 (score가 0인 문항)"""
        try:
            logger.info(f"📝 취약 부문 조회 요청: company_name={company_name}")
            
            # 기본 결과 조회
            results = self.repository.get_company_results(company_name)
            
            # score가 0인 문항만 필터링
            vulnerable_results = [result for result in results if result.get('score', 0) == 0]
            
            # kesg 데이터와 조인하여 상세 정보 추가
            detailed_vulnerable_sections = []
            for result in vulnerable_results:
                question_id = result['question_id']
                kesg_data = self.repository.get_kesg_item_by_id(question_id)
                
                if kesg_data:
                    detailed_section = {
                        **result,
                        'item_name': kesg_data.get('item_name'),
                        'item_desc': kesg_data.get('item_desc'),
                        'classification': kesg_data.get('classification'),
                        'domain': kesg_data.get('domain')
                    }
                else:
                    detailed_section = {
                        **result,
                        'item_name': f'문항 {question_id}',
                        'item_desc': '설명 없음',
                        'classification': 'N/A',
                        'domain': 'N/A'
                    }
                
                detailed_vulnerable_sections.append(detailed_section)
            
            logger.info(f"✅ 취약 부문 조회 성공: {len(detailed_vulnerable_sections)}개 취약 부문")
            return detailed_vulnerable_sections
            
        except Exception as e:
            logger.error(f"❌ 취약 부문 조회 중 예상치 못한 오류: {e}")
            return []
