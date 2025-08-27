'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';

interface LoginData {
  user_id: string;
  user_pw: string;
}

interface AccountResponse {
  status: string;
  message: string;
  user_id: string;
  company_id: string;
  user_name?: string;
  user: {
    user_id: string;
    company_id: string;
    user_name?: string;
  };
}

interface ApiErrorResponse {
  detail?: string;
  message?: string;
}

// === ADD: API base util ===
const BASE = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "";
const join = (p: string) => (BASE ? `${BASE}${p}` : p);
// ==========================

export default function LoginPage() {
  const router = useRouter();

  // Form state management
  const [userData, setUserData] = useState<LoginData>({
    user_id: '',
    user_pw: ''
  });

  // Loading state
  const [isLoading, setIsLoading] = useState(false);

  // Form input handler
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setUserData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Login form submission
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    console.log("🔐 로그인 시도", { user_id: userData.user_id });

    try {
      const url = join("/api/account/login");
      console.log("📡 API 요청", { url, method: "POST" });
      
      const response = await axios.post<AccountResponse>(url, userData, {
        headers: { "Content-Type": "application/json" },
        withCredentials: true, // 쿠키 기반이면 필수
      });

      console.log("✅ 로그인 성공", response.data);
      console.log('로그인 성공:', response.data);
      
      // 사용자 정보를 localStorage에 저장
      if (response.data.company_id) {
        localStorage.setItem('user_company_id', response.data.company_id);
        localStorage.setItem('user_id', response.data.user_id);
        localStorage.setItem('user_name', response.data.user_id); // 담당자 이름 (현재는 user_id 사용)
        console.log("💾 사용자 정보 저장", { 
          user_id: response.data.user_id, 
          company_id: response.data.company_id,
          user_name: response.data.user_id
        });
      }
      
      // 로그인 성공 시 대시보드로 리다이렉트
      console.log("🔄 대시보드로 리다이렉트");
      router.push('/dashboard');
      
    } catch (error) {
      console.error("❌ 로그인 실패", error as Error, { user_id: userData.user_id });
      console.error('로그인 실패:', error);
      
      if (axios.isAxiosError(error)) {
        if (error.response) {
          const data = error.response.data as ApiErrorResponse;
          const msg = data?.detail ?? data?.message ?? '알 수 없는 오류가 발생했습니다.';
          console.warn("⚠️ 서버 응답 오류", { status: error.response.status, data });
          alert(`로그인 실패: ${msg}`);
        } else if (error.request) {
          console.error("❌ 서버 연결 실패", error as Error);
          alert('서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.');
        } else {
          console.error("❌ 네트워크 오류", error as Error);
          alert('네트워크 오류가 발생했습니다.');
        }
      } else {
        console.error("❌ 알 수 없는 로그인 오류", error as Error);
        alert('로그인 중 오류가 발생했습니다.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <div className="bg-white rounded-3xl shadow-2xl px-8 py-12">
          {/* Login Title */}
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold text-gray-900 tracking-tight">
              Login
            </h1>
          </div>

          {/* Login Form */}
          <form onSubmit={handleLogin} className="space-y-8">
            {/* Username Input */}
            <div className="relative">
              <input
                type="text"
                name="user_id"
                value={userData.user_id}
                onChange={handleInputChange}
                placeholder="Username"
                className="w-full px-0 py-4 text-lg text-gray-800 placeholder-gray-400 bg-transparent border-0 border-b-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all duration-300"
                required
                disabled={isLoading}
              />
            </div>

            {/* Password Input */}
            <div className="relative">
              <input
                type="password"
                name="user_pw"
                value={userData.user_pw}
                onChange={handleInputChange}
                placeholder="Password"
                className="w-full px-0 py-4 text-lg text-gray-800 placeholder-gray-400 bg-transparent border-0 border-b-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all duration-300"
                required
                disabled={isLoading}
              />
            </div>

            {/* Find ID/Password Links */}
            <div className="text-center py-6">
              <div className="text-sm text-gray-500 space-x-1">
                <a href="/find-id" className="hover:text-blue-600 transition-colors duration-200">
                  Find ID
                </a>
                <span className="mx-3 text-gray-300">|</span>
                <a href="/find-password" className="hover:text-blue-600 transition-colors duration-200">
                  Find Password
                </a>
              </div>
            </div>

            {/* Login Button */}
            <button
              type="submit"
              disabled={isLoading}
              className={`w-full py-4 rounded-2xl font-medium text-lg shadow-sm transition-all duration-200 ${
                isLoading 
                  ? 'bg-gray-400 text-white cursor-not-allowed' 
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a 8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  로그인 중...
                </div>
              ) : (
                'Login'
              )}
            </button>

            {/* Sign Up Button */}
            <button
              type="button"
              onClick={() => router.push('/signup')}
              disabled={isLoading}
              className="w-full bg-white border-2 border-gray-300 text-gray-800 py-4 rounded-2xl hover:bg-gray-50 hover:border-gray-400 transition-all duration-200 font-medium text-lg shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Sign Up
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
