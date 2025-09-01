// Assessment 관련 타입 정의

export interface KesgItem {
  id: number;
  classification?: string;
  domain?: string;
  category?: string;
  item_name?: string;
  item_desc?: string;
  metric_desc?: string;
  data_source?: string;
  data_period?: string;
  data_method?: string;
  data_detail?: string;
  question_type?: string;
  levels_json?: LevelData[];
  choices_json?: ChoiceData[];
  scoring_json?: Record<string, number>;
  weight?: number;
}

export interface KesgResponse {
  items: KesgItem[];
  total_count: number;
}

export interface AssessmentSubmissionRequest {
  question_id: number;
  question_type: string;
  level_no?: number;
  choice_ids?: number[];
}

export interface AssessmentSubmissionResponse {
  id: number;
  company_name: string;
  question_id: number;
  question_type: string;
  level_no?: number;
  choice_ids?: number[];
  score: number;
  timestamp?: string;
}

export interface AssessmentRequest {
  company_name: string;
  responses: AssessmentSubmissionRequest[];
}

export interface AssessmentResponse {
  id: string;
  company_name: string;
  created_at: string;
  status: string;
}

// Level and Choice types
export interface LevelData {
  level_no: number;
  label: string;
  desc: string;
  score: number;
}

export interface ChoiceData {
  id: number;
  text: string;
}

// Solution types
export interface SolutionSubmissionResponse {
  id: number;
  company_name: string;
  question_id: number;
  sol: string;
  timestamp: string;
  item_name: string;
  item_desc: string;
  classification: string;
  domain: string;
}
