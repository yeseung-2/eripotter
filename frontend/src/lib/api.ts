export const API_BASE = process.env.NEXT_PUBLIC_REPORT_API_URL as string;

async function httpJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    cache: "no-store",
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<T>;
}

async function httpText(path: string, init?: RequestInit): Promise<string> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    cache: "no-store",
  });
  if (!res.ok) throw new Error(await res.text());
  return res.text();
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
