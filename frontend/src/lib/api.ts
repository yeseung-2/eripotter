// 공통 API 래퍼 - Gateway를 통해 모든 서비스에 접근
const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

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

// ===== 데이터 공유 API 함수들 =====
export const getSharingRequestsByProvider = (providerId: string, status?: string): Promise<any> =>
  api(`/sharing/provider/${providerId}${status ? `?status=${status}` : ''}`);

export const getSharingRequestsByRequester = (requesterId: string, status?: string): Promise<any> =>
  api(`/sharing/requester/${requesterId}${status ? `?status=${status}` : ''}`);

export const getSharingRequestById = (requestId: string): Promise<any> =>
  api(`/sharing/${requestId}`);

export const createSharingRequest = (requestData: any): Promise<any> =>
  api('/sharing/', {
    method: "POST",
    body: JSON.stringify(requestData),
  });

export const approveSharingRequest = (requestId: string, reviewerId: string, reviewerName: string, comment: string = ""): Promise<any> =>
  api(`/sharing/${requestId}/approve?reviewer_id=${reviewerId}&reviewer_name=${encodeURIComponent(reviewerName)}&comment=${encodeURIComponent(comment)}`, {
    method: "PUT",
  });

export const rejectSharingRequest = (requestId: string, reviewerId: string, reviewerName: string, comment: string = ""): Promise<any> =>
  api(`/sharing/${requestId}/reject?reviewer_id=${reviewerId}&reviewer_name=${encodeURIComponent(reviewerName)}&comment=${encodeURIComponent(comment)}`, {
    method: "PUT",
  });

export const reviewSharingRequest = (requestId: string, reviewData: any): Promise<any> =>
  api(`/sharing/${requestId}/review`, {
    method: "PUT",
    body: JSON.stringify(reviewData),
  });

export const sendApprovedData = (requestId: string, dataUrl: string): Promise<any> =>
  api(`/sharing/${requestId}/send?data_url=${encodeURIComponent(dataUrl)}`, {
    method: "POST",
  });

export const getPendingRequestsCount = (providerId: string): Promise<any> =>
  api(`/sharing/provider/${providerId}/pending-count`);

export const getSharingStats = (companyId: string, days: number = 30): Promise<any> =>
  api(`/sharing/stats/${companyId}?days=${days}`);

export const getSupplierChain = (parentCompanyId: string, chainLevel?: number): Promise<any> =>
  api(`/sharing/chain/${chainLevel || 0}`);

// ===== 핵심 협력사 관리 API 함수들 =====
export const toggleStrategicSupplier = (supplierId: string, isStrategic: boolean): Promise<any> =>
  api(`/sharing/suppliers/${supplierId}/strategic?is_strategic=${isStrategic}`, {
    method: "PUT",
  });

export const getStrategicSuppliers = (companyId: string): Promise<any> =>
  api(`/sharing/suppliers/strategic?company_id=${companyId}`);

// ===== 회사 관리 API 함수들 =====
export const getCompanies = (): Promise<any> =>
  api(`/sharing/companies`);