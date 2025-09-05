'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';

// === ADD: API base util ===
const BASE = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "";
const join = (p: string) => (BASE ? `${BASE}${p}` : p);
// ==========================

export default function SignupPage() {
  const router = useRouter();

  // Form state management - ERD에 맞춰 필드 수정
  const [userData, setUserData] = useState({
    user_id: '',
    user_pw: '',
    user_pw_confirm: '',
    industry: '',
    bs_num: '',
    company_id: '',
    company_add: '',
    company_country: '',
    manager_dept: '',
    manager_name: '',
    manager_email: '',
    manager_phone: ''
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

  // Signup form submission
  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    // 비밀번호 확인
    if (userData.user_pw !== userData.user_pw_confirm) {
      alert('비밀번호가 일치하지 않습니다.');
      setIsLoading(false);
      return;
    }

    try {
      // 서버로 보낼 데이터에서 user_pw_confirm 제거
      const signupData = {
        user_id: userData.user_id,
        user_pw: userData.user_pw,
        industry: userData.industry,
        bs_num: userData.bs_num,
        company_id: userData.company_id,
        company_add: userData.company_add,
        company_country: userData.company_country,
        manager_dept: userData.manager_dept,
        manager_name: userData.manager_name,
        manager_email: userData.manager_email,
        manager_phone: userData.manager_phone
      };

      // ✅ 게이트웨이 경유로 호출
      const response = await axios.post(
        join('/api/account/signup'),
        signupData,
        {
          headers: { 'Content-Type': 'application/json' },
          withCredentials: true,
        }
      );

      console.log('회원가입 성공:', response.data);
      alert('회원가입이 완료되었습니다!');

      // 회원가입 성공 시 로그인 페이지로 리다이렉트
      router.push('/');

    } catch (error) {
      console.error('회원가입 실패:', error);

      // 에러 처리
      if (axios.isAxiosError(error)) {
        if (error.response) {
                     const data: { detail?: string; message?: string } = error.response.data ?? {};
          const msg = data?.detail ?? data?.message ?? '알 수 없는 오류가 발생했습니다.';
          alert(`회원가입 실패: ${msg}`);
        } else if (error.request) {
          alert('서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.');
        } else {
          alert('네트워크 오류가 발생했습니다.');
        }
      } else {
        alert('회원가입 중 오류가 발생했습니다.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-3xl shadow-2xl px-8 py-12">
          {/* Signup Title */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 tracking-tight">
              Sign Up
            </h1>
            <p className="text-gray-600 mt-2">새로운 계정을 만들어 보세요</p>
          </div>

          {/* Signup Form */}
          <form onSubmit={handleSignup} className="space-y-6">
            {/* 계정 정보 섹션 */}
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-700">계정 정보</h3>
              <div className="relative">
                <input
                  type="text"
                  name="user_id"
                  value={userData.user_id}
                  onChange={handleInputChange}
                  placeholder="아이디"
                  className="w-full px-0 py-4 text-lg text-gray-800 placeholder-gray-400 bg-transparent border-0 border-b-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all duration-300"
                  required
                  disabled={isLoading}
                />
              </div>
              <div className="relative">
                <input
                  type="password"
                  name="user_pw"
                  value={userData.user_pw}
                  onChange={handleInputChange}
                  placeholder="비밀번호"
                  className="w-full px-0 py-4 text-lg text-gray-800 placeholder-gray-400 bg-transparent border-0 border-b-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all duration-300"
                  required
                  disabled={isLoading}
                />
              </div>
              <div className="relative">
                <input
                  type="password"
                  name="user_pw_confirm"
                  value={userData.user_pw_confirm}
                  onChange={handleInputChange}
                  placeholder="비밀번호 확인"
                  className="w-full px-0 py-4 text-lg text-gray-800 placeholder-gray-400 bg-transparent border-0 border-b-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all duration-300"
                  required
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* 회사 정보 섹션 */}
            <div className="space-y-6 mt-8">
              <h3 className="text-lg font-semibold text-gray-700">회사 정보</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="relative">
                  <input
                    type="text"
                    name="company_id"
                    value={userData.company_id}
                    onChange={handleInputChange}
                    placeholder="회사명"
                    className="w-full px-0 py-4 text-lg text-gray-800 placeholder-gray-400 bg-transparent border-0 border-b-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all duration-300"
                    required
                    disabled={isLoading}
                  />
                </div>
                <div className="relative">
                  <input
                    type="text"
                    name="industry"
                    value={userData.industry}
                    onChange={handleInputChange}
                    placeholder="업종"
                    className="w-full px-0 py-4 text-lg text-gray-800 placeholder-gray-400 bg-transparent border-0 border-b-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all duration-300"
                    required
                    disabled={isLoading}
                  />
                </div>
                <div className="relative">
                  <input
                    type="text"
                    name="bs_num"
                    value={userData.bs_num}
                    onChange={handleInputChange}
                    placeholder="사업자등록번호"
                    className="w-full px-0 py-4 text-lg text-gray-800 placeholder-gray-400 bg-transparent border-0 border-b-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all duration-300"
                    required
                    disabled={isLoading}
                  />
                </div>
                <div className="relative">
                  <input
                    type="text"
                    name="company_country"
                    value={userData.company_country}
                    onChange={handleInputChange}
                    placeholder="국가"
                    className="w-full px-0 py-4 text-lg text-gray-800 placeholder-gray-400 bg-transparent border-0 border-b-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all duration-300"
                    required
                    disabled={isLoading}
                  />
                </div>
              </div>
              <div className="relative">
                <input
                  type="text"
                  name="company_add"
                  value={userData.company_add}
                  onChange={handleInputChange}
                  placeholder="회사 주소"
                  className="w-full px-0 py-4 text-lg text-gray-800 placeholder-gray-400 bg-transparent border-0 border-b-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all duration-300"
                  required
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* 담당자 정보 섹션 */}
            <div className="space-y-6 mt-8">
              <h3 className="text-lg font-semibold text-gray-700">담당자 정보</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="relative">
                  <input
                    type="text"
                    name="manager_name"
                    value={userData.manager_name}
                    onChange={handleInputChange}
                    placeholder="담당자 이름"
                    className="w-full px-0 py-4 text-lg text-gray-800 placeholder-gray-400 bg-transparent border-0 border-b-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all duration-300"
                    required
                    disabled={isLoading}
                  />
                </div>
                <div className="relative">
                  <input
                    type="text"
                    name="manager_dept"
                    value={userData.manager_dept}
                    onChange={handleInputChange}
                    placeholder="담당자 부서"
                    className="w-full px-0 py-4 text-lg text-gray-800 placeholder-gray-400 bg-transparent border-0 border-b-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all duration-300"
                    required
                    disabled={isLoading}
                  />
                </div>
                <div className="relative">
                  <input
                    type="email"
                    name="manager_email"
                    value={userData.manager_email}
                    onChange={handleInputChange}
                    placeholder="담당자 이메일"
                    className="w-full px-0 py-4 text-lg text-gray-800 placeholder-gray-400 bg-transparent border-0 border-b-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all duration-300"
                    required
                    disabled={isLoading}
                  />
                </div>
                <div className="relative">
                  <input
                    type="tel"
                    name="manager_phone"
                    value={userData.manager_phone}
                    onChange={handleInputChange}
                    placeholder="담당자 연락처"
                    className="w-full px-0 py-4 text-lg text-gray-800 placeholder-gray-400 bg-transparent border-0 border-b-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all duration-300"
                    required
                    disabled={isLoading}
                  />
                </div>
              </div>
            </div>

            {/* Signup Button */}
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
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  회원가입 중...
                </div>
              ) : (
                'Sign Up'
              )}
            </button>

            {/* Back to Login Button */}
            <button
              type="button"
              onClick={() => router.push('/')}
              disabled={isLoading}
              className="w-full bg-white border-2 border-gray-300 text-gray-800 py-4 rounded-2xl hover:bg-gray-50 hover:border-gray-400 transition-all duration-200 font-medium text-lg shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Back to Login
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
