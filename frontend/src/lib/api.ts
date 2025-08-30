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
  api("/report/indicators");
