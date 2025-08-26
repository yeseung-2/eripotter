'use client';

import React, { useState, useEffect } from 'react';
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

interface Question {
  id: number;
  question_text: string;
  question_type: string;
  choices?: Choices;
  category?: string;
  weight: number;
}

const AssessmentPage = () => {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [responses, setResponses] = useState<Record<number, number | number[]>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  // 임시 샘플 데이터 (나중에 DB에서 가져올 예정)
  const sampleQuestions: Question[] = [
    {
      id: 1,
      question_text: "세부적인 면에 대해 꼼꼼하게 주의를 기울이지 못하거나 학업에서 부주의한 실수를 한다.",
      question_type: "four_level",
      choices: {
        "0": { text: "전혀 그렇지 않다", score: 0 },
        "1": { text: "가끔 그렇다", score: 1 },
        "2": { text: "자주 그렇다", score: 2 },
        "3": { text: "매우 자주 그렇다", score: 3 }
      },
      category: "주의력",
      weight: 1
    },
    {
      id: 2,
      question_text: "손발을 가만히 두지 못하거나 의자에 앉아서도 몸을 꼼지락거린다.",
      question_type: "four_level",
      choices: {
        "0": { text: "전혀 그렇지 않다", score: 0 },
        "1": { text: "가끔 그렇다", score: 1 },
        "2": { text: "자주 그렇다", score: 2 },
        "3": { text: "매우 자주 그렇다", score: 3 }
      },
      category: "과잉행동",
      weight: 1
    },
    {
      id: 3,
      question_text: "일을 하거나 놀이를 할 때 지속적으로 주의를 집중하는데 어려움이 있다.",
      question_type: "four_level",
      choices: {
        "0": { text: "전혀 그렇지 않다", score: 0 },
        "1": { text: "가끔 그렇다", score: 1 },
        "2": { text: "자주 그렇다", score: 2 },
        "3": { text: "매우 자주 그렇다", score: 3 }
      },
      category: "주의력",
      weight: 1
    },
    {
      id: 4,
      question_text: "자리에 앉아 있어야 하는 교실이나 다른 상황에서 앉아있지 못한다.",
      question_type: "four_level",
      choices: {
        "0": { text: "전혀 그렇지 않다", score: 0 },
        "1": { text: "가끔 그렇다", score: 1 },
        "2": { text: "자주 그렇다", score: 2 },
        "3": { text: "매우 자주 그렇다", score: 3 }
      },
      category: "과잉행동",
      weight: 1
    },
    {
      id: 5,
      question_text: "다른 사람이 마주보고 이야기 할 때 경청하지 않는 것처럼 보인다.",
      question_type: "four_level",
      choices: {
        "0": { text: "전혀 그렇지 않다", score: 0 },
        "1": { text: "가끔 그렇다", score: 1 },
        "2": { text: "자주 그렇다", score: 2 },
        "3": { text: "매우 자주 그렇다", score: 3 }
      },
      category: "주의력",
      weight: 1
    },
    {
      id: 6,
      question_text: "그렇게 하면 안 되는 상황에서 지나치게 뛰어다니거나 기어오른다.",
      question_type: "four_level",
      choices: {
        "0": { text: "전혀 그렇지 않다", score: 0 },
        "1": { text: "가끔 그렇다", score: 1 },
        "2": { text: "자주 그렇다", score: 2 },
        "3": { text: "매우 자주 그렇다", score: 3 }
      },
      category: "과잉행동",
      weight: 1
    },
    {
      id: 7,
      question_text: "지시를 따르지 않고, 일을 끝내지 못한다.",
      question_type: "four_level",
      choices: {
        "0": { text: "전혀 그렇지 않다", score: 0 },
        "1": { text: "가끔 그렇다", score: 1 },
        "2": { text: "자주 그렇다", score: 2 },
        "3": { text: "매우 자주 그렇다", score: 3 }
      },
      category: "주의력",
      weight: 1
    },
    {
      id: 8,
      question_text: "여가 활동이나 재미있는 일에 조용히 참여하기가 어렵다.",
      question_type: "four_level",
      choices: {
        "0": { text: "전혀 그렇지 않다", score: 0 },
        "1": { text: "가끔 그렇다", score: 1 },
        "2": { text: "자주 그렇다", score: 2 },
        "3": { text: "매우 자주 그렇다", score: 3 }
      },
      category: "과잉행동",
      weight: 1
    },
    {
      id: 9,
      question_text: "과제와 일을 체계적으로 하지 못한다.",
      question_type: "four_level",
      choices: {
        "0": { text: "전혀 그렇지 않다", score: 0 },
        "1": { text: "가끔 그렇다", score: 1 },
        "2": { text: "자주 그렇다", score: 2 },
        "3": { text: "매우 자주 그렇다", score: 3 }
      },
      category: "주의력",
      weight: 1
    },
    {
      id: 10,
      question_text: "끊임없이 무엇인가를 하거나 마치 모터가 돌아가듯 움직인다.",
      question_type: "four_level",
      choices: {
        "0": { text: "전혀 그렇지 않다", score: 0 },
        "1": { text: "가끔 그렇다", score: 1 },
        "2": { text: "자주 그렇다", score: 2 },
        "3": { text: "매우 자주 그렇다", score: 3 }
      },
      category: "과잉행동",
      weight: 1
    },
    {
      id: 11,
      question_text: "지속적인 노력이 요구되는 과제(학교공부나 숙제)를 하지 않으려 한다.",
      question_type: "four_level",
      choices: {
        "0": { text: "전혀 그렇지 않다", score: 0 },
        "1": { text: "가끔 그렇다", score: 1 },
        "2": { text: "자주 그렇다", score: 2 },
        "3": { text: "매우 자주 그렇다", score: 3 }
      },
      category: "주의력",
      weight: 1
    },
    {
      id: 12,
      question_text: "지나치게 말을 많이 한다.",
      question_type: "four_level",
      choices: {
        "0": { text: "전혀 그렇지 않다", score: 0 },
        "1": { text: "가끔 그렇다", score: 1 },
        "2": { text: "자주 그렇다", score: 2 },
        "3": { text: "매우 자주 그렇다", score: 3 }
      },
      category: "과잉행동",
      weight: 1
    },
    {
      id: 13,
      question_text: "과제나 일을 하는데 필요한 물건들은 잃어버린다.",
      question_type: "four_level",
      choices: {
        "0": { text: "전혀 그렇지 않다", score: 0 },
        "1": { text: "가끔 그렇다", score: 1 },
        "2": { text: "자주 그렇다", score: 2 },
        "3": { text: "매우 자주 그렇다", score: 3 }
      },
      category: "주의력",
      weight: 1
    },
    {
      id: 14,
      question_text: "질문이 채 끝나기도 전에 성급하게 대답한다.",
      question_type: "four_level",
      choices: {
        "0": { text: "전혀 그렇지 않다", score: 0 },
        "1": { text: "가끔 그렇다", score: 1 },
        "2": { text: "자주 그렇다", score: 2 },
        "3": { text: "매우 자주 그렇다", score: 3 }
      },
      category: "과잉행동",
      weight: 1
    },
    {
      id: 15,
      question_text: "쉽게 산만해 진다.",
      question_type: "four_level",
      choices: {
        "0": { text: "전혀 그렇지 않다", score: 0 },
        "1": { text: "가끔 그렇다", score: 1 },
        "2": { text: "자주 그렇다", score: 2 },
        "3": { text: "매우 자주 그렇다", score: 3 }
      },
      category: "주의력",
      weight: 1
    },
    {
      id: 16,
      question_text: "차례를 기다리는데 어려움이 있다.",
      question_type: "four_level",
      choices: {
        "0": { text: "전혀 그렇지 않다", score: 0 },
        "1": { text: "가끔 그렇다", score: 1 },
        "2": { text: "자주 그렇다", score: 2 },
        "3": { text: "매우 자주 그렇다", score: 3 }
      },
      category: "과잉행동",
      weight: 1
    },
    {
      id: 17,
      question_text: "일상적으로 하는 일을 잊어버린다.",
      question_type: "four_level",
      choices: {
        "0": { text: "전혀 그렇지 않다", score: 0 },
        "1": { text: "가끔 그렇다", score: 1 },
        "2": { text: "자주 그렇다", score: 2 },
        "3": { text: "매우 자주 그렇다", score: 3 }
      },
      category: "주의력",
      weight: 1
    },
    {
      id: 18,
      question_text: "다른 사람을 방해하거나 간섭한다.",
      question_type: "four_level",
      choices: {
        "0": { text: "전혀 그렇지 않다", score: 0 },
        "1": { text: "가끔 그렇다", score: 1 },
        "2": { text: "자주 그렇다", score: 2 },
        "3": { text: "매우 자주 그렇다", score: 3 }
      },
      category: "과잉행동",
      weight: 1
    }
  ];

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
          const transformedQuestions = response.data.items.map((item: any, index: number) => {
            console.log(`변환 중 ${index + 1}번째 항목:`, item);
            return {
              id: item.id,
              question_text: item.item_name, // item_name을 question_text로 사용
              question_type: item.question_type || "three_level",
              choices: item.choices || {},
              category: item.category || "자가진단",
              weight: 1
            };
          });
          
          setQuestions(transformedQuestions);
          console.log('변환된 문항:', transformedQuestions);
        } else {
          console.log('kesg 데이터가 비어있어서 샘플 데이터를 사용합니다.');
          setQuestions(sampleQuestions);
        }
      } catch (error) {
        console.error('kesg 테이블 조회 실패:', error);
        console.log('샘플 데이터로 대체합니다.');
        setQuestions(sampleQuestions); // 에러 시 샘플 데이터 사용
      } finally {
        setLoading(false);
      }
    };

    // 인증 체크
    if (!isAuthenticated || !user) {
      alert('로그인이 필요합니다.');
      router.push('/');
      return;
    }

    fetchQuestions();
  }, [isAuthenticated, user, router, sampleQuestions]);

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
      // 로그인한 사용자의 company_id 사용
      if (!user || !user.company_id) {
        alert('사용자 정보를 찾을 수 없습니다. 다시 로그인해주세요.');
        router.push('/');
        return;
      }
      
      const company_id = user.company_id;
      
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
      
    } catch (error: any) {
      console.error('제출 실패:', error);
      const errorMessage = error.response?.data?.detail || '제출 중 오류가 발생했습니다.';
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
                                               {Array.isArray(question.choices) && question.choices.map((choice: any) => (
                          <label key={choice.id} className="flex items-center">
                            <input
                              type="checkbox"
                              value={choice.id}
                              checked={Array.isArray(responses[question.id]) && (responses[question.id] as number[]).includes(choice.id)}
                              onChange={(e) => handleResponseChange(question.id, choice.id, question.question_type)}
                              className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2"
                            />
                            <span className="ml-2 text-gray-700">{choice.text}</span>
                          </label>
                        ))}
                     </div>
                   ) : (
                     // radio 버튼 렌더링 (levels_json)
                     <div className="space-y-2">
                                               {Array.isArray(question.choices) && question.choices.map((level: any) => (
                          <label key={level.level_no} className="flex items-center">
                            <input
                              type="radio"
                              name={`question-${question.id}`}
                              value={level.level_no}
                              checked={responses[question.id] === level.level_no}
                              onChange={(e) => handleResponseChange(question.id, level.level_no, question.question_type)}
                              className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 focus:ring-2"
                            />
                            <div className="ml-2">
                              <div className="font-medium text-gray-700">{level.label}</div>
                              <div className="text-sm text-gray-600">{level.desc}</div>
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
