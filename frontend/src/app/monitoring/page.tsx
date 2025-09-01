"use client";

import { useState, useEffect } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';

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

// ===== Monitoring Page Component =====

export default function MonitoringPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  const [vulnerableCompanies, setVulnerableCompanies] = useState<FlattenedCompany[]>([]);

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
    const response = await fetch(`http://localhost:8004/monitoring/supply-chain/vulnerabilities`);
    if (!response.ok) throw new Error('공급망 취약부문 조회 실패');
    return response.json();
  };

  // 페이지 로드 시 자동으로 데이터 조회
  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      setError('');

      try {
        const data = await fetchSupplyChainVulnerabilities();
        const flattenedCompanies = flattenSupplyChainTree(data.supply_chain_tree);
        setVulnerableCompanies(flattenedCompanies);
      } catch (err) {
        setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

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
        {/* 페이지 제목 */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            {rootCompany} 공급망 취약부문 현황
          </h2>
          <p className="text-gray-600">
            공급망 내 취약부문이 있는 회사들을 표시합니다.
          </p>
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
            {vulnerableCompanies.length > 0 ? (
              <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 xl:grid-cols-3">
                {vulnerableCompanies.map((company, index) => (
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
                          Tier 1: {company.tier1s.join(', ')}
                        </p>
                      )}
                    </div>
                    <div className="px-6 py-4">
                      <div className="space-y-3">
                        {company.vulnerable_sections.map((section) => (
                          <div key={section.id} className="border border-red-200 bg-red-50 rounded-lg p-3">
                            <div className="flex justify-between items-start mb-2">
                              <h4 className="font-semibold text-red-800 text-sm">
                                {section.item_name || `문항 ${section.question_id}`}
                              </h4>
                              <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                                점수: {section.score}
                              </span>
                            </div>
                            <div className="text-xs text-gray-600 space-y-1">
                              <div>
                                <span className="font-medium">분류:</span> {section.classification || '-'}
                              </div>
                              <div>
                                <span className="font-medium">도메인:</span> {section.domain || '-'}
                              </div>
                              {section.item_desc && (
                                <div className="text-gray-500 mt-1">
                                  {section.item_desc}
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h3 className="text-lg font-medium text-gray-900 mb-2">취약부문이 없습니다</h3>
                <p className="text-gray-500">{rootCompany} 공급망에서 취약부문(score=0)이 있는 회사가 없습니다.</p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
