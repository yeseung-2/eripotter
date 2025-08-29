"use client";
import { useEffect, useMemo, useState } from "react";
import { getAllIndicators } from "@/lib/api";
import type { Indicator, IndicatorListResponse } from "@/types/report";

export default function IndicatorPicker({ onPick }: { onPick: (ind: Indicator) => void }) {
  const [data, setData] = useState<Indicator[]>([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState("");
  const [cat, setCat] = useState("");

  useEffect(() => {
    (async () => {
      const res: IndicatorListResponse = await getAllIndicators();
      setData(res.indicators);
      setLoading(false);
    })();
  }, []);

  const categories = useMemo(() => Array.from(new Set(data.map((d) => d.category))), [data]);
  const filtered = useMemo(
    () =>
      data.filter(
        (d) =>
          (!cat || d.category === cat) &&
          (!q ||
            d.indicator_id.toLowerCase().includes(q.toLowerCase()) ||
            d.title.toLowerCase().includes(q.toLowerCase()))
      ),
    [data, q, cat]
  );

  if (loading) return <div className="p-4">지표 불러오는 중…</div>;

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        <input
          className="border rounded px-3 py-2 text-sm w-64"
          placeholder="지표 코드/제목 검색"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <select className="border rounded px-2 py-2 text-sm" value={cat} onChange={(e) => setCat(e.target.value)}>
          <option value="">전체 카테고리</option>
          {categories.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>
      <ul className="grid md:grid-cols-2 gap-3">
        {filtered.map((ind) => (
          <li key={ind.indicator_id} className="border rounded p-3 hover:shadow-sm bg-white">
            <div className="text-xs text-slate-500">{ind.indicator_id}</div>
            <div className="font-medium">{ind.title}</div>
            <div className="text-xs text-slate-500 mt-1">{ind.category}</div>
            <button className="mt-2 text-sm underline" onClick={() => onPick(ind)}>
              선택
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
