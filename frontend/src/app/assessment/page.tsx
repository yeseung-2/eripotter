'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import axios from '@/lib/axios';

export default function AssessmentMainPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isLoading, setIsLoading] = useState(false);
  const [companyName, setCompanyName] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // OAuth Sub로 회사명 조회
  useEffect(() => {
    const fetchCompanyName = async () => {
      try {
        const oauthSub = searchParams.get('oauth_sub');
        
        if (!oauthSub) {
          setError('OAuth 인증 정보가 없습니다. 다시 로그인해주세요.');
          return;
        }

        console.log('OAuth Sub 조회:', oauthSub);
        
        // OAuth Sub로 회사명 조회
        const response = await axios.get(`/api/account/accounts/me?oauth_sub=${oauthSub}`);
        
        if (response.data && response.data.company_name) {
          const company = response.data.company_name;
          setCompanyName(company);
          localStorage.setItem('companyName', company);
          console.log('회사명 저장 성공:', company);
        } else {
          setError('회사 정보가 설정되지 않았습니다. 프로필을 먼저 설정해주세요.');
          console.log('회사명이 설정되지 않음');
        }
      } catch (error: any) {
        console.error('회사명 조회 실패:', error);
        if (error.response?.status === 404) {
          setError('계정 정보를 찾을 수 없습니다. 회원가입을 먼저 진행해주세요.');
        } else {
          setError('회사 정보 조회 중 오류가 발생했습니다. 다시 시도해주세요.');
        }
      }
    };

    fetchCompanyName();
  }, [searchParams]);

  const handleStartAssessment = () => {
    if (!companyName) {
      alert('회사 정보를 먼저 설정해주세요.');
      return;
    }
    
    setIsLoading(true);
    // localStorage에서 기존 응답 데이터가 있다면 제거
    localStorage.removeItem('assessmentResponses');
    
    // oauth_sub를 쿼리 파라미터로 전달
    const oauthSub = searchParams.get('oauth_sub');
    if (oauthSub) {
      router.push(`/assessment/survey?oauth_sub=${oauthSub}`);
    } else {
      router.push('/assessment/survey');
    }
  };

  const handleViewResults = () => {
    if (!companyName) {
      alert('회사 정보를 먼저 설정해주세요.');
      return;
    }
    
    setIsLoading(true);
    // localStorage에서 기존 응답 데이터가 없다면 빈 배열로 초기화
    if (!localStorage.getItem('assessmentResponses')) {
      localStorage.setItem('assessmentResponses', JSON.stringify([]));
    }
    
    // oauth_sub를 쿼리 파라미터로 전달
    const oauthSub = searchParams.get('oauth_sub');
    if (oauthSub) {
      router.push(`/assessment/result?oauth_sub=${oauthSub}`);
    } else {
      router.push('/assessment/result');
    }
  };

  // 에러가 있는 경우
  if (error) {
    return (
      <div style={{
        maxWidth: '800px',
        margin: '0 auto',
        padding: '40px 20px',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        backgroundColor: '#f8f9fa',
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{
          backgroundColor: 'white',
          borderRadius: '16px',
          padding: '60px 40px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
          textAlign: 'center',
          width: '100%',
          maxWidth: '600px'
        }}>
          <div style={{
            fontSize: '48px',
            marginBottom: '24px'
          }}>
            ⚠️
          </div>
          <h2 style={{
            fontSize: '24px',
            fontWeight: '600',
            color: '#dc3545',
            marginBottom: '16px'
          }}>
            인증 오류
          </h2>
          <p style={{
            fontSize: '16px',
            color: '#6c757d',
            marginBottom: '24px',
            lineHeight: '1.6'
          }}>
            {error}
          </p>
          <button 
            onClick={() => window.location.href = '/'}
            style={{
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              fontSize: '16px',
              fontWeight: '600',
              borderRadius: '8px',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            홈으로 돌아가기
          </button>
        </div>
      </div>
    );
  }

  // 로딩 중인 경우
  if (!companyName) {
    return (
      <div style={{
        maxWidth: '800px',
        margin: '0 auto',
        padding: '40px 20px',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        backgroundColor: '#f8f9fa',
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{
          backgroundColor: 'white',
          borderRadius: '16px',
          padding: '60px 40px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
          textAlign: 'center',
          width: '100%',
          maxWidth: '600px'
        }}>
          <div style={{
            fontSize: '48px',
            marginBottom: '24px'
          }}>
            🔄
          </div>
          <h2 style={{
            fontSize: '24px',
            fontWeight: '600',
            color: '#2c3e50',
            marginBottom: '16px'
          }}>
            회사 정보 확인 중...
          </h2>
          <p style={{
            fontSize: '16px',
            color: '#6c757d',
            marginBottom: '0',
            lineHeight: '1.6'
          }}>
            잠시만 기다려주세요.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      maxWidth: '800px',
      margin: '0 auto',
      padding: '40px 20px',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      backgroundColor: '#f8f9fa',
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '16px',
        padding: '60px 40px',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
        textAlign: 'center',
        width: '100%',
        maxWidth: '600px'
      }}>
        {/* 헤더 섹션 */}
        <div style={{
          marginBottom: '50px'
        }}>
          <div style={{
            width: '80px',
            height: '80px',
            backgroundColor: '#007bff',
            borderRadius: '50%',
            margin: '0 auto 24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 16px rgba(0, 123, 255, 0.3)'
          }}>
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
              <path d="M9 12l2 2 4-4"/>
              <path d="M21 12c-1 0-2-1-2-2s1-2 2-2 2 1 2 2-1 2-2 2z"/>
              <path d="M3 12c1 0 2-1 2-2s-1-2-2-2-2 1-2 2 1 2 2 2z"/>
              <path d="M12 3c0 1-1 2-2 2s-2 1-2 2 1 2 2 2 2-1 2-2 1-2 2-2 2-1 2-2-1-2-2-2z"/>
            </svg>
          </div>
          
          <h1 style={{
            fontSize: '36px',
            fontWeight: '700',
            color: '#2c3e50',
            marginBottom: '16px'
          }}>
            ESG 자가진단
          </h1>
          
          <p style={{
            fontSize: '18px',
            color: '#7f8c8d',
            marginBottom: '8px'
          }}>
            현재 로그인된 회사: <strong style={{ color: '#007bff' }}>{companyName}</strong>
          </p>
          
          <p style={{
            fontSize: '16px',
            color: '#6c757d',
            lineHeight: '1.6'
          }}>
            ESG 경영 수준을 진단하고 개선 방안을 제시받으세요
          </p>
        </div>

        {/* 버튼 섹션 */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '20px'
        }}>
          <button 
            onClick={handleStartAssessment}
            disabled={isLoading}
            style={{
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              padding: '20px 32px',
              fontSize: '18px',
              fontWeight: '600',
              borderRadius: '12px',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s ease',
              opacity: isLoading ? 0.7 : 1,
              boxShadow: '0 4px 16px rgba(0, 123, 255, 0.3)'
            }}
            onMouseEnter={(e) => {
              if (!isLoading) {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 6px 20px rgba(0, 123, 255, 0.4)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isLoading) {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 16px rgba(0, 123, 255, 0.3)';
              }
            }}
          >
            {isLoading ? '진행 중...' : '자가진단 시작하기'}
          </button>
          
          <button 
            onClick={handleViewResults}
            disabled={isLoading}
            style={{
              backgroundColor: 'white',
              color: '#007bff',
              border: '2px solid #007bff',
              padding: '18px 32px',
              fontSize: '16px',
              fontWeight: '600',
              borderRadius: '12px',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s ease',
              opacity: isLoading ? 0.7 : 1
            }}
            onMouseEnter={(e) => {
              if (!isLoading) {
                e.currentTarget.style.backgroundColor = '#f8f9fa';
                e.currentTarget.style.transform = 'translateY(-2px)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isLoading) {
                e.currentTarget.style.backgroundColor = 'white';
                e.currentTarget.style.transform = 'translateY(0)';
              }
            }}
          >
            {isLoading ? '진행 중...' : '기존 결과 보기'}
          </button>
        </div>

        {/* 안내 섹션 */}
        <div style={{
          marginTop: '40px',
          padding: '24px',
          backgroundColor: '#f8f9fa',
          borderRadius: '12px',
          border: '1px solid #e9ecef'
        }}>
          <h3 style={{
            fontSize: '16px',
            fontWeight: '600',
            color: '#2c3e50',
            marginBottom: '12px'
          }}>
            📋 자가진단 안내
          </h3>
          <ul style={{
            fontSize: '14px',
            color: '#6c757d',
            lineHeight: '1.6',
            textAlign: 'left',
            margin: '0',
            paddingLeft: '20px'
          }}>
            <li>자가진단은 약 10-15분 정도 소요됩니다</li>
            <li>답변은 언제든지 수정할 수 있습니다</li>
            <li>진단 완료 후 상세한 결과와 개선 방안을 확인할 수 있습니다</li>
            <li>진단 결과는 회사별로 안전하게 저장됩니다</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
