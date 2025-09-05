"use client";
export default function Stepper({ step }: { step: number }) {
  const items = ["지표 선택", "데이터 입력", "초안 생성", "임시저장"];
  return (
    <ol className="flex flex-wrap gap-3">
      {items.map((label, i) => {
        const active = i + 1 <= step;
        return (
          <li key={label} className="flex items-center">
            <span
              className={`inline-flex h-6 w-6 items-center justify-center rounded-full text-xs font-semibold mr-2
                ${active ? "bg-blue-600 text-white" : "bg-slate-200 text-slate-600"}`}
            >
              {i + 1}
            </span>
            <span className={`text-sm ${active ? "text-slate-900" : "text-slate-500"}`}>{label}</span>
            {i < items.length - 1 && <span className="mx-3 text-slate-300">›</span>}
          </li>
        );
      })}
    </ol>
  );
}
