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
export const getCompanyResults = (companyName: string): Promise<{ assessment_results: any[] }> =>
  api(`/api/assessment/assessment-results/${companyName}`);

// Assessment 서비스 상태 확인
export const checkAssessmentHealth = () =>
  api("/api/assessment/health");

// ===== Solution API 함수들 =====
import type { SolutionSubmissionResponse } from "@/types/assessment";

// 회사별 솔루션 조회
export const getCompanySolutions = (companyName: string): Promise<SolutionSubmissionResponse[]> =>
  api(`/api/solution/${companyName}`);

// 솔루션 생성
export const generateSolutions = (companyName: string): Promise<SolutionSubmissionResponse[]> =>
  api(`/api/solution/generate/${companyName}`, {
    method: "POST",
  });
