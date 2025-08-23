'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function CompanyDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [mounted, setMounted] = useState(false);
  
  // 클라이언트 사이드에서만 router 사용
  const router = useRouter();
  
  // 컴포넌트가 마운트된 후에만 router 사용
  useEffect(() => {
    setMounted(true);
  }, []);
  
  // 마운트 전에는 router 기능 비활성화
  const handleNavigation = (path: string) => {
    if (mounted) {
      router.push(path);
    }
  };

  // 더미 데이터
  const stats = {
    totalRevenue: 1250000,
    monthlyGrowth: 12.5,
    activeUsers: 2840,
    pendingTasks: 15
  };

  const recentActivities = [
    { id: 1, type: 'login', user: '김철수', time: '2분 전', description: '시스템에 로그인했습니다.' },
    { id: 2, type: 'report', user: '이영희', time: '15분 전', description: '월간 리포트를 생성했습니다.' },
    { id: 3, type: 'update', user: '박민수', time: '1시간 전', description: '프로젝트 정보를 업데이트했습니다.' },
    { id: 4, type: 'upload', user: '정수진', time: '2시간 전', description: '새로운 문서를 업로드했습니다.' }
  ];

  const projects = [
    { id: 1, name: '웹사이트 리뉴얼', progress: 75, status: '진행중', dueDate: '2024-02-15' },
    { id: 2, name: '모바일 앱 개발', progress: 45, status: '진행중', dueDate: '2024-03-20' },
    { id: 3, name: '데이터베이스 마이그레이션', progress: 90, status: '검토중', dueDate: '2024-01-30' },
    { id: 4, name: '보안 업데이트', progress: 100, status: '완료', dueDate: '2024-01-25' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">기업 대시보드</h1>
            </div>
            <div className="flex items-center space-x-4">
              {/* ESG 데이터 업로드 버튼 */}
              <button
                onClick={() => handleNavigation('/data-upload')}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2"
              >
                <span>📊</span>
                <span>ESG 데이터 업로드</span>
              </button>
              
              <div className="relative">
                <a href="/chat" className="p-2 text-gray-400 hover:text-gray-500 transition-colors">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                </a>
              </div>
              <div className="flex items-center space-x-3">
                <div className="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center">
                  <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <span className="text-sm font-medium text-gray-700">관리자</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {[
              { id: 'overview', name: '개요' },
              { id: 'esg', name: 'ESG 관리' },
              { id: 'projects', name: '프로젝트' },
              { id: 'analytics', name: '분석' },
              { id: 'reports', name: '보고서' },
              { id: 'settings', name: '설정' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.name}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-5">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                      </svg>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">총 매출</dt>
                        <dd className="text-lg font-medium text-gray-900">₩{stats.totalRevenue.toLocaleString()}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                      </svg>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">월간 성장률</dt>
                        <dd className="text-lg font-medium text-gray-900">+{stats.monthlyGrowth}%</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                      </svg>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">활성 사용자</dt>
                        <dd className="text-lg font-medium text-gray-900">{stats.activeUsers.toLocaleString()}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <svg className="w-6 h-6 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">대기 작업</dt>
                        <dd className="text-lg font-medium text-gray-900">{stats.pendingTasks}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              {/* ESG 데이터 카드 */}
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                        <span className="text-green-600 text-lg">🌱</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">ESG 점수</dt>
                        <dd className="text-lg font-medium text-gray-900">87/100</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Charts and Recent Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Chart Placeholder */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">매출 추이</h3>
                <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
                  <div className="text-gray-500 text-center">
                    <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    <p>차트가 여기에 표시됩니다</p>
                  </div>
                </div>
              </div>

              {/* Recent Activity */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">최근 활동</h3>
                <div className="flow-root">
                  <ul className="-mb-8">
                    {recentActivities.map((activity, activityIdx) => (
                      <li key={activity.id}>
                        <div className="relative pb-8">
                          {activityIdx !== recentActivities.length - 1 ? (
                            <span className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200" aria-hidden="true" />
                          ) : null}
                          <div className="relative flex space-x-3">
                            <div>
                              <span className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center ring-8 ring-white">
                                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                </svg>
                              </span>
                            </div>
                            <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                              <div>
                                <p className="text-sm text-gray-500">
                                  <span className="font-medium text-gray-900">{activity.user}</span> {activity.description}
                                </p>
                              </div>
                              <div className="text-right text-sm whitespace-nowrap text-gray-500">
                                <time>{activity.time}</time>
                              </div>
                            </div>
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            {/* ESG 데이터 섹션 */}
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">ESG 데이터 현황</h3>
                                     <button
                     onClick={() => handleNavigation('/data-upload')}
                     className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 transition-colors"
                   >
                    데이터 업로드
                  </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="border rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                      <span className="text-green-600 mr-2">🌱</span>
                      환경 (Environmental)
                    </h4>
                    <div className="text-sm text-gray-600">
                      <div className="flex justify-between">
                        <span>완료 항목:</span>
                        <span className="text-green-600">2/3</span>
                      </div>
                      <div className="flex justify-between">
                        <span>점수:</span>
                        <span className="text-green-600">85점</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="border rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                      <span className="text-blue-600 mr-2">👥</span>
                      사회 (Social)
                    </h4>
                    <div className="text-sm text-gray-600">
                      <div className="flex justify-between">
                        <span>완료 항목:</span>
                        <span className="text-yellow-600">1/3</span>
                      </div>
                      <div className="flex justify-between">
                        <span>점수:</span>
                        <span className="text-yellow-600">75점</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="border rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                      <span className="text-purple-600 mr-2">⚖️</span>
                      지배구조 (Governance)
                    </h4>
                    <div className="text-sm text-gray-600">
                      <div className="flex justify-between">
                        <span>완료 항목:</span>
                        <span className="text-green-600">2/3</span>
                      </div>
                      <div className="flex justify-between">
                        <span>점수:</span>
                        <span className="text-green-600">90점</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Projects */}
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">진행 중인 프로젝트</h3>
                <div className="overflow-hidden">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">프로젝트</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">진행률</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">상태</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">마감일</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {projects.map((project) => (
                        <tr key={project.id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">{project.name}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div className="w-full bg-gray-200 rounded-full h-2 mr-2">
                                <div 
                                  className="bg-blue-600 h-2 rounded-full" 
                                  style={{ width: `${project.progress}%` }}
                                ></div>
                              </div>
                              <span className="text-sm text-gray-500">{project.progress}%</span>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              project.status === '완료' ? 'bg-green-100 text-green-800' :
                              project.status === '진행중' ? 'bg-blue-100 text-blue-800' :
                              'bg-yellow-100 text-yellow-800'
                            }`}>
                              {project.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {project.dueDate}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'esg' && (
          <div className="space-y-6">
            {/* ESG 대시보드 헤더 */}
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold text-gray-900">ESG 데이터 관리</h2>
                <button
                  onClick={() => router.push('/data-upload')}
                  className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2"
                >
                  <span>📤</span>
                  <span>데이터 업로드</span>
                </button>
              </div>
              
              {/* ESG 요약 카드 */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center mr-3">
                      <span className="text-green-600 text-lg">🌱</span>
                    </div>
                    <div>
                      <p className="text-sm text-green-600 font-medium">총 ESG 점수</p>
                      <p className="text-2xl font-bold text-green-700">87/100</p>
                    </div>
                  </div>
                </div>
                
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                      <span className="text-blue-600 text-lg">📊</span>
                    </div>
                    <div>
                      <p className="text-sm text-blue-600 font-medium">완료 항목</p>
                      <p className="text-2xl font-bold text-blue-700">24/30</p>
                    </div>
                  </div>
                </div>
                
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <div className="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center mr-3">
                      <span className="text-yellow-600 text-lg">⚠️</span>
                    </div>
                    <div>
                      <p className="text-sm text-yellow-600 font-medium">개선 필요</p>
                      <p className="text-2xl font-bold text-yellow-700">6개</p>
                    </div>
                  </div>
                </div>
                
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
                      <span className="text-purple-600 text-lg">📅</span>
                    </div>
                    <div>
                      <p className="text-sm text-purple-600 font-medium">다음 제출일</p>
                      <p className="text-lg font-bold text-purple-700">2024-02-15</p>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* ESG 카테고리별 상세 정보 */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="border rounded-lg p-4">
                  <h3 className="font-medium text-gray-900 mb-3 flex items-center">
                    <span className="text-green-600 mr-2">🌱</span>
                    환경 (Environmental)
                  </h3>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>탄소 배출량</span>
                      <span className="text-green-600">✅ 완료</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>에너지 효율성</span>
                      <span className="text-yellow-600">🔄 진행중</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>폐기물 관리</span>
                      <span className="text-green-600">✅ 완료</span>
                    </div>
                  </div>
                </div>
                
                <div className="border rounded-lg p-4">
                  <h3 className="font-medium text-gray-900 mb-3 flex items-center">
                    <span className="text-blue-600 mr-2">👥</span>
                    사회 (Social)
                  </h3>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>노동 조건</span>
                      <span className="text-green-600">✅ 완료</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>공급망 관리</span>
                      <span className="text-red-600">❌ 미완료</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>커뮤니티 참여</span>
                      <span className="text-yellow-600">🔄 진행중</span>
                    </div>
                  </div>
                </div>
                
                <div className="border rounded-lg p-4">
                  <h3 className="font-medium text-gray-900 mb-3 flex items-center">
                    <span className="text-purple-600 mr-2">⚖️</span>
                    지배구조 (Governance)
                  </h3>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>이사회 구성</span>
                      <span className="text-green-600">✅ 완료</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>윤리 경영</span>
                      <span className="text-green-600">✅ 완료</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>투명성</span>
                      <span className="text-yellow-600">🔄 진행중</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'projects' && (
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">프로젝트 관리</h2>
            <p className="text-gray-600">프로젝트 관리 기능이 여기에 구현됩니다.</p>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">데이터 분석</h2>
            <p className="text-gray-600">데이터 분석 기능이 여기에 구현됩니다.</p>
          </div>
        )}

        {activeTab === 'reports' && (
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">보고서</h2>
            <p className="text-gray-600">보고서 기능이 여기에 구현됩니다.</p>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">설정</h2>
            <p className="text-gray-600">설정 기능이 여기에 구현됩니다.</p>
          </div>
        )}
      </main>
    </div>
  );
}
