'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

// === ADD: API base util ===
const BASE = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "";
const join = (p: string) => (BASE ? `${BASE}${p}` : p);
// ==========================

interface ReportData {
  id?: string;
  company_name: string;
  report_type: string;
  topic: string;
  description: string;
  status: string;
  created_at?: string;
  updated_at?: string;
}

export default function ReportDetailPage() {
  const router = useRouter();
  const params = useParams();
  const reportId = params.id as string;
  
  const [isLoading, setIsLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [editData, setEditData] = useState<ReportData | null>(null);

  useEffect(() => {
    if (reportId && reportId !== 'detail') {
      fetchReportData();
    } else {
      setIsLoading(false);
    }
  }, [reportId]);

  const fetchReportData = async () => {
    try {
      // 실제 API 호출 대신 임시 데이터 사용 (API 엔드포인트가 완성되면 교체)
      const mockData: ReportData = {
        id: reportId,
        company_name: '샘플 회사',
        report_type: 'esg',
        topic: '2024년 ESG 성과 보고서',
        description: '환경, 사회, 지배구조 측면에서의 성과를 종합적으로 분석한 보고서입니다.',
        status: 'draft',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      
      setReportData(mockData);
      setEditData(mockData);
    } catch (error) {
      console.error('보고서 데이터 로드 실패:', error);
      alert('보고서 데이터를 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditData(reportData);
  };

  const handleSave = async () => {
    if (!editData) return;

    setIsSaving(true);
    try {
      // 실제 API 호출 대신 임시 처리
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setReportData(editData);
      setIsEditing(false);
      alert('보고서가 성공적으로 저장되었습니다!');
    } catch (error) {
      console.error('보고서 저장 실패:', error);
      alert('보고서 저장에 실패했습니다.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleComplete = async () => {
    if (!reportData) return;

    if (confirm('보고서를 완료하시겠습니까? 완료 후에는 수정이 제한됩니다.')) {
      try {
        // 실제 API 호출 대신 임시 처리
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        setReportData(prev => prev ? { ...prev, status: 'completed' } : null);
        alert('보고서가 완료되었습니다!');
      } catch (error) {
        console.error('보고서 완료 실패:', error);
        alert('보고서 완료에 실패했습니다.');
      }
    }
  };

  const handleDelete = async () => {
    if (!reportData) return;

    if (confirm('정말로 이 보고서를 삭제하시겠습니까?')) {
      try {
        // 실제 API 호출 대신 임시 처리
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        alert('보고서가 삭제되었습니다.');
        router.push('/report/create');
      } catch (error) {
        console.error('보고서 삭제 실패:', error);
        alert('보고서 삭제에 실패했습니다.');
      }
    }
  };

  const handleInputChange = (field: keyof ReportData, value: string) => {
    if (!editData) return;
    
    setEditData(prev => prev ? {
      ...prev,
      [field]: value
    } : null);
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

  if (!reportData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
        <Card className="w-full max-w-md bg-white rounded-3xl shadow-2xl px-8 py-12 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">보고서를 찾을 수 없습니다</h2>
          <p className="text-gray-600 mb-6">요청하신 보고서가 존재하지 않거나 삭제되었습니다.</p>
          <Button
            onClick={() => router.push('/report/create')}
            className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl"
          >
            새 보고서 작성
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-3xl font-bold text-gray-900">보고서 상세</h1>
            <div className="flex space-x-2">
              {!isEditing && reportData.status === 'draft' && (
                <>
                  <Button
                    onClick={handleEdit}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl"
                  >
                    편집
                  </Button>
                  <Button
                    onClick={handleComplete}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-xl"
                  >
                    완료
                  </Button>
                </>
              )}
              {isEditing && (
                <>
                  <Button
                    onClick={handleCancel}
                    className="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-xl"
                  >
                    취소
                  </Button>
                  <Button
                    onClick={handleSave}
                    disabled={isSaving}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl disabled:opacity-50"
                  >
                    {isSaving ? '저장 중...' : '저장'}
                  </Button>
                </>
              )}
              <Button
                onClick={() => router.push('/report/create')}
                className="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-xl"
              >
                목록
              </Button>
            </div>
          </div>
          
          {/* Status Badge */}
          <div className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
            {reportData.status === 'draft' ? '초안' : '완료'}
          </div>
        </div>

        {/* Report Content */}
        <Card className="bg-white rounded-3xl shadow-2xl p-8">
          <div className="space-y-6">
            {/* Company Name */}
            <div>
              <Label className="text-sm font-medium text-gray-700">회사명</Label>
              {isEditing ? (
                <Input
                  value={editData?.company_name || ''}
                  onChange={(e) => handleInputChange('company_name', e.target.value)}
                  className="mt-1 w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              ) : (
                <p className="mt-1 text-lg text-gray-900">{reportData.company_name}</p>
              )}
            </div>

            {/* Report Type */}
            <div>
              <Label className="text-sm font-medium text-gray-700">보고서 유형</Label>
              {isEditing ? (
                <Input
                  value={editData?.report_type || ''}
                  onChange={(e) => handleInputChange('report_type', e.target.value)}
                  className="mt-1 w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              ) : (
                <p className="mt-1 text-lg text-gray-900">{reportData.report_type}</p>
              )}
            </div>

            {/* Topic */}
            <div>
              <Label className="text-sm font-medium text-gray-700">보고서 주제</Label>
              {isEditing ? (
                <Input
                  value={editData?.topic || ''}
                  onChange={(e) => handleInputChange('topic', e.target.value)}
                  className="mt-1 w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              ) : (
                <p className="mt-1 text-lg text-gray-900">{reportData.topic}</p>
              )}
            </div>

            {/* Description */}
            <div>
              <Label className="text-sm font-medium text-gray-700">설명</Label>
              {isEditing ? (
                <Textarea
                  value={editData?.description || ''}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  className="mt-1 w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-[100px]"
                  rows={4}
                />
              ) : (
                <p className="mt-1 text-gray-700">{reportData.description}</p>
              )}
            </div>

            {/* Metadata */}
            <div className="pt-6 border-t border-gray-200">
              <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                <div>
                  <span className="font-medium">생성일:</span> {new Date(reportData.created_at || '').toLocaleDateString()}
                </div>
                <div>
                  <span className="font-medium">수정일:</span> {new Date(reportData.updated_at || '').toLocaleDateString()}
                </div>
              </div>
            </div>
          </div>
        </Card>

        {/* Delete Button */}
        {reportData.status === 'draft' && (
          <div className="mt-6 text-center">
            <Button
              onClick={handleDelete}
              className="px-6 py-2 bg-red-600 hover:bg-red-700 text-white rounded-xl"
            >
              보고서 삭제
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
