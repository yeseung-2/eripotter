'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getCompanyResults, getCompanySolutions, generateSolutions } from '@/lib/api';

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
  levels_json?: Array<{
    level_no: number;
    label: string;
    desc: string;
    score: number;
  }>;
  choices_json?: Array<{
    id: number;
    text: string;
  }>;
  weight?: number; // KESG 테이블의 weight 추가
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
  const [totalScore, setTotalScore] = useState<number>(0);
  const [maxPossibleScore, setMaxPossibleScore] = useState<number>(0);
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
        // 솔루션은 버튼 클릭 시에만 생성되므로 초기 로딩 시에는 불러오지 않음
      } catch (error) {
        console.error('응답 데이터 파싱 오류:', error);
      }
    } else {
      // 응답 데이터가 없어도 결과 페이지에서 데이터를 불러올 수 있도록 시도
      fetchAssessmentResults();
    }
    setLoading(false);
  }, [router]);

  // Assessment 결과가 변경될 때마다 취약 부문 업데이트 및 총 점수 계산
  useEffect(() => {
    if (assessmentResults.length > 0) {
      fetchVulnerableSections();
      calculateTotalScore();
    }
  }, [assessmentResults]);

  const fetchAssessmentResults = async () => {
    try {
      // localStorage에서 회사명 가져오기 (실제로는 사용자 정보에서 가져와야 함)
      const companyName = localStorage.getItem('companyName') || '테스트회사';
      const data = await getCompanyResults(companyName);
      setAssessmentResults(data.assessment_results || []);
    } catch (error) {
      console.error('자가진단 결과 API 호출 오류:', error);
    }
  };

  const fetchVulnerableSections = async () => {
    try {
      // Assessment 결과에서 score=0인 항목을 직접 필터링하여 취약 부문으로 설정
      const vulnerableFromAssessment = assessmentResults.filter(result => result.score === 0);
      setVulnerableSections(vulnerableFromAssessment);
    } catch (error) {
      console.error('취약 부문 데이터 처리 오류:', error);
    }
  };

  const fetchSolutions = async () => {
    try {
      const companyName = localStorage.getItem('companyName') || '테스트회사';
      const data = await getCompanySolutions(companyName);
      setSolutions(data || []);
    } catch (error) {
      console.error('솔루션 API 호출 오류:', error);
    }
  };

  const handleGenerateSolutions = async () => {
    setGeneratingSolutions(true);
    try {
      const companyName = localStorage.getItem('companyName') || '테스트회사';
      const data = await generateSolutions(companyName);
      setSolutions(Array.isArray(data) ? data : []);
      if (data && data.length > 0) {
        alert(`${data.length}개의 솔루션이 성공적으로 생성되었습니다!`);
      } else {
        alert('생성할 취약 부문이 없습니다.');
      }
    } catch (error) {
      console.error('솔루션 생성 API 호출 오류:', error);
      alert('네트워크 오류가 발생했습니다. 다시 시도해주세요.');
    } finally {
      setGeneratingSolutions(false);
    }
  };

  const calculateTotalScore = () => {
    let total = 0;
    let maxScore = 0;
    
    assessmentResults.forEach(result => {
      const weight = result.weight || 1.0; // weight가 없으면 기본값 1.0
      const weightedScore = result.score * weight;
      total += weightedScore;
      
      // 최대 가능 점수 계산 (100점 * weight)
      maxScore += 100 * weight;
    });
    
    setTotalScore(Math.round(total * 100) / 100); // 소수점 2자리까지 반올림
    setMaxPossibleScore(Math.round(maxScore * 100) / 100);
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
      if (!result.level_no) return '미응답';
      
      // levels_json에서 해당 level_no의 desc 찾기
      const levelInfo = result.levels_json?.find(level => level.level_no === result.level_no);
      if (levelInfo) {
        return `${result.level_no}단계: ${levelInfo.desc}`;
      }
      return `${result.level_no}단계`;
    } else if (result.question_type === 'five_choice') {
      if (!result.choice_ids || result.choice_ids.length === 0) return '미응답';
      
      // choices_json에서 선택된 choice들의 text 찾기
      const selectedChoices = result.choices_json?.filter(choice => 
        result.choice_ids?.includes(choice.id)
      );
      
      if (selectedChoices && selectedChoices.length > 0) {
        const choiceTexts = selectedChoices.map(choice => choice.text).join(', ');
        return `${result.choice_ids.length}개 선택: ${choiceTexts}`;
      }
      return `${result.choice_ids.length}개 선택`;
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


  if (responses.length === 0 && assessmentResults.length === 0) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '18px',
        color: '#e74c3c'
      }}>
        <div style={{
          textAlign: 'center',
          maxWidth: '400px',
          padding: '40px'
        }}>
          <h2 style={{
            fontSize: '24px',
            fontWeight: '600',
            color: '#2c3e50',
            marginBottom: '16px'
          }}>
            진단 결과가 없습니다
          </h2>
          <p style={{
            fontSize: '16px',
            color: '#6c757d',
            marginBottom: '24px',
            lineHeight: '1.6'
          }}>
            자가진단을 먼저 진행하시거나,<br />
            기존 진단 결과를 확인해보세요.
          </p>
          <button 
            onClick={() => router.push('/assessment')}
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
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#0056b3';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#007bff';
            }}
          >
            자가진단 시작하기
          </button>
        </div>
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
        
        {/* 총 점수 표시 섹션 */}
        {assessmentResults.length > 0 && (
          <div style={{
            backgroundColor: '#e8f5e8',
            border: '2px solid #28a745',
            borderRadius: '12px',
            padding: '24px',
            marginBottom: '40px',
            textAlign: 'center'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              gap: '20px',
              flexWrap: 'wrap'
            }}>
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '8px'
              }}>
                <span style={{
                  fontSize: '16px',
                  color: '#495057',
                  fontWeight: '500'
                }}>
                  총 점수
                </span>
                <span style={{
                  fontSize: '36px',
                  color: '#28a745',
                  fontWeight: '700'
                }}>
                  {totalScore}점
                </span>
              </div>
              
              <div style={{
                width: '2px',
                height: '60px',
                backgroundColor: '#28a745',
                opacity: '0.3'
              }} />
              
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '8px'
              }}>
                <span style={{
                  fontSize: '16px',
                  color: '#495057',
                  fontWeight: '500'
                }}>
                  최대 점수
                </span>
                <span style={{
                  fontSize: '24px',
                  color: '#6c757d',
                  fontWeight: '600'
                }}>
                  {maxPossibleScore}점
                </span>
              </div>
              

            </div>
            
            <p style={{
              fontSize: '14px',
              color: '#6c757d',
              marginTop: '12px',
              marginBottom: '0'
            }}>
              * 총 점수 = Σ(문항별 점수 × 가중치)
            </p>
          </div>
        )}

        <p style={{
          fontSize: '16px',
          color: '#7f8c8d',
          textAlign: 'center',
          marginBottom: '40px'
        }}>

        </p>

        {/* 자가진단 결과 섹션 */}
        <div style={{ marginBottom: '40px' }}>
          <h3 style={{
            fontSize: '20px',
            fontWeight: '600',
            color: '#2c3e50',
            marginBottom: '20px'
          }}>
            
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
                      alignItems: 'flex-start'
                    }}>
                      <div style={{
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '8px',
                        flex: 1
                      }}>
                        <span style={{
                          fontSize: '14px',
                          color: '#495057',
                          fontWeight: '500'
                        }}>
                          응답 결과:
                        </span>
                        <div style={{
                          fontSize: '14px',
                          color: '#2c3e50',
                          lineHeight: '1.6',
                          backgroundColor: '#f8f9fa',
                          padding: '12px',
                          borderRadius: '6px',
                          border: '1px solid #e9ecef'
                        }}>
                          {getResponseText(result)}
                        </div>
                      </div>
                      <div style={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'flex-end',
                        gap: '8px',
                        marginLeft: '16px'
                      }}>
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
                        {result.weight && result.weight !== 1.0 && (
                          <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px'
                          }}>
                            <span style={{
                              fontSize: '12px',
                              color: '#6c757d',
                              fontWeight: '500'
                            }}>
                              가중치:
                            </span>
                            <span style={{
                              fontSize: '14px',
                              color: '#6c757d',
                              fontWeight: '600'
                            }}>
                              {result.weight}
                            </span>
                          </div>
                        )}
                        {result.weight && result.weight !== 1.0 && (
                          <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px'
                          }}>
                            <span style={{
                              fontSize: '12px',
                              color: '#007bff',
                              fontWeight: '500'
                            }}>
                              가중점수:
                            </span>
                            <span style={{
                              fontSize: '14px',
                              color: '#007bff',
                              fontWeight: '600'
                            }}>
                              {Math.round(result.score * result.weight * 100) / 100}점
                            </span>
                          </div>
                        )}
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
              ⚠️ 다음 부문들은 자가진단 점수가 0점인 취약 영역입니다.
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
                  자가진단 점수가 0점인 취약 부문이 없습니다.
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
                아직 생성된 솔루션이 없습니다. 아래 버튼을 클릭하여 취약 부문에 대한 AI 솔루션을 생성해보세요.
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
                            onClick={handleGenerateSolutions}
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
            {generatingSolutions ? '솔루션 생성 중...' : '취약부문 솔루션 생성하기'}
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
