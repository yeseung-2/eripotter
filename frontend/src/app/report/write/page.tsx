"use client";

import { useEffect, useMemo, useState } from "react";
import { getAllIndicators } from "@/lib/api";
import { 
  getInputFields, 
  generateDraft 
} from "@/lib/reportApi";
import type { Indicator } from "@/types/report";
import { normalizeFields, type FormField } from "@/lib/form";
import Stepper from "@/components/ui/Stepper";
import IndicatorPicker from "@/components/ui/IndicatorPicker";
import InputFieldsForm from "@/components/ui/InputFieldsForm";
import DraftViewer from "@/components/ui/DraftViewer";

interface ProcessedIndicator {
  indicator: Indicator;
  inputFields: any;
  inputs: Record<string, any>;
  draft: string;
  status: 'pending' | 'input-fields' | 'data-input' | 'draft-generated' | 'completed';
}

export default function ReportWritePage() {
  const [step, setStep] = useState(1);
  const [companyName, setCompanyName] = useState("");
  const [indicators, setIndicators] = useState<Indicator[]>([]);
  const [processedIndicators, setProcessedIndicators] = useState<ProcessedIndicator[]>([]);
  const [currentIndicatorId, setCurrentIndicatorId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState(false);

  // 지표 목록 로드
  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const response = await getAllIndicators();
        if (response.success) {
          setIndicators(response.indicators);
        } else {
          setApiError(true);
        }
      } catch (error) {
        console.error("지표 목록 로드 실패:", error);
        setApiError(true);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // 지표 선택 시 처리
  const handleIndicatorSelect = async (indicator: Indicator) => {
    setLoading(true);
    try {
      // 이미 처리된 지표인지 확인
      const existing = processedIndicators.find(p => p.indicator.indicator_id === indicator.indicator_id);
      if (existing) {
        setCurrentIndicatorId(indicator.indicator_id);
        setStep(2);
        return;
      }

      // 새로운 지표 처리 시작
      const newProcessedIndicator: ProcessedIndicator = {
        indicator,
        inputFields: {},
        inputs: {},
        draft: "",
        status: 'pending'
      };

      setProcessedIndicators(prev => [...prev, newProcessedIndicator]);
      setCurrentIndicatorId(indicator.indicator_id);
      setStep(2);

      // 입력필드 생성
      await generateInputFieldsForIndicator(indicator.indicator_id);
    } catch (error) {
      console.error("지표 선택 처리 실패:", error);
      alert("지표 처리 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // 입력필드 생성
  const generateInputFieldsForIndicator = async (indicatorId: string) => {
    try {
      const response = await getInputFields(indicatorId);
      setProcessedIndicators(prev => 
        prev.map(p => 
          p.indicator.indicator_id === indicatorId 
            ? { ...p, inputFields: response.required_fields || {}, status: 'input-fields' }
            : p
        )
      );
    } catch (error) {
      console.error("입력필드 생성 실패:", error);
      // 기본 입력필드 설정
      setProcessedIndicators(prev => 
        prev.map(p => 
          p.indicator.indicator_id === indicatorId 
            ? { 
                ...p, 
                inputFields: { company_data: { type: "text", label: "회사 데이터", required: true } },
                status: 'input-fields' 
              }
            : p
        )
      );
    }
  };

  // 데이터 입력 처리
  const handleInputChange = (indicatorId: string, inputs: Record<string, any>) => {
    setProcessedIndicators(prev => 
      prev.map(p => 
        p.indicator.indicator_id === indicatorId 
          ? { ...p, inputs, status: 'data-input' }
          : p
      )
    );
  };

  // 초안 생성
  const generateDraftForIndicator = async (indicatorId: string) => {
    const indicator = processedIndicators.find(p => p.indicator.indicator_id === indicatorId);
    if (!indicator || !companyName) return;

    setLoading(true);
    try {
      const response = await generateDraft(indicatorId, companyName, indicator.inputs);
      
      setProcessedIndicators(prev => 
        prev.map(p => 
          p.indicator.indicator_id === indicatorId 
            ? { ...p, draft: response, status: 'draft-generated' }
            : p
        )
      );
      setStep(3);
    } catch (error) {
      console.error("초안 생성 실패:", error);
      alert("초안 생성 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // 현재 처리 중인 지표
  const currentIndicator = processedIndicators.find(p => p.indicator.indicator_id === currentIndicatorId);

  // 완료된 지표 수
  const completedCount = processedIndicators.filter(p => p.status === 'draft-generated').length;

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {apiError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">API 서버 연결 실패</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>보고서 서비스 API 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.</p>
              </div>
            </div>
          </div>
        </div>
      )}
      
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">보고서 작성 (개별 지표 처리)</h1>
        <Stepper step={step} />
      </div>

      {/* 진행 상황 표시 */}
      {processedIndicators.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-blue-800 mb-2">처리 진행 상황</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
            <div>총 지표: {indicators.length}개</div>
            <div>처리 중: {processedIndicators.length}개</div>
            <div>완료: {completedCount}개</div>
            <div>남은 지표: {indicators.length - completedCount}개</div>
          </div>
        </div>
      )}

      {/* 1. 지표 선택 */}
      <section className="space-y-3">
        <label className="block text-sm font-medium">회사명</label>
        <input
          className="border rounded px-3 py-2 w-80"
          placeholder="예) 에코머티리얼즈"
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
        />
        <div className="mt-4">
          <h2 className="text-lg font-semibold mb-2">지표 선택 (개별 처리)</h2>
          {loading ? (
            <div className="p-4">지표 목록 로딩중…</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {indicators.map((indicator) => {
                const processed = processedIndicators.find(p => p.indicator.indicator_id === indicator.indicator_id);
                const isCurrent = currentIndicatorId === indicator.indicator_id;
                
                return (
                  <div 
                    key={indicator.indicator_id}
                    className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                      isCurrent 
                        ? 'border-blue-500 bg-blue-50' 
                        : processed 
                          ? 'border-green-300 bg-green-50' 
                          : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => handleIndicatorSelect(indicator)}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-sm font-medium text-gray-900">{indicator.indicator_id}</span>
                      {processed && (
                        <span className={`text-xs px-2 py-1 rounded ${
                          processed.status === 'draft-generated' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {processed.status === 'draft-generated' ? '완료' : '진행중'}
                        </span>
                      )}
                    </div>
                    <h3 className="text-sm font-medium mb-1">{indicator.title}</h3>
                    <p className="text-xs text-gray-500">{indicator.category}</p>
                    {processed && (
                      <div className="mt-2 text-xs text-gray-600">
                        <div>입력필드: {Object.keys(processed.inputFields).length}개</div>
                        {processed.draft && <div>초안: 생성됨</div>}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </section>

      {/* 2. 현재 지표 처리 */}
      {currentIndicator && (
        <section className="space-y-4">
          <div className="border-t pt-6">
            <h2 className="text-lg font-semibold mb-4">
              현재 처리 중: {currentIndicator.indicator.indicator_id} - {currentIndicator.indicator.title}
            </h2>
            
            {/* 입력 필드 */}
            {currentIndicator.status === 'input-fields' && (
              <div className="space-y-4">
                <h3 className="text-md font-medium">데이터 입력</h3>
                <InputFieldsForm 
                  fields={Object.entries(currentIndicator.inputFields).map(([key, field]: [string, any]) => ({
                    key: key,
                    label: field.label || key,
                    type: field.type || 'text',
                    required: field.required || false,
                    description: field.description || ''
                  }))}
                  value={currentIndicator.inputs}
                  onChange={(inputs) => handleInputChange(currentIndicator.indicator.indicator_id, inputs)}
                />
                <button
                  onClick={() => generateDraftForIndicator(currentIndicator.indicator.indicator_id)}
                  disabled={!companyName || loading}
                  className={`px-4 py-2 rounded text-white ${
                    !companyName || loading 
                      ? "bg-slate-300" 
                      : "bg-blue-600 hover:bg-blue-700"
                  }`}
                >
                  {loading ? "초안 생성 중..." : "초안 생성"}
                </button>
              </div>
            )}

            {/* 초안 표시 */}
            {currentIndicator.status === 'draft-generated' && currentIndicator.draft && (
              <div className="space-y-4">
                <h3 className="text-md font-medium">생성된 초안</h3>
                <DraftViewer html={currentIndicator.draft} />
                <div className="flex gap-2">
                  <button
                    onClick={() => setStep(1)}
                    className="px-4 py-2 rounded border border-gray-300 bg-white hover:bg-gray-50"
                  >
                    다음 지표 선택
                  </button>
                  <button
                    onClick={() => setStep(4)}
                    className="px-4 py-2 rounded bg-green-600 text-white hover:bg-green-700"
                  >
                    모든 지표 완료
                  </button>
                </div>
              </div>
            )}
          </div>
        </section>
      )}

      {/* 3. 완료된 지표 목록 */}
      {completedCount > 0 && (
        <section className="space-y-4">
          <h2 className="text-lg font-semibold">완료된 지표 목록</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {processedIndicators
              .filter(p => p.status === 'draft-generated')
              .map((processed) => (
                <div key={processed.indicator.indicator_id} className="border border-green-200 rounded-lg p-4 bg-green-50">
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-sm font-medium">{processed.indicator.indicator_id}</span>
                    <span className="text-xs px-2 py-1 rounded bg-green-100 text-green-800">완료</span>
                  </div>
                  <h3 className="text-sm font-medium mb-1">{processed.indicator.title}</h3>
                  <p className="text-xs text-gray-500">{processed.indicator.category}</p>
                  <div className="mt-2 text-xs text-gray-600">
                    <div>입력 데이터: {Object.keys(processed.inputs).length}개</div>
                    <div>초안 길이: {processed.draft.length}자</div>
                  </div>
                </div>
              ))}
          </div>
        </section>
      )}
    </div>
  );
}
