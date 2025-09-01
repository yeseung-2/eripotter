'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

// 인터페이스 정의
interface MappingResult {
  original_gas_name: string;
  original_amount: string;
  ai_mapped_name: string;
  ai_confidence: number;
  status: 'auto_mapped' | 'needs_review' | 'mapping_failed' | 'save_failed';
  certification_id?: number;
  error?: string;
  review_notes?: string;
}

interface NormalData {
  id: number;
  product_name: string;
  supplier: string;
  manufacturing_date: string;
  greenhouse_gas_emissions: Array<{
    materialName: string;
    amount: string;
    unit: string;
  }>;
}

function MappingEditContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const normalId = searchParams.get('normalId');
  
  const [normalData, setNormalData] = useState<NormalData | null>(null);
  const [mappingResults, setMappingResults] = useState<MappingResult[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [edits, setEdits] = useState<Record<number, Partial<MappingResult>>>({});

  useEffect(() => {
    if (normalId) {
      loadMappingData();
    }
  }, [normalId]);

  const loadMappingData = async () => {
    try {
      setIsLoading(true);
      
      // 원본 데이터 조회
      const normalResponse = await fetch(`/api/normal/substance/${normalId}`);
      if (normalResponse.ok) {
        const normalResult = await normalResponse.json();
        if (normalResult.status === 'success') {
          setNormalData(normalResult.data);
        }
      }

      // 매핑 결과 조회
      const mappingResponse = await fetch(`/api/normal/substance/mapping-results/${normalId}`);
      if (mappingResponse.ok) {
        const mappingResult = await mappingResponse.json();
        if (mappingResult.status === 'success') {
          setMappingResults(mappingResult.data);
        }
      }
    } catch (error) {
      console.error('데이터 로드 오류:', error);
      alert('데이터를 불러오는 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const updateMapping = (index: number, field: keyof MappingResult, value: any) => {
    setEdits(prev => ({
      ...prev,
      [index]: {
        ...prev[index],
        [field]: value
      }
    }));
  };

  const saveMappings = async () => {
    try {
      setIsSaving(true);
      
      const corrections = Object.entries(edits).map(([index, edit]) => ({
        certification_id: mappingResults[parseInt(index)].certification_id,
        correction_data: {
          final_mapped_name: edit.ai_mapped_name || mappingResults[parseInt(index)].ai_mapped_name,
          final_confidence: edit.ai_confidence || mappingResults[parseInt(index)].ai_confidence,
          review_status: 'user_reviewed',
          review_notes: edit.review_notes || ''
        },
        reviewed_by: 'user'
      }));

      const response = await fetch('/api/normal/substance/save-corrections', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          normal_id: normalId,
          corrections
        }),
      });

      const result = await response.json();
      
      if (result.status === 'success') {
        alert('매핑 수정이 완료되었습니다.');
        router.push('/data-upload');
      } else {
        alert(`저장 중 오류가 발생했습니다: ${result.message || result.error}`);
      }
    } catch (error) {
      console.error('저장 오류:', error);
      alert('저장 중 오류가 발생했습니다.');
    } finally {
      setIsSaving(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'auto_mapped':
        return 'bg-green-100 text-green-800';
      case 'needs_review':
        return 'bg-yellow-100 text-yellow-800';
      case 'mapping_failed':
        return 'bg-red-100 text-red-800';
      case 'save_failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'auto_mapped':
        return '자동 매핑 완료';
      case 'needs_review':
        return '검토 필요';
      case 'mapping_failed':
        return '매핑 실패';
      case 'save_failed':
        return '저장 실패';
      default:
        return status;
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">데이터를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (!normalData || !mappingResults.length) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">데이터를 찾을 수 없습니다.</p>
          <button
            onClick={() => router.push('/data-upload')}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            데이터 업로드로 돌아가기
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <button
                onClick={() => router.push('/data-upload')}
                className="mr-4 p-2 text-gray-400 hover:text-gray-600"
              >
                ←
              </button>
              <h1 className="text-2xl font-bold text-gray-900">매핑 결과 수정</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">Normal ID: {normalId}</span>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* 제품 정보 */}
        <div className="bg-white shadow rounded-lg mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">제품 정보</h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">제품명</label>
                <p className="mt-1 text-sm text-gray-900">{normalData.product_name}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">공급업체</label>
                <p className="mt-1 text-sm text-gray-900">{normalData.supplier}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">제조일자</label>
                <p className="mt-1 text-sm text-gray-900">{normalData.manufacturing_date}</p>
              </div>
            </div>
          </div>
        </div>

        {/* 매핑 결과 */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">온실가스 매핑 결과</h2>
            <p className="mt-1 text-sm text-gray-500">
              AI가 자동 매핑한 결과를 검토하고 필요시 수정하세요.
            </p>
          </div>
          <div className="p-6">
            <div className="space-y-6">
              {mappingResults.map((result, index) => (
                <div key={index} className="border rounded-lg p-6 bg-gray-50">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* 원본 정보 */}
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">원본 정보</h4>
                      <div className="space-y-2">
                        <div>
                          <label className="block text-sm font-medium text-gray-700">물질명</label>
                          <p className="text-sm text-gray-900">{result.original_gas_name}</p>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700">배출량</label>
                          <p className="text-sm text-gray-900">{result.original_amount}</p>
                        </div>
                      </div>
                    </div>

                    {/* AI 매핑 결과 */}
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">AI 매핑 결과</h4>
                      <div className="space-y-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-700">매핑된 물질명</label>
                          <input
                            type="text"
                            value={edits[index]?.ai_mapped_name || result.ai_mapped_name || ''}
                            onChange={(e) => updateMapping(index, 'ai_mapped_name', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="매핑된 물질명을 입력하세요"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700">신뢰도</label>
                          <input
                            type="number"
                            min="0"
                            max="1"
                            step="0.01"
                            value={edits[index]?.ai_confidence || result.ai_confidence || 0}
                            onChange={(e) => updateMapping(index, 'ai_confidence', parseFloat(e.target.value))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700">상태</label>
                          <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(result.status)}`}>
                            {getStatusText(result.status)}
                          </span>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700">검토 노트</label>
                          <textarea
                            value={edits[index]?.review_notes || ''}
                            onChange={(e) => updateMapping(index, 'review_notes', e.target.value)}
                            rows={2}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="검토 노트를 입력하세요"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {result.error && (
                    <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                      <p className="text-sm text-red-800">오류: {result.error}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 액션 버튼 */}
        <div className="flex justify-end space-x-4 mt-6">
          <button
            onClick={() => router.push('/data-upload')}
            className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500"
          >
            취소
          </button>
          <button
            onClick={saveMappings}
            disabled={isSaving}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSaving ? '저장 중...' : '수정사항 저장'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function MappingEditPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">페이지를 불러오는 중...</p>
        </div>
      </div>
    }>
      <MappingEditContent />
    </Suspense>
  );
}
