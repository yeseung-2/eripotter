"""
Monitoring Service - 공급망 모니터링 및 취약부문 관리
"""

import logging
from typing import List, Dict, Union, Optional
from datetime import datetime

from ..repository.monitoring_repository import MonitoringRepository
from ..model.monitoring_model import (
    # Base Entity Models
    KesgEntity, AssessmentEntity, SolutionEntity, CompanyEntity,
    
    # Supply Chain Models
    CompanyRelation, SupplyChainNode,
    
    # Vulnerability Models
    VulnerableSection, CompanyVulnerabilityResponse, 
    SupplyChainVulnerabilityNode, SupplyChainVulnerabilityResponse,
    
    # Assessment Result Models
    AssessmentResult, CompanyAssessmentResponse,
    
    # Solution Models
    SolutionWithDetails, CompanySolutionResponse,
    
    # Supply Chain Assessment Models
    SupplyChainAssessmentNode, SupplyChainAssessmentResponse,
    
    # Company Management Models
    CompanyListResponse,
    
    # Error Response Models
    ErrorResponse
)

logger = logging.getLogger("monitoring-service")

class MonitoringService:
    def __init__(self, repository: MonitoringRepository):
        self.repository = repository
    
    # ===== Company Management =====
    
    def get_company_list(self) -> CompanyListResponse:
        """회사 목록 조회"""
        try:
            logger.info("📝 회사 목록 조회 요청")
            
            companies_data = self.repository.get_all_companies()
            companies = [CompanyEntity(**company) for company in companies_data]
            
            response = CompanyListResponse(
                companies=companies,
                total_count=len(companies)
            )
            
            logger.info(f"✅ 회사 목록 조회 성공: {len(companies)}개 회사")
            return response
            
        except Exception as e:
            logger.error(f"❌ 회사 목록 조회 중 예상치 못한 오류: {e}")
            return CompanyListResponse(
                status="error",
                message=f"회사 목록 조회 실패: {str(e)}"
            )
    
    # ===== Vulnerability Analysis =====
    
    def get_company_vulnerabilities(self, company_name: str) -> CompanyVulnerabilityResponse:
        """특정 회사의 취약부문(score=0) 조회"""
        try:
            logger.info(f"📝 회사 취약부문 조회 요청: company_name={company_name}")
            
            # Assessment Service에서 취약부문 조회
            vulnerable_sections_data = self.repository.get_company_vulnerable_sections(company_name)
            
            # Pydantic 모델로 변환
            vulnerable_sections = []
            for section_data in vulnerable_sections_data:
                try:
                    vulnerable_section = VulnerableSection(**section_data)
                    vulnerable_sections.append(vulnerable_section)
                except Exception as e:
                    logger.warning(f"⚠️ 취약부문 데이터 변환 실패: {e}")
                    continue
            
            response = CompanyVulnerabilityResponse(
                company_name=company_name,
                vulnerable_sections=vulnerable_sections,
                total_count=len(vulnerable_sections)
            )
            
            logger.info(f"✅ 회사 취약부문 조회 성공: {len(vulnerable_sections)}개 취약부문")
            return response
            
        except Exception as e:
            logger.error(f"❌ 회사 취약부문 조회 중 예상치 못한 오류: {e}")
            return CompanyVulnerabilityResponse(
                status="error",
                company_name=company_name,
                message=f"회사 취약부문 조회 실패: {str(e)}"
            )
    
    def get_supply_chain_vulnerabilities(self, company_name: str) -> SupplyChainVulnerabilityResponse:
        """공급망 전체 취약부문 재귀 탐색"""
        try:
            logger.info(f"📝 공급망 취약부문 조회 요청: root_company={company_name}")
            
            # 데이터베이스 연결 테스트
            try:
                # 간단한 연결 테스트
                test_companies = self.repository.get_all_companies()
                logger.info(f"✅ 데이터베이스 연결 확인: {len(test_companies)}개 회사 데이터")
            except Exception as db_error:
                logger.error(f"❌ 데이터베이스 연결 실패: {db_error}")
                return SupplyChainVulnerabilityResponse(
                    status="error",
                    root_company=company_name,
                    message=f"데이터베이스 연결 실패: {str(db_error)}"
                )
            
            # 재귀적으로 공급망 트리 구축
            supply_chain_tree = self._build_supply_chain_vulnerability_tree(company_name)
            
            # 전체 통계 계산
            total_companies, total_vulnerabilities = self._calculate_supply_chain_stats(supply_chain_tree)
            
            response = SupplyChainVulnerabilityResponse(
                root_company=company_name,
                supply_chain_tree=supply_chain_tree,
                total_companies=total_companies,
                total_vulnerabilities=total_vulnerabilities
            )
            
            logger.info(f"✅ 공급망 취약부문 조회 성공: {total_companies}개 회사, {total_vulnerabilities}개 취약부문")
            return response
            
        except Exception as e:
            logger.error(f"❌ 공급망 취약부문 조회 중 예상치 못한 오류: {e}")
            logger.error(f"❌ 오류 상세: {str(e)}")
            import traceback
            logger.error(f"❌ 스택 트레이스: {traceback.format_exc()}")
            
            return SupplyChainVulnerabilityResponse(
                status="error",
                root_company=company_name,
                message=f"공급망 취약부문 조회 실패: {str(e)}"
            )
    
    def _build_supply_chain_vulnerability_tree(self, company_name: str = None) -> SupplyChainVulnerabilityNode:
        """재귀적으로 공급망 취약부문 트리 구축"""
        try:
            # 초기 호출 시 root_company 사용
            if company_name is None:
                company_name = self.root_company
                
            logger.info(f"📝 공급망 트리 구축 중: company={company_name}")
            
            # 현재 회사의 취약부문 조회
            try:
                vulnerable_sections_data = self.repository.get_company_vulnerable_sections(company_name)
                logger.info(f"📝 취약부문 데이터 조회: {company_name} - {len(vulnerable_sections_data)}개")
            except Exception as e:
                logger.error(f"❌ 취약부문 데이터 조회 실패 (company={company_name}): {e}")
                vulnerable_sections_data = []
            vulnerable_sections = []
            
            for section_data in vulnerable_sections_data:
                try:
                    vulnerable_section = VulnerableSection(**section_data)
                    vulnerable_sections.append(vulnerable_section)
                except Exception as e:
                    logger.warning(f"⚠️ 취약부문 데이터 변환 실패: {e}")
                    continue
            
            # 현재 회사의 tier1 협력사들 조회
            try:
                tier1_companies = self.repository.get_tier1_companies(company_name)
                logger.info(f"📝 Tier1 협력사 조회: {company_name} - {len(tier1_companies)}개")
            except Exception as e:
                logger.error(f"❌ Tier1 협력사 조회 실패 (company={company_name}): {e}")
                tier1_companies = []
            
            # 재귀적으로 하위 노드들 구축
            children = []
            for tier1_company in tier1_companies:
                try:
                    child_node = self._build_supply_chain_vulnerability_tree(tier1_company)
                    children.append(child_node)
                except Exception as e:
                    logger.error(f"❌ 하위 노드 구축 실패 (company={tier1_company}): {e}")
                    # 오류가 발생해도 계속 진행
                    continue
            
            # 취약부문 개수 계산
            vulnerability_count = len(vulnerable_sections)
            
            logger.info(f"✅ 노드 구축 완료: {company_name} - 취약부문 {vulnerability_count}개, 하위 노드 {len(children)}개")
            
            return SupplyChainVulnerabilityNode(
                company_name=company_name,
                tier1s=tier1_companies,
                vulnerable_sections=vulnerable_sections,
                vulnerability_count=vulnerability_count,
                children=children
            )
            
        except Exception as e:
            logger.error(f"❌ 공급망 트리 구축 중 오류 (company={company_name}): {e}")
            logger.error(f"❌ 오류 상세: {str(e)}")
            import traceback
            logger.error(f"❌ 스택 트레이스: {traceback.format_exc()}")
            return SupplyChainVulnerabilityNode(
                company_name=company_name,
                tier1s=[],
                vulnerable_sections=[],
                vulnerability_count=0,
                children=[]
            )
    
    def _calculate_supply_chain_stats(self, node: SupplyChainVulnerabilityNode) -> tuple[int, int]:
        """공급망 트리에서 전체 통계 계산"""
        total_companies = 1  # 현재 노드
        total_vulnerabilities = node.vulnerability_count
        
        for child in node.children:
            child_companies, child_vulnerabilities = self._calculate_supply_chain_stats(child)
            total_companies += child_companies
            total_vulnerabilities += child_vulnerabilities
        
        return total_companies, total_vulnerabilities
    
    # ===== Assessment Results =====
    
    def get_company_assessment(self) -> CompanyAssessmentResponse:
        """특정 회사의 Assessment 결과 조회"""
        try:
            logger.info(f"📝 회사 Assessment 결과 조회 요청: company_name={self.root_company}")
            
            # Assessment Service에서 결과 조회
            assessment_results_data = self.repository.get_company_assessment_results(self.root_company)
            
            # Pydantic 모델로 변환 및 점수 계산
            assessment_results = []
            total_score = 0.0
            max_possible_score = 0.0
            
            for result_data in assessment_results_data:
                try:
                    assessment_result = AssessmentResult(**result_data)
                    assessment_results.append(assessment_result)
                    
                    # 점수 계산
                    weight = assessment_result.weight or 1.0
                    total_score += assessment_result.score * weight
                    max_possible_score += 100 * weight
                    
                except Exception as e:
                    logger.warning(f"⚠️ Assessment 결과 데이터 변환 실패: {e}")
                    continue
            
            # 달성률 계산
            achievement_rate = (total_score / max_possible_score * 100) if max_possible_score > 0 else 0.0
            
            response = CompanyAssessmentResponse(
                company_name=self.root_company,
                assessment_results=assessment_results,
                total_count=len(assessment_results),
                total_score=round(total_score, 2),
                max_possible_score=round(max_possible_score, 2),
                achievement_rate=round(achievement_rate, 2)
            )
            
            logger.info(f"✅ 회사 Assessment 결과 조회 성공: {len(assessment_results)}개 결과, 달성률 {achievement_rate:.1f}%")
            return response
            
        except Exception as e:
            logger.error(f"❌ 회사 Assessment 결과 조회 중 예상치 못한 오류: {e}")
            return CompanyAssessmentResponse(
                status="error",
                company_name=self.root_company,
                message=f"Assessment 결과 조회 실패: {str(e)}"
            )
    
    def get_supply_chain_assessment(self) -> SupplyChainAssessmentResponse:
        """공급망 전체 Assessment 결과 재귀 탐색"""
        try:
            logger.info(f"📝 공급망 Assessment 결과 조회 요청: root_company={self.root_company}")
            
            # 재귀적으로 공급망 Assessment 트리 구축
            supply_chain_tree = self._build_supply_chain_assessment_tree()
            
            # 전체 통계 계산
            total_companies, average_achievement_rate = self._calculate_supply_chain_assessment_stats(supply_chain_tree)
            
            response = SupplyChainAssessmentResponse(
                root_company=self.root_company,
                supply_chain_tree=supply_chain_tree,
                total_companies=total_companies,
                average_achievement_rate=round(average_achievement_rate, 2)
            )
            
            logger.info(f"✅ 공급망 Assessment 결과 조회 성공: {total_companies}개 회사, 평균 달성률 {average_achievement_rate:.1f}%")
            return response
            
        except Exception as e:
            logger.error(f"❌ 공급망 Assessment 결과 조회 중 예상치 못한 오류: {e}")
            return SupplyChainAssessmentResponse(
                status="error",
                root_company=self.root_company,
                message=f"공급망 Assessment 결과 조회 실패: {str(e)}"
            )
    
    def _build_supply_chain_assessment_tree(self, company_name: str = None) -> SupplyChainAssessmentNode:
        """재귀적으로 공급망 Assessment 트리 구축"""
        try:
            # 초기 호출 시 root_company 사용
            if company_name is None:
                company_name = self.root_company
                
            # 현재 회사의 Assessment 결과 조회
            assessment_results_data = self.repository.get_company_assessment_results(company_name)
            assessment_results = []
            
            total_score = 0.0
            max_possible_score = 0.0
            
            for result_data in assessment_results_data:
                try:
                    assessment_result = AssessmentResult(**result_data)
                    assessment_results.append(assessment_result)
                    
                    # 점수 계산
                    weight = assessment_result.weight or 1.0
                    total_score += assessment_result.score * weight
                    max_possible_score += 100 * weight
                    
                except Exception as e:
                    logger.warning(f"⚠️ Assessment 결과 데이터 변환 실패: {e}")
                    continue
            
            # 달성률 계산
            achievement_rate = (total_score / max_possible_score * 100) if max_possible_score > 0 else 0.0
            
            # 현재 회사의 tier1 협력사들 조회
            tier1_companies = self.repository.get_tier1_companies(company_name)
            
            # 재귀적으로 하위 노드들 구축
            children = []
            for tier1_company in tier1_companies:
                child_node = self._build_supply_chain_assessment_tree(tier1_company)
                children.append(child_node)
            
            return SupplyChainAssessmentNode(
                company_name=company_name,
                tier1s=tier1_companies,
                assessment_results=assessment_results,
                total_score=round(total_score, 2),
                max_possible_score=round(max_possible_score, 2),
                achievement_rate=round(achievement_rate, 2),
                children=children
            )
            
        except Exception as e:
            logger.error(f"❌ 공급망 Assessment 트리 구축 중 오류 (company={company_name}): {e}")
            return SupplyChainAssessmentNode(
                company_name=company_name,
                tier1s=[],
                assessment_results=[],
                total_score=0.0,
                max_possible_score=0.0,
                achievement_rate=0.0,
                children=[]
            )
    
    def _calculate_supply_chain_assessment_stats(self, node: SupplyChainAssessmentNode) -> tuple[int, float]:
        """공급망 Assessment 트리에서 전체 통계 계산"""
        total_companies = 1  # 현재 노드
        total_achievement_rate = node.achievement_rate
        
        for child in node.children:
            child_companies, child_achievement_rate = self._calculate_supply_chain_assessment_stats(child)
            total_companies += child_companies
            total_achievement_rate += child_achievement_rate
        
        average_achievement_rate = total_achievement_rate / total_companies if total_companies > 0 else 0.0
        return total_companies, average_achievement_rate
    
    # ===== Solution Management =====
    
    def get_company_solutions(self) -> CompanySolutionResponse:
        """특정 회사의 솔루션 리스트 조회"""
        try:
            logger.info(f"📝 회사 솔루션 조회 요청: company_name={self.root_company}")
            
            # Solution Service에서 솔루션 조회
            solutions_data = self.repository.get_company_solutions(self.root_company)
            
            # Pydantic 모델로 변환
            solutions = []
            for solution_data in solutions_data:
                try:
                    solution = SolutionWithDetails(**solution_data)
                    solutions.append(solution)
                except Exception as e:
                    logger.warning(f"⚠️ 솔루션 데이터 변환 실패: {e}")
                    continue
            
            response = CompanySolutionResponse(
                company_name=self.root_company,
                solutions=solutions,
                total_count=len(solutions)
            )
            
            logger.info(f"✅ 회사 솔루션 조회 성공: {len(solutions)}개 솔루션")
            return response
            
        except Exception as e:
            logger.error(f"❌ 회사 솔루션 조회 중 예상치 못한 오류: {e}")
            return CompanySolutionResponse(
                status="error",
                company_name=self.root_company,
                message=f"솔루션 조회 실패: {str(e)}"
            )
