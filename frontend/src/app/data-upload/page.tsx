'use client';

import { useState, useCallback, useMemo, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';

enum FileUploadStatus {
  UPLOADING = 'uploading',
  MAPPING = 'mapping',
  AI_VALIDATING = 'ai_validating',
  SUCCESS = 'success',
  ERROR = 'error'
}

interface MappedField {
  original: string;
  mapped: string;
  confidence: number;
  casNumber: string;
  englishName: string;
  msdsName: string;
  esgIndicator: string;
  industryClass: string;
  required: string;
  unit: string;
  isManual?: boolean;
}

interface UnmappedField {
  field: string;
  reason: string;
  casNumber: string;
  englishName: string;
  msdsName: string;
  esgIndicator: string;
  industryClass: string;
  required: string;
  unit: string;
}

interface MappingResult {
  mappedFields: MappedField[];
  reviewFields: MappedField[];
  unmappedFields: UnmappedField[];
  mappingScore: number;
}

interface ValidationIssue {
  field: string;
  severity: 'low' | 'medium' | 'high';
  message: string;
}

interface AIValidationResult {
  isValid: boolean;
  confidence: number;
  recommendations: string[];
  issues: ValidationIssue[];
}

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  status: FileUploadStatus;
  progress: number;
  mappingResult?: MappingResult;
  aiValidationResult?: AIValidationResult;
  uploadedAt: string;
  uploadedBy: string;
  description?: string;
  version?: string;
  file?: File;
}

export default function PartnerDataUploadPage() {
  const [activeTab, setActiveTab] = useState<'upload' | 'reports'>('upload');
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [partnerInfo, setPartnerInfo] = useState({
     name: 'LG화학',
     companyId: 'LG001',
     status: 'active',
     lastSubmission: '2024-01-15',
     nextDeadline: '2024-02-15',
     userName: '담당자'
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

        console.log("👤 사용자 정보 로드", { 
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
    console.log("📁 파일 업로드 시작", { fileCount: acceptedFiles.length });
    
    const newFiles: UploadedFile[] = acceptedFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      type: file.type,
      status: FileUploadStatus.UPLOADING,
      progress: 0,
      uploadedAt: new Date().toISOString(),
      uploadedBy: '김철수', // 실제로는 로그인된 사용자 정보
      description: '',
      version: '1.0',
      file: file // 실제 File 객체 저장
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
            console.log("✅ 파일 업로드 완료", { fileName: file.name });
            return { ...file, status: FileUploadStatus.MAPPING, progress: 0 };
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
              { 
                original: '이산화탄소', 
                mapped: 'GHG-CO2', 
                confidence: 0.95,
                casNumber: '124-38-9',
                englishName: 'Carbon dioxide',
                msdsName: '이산화탄소',
                esgIndicator: '온실가스별 배출량',
                industryClass: '공통',
                required: '필수',
                unit: 'tonCO2eq'
              },
              { 
                original: '에너지소비량', 
                mapped: 'ENERGY-CONSUMPTION', 
                confidence: 0.87,
                casNumber: 'N/A',
                englishName: 'Energy Consumption',
                msdsName: '에너지소비량',
                esgIndicator: '에너지 효율성',
                industryClass: '공통',
                required: '필수',
                unit: 'GJ'
              },
              { 
                original: '폐기물발생량', 
                mapped: 'WASTE-GENERATION', 
                confidence: 0.92,
                casNumber: 'N/A',
                englishName: 'Waste Generation',
                msdsName: '폐기물발생량',
                esgIndicator: '폐기물 관리',
                industryClass: '공통',
                required: '필수',
                unit: 'ton'
              }
            ],
            reviewFields: [
              { 
                original: '노동시간', 
                mapped: 'LABOR-HOURS', 
                confidence: 0.75,
                casNumber: 'N/A',
                englishName: 'Labor Hours',
                msdsName: '노동시간',
                esgIndicator: '노동 조건',
                industryClass: '공통',
                required: '필수',
                unit: 'hours'
              },
              { 
                original: 'HFC-227ea', 
                mapped: 'GHG-HFCs', 
                confidence: 0.72,
                casNumber: '431-89-0',
                englishName: '1,1,1,2,3,3,3-Heptafluoropropane',
                msdsName: '헵타플루오로프로판',
                esgIndicator: '온실가스별 배출량',
                industryClass: '공통',
                required: '선택',
                unit: 'tonCO2eq'
              }
            ],
            unmappedFields: [
              { 
                field: '공급망관리', 
                reason: '표준 필드에 매핑할 수 없음',
                casNumber: 'N/A',
                englishName: 'Supply Chain Management',
                msdsName: '공급망관리',
                esgIndicator: 'N/A',
                industryClass: 'N/A',
                required: 'N/A',
                unit: 'N/A'
              },
              { 
                field: '육발화황', 
                reason: '매핑 신뢰도가 낮음 (50% 미만)',
                casNumber: '2551-62-4',
                englishName: 'Sulfur hexafluoride',
                msdsName: '육불화황',
                esgIndicator: '온실가스별 배출량',
                industryClass: '공통',
                required: '선택',
                unit: 'tonCO2eq'
              }
            ],
            mappingScore: 0.83
          };
          
          console.log("🗺️ 데이터 매핑 완료", { 
            fileName: file.name, 
            mappedCount: mappingResult.mappedFields.length,
            mappingScore: mappingResult.mappingScore
          });
          
                      return { 
            ...file, 
            status: FileUploadStatus.AI_VALIDATING, 
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
                  { field: '공급망 관리', severity: 'medium' as const, message: '데이터가 불완전합니다.' },
                  { field: '에너지 효율성', severity: 'low' as const, message: '단위 변환이 필요합니다.' }
                ] : []
              };
              
              console.log("🤖 AI 검증 완료", { 
                fileName: file.name, 
                isValid: aiValidationResult.isValid,
                confidence: aiValidationResult.confidence,
                issueCount: aiValidationResult.issues.length
              });
              
              return { 
                ...file, 
                status: aiValidationResult.isValid ? FileUploadStatus.SUCCESS : FileUploadStatus.ERROR,
                aiValidationResult 
              };
            }
          }
          return file;
        }));
      }, 300);
    }, 2000);
  };

  // 전체 파일 삭제
  const removeAllFiles = () => {
    setUploadedFiles([]);
    console.log("🗑️ 전체 파일 삭제");
  };

  // 선택된 파일들 삭제
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [previewFile, setPreviewFile] = useState<File | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  const [showMappingModal, setShowMappingModal] = useState(false);
  const [currentMappingFile, setCurrentMappingFile] = useState<UploadedFile | null>(null);
  const [mappingFields, setMappingFields] = useState<MappedField[]>([]);
  const [reviewFields, setReviewFields] = useState<MappedField[]>([]);
  const [unmappedFields, setUnmappedFields] = useState<UnmappedField[]>([]);
  
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
    console.log("🗑️ 선택된 파일들 삭제", { count: selectedFiles.length });
  };

  const selectAllFiles = () => {
    setSelectedFiles(uploadedFiles.map(f => f.id));
  };

  const deselectAllFiles = () => {
    setSelectedFiles([]);
  };

  // 파일 미리보기 함수
  const handlePreviewFile = (file: UploadedFile) => {
    if (file.file) {
      setPreviewFile(file.file);
      setShowPreview(true);
    }
  };

  // 파일 미리보기 닫기
  const closePreview = () => {
    setShowPreview(false);
    setPreviewFile(null);
  };

  // 매핑 모달 열기
  const openMappingModal = (file: UploadedFile) => {
    if (file.mappingResult) {
      setCurrentMappingFile(file);
      setMappingFields(file.mappingResult.mappedFields || []);
      setReviewFields(file.mappingResult.reviewFields || []);
      setUnmappedFields(file.mappingResult.unmappedFields || []);
      setShowMappingModal(true);
    }
  };

  // 매핑 모달 닫기
  const closeMappingModal = () => {
    setShowMappingModal(false);
    setCurrentMappingFile(null);
    setMappingFields([]);
    setReviewFields([]);
    setUnmappedFields([]);
  };

  // 매핑 필드 수정
  const updateMappingField = (index: number, newMapping: Partial<MappedField>) => {
    setMappingFields(prev => prev.map((field, i) => 
      i === index ? { ...field, ...newMapping } : field
    ));
  };

  // 검토 필드 수정
  const updateReviewField = (index: number, newReview: Partial<MappedField>) => {
    setReviewFields(prev => prev.map((field, i) => 
      i === index ? { ...field, ...newReview } : field
    ));
  };

  // 매핑되지 않은 필드에 매핑 추가
  const addMappingForUnmappedField = (unmappedIndex: number, targetField: string) => {
    const unmappedField = unmappedFields[unmappedIndex];
    
    // 표준 필드 정보 매핑
    const standardFieldInfo: Record<string, Omit<MappedField, 'original' | 'mapped' | 'confidence' | 'isManual'>> = {
      'GHG-CO2': {
        casNumber: '124-38-9',
        englishName: 'Carbon dioxide',
        msdsName: '이산화탄소',
        esgIndicator: '온실가스별 배출량',
        industryClass: '공통',
        required: '필수',
        unit: 'tonCO2eq'
      },
      'GHG-N2O': {
        casNumber: '10024-97-2',
        englishName: 'Dinitrogen oxide',
        msdsName: '아산화질소',
        esgIndicator: '온실가스별 배출량',
        industryClass: '공통',
        required: '필수',
        unit: 'tonCO2eq'
      },
      'GHG-HFCs': {
        casNumber: 'N/A',
        englishName: 'Hydrofluorocarbons',
        msdsName: '수소불화탄소',
        esgIndicator: '온실가스별 배출량',
        industryClass: '공통',
        required: '선택',
        unit: 'tonCO2eq'
      },
      'GHG-SF6': {
        casNumber: '2551-62-4',
        englishName: 'Sulfur hexafluoride',
        msdsName: '육불화황',
        esgIndicator: '온실가스별 배출량',
        industryClass: '공통',
        required: '선택',
        unit: 'tonCO2eq'
      },
      'GHG-NF3': {
        casNumber: '7783-54-2',
        englishName: 'Nitrogen trifluoride',
        msdsName: '삼불화질소',
        esgIndicator: '온실가스별 배출량',
        industryClass: '공통',
        required: '선택',
        unit: 'tonCO2eq'
      },
      'ENERGY-CONSUMPTION': {
        casNumber: 'N/A',
        englishName: 'Energy Consumption',
        msdsName: '에너지소비량',
        esgIndicator: '에너지 효율성',
        industryClass: '공통',
        required: '필수',
        unit: 'GJ'
      },
      'WASTE-GENERATION': {
        casNumber: 'N/A',
        englishName: 'Waste Generation',
        msdsName: '폐기물발생량',
        esgIndicator: '폐기물 관리',
        industryClass: '공통',
        required: '필수',
        unit: 'ton'
      },
      'LABOR-HOURS': {
        casNumber: 'N/A',
        englishName: 'Labor Hours',
        msdsName: '노동시간',
        esgIndicator: '노동 조건',
        industryClass: '공통',
        required: '필수',
        unit: 'hours'
      },
      'SUPPLY-CHAIN': {
        casNumber: 'N/A',
        englishName: 'Supply Chain Management',
        msdsName: '공급망관리',
        esgIndicator: '공급망 관리',
        industryClass: '공통',
        required: '필수',
        unit: 'N/A'
      },
      'STD-VOC': {
        casNumber: 'N/A',
        englishName: 'Volatile Organic Compounds',
        msdsName: '휘발성유기화합물',
        esgIndicator: '대기오염물질 배출량',
        industryClass: '공통',
        required: '선택',
        unit: 'ton'
      },
      'APE-VOC': {
        casNumber: 'N/A',
        englishName: 'Air Pollutant Emissions - VOC',
        msdsName: '대기오염물질',
        esgIndicator: '대기오염물질 배출량',
        industryClass: '공통',
        required: '필수',
        unit: 'ton'
      }
    };

    const fieldInfo = standardFieldInfo[targetField as keyof typeof standardFieldInfo] || {
      casNumber: 'N/A',
      englishName: 'Unknown',
      msdsName: '알 수 없음',
      esgIndicator: 'N/A',
      industryClass: 'N/A',
      required: 'N/A',
      unit: 'N/A'
    };

    const newMapping = {
      original: unmappedField.field,
      mapped: targetField,
      confidence: 0.5, // 수동 매핑이므로 중간 신뢰도
      isManual: true,
      ...fieldInfo
    };
    
    setMappingFields(prev => [...prev, newMapping]);
    setUnmappedFields(prev => prev.filter((_, i) => i !== unmappedIndex));
  };

  // 매핑 저장
  const saveMapping = () => {
    if (currentMappingFile) {
      const updatedMappingResult = {
        ...currentMappingFile.mappingResult,
        mappedFields: mappingFields,
        reviewFields: reviewFields, // 새로 추가된 상태
        unmappedFields: unmappedFields,
        mappingScore: mappingFields.length / (mappingFields.length + unmappedFields.length)
      };

      setUploadedFiles(prev => prev.map(file => 
        file.id === currentMappingFile.id 
          ? { ...file, mappingResult: updatedMappingResult }
          : file
      ));

      console.log("🗺️ 매핑 수정 완료", { 
        fileName: currentMappingFile.name,
        mappedCount: mappingFields.length,
        unmappedCount: unmappedFields.length
      });

      closeMappingModal();
    }
  };

  // 통계 계산
  const stats = useMemo(() => {
    const totalFiles = uploadedFiles.length;
    const successFiles = uploadedFiles.filter(f => f.status === FileUploadStatus.SUCCESS).length;
    const errorFiles = uploadedFiles.filter(f => f.status === FileUploadStatus.ERROR).length;
    const pendingFiles = uploadedFiles.filter(f => 
      f.status === FileUploadStatus.UPLOADING || f.status === FileUploadStatus.MAPPING || f.status === FileUploadStatus.AI_VALIDATING
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
              { id: 'reports', name: '보고서 생성', icon: '📋' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as 'upload' | 'reports')}
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
                           <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-24">원문보기</th>
                           <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-24">매핑</th>
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
                                   {/* 파일 타입별 아이콘 */}
                                   {file.name.toLowerCase().endsWith('.xlsx') || file.name.toLowerCase().endsWith('.xls') ? (
                                     <span className="text-green-600 text-lg">📈</span>
                                   ) : file.name.toLowerCase().endsWith('.pdf') ? (
                                     <span className="text-red-600 text-lg">📄</span>
                                   ) : file.name.toLowerCase().endsWith('.csv') ? (
                                     <span className="text-blue-600 text-lg">📊</span>
                                   ) : file.name.toLowerCase().endsWith('.txt') ? (
                                     <span className="text-gray-600 text-lg">📝</span>
                                   ) : (
                                     <span className="text-gray-500 text-lg">📁</span>
                                   )}
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
                                  file.status === FileUploadStatus.SUCCESS ? 'bg-green-100 text-green-800' :
                                  file.status === FileUploadStatus.ERROR ? 'bg-red-100 text-red-800' :
                                  file.status === FileUploadStatus.AI_VALIDATING ? 'bg-purple-100 text-purple-800' :
                                  file.status === FileUploadStatus.MAPPING ? 'bg-yellow-100 text-yellow-800' :
                                  'bg-blue-100 text-blue-800'
                                }`}>
                                  {file.status === FileUploadStatus.UPLOADING ? '업로드중' :
                                   file.status === FileUploadStatus.MAPPING ? '매핑중' :
                                   file.status === FileUploadStatus.AI_VALIDATING ? 'AI검증중' :
                                   file.status === FileUploadStatus.SUCCESS ? '완료' : '오류'}
                                </span>
                                {(file.status === FileUploadStatus.UPLOADING || file.status === FileUploadStatus.MAPPING || file.status === FileUploadStatus.AI_VALIDATING) && (
                                  <div className="mt-1 w-full bg-gray-200 rounded-full h-1">
                                    <div
                                      className={`h-1 rounded-full transition-all duration-300 ${
                                        file.status === FileUploadStatus.UPLOADING ? 'bg-blue-600' :
                                        file.status === FileUploadStatus.MAPPING ? 'bg-yellow-600' :
                                        'bg-purple-600'
                                      }`}
                                      style={{ width: `${file.progress}%` }}
                                    ></div>
                                  </div>
                                )}
                              </td>
                              <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-900">
                                <div className="flex space-x-2">
                                                                     <button
                                     onClick={() => handlePreviewFile(file)}
                                     className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 shadow-sm hover:shadow-md"
                                   >
                                     <svg className="w-3 h-3 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                       <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                       <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                     </svg>
                                     원문보기
                                   </button>
                                </div>
                              </td>
                              <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-900">
                                <div className="flex space-x-2">
                                   {file.mappingResult && (
                                     <button
                                       onClick={() => openMappingModal(file)}
                                       className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-all duration-200 shadow-sm hover:shadow-md"
                                     >
                                       <svg className="w-3 h-3 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                         <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                       </svg>
                                       매핑수정
                                     </button>
                                   )}
                                 </div>
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

      {/* 파일 미리보기 모달 */}
      {showPreview && previewFile && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900">파일 미리보기</h3>
                <button
                  onClick={closePreview}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <span className="text-2xl">×</span>
                </button>
              </div>
              
              <div className="mb-4">
                <h4 className="font-medium text-gray-900 mb-2">{previewFile.name}</h4>
                <p className="text-sm text-gray-600">
                  크기: {formatFileSize(previewFile.size)} | 
                  타입: {previewFile.type}
                </p>
              </div>

              <div className="border rounded-lg p-4 bg-gray-50 max-h-96 overflow-y-auto">
                {previewFile.type.includes('text') || previewFile.type.includes('csv') ? (
                  <pre className="text-sm text-gray-800 whitespace-pre-wrap">
                    {/* 텍스트 파일 내용을 여기에 표시 */}
                    파일 내용을 읽는 중...
                  </pre>
                ) : previewFile.type.includes('pdf') ? (
                  <div className="text-center py-8">
                    <div className="text-6xl mb-4">📄</div>
                    <p className="text-gray-600">PDF 파일은 미리보기를 지원하지 않습니다.</p>
                    <a
                      href={URL.createObjectURL(previewFile)}
                      download={previewFile.name}
                      className="mt-4 inline-block bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                    >
                      다운로드
                    </a>
                  </div>
                ) : previewFile.type.includes('excel') || previewFile.type.includes('spreadsheet') ? (
                  <div className="text-center py-8">
                    <div className="text-6xl mb-4">📊</div>
                    <p className="text-gray-600">Excel 파일은 미리보기를 지원하지 않습니다.</p>
                    <a
                      href={URL.createObjectURL(previewFile)}
                      download={previewFile.name}
                      className="mt-4 inline-block bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                    >
                      다운로드
                    </a>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="text-6xl mb-4">📁</div>
                    <p className="text-gray-600">이 파일 형식은 미리보기를 지원하지 않습니다.</p>
                    <a
                      href={URL.createObjectURL(previewFile)}
                      download={previewFile.name}
                      className="mt-4 inline-block bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                    >
                      다운로드
                    </a>
                  </div>
                )}
              </div>

              <div className="flex justify-end mt-4 space-x-3">
                <button
                  onClick={closePreview}
                  className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
                >
                  닫기
                </button>
                <a
                  href={URL.createObjectURL(previewFile)}
                  download={previewFile.name}
                  className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                >
                  다운로드
                </a>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 매핑 수정 모달 */}
      {showMappingModal && currentMappingFile && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-10 mx-auto p-5 border w-11/12 md:w-4/5 lg:w-3/4 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900">데이터 매핑 수정</h3>
                <button
                  onClick={closeMappingModal}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <span className="text-2xl">×</span>
                </button>
              </div>
              
              <div className="mb-4">
                <h4 className="font-medium text-gray-900 mb-2">{currentMappingFile.name}</h4>
                <p className="text-sm text-gray-600">
                  AI가 자동으로 매핑한 결과를 검토하고 수정할 수 있습니다.
                </p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* 매핑된 필드 */}
                <div className="border rounded-lg p-4">
                  <h5 className="font-medium text-gray-900 mb-3 flex items-center">
                    <span className="text-green-600 mr-2">✅</span>
                    매핑된 필드 ({mappingFields.length})
                  </h5>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {mappingFields.map((field, index) => (
                      <div key={index} className="border rounded p-3 bg-green-50">
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex-1">
                            <div className="text-sm font-medium text-gray-900">
                               원본: {field.original}
                             </div>
                             <div className="text-sm text-gray-600">
                               매핑: {field.mapped}
                             </div>
                             <div className="text-xs text-gray-500 mt-1">
                               CAS: {field.casNumber} | 단위: {field.unit}
                             </div>
                             <div className="text-xs text-gray-500">
                               영문: {field.englishName} | MSDS: {field.msdsName}
                             </div>
                           </div>
                           <div className="flex items-center space-x-2">
                             <span className={`px-2 py-1 text-xs rounded-full ${
                               field.confidence >= 0.8 ? 'bg-green-100 text-green-800' :
                               field.confidence >= 0.6 ? 'bg-yellow-100 text-yellow-800' :
                               'bg-red-100 text-red-800'
                             }`}>
                               {Math.round(field.confidence * 100)}%
                             </span>
                             {field.isManual && (
                               <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                                 수동
                               </span>
                             )}
                           </div>
                         </div>
                         <div className="flex space-x-2">
                           <select
                             value={field.mapped}
                             onChange={(e) => updateMappingField(index, { mapped: e.target.value })}
                             className="text-xs border rounded px-2 py-1 flex-1"
                           >
                             <option value="GHG-CO2">GHG-CO2 (이산화탄소)</option>
                             <option value="GHG-N2O">GHG-N2O (아산화질소)</option>
                             <option value="GHG-HFCs">GHG-HFCs (수소불화탄소)</option>
                             <option value="GHG-SF6">GHG-SF6 (육불화황)</option>
                             <option value="GHG-NF3">GHG-NF3 (삼불화질소)</option>
                             <option value="ENERGY-CONSUMPTION">에너지 소비량</option>
                             <option value="WASTE-GENERATION">폐기물 발생량</option>
                             <option value="LABOR-HOURS">노동 시간</option>
                             <option value="SUPPLY-CHAIN">공급망 관리</option>
                             <option value="STD-VOC">STD-VOC (휘발성유기화합물)</option>
                             <option value="APE-VOC">APE-VOC (대기오염물질)</option>
                           </select>
                           <button
                             onClick={() => {
                               setMappingFields(prev => prev.filter((_, i) => i !== index));
                               setUnmappedFields(prev => [...prev, { 
                                 field: field.original, 
                                 reason: '수동으로 매핑 해제됨',
                                 casNumber: field.casNumber,
                                 englishName: field.englishName,
                                 msdsName: field.msdsName,
                                 esgIndicator: field.esgIndicator,
                                 industryClass: field.industryClass,
                                 required: field.required,
                                 unit: field.unit
                               }]);
                             }}
                             className="text-xs text-red-600 hover:text-red-800 px-2 py-1 border border-red-300 rounded hover:bg-red-50"
                           >
                             해제
                           </button>
                         </div>
                       </div>
                     ))}
                  </div>
                </div>

                {/* 검토가 필요한 필드 */}
                <div className="border rounded-lg p-4">
                  <h5 className="font-medium text-gray-900 mb-3 flex items-center">
                    <span className="text-yellow-600 mr-2">⚠️</span>
                    검토가 필요한 필드 ({reviewFields.length})
                  </h5>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {reviewFields.map((field, index) => (
                      <div key={index} className="border rounded p-3 bg-yellow-50">
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex-1">
                            <div className="text-sm font-medium text-gray-900">
                               원본: {field.original}
                             </div>
                             <div className="text-sm text-gray-600">
                               매핑: {field.mapped}
                             </div>
                             <div className="text-xs text-gray-500 mt-1">
                                CAS: {field.casNumber} | 단위: {field.unit}
                             </div>
                             <div className="text-xs text-gray-500">
                               영문: {field.englishName} | MSDS: {field.msdsName}
                             </div>
                           </div>
                           <div className="flex items-center space-x-2">
                             <span className={`px-2 py-1 text-xs rounded-full ${
                               field.confidence >= 0.8 ? 'bg-green-100 text-green-800' :
                               field.confidence >= 0.6 ? 'bg-yellow-100 text-yellow-800' :
                               'bg-red-100 text-red-800'
                             }`}>
                               {Math.round(field.confidence * 100)}%
                             </span>
                             {field.isManual && (
                               <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                                 수동
                               </span>
                             )}
                           </div>
                         </div>
                         <div className="flex space-x-2">
                           <select
                             value={field.mapped}
                             onChange={(e) => updateReviewField(index, { mapped: e.target.value })}
                             className="text-xs border rounded px-2 py-1 flex-1"
                           >
                             <option value="GHG-CO2">GHG-CO2 (이산화탄소)</option>
                             <option value="GHG-N2O">GHG-N2O (아산화질소)</option>
                             <option value="GHG-HFCs">GHG-HFCs (수소불화탄소)</option>
                             <option value="GHG-SF6">GHG-SF6 (육불화황)</option>
                             <option value="GHG-NF3">GHG-NF3 (삼불화질소)</option>
                             <option value="ENERGY-CONSUMPTION">에너지 소비량</option>
                             <option value="WASTE-GENERATION">폐기물 발생량</option>
                             <option value="LABOR-HOURS">노동 시간</option>
                             <option value="SUPPLY-CHAIN">공급망 관리</option>
                             <option value="STD-VOC">STD-VOC (휘발성유기화합물)</option>
                             <option value="APE-VOC">APE-VOC (대기오염물질)</option>
                           </select>
                           <button
                             onClick={() => {
                               setReviewFields(prev => prev.filter((_, i) => i !== index));
                               setUnmappedFields(prev => [...prev, { 
                                 field: field.original, 
                                 reason: '수동으로 매핑 해제됨',
                                 casNumber: field.casNumber,
                                 englishName: field.englishName,
                                 msdsName: field.msdsName,
                                 esgIndicator: field.esgIndicator,
                                 industryClass: field.industryClass,
                                 required: field.required,
                                 unit: field.unit
                               }]);
                             }}
                             className="text-xs text-red-600 hover:text-red-800 px-2 py-1 border border-red-300 rounded hover:bg-red-50"
                           >
                             해제
                           </button>
                         </div>
                       </div>
                     ))}
                   </div>
                 </div>

                 {/* 매핑되지 않은 필드 */}
                 <div className="border rounded-lg p-4">
                   <h5 className="font-medium text-gray-900 mb-3 flex items-center">
                     <span className="text-red-600 mr-2">❌</span>
                     매핑되지 않은 필드 ({unmappedFields.length})
                   </h5>
                   <div className="space-y-3 max-h-96 overflow-y-auto">
                     {unmappedFields.map((field, index) => (
                       <div key={index} className="border rounded p-3 bg-red-50">
                         <div className="text-sm font-medium text-gray-900 mb-2">
                           원본: {field.field}
                         </div>
                         <div className="text-xs text-gray-600 mb-2">
                           사유: {field.reason}
                         </div>
                         {field.casNumber !== 'N/A' && (
                           <div className="text-xs text-gray-500 mb-1">
                             CAS: {field.casNumber} | 영문: {field.englishName}
                           </div>
                         )}
                         {field.unit !== 'N/A' && (
                           <div className="text-xs text-gray-500 mb-2">
                             단위: {field.unit} | MSDS: {field.msdsName}
                           </div>
                         )}
                         <div className="flex space-x-2">
                           <select
                             onChange={(e) => addMappingForUnmappedField(index, e.target.value)}
                             className="text-xs border rounded px-2 py-1 flex-1"
                             defaultValue=""
                           >
                             <option value="" disabled>매핑할 필드 선택</option>
                             <option value="GHG-CO2">GHG-CO2 (이산화탄소)</option>
                             <option value="GHG-N2O">GHG-N2O (아산화질소)</option>
                             <option value="GHG-HFCs">GHG-HFCs (수소불화탄소)</option>
                             <option value="GHG-SF6">GHG-SF6 (육불화황)</option>
                             <option value="GHG-NF3">GHG-NF3 (삼불화질소)</option>
                             <option value="ENERGY-CONSUMPTION">에너지 소비량</option>
                             <option value="WASTE-GENERATION">폐기물 발생량</option>
                             <option value="LABOR-HOURS">노동 시간</option>
                             <option value="SUPPLY-CHAIN">공급망 관리</option>
                             <option value="STD-VOC">STD-VOC (휘발성유기화합물)</option>
                             <option value="APE-VOC">APE-VOC (대기오염물질)</option>
                           </select>
                         </div>
                       </div>
                     ))}
                   </div>
                 </div>
               </div>

              <div className="flex justify-end mt-6 space-x-3">
                <button
                  onClick={closeMappingModal}
                  className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
                >
                  취소
                </button>
                <button
                  onClick={saveMapping}
                  className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                >
                  매핑 저장
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
