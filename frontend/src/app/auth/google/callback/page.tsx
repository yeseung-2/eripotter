'use client';

import { Suspense, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

function CallbackHandler() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    // URL에서 토큰과 에러 파라미터 확인
    const error = searchParams.get('error');
    const token = searchParams.get('token');

    if (error) {
      console.error('Login error:', error);
      router.push('/');
      return;
    }

    if (token) {
      // 토큰 저장
      localStorage.setItem('access_token', token);
      router.push('/company-profile');
    } else {
      // 토큰이 없으면 홈으로
      router.push('/');
    }
  }, [router, searchParams]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h2 className="text-2xl font-semibold mb-4">로그인 처리 중...</h2>
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
      </div>
    </div>
  );
}

export default function GoogleCallbackPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-semibold mb-4">로딩 중...</h2>
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
        </div>
      </div>
    }>
      <CallbackHandler />
    </Suspense>
  );
}