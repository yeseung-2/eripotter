'use client';

import { useState, useEffect } from 'react';
import { Info } from 'lucide-react';
import { Drawer } from '@/components/Drawer';
import { getKesgItems, submitAssessment } from '@/lib/api';
import type { KesgItem, KesgResponse, AssessmentSubmissionRequest, AssessmentSubmissionResponse, AssessmentRequest, LevelData, ChoiceData } from '@/types/assessment';

// Response type for managing form state
type ResponseData = {
  level_no?: number;
  choice_ids?: number[];
};

export default function AssessmentPage() {
  const [kesgItems, setKesgItems] = useState<KesgItem[]>([]);
  const [responses, setResponses] = useState<Record<number, ResponseData>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState<KesgItem | null>(null);

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
    
    try {
      // API 호출하여 실제로 데이터 저장
      const result = await submitAssessment({
        company_name: localStorage.getItem('companyName') || '테스트회사',
        responses: formattedResponses
      });

      console.log('자가진단 응답이 성공적으로 저장되었습니다:', result);
      // 응답 데이터를 localStorage에 저장하고 결과 페이지로 이동
      localStorage.setItem('assessmentResponses', JSON.stringify(formattedResponses));
      window.location.href = '/assessment/result';
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
          자가진단
        </h1>
        <p style={{
          fontSize: '16px',
          color: '#7f8c8d',
          textAlign: 'center',
          marginBottom: '40px'
        }}>
          환경, 사회, 지배구조(ESG) 자가진단을 진행하세요.
        </p>

        <form onSubmit={handleSubmit}>
          {kesgItems.map((item, index) => (
            <div key={item.id} style={{
              marginBottom: '40px',
              padding: '30px',
              backgroundColor: '#f8f9fa',
              borderRadius: '8px',
              border: '1px solid #e9ecef',
              position: 'relative'
            }}>
              <div style={{ marginBottom: '24px' }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  gap: '12px'
                }}>
                  <h3 style={{
                    fontSize: '20px',
                    fontWeight: '600',
                    color: '#2c3e50',
                    marginBottom: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    flex: 1
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
                      {item.id}
                    </span>
                    {item.item_name}
                  </h3>
                  <button
                    onClick={(e) => handleInfoClick(item, e)}
                    style={{
                      backgroundColor: 'transparent',
                      border: 'none',
                      padding: '8px',
                      borderRadius: '50%',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      transition: 'all 0.2s ease',
                      minWidth: '32px',
                      height: '32px'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = '#e3f2fd';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'transparent';
                    }}
                  >
                    <Info size={20} color="#007bff" />
                  </button>
                </div>
              </div>

              {/* 단계형 문항 */}
              {(item.question_type === 'five_level' || item.question_type === 'three_level') &&
                item.levels_json && (
                  <div>
                    <h4 style={{
                      fontSize: '16px',
                      fontWeight: '600',
                      color: '#495057',
                      marginBottom: '16px'
                    }}>
                      귀사의 상황을 가장 잘 설명하는 단계를 선택해주세요.:
                    </h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                      {item.levels_json.map((level) => (
                        <label
                          key={level.level_no}
                          style={{
                            display: 'flex',
                            alignItems: 'flex-start',
                            padding: '16px',
                            backgroundColor: responses[item.id]?.level_no === level.level_no ? '#e3f2fd' : 'white',
                            border: `2px solid ${responses[item.id]?.level_no === level.level_no ? '#2196f3' : '#dee2e6'}`,
                            borderRadius: '8px',
                            cursor: 'pointer',
                            transition: 'all 0.2s ease',
                            minHeight: '60px'
                          }}
                          onMouseEnter={(e) => {
                            if (responses[item.id]?.level_no !== level.level_no) {
                              e.currentTarget.style.backgroundColor = '#f8f9fa';
                              e.currentTarget.style.borderColor = '#adb5bd';
                            }
                          }}
                          onMouseLeave={(e) => {
                            if (responses[item.id]?.level_no !== level.level_no) {
                              e.currentTarget.style.backgroundColor = 'white';
                              e.currentTarget.style.borderColor = '#dee2e6';
                            }
                          }}
                        >
                          <input
                            type="radio"
                            name={`question-${item.id}`}
                            value={level.level_no}
                            checked={responses[item.id]?.level_no === level.level_no}
                            onChange={() => handleLevelChange(item.id, level.level_no)}
                            style={{
                              marginRight: '12px',
                              marginTop: '2px',
                              transform: 'scale(1.2)'
                            }}
                          />
                          <div>
                            <span style={{
                              fontWeight: '600',
                              color: '#2c3e50',
                              fontSize: '15px',
                              display: 'block',
                              marginBottom: '4px'
                            }}>
                              {level.label}
                            </span>
                            <span style={{
                              color: '#6c757d',
                              fontSize: '14px',
                              lineHeight: '1.5'
                            }}>
                              {level.desc}
                            </span>
                          </div>
                        </label>
                      ))}
                    </div>
                  </div>
                )}

              {/* 선택형 문항 */}
              {item.question_type === 'five_choice' && item.choices_json && (
                <div>
                  <h4 style={{
                    fontSize: '16px',
                    fontWeight: '600',
                    color: '#495057',
                    marginBottom: '16px'
                  }}>
                    귀사에 해당하는 항목을 모두 선택해 주세요.
                  </h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {item.choices_json.map((choice) => (
                      <label
                        key={choice.id}
                        style={{
                          display: 'flex',
                          alignItems: 'flex-start',
                          padding: '16px',
                          backgroundColor: responses[item.id]?.choice_ids?.includes(choice.id) ? '#e8f5e8' : 'white',
                          border: `2px solid ${responses[item.id]?.choice_ids?.includes(choice.id) ? '#4caf50' : '#dee2e6'}`,
                          borderRadius: '8px',
                          cursor: 'pointer',
                          transition: 'all 0.2s ease',
                          minHeight: '50px'
                        }}
                        onMouseEnter={(e) => {
                          if (!responses[item.id]?.choice_ids?.includes(choice.id)) {
                            e.currentTarget.style.backgroundColor = '#f8f9fa';
                            e.currentTarget.style.borderColor = '#adb5bd';
                          }
                        }}
                        onMouseLeave={(e) => {
                          if (!responses[item.id]?.choice_ids?.includes(choice.id)) {
                            e.currentTarget.style.backgroundColor = 'white';
                            e.currentTarget.style.borderColor = '#dee2e6';
                          }
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={responses[item.id]?.choice_ids?.includes(choice.id) || false}
                          onChange={(e) =>
                            handleChoiceChange(item.id, choice.id, e.target.checked)
                          }
                          style={{
                            marginRight: '12px',
                            marginTop: '2px',
                            transform: 'scale(1.2)'
                          }}
                        />
                        <span style={{
                          color: '#2c3e50',
                          fontSize: '15px',
                          lineHeight: '1.5'
                        }}>
                          {choice.text}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}

          <div style={{
            textAlign: 'center',
            marginTop: '40px',
            paddingTop: '30px',
            borderTop: '1px solid #e9ecef'
          }}>
            <button 
              type="submit"
              style={{
                backgroundColor: '#007bff',
                color: 'white',
                border: 'none',
                padding: '16px 32px',
                fontSize: '18px',
                fontWeight: '600',
                borderRadius: '8px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                minWidth: '200px'
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
              자가진단 제출
            </button>
          </div>
        </form>
      </div>
      
      {/* Drawer */}
      {selectedQuestion && (
        <Drawer
          isOpen={drawerOpen}
          onClose={handleDrawerClose}
          question={selectedQuestion}
        />
      )}
    </div>
  );
}
