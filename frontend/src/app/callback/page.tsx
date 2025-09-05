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

        if (error) {
          console.error('Login error:', error);
          router.replace('/');
          return;
        }

        // 토큰 처리 없이 바로 main 페이지로 이동
        console.log('Login successful, redirecting to main page...');
        router.replace('/main');
        
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