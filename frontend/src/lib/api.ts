// 공통 API 래퍼 - Gateway를 통해 모든 서비스에 접근
import { httpJson, httpText } from "./http";

// 기존 호환성을 위한 별칭
export const api = httpJson;
export const apiText = httpText;

// ===== API 함수들 =====
import type {
  IndicatorListResponse,
} from "@/types/report";

export const getAllIndicators = (): Promise<IndicatorListResponse> =>
  api("/api/report/indicators");

// ===== Assessment API 함수들 =====
import type { KesgResponse, AssessmentRequest, AssessmentSubmissionResponse } from "@/types/assessment";

// KESG 문항 목록 조회
export const getKesgItems = (): Promise<KesgResponse> =>
  api("/api/assessment/kesg");

// 특정 KESG 문항 조회
export const getKesgItemById = (itemId: number) =>
  api(`/api/assessment/kesg/${itemId}`);

// 자가진단 응답 제출
export const submitAssessment = (request: AssessmentRequest): Promise<AssessmentSubmissionResponse[]> =>
  api("/api/assessment/", {
    method: "POST",
    body: JSON.stringify(request),
  });

// 회사별 자가진단 결과 조회
export const getCompanyResults = (companyName: string): Promise<{ assessment_results: any[] }> => {
  if (!companyName) {
    return Promise.reject(new Error('회사명이 필요합니다.'));
  }
  return api(`/api/assessment/assessment-results/${encodeURIComponent(companyName)}`);
};

// Assessment 서비스 상태 확인
export const checkAssessmentHealth = () =>
  api("/api/assessment/health");

// ===== Solution API 함수들 =====
import type { SolutionSubmissionResponse } from "@/types/assessment";

// 회사별 솔루션 조회
export const getCompanySolutions = (companyName: string): Promise<SolutionSubmissionResponse[]> => {
  if (!companyName) {
    return Promise.reject(new Error('회사명이 필요합니다.'));
  }
  return api(`/api/solution/${encodeURIComponent(companyName)}`);
};

// 솔루션 생성
export const generateSolutions = (companyName: string): Promise<SolutionSubmissionResponse[]> => {
  if (!companyName) {
    return Promise.reject(new Error('회사명이 필요합니다.'));
  }
  return api(`/api/solution/generate/${encodeURIComponent(companyName)}`, {
    method: "POST",
  });
};

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

// ===== Monitoring API 함수들 =====
// 공급망 취약부문 조회
export const getSupplyChainVulnerabilities = (): Promise<any> =>
  api("/api/monitoring/supply-chain/vulnerabilities");

// 회사별 취약부문 조회
export const getCompanyVulnerabilities = (): Promise<any> =>
  api("/api/monitoring/vulnerabilities");

// 회사별 Assessment 결과 조회
export const getCompanyAssessment = (): Promise<any> =>
  api("/api/monitoring/assessments");

// 공급망 Assessment 결과 조회
export const getSupplyChainAssessment = (): Promise<any> =>
  api("/api/monitoring/supply-chain/assessments");

// 회사별 솔루션 조회
export const getCompanySolutionsFromMonitoring = (): Promise<any> =>
  api("/api/monitoring/solutions");

// 회사 목록 조회
export const getCompanyList = (): Promise<any> =>
  api("/api/monitoring/companies");