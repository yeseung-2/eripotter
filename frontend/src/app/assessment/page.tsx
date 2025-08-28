'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from '@/lib/axios';
import { useAuthStore } from '@/store/useStore';

interface Choice {
  text: string;
  score: number;
}

interface Choices {
  [key: string]: Choice;
}

interface ApiQuestion {
  id: number;
  item_name: string;
  question_text?: string;
  question_type?: string;
  choices?: Choices;  // API 응답의 choices 필드
  category?: string;
  weight?: number;
}

interface Question {
  id: number;
  question_text: string;
  question_type: string;
  choices?: Choices;
  category?: string;
  weight: number;
}

interface ApiResponse {
  items: ApiQuestion[];
  status?: string;
}

const AssessmentPage = () => {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [responses, setResponses] = useState<Record<number, number | number[]>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);



  React.useEffect(() => {
    const fetchQuestions = async () => {
      try {
        console.log('kesg 테이블 데이터 조회 중...');
        const response = await axios.get('/api/assessment/kesg');
        console.log('kesg 응답:', response.data);
        
        if (response.data && response.data.items && response.data.items.length > 0) {
          console.log('kesg 데이터 개수:', response.data.items.length);
          console.log('첫 번째 kesg 항목:', response.data.items[0]);
          
          // kesg 데이터를 기존 형식으로 변환
          const transformedQuestions = response.data.items.map((item: ApiQuestion, index: number) => {
            console.log(`변환 중 ${index + 1}번째 항목:`, item);
            return {
              id: item.id,
              question_text: item.question_text || item.item_name,
              question_type: item.question_type || "three_level",
              choices: item.choices || {},  // choices 필드 사용
              category: item.category || "자가진단",
              weight: 1
            };
          });
          
          setQuestions(transformedQuestions);
          console.log('변환된 문항:', transformedQuestions);
        } else {
          console.log('kesg 데이터가 비어있습니다.');
          setQuestions([]);
        }
      } catch (error) {
        console.error('kesg 테이블 조회 실패:', error);
        setQuestions([]); // 에러 시 빈 배열로 설정
      } finally {
        setLoading(false);
      }
    };

    // 인증 체크 임시 비활성화
    // if (!isAuthenticated || !user) {
    //   alert('로그인이 필요합니다.');
    //   router.push('/');
    //   return;
    // }

    fetchQuestions();
  }, [isAuthenticated, user, router]);

  const handleResponseChange = (questionId: number, value: number | number[], questionType: string) => {
    setResponses(prev => {
      if (questionType === 'five_choice') {
        // checkbox의 경우 배열로 관리
        const currentChoices = (prev[questionId] as number[]) || [];
        const newChoices = currentChoices.includes(value as number)
          ? currentChoices.filter((choice: number) => choice !== value)
          : [...currentChoices, value as number];
        
        return {
          ...prev,
          [questionId]: newChoices
        };
      } else {
        // radio의 경우 단일 값
        return {
          ...prev,
          [questionId]: value as number
        };
      }
    });
  };

  const handleSubmit = async () => {
    // 모든 문항에 답변했는지 확인
    const answeredQuestions = questions.filter(question => {
      const response = responses[question.id];
      if (question.question_type === 'five_choice') {
        return response && Array.isArray(response) && response.length > 0;
      } else {
        return response !== undefined && response !== null;
      }
    });

    if (answeredQuestions.length !== questions.length) {
      alert('모든 문항에 답변해주세요.');
      return;
    }

    setSubmitting(true);
    try {
      // 임시로 고정된 company_id 사용
      const company_id = "삼성";
      
      const assessmentData = {
        company_id: company_id,
        responses: questions.map(question => ({
          question_id: question.id,
          question_type: question.question_type,
          level_id: question.question_type !== 'five_choice' ? responses[question.id] : undefined,
          choice_ids: question.question_type === 'five_choice' ? responses[question.id] : undefined
        }))
      };

      console.log('제출할 데이터:', assessmentData);
      
      const response = await axios.post('/api/assessment/', assessmentData);
      console.log('제출 응답:', response.data);
      
      if (response.data.status === 'success') {
        alert('자가진단이 성공적으로 완료되었습니다!');
        // 결과 페이지로 이동
        router.push('/assessment/result');
      } else {
        alert('제출 중 오류가 발생했습니다.');
      }
      
    } catch (err: Error | unknown) {
      console.error('제출 실패:', err);
      const errorMessage = err instanceof Error ? err.message : 
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || '제출 중 오류가 발생했습니다.';
      alert(`제출 실패: ${errorMessage}`);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">문항을 불러오는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* 헤더 */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">공급망실사 자가진단</h1>
          <p className="text-gray-600">
            아래 문항들을 읽고, 귀사의 상황에 가장 잘 맞는 답변을 선택해주세요.
          </p>
        </div>

        {/* 설문지 */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div className="p-6">
            {questions.map((question, index) => (
              <div key={question.id} className="mb-8 last:mb-0">
                <div className="mb-4">
                  <div className="flex items-start">
                    <span className="font-medium text-gray-700 mr-2 min-w-[20px]">
                      {index + 1}.
                    </span>
                    <span className="text-gray-900">{question.question_text}</span>
                  </div>
                </div>

                {/* 문항 타입에 따른 안내 문구 */}
                <div className="mb-3 text-sm text-gray-600">
                  {question.question_type === 'five_choice' 
                    ? "귀사에 해당하는 항목을 모두 선택해 주세요."
                    : "귀사의 현황에 가장 부합하는 항목을 선택해 주세요."
                  }
                </div>

                                 {/* 선택지 렌더링 */}
                 <div className="ml-6">
                   {question.question_type === 'five_choice' ? (
                     // checkbox 렌더링 (choices_json)
                     <div className="space-y-2">
                                               {question.choices && Object.entries(question.choices).map(([id, choice]) => (
                          <label key={id} className="flex items-center">
                            <input
                              type="checkbox"
                              value={id}
                              checked={Array.isArray(responses[question.id]) && (responses[question.id] as number[]).includes(Number(id))}
                              onChange={() => handleResponseChange(question.id, Number(id), question.question_type)}
                              className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2"
                            />
                            <span className="ml-2 text-gray-700">{choice.text}</span>
                          </label>
                        ))}
                     </div>
                   ) : (
                     // radio 버튼 렌더링 (levels_json)
                     <div className="space-y-2">
                                               {question.choices && Object.entries(question.choices).map(([level_no, choice]) => (
                          <label key={level_no} className="flex items-center">
                            <input
                              type="radio"
                              name={`question-${question.id}`}
                              value={level_no}
                              checked={responses[question.id] === Number(level_no)}
                              onChange={() => handleResponseChange(question.id, Number(level_no), question.question_type)}
                              className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 focus:ring-2"
                            />
                            <div className="ml-2">
                              <div className="font-medium text-gray-700">{choice.text}</div>
                              <div className="text-sm text-gray-600">{choice.score}</div>
                            </div>
                          </label>
                        ))}
                     </div>
                   )}
                 </div>
              </div>
            ))}
          </div>
        </div>

        {/* 제출 버튼 */}
        <div className="mt-6 flex justify-center">
          <button
            onClick={handleSubmit}
            disabled={submitting || questions.filter(q => {
              const response = responses[q.id];
              if (q.question_type === 'five_choice') {
                return response && Array.isArray(response) && response.length > 0;
              } else {
                return response !== undefined && response !== null;
              }
            }).length !== questions.length}
            className="px-8 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {submitting ? '제출 중...' : '자가진단 제출'}
          </button>
        </div>

        {/* 진행률 표시 */}
        <div className="mt-4 text-center">
          <p className="text-sm text-gray-600">
            진행률: {questions.filter(q => {
              const response = responses[q.id];
              if (q.question_type === 'five_choice') {
                return response && Array.isArray(response) && response.length > 0;
              } else {
                return response !== undefined && response !== null;
              }
            }).length} / {questions.length} 문항 완료
          </p>
        </div>
      </div>
    </div>
  );
};

export default AssessmentPage;
