'use client';

import { useState, useEffect, Suspense } from 'react';
import { Drawer } from '@/components/Drawer';
import { getKesgItems, submitAssessment } from '@/lib/api';
import type { KesgItem, KesgResponse, AssessmentSubmissionRequest, AssessmentSubmissionResponse, AssessmentRequest, LevelData, ChoiceData } from '@/types/assessment';
import { useRouter, useSearchParams } from 'next/navigation';
import axios from '@/lib/axios';

// Response type for managing form state
type ResponseData = {
  level_no?: number;
  choice_ids?: number[];
};

// AssessmentPage 컴포넌트를 별도로 분리
function AssessmentPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [kesgItems, setKesgItems] = useState<KesgItem[]>([]);
  const [responses, setResponses] = useState<Record<number, ResponseData>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState<KesgItem | null>(null);
  const [companyName, setCompanyName] = useState<string | null>(null);

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
          console.log('회사명 조회 성공:', company);
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

  const handleInfoClick = (question: KesgItem, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setSelectedQuestion(question);
    setDrawerOpen(true);
  };

  const handleDrawerClose = () => {
    setDrawerOpen(false);
    setSelectedQuestion(null);
  };

  // KESG 데이터 불러오기
  useEffect(() => {
    const fetchKesgData = async () => {
      try {
        const data = await getKesgItems();
        console.log('API 응답 데이터:', data);

        // 응답 데이터 구조에 따른 처리
        if (Array.isArray(data)) {
          // 응답이 배열로 직접 오는 경우
          setKesgItems(data);
        } else if (data && Array.isArray(data.items)) {
          // 응답이 { items: [...] } 구조인 경우
          setKesgItems(data.items);
        } else {
          // 그 외 구조인 경우
          console.error('예상치 못한 API 응답 구조:', data);
          setKesgItems([]);
        }
      } catch (err) {
        console.error('API 호출 오류:', err);
        setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
      } finally {
        setLoading(false);
      }
    };

    fetchKesgData();
  }, []);

  // 단계형 응답 처리
  const handleLevelChange = (questionId: number, levelNo: number) => {
    setResponses((prev) => ({
      ...prev,
      [questionId]: { level_no: levelNo },
    }));
  };

  // 선택형 응답 처리
  const handleChoiceChange = (questionId: number, choiceId: number, checked: boolean) => {
    setResponses((prev) => {
      const currentChoices = prev[questionId]?.choice_ids || [];
      let newChoices: number[];

      if (checked) {
        newChoices = [...currentChoices, choiceId];
      } else {
        newChoices = currentChoices.filter((id: number) => id !== choiceId);
      }

      return {
        ...prev,
        [questionId]: { choice_ids: newChoices },
      };
    });
  };

  // 폼 제출 처리
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // 회사명 확인 및 디버깅
    console.log('현재 companyName 상태:', companyName);
    console.log('현재 searchParams:', searchParams.toString());
    
    if (!companyName) {
      alert('회사 정보가 없습니다. 자가진단 페이지로 이동합니다.');
      router.push('/assessment');
      return;
    }

    const formattedResponses: AssessmentSubmissionRequest[] = kesgItems.map((item) => {
      const response = responses[item.id];

      if (item.question_type === 'five_level' || item.question_type === 'three_level') {
        return {
          question_id: item.id,
          question_type: item.question_type || '',
          level_no: response?.level_no,
        };
      } else if (item.question_type === 'five_choice') {
        return {
          question_id: item.id,
          question_type: item.question_type || '',
          choice_ids: response?.choice_ids,
        };
      }

      return {
        question_id: item.id,
        question_type: item.question_type || '',
      };
    });

    console.log('제출된 응답:', formattedResponses);
    console.log('API 호출 시 전송할 데이터:', {
      company_name: companyName,
      responses: formattedResponses
    });
    
    try {
      // API 호출하여 실제로 데이터 저장
      const result = await submitAssessment({
        company_name: companyName,
        responses: formattedResponses
      });

      console.log('자가진단 응답이 성공적으로 저장되었습니다:', result);
      // 응답 데이터를 localStorage에 저장하고 결과 페이지로 이동
      localStorage.setItem('assessmentResponses', JSON.stringify(formattedResponses));
      
      // oauth_sub를 쿼리 파라미터로 전달
      const oauthSub = searchParams.get('oauth_sub');
      if (oauthSub) {
        router.push(`/assessment/result?oauth_sub=${oauthSub}`);
      } else {
        router.push('/assessment/result');
      }
    } catch (error) {
      console.error('API 호출 오류:', error);
      alert('네트워크 오류가 발생했습니다. 다시 시도해주세요.');
    }
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
        데이터를 불러오는 중...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '18px',
        color: '#e74c3c'
      }}>
        오류: {error}
      </div>
    );
  }

  // kesgItems가 배열이 아닌 경우 처리
  if (!Array.isArray(kesgItems)) {
    console.error('kesgItems가 배열이 아닙니다:', kesgItems);
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '18px',
        color: '#e74c3c'
      }}>
        데이터 형식 오류: kesgItems가 배열이 아닙니다. (타입: {typeof kesgItems})
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
      minHeight: '100vh'
    }}>
      {/* 헤더 */}
      <div style={{
        textAlign: 'center',
        marginBottom: '40px'
      }}>
        <h1 style={{
          fontSize: '32px',
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
          현재 회사: <strong style={{ color: '#007bff' }}>{companyName}</strong>
        </p>
        <p style={{
          fontSize: '16px',
          color: '#6c757d'
        }}>
          각 문항에 대해 가장 적절한 답변을 선택해주세요
        </p>
      </div>

      {/* 폼 */}
      <form onSubmit={handleSubmit}>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '24px'
        }}>
          {kesgItems.map((item) => (
            <div key={item.id} style={{
              backgroundColor: 'white',
              borderRadius: '16px',
              padding: '24px',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
              border: '1px solid #e9ecef'
            }}>
              {/* 문항 정보 */}
              <div style={{
                marginBottom: '20px'
              }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  marginBottom: '12px'
                }}>
                  <span style={{
                    backgroundColor: '#007bff',
                    color: 'white',
                    padding: '4px 12px',
                    borderRadius: '20px',
                    fontSize: '14px',
                    fontWeight: '600'
                  }}>
                    {item.classification}
                  </span>
                  <span style={{
                    backgroundColor: '#28a745',
                    color: 'white',
                    padding: '4px 12px',
                    borderRadius: '20px',
                    fontSize: '14px',
                    fontWeight: '600'
                  }}>
                    {item.domain}
                  </span>
                  <span style={{
                    backgroundColor: '#6f42c1',
                    color: 'white',
                    padding: '4px 12px',
                    borderRadius: '20px',
                    fontSize: '14px',
                    fontWeight: '600'
                  }}>
                    {item.category}
                  </span>
                </div>
                
                <h3 style={{
                  fontSize: '18px',
                  fontWeight: '600',
                  color: '#2c3e50',
                  marginBottom: '8px',
                  lineHeight: '1.4'
                }}>
                  {item.item_name}
                </h3>
                
                <p style={{
                  fontSize: '16px',
                  color: '#6c757d',
                  lineHeight: '1.6',
                  marginBottom: '16px'
                }}>
                  {item.item_desc}
                </p>

                <button
                  type="button"
                  onClick={(e) => handleInfoClick(item, e)}
                  style={{
                    backgroundColor: 'transparent',
                    border: '1px solid #007bff',
                    color: '#007bff',
                    padding: '8px 16px',
                    borderRadius: '8px',
                    fontSize: '14px',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#007bff';
                    e.currentTarget.style.color = 'white';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'transparent';
                    e.currentTarget.style.color = '#007bff';
                  }}
                >
                  ℹ️ 상세 정보 보기
                </button>
              </div>

              {/* 응답 입력 */}
              <div>
                {item.question_type === 'five_level' && (
                  <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '12px'
                  }}>
                    <label style={{
                      fontSize: '16px',
                      fontWeight: '600',
                      color: '#2c3e50',
                      marginBottom: '8px'
                    }}>
                      현재 수준을 선택해주세요:
                    </label>
                    <div style={{
                      display: 'flex',
                      gap: '8px',
                      flexWrap: 'wrap'
                    }}>
                      {[1, 2, 3, 4, 5].map((level) => (
                        <label key={level} style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          cursor: 'pointer'
                        }}>
                          <input
                            type="radio"
                            name={`question_${item.id}`}
                            value={level}
                            checked={responses[item.id]?.level_no === level}
                            onChange={() => handleLevelChange(item.id, level)}
                            style={{
                              width: '18px',
                              height: '18px',
                              accentColor: '#007bff'
                            }}
                          />
                          <span style={{
                            fontSize: '16px',
                            color: '#2c3e50'
                          }}>
                            {level}
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>
                )}

                {item.question_type === 'three_level' && (
                  <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '12px'
                  }}>
                    <label style={{
                      fontSize: '16px',
                      fontWeight: '600',
                      color: '#2c3e50',
                      marginBottom: '8px'
                    }}>
                      현재 수준을 선택해주세요:
                    </label>
                    <div style={{
                      display: 'flex',
                      gap: '8px',
                      flexWrap: 'wrap'
                    }}>
                      {[1, 2, 3].map((level) => (
                        <label key={level} style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          cursor: 'pointer'
                        }}>
                          <input
                            type="radio"
                            name={`question_${item.id}`}
                            value={level}
                            checked={responses[item.id]?.level_no === level}
                            onChange={() => handleLevelChange(item.id, level)}
                            style={{
                              width: '18px',
                              height: '18px',
                              accentColor: '#007bff'
                            }}
                          />
                          <span style={{
                            fontSize: '16px',
                            color: '#2c3e50'
                          }}>
                            {level}
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>
                )}

                {item.question_type === 'five_choice' && (
                  <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '12px'
                  }}>
                    <label style={{
                      fontSize: '16px',
                      fontWeight: '600',
                      color: '#2c3e50',
                      marginBottom: '8px'
                    }}>
                      해당하는 항목을 모두 선택해주세요:
                    </label>
                    <div style={{
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '8px'
                    }}>
                      {[1, 2, 3, 4, 5].map((choice) => (
                        <label key={choice} style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          cursor: 'pointer'
                        }}>
                          <input
                            type="checkbox"
                            value={choice}
                            checked={responses[item.id]?.choice_ids?.includes(choice) || false}
                            onChange={(e) => handleChoiceChange(item.id, choice, e.target.checked)}
                            style={{
                              width: '18px',
                              height: '18px',
                              accentColor: '#007bff'
                            }}
                          />
                          <span style={{
                            fontSize: '16px',
                            color: '#2c3e50'
                          }}>
                            선택지 {choice}
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* 제출 버튼 */}
        <div style={{
          marginTop: '40px',
          textAlign: 'center'
        }}>
          <button
            type="submit"
            style={{
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              padding: '16px 48px',
              fontSize: '18px',
              fontWeight: '600',
              borderRadius: '12px',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              boxShadow: '0 4px 16px rgba(0, 123, 255, 0.3)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 6px 20px rgba(0, 123, 255, 0.4)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 16px rgba(0, 123, 255, 0.3)';
            }}
          >
            📤 자가진단 제출하기
          </button>
        </div>
      </form>

      {/* Drawer */}
      <Drawer
        isOpen={drawerOpen}
        onClose={handleDrawerClose}
        title={selectedQuestion?.item_name || ''}
      >
        {selectedQuestion && (
          <div style={{
            padding: '20px'
          }}>
            <h3 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#2c3e50',
              marginBottom: '16px'
            }}>
              {selectedQuestion.item_name}
            </h3>
            
            <p style={{
              fontSize: '16px',
              color: '#6c757d',
              lineHeight: '1.6',
              marginBottom: '20px'
            }}>
              {selectedQuestion.item_desc}
            </p>

            {selectedQuestion.metric_desc && (
              <div style={{
                marginBottom: '20px'
              }}>
                <h4 style={{
                  fontSize: '16px',
                  fontWeight: '600',
                  color: '#2c3e50',
                  marginBottom: '8px'
                }}>
                  측정 방법:
                </h4>
                <p style={{
                  fontSize: '14px',
                  color: '#6c757d',
                  lineHeight: '1.6'
                }}>
                  {selectedQuestion.metric_desc}
                </p>
              </div>
            )}

            {selectedQuestion.data_source && (
              <div style={{
                marginBottom: '20px'
              }}>
                <h4 style={{
                  fontSize: '16px',
                  fontWeight: '600',
                  color: '#2c3e50',
                  marginBottom: '8px'
                }}>
                  데이터 소스:
                </h4>
                <p style={{
                  fontSize: '14px',
                  color: '#6c757d',
                  lineHeight: '1.6'
                }}>
                  {selectedQuestion.data_source}
                </p>
              </div>
            )}
          </div>
        )}
      </Drawer>
    </div>
  );
}

// 메인 export 컴포넌트를 Suspense로 감싸기
export default function AssessmentSurveyPage() {
  return (
    <Suspense fallback={
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: '18px',
        color: '#666'
      }}>
        로딩 중...
      </div>
    }>
      <AssessmentPage />
    </Suspense>
  );
}
