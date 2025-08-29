// 공통 API 래퍼 - Gateway를 통해 모든 서비스에 접근
const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function api(path: string, init?: RequestInit) {
  try {
    const res = await fetch(`${BASE}${path}`, {
      ...init,
      headers: {
        'Content-Type': 'application/json',
        ...(init?.headers || {}),
      },
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
    return res.json();
  } catch (error) {
    console.error(`API 호출 실패 (${path}):`, error);
    throw error;
  }
}

export async function apiText(path: string, init?: RequestInit) {
  try {
    const res = await fetch(`${BASE}${path}`, {
      ...init,
      headers: {
        'Content-Type': 'application/json',
        ...(init?.headers || {}),
      },
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
    return res.text();
  } catch (error) {
    console.error(`API 호출 실패 (${path}):`, error);
    throw error;
  }
}

// ===== API 함수들 =====
import type {
  IndicatorListResponse,
  IndicatorInputFieldResponse,
  IndicatorDraftRequest,
  IndicatorSaveRequest,
} from "@/types/report";

export const getAllIndicators = (): Promise<IndicatorListResponse> =>
  api("/report/indicators");

export const getIndicatorWithFields = (id: string): Promise<IndicatorInputFieldResponse> =>
  api(`/report/indicators/${id}/fields`);

export const generateInputFields = (id: string): Promise<{ indicator_id: string; required_data: string; required_fields: any[] }> =>
  api(`/report/reports/indicator/${id}/input-fields`);

export const generateDraft = (id: string, body: IndicatorDraftRequest): Promise<string> =>
  apiText(`/report/reports/indicator/${id}/draft`, {
    method: "POST",
    body: JSON.stringify(body),
  });

export const saveIndicator = (id: string, body: IndicatorSaveRequest): Promise<boolean> =>
  api(`/report/reports/indicator/${id}/save`, {
    method: "POST",
    body: JSON.stringify(body),
  });
