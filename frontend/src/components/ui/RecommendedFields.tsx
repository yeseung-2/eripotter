"use client";
import type { IndicatorInputFieldResponse } from "@/types/report";

export default function RecommendedFields({ data }: { data: IndicatorInputFieldResponse | null }) {
  if (!data) return null;
  if (!data.recommended_fields?.length)
    return <div className="text-sm text-slate-500">추천 필드 없음</div>;
  return (
    <div className="space-y-3">
      {data.recommended_fields.map((rf, i) => (
        <div key={i} className="border rounded p-3 bg-white">
          <div className="text-xs text-slate-500">{rf.source} · score {rf.score.toFixed(3)}</div>
          <div className="font-medium">{rf.title}</div>
          <p className="text-sm whitespace-pre-wrap mt-1">{rf.content}</p>
        </div>
      ))}
    </div>
  );
}
