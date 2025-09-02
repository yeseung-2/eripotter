'use client';

import { useState, useEffect } from 'react';
import Navigation from '@/components/Navigation';
import Image from 'next/image';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

export default function MainPage() {
  const [userType, setUserType] = useState<'supplier' | 'customer'>('supplier');

  // URL에서 토큰 처리
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search);
      const token = urlParams.get('token');
      
      if (token) {
        // JWT 토큰에서 oauth_sub 추출
        try {
          const payload = token.split('.')[1];
          const decodedPayload = JSON.parse(atob(payload));
          const oauth_sub = decodedPayload.oauth_sub;
          
          if (oauth_sub) {
            localStorage.setItem('access_token', token);
            localStorage.setItem('oauth_sub', oauth_sub);
            console.log('OAuth sub saved:', oauth_sub);
            
            // URL에서 토큰 파라미터 제거
            window.history.replaceState({}, document.title, '/main');
          }
        } catch (error) {
          console.error('JWT 토큰 파싱 실패:', error);
        }
      }
    }
  }, []);

  const supplierContent = {
    title: "협력사 메인 페이지",
    subtitle: "ESG 데이터 관리 및 공유",
    description: "환경 데이터 업로드, 평가, 보고서 작성을 통해 지속가능한 공급망을 구축하세요.",
    features: [
      "환경 데이터 업로드 및 관리",
      "ESG 평가 및 분석",
      "데이터 공유 승인",
      "보고서 작성 및 생성",
      "AI 챗봇 상담"
    ]
  };

  const customerContent = {
    title: "고객사 메인 페이지",
    subtitle: "공급망 모니터링 및 데이터 요청",
    description: "협력사의 ESG 데이터를 모니터링하고 필요한 정보를 요청하여 리스크를 관리하세요.",
    features: [
      "협력사 ESG 데이터 모니터링",
      "데이터 공유 요청",
      "리스크 분석 및 대응",
      "공급망 현황 파악"
    ]
  };

  const currentContent = userType === 'supplier' ? supplierContent : customerContent;

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Left Navigation */}
      <Navigation userType={userType} />
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header with Toggle */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">ERI Dashboard</h1>
            
            {/* User Type Toggle */}
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">사용자 유형:</span>
              <div className="flex bg-gray-100 rounded-lg p-1">
                <Button
                  variant={userType === 'supplier' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setUserType('supplier')}
                  className={userType === 'supplier' ? 'bg-blue-600 text-white' : 'text-gray-600'}
                >
                  협력사
                </Button>
                <Button
                  variant={userType === 'customer' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setUserType('customer')}
                  className={userType === 'customer' ? 'bg-blue-600 text-white' : 'text-gray-600'}
                >
                  고객사
                </Button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="flex-1 p-6">
          <div className="relative h-full rounded-xl overflow-hidden">
            {/* Background Image */}
            <div className="absolute inset-0">
              <Image
                src="/background.png"
                alt="Background"
                fill
                className="object-cover"
                priority
              />
              {/* Dark overlay for better text readability */}
              <div className="absolute inset-0 bg-black/30"></div>
            </div>

            {/* Content Overlay */}
            <div className="relative z-10 h-full flex items-center justify-center">
              <Card className="w-full max-w-4xl bg-white/95 backdrop-blur-sm border-0 shadow-2xl">
                <CardContent className="p-8">
                  <div className="text-center mb-8">
                    <h2 className="text-4xl font-bold text-gray-900 mb-4">
                      {currentContent.title}
                    </h2>
                    <p className="text-xl text-blue-600 font-semibold mb-2">
                      {currentContent.subtitle}
                    </p>
                    <p className="text-gray-600 text-lg">
                      {currentContent.description}
                    </p>
                  </div>

                  {/* Features Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {currentContent.features.map((feature, index) => (
                      <div
                        key={index}
                        className="flex items-center space-x-3 p-4 bg-blue-50 rounded-lg border border-blue-200"
                      >
                        <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                          <span className="text-white text-sm font-bold">{index + 1}</span>
                        </div>
                        <span className="text-gray-700 font-medium">{feature}</span>
                      </div>
                    ))}
                  </div>

                  {/* Welcome Message */}
                  <div className="mt-8 text-center">
                    <p className="text-gray-600">
                      좌측 네비게이션을 통해 원하는 서비스에 접근하세요.
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
