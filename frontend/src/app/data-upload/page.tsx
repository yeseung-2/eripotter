'use client';

import { useState, useCallback, useMemo, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { logInfo, logError, logWarn } from '@/lib/logger';

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  status: 'uploading' | 'mapping' | 'ai_validating' | 'success' | 'error';
  progress: number;
  validationResult?: any;
  mappingResult?: any;
  aiValidationResult?: any;
  uploadedAt: string;
  uploadedBy: string;
  description?: string;
  version?: string;
}

interface CompanyData {
  id: string;
  name: string;
  type: 'partner' | 'client';
  status: 'active' | 'pending' | 'approved';
  lastUpdated: string;
  dataQuality: number;
}

export default function PartnerDataUploadPage() {
  const [activeTab, setActiveTab] = useState<'upload' | 'dashboard' | 'reports'>('upload');
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [partnerInfo, setPartnerInfo] = useState({
    name: 'LG화학',
    companyId: 'LG001',
    status: 'active',
    lastSubmission: '2024-01-15',
    nextDeadline: '2024-02-15'
  });

  // 사용자 정보 로드
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const companyId = localStorage.getItem('user_company_id');
      const userId = localStorage.getItem('user_id');
      const userName = localStorage.getItem('user_name');
      
      if (companyId) {
        // 회사 ID를 기반으로 회사명 매핑 (실제로는 API에서 가져와야 함)
        const companyMapping: { [key: string]: string } = {
          'LG001': 'LG화학',
          'SAMSUNG001': '삼성전자',
          'HYUNDAI001': '현대자동차',
          'SK001': 'SK하이닉스',
          'POSCO001': '포스코',
          'LOTTE001': '롯데케미칼',
          'CJ001': 'CJ제일제당',
          'HANWHA001': '한화솔루션',
          'GS001': 'GS칼텍스',
          'KOGAS001': '한국가스공사'
        };

        const companyName = companyMapping[companyId] || companyId;
        const displayName = userName || userId || '담당자';
        
        setPartnerInfo(prev => ({
          ...prev,
          name: companyName,
          companyId: companyId,
          userName: displayName
        }));

        logInfo("👤 사용자 정보 로드", { 
          user_id: userId, 
          company_id: companyId, 
          company_name: companyName,
          user_name: displayName
        });
      }
    }
  }, []);

  // 파일 업로드 처리
  const onDrop = useCallback((acceptedFiles: File[]) => {
    logInfo("📁 파일 업로드 시작", { fileCount: acceptedFiles.length });
    
    const newFiles: UploadedFile[] = acceptedFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'uploading',
      progress: 0,
      uploadedAt: new Date().toISOString(),
      uploadedBy: '김철수', // 실제로는 로그인된 사용자 정보
      description: '',
      version: '1.0'
    }));

    setUploadedFiles(prev => [...prev, ...newFiles]);

    // 파일 업로드 시뮬레이션
    newFiles.forEach(file => {
      simulateFileUpload(file.id);
    });
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'text/csv': ['.csv'],
      'application/pdf': ['.pdf']
    },
    multiple: true
  });

  // AI 데이터 매핑 검증 프로세스 시뮬레이션
  const simulateFileUpload = (fileId: string) => {
    // 1단계: 파일 업로드
    const uploadInterval = setInterval(() => {
      setUploadedFiles(prev => prev.map(file => {
        if (file.id === fileId) {
          if (file.progress < 100) {
            return { ...file, progress: file.progress + 10 };
          } else {
            clearInterval(uploadInterval);
            logInfo("✅ 파일 업로드 완료", { fileName: file.name });
            return { ...file, status: 'mapping', progress: 0 };
          }
        }
        return file;
      }));
    }, 200);

    // 2단계: 데이터 매핑 (1초 후)
    setTimeout(() => {
      setUploadedFiles(prev => prev.map(file => {
        if (file.id === fileId) {
          const mappingResult = {
            mappedFields: [
              { original: '탄소배출량', mapped: 'carbon_emissions', confidence: 0.95 },
              { original: '에너지효율성', mapped: 'energy_efficiency', confidence: 0.87 },
              { original: '폐기물관리', mapped: 'waste_management', confidence: 0.92 },
              { original: '노동조건', mapped: 'labor_conditions', confidence: 0.78 }
            ],
            unmappedFields: [
              { field: '공급망관리', reason: '표준 필드에 매핑할 수 없음' }
            ],
            mappingScore: 0.85
          };
          
          logInfo("🗺️ 데이터 매핑 완료", { 
            fileName: file.name, 
            mappedCount: mappingResult.mappedFields.length,
            mappingScore: mappingResult.mappingScore
          });
          
          return { 
            ...file, 
            status: 'ai_validating', 
            progress: 0,
            mappingResult 
          };
        }
        return file;
      }));
    }, 1000);

    // 3단계: AI 검증 (2초 후)
    setTimeout(() => {
      const aiValidationInterval = setInterval(() => {
        setUploadedFiles(prev => prev.map(file => {
          if (file.id === fileId) {
            if (file.progress < 100) {
              return { ...file, progress: file.progress + 20 };
            } else {
              clearInterval(aiValidationInterval);
              
              const aiValidationResult = {
                isValid: Math.random() > 0.2, // 80% 성공률
                confidence: Math.random() * 0.3 + 0.7, // 70-100% 신뢰도
                recommendations: [
                  '공급망 관리 데이터 추가 권장',
                  '에너지 효율성 데이터 정확성 검토 필요',
                  '탄소 배출량 데이터는 우수함'
                ],
                issues: Math.random() > 0.6 ? [
                  { field: '공급망 관리', severity: 'medium', message: '데이터가 불완전합니다.' },
                  { field: '에너지 효율성', severity: 'low', message: '단위 변환이 필요합니다.' }
                ] : []
              };
              
              logInfo("🤖 AI 검증 완료", { 
                fileName: file.name, 
                isValid: aiValidationResult.isValid,
                confidence: aiValidationResult.confidence,
                issueCount: aiValidationResult.issues.length
              });
              
              return { 
                ...file, 
                status: aiValidationResult.isValid ? 'success' : 'error',
                aiValidationResult 
              };
            }
          }
          return file;
        }));
      }, 300);
    }, 2000);
  };

  // 파일 삭제
  const removeFile = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
    logInfo("🗑️ 파일 삭제", { fileId });
  };

  // 전체 파일 삭제
  const removeAllFiles = () => {
    setUploadedFiles([]);
    logInfo("🗑️ 전체 파일 삭제");
  };

  // 선택된 파일들 삭제
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  
  const toggleFileSelection = (fileId: string) => {
    setSelectedFiles(prev => 
      prev.includes(fileId) 
        ? prev.filter(id => id !== fileId)
        : [...prev, fileId]
    );
  };

  const removeSelectedFiles = () => {
    setUploadedFiles(prev => prev.filter(f => !selectedFiles.includes(f.id)));
    setSelectedFiles([]);
    logInfo("🗑️ 선택된 파일들 삭제", { count: selectedFiles.length });
  };

  const selectAllFiles = () => {
    setSelectedFiles(uploadedFiles.map(f => f.id));
  };

  const deselectAllFiles = () => {
    setSelectedFiles([]);
  };

  // 통계 계산
  const stats = useMemo(() => {
    const totalFiles = uploadedFiles.length;
    const successFiles = uploadedFiles.filter(f => f.status === 'success').length;
    const errorFiles = uploadedFiles.filter(f => f.status === 'error').length;
    const pendingFiles = uploadedFiles.filter(f => 
      f.status === 'uploading' || f.status === 'mapping' || f.status === 'ai_validating'
    ).length;

    return { totalFiles, successFiles, errorFiles, pendingFiles };
  }, [uploadedFiles]);

  // 날짜 포맷팅 함수
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // 파일 크기 포맷팅 함수
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">협력사 ESG 데이터 관리</h1>
            </div>
            <div className="flex items-center space-x-4">
                             <div className="text-sm text-gray-600">
                 <span className="font-medium">{partnerInfo.name}</span> ({partnerInfo.userName || '담당자'})
               </div>
              <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                partnerInfo.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
              }`}>
                {partnerInfo.status === 'active' ? '활성' : '대기중'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {[
              { id: 'upload', name: '데이터 업로드', icon: '📤' },
              { id: 'dashboard', name: '자가진단 대시보드', icon: '📊' },
              { id: 'reports', name: '보고서 생성', icon: '📋' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {activeTab === 'upload' && (
          <div className="space-y-6">
            {/* File Upload Area - 상단에 배치 */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">파일 업로드</h3>
              
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                  isDragActive
                    ? 'border-blue-400 bg-blue-50'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <input {...getInputProps()} />
                <div className="space-y-4">
                  <div className="text-6xl">📁</div>
                  <div>
                    <p className="text-lg font-medium text-gray-900">
                      {isDragActive ? '파일을 여기에 놓으세요' : '파일을 드래그하거나 클릭하여 업로드'}
                    </p>
                    <p className="text-sm text-gray-500 mt-2">
                      Excel (.xlsx, .xls), CSV (.csv), PDF (.pdf) 파일을 지원합니다
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* File Upload Statistics */}
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                        <span className="text-blue-600 text-lg">📁</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">총 파일</dt>
                        <dd className="text-lg font-medium text-gray-900">{stats.totalFiles}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                        <span className="text-green-600 text-lg">✅</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">성공</dt>
                        <dd className="text-lg font-medium text-gray-900">{stats.successFiles}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
                        <span className="text-red-600 text-lg">❌</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">오류</dt>
                        <dd className="text-lg font-medium text-gray-900">{stats.errorFiles}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
                        <span className="text-yellow-600 text-lg">⏳</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">처리중</dt>
                        <dd className="text-lg font-medium text-gray-900">{stats.pendingFiles}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>



            {/* Uploaded Files History Table */}
            {uploadedFiles.length > 0 && (
              <div className="bg-white shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">업로드 히스토리</h3>
                    <div className="flex space-x-2">
                      {selectedFiles.length > 0 && (
                        <button
                          onClick={removeSelectedFiles}
                          className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700 transition-colors"
                        >
                          선택 삭제 ({selectedFiles.length})
                        </button>
                      )}
                      <button
                        onClick={removeAllFiles}
                        className="bg-gray-600 text-white px-3 py-1 rounded text-sm hover:bg-gray-700 transition-colors"
                      >
                        전체 삭제
                      </button>
                    </div>
                  </div>
                  
                                     <div className="overflow-x-auto">
                     <table className="min-w-full divide-y divide-gray-200">
                       <thead className="bg-gray-50">
                         <tr>
                           <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-8">
                             <input
                               type="checkbox"
                               checked={selectedFiles.length === uploadedFiles.length && uploadedFiles.length > 0}
                               onChange={() => selectedFiles.length === uploadedFiles.length ? deselectAllFiles() : selectAllFiles()}
                               className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                             />
                           </th>
                           <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-48">파일명</th>
                           <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-20">크기</th>
                           <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-24">업로드자</th>
                           <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-32">업로드 시간</th>
                                                       <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-28">상태</th>
                         </tr>
                       </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                                                 {uploadedFiles.map((file) => (
                           <tr key={file.id} className="hover:bg-gray-50">
                             <td className="px-3 py-4 whitespace-nowrap">
                               <input
                                 type="checkbox"
                                 checked={selectedFiles.includes(file.id)}
                                 onChange={() => toggleFileSelection(file.id)}
                                 className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                               />
                             </td>
                             <td className="px-3 py-4 whitespace-nowrap">
                               <div className="flex items-center">
                                 <div className="flex-shrink-0 h-8 w-8">
                                   {file.status === 'uploading' && <span className="text-blue-500 text-lg">⏳</span>}
                                   {file.status === 'mapping' && <span className="text-yellow-500 text-lg">🗺️</span>}
                                   {file.status === 'ai_validating' && <span className="text-purple-500 text-lg">🤖</span>}
                                   {file.status === 'success' && <span className="text-green-500 text-lg">✅</span>}
                                   {file.status === 'error' && <span className="text-red-500 text-lg">❌</span>}
                                 </div>
                                 <div className="ml-3 min-w-0 flex-1">
                                   <div className="text-sm font-medium text-gray-900 truncate">{file.name}</div>
                                   <div className="text-xs text-gray-500 truncate">{file.type}</div>
                                 </div>
                               </div>
                             </td>
                             <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-900">
                               {formatFileSize(file.size)}
                             </td>
                             <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-900">
                               {file.uploadedBy}
                             </td>
                             <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500">
                               {formatDate(file.uploadedAt)}
                             </td>
                                                           <td className="px-3 py-4 whitespace-nowrap">
                                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                  file.status === 'success' ? 'bg-green-100 text-green-800' :
                                  file.status === 'error' ? 'bg-red-100 text-red-800' :
                                  file.status === 'ai_validating' ? 'bg-purple-100 text-purple-800' :
                                  file.status === 'mapping' ? 'bg-yellow-100 text-yellow-800' :
                                  'bg-blue-100 text-blue-800'
                                }`}>
                                  {file.status === 'uploading' ? '업로드중' :
                                   file.status === 'mapping' ? '매핑중' :
                                   file.status === 'ai_validating' ? 'AI검증중' :
                                   file.status === 'success' ? '완료' : '오류'}
                                </span>
                                {(file.status === 'uploading' || file.status === 'mapping' || file.status === 'ai_validating') && (
                                  <div className="mt-1 w-full bg-gray-200 rounded-full h-1">
                                    <div
                                      className={`h-1 rounded-full transition-all duration-300 ${
                                        file.status === 'uploading' ? 'bg-blue-600' :
                                        file.status === 'mapping' ? 'bg-yellow-600' :
                                        'bg-purple-600'
                                      }`}
                                      style={{ width: `${file.progress}%` }}
                                    ></div>
                                  </div>
                                )}
                              </td>
                           </tr>
                         ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {/* Partner Self-Assessment Dashboard */}
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                        <span className="text-blue-600 text-lg">📊</span>
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

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                        <span className="text-green-600 text-lg">✅</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">완료 항목</dt>
                        <dd className="text-lg font-medium text-gray-900">24/30</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
                        <span className="text-yellow-600 text-lg">⚠️</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">개선 필요</dt>
                        <dd className="text-lg font-medium text-gray-900">6개</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                        <span className="text-purple-600 text-lg">📅</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">다음 제출일</dt>
                        <dd className="text-lg font-medium text-gray-900">{partnerInfo.nextDeadline}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* ESG Categories */}
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">ESG 카테고리별 진단</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="border rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                      <span className="text-green-600 mr-2">🌱</span>
                      환경 (Environmental)
                    </h4>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>탄소 배출량</span>
                        <span className="text-green-600">완료</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>에너지 효율성</span>
                        <span className="text-yellow-600">진행중</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>폐기물 관리</span>
                        <span className="text-green-600">완료</span>
                      </div>
                    </div>
                  </div>

                  <div className="border rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                      <span className="text-blue-600 mr-2">👥</span>
                      사회 (Social)
                    </h4>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>노동 조건</span>
                        <span className="text-green-600">완료</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>공급망 관리</span>
                        <span className="text-red-600">미완료</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>커뮤니티 참여</span>
                        <span className="text-yellow-600">진행중</span>
                      </div>
                    </div>
                  </div>

                  <div className="border rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                      <span className="text-purple-600 mr-2">⚖️</span>
                      지배구조 (Governance)
                    </h4>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>이사회 구성</span>
                        <span className="text-green-600">완료</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>윤리 경영</span>
                        <span className="text-green-600">완료</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>투명성</span>
                        <span className="text-yellow-600">진행중</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'reports' && (
          <div className="space-y-6">
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">ESG 보고서 생성</h2>
              <p className="text-gray-600">보고서 생성 기능이 여기에 구현됩니다.</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
