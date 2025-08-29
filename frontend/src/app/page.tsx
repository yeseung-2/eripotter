'use client';

import { useRouter } from 'next/navigation';
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

// === ADD: API base util ===
const BASE = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "";
const join = (p: string) => (BASE ? `${BASE}${p}` : p);
// ==========================

export default function LoginPage() {
  const router = useRouter();

  const handleGoogleLogin = () => {
    // Google OAuth 로그인 엔드포인트로 리다이렉트
    window.location.href = join("/api/auth/google/login");  // URL 패턴 수정
  };

  const handleReportCreate = () => {
    // 보고서 작성 페이지로 이동
    router.push('/report/create');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center p-4">
      <Card className="w-full max-w-sm bg-white rounded-3xl shadow-2xl px-8 py-12">
        {/* Login Title */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 tracking-tight mb-4">
            Welcome
          </h1>
          <p className="text-gray-600">
            공급망 관리를 위한 첫걸음을 시작하세요
          </p>
        </div>

        {/* Google Login Button */}
        <Button
          onClick={handleGoogleLogin}
          className="w-full py-6 mb-4 bg-white hover:bg-gray-50 text-gray-800 border border-gray-300 rounded-2xl flex items-center justify-center space-x-2 text-lg font-medium"
        >
          <svg className="w-6 h-6" viewBox="0 0 24 24">
            <path
              className="text-[#4285F4]"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              className="text-[#34A853]"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              className="text-[#FBBC05]"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
            />
            <path
              className="text-[#EA4335]"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            />
          </svg>
          <span>Google 계정으로 로그인</span>
        </Button>

        {/* Report Create Button */}
        <Button
          onClick={handleReportCreate}
          className="w-full py-6 mb-4 bg-blue-600 hover:bg-blue-700 text-white rounded-2xl flex items-center justify-center space-x-2 text-lg font-medium"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span>보고서 작성</span>
        </Button>

        <div className="text-center text-sm text-gray-600 mt-8">
          로그인 시{" "}
          <a href="/terms" className="text-blue-600 hover:underline">
            이용약관
          </a>
          과{" "}
          <a href="/privacy" className="text-blue-600 hover:underline">
            개인정보처리방침
          </a>
          에 동의하게 됩니다.
        </div>
      </Card>
    </div>
  );
}