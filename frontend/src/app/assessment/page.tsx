'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function AssessmentMainPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const handleStartAssessment = () => {
    setIsLoading(true);
    // localStorage에서 기존 응답 데이터가 있다면 제거
    localStorage.removeItem('assessmentResponses');
    router.push('/assessment/survey');
  };

  const handleViewResults = () => {
    setIsLoading(true);
    router.push('/assessment/result');
  };

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
            marginBottom: '16px',
            lineHeight: '1.2'
          }}>
            ESG 자가진단
          </h1>
          
          <p style={{
            fontSize: '18px',
            color: '#6c757d',
            lineHeight: '1.6',
            marginBottom: '0'
          }}>
            환경, 사회, 지배구조(ESG) 자가진단을 통해<br />
            귀사의 ESG 현황을 파악하고 개선 방향을 제시받으세요
          </p>
        </div>

        {/* 기능 설명 섹션 */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '24px',
          marginBottom: '50px'
        }}>
          <div style={{
            backgroundColor: '#f8f9fa',
            borderRadius: '12px',
            padding: '24px',
            border: '2px solid #e9ecef'
          }}>
            <div style={{
              width: '48px',
              height: '48px',
              backgroundColor: '#28a745',
              borderRadius: '50%',
              margin: '0 auto 16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
            </div>
            <h3 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#2c3e50',
              marginBottom: '8px'
            }}>
              자가진단 진행
            </h3>
            <p style={{
              fontSize: '14px',
              color: '#6c757d',
              lineHeight: '1.5',
              margin: '0'
            }}>
              ESG 관련 문항에 답변하여<br />
              현재 상태를 진단해보세요
            </p>
          </div>

          <div style={{
            backgroundColor: '#f8f9fa',
            borderRadius: '12px',
            padding: '24px',
            border: '2px solid #e9ecef'
          }}>
            <div style={{
              width: '48px',
              height: '48px',
              backgroundColor: '#17a2b8',
              borderRadius: '50%',
              margin: '0 auto 16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14,2 14,8 20,8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
                <polyline points="10,9 9,9 8,9"/>
              </svg>
            </div>
            <h3 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#2c3e50',
              marginBottom: '8px'
            }}>
              결과 확인
            </h3>
            <p style={{
              fontSize: '14px',
              color: '#6c757d',
              lineHeight: '1.5',
              margin: '0'
            }}>
              진단 결과와 취약 부문<br />
              솔루션을 확인하세요
            </p>
          </div>
        </div>

        {/* 버튼 섹션 */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '16px'
        }}>
          <button 
            onClick={handleStartAssessment}
            disabled={isLoading}
            style={{
              backgroundColor: '#28a745',
              color: 'white',
              border: 'none',
              padding: '20px 32px',
              fontSize: '18px',
              fontWeight: '600',
              borderRadius: '12px',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s ease',
              width: '100%',
              opacity: isLoading ? 0.7 : 1,
              boxShadow: '0 4px 12px rgba(40, 167, 69, 0.3)'
            }}
            onMouseEnter={(e) => {
              if (!isLoading) {
                e.currentTarget.style.backgroundColor = '#218838';
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 6px 20px rgba(40, 167, 69, 0.4)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isLoading) {
                e.currentTarget.style.backgroundColor = '#28a745';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(40, 167, 69, 0.3)';
              }
            }}
          >
            {isLoading ? (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}>
                <div style={{
                  width: '16px',
                  height: '16px',
                  border: '2px solid transparent',
                  borderTop: '2px solid white',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }} />
                처리 중...
              </div>
            ) : (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M5 12h14"/>
                  <path d="m12 5 7 7-7 7"/>
                </svg>
                자가진단 하러가기
              </div>
            )}
          </button>

          <button 
            onClick={handleViewResults}
            disabled={isLoading}
            style={{
              backgroundColor: 'transparent',
              color: '#007bff',
              border: '2px solid #007bff',
              padding: '18px 32px',
              fontSize: '16px',
              fontWeight: '600',
              borderRadius: '12px',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s ease',
              width: '100%',
              opacity: isLoading ? 0.7 : 1
            }}
            onMouseEnter={(e) => {
              if (!isLoading) {
                e.currentTarget.style.backgroundColor = '#007bff';
                e.currentTarget.style.color = 'white';
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 6px 20px rgba(0, 123, 255, 0.3)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isLoading) {
                e.currentTarget.style.backgroundColor = 'transparent';
                e.currentTarget.style.color = '#007bff';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }
            }}
          >
            자가진단 결과 보기
          </button>
        </div>

        {/* 추가 정보 섹션 */}
        <div style={{
          marginTop: '40px',
          padding: '24px',
          backgroundColor: '#f8f9fa',
          borderRadius: '12px',
          border: '1px solid #e9ecef'
        }}>
          <h4 style={{
            fontSize: '16px',
            fontWeight: '600',
            color: '#495057',
            marginBottom: '12px'
          }}>
            💡 자가진단 안내
          </h4>
          <ul style={{
            fontSize: '14px',
            color: '#495057',
            lineHeight: '1.8',
            margin: '0',
            paddingLeft: '20px',
            textAlign: 'left'
            }}>
            <li><strong>소요 시간:</strong> 평균 10~15분이 소요됩니다.</li>
            <li><strong>진단 범위:</strong> 환경(E), 사회(S), 지배구조(G) 3개 영역으로 구성되어 있습니다.</li>
            <li><strong>필요 자료:</strong> 최근 5개년 경영/환경 데이터(사업보고서, 내부 경영자료 등)를 참고하면 더욱 정확하게 응답할 수 있습니다.</li>
            <li><strong>진단 결과:</strong> 현재 상태 분석과 함께 취약 부문에 대한 맞춤형 솔루션이 제공됩니다.</li>
            <li><strong>진행 방법:</strong> 중간 저장은 불가능하므로 한 번에 완료해 주세요.</li>
            </ul>
        </div>
        <style jsx>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    </div>
  );
}
