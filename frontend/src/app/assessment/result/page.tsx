'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export interface AssessmentSubmissionRequest {
  question_id: number;
  question_type: string;
  level_no?: number;
  choice_ids?: number[];
}

export interface AssessmentResult {
  id: number;
  company_name: string;
  question_id: number;
  question_type: string;
  level_no?: number;
  choice_ids?: number[];
  score: number;
  timestamp: string;
  item_name: string;
  item_desc: string;
  classification: string;
  domain: string;
}

export interface VulnerableSection {
  id: number;
  company_name: string;
  question_id: number;
  question_type: string;
  level_no?: number;
  choice_ids?: number[];
  score: number;
  timestamp: string;
  item_name: string;
  item_desc: string;
  classification: string;
  domain: string;
}

export interface SolutionSubmissionResponse {
  id: number;
  company_name: string;
  question_id: number;
  sol: string;
  timestamp: string;
  item_name: string;
  item_desc: string;
  classification: string;
  domain: string;
}

export default function AssessmentResultPage() {
  const [responses, setResponses] = useState<AssessmentSubmissionRequest[]>([]);
  const [assessmentResults, setAssessmentResults] = useState<AssessmentResult[]>([]);
  const [vulnerableSections, setVulnerableSections] = useState<VulnerableSection[]>([]);
  const [solutions, setSolutions] = useState<SolutionSubmissionResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [generatingSolutions, setGeneratingSolutions] = useState(false);
  const router = useRouter();

  useEffect(() => {
    // localStorage에서 응답 데이터 가져오기
    const savedResponses = localStorage.getItem('assessmentResponses');
    if (savedResponses) {
      try {
        const parsedResponses = JSON.parse(savedResponses);
        setResponses(parsedResponses);
        
        // 자가진단 결과 데이터 가져오기
        fetchAssessmentResults();
        // 취약 부문 데이터 가져오기
        fetchVulnerableSections();
        // 솔루션은 버튼 클릭 시에만 생성되므로 초기 로딩 시에는 불러오지 않음
      } catch (error) {
        console.error('응답 데이터 파싱 오류:', error);
      }
    } else {
      // 응답 데이터가 없으면 자가진단 페이지로 리다이렉트
      router.push('/assessment');
    }
    setLoading(false);
  }, [router]);

  const fetchAssessmentResults = async () => {
    try {
      const response = await fetch('http://localhost:8002/assessment/assessment-results/테스트회사');
      if (response.ok) {
        const data = await response.json();
        setAssessmentResults(data.assessment_results || []);
      } else {
        console.error('자가진단 결과 데이터를 불러오는데 실패했습니다.');
      }
    } catch (error) {
      console.error('자가진단 결과 API 호출 오류:', error);
    }
  };

  const fetchVulnerableSections = async () => {
    try {
      const response = await fetch('http://localhost:8002/assessment/vulnerable-sections/테스트회사');
      if (response.ok) {
        const data = await response.json();
        setVulnerableSections(data.vulnerable_sections || []);
      } else {
        console.error('취약 부문 데이터를 불러오는데 실패했습니다.');
      }
    } catch (error) {
      console.error('취약 부문 API 호출 오류:', error);
    }
  };

  const fetchSolutions = async () => {
    try {
      const response = await fetch('http://localhost:8080/solution/테스트회사');
      if (response.ok) {
        const data = await response.json();
        setSolutions(data || []);
      } else {
        console.error('솔루션 데이터를 불러오는데 실패했습니다.');
      }
    } catch (error) {
      console.error('솔루션 API 호출 오류:', error);
    }
  };

  const generateSolutions = async () => {
    setGeneratingSolutions(true);
    try {
      const response = await fetch('http://localhost:8080/solution/generate/테스트회사', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setSolutions(data || []);
        if (data && data.length > 0) {
          alert(`${data.length}개의 솔루션이 성공적으로 생성되었습니다!`);
        } else {
          alert('생성할 취약 부문이 없습니다. (score=0인 항목이 없음)');
        }
      } else {
        console.error('솔루션 생성에 실패했습니다.');
        alert('솔루션 생성에 실패했습니다. 다시 시도해주세요.');
      }
    } catch (error) {
      console.error('솔루션 생성 API 호출 오류:', error);
      alert('네트워크 오류가 발생했습니다. 다시 시도해주세요.');
    } finally {
      setGeneratingSolutions(false);
    }
  };

  const handleRetakeAssessment = () => {
    localStorage.removeItem('assessmentResponses');
    router.push('/assessment');
  };

  const handleGoHome = () => {
    localStorage.removeItem('assessmentResponses');
    router.push('/');
  };

  const getResponseText = (result: AssessmentResult) => {
    if (result.question_type === 'five_level' || result.question_type === 'three_level') {
      return result.level_no ? `${result.level_no}단계` : '미응답';
    } else if (result.question_type === 'five_choice') {
      if (result.choice_ids && result.choice_ids.length > 0) {
        return `${result.choice_ids.length}개 선택`;
      } else {
        return '미응답';
      }
    }
    return '미응답';
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '18px',
        color: '#666'
      }}>
        결과를 불러오는 중...
      </div>
    );
  }

  if (responses.length === 0) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '18px',
        color: '#e74c3c'
      }}>
        응답 데이터를 찾을 수 없습니다.
      </div>
    );
  }

  return (
    <div style={{
      maxWidth: '1000px',
      margin: '0 auto',
      padding: '40px 20px',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      backgroundColor: '#f8f9fa',
      minHeight: '100vh'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '40px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        marginBottom: '30px'
      }}>
        <h1 style={{
          fontSize: '32px',
          fontWeight: '700',
          color: '#2c3e50',
          marginBottom: '8px',
          textAlign: 'center'
        }}>
          자가진단 결과
        </h1>
        <p style={{
          fontSize: '16px',
          color: '#7f8c8d',
          textAlign: 'center',
          marginBottom: '40px'
        }}>
          ESG 자가진단 결과를 확인하세요.
        </p>

        {/* 자가진단 결과 섹션 */}
        <div style={{ marginBottom: '40px' }}>
          <h3 style={{
            fontSize: '20px',
            fontWeight: '600',
            color: '#2c3e50',
            marginBottom: '20px'
          }}>
            자가진단 결과
          </h3>
          
          <div style={{
            backgroundColor: '#f8f9fa',
            borderRadius: '8px',
            padding: '20px',
            border: '1px solid #e9ecef'
          }}>
            {assessmentResults.length > 0 ? (
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '16px'
              }}>
                {assessmentResults.map((result, index) => (
                  <div key={`${result.company_name}-${result.question_id}-${index}`} style={{
                    backgroundColor: 'white',
                    border: '1px solid #dee2e6',
                    borderRadius: '8px',
                    padding: '20px',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                  }}>
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'flex-start',
                      marginBottom: '12px'
                    }}>
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px'
                      }}>
                        <span style={{
                          backgroundColor: '#007bff',
                          color: 'white',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '14px',
                          fontWeight: '500',
                          minWidth: '24px',
                          textAlign: 'center'
                        }}>
                          {result.question_id}
                        </span>
                        <h4 style={{
                          fontSize: '18px',
                          fontWeight: '600',
                          color: '#2c3e50',
                          margin: '0'
                        }}>
                          {result.item_name}
                        </h4>
                      </div>
                      <div style={{
                        display: 'flex',
                        gap: '8px',
                        alignItems: 'center'
                      }}>
                        <span style={{
                          backgroundColor: '#6c757d',
                          color: 'white',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '12px',
                          fontWeight: '500'
                        }}>
                          {result.classification}
                        </span>
                        <span style={{
                          backgroundColor: '#17a2b8',
                          color: 'white',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '12px',
                          fontWeight: '500'
                        }}>
                          {result.domain}
                        </span>
                      </div>
                    </div>
                    
                    <p style={{
                      fontSize: '14px',
                      color: '#6c757d',
                      lineHeight: '1.6',
                      marginBottom: '12px'
                    }}>
                      {result.item_desc}
                    </p>
                    
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}>
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '16px'
                      }}>
                        <span style={{
                          fontSize: '14px',
                          color: '#495057',
                          fontWeight: '500'
                        }}>
                          응답 결과: <strong>{getResponseText(result)}</strong>
                        </span>
                        <span style={{
                          fontSize: '14px',
                          color: '#495057',
                          fontWeight: '500'
                        }}>
                          문항 유형: <strong>{result.question_type}</strong>
                        </span>
                      </div>
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                      }}>
                        <span style={{
                          fontSize: '14px',
                          color: '#28a745',
                          fontWeight: '600'
                        }}>
                          점수:
                        </span>
                        <span style={{
                          fontSize: '18px',
                          color: '#28a745',
                          fontWeight: '700'
                        }}>
                          {result.score}점
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{
                backgroundColor: '#f8f9fa',
                border: '1px solid #dee2e6',
                borderRadius: '8px',
                padding: '40px',
                textAlign: 'center'
              }}>
                <p style={{
                  fontSize: '16px',
                  color: '#6c757d',
                  margin: '0'
                }}>
                  자가진단 결과 데이터를 불러올 수 없습니다.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* 취약 부문 섹션 */}
        <div style={{ marginBottom: '40px' }}>
          <h3 style={{
            fontSize: '20px',
            fontWeight: '600',
            color: '#2c3e50',
            marginBottom: '20px'
          }}>
            취약 부문
          </h3>
          
          <div style={{
            backgroundColor: '#fff3cd',
            border: '2px solid #ffc107',
            borderRadius: '8px',
            padding: '20px',
            marginBottom: '20px'
          }}>
            <p style={{
              fontSize: '16px',
              color: '#856404',
              marginBottom: '0',
              textAlign: 'center',
              fontWeight: '500'
            }}>
              ⚠️ 다음 부문들은 개선이 필요한 취약 영역입니다.
            </p>
          </div>
          
          {vulnerableSections.length > 0 ? (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '16px'
            }}>
              {vulnerableSections.map((section, index) => (
                <div key={`vulnerable-${section.company_name}-${section.question_id}-${index}`} style={{
                  backgroundColor: 'white',
                  border: '1px solid #dee2e6',
                  borderRadius: '8px',
                  padding: '20px',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }}>
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    marginBottom: '12px'
                  }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px'
                    }}>
                      <span style={{
                        backgroundColor: '#dc3545',
                        color: 'white',
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '14px',
                        fontWeight: '500',
                        minWidth: '24px',
                        textAlign: 'center'
                      }}>
                        {section.question_id}
                      </span>
                      <h4 style={{
                        fontSize: '18px',
                        fontWeight: '600',
                        color: '#2c3e50',
                        margin: '0'
                      }}>
                        {section.item_name}
                      </h4>
                    </div>
                    <div style={{
                      display: 'flex',
                      gap: '8px',
                      alignItems: 'center'
                    }}>
                      <span style={{
                        backgroundColor: '#dc3545',
                        color: 'white',
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: '500'
                      }}>
                        {section.classification}
                      </span>
                      <span style={{
                        backgroundColor: '#6c757d',
                        color: 'white',
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: '500'
                      }}>
                        {section.domain}
                      </span>
                    </div>
                  </div>
                  
                  <p style={{
                    fontSize: '14px',
                    color: '#6c757d',
                    lineHeight: '1.6',
                    marginBottom: '12px'
                  }}>
                    {section.item_desc}
                  </p>
                  
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}>
                    <span style={{
                      fontSize: '14px',
                      color: '#dc3545',
                      fontWeight: '600'
                    }}>
                      점수:
                    </span>
                    <span style={{
                      fontSize: '16px',
                      color: '#dc3545',
                      fontWeight: '700'
                    }}>
                      {section.score}점
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div style={{
              backgroundColor: '#f8f9fa',
              border: '1px solid #dee2e6',
              borderRadius: '8px',
              padding: '40px',
              textAlign: 'center'
            }}>
              <p style={{
                fontSize: '16px',
                color: '#6c757d',
                margin: '0'
              }}>
                취약 부문이 없습니다. 모든 영역에서 양호한 성과를 보이고 있습니다.
              </p>
            </div>
          )}
        </div>

        {/* 솔루션 섹션 */}
        <div style={{ marginBottom: '40px' }}>
          <h3 style={{
            fontSize: '20px',
            fontWeight: '600',
            color: '#2c3e50',
            marginBottom: '20px'
          }}>
            취약 부문 솔루션
          </h3>
          
          {solutions.length > 0 ? (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '16px'
            }}>
              {solutions.map((solution, index) => (
                <div key={`solution-${solution.company_name}-${solution.question_id}-${index}`} style={{
                  backgroundColor: 'white',
                  border: '1px solid #dee2e6',
                  borderRadius: '8px',
                  padding: '20px',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }}>
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    marginBottom: '12px'
                  }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px'
                    }}>
                      <span style={{
                        backgroundColor: '#28a745',
                        color: 'white',
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '14px',
                        fontWeight: '500',
                        minWidth: '24px',
                        textAlign: 'center'
                      }}>
                        {solution.question_id}
                      </span>
                      <h4 style={{
                        fontSize: '18px',
                        fontWeight: '600',
                        color: '#2c3e50',
                        margin: '0'
                      }}>
                        {solution.item_name}
                      </h4>
                    </div>
                    <div style={{
                      display: 'flex',
                      gap: '8px',
                      alignItems: 'center'
                    }}>
                      <span style={{
                        backgroundColor: '#28a745',
                        color: 'white',
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: '500'
                      }}>
                        {solution.classification}
                      </span>
                      <span style={{
                        backgroundColor: '#17a2b8',
                        color: 'white',
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: '500'
                      }}>
                        {solution.domain}
                      </span>
                    </div>
                  </div>
                  
                  <p style={{
                    fontSize: '14px',
                    color: '#6c757d',
                    lineHeight: '1.6',
                    marginBottom: '12px'
                  }}>
                    {solution.item_desc}
                  </p>
                  
                  <div style={{
                    backgroundColor: '#e8f5e8',
                    border: '1px solid #c3e6c3',
                    borderRadius: '8px',
                    padding: '16px',
                    marginTop: '12px'
                  }}>
                    <h5 style={{
                      fontSize: '16px',
                      fontWeight: '600',
                      color: '#28a745',
                      marginBottom: '8px'
                    }}>
                      AI 솔루션 제안:
                    </h5>
                    <div 
                      dangerouslySetInnerHTML={{ __html: solution.sol }}
                      style={{
                        fontSize: '14px',
                        color: '#495057',
                        lineHeight: '1.6'
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div style={{
              backgroundColor: '#f8f9fa',
              border: '1px solid #dee2e6',
              borderRadius: '8px',
              padding: '40px',
              textAlign: 'center'
            }}>
              <p style={{
                fontSize: '16px',
                color: '#6c757d',
                margin: '0',
                marginBottom: '20px'
              }}>
                아직 생성된 솔루션이 없습니다. 아래 버튼을 클릭하여 취약 부문(score=0)에 대한 AI 솔루션을 생성해보세요.
              </p>
            </div>
          )}
        </div>

        <div style={{
          display: 'flex',
          gap: '16px',
          justifyContent: 'center',
          flexWrap: 'wrap'
        }}>
          <button 
            onClick={generateSolutions}
            disabled={generatingSolutions}
            style={{
              backgroundColor: generatingSolutions ? '#6c757d' : '#28a745',
              color: 'white',
              border: 'none',
              padding: '16px 24px',
              fontSize: '16px',
              fontWeight: '600',
              borderRadius: '8px',
              cursor: generatingSolutions ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s ease',
              minWidth: '200px',
              opacity: generatingSolutions ? 0.7 : 1
            }}
            onMouseEnter={(e) => {
              if (!generatingSolutions) {
                e.currentTarget.style.backgroundColor = '#218838';
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 6px 12px rgba(40, 167, 69, 0.3)';
              }
            }}
            onMouseLeave={(e) => {
              if (!generatingSolutions) {
                e.currentTarget.style.backgroundColor = '#28a745';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }
            }}
          >
            {generatingSolutions ? '솔루션 생성 중...' : '취약 부문 솔루션 생성하기'}
          </button>
          
          <button 
            onClick={handleRetakeAssessment}
            style={{
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              padding: '16px 24px',
              fontSize: '16px',
              fontWeight: '600',
              borderRadius: '8px',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              minWidth: '160px'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#0056b3';
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 6px 12px rgba(0, 123, 255, 0.3)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#007bff';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            다시 진단하기
          </button>
          
          <button 
            onClick={handleGoHome}
            style={{
              backgroundColor: '#6c757d',
              color: 'white',
              border: 'none',
              padding: '16px 24px',
              fontSize: '16px',
              fontWeight: '600',
              borderRadius: '8px',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              minWidth: '160px'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#545b62';
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 6px 12px rgba(108, 117, 125, 0.3)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#6c757d';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            홈으로 돌아가기
          </button>
        </div>
      </div>
    </div>
  );
}
