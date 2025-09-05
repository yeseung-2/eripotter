// src/types/report.ts
export type Indicator = {
    indicator_id: string;
    title: string;
    category: string;
    subcategory?: string | null;
    description?: string | null;
    input_fields?: Record<string, any> | null;
    example_data?: Record<string, any> | null;
    status: "active" | "inactive";
    created_at: string;
    updated_at?: string | null;
  };
  
  export type IndicatorListResponse = {
    success: boolean;
    message: string;
    indicators: Indicator[];
    total_count: number;
  };
  
  export type IndicatorInputFieldResponse = {
    success: boolean;
    message: string;
    indicator_id: string;
    title: string;
    input_fields: Record<string, any>;
    recommended_fields: Array<{
      source: string;
      title: string;
      content: string;
      score: number;
      suggested_fields: Array<{
        field_name: string;
        field_type: "text" | "number" | "select" | "date";
        description: string;
        required: boolean;
        options?: string[];
      }>;
    }>;
  };
  
  export type IndicatorDraftRequest = {
    company_name: string;
    inputs: Record<string, any>;
  };
  
  export type IndicatorSaveRequest = IndicatorDraftRequest;

  // 새로운 통일된 API 응답 타입들
  export type InputFieldsResponse = {
    indicator_id: string;
    required_data: string;
    required_fields: any[];
  };

  export type DraftResponse = string; // HTML 문자열

  export type SaveResponse = {
    success: boolean;
    message: string;
    indicator_id: string;
    company_name: string;
    saved_at?: string;
  };

  export type IndicatorDataResponse = {
    success: boolean;
    message: string;
    data: {
      indicator_id: string;
      company_name: string;
      inputs: Record<string, any>;
      retrieved_at: string;
    } | null;
  };

  export type SummaryResponse = string; // HTML 문자열
  