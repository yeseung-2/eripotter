'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";

// === ADD: API base util ===
const BASE = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "";
const join = (p: string) => (BASE ? `${BASE}${p}` : p);
// ==========================

interface ReportFormData {
  company_name: string;
  report_type: string;
  topic: string;
  description: string;
}

export default function ReportCreatePage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState<ReportFormData>({
    company_name: '',
    report_type: '',
    topic: '',
    description: ''
  });

  const reportTypes = [
    { value: 'esg', label: 'ESG 보고서' },
    { value: 'sustainability', label: '지속가능성 보고서' },
    { value: 'csr', label: 'CSR 보고서' },
    { value: 'annual', label: '연간 보고서' }
  ];

  const handleInputChange = (field: keyof ReportFormData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.company_name || !formData.report_type || !formData.topic) {
      alert('필수 항목을 모두 입력해주세요.');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(join('/reports'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          company_name: formData.company_name,
          report_type: formData.report_type,
          topic: formData.topic,
          description: formData.description,
          status: 'draft'
        }),
      });

      if (response.ok) {
        const result = await response.json();
        alert('보고서가 성공적으로 생성되었습니다!');
        // 생성된 보고서 상세 페이지로 이동
        router.push(`/report/${result.report_id || 'detail'}`);
      } else {
        const errorData = await response.json();
        alert(`보고서 생성 실패: ${errorData.message || '알 수 없는 오류가 발생했습니다.'}`);
      }
    } catch (error) {
      console.error('보고서 생성 중 오류:', error);
      alert('보고서 생성 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBack = () => {
    router.back();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl bg-white rounded-3xl shadow-2xl px-8 py-12">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 tracking-tight mb-2">
            보고서 작성
          </h1>
          <p className="text-gray-600">
            새로운 ESG 보고서를 작성하세요
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Company Name */}
          <div className="space-y-2">
            <Label htmlFor="company_name" className="text-sm font-medium text-gray-700">
              회사명 *
            </Label>
            <Input
              id="company_name"
              type="text"
              placeholder="회사명을 입력하세요"
              value={formData.company_name}
              onChange={(e) => handleInputChange('company_name', e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          {/* Report Type */}
          <div className="space-y-2">
            <Label htmlFor="report_type" className="text-sm font-medium text-gray-700">
              보고서 유형 *
            </Label>
            <Select
              value={formData.report_type}
              onValueChange={(value) => handleInputChange('report_type', value)}
            >
              <SelectTrigger className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                <SelectValue placeholder="보고서 유형을 선택하세요" />
              </SelectTrigger>
              <SelectContent>
                {reportTypes.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Topic */}
          <div className="space-y-2">
            <Label htmlFor="topic" className="text-sm font-medium text-gray-700">
              보고서 주제 *
            </Label>
            <Input
              id="topic"
              type="text"
              placeholder="보고서 주제를 입력하세요 (예: 2024년 ESG 성과 보고서)"
              value={formData.topic}
              onChange={(e) => handleInputChange('topic', e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description" className="text-sm font-medium text-gray-700">
              보고서 설명
            </Label>
            <Textarea
              id="description"
              placeholder="보고서에 대한 간단한 설명을 입력하세요"
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-[100px]"
              rows={4}
            />
          </div>

          {/* Buttons */}
          <div className="flex space-x-4 pt-6">
            <Button
              type="button"
              onClick={handleBack}
              className="flex-1 py-3 bg-gray-500 hover:bg-gray-600 text-white rounded-xl font-medium"
            >
              뒤로가기
            </Button>
            <Button
              type="submit"
              disabled={isLoading}
              className="flex-1 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium disabled:opacity-50"
            >
              {isLoading ? '생성 중...' : '보고서 생성'}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
