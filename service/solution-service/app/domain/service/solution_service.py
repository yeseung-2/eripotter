"""
Solution Service - Service Layer
비즈니스 로직 (솔루션 생성) 담당
"""

import logging
import os
from typing import List, Dict, Union, Optional
from openai import OpenAI
from dotenv import load_dotenv
from ..repository.solution_repository import SolutionRepository
from ..model.solution_model import (
    SolutionSubmissionResponse, 
    KesgItem, 
    AssessmentEntity, 
    VulnerableSection, 
    AssessmentResult
)

# .env 파일 로드
load_dotenv()

logger = logging.getLogger("solution-service")

class SolutionService:
    def __init__(self, repository: SolutionRepository):
        self.repository = repository
        # OpenAI 클라이언트 초기화
        self.openai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def generate_solutions(self, company_name: str) -> List[SolutionSubmissionResponse]:
        """취약 부문별 솔루션 생성 - Assessment 테이블의 score=0 또는 score=25인 문항에 대해서만"""
        try:
            logger.info(f"📝 솔루션 생성 요청: company_name={company_name}")
            
            # 1) Assessment Service에서 score=0 또는 score=25인 데이터 조회
            vulnerable_sections_data = self.repository.get_vulnerable_sections(company_name)
            
            if not vulnerable_sections_data:
                logger.info(f"✅ 취약 부문이 없습니다: company_name={company_name}")
                return []
            
            logger.info(f"📝 취약 부문 {len(vulnerable_sections_data)}개 발견")
            
            # 2) Pydantic 모델로 변환하여 검증
            vulnerable_sections = []
            for section_data in vulnerable_sections_data:
                try:
                    # VulnerableSection 모델로 변환하여 검증
                    vulnerable_section = VulnerableSection(**section_data)
                    vulnerable_sections.append(vulnerable_section)
                except Exception as e:
                    logger.warning(f"⚠️ 취약 부문 데이터 검증 실패: {e}")
                    continue
            
            if not vulnerable_sections:
                logger.info(f"✅ 검증된 취약 부문이 없습니다: company_name={company_name}")
                return []
            
            # 3) GPT API 호출하여 솔루션 생성 (score=0 또는 score=25인 항목)
            solutions = []
            for vulnerable_section in vulnerable_sections:
                try:
                    # Assessment 테이블의 score=0 또는 score=25 조건을 엄격하게 검증
                    if not self._is_vulnerable_section_model(vulnerable_section):
                        continue
                    
                    # GPT 솔루션 생성 (score=0 또는 score=25인 항목에 대해서만)
                    solution_text = self._generate_solution_with_gpt_model(vulnerable_section)
                    
                    # 4) 솔루션 저장
                    saved_solution = self.repository.save_solution(
                        company_name=company_name,
                        question_id=vulnerable_section.question_id,
                        sol=solution_text
                    )
                    
                    # 5) 응답 모델 생성 (kesg 정보 포함)
                    solution_response = SolutionSubmissionResponse(
                        id=saved_solution['id'],
                        company_name=saved_solution['company_name'],
                        question_id=saved_solution['question_id'],
                        sol=saved_solution['sol'],
                        timestamp=saved_solution['timestamp'],
                        item_name=vulnerable_section.item_name,
                        item_desc=vulnerable_section.item_desc,
                        classification=vulnerable_section.classification,
                        domain=vulnerable_section.domain
                    )
                    
                    solutions.append(solution_response)
                    
                except Exception as e:
                    logger.error(f"❌ 개별 솔루션 생성 실패: question_id={vulnerable_section.question_id}, error={e}")
                    continue
            
            logger.info(f"✅ 솔루션 생성 완료: {len(solutions)}개 생성")
            return solutions
            
        except Exception as e:
            logger.error(f"❌ 솔루션 생성 중 예상치 못한 오류: {e}")
            raise
    
    def _is_vulnerable_section_model(self, vulnerable_section: VulnerableSection) -> bool:
        """Assessment 테이블의 score=0 또는 score=25 조건을 Pydantic 모델로 엄격하게 검증"""
        try:
            # 1. score가 0 또는 25인지 확인
            if vulnerable_section.score not in [0, 25]:
                return False
            
            # 2. 필수 필드들이 존재하는지 확인
            if not vulnerable_section.question_id or not vulnerable_section.company_name:
                logger.warning(f"⚠️ 필수 필드 누락: question_id={vulnerable_section.question_id}, company_name={vulnerable_section.company_name}")
                return False
            
            # 3. KESG 정보가 있는지 확인
            if not vulnerable_section.item_name or not vulnerable_section.item_desc:
                logger.warning(f"⚠️ KESG 정보 누락: item_name={vulnerable_section.item_name}, item_desc={vulnerable_section.item_desc}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 취약 부문 검증 중 오류: {e}")
            return False
    
    def _is_vulnerable_section(self, section: Dict[str, Union[str, int, None]]) -> bool:
        """Assessment 테이블의 score=0 또는 score=25 조건을 엄격하게 검증 (기존 메서드 - 호환성 유지)"""
        try:
            # 1. score 필드가 존재하는지 확인
            if 'score' not in section:
                logger.warning(f"⚠️ score 필드가 없음: {section}")
                return False
            
            # 2. score가 정수인지 확인
            score = section.get('score')
            if not isinstance(score, int):
                logger.warning(f"⚠️ score가 정수가 아님: {score}, type: {type(score)}")
                return False
            
            # 3. score가 0 또는 25인지 확인
            if score not in [0, 25]:
                return False
            
            # 4. 필수 필드들이 존재하는지 확인
            required_fields = ['question_id', 'company_name']
            for field in required_fields:
                if field not in section:
                    logger.warning(f"⚠️ 필수 필드 {field}가 없음: {section}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 취약 부문 검증 중 오류: {e}")
            return False
    
    def get_solutions(self, company_name: str) -> List[SolutionSubmissionResponse]:
        """특정 회사의 솔루션 목록 조회"""
        try:
            logger.info(f"📝 솔루션 목록 조회 요청: company_name={company_name}")
            
            # Repository에서 솔루션 조회 (dict 반환)
            solutions_data = self.repository.get_solutions(company_name)
            
            # 응답 모델로 변환
            solutions = []
            for solution_data in solutions_data:
                solution_response = SolutionSubmissionResponse(
                    id=solution_data['id'],
                    company_name=solution_data['company_name'],
                    question_id=solution_data['question_id'],
                    sol=solution_data['sol'],
                    timestamp=solution_data['timestamp'],
                    item_name=solution_data.get('item_name'),
                    item_desc=solution_data.get('item_desc'),
                    classification=solution_data.get('classification'),
                    domain=solution_data.get('domain')
                )
                solutions.append(solution_response)
            
            logger.info(f"✅ 솔루션 목록 조회 성공: {len(solutions)}개 솔루션")
            return solutions
            
        except Exception as e:
            logger.error(f"❌ 솔루션 목록 조회 중 예상치 못한 오류: {e}")
            raise
    
    def _generate_solution_with_gpt_model(self, vulnerable_section: VulnerableSection) -> str:
        """GPT API를 사용하여 솔루션 생성 (Pydantic 모델 기반)"""
        try:
            # KESG 문항 정보 추출 (Pydantic 모델에서 직접 접근)
            item_name = vulnerable_section.item_name or '알 수 없는 항목'
            item_desc = vulnerable_section.item_desc or '설명 없음'
            domain = vulnerable_section.domain or '알 수 없는 도메인'
            classification = vulnerable_section.classification or '알 수 없는 분류'
            
            # Few-shot 예시들
            few_shot_examples = [
                {
                    "user": "분류: E-3-2, 도메인: 환경, 카테고리: 에너지 및 온실가스, 항목명: 에너지 사용량, 항목 설명: • 조직이 소유, 관리, 통제하는 물리적 경계(사업장 등) 내에서 직접 생산하거나 외부로부터 구매하는 에너지 사용 총량을 절감하고 있는지 점검   • 조직 간 규모 차이(매출액, 생산량 등) 또는 각 조직의 사업 변동(구조조정, 인수합병 등)을 고려하여 상대적으로 비교가 용이한 단위당 개념의 ‘원단위’를 기반으로 에너지 사용량을 확인",
                    "assistant": "<p>활동: 전기차 및 친환경 차량 도입</p><p>방법: 사내 차량을 EV로 교체</p><p>목표: 연료 사용량 30% 절감</p>"
                },
                {
                    "user": "분류: G-1-1, 도메인: 지배구조, 카테고리: 윤리 경영, 항목명: 윤리헌장 및 실천 규범, 항목 설명: • 기업이 윤리경영을 선언하고, 이를 실천하기 위한 헌장 및 규범을 갖추고 있는지 확인 • 내부 구성원을 대상으로 윤리경영을 확산하기 위한 교육 및 정책을 수립하고 있는지 점검 • 윤리경영 방침 및 결과를 문서화하여 대내외적으로 공개하고 있는지 확인",
                    "assistant": "<p>활동: CEO 및 이사회 주관 윤리경영 선언</p><p>방법: 전사 행동강령 공표 및 임직원 서약제 도입</p><p>목표: 경영진의 윤리경영 의지 대내외 표명</p>"
                },
                {
                    "user": "분류: S-5-4, 도메인: 사회, 카테고리: 작업환경 개선, 항목명: 산업재해율, 항목 설명: • 조직의 안전보건 거버넌스 구축, 중점 과제 추진, 업무 시스템 구축, 성과 점검 및 평가 등 안전보건 추진 체계가 효과성을 나타내고 있는지 확인 • 조직 구성원의 안전·보건을 위협하는 요인을 지속적으로 관리하고 재해율을 줄이기 위해 노력하고 있는지 점검 (국내외 모든 구성원으로부터 발생하는 산업재해율 추이 분석)",
                    "assistant": "<p>활동: AI 기반 산업재해 예측 시스템 구축</p><p>방법: 고위험사업장 예측 플랫폼 도입, AI로 잠재적 재해 시점 사전 인지</p><p>목표: 패턴 기반 리스크 관리 및 선제적 재해 예방</p>"
                }
            ]
            
            # Messages 배열 구성: system → few-shot examples → 마지막 user
            messages = [
                {
                    "role": "system", 
                    "content": "당신은 ESG 전문가입니다. 기업의 ESG 취약 부문에 대한 구체적이고 실현 가능한 솔루션을 제시합니다. 반드시 '<p>활동: ...</p><p>방법: ...</p><p>목표: ...</p>' HTML 태그 구조로 응답해야 합니다. 다른 설명이나 추가 텍스트 없이, HTML 태그 형식만 반환하세요."
                }
            ]
            
            # Few-shot 예시 추가
            for example in few_shot_examples:
                messages.append({"role": "user", "content": example["user"]})
                messages.append({"role": "assistant", "content": example["assistant"]})
            
            # 마지막 user 메시지 (실제 취약부문 정보)
            final_user_message = f"분류: {classification}, 도메인: {domain}, 항목명: {item_name}, 항목 설명: {item_desc}"
            messages.append({"role": "user", "content": final_user_message})
            
            # GPT API 호출
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=600,
                temperature=0.3
            )
            
            # 응답에서 솔루션 텍스트 추출
            solution_text = response.choices[0].message.content.strip()
            
            return solution_text
            
        except Exception as e:
            logger.error(f"❌ GPT API 호출 실패: {e}")
            # GPT API 실패 시 예외를 다시 발생시켜서 상위에서 처리하도록 함
            raise
    
    def _generate_solution_with_gpt(self, vulnerable_section: Dict[str, Union[str, int, None]]) -> str:
        """GPT API를 사용하여 솔루션 생성 (기존 메서드 - 호환성 유지)"""
        try:
            # KESG 문항 정보 추출
            item_name = vulnerable_section.get('item_name', '알 수 없는 항목')
            item_desc = vulnerable_section.get('item_desc', '설명 없음')
            domain = vulnerable_section.get('domain', '알 수 없는 도메인')
            classification = vulnerable_section.get('classification', '알 수 없는 분류')
            
            # Few-shot 예시들
            few_shot_examples = [
                {
                    "user": "분류: E-3-2, 도메인: 환경, 카테고리: 에너지 및 온실가스, 항목명: 에너지 사용량, 항목 설명: • 조직이 소유, 관리, 통제하는 물리적 경계(사업장 등) 내에서 직접 생산하거나 외부로부터 구매하는 에너지 사용 총량을 절감하고 있는지 점검   • 조직 간 규모 차이(매출액, 생산량 등) 또는 각 조직의 사업 변동(구조조정, 인수합병 등)을 고려하여 상대적으로 비교가 용이한 단위당 개념의 '원단위'를 기반으로 에너지 사용량을 확인",
                    "assistant": "<p>활동: 전기차 및 친환경 차량 도입</p><p>방법: 사내 차량을 EV로 교체</p><p>목표: 연료 사용량 30% 절감</p>"
                },
                {
                    "user": "분류: G-1-1, 도메인: 지배구조, 카테고리: 윤리 경영, 항목명: 윤리헌장 및 실천 규범, 항목 설명: • 기업이 윤리경영을 선언하고, 이를 실천하기 위한 헌장 및 규범을 갖추고 있는지 확인 • 내부 구성원을 대상으로 윤리경영을 확산하기 위한 교육 및 정책을 수립하고 있는지 점검 • 윤리경영 방침 및 결과를 문서화하여 대내외적으로 공개하고 있는지 확인",
                    "assistant": "<p>활동: CEO 및 이사회 주관 윤리경영 선언</p><p>방법: 전사 행동강령 공표 및 임직원 서약제 도입</p><p>목표: 경영진의 윤리경영 의지 대내외 표명</p>"
                },
                {
                    "user": "분류: S-5-4, 도메인: 사회, 카테고리: 작업환경 개선, 항목명: 산업재해율, 항목 설명: • 조직의 안전보건 거버넌스 구축, 중점 과제 추진, 업무 시스템 구축, 성과 점검 및 평가 등 안전보건 추진 체계가 효과성을 나타내고 있는지 확인 • 조직 구성원의 안전·보건을 위협하는 요인을 지속적으로 관리하고 재해율을 줄이기 위해 노력하고 있는지 점검 (국내외 모든 구성원으로부터 발생하는 산업재해율 추이 분석)",
                    "assistant": "<p>활동: AI 기반 산업재해 예측 시스템 구축</p><p>방법: 고위험사업장 예측 플랫폼 도입, AI로 잠재적 재해 시점 사전 인지</p><p>목표: 패턴 기반 리스크 관리 및 선제적 재해 예방</p>"
                }
            ]
            
            # Messages 배열 구성: system → few-shot examples → 마지막 user
            messages = [
                {
                    "role": "system", 
                    "content": "당신은 ESG 전문가입니다. 기업의 ESG 취약 부문에 대한 구체적이고 실현 가능한 솔루션을 제시합니다. 반드시 '<p>활동: ...</p><p>방법: ...</p><p>목표: ...</p>' HTML 태그 구조로 응답해야 합니다. 다른 설명이나 추가 텍스트 없이, HTML 태그 형식만 반환하세요."
                }
            ]
            
            # Few-shot 예시 추가
            for example in few_shot_examples:
                messages.append({"role": "user", "content": example["user"]})
                messages.append({"role": "assistant", "content": example["assistant"]})
            
            # 마지막 user 메시지 (실제 취약부문 정보)
            final_user_message = f"분류: {classification}, 도메인: {domain}, 항목명: {item_name}, 항목 설명: {item_desc}"
            messages.append({"role": "user", "content": final_user_message})
            
            # GPT API 호출
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=600,
                temperature=0.3
            )
            
            # 응답에서 솔루션 텍스트 추출
            solution_text = response.choices[0].message.content.strip()
            
            return solution_text
            
        except Exception as e:
            logger.error(f"❌ GPT API 호출 실패: {e}")
            # GPT API 실패 시 예외를 다시 발생시켜서 상위에서 처리하도록 함
            raise
