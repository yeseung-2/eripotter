"use client";

import { useState, useEffect } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { getSupplyChainVulnerabilities, getAssessmentCompanies } from '@/lib/api';

// ===== Supply Chain Vulnerability Interfaces =====

interface VulnerableSection {
  id: number;
  company_name: string;
  question_id: number;
  question_type: string;
  level_no?: number;
  choice_ids?: number[];
  score: number;
  timestamp?: string;
  item_name?: string;
  item_desc?: string;
  classification?: string;
  domain?: string;
  category?: string;
  levels_json?: Array<{ [key: string]: string | number }>;
  choices_json?: Array<{ [key: string]: string | number }>;
  weight?: number;
}

interface SupplyChainVulnerabilityNode {
  company_name: string;
  tier1s: string[];
  vulnerable_sections: VulnerableSection[];
  vulnerability_count: number;
  children: SupplyChainVulnerabilityNode[];
}

interface SupplyChainVulnerabilityResponse {
  status: string;
  root_company: string;
  supply_chain_tree: SupplyChainVulnerabilityNode;
  total_companies: number;
  total_vulnerabilities: number;
  message?: string;
}

// ===== Flattened Company Interface =====

interface FlattenedCompany {
  company_name: string;
  tier1s: string[];
  vulnerable_sections: VulnerableSection[];
  vulnerability_count: number;
}

// ===== Assessment Company Interfaces =====

interface AssessmentCompany {
  company_name: string;
  assessment_date: string;
  score: number;
  status: string;
  self_assessment_score: number;
  self_assessment_status: string;
  self_assessment_date: string;
  self_assessment_result: string;
  self_assessment_comment: string;
  self_assessment_score_details: {
    question_id: number;
    question_type: string;
    level_no?: number;
    choice_ids?: number[];
    score: number;
    item_name?: string;
    item_desc?: string;
    classification?: string;
    domain?: string;
    category?: string;
    levels_json?: Array<{ [key: string]: string | number }>;
    choices_json?: Array<{ [key: string]: string | number }>;
  }[];
}

interface AssessmentCompanyListResponse {
  status: string;
  companies: AssessmentCompany[];
  message?: string;
}

// ===== Monitoring Page Component =====

export default function MonitoringPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  const [vulnerableCompanies, setVulnerableCompanies] = useState<FlattenedCompany[]>([]);
  const [assessmentCompanies, setAssessmentCompanies] = useState<AssessmentCompany[]>([]);
  const [activeTab, setActiveTab] = useState<'supply-chain' | 'assessment'>('supply-chain');

  // 하드코딩된 root company
  const rootCompany = "LG에너지솔루션";

  // supply_chain_tree를 flatten하는 함수
  const flattenSupplyChainTree = (node: SupplyChainVulnerabilityNode): FlattenedCompany[] => {
    const companies: FlattenedCompany[] = [];
    
    // 현재 노드가 취약부문이 있으면 추가
    if (node.vulnerable_sections.length > 0) {
      companies.push({
        company_name: node.company_name,
        tier1s: node.tier1s,
        vulnerable_sections: node.vulnerable_sections,
        vulnerability_count: node.vulnerability_count
      });
    }
    
    // 자식 노드들도 재귀적으로 처리
    node.children.forEach(child => {
      companies.push(...flattenSupplyChainTree(child));
    });
    
    return companies;
  };

  // API 호출 함수
  const fetchSupplyChainVulnerabilities = async (): Promise<SupplyChainVulnerabilityResponse> => {
    try {
      const data = await getSupplyChainVulnerabilities();
      return data;
    } catch (error) {
      console.error('API 호출 오류:', error);
      throw new Error('공급망 취약부문 조회 실패');
    }
  };

  // Assessment 기업 목록 조회 함수
  const fetchAssessmentCompanies = async (): Promise<AssessmentCompanyListResponse> => {
    try {
      const data = await getAssessmentCompanies();
      return data;
    } catch (error) {
      console.error('Assessment 기업 목록 조회 오류:', error);
      throw new Error('Assessment 기업 목록 조회 실패');
    }
  };

  // 페이지 로드 시 자동으로 데이터 조회
  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      setError('');

      try {
        if (activeTab === 'supply-chain') {
          const data = await fetchSupplyChainVulnerabilities();
          const flattenedCompanies = flattenSupplyChainTree(data.supply_chain_tree);
          setVulnerableCompanies(flattenedCompanies);
        } else {
          const data = await fetchAssessmentCompanies();
          setAssessmentCompanies(data.companies);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, [activeTab]);

  // 탭 변경 시 데이터 다시 로드
  const handleTabChange = (tab: 'supply-chain' | 'assessment') => {
    setActiveTab(tab);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">공급망 모니터링</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/dashboard')}
                className="p-2 text-gray-400 hover:text-gray-500 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
              </button>
              <div className="flex items-center space-x-3">
                <Image 
                  className="h-8 w-8 rounded-full" 
                  src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80" 
                  alt="User avatar"
                  width={32}
                  height={32}
                />
                <span className="text-sm font-medium text-gray-700">관리자</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* 탭 네비게이션 */}
        <div className="mb-6">
          <nav className="flex space-x-8">
            <button
              onClick={() => handleTabChange('supply-chain')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'supply-chain'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              공급망 취약부문
            </button>
            <button
              onClick={() => handleTabChange('assessment')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'assessment'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Assessment 기업 목록
            </button>
          </nav>
        </div>

        {/* 페이지 제목 */}
        <div className="mb-8">
          {activeTab === 'supply-chain' ? (
            <>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                {rootCompany} 공급망 취약부문 현황
              </h2>
              <p className="text-gray-600">
                공급망 내 취약부문이 있는 회사들을 표시합니다.
              </p>
            </>
          ) : (
            <>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Assessment 기업 모니터링
              </h2>
              <p className="text-gray-600">
                자가진단을 완료한 모든 기업의 결과를 모니터링합니다.
              </p>
            </>
          )}
        </div>

        {/* 에러 메시지 */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              <span className="text-red-800">{error}</span>
            </div>
          </div>
        )}

        {/* 로딩 스피너 */}
        {isLoading && (
          <div className="flex justify-center items-center py-12">
            <div className="text-center">
              <svg className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span className="text-gray-600">불러오는 중...</span>
            </div>
          </div>
        )}

        {/* 취약부문이 있는 회사들 카드 목록 */}
        {!isLoading && !error && (
          <div className="space-y-6">
            {activeTab === 'supply-chain' && (
              <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 xl:grid-cols-3">
                {vulnerableCompanies.length > 0 ? (
                  vulnerableCompanies.map((company, index) => (
                    <div key={index} className="bg-white shadow rounded-lg overflow-hidden">
                      <div className="px-6 py-4 border-b border-gray-200">
                        <div className="flex justify-between items-start">
                          <h3 className="text-lg font-bold text-gray-900">{company.company_name}</h3>
                          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                            {company.vulnerability_count}개 취약부문
                          </span>
                        </div>
                        {company.tier1s.length > 0 && (
                          <p className="text-sm text-gray-500 mt-1">
                            2차사: {company.tier1s.join(', ')}
                          </p>
                        )}
                      </div>
                      <div className="px-6 py-4">
                        <div className="space-y-3">
                          {company.vulnerable_sections.map((section) => (
                            <div key={section.id} className={`border rounded-lg p-3 ${
                              section.score === 0 
                                ? 'border-red-200 bg-red-50' 
                                : 'border-orange-200 bg-orange-50'
                            }`}>
                              <div className="flex justify-between items-start mb-2">
                                <h4 className={`font-semibold text-sm ${
                                  section.score === 0 ? 'text-red-800' : 'text-orange-800'
                                }`}>
                                  {section.item_name || `문항 ${section.question_id}`}
                                </h4>
                                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                  section.score === 0 ? 'bg-red-100 text-red-800' : 'bg-orange-100 text-orange-800'
                                }`}>
                                  점수: {section.score}
                                  {section.score === 25 && (
                                    <span className="ml-1 text-xs">(보통)</span>
                                  )}
                                </span>
                              </div>
                              <div className="text-xs text-gray-600 space-y-1">
                                <div>
                                  <span className="font-medium">분류:</span> {section.classification || '-'}
                                </div>
                                <div>
                                  <span className="font-medium">도메인:</span> {section.domain || '-'}
                                </div>
                                {/* 회사 응답결과 추가 */}
                                <div className="mt-2 p-2 bg-gray-50 rounded border">
                                  <span className="font-medium text-gray-700">응답결과:</span>
                                  <div className="text-gray-600 mt-1">
                                    {section.question_type === 'five_level' || section.question_type === 'three_level' ? (
                                      section.level_no ? `${section.level_no}단계` : '미응답'
                                    ) : section.question_type === 'five_choice' ? (
                                      section.choice_ids && section.choice_ids.length > 0 ? 
                                      `${section.choice_ids.length}개 선택` : '미응답'
                                    ) : '미응답'}
                                  </div>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-12">
                    <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">취약부문이 없습니다</h3>
                    <p className="text-gray-500">{rootCompany} 공급망에서 취약부문(자가진단 점수가 25점 이하인 문항)이 있는 회사가 없습니다.</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'assessment' && (
              <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 xl:grid-cols-3">
                {assessmentCompanies.length > 0 ? (
                  assessmentCompanies.map((company, index) => (
                    <div key={index} className="bg-white shadow rounded-lg overflow-hidden">
                      <div className="px-6 py-4 border-b border-gray-200">
                        <div className="flex justify-between items-start">
                          <h3 className="text-lg font-bold text-gray-900">{company.company_name}</h3>
                          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                            달성률: {company.achievement_rate}%
                          </span>
                        </div>
                        <div className="mt-2 space-y-1">
                          <p className="text-sm text-gray-500">
                            총 문항: {company.total_questions}개
                          </p>
                          <p className="text-sm text-gray-500">
                            총 점수: {company.total_score} / {company.max_possible_score}
                          </p>
                          <p className="text-sm text-gray-500">
                            취약 부문: {company.vulnerable_count}개
                          </p>
                          {company.last_assessment_date && (
                            <p className="text-sm text-gray-500">
                              마지막 진단: {new Date(company.last_assessment_date).toLocaleDateString()}
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="px-6 py-4">
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium text-gray-700">달성률</span>
                            <div className="flex items-center space-x-2">
                              <div className="w-24 bg-gray-200 rounded-full h-2">
                                <div 
                                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                                  style={{ width: `${company.achievement_rate}%` }}
                                ></div>
                              </div>
                              <span className="text-sm font-medium text-gray-900">{company.achievement_rate}%</span>
                            </div>
                          </div>
                          
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium text-gray-700">취약 부문</span>
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              company.vulnerable_count === 0 
                                ? 'bg-green-100 text-green-800' 
                                : company.vulnerable_count <= 3 
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {company.vulnerable_count}개
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-12">
                    <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Assessment 기업 목록이 없습니다</h3>
                    <p className="text-gray-500">Assessment 기업 목록을 불러오는데 실패했거나, 데이터가 없습니다.</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
