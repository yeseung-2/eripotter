import type { IndicatorInputFieldResponse } from "@/types/report";

export type FormField = {
  key: string;
  label: string;
  type: "text" | "number" | "select" | "date";
  required?: boolean;
  options?: string[];
  description?: string;
  unit?: string;
  year?: string;
};

export function normalizeFields(
  data: IndicatorInputFieldResponse | null,
  ragFields: Array<{ [k: string]: any }> = []
): FormField[] {
  const out: FormField[] = [];

  // DB 정의
  const base = data?.input_fields ?? {};
  Object.entries(base).forEach(([key, v]) => {
    const vv = v as any;
    out.push({
      key,
      label: vv?.label ?? key,
      type: (vv?.type as FormField["type"]) ?? "text",
      required: !!vv?.required,
      options: vv?.options ?? undefined,
      description: vv?.description ?? undefined,
    });
  });

  // RAG 추천 병합(중복 키 스킵)
  const recs = (data?.recommended_fields ?? []).flatMap((rf) => rf.suggested_fields || []);
  [...recs, ...ragFields].forEach((f: any) => {
    const key = (f.field_name || "").trim();
    if (!key) return;
    if (out.some((o) => o.key === key)) return;
    out.push({
      key,
      label: key,
      type: (f.field_type as FormField["type"]) || "text",
      required: !!f.required,
      options: f.options || undefined,
      description: f.description || undefined,
    });
  });

  if (!out.length) out.push({ key: "company_overview", label: "회사 개요", type: "text" });
  return out;
}
