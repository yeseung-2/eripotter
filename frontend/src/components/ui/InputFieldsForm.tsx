"use client";
import { useEffect, useState } from "react";
import type { FormField } from "@/lib/form";

export default function InputFieldsForm({
  fields,
  value,
  onChange,
}: {
  fields: FormField[];
  value: Record<string, any>;
  onChange: (v: Record<string, any>) => void;
}) {
  const [data, setData] = useState<Record<string, any>>(value || {});

  useEffect(() => setData(value || {}), [value]);

  const set = (k: string, v: any) => {
    const next = { ...data, [k]: v };
    setData(next);
    onChange(next);
  };

  return (
    <div className="space-y-4">
      {fields.map((f) => (
        <div key={f.key} className="bg-white border rounded p-3">
          <label className="block text-sm font-medium text-slate-700">
            {f.label}
            {f.required && <span className="text-red-500 ml-1">*</span>}
          </label>
          <div className="flex gap-2 text-xs text-slate-500 mt-1">
            {f.description && <span>{f.description}</span>}
            {f.unit && <span className="text-blue-600">단위: {f.unit}</span>}
            {f.year && <span className="text-green-600">연도: {f.year}</span>}
          </div>

          {f.type === "select" ? (
            <select
              className="mt-2 border rounded px-3 py-2 w-full"
              value={data[f.key] ?? ""}
              onChange={(e) => set(f.key, e.target.value)}
            >
              <option value="">선택</option>
              {(f.options || []).map((o) => (
                <option key={o} value={o}>
                  {o}
                </option>
              ))}
            </select>
          ) : f.type === "number" ? (
            <input
              type="number"
              className="mt-2 border rounded px-3 py-2 w-full"
              value={data[f.key] ?? ""}
              onChange={(e) => set(f.key, e.target.value === "" ? "" : Number(e.target.value))}
            />
          ) : f.type === "date" ? (
            <input
              type="date"
              className="mt-2 border rounded px-3 py-2 w-full"
              value={data[f.key] ?? ""}
              onChange={(e) => set(f.key, e.target.value)}
            />
          ) : (
            <textarea
              className="mt-2 border rounded px-3 py-2 w-full"
              rows={3}
              value={data[f.key] ?? ""}
              onChange={(e) => set(f.key, e.target.value)}
            />
          )}
        </div>
      ))}
    </div>
  );
}
