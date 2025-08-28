'use client';

import { Suspense, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import axios from '@/lib/axios';

function CallbackHandler() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // OAuth 콜백 처리
        const response = await axios.get('/api/v1/auth/google/callback', {
          params: {
            code: searchParams.get('code'),
            state: searchParams.get('state')
          }
        });

        // 토큰 저장
        if (response.data.access_token) {
          localStorage.setItem('access_token', response.data.access_token);
          
          // 사용자 정보 조회
          const userResponse = await axios.get('/api/v1/accounts/me', {
            headers: {
              Authorization: `Bearer ${response.data.access_token}`
            }
          });

          // 기업 프로필이 없으면 프로필 페이지로, 있으면 대시보드로
          if (!userResponse.data.company_name) {
            router.push('/company-profile');
          } else {
            router.push('/dashboard');
          }
        }
      } catch (error) {
        console.error('OAuth callback error:', error);
        alert('로그인 처리 중 오류가 발생했습니다.');
        router.push('/');
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
