// src/lib/http.ts - 통일된 HTTP 클라이언트
const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function http<T>(path: string, init?: RequestInit): Promise<T> {
  try {
    const res = await fetch(`${BASE}${path}`, {
      ...init,
      headers: {
        'Content-Type': 'application/json',
        ...(init?.headers || {}),
      },
      cache: "no-store",
    });
    
    if (!res.ok) {
      const text = await res.text().catch(() => "");
      throw new Error(`API ${res.status}: ${text || res.statusText}`);
    }
    
    const ct = res.headers.get("content-type") || "";
    return (ct.includes("application/json") ? await res.json() : (await res.text())) as T;
  } catch (error) {
    console.error(`API 호출 실패 (${path}):`, error);
    throw error;
  }
}

// JSON 응답을 위한 편의 함수
export async function httpJson<T>(path: string, init?: RequestInit): Promise<T> {
  return http<T>(path, { ...init, headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) } });
}

// 텍스트 응답을 위한 편의 함수
export async function httpText(path: string, init?: RequestInit): Promise<string> {
  return http<string>(path, { ...init, headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) } });
}
