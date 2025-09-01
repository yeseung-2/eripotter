// src/lib/reportApi.ts
// 새로운 통일된 엔드포인트 사용
// 서버에서 /api/report/indicator/{id}/... 형태로 구현됨

import type {
  InputFieldsResponse,
  DraftResponse,
  SaveResponse,
  IndicatorDataResponse,
  SummaryResponse,
} from "@/types/report";
import { http } from "./http";

export function getInputFields(indicatorId: string): Promise<InputFieldsResponse> {
  // 임시로 직접 백엔드 호출 (게이트웨이 우회)
  const directBackendUrl = "https://report-service-production-91aa.up.railway.app";
  const url = `${directBackendUrl}/indicator/${encodeURIComponent(indicatorId)}/input-fields`;
  
  console.log(`🔗 직접 백엔드 호출: ${url}`);
  
  return fetch(url)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return response.json();
    })
    .catch(error => {
      console.error(`❌ 직접 백엔드 호출 실패: ${error}`);
      // 실패 시 게이트웨이로 폴백
      return http<InputFieldsResponse>(
        `/api/report/indicator/${encodeURIComponent(indicatorId)}/input-fields`
      );
    });
}

export function generateDraft(indicatorId: string, companyName: string, inputs: Record<string, any>): Promise<DraftResponse> {
  return http<DraftResponse>(
    `/api/report/indicator/${encodeURIComponent(indicatorId)}/draft?company_name=${encodeURIComponent(companyName)}`,
    { method: "POST", body: JSON.stringify(inputs) }
  );
}

export function saveIndicatorData(indicatorId: string, companyName: string, inputs: Record<string, any>): Promise<SaveResponse> {
  return http<SaveResponse>(
    `/api/report/indicator/${encodeURIComponent(indicatorId)}/save?company_name=${encodeURIComponent(companyName)}`,
    { method: "POST", body: JSON.stringify(inputs) }
  );
}

export function getIndicatorData(indicatorId: string, companyName: string): Promise<IndicatorDataResponse> {
  return http<IndicatorDataResponse>(
    `/api/report/indicator/${encodeURIComponent(indicatorId)}/data?company_name=${encodeURIComponent(companyName)}`
  );
}

export function getIndicatorSummary(indicatorId: string): Promise<SummaryResponse> {
  return http<SummaryResponse>(`/api/report/indicator/${encodeURIComponent(indicatorId)}/summary`);
}

// 보고서 목록 관련 함수들
export interface ReportItem {
  id: string;
  company_name: string;
  report_type: string;
  topic: string;
  description: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export function getReports(): Promise<ReportItem[]> {
  return http<ReportItem[]>("/api/report/reports");
}

export function getReportById(reportId: string): Promise<ReportItem> {
  return http<ReportItem>(`/api/report/reports/${encodeURIComponent(reportId)}`);
}
