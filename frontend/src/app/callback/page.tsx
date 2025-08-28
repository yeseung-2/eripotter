'use client';

import { Suspense, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

function CallbackHandler() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const error = searchParams.get('error');
        const token = searchParams.get('token');

        console.log('Callback received:', { error, token }); // 디버깅용 로그

        if (error) {
          console.error('Login error:', error);
          router.replace('/');
          return;
        }

        if (token) {
          console.log('Token received, storing...'); // 디버깅용 로그
          
          // 토큰 저장
          localStorage.setItem('access_token', token);
          console.log('Token stored successfully'); // 디버깅용 로그
          
          // 강제로 페이지 이동 (replace 사용)
          window.location.replace('/company-profile');
        } else {
          console.error('No token received');
          router.replace('/');
        }
      } catch (error) {
        console.error('Callback handling error:', error);
        router.replace('/');
      }
    };

    handleCallback();
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
