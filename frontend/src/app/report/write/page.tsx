"use client";

import { useEffect, useMemo, useState } from "react";
import { generateDraft, saveIndicator, getIndicatorWithFields, generateInputFields } from "@/lib/api";
import type { Indicator, IndicatorInputFieldResponse, IndicatorDraftRequest } from "@/types/report";
import { normalizeFields, type FormField } from "@/lib/form";
import Stepper from "@/components/ui/Stepper";
import IndicatorPicker from "@/components/ui/IndicatorPicker";
import RecommendedFields from "@/components/ui/RecommendedFields";
import InputFieldsForm from "@/components/ui/InputFieldsForm";
import DraftViewer from "@/components/ui/DraftViewer";


export default function ReportWritePage() {
  const [step, setStep] = useState(1);
  const [companyName, setCompanyName] = useState("");
  const [picked, setPicked] = useState<Indicator | null>(null);
  const [fieldsInfo, setFieldsInfo] = useState<IndicatorInputFieldResponse | null>(null);
  const [ragRequired, setRagRequired] = useState<any[]>([]);
  const [fields, setFields] = useState<FormField[]>([]);
  const [inputs, setInputs] = useState<Record<string, any>>({});
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState(false);

  useEffect(() => {
    (async () => {
      if (!picked) return;
      setLoading(true);
      try {
        const info = await getIndicatorWithFields(picked.indicator_id);
        setFieldsInfo(info);
        const rag = await generateInputFields(picked.indicator_id);
        setRagRequired(rag.required_fields || []);
        const normalized = normalizeFields(info, rag.required_fields);
        setFields(normalized);
        setStep(2);
      } finally {
        setLoading(false);
      }
    })();
  }, [picked]);

  const disabledGen = useMemo(() => !picked || !companyName || loading, [picked, companyName, loading]);

  const onGenerate = async () => {
    if (!picked) return;
    setLoading(true);
    try {
      const body: IndicatorDraftRequest = { company_name: companyName, inputs };
      const html = await generateDraft(picked.indicator_id, body);
      setDraft(html);
      setStep(3);
    } catch (error) {
      console.error("초안 생성 실패:", error);
      alert("초안 생성에 실패했습니다. API 서버가 실행 중인지 확인해주세요.");
    } finally {
      setLoading(false);
    }
  };

  const onSave = async () => {
    if (!picked) return;
    setLoading(true);
    try {
      const ok = await saveIndicator(picked.indicator_id, { company_name: companyName, inputs });
      alert(ok ? "임시저장 완료!" : "임시저장 실패");
      if (ok) setStep(4);
    } catch (error) {
      console.error("임시저장 실패:", error);
      alert("임시저장에 실패했습니다. API 서버가 실행 중인지 확인해주세요.");
    } finally {
      setLoading(false);
    }
  };

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
        <h1 className="text-2xl font-bold">보고서 작성</h1>
        <Stepper step={step} />
      </div>

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
          <h2 className="text-lg font-semibold mb-2">지표 선택</h2>
          <IndicatorPicker onPick={setPicked} onError={setApiError} />
        </div>
      </section>

      {/* 2. 입력 필드 */}
      {picked && (
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-3">
            <h2 className="text-lg font-semibold">데이터 입력</h2>
            {loading ? (
              <div className="p-4">필드 로딩중…</div>
            ) : (
              <InputFieldsForm fields={fields} value={inputs} onChange={setInputs} />
            )}
          </div>
          <div className="lg:col-span-1 space-y-3">
            <h3 className="text-sm font-semibold text-slate-700">추천 입력 항목 (RAG)</h3>
            <RecommendedFields data={fieldsInfo} />
            {!!ragRequired?.length && (
              <div className="text-xs text-slate-600 border rounded p-3 bg-white">
                <div className="font-semibold mb-1">LLM 필요항목(해석):</div>
                <ul className="list-disc pl-5 space-y-1">
                  {ragRequired.map((r, i) => (
                    <li key={i}>{r["항목"] || JSON.stringify(r)}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </section>
      )}

      {/* 3. 생성 & 초안 */}
      {picked && (
        <section className="space-y-3">
          <div className="flex gap-2">
            <button
              onClick={onGenerate}
              disabled={disabledGen}
              className={`px-4 py-2 rounded text-white ${disabledGen ? "bg-slate-300" : "bg-blue-600 hover:bg-blue-700"}`}
            >
              초안 생성
            </button>
            <button
              onClick={onSave}
              disabled={!draft || loading}
              className={`px-4 py-2 rounded border ${!draft || loading ? "bg-white text-slate-300 border-slate-200" : "bg-white text-slate-700 hover:bg-slate-50 border-slate-300"}`}
            >
              임시저장
            </button>
          </div>

          <DraftViewer html={draft} />
        </section>
      )}
    </div>
  );
}
