'use client';

import { useEffect, useMemo, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

// ----- Types -----
type StatusKey =
  | 'auto_mapped'
  | 'needs_review'
  | 'mapping_failed'
  | 'save_failed'
  | 'no_model';

interface MappingResult {
  original_gas_name: string;
  original_amount: string;
  ai_mapped_name: string | null;
  ai_confidence: number | null;
  status: StatusKey;
  certification_id?: number;
  error?: string;
  review_notes?: string | null;
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

// ----- UI helpers -----
const STATUS_META: Record<
  StatusKey,
  { text: string; chip: string; ring: string }
> = {
  auto_mapped: {
    text: '자동 매핑 완료',
    chip: 'bg-green-100 text-green-700',
    ring: 'ring-1 ring-green-200',
  },
  needs_review: {
    text: '검토 필요',
    chip: 'bg-yellow-100 text-yellow-700',
    ring: 'ring-1 ring-yellow-200',
  },
  mapping_failed: {
    text: '매핑 실패',
    chip: 'bg-red-100 text-red-700',
    ring: 'ring-1 ring-red-200',
  },
  save_failed: {
    text: '저장 실패',
    chip: 'bg-red-100 text-red-700',
    ring: 'ring-1 ring-red-200',
  },
  no_model: {
    text: '모델 없음',
    chip: 'bg-orange-100 text-orange-700',
    ring: 'ring-1 ring-orange-200',
  },
};

function toFixedOrDash(n: number | null | undefined, digits = 2) {
  if (n === null || n === undefined || Number.isNaN(n)) return '-';
  return Number(n).toFixed(digits);
}

// ----- Data normalization (accepts snake_case/camelCase) -----
function normalizeNormalData(data: any): NormalData {
  return {
    id: data.id ?? data.normal_id ?? 0,
    product_name: data.product_name ?? data.productName ?? '',
    supplier: data.supplier ?? data.supplier_name ?? '',
    manufacturing_date: data.manufacturing_date ?? data.manufacturingDate ?? '',
    greenhouse_gas_emissions:
      data.greenhouse_gas_emissions ??
      data.greenhouseGasEmissions ??
      [],
  };
}

function normalizeMappingResults(arr: any[]): MappingResult[] {
  return (arr ?? []).map((r) => ({
    original_gas_name:
      r.original_gas_name ?? r.originalGasName ?? r.original ?? '',
    original_amount:
      r.original_amount ?? r.originalAmount ?? r.amount ?? '',
    ai_mapped_name:
      r.ai_mapped_name ?? r.aiMappedName ?? r.mapped ?? null,
    ai_confidence:
      r.ai_confidence ?? r.aiConfidence ?? r.confidence ?? null,
    status: (r.status ??
      r.mapping_status ??
      'needs_review') as StatusKey,
    certification_id: r.certification_id ?? r.certificationId,
    error: r.error,
    review_notes: r.review_notes ?? r.reviewNotes ?? null,
  }));
}

// ----- Page -----
function MappingEditContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const normalId = searchParams.get('normalId');

  const [normalData, setNormalData] = useState<NormalData | null>(null);
  const [mappingResults, setMappingResults] = useState<MappingResult[]>([]);
  const [filtered, setFiltered] = useState<MappingResult[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // edits: key = row index, value = partial changes
  const [edits, setEdits] = useState<Record<number, Partial<MappingResult>>>(
    {}
  );

  // UI controls
  const [statusFilter, setStatusFilter] = useState<
    'all' | StatusKey
  >('all');
  const [query, setQuery] = useState('');

  // ----- Load -----
  useEffect(() => {
    if (!normalId) return;
    (async () => {
      try {
        setIsLoading(true);
        setErrorMessage(null);

        // 원본 데이터
        const nRes = await fetch(`/api/normal/substance/${normalId}`);
        if (!nRes.ok) throw new Error('원본 데이터 응답 오류');
        const nJson = await nRes.json();
        if (nJson.status !== 'success') {
          throw new Error(nJson.message || '원본 데이터를 불러올 수 없습니다.');
        }
        setNormalData(normalizeNormalData(nJson.data));

        // 매핑 결과
        const mRes = await fetch(
          `/api/normal/substance/mapping-results/${normalId}`
        );
        if (!mRes.ok) throw new Error('매핑 결과 응답 오류');
        const mJson = await mRes.json();
        if (mJson.status !== 'success') {
          throw new Error(
            mJson.message || '매핑 결과를 불러올 수 없습니다.'
          );
        }
        const list = normalizeMappingResults(mJson.data);
        setMappingResults(list);
      } catch (e: any) {
        console.error(e);
        setErrorMessage(
          e?.message || '데이터를 불러오는 중 오류가 발생했습니다.'
        );
      } finally {
        setIsLoading(false);
      }
    })();
  }, [normalId]);

  // ----- Derived: KPI counts -----
  const kpis = useMemo(() => {
    const total = mappingResults.length;
    const ok = mappingResults.filter((r) => r.status === 'auto_mapped').length;
    const need = mappingResults.filter((r) => r.status === 'needs_review').length;
    const fail = mappingResults.filter(
      (r) => r.status === 'mapping_failed' || r.status === 'save_failed'
    ).length;
    return { total, ok, need, fail };
  }, [mappingResults]);

  // ----- Filtering/Search -----
  useEffect(() => {
    let base = [...mappingResults];
    if (statusFilter !== 'all') base = base.filter((r) => r.status === statusFilter);
    if (query.trim()) {
      const q = query.toLowerCase();
      base = base.filter(
        (r) =>
          r.original_gas_name.toLowerCase().includes(q) ||
          (r.ai_mapped_name ?? '').toLowerCase().includes(q)
      );
    }
    setFiltered(base);
  }, [mappingResults, statusFilter, query]);

  // ----- Edit helpers -----
  function updateMapping(
    idx: number,
    field: keyof MappingResult,
    value: any
  ) {
    setEdits((prev) => ({
      ...prev,
      [idx]: {
        ...prev[idx],
        [field]: value,
      },
    }));
  }

  function resetRow(idx: number) {
    setEdits((prev) => {
      const p = { ...prev };
      delete p[idx];
      return p;
    });
  }

  const changedCount = useMemo(() => Object.keys(edits).length, [edits]);

  // ----- Save -----
  async function saveMappings() {
    if (!normalId) return;
    try {
      setIsSaving(true);
      setErrorMessage(null);

      // diff → corrections payload
      const corrections = Object.entries(edits).map(([idx, edit]) => {
        const i = Number(idx);
        const base = mappingResults[i];

        return {
          certification_id: base.certification_id, // may be undefined; backend should accept or map by normal_id + original
          correction_data: {
            final_mapped_name:
              (edit.ai_mapped_name ?? base.ai_mapped_name) || '',
            final_confidence:
              edit.ai_confidence ?? base.ai_confidence ?? 0,
            review_status: 'user_reviewed',
            review_notes: (edit.review_notes ?? base.review_notes) || '',
          },
          reviewed_by: 'user',
        };
      });

      if (corrections.length === 0) {
        alert('변경된 항목이 없습니다.');
        return;
      }

      const res = await fetch('/api/normal/substance/save-corrections', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ normal_id: normalId, corrections }),
      });
      const json = await res.json();

      if (json.status === 'success') {
        // 적용된 값으로 화면 동기화
        const updated = [...mappingResults];
        Object.entries(edits).forEach(([idx, e]) => {
          const i = Number(idx);
          updated[i] = {
            ...updated[i],
            ai_mapped_name: e.ai_mapped_name ?? updated[i].ai_mapped_name,
            ai_confidence: e.ai_confidence ?? updated[i].ai_confidence,
            review_notes: e.review_notes ?? updated[i].review_notes,
            status: 'auto_mapped', // 저장 성공 시 상태 업그레이드
          };
        });
        setMappingResults(updated);
        setEdits({});
        alert('매핑 수정이 저장되었습니다.');
        router.push('/data-upload');
      } else {
        throw new Error(json.message || json.error || '저장 실패');
      }
    } catch (e: any) {
      console.error(e);
      setErrorMessage(e?.message || '저장 중 오류가 발생했습니다.');
      alert(`저장 중 오류: ${e?.message || ''}`);
    } finally {
      setIsSaving(false);
    }
  }

  // ----- Render -----
  if (!normalId) {
    return (
      <div className="min-h-screen bg-gray-50 grid place-items-center">
        <div className="text-center">
          <p className="text-gray-600">잘못된 접근입니다. (normalId 없음)</p>
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

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 grid place-items-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto" />
          <p className="mt-4 text-gray-600">데이터를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (errorMessage) {
    return (
      <div className="min-h-screen bg-gray-50 grid place-items-center">
        <div className="bg-white border shadow-sm p-6 rounded-lg max-w-md text-center">
          <p className="text-red-600 font-medium">오류</p>
          <p className="mt-2 text-gray-700">{errorMessage}</p>
          <button
            onClick={() => router.refresh()}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  if (!normalData || mappingResults.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 grid place-items-center">
        <div className="text-center">
          <p className="text-gray-600">표시할 데이터가 없습니다.</p>
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
      <header className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => router.push('/data-upload')}
              className="mr-2 p-2 text-gray-400 hover:text-gray-600"
              aria-label="back"
            >
              ←
            </button>
            <h1 className="text-2xl font-bold text-gray-900">
              매핑 결과 검토/수정
            </h1>
            <span className="ml-2 text-xs px-2 py-1 bg-blue-50 text-blue-700 rounded-full">
              Normal ID: {normalId}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => router.refresh()}
              className="px-3 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
            >
              새로고침
            </button>
            <button
              onClick={saveMappings}
              disabled={isSaving || changedCount === 0}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {isSaving ? '저장 중…' : `수정사항 저장 (${changedCount})`}
            </button>
          </div>
        </div>
      </header>

      {/* Summary bar */}
      <div className="bg-gradient-to-r from-gray-50 to-gray-100 border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="p-4 bg-white rounded-lg shadow-sm border">
            <p className="text-sm text-gray-500">총 항목</p>
            <p className="text-2xl font-bold">{kpis.total}</p>
          </div>
          <div className="p-4 bg-white rounded-lg shadow-sm border">
            <p className="text-sm text-gray-500">자동 매핑</p>
            <p className="text-2xl font-bold text-green-600">{kpis.ok}</p>
          </div>
          <div className="p-4 bg-white rounded-lg shadow-sm border">
            <p className="text-sm text-gray-500">검토 필요</p>
            <p className="text-2xl font-bold text-yellow-600">{kpis.need}</p>
          </div>
          <div className="p-4 bg-white rounded-lg shadow-sm border">
            <p className="text-sm text-gray-500">실패/오류</p>
            <p className="text-2xl font-bold text-red-600">{kpis.fail}</p>
          </div>
        </div>
      </div>

      {/* Product info */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        <div className="bg-white rounded-lg shadow border">
          <div className="px-6 py-4 border-b">
            <h2 className="text-lg font-semibold text-gray-900">제품 정보</h2>
          </div>
          <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <p className="text-sm text-gray-500">제품명</p>
              <p className="mt-1 font-medium">{normalData.product_name || '-'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">공급업체</p>
              <p className="mt-1 font-medium">{normalData.supplier || '-'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">제조일자</p>
              <p className="mt-1 font-medium">
                {normalData.manufacturing_date || '-'}
              </p>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="mt-6 flex flex-col md:flex-row gap-3 md:items-center">
          <div className="flex gap-2">
            {(['all', 'auto_mapped', 'needs_review', 'mapping_failed', 'save_failed', 'no_model'] as const).map(
              (k) => (
                <button
                  key={k}
                  onClick={() => setStatusFilter(k as any)}
                  className={`px-3 py-2 rounded-md text-sm border ${
                    statusFilter === k
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'bg-white text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  {k === 'all'
                    ? `전체 (${mappingResults.length})`
                    : `${STATUS_META[k].text} (${mappingResults.filter((r) => r.status === k).length})`}
                </button>
              )
            )}
          </div>
          <div className="md:ml-auto">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="원본/매핑명 검색…"
              className="w-full md:w-72 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Mapping list */}
        <div className="mt-4 space-y-4">
          {filtered.map((r, idx) => {
            const e = edits[idx] || {};
            const mapped = e.ai_mapped_name ?? r.ai_mapped_name ?? '';
            const conf = e.ai_confidence ?? r.ai_confidence ?? 0;
            const notes = e.review_notes ?? r.review_notes ?? '';

            return (
              <div
                key={idx}
                className={`bg-white rounded-lg shadow-sm border p-5 ${STATUS_META[r.status].ring}`}
              >
                <div className="flex flex-col md:flex-row md:items-start gap-4">
                  {/* left: original */}
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`text-xs px-2 py-1 rounded-full ${STATUS_META[r.status].chip}`}>
                        {STATUS_META[r.status].text}
                      </span>
                      {r.error && (
                        <span className="text-xs px-2 py-1 rounded-full bg-red-50 text-red-700">
                          오류
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-gray-500">원본 물질명</div>
                    <div className="text-base font-medium">{r.original_gas_name}</div>
                    <div className="mt-1 text-sm text-gray-600">
                      배출량: <span className="font-medium">{r.original_amount || '-'}</span>
                    </div>

                    {r.error && (
                      <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-md text-sm text-red-800">
                        {r.error}
                      </div>
                    )}

                    {r.status === 'mapping_failed' && !r.error && (
                      <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-md text-sm text-yellow-800">
                        자동 매핑에 실패했습니다. 우측에서 수동으로 입력하세요.
                      </div>
                    )}

                    {r.status === 'no_model' && (
                      <div className="mt-3 p-3 bg-orange-50 border border-orange-200 rounded-md text-sm text-orange-800">
                        AI 모델 미로드. 수동 입력이 필요합니다.
                      </div>
                    )}
                  </div>

                  {/* right: editable */}
                  <div className="flex-1">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          매핑된 물질명
                        </label>
                        <input
                          value={mapped}
                          onChange={(e) =>
                            updateMapping(idx, 'ai_mapped_name', e.target.value)
                          }
                          placeholder="예: CO₂, ENERGY-CONSUMPTION 등"
                          className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          신뢰도 (0~1)
                        </label>
                        <input
                          type="number"
                          min={0}
                          max={1}
                          step={0.01}
                          value={typeof conf === 'number' ? conf : 0}
                          onChange={(e) =>
                            updateMapping(
                              idx,
                              'ai_confidence',
                              Number(e.target.value)
                            )
                          }
                          className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <p className="mt-1 text-xs text-gray-500">
                          현재: {toFixedOrDash(r.ai_confidence, 2)}
                        </p>
                      </div>
                      <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          검토 노트
                        </label>
                        <textarea
                          rows={2}
                          value={notes}
                          onChange={(e) =>
                            updateMapping(idx, 'review_notes', e.target.value)
                          }
                          placeholder="수정 사유, 참고사항 등"
                          className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    </div>

                    <div className="mt-3 flex items-center gap-2">
                      {edits[idx] ? (
                        <button
                          onClick={() => resetRow(idx)}
                          className="px-3 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md text-sm"
                        >
                          행 수정 취소
                        </button>
                      ) : (
                        <span className="text-xs text-gray-400">
                          수정 없음
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 my-8">
          <button
            onClick={() => router.push('/data-upload')}
            className="px-4 py-2 text-gray-700 bg-white border rounded-md hover:bg-gray-50"
          >
            취소
          </button>
          <button
            onClick={saveMappings}
            disabled={isSaving || changedCount === 0}
            className="px-5 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {isSaving ? '저장 중…' : `수정사항 저장 (${changedCount})`}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function MappingEditPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gray-50 grid place-items-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">페이지를 불러오는 중...</p>
          </div>
        </div>
      }
    >
      <MappingEditContent />
    </Suspense>
  );
}
