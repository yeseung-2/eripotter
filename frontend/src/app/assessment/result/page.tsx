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

interface AssessmentResult {
  id: number;
  company_id: string;
  question_id: number;
  question_type: string;
  level_no?: number;
  choice_ids?: number[];
  score: number;
  timestamp: string;
  question_text?: string;
  category?: string;
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

const AssessmentResultPage = () => {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const [results, setResults] = useState<AssessmentResult[]>([]);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);



  useEffect(() => {
    const fetchData = async () => {
      // 인증 체크
      if (!isAuthenticated || !user) {
        alert('로그인이 필요합니다.');
        router.push('/');
        return;
      }

      try {
        setLoading(true);
        
        // 1. 문항 데이터 가져오기
        try {
          const questionResponse = await axios.get('/api/assessment/kesg');
          if (questionResponse.data && questionResponse.data.items && questionResponse.data.items.length > 0) {
            const questionData = questionResponse.data.items.map((item: ApiQuestion) => {
              return {
                id: item.id,
                question_text: item.question_text || item.item_name,
                question_type: item.question_type || "four_level",
                choices: item.choices || {},  // choices 필드 사용
                category: item.category || "자가진단",
                weight: 1
              };
            });
            setQuestions(questionData);
          } else {
            setQuestions([]);
          }
        } catch (error: Error | unknown) {
          console.error('문항 데이터 로드 실패:', error);
          setQuestions([]);
        }

        // 2. 해당 회사의 자가진단 결과 가져오기
        const company_id = user.company_id;
        const resultResponse = await axios.get(`/api/assessment/results/${company_id}`);
        
        if (resultResponse.data && resultResponse.data.results) {
          // 문항 정보와 결과를 합치기
          const resultsWithQuestions = resultResponse.data.results.map((result: AssessmentResult) => {
            const question = questions.find((q: Question) => q.id === result.question_id);
            return {
              ...result,
              question_text: question?.question_text || `문항 ${result.question_id}`,
              category: question?.category || "기타"
            };
          });
          setResults(resultsWithQuestions);
        } else {
          setError('자가진단 결과를 찾을 수 없습니다.');
        }
      } catch (err: Error | unknown) {
        const errorMessage = err instanceof Error ? err.message : '알 수 없는 오류';
        console.error('데이터 로드 실패:', errorMessage);
        setError('데이터를 불러오는 중 오류가 발생했습니다.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [isAuthenticated, user, router, questions]);

  const getAnswerText = (result: AssessmentResult) => {
    const question = questions.find(q => q.id === result.question_id);
    if (!question) return '알 수 없음';

    if (result.question_type === 'five_choice' && result.choice_ids) {
      // 다중 선택의 경우
      const selectedChoices = result.choice_ids.map(choiceId => {
        const choice = question.choices?.[choiceId];
        return choice?.text || `선택 ${choiceId}`;
      });
      return selectedChoices.join(', ');
    } else if (result.level_no !== undefined) {
      // 단일 선택의 경우
      const choice = question.choices?.[result.level_no];
      return choice?.text || `레벨 ${result.level_no}`;
    }

    return '답변 없음';
  };

  const getCategoryResults = () => {
    const categoryMap = new Map<string, AssessmentResult[]>();
    
    results.forEach(result => {
      const category = result.category || '기타';
      if (!categoryMap.has(category)) {
        categoryMap.set(category, []);
      }
      categoryMap.get(category)!.push(result);
    });

    return Array.from(categoryMap.entries()).map(([category, categoryResults]) => ({
      category,
      results: categoryResults,
      totalScore: categoryResults.reduce((sum, result) => sum + result.score, 0),
      averageScore: categoryResults.length > 0 ? categoryResults.reduce((sum, result) => sum + result.score, 0) / categoryResults.length : 0
    }));
  };

  const categoryResults = getCategoryResults();
  const totalScore = results.reduce((sum, result) => sum + result.score, 0);
  const averageScore = results.length > 0 ? totalScore / results.length : 0;

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">결과를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-xl mb-4">⚠️</div>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => router.push('/assessment')}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            자가진단 다시 하기
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* 헤더 */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">자가진단 결과</h1>
              <p className="text-gray-600">
                {user?.company_id}의의 자가진단 결과입니다.
              </p>
            </div>
            <button
              onClick={() => router.push('/assessment')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              다시 진단하기
            </button>
          </div>
        </div>

        {/* 전체 요약 */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">전체 요약</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{results.length}</div>
              <div className="text-sm text-gray-600">총 문항 수</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{totalScore}</div>
              <div className="text-sm text-gray-600">총 점수</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{averageScore.toFixed(1)}</div>
              <div className="text-sm text-gray-600">평균 점수</div>
            </div>
          </div>
        </div>

        {/* 카테고리별 결과 */}
        {categoryResults.map((categoryData) => (
          <div key={categoryData.category} className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">{categoryData.category}</h3>
              <div className="text-sm text-gray-600">
                평균: {categoryData.averageScore.toFixed(1)}점
              </div>
            </div>
            
            <div className="space-y-4">
              {categoryData.results.map((result) => (
                <div key={result.id} className="border-l-4 border-blue-500 pl-4 py-2">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <p className="font-medium text-gray-900 mb-1">
                        {result.question_text}
                      </p>
                      <p className="text-sm text-gray-600">
                        답변: <span className="font-medium">{getAnswerText(result)}</span>
                      </p>
                    </div>
                    <div className="text-right ml-4">
                      <div className="text-lg font-bold text-blue-600">{result.score}점</div>
                      <div className="text-xs text-gray-500">
                        {new Date(result.timestamp).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}

        {/* 상세 결과 테이블 */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">상세 결과</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    문항
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    카테고리
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    답변
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    점수
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    제출일
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {results.map((result) => (
                  <tr key={result.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-normal">
                      <div className="text-sm font-medium text-gray-900">
                        {result.question_text}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                        {result.category}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {getAnswerText(result)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm font-medium text-gray-900">{result.score}점</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(result.timestamp).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssessmentResultPage;
