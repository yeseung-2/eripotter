export const API_BASE = process.env.NEXT_PUBLIC_REPORT_API_URL || "http://localhost:8000";

async function httpJson<T>(path: string, init?: RequestInit): Promise<T> {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
      cache: "no-store",
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json() as Promise<T>;
  } catch (error) {
    console.error(`API 호출 실패 (${path}):`, error);
    throw error;
  }
}

async function httpText(path: string, init?: RequestInit): Promise<string> {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
      cache: "no-store",
    });
    if (!res.ok) throw new Error(await res.text());
    return res.text();
  } catch (error) {
    console.error(`API 호출 실패 (${path}):`, error);
    throw error;
  }
}

// ===== API =====
import type {
  IndicatorListResponse,
  IndicatorInputFieldResponse,
  IndicatorDraftRequest,
  IndicatorSaveRequest,
} from "@/types/report";

export const getAllIndicators = () =>
  httpJson<IndicatorListResponse>("/indicators");

export const getIndicatorWithFields = (id: string) =>
  httpJson<IndicatorInputFieldResponse>(`/indicators/${id}/fields`);

export const generateInputFields = (id: string) =>
  httpJson<{ indicator_id: string; required_data: string; required_fields: any[] }>(
    `/reports/indicator/${id}/input-fields`
  );

export const generateDraft = (id: string, body: IndicatorDraftRequest) =>
  httpText(`/reports/indicator/${id}/draft`, {
    method: "POST",
    body: JSON.stringify(body),
  });

export const saveIndicator = (id: string, body: IndicatorSaveRequest) =>
  httpJson<boolean>(`/reports/indicator/${id}/save`, {
    method: "POST",
    body: JSON.stringify(body),
  });
