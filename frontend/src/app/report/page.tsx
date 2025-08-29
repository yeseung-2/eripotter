'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

// === ADD: API base util ===
const BASE = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "";
const join = (p: string) => (BASE ? `${BASE}${p}` : p);
// ==========================

interface ReportItem {
  id: string;
  company_name: string;
  report_type: string;
  topic: string;
  description: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export default function ReportListPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [reports, setReports] = useState<ReportItem[]>([]);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      // 실제 API 호출 대신 임시 데이터 사용
      const mockReports: ReportItem[] = [
        {
          id: '1',
          company_name: '삼성전자',
          report_type: 'esg',
          topic: '2024년 ESG 성과 보고서',
          description: '환경, 사회, 지배구조 측면에서의 성과를 종합적으로 분석한 보고서입니다.',
          status: 'draft',
          created_at: '2024-01-15T10:30:00Z',
          updated_at: '2024-01-20T14:45:00Z'
        },
        {
          id: '2',
          company_name: 'LG화학',
          report_type: 'sustainability',
          topic: '2024년 지속가능성 보고서',
          description: '지속가능한 발전을 위한 노력과 성과를 담은 보고서입니다.',
          status: 'completed',
          created_at: '2024-01-10T09:15:00Z',
          updated_at: '2024-01-18T16:20:00Z'
        },
        {
          id: '3',
          company_name: 'SK하이닉스',
          report_type: 'csr',
          topic: '2024년 CSR 활동 보고서',
          description: '기업의 사회적 책임 활동과 성과를 정리한 보고서입니다.',
          status: 'draft',
          created_at: '2024-01-12T11:00:00Z',
          updated_at: '2024-01-19T13:30:00Z'
        }
      ];
      
      setReports(mockReports);
    } catch (error) {
      console.error('보고서 목록 로드 실패:', error);
      alert('보고서 목록을 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateReport = () => {
    router.push('/report/write');
  };

  const handleViewReport = (reportId: string) => {
    router.push(`/report/${reportId}`);
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      draft: { label: '초안', className: 'bg-yellow-100 text-yellow-800' },
      completed: { label: '완료', className: 'bg-green-100 text-green-800' },
      in_progress: { label: '진행중', className: 'bg-blue-100 text-blue-800' }
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.draft;
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.className}`}>
        {config.label}
      </span>
    );
  };

  const getReportTypeLabel = (type: string) => {
    const typeLabels: { [key: string]: string } = {
      esg: 'ESG 보고서',
      sustainability: '지속가능성 보고서',
      csr: 'CSR 보고서',
      annual: '연간 보고서'
    };
    
    return typeLabels[type] || type;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">로딩 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-3xl font-bold text-gray-900">보고서 목록</h1>
            <Button
              onClick={handleCreateReport}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium"
            >
              새 보고서 작성
            </Button>
          </div>
          <p className="text-gray-600">
            작성한 보고서들을 관리하고 확인할 수 있습니다.
          </p>
        </div>

        {/* Reports Grid */}
        {reports.length === 0 ? (
          <Card className="bg-white rounded-3xl shadow-2xl p-12 text-center">
            <div className="mb-6">
              <svg className="w-16 h-16 text-gray-400 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">아직 작성된 보고서가 없습니다</h3>
            <p className="text-gray-600 mb-6">첫 번째 보고서를 작성해보세요!</p>
            <Button
              onClick={handleCreateReport}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium"
            >
              보고서 작성하기
            </Button>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {reports.map((report) => (
              <Card
                key={report.id}
                className="bg-white rounded-3xl shadow-2xl p-6 hover:shadow-3xl transition-shadow duration-300 cursor-pointer"
                onClick={() => handleViewReport(report.id)}
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1 line-clamp-2">
                      {report.topic}
                    </h3>
                    <p className="text-sm text-gray-600 mb-2">
                      {report.company_name}
                    </p>
                  </div>
                  {getStatusBadge(report.status)}
                </div>

                {/* Content */}
                <div className="mb-4">
                  <p className="text-sm text-gray-700 line-clamp-3">
                    {report.description}
                  </p>
                </div>

                {/* Footer */}
                <div className="border-t border-gray-100 pt-4">
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>{getReportTypeLabel(report.report_type)}</span>
                    <span>{new Date(report.updated_at).toLocaleDateString()}</span>
                  </div>
                </div>

                {/* Hover Effect */}
                <div className="mt-4 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                  <Button
                    className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleViewReport(report.id);
                    }}
                  >
                    상세보기
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Statistics */}
        {reports.length > 0 && (
          <div className="mt-8">
            <Card className="bg-white rounded-3xl shadow-2xl p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">통계</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{reports.length}</div>
                  <div className="text-sm text-gray-600">전체 보고서</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-yellow-600">
                    {reports.filter(r => r.status === 'draft').length}
                  </div>
                  <div className="text-sm text-gray-600">초안</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {reports.filter(r => r.status === 'completed').length}
                  </div>
                  <div className="text-sm text-gray-600">완료</div>
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
