'use client';

import { useState, useCallback, useMemo, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { useRouter } from 'next/navigation';

// 인터페이스 정의
interface GreenhouseGasEmission {
  materialName: string;
  amount: string;
  unit: string;
}

interface RawMaterialSource {
  material: string;
  sourceType: string;
  address?: string;
  country?: string;
  countryOther?: string;
}

interface SubstanceData {
  productName: string;
  supplier: string;
  manufacturingDate: string;
  manufacturingNumber: string;
  safetyInformation: string;
  recycledMaterial: boolean;
  capacity: string;
  energyDensity: string;
  disposalMethod: string;
  recyclingMethod: string;
  manufacturingCountry: string;
  manufacturingCountryOther: string;
  productionPlant: string;
  rawMaterials: string[];
  rawMaterialsOther: string[];
  rawMaterialSources: RawMaterialSource[];
  greenhouseGasEmissions: GreenhouseGasEmission[];
  chemicalComposition: string;
}

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  uploadedAt: string;
  uploadedBy: string;
  file: File;
}

// 빈 물질 데이터 생성 함수
const createEmptySubstance = (): SubstanceData => ({
  productName: '',
  supplier: '',
  manufacturingDate: '',
  manufacturingNumber: '',
  safetyInformation: '',
  recycledMaterial: false,
  capacity: '',
  energyDensity: '',
  disposalMethod: '',
  recyclingMethod: '',
  manufacturingCountry: '',
  manufacturingCountryOther: '',
  productionPlant: '',
  rawMaterials: [],
  rawMaterialsOther: [],
  rawMaterialSources: [],
  greenhouseGasEmissions: [],
  chemicalComposition: ''
});

// 히스토리 관련 인터페이스
interface UploadHistoryItem {
  id: string;
  fileName: string;
  fileType: string;
  fileSize: number;
  uploadDate: string;
  uploadedBy: string;
  status: 'completed' | 'processing' | 'failed';
  substanceCount: number;
  processingTime: string;
  description?: string;
}

interface SubstanceDataHistory {
  id: string;
  productName: string;
  supplier: string;
  manufacturingDate: string;
  capacity: string;
  recycledMaterial: boolean;
  uploadDate: string;
  source: 'manual' | 'excel';
}

export default function PartnerDataUploadPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'upload' | 'history'>('upload');
  const [historySubTab, setHistorySubTab] = useState<'history' | 'substances' | 'analytics'>('history');
  const [uploadMode, setUploadMode] = useState<'direct' | 'excel'>('direct');
  const [substanceData, setSubstanceData] = useState<SubstanceData>(createEmptySubstance());
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [uploadHistory, setUploadHistory] = useState<UploadHistoryItem[]>([]);
  const [substanceHistory, setSubstanceHistory] = useState<SubstanceDataHistory[]>([]);
  const [selectedPeriod, setSelectedPeriod] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [showMappingModal, setShowMappingModal] = useState(false);
  const [selectedMappingData, setSelectedMappingData] = useState<any>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedDetailData, setSelectedDetailData] = useState<any>(null);
  
  // State for selected substances in history
  const [selectedSubstances, setSelectedSubstances] = useState<Set<string>>(new Set());
  
  const [partnerInfo] = useState({
     name: 'LG화학',
     companyId: 'LG001',
     status: 'active',
     lastSubmission: '2024-01-15',
     nextDeadline: '2024-02-15',
     userName: '담당자'
   });

  // 히스토리 mock 데이터 초기화
  useEffect(() => {
    const mockUploadHistory: UploadHistoryItem[] = [
      {
        id: '1',
        fileName: 'LG화학_물질데이터_2024_01.xlsx',
        fileType: 'Excel',
        fileSize: 2.4,
        uploadDate: '2024-01-15 14:30:00',
        uploadedBy: '김철수',
        status: 'completed',
        substanceCount: 45,
        processingTime: '2분 30초',
        description: 'LG화학 2024년 1분기 물질 데이터'
      },
      {
        id: '2',
        fileName: 'LG화학_ESG데이터_2024_01.csv',
        fileType: 'CSV',
        fileSize: 1.8,
        uploadDate: '2024-01-14 09:15:00',
        uploadedBy: '이영희',
        status: 'completed',
        substanceCount: 32,
        processingTime: '1분 45초',
        description: 'LG화학 ESG 데이터 업로드'
      },
      {
        id: '3',
        fileName: 'LG화학_물질리스트_2024_01.xlsx',
        fileType: 'Excel',
        fileSize: 3.2,
        uploadDate: '2024-01-13 16:20:00',
        uploadedBy: '박민수',
        status: 'processing',
        substanceCount: 35,
        processingTime: '매핑확정 필요',
        description: 'LG화학 물질 리스트 (매핑 검토 대기)'
      },
      {
        id: '4',
        fileName: '직접입력_NCM양극재_2024_01',
        fileType: 'Manual',
        fileSize: 0.1,
        uploadDate: '2024-01-12 11:45:00',
        uploadedBy: '최지영',
        status: 'processing',
        substanceCount: 1,
        processingTime: '매핑확정 필요',
        description: 'NCM 양극재 직접 입력 데이터'
      }
    ];

    const mockSubstanceHistory: SubstanceDataHistory[] = [
      {
        id: '1',
        productName: 'NCM 양극재',
        supplier: 'LG화학',
        manufacturingDate: '2024-01-15',
        capacity: '100Ah',
        recycledMaterial: true,
        uploadDate: '2024-01-15 14:30:00',
        source: 'excel'
      },
      {
        id: '2',
        productName: 'LiPF₆ 전해질',
        supplier: 'LG화학',
        manufacturingDate: '2024-01-15',
        capacity: '50L',
        recycledMaterial: false,
        uploadDate: '2024-01-15 14:30:00',
        source: 'excel'
      },
      {
        id: '3',
        productName: '흑연 음극재',
        supplier: '삼성전자',
        manufacturingDate: '2024-01-14',
        capacity: '80Ah',
        recycledMaterial: true,
        uploadDate: '2024-01-14 09:15:00',
        source: 'manual'
      },
      {
        id: '4',
        productName: '구리 호일',
        supplier: '현대자동차',
        manufacturingDate: '2024-01-13',
        capacity: '200m²',
        recycledMaterial: false,
        uploadDate: '2024-01-13 16:20:00',
        source: 'excel'
      }
    ];

    setUploadHistory(mockUploadHistory);
    setSubstanceHistory(mockSubstanceHistory);
  }, []);

  // 원재료 관련 함수들
  const handleRawMaterialChange = (material: string, checked: boolean) => {
    setSubstanceData(prev => {
      const updatedRawMaterials = checked
        ? [...prev.rawMaterials, material]
        : prev.rawMaterials.filter(m => m !== material);

      // 원재료 소스도 함께 관리
      let updatedSources = [...prev.rawMaterialSources];
      
      if (checked) {
        // 원재료가 추가되면 소스 정보도 추가
        updatedSources.push({
          material,
          sourceType: '',
          address: '',
          country: '',
          countryOther: ''
        });
        
        // "기타"가 처음 선택되면 빈 항목 추가
        if (material === '기타' && prev.rawMaterialsOther.length === 0) {
                      return { 
            ...prev,
            rawMaterials: updatedRawMaterials,
            rawMaterialsOther: [''],
            rawMaterialSources: updatedSources
          };
        }
            } else {
        // 원재료가 제거되면 소스 정보도 제거
        updatedSources = updatedSources.filter(source => source.material !== material);
        
        // "기타"가 해제되면 모든 "기타" 항목 제거
        if (material === '기타') {
              return { 
            ...prev,
            rawMaterials: updatedRawMaterials,
            rawMaterialsOther: [],
            rawMaterialSources: updatedSources
          };
        }
      }

      return {
        ...prev,
        rawMaterials: updatedRawMaterials,
        rawMaterialSources: updatedSources
      };
    });
  };

  const addOtherRawMaterial = () => {
    setSubstanceData(prev => ({
      ...prev,
      rawMaterialsOther: [...prev.rawMaterialsOther, '']
    }));
  };

  const removeOtherRawMaterial = (index: number) => {
    setSubstanceData(prev => ({
      ...prev,
      rawMaterialsOther: prev.rawMaterialsOther.filter((_, i) => i !== index)
    }));
  };

  const updateOtherRawMaterial = (index: number, value: string) => {
    setSubstanceData(prev => {
      const updatedOther = [...prev.rawMaterialsOther];
      updatedOther[index] = value;

      // 원재료 소스도 업데이트
      const materialName = `기타_${index}`;
      let updatedSources = [...prev.rawMaterialSources];
      
      const existingSourceIndex = updatedSources.findIndex(source => source.material === materialName);
      if (existingSourceIndex >= 0) {
        updatedSources[existingSourceIndex].material = materialName;
      } else if (value.trim()) {
        updatedSources.push({
          material: materialName,
          sourceType: '',
          address: '',
          country: '',
          countryOther: ''
        });
      }

      return {
        ...prev,
        rawMaterialsOther: updatedOther,
        rawMaterialSources: updatedSources
      };
    });
  };

  const getAllSelectedMaterials = () => {
    const predefined = substanceData.rawMaterials.filter(m => m !== '기타');
    const other = substanceData.rawMaterialsOther
      .map((material, index) => ({ name: material, key: `기타_${index}` }))
      .filter(item => item.name.trim());
    
    return [
      ...predefined.map(name => ({ name, key: name })),
      ...other
    ];
  };

  const updateMaterialSource = (material: string, field: string, value: string) => {
    setSubstanceData(prev => ({
      ...prev,
      rawMaterialSources: prev.rawMaterialSources.map(source =>
        source.material === material
          ? { ...source, [field]: value }
          : source
      )
    }));
  };

  // 온실가스 관련 함수들
  const addGreenhouseGas = () => {
    setSubstanceData(prev => ({
      ...prev,
      greenhouseGasEmissions: [
        ...prev.greenhouseGasEmissions,
        { materialName: '', amount: '', unit: 'tonCO2eq' }
      ]
    }));
  };

  const removeGreenhouseGas = (index: number) => {
    setSubstanceData(prev => ({
      ...prev,
      greenhouseGasEmissions: prev.greenhouseGasEmissions.filter((_, i) => i !== index)
    }));
  };

  const updateGreenhouseGas = (index: number, field: string, value: string) => {
    setSubstanceData(prev => ({
      ...prev,
      greenhouseGasEmissions: prev.greenhouseGasEmissions.map((item, i) =>
        i === index ? { ...item, [field]: value } : item
      )
    }));
  };

  // 폼 리셋
  const resetForm = () => {
    setSubstanceData(createEmptySubstance());
  };

  // 데이터 저장
  const saveData = () => {
    const finalManufacturingCountry = substanceData.manufacturingCountry === '기타' 
      ? substanceData.manufacturingCountryOther 
      : substanceData.manufacturingCountry;

    const allRawMaterials = [
      ...substanceData.rawMaterials.filter(m => m !== '기타'),
      ...substanceData.rawMaterialsOther.filter(m => m.trim())
    ];

    const processedSources = substanceData.rawMaterialSources.map(source => ({
      material: source.material.startsWith('기타_') 
        ? substanceData.rawMaterialsOther[parseInt(source.material.split('_')[1])] || source.material
        : source.material,
      sourceType: source.sourceType,
      location: source.sourceType === '국내 조달' 
        ? source.address 
        : source.country === '기타' 
          ? source.countryOther 
          : source.country
    }));

    const totalGreenhouseGasEmission = substanceData.greenhouseGasEmissions
      .reduce((total, emission) => total + (parseFloat(emission.amount) || 0), 0);

    const savedData = {
      ...substanceData,
      manufacturingCountry: finalManufacturingCountry,
      rawMaterials: allRawMaterials,
      rawMaterialSources: processedSources,
      totalGreenhouseGasEmission,
      savedAt: new Date().toISOString(),
      savedBy: partnerInfo.userName
    };

    console.log('저장된 데이터:', savedData);
    alert('데이터가 저장되었습니다!');
    resetForm();
  };

  // 파일 업로드 처리
  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      uploadedAt: new Date().toISOString(),
      uploadedBy: partnerInfo.userName,
      file: file
    }));

    setUploadedFiles(prev => [...prev, ...newFiles]);
  }, [partnerInfo.userName]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'text/csv': ['.csv']
    },
    multiple: true
  });

  // 히스토리 유틸리티 함수들
  const getFilteredHistory = () => {
    const now = new Date();
    const filtered = uploadHistory.filter(item => {
      const uploadDate = new Date(item.uploadDate);
      switch (selectedPeriod) {
        case 'today':
          return uploadDate.toDateString() === now.toDateString();
        case 'week':
          const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
          return uploadDate >= weekAgo;
        case 'month':
          const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
          return uploadDate >= monthAgo;
        default:
          return true;
      }
    });

    if (searchTerm) {
      return filtered.filter(item => 
        item.fileName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.uploadedBy.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    return filtered;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'processing':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return '완료';
      case 'processing':
        return '매핑확정 필요';
      case 'failed':
        return '실패';
      default:
        return '알 수 없음';
    }
  };

  const formatFileSize = (size: number) => {
    return `${size} MB`;
  };

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

  // 매핑 검토 열기
  const openMappingReview = (item: UploadHistoryItem) => {
    // 매핑 결과 mock 데이터
    const mockMappingData = {
      fileName: item.fileName,
      totalItems: item.substanceCount,
      mappedItems: [
        {
          id: 1,
          original: "GHG-CO2 (이산화탄소)",
          mapped: "ENERGY-CONSUMPTION",
          confidence: 95,
          status: "auto", // auto, review, manual
          type: "매핑된 필드"
        },
        {
          id: 2,
          original: "에너지소비량",
          mapped: "ENERGY-CONSUMPTION", 
          confidence: 87,
          status: "auto",
          type: "매핑된 필드"
        },
        {
          id: 3,
          original: "폐기물발생량",
          mapped: "WASTE-GENERATION",
          confidence: 92,
          status: "auto", 
          type: "매핑된 필드"
        },
        {
          id: 4,
          original: "유발화황",
          mapped: null,
          confidence: 50,
          status: "review",
          type: "검토가 필요한 필드"
        },
        {
          id: 5,
          original: "HFC-227ea",
          mapped: null,
          confidence: 72,
          status: "review",
          type: "검토가 필요한 필드"
        }
      ]
    };
    setSelectedMappingData(mockMappingData);
    setShowMappingModal(true);
  };

  // 상세보기 열기
  const openDetailView = (item: UploadHistoryItem) => {
    // 물질 상세정보 mock 데이터
    const mockDetailData = {
      fileName: item.fileName,
      fileType: item.fileType,
      uploadDate: item.uploadDate,
      uploadedBy: item.uploadedBy,
      substanceData: {
        productName: item.fileType === 'Manual' ? 'NCM 양극재' : 'LiPF₆ 전해질',
        supplier: '1차',
        manufacturingDate: '2024-01-15',
        manufacturingNumber: 'LG2024-001',
        safetyInformation: 'UN3481, Class 9, PG II',
        recycledMaterial: true,
        capacity: '100Ah',
        energyDensity: '250Wh/kg',
        disposalMethod: '전문 처리업체 위탁',
        recyclingMethod: 'Li 회수 후 재활용',
        manufacturingCountry: '한국',
        productionPlant: '청주공장',
        rawMaterials: ['리튬', '니켈', '코발트'],
        rawMaterialSources: [
          { material: '리튬', sourceType: '수입', country: '칠레' },
          { material: '니켈', sourceType: '국내 조달', address: '포항시 남구' },
          { material: '코발트', sourceType: '수입', country: '콩고' }
        ],
        greenhouseGasEmissions: [
          { materialName: 'CO₂', amount: '2.5', unit: 'tonCO2eq' },
          { materialName: 'CH₄', amount: '0.1', unit: 'tonCO2eq' }
        ],
        chemicalComposition: 'LiNi0.8Co0.15Al0.05O2 (NCM811) 95%, 바인더 3%, 도전재 2%'
      }
    };
    setSelectedDetailData(mockDetailData);
    setShowDetailModal(true);
  };

  // 매핑 결과 다운로드
  const downloadMappingResult = (item: UploadHistoryItem) => {
    // CSV 형태로 매핑 결과 다운로드
    const csvContent = [
      'Original Field,Mapped Field,Confidence,Status,CAS Number,Unit',
      'GHG-CO2 (이산화탄소),ENERGY-CONSUMPTION,95%,자동매핑,124-38-9,tonCO2eq',
      '에너지소비량,ENERGY-CONSUMPTION,87%,자동매핑,N/A,GJ',
      '폐기물발생량,WASTE-GENERATION,92%,자동매핑,N/A,ton',
      '유발화황,Sulfur hexafluoride,50%,수동검토,2551-62-4,tonCO2eq',
      'HFC-227ea,GHG-HFCs,72%,수동검토,431-89-0,tonCO2eq'
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `${item.fileName}_매핑결과.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // 매핑 저장
  const saveMappingResults = () => {
    alert('매핑이 저장되었습니다.');
    setShowMappingModal(false);
    setSelectedMappingData(null);
  };

  // Substance selection functions
  const toggleSelectSubstance = (substanceId: string) => {
    setSelectedSubstances(prev => {
      const newSet = new Set(prev);
      if (newSet.has(substanceId)) {
        newSet.delete(substanceId);
      } else {
        newSet.add(substanceId);
      }
      return newSet;
    });
  };

  const selectAllSubstances = () => {
    setSelectedSubstances(new Set(substanceHistory.map(substance => substance.id)));
  };

  const deselectAllSubstances = () => {
    setSelectedSubstances(new Set());
  };

  const deleteSelectedSubstances = () => {
    if (selectedSubstances.size === 0) {
      alert('삭제할 항목을 선택해주세요.');
      return;
    }
    
    if (confirm(`선택한 ${selectedSubstances.size}개 항목을 삭제하시겠습니까?`)) {
      setSubstanceHistory(prev => prev.filter(substance => !selectedSubstances.has(substance.id)));
      setSelectedSubstances(new Set());
      alert('선택한 항목이 삭제되었습니다.');
    }
  };

  // 자동 매핑 시작
  const startAutoMapping = () => {
    if (uploadMode === 'direct') {
      if (!substanceData.productName) {
        alert('최소한 제품명은 입력해주세요.');
        return;
      }
      console.log('직접 입력 데이터 처리:', substanceData);
    } else {
      if (uploadedFiles.length === 0) {
        alert('업로드할 파일을 선택해주세요.');
        return;
      }
      console.log('엑셀 파일 처리:', uploadedFiles);
    }
    
    alert('데이터 업로드 및 자동 매핑을 시작합니다.');
    setActiveTab('history');  // 같은 페이지 내에서 히스토리 탭으로 전환
  };

  const predefinedMaterials = ['리튬', '니켈', '코발트', '망간', '알루미늄', '흑연', '형석', '기타'];
  const countries = ['한국', '중국', '일본', '미국', '독일', '프랑스', '영국', '이탈리아', '스페인', '네덜란드', '벨기에', '스위스', '오스트리아', '기타'];
  const importCountries = countries.filter(country => country !== '한국');

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
                <span className="font-medium">{partnerInfo.name}</span> • {partnerInfo.userName}
               </div>
            </div>
          </div>
        </div>
      </header>

            {/* 탭 네비게이션 - 가로로 넓은 디자인 */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-center py-6">
            <div className="flex w-full max-w-6xl bg-gray-50 rounded-2xl p-2 shadow-inner">
            {[
                { id: "upload", name: "데이터 업로드", icon: "📤", gradient: "from-blue-500 to-blue-600", desc: "물질 데이터를 직접 입력하거나 엑셀로 업로드" },
                { id: "history", name: "데이터 히스토리", icon: "📊", gradient: "from-indigo-500 to-indigo-600", desc: "업로드된 데이터 관리 및 분석 결과 확인" }
            ].map((tab) => (
              <button
                key={tab.id}
                  onClick={() => setActiveTab(tab.id as 'upload' | 'history')}
                  className={`w-1/2 flex items-center gap-5 p-6 rounded-xl font-semibold transition-all duration-300 ease-in-out transform ${
                  activeTab === tab.id
                      ? `bg-gradient-to-r ${tab.gradient} text-white shadow-lg scale-105`
                      : "text-gray-600 hover:text-gray-800 hover:bg-white/70 hover:shadow-md"
                  }`}
                >
                  <div className={`w-14 h-14 rounded-full flex items-center justify-center text-2xl transition-all duration-300 flex-shrink-0 ${
                    activeTab === tab.id 
                      ? 'bg-white/20 backdrop-blur-sm shadow-lg' 
                      : 'bg-gray-200'
                  }`}>
                    {tab.icon}
                  </div>
                  <div className="flex-1 text-left">
                    <div className="text-lg font-bold mb-1">{tab.name}</div>
                    <div className={`text-sm opacity-80 leading-relaxed ${
                      activeTab === tab.id ? 'text-white/90' : 'text-gray-500'
                    }`}>
                      {tab.desc}
                    </div>
                  </div>
                  {activeTab === tab.id && (
                    <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-white/10 to-transparent animate-pulse"></div>
                  )}
              </button>
            ))}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {activeTab === 'upload' && (
          <div className="space-y-6">
          {/* 업로드 방식 선택 */}
            <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">데이터 업로드 방식 선택</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <button
                onClick={() => setUploadMode('direct')}
                className={`p-4 border-2 rounded-lg text-left transition-colors ${
                  uploadMode === 'direct'
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <div className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                    uploadMode === 'direct' ? 'border-blue-500' : 'border-gray-300'
                  }`}>
                    {uploadMode === 'direct' && <div className="w-2 h-2 bg-blue-500 rounded-full"></div>}
                  </div>
                  <div>
                    <h4 className="font-medium">📝 물질 데이터 직접 입력</h4>
                    <p className="text-sm text-gray-500">폼을 통해 직접 데이터를 입력합니다</p>
                  </div>
                </div>
              </button>
              <button
                onClick={() => setUploadMode('excel')}
                className={`p-4 border-2 rounded-lg text-left transition-colors ${
                  uploadMode === 'excel'
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <div className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                    uploadMode === 'excel' ? 'border-blue-500' : 'border-gray-300'
                  }`}>
                    {uploadMode === 'excel' && <div className="w-2 h-2 bg-blue-500 rounded-full"></div>}
              </div>
                  <div>
                    <h4 className="font-medium">📊 엑셀 파일 업로드</h4>
                    <p className="text-sm text-gray-500">엑셀 파일을 업로드하여 일괄 처리합니다</p>
            </div>
                      </div>
              </button>
              </div>
            </div>

          {/* 선택된 모드에 따른 콘텐츠 */}
          {uploadMode === 'direct' && (
            <div className="space-y-8">
              {/* 기본 정보 섹션 */}
              <div className="border rounded-lg p-6 bg-gray-50">
                <h4 className="text-md font-semibold text-gray-800 mb-4 border-b border-gray-300 pb-2">
                  기본 정보
                </h4>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">제품명</label>
                    <input
                      type="text"
                      value={substanceData.productName}
                      onChange={(e) => setSubstanceData(prev => ({ ...prev, productName: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="제품명을 입력하세요"
                    />
                      </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">납품처</label>
                    <select
                      value={substanceData.supplier}
                      onChange={(e) => setSubstanceData(prev => ({ ...prev, supplier: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="">납품처를 선택하세요</option>
                      <option value="원청">원청</option>
                      {[...Array(10)].map((_, i) => (
                        <option key={i} value={`${i + 1}차`}>{i + 1}차</option>
                      ))}
                    </select>
                    </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">제조일</label>
                    <input
                      type="date"
                      value={substanceData.manufacturingDate}
                      onChange={(e) => setSubstanceData(prev => ({ ...prev, manufacturingDate: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                    </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">제조 번호</label>
                    <input
                      type="text"
                      value={substanceData.manufacturingNumber}
                      onChange={(e) => setSubstanceData(prev => ({ ...prev, manufacturingNumber: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="제조 번호를 입력하세요"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">안전 인증 정보</label>
                    <input
                      type="text"
                      value={substanceData.safetyInformation}
                      onChange={(e) => setSubstanceData(prev => ({ ...prev, safetyInformation: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="안전 인증 정보를 입력하세요"
                    />
                </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">재활용 자재 사용 여부</label>
                    <select
                      value={substanceData.recycledMaterial ? 'true' : 'false'}
                      onChange={(e) => setSubstanceData(prev => ({ ...prev, recycledMaterial: e.target.value === 'true' }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="false">아니오</option>
                      <option value="true">예</option>
                    </select>
              </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">용량 (Ah, Wh)</label>
                    <input
                      type="text"
                      value={substanceData.capacity}
                      onChange={(e) => setSubstanceData(prev => ({ ...prev, capacity: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="용량을 입력하세요"
                    />
                      </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">에너지밀도</label>
                    <input
                      type="text"
                      value={substanceData.energyDensity}
                      onChange={(e) => setSubstanceData(prev => ({ ...prev, energyDensity: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="에너지밀도를 입력하세요"
                    />
                    </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">폐기 방법 및 인증</label>
                    <input
                      type="text"
                      value={substanceData.disposalMethod}
                      onChange={(e) => setSubstanceData(prev => ({ ...prev, disposalMethod: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="폐기 방법 및 인증을 입력하세요"
                    />
                    </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">재활용 방법 및 인증</label>
                    <input
                      type="text"
                      value={substanceData.recyclingMethod}
                      onChange={(e) => setSubstanceData(prev => ({ ...prev, recyclingMethod: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="재활용 방법 및 인증을 입력하세요"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">제조국</label>
                    <select
                      value={substanceData.manufacturingCountry}
                      onChange={(e) => {
                        setSubstanceData(prev => ({ 
                          ...prev, 
                          manufacturingCountry: e.target.value,
                          manufacturingCountryOther: e.target.value !== '기타' ? '' : prev.manufacturingCountryOther
                        }));
                      }}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="">제조국을 선택하세요</option>
                      {countries.map(country => (
                        <option key={country} value={country}>{country}</option>
                      ))}
                    </select>
                    {substanceData.manufacturingCountry === '기타' && (
                      <input
                        type="text"
                        value={substanceData.manufacturingCountryOther}
                        onChange={(e) => setSubstanceData(prev => ({ ...prev, manufacturingCountryOther: e.target.value }))}
                        className="mt-2 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        placeholder="기타 제조국을 입력하세요"
                      />
                    )}
                </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">생산공장 위치</label>
                    <input
                      type="text"
                      value={substanceData.productionPlant}
                      onChange={(e) => setSubstanceData(prev => ({ ...prev, productionPlant: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="생산공장 위치를 입력하세요"
                    />
              </div>
                      </div>
                    </div>

              {/* 원재료 정보 섹션 */}
              <div className="border rounded-lg p-6 bg-gray-50">
                <h4 className="text-md font-semibold text-gray-800 mb-4 border-b border-gray-300 pb-2">
                  원재료 정보
                </h4>
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">주요 원재료 사용 여부</label>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {predefinedMaterials.map(material => (
                        <label key={material} className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            checked={substanceData.rawMaterials.includes(material)}
                            onChange={(e) => handleRawMaterialChange(material, e.target.checked)}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                          />
                          <span className="text-sm text-gray-700">{material}</span>
                        </label>
                      ))}
                    </div>
                    
                    {/* 기타 원재료 동적 입력 */}
                    {substanceData.rawMaterials.includes('기타') && (
                      <div className="mt-4 space-y-2">
                        <label className="block text-sm font-medium text-gray-700">기타 원재료</label>
                        {substanceData.rawMaterialsOther.map((material, index) => (
                          <div key={index} className="flex items-center space-x-2">
                            <input
                              type="text"
                              value={material}
                              onChange={(e) => updateOtherRawMaterial(index, e.target.value)}
                              className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                              placeholder="기타 원재료를 입력하세요"
                            />
                            <button
                              onClick={() => removeOtherRawMaterial(index)}
                              className="px-3 py-2 text-red-600 hover:text-red-800 border border-red-300 rounded-md hover:bg-red-50"
                            >
                              삭제
                            </button>
                  </div>
                        ))}
                        <button
                          onClick={addOtherRawMaterial}
                          className="px-4 py-2 text-blue-600 hover:text-blue-800 border border-blue-300 rounded-md hover:bg-blue-50"
                        >
                          + 추가
                        </button>
                </div>
                    )}
              </div>

                  <div className="border-t border-gray-300 pt-6">
                    <label className="block text-sm font-medium text-gray-700 mb-4">원재료별 출처 정보</label>
                    <div className="space-y-4">
                      {getAllSelectedMaterials().map((material, index) => (
                        <div key={material.key} className="border border-gray-200 rounded-lg p-4 bg-white">
                          <h5 className="font-medium text-gray-800 mb-3">{material.name}</h5>
                          <div className="space-y-3">
                            <div className="flex space-x-4">
                              <label className="flex items-center">
                                <input
                                  type="radio"
                                  name={`sourceType-${material.key.replace(/[^a-zA-Z0-9가-힣]/g, '')}-${index}`}
                                  value="국내 조달"
                                  checked={substanceData.rawMaterialSources.find(s => s.material === material.key)?.sourceType === '국내 조달'}
                                  onChange={(e) => updateMaterialSource(material.key, 'sourceType', e.target.value)}
                                  className="mr-2"
                                />
                                국내 조달
                              </label>
                              <label className="flex items-center">
                                <input
                                  type="radio"
                                  name={`sourceType-${material.key.replace(/[^a-zA-Z0-9가-힣]/g, '')}-${index}`}
                                  value="수입"
                                  checked={substanceData.rawMaterialSources.find(s => s.material === material.key)?.sourceType === '수입'}
                                  onChange={(e) => updateMaterialSource(material.key, 'sourceType', e.target.value)}
                                  className="mr-2"
                                />
                                수입
                              </label>
                      </div>

                            {substanceData.rawMaterialSources.find(s => s.material === material.key)?.sourceType === '국내 조달' && (
                              <input
                                type="text"
                                value={substanceData.rawMaterialSources.find(s => s.material === material.key)?.address || ''}
                                onChange={(e) => updateMaterialSource(material.key, 'address', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                placeholder="주소를 입력하세요"
                              />
                            )}
                            
                            {substanceData.rawMaterialSources.find(s => s.material === material.key)?.sourceType === '수입' && (
                              <div className="space-y-2">
                                <select
                                  value={substanceData.rawMaterialSources.find(s => s.material === material.key)?.country || ''}
                                  onChange={(e) => {
                                    updateMaterialSource(material.key, 'country', e.target.value);
                                    if (e.target.value !== '기타') {
                                      updateMaterialSource(material.key, 'countryOther', '');
                                    }
                                  }}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                >
                                  <option value="">수입국을 선택하세요</option>
                                  {importCountries.map(country => (
                                    <option key={country} value={country}>{country}</option>
                                  ))}
                                </select>
                                {substanceData.rawMaterialSources.find(s => s.material === material.key)?.country === '기타' && (
                                  <input
                                    type="text"
                                    value={substanceData.rawMaterialSources.find(s => s.material === material.key)?.countryOther || ''}
                                    onChange={(e) => updateMaterialSource(material.key, 'countryOther', e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                    placeholder="기타 수입국을 입력하세요"
                                  />
                                )}
                    </div>
                            )}
                    </div>
                    </div>
                      ))}
                  </div>
                </div>
              </div>
            </div>

              {/* 온실가스 배출량 섹션 */}
              <div className="border rounded-lg p-6 bg-gray-50">
                <h4 className="text-md font-semibold text-gray-800 mb-4 border-b border-gray-300 pb-2">
                  온실가스 배출량
                </h4>
                <div className="space-y-4">
                  <p className="text-sm text-gray-600">
                    제품을 생산할때 발생하는 온실가스 (CH4, CO₂, HFCs, N₂O, NF3, PFCs, SF₆)를 tonCO2eq 기준 단위로 입력하세요
                  </p>
                  
                  {substanceData.greenhouseGasEmissions.map((emission, index) => (
                    <div key={index} className="flex items-center space-x-4 p-4 border border-gray-200 rounded-lg bg-white">
                      <div className="flex-1">
                        <input
                          type="text"
                          value={emission.materialName}
                          onChange={(e) => updateGreenhouseGas(index, 'materialName', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          placeholder="물질명을 입력하세요"
                        />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <input
                            type="number"
                            value={emission.amount}
                            onChange={(e) => updateGreenhouseGas(index, 'amount', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                            placeholder="사용량"
                          />
                          <span className="text-sm text-gray-500 whitespace-nowrap">tonCO2eq</span>
                        </div>
                      </div>
                        <button
                        onClick={() => removeGreenhouseGas(index)}
                        className="px-3 py-2 text-red-600 hover:text-red-800 border border-red-300 rounded-md hover:bg-red-50"
                        >
                        삭제
                        </button>
                    </div>
                  ))}
                  
                      <button
                    onClick={addGreenhouseGas}
                    className="px-4 py-2 text-blue-600 hover:text-blue-800 border border-blue-300 rounded-md hover:bg-blue-50"
                      >
                    + 추가
                      </button>
                    </div>
                  </div>

              {/* 화학물질 구성 비율 섹션 */}
              <div className="border rounded-lg p-6 bg-gray-50">
                <h4 className="text-md font-semibold text-gray-800 mb-4 border-b border-gray-300 pb-2">
                  화학물질 구성 비율
                </h4>
                <textarea
                  value={substanceData.chemicalComposition}
                  onChange={(e) => setSubstanceData(prev => ({ ...prev, chemicalComposition: e.target.value }))}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="화학물질 구성 비율을 입력하세요"
                />
              </div>



              {/* 입력된 데이터 미리보기 */}
              {substanceData.productName && (
                <div className="bg-white shadow rounded-lg p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">입력된 데이터 미리보기</h3>
                  
                                     <div className="overflow-x-auto">
                     <table className="min-w-full divide-y divide-gray-200">
                       <thead className="bg-gray-50">
                         <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">항목</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">내용</th>
                         </tr>
                       </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        <tr>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">제품명</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{substanceData.productName}</td>
                        </tr>
                        <tr>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">납품처</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{substanceData.supplier}</td>
                        </tr>
                        <tr>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">제조일</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{substanceData.manufacturingDate}</td>
                        </tr>
                        <tr>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">제조 번호</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{substanceData.manufacturingNumber}</td>
                        </tr>
                        <tr>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">안전 인증 정보</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{substanceData.safetyInformation}</td>
                        </tr>
                        <tr>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">재활용 자재 사용</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            <span className={`inline-block px-2 py-1 text-xs rounded-full ${
                              substanceData.recycledMaterial 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-gray-100 text-gray-800'
                            }`}>
                              {substanceData.recycledMaterial ? '예' : '아니오'}
                            </span>
                             </td>
                        </tr>
                        <tr>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">주요 원재료</td>
                          <td className="px-6 py-4 text-sm text-gray-900">
                            <div className="flex flex-wrap gap-1">
                              {substanceData.rawMaterials.filter(m => m !== '기타').map(material => (
                                <span key={material} className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                                  {material}
                                </span>
                              ))}
                              {substanceData.rawMaterialsOther.filter(m => m.trim()).map((material, index) => (
                                <span key={index} className="inline-block bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                                  {material}
                                </span>
                              ))}
                               </div>
                             </td>
                        </tr>
                        <tr>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">원재료 출처</td>
                          <td className="px-6 py-4 text-sm text-gray-900">
                            <div className="space-y-1">
                              {substanceData.rawMaterialSources.filter(source => source.sourceType).map((source, index) => {
                                const materialName = source.material.startsWith('기타_') 
                                  ? substanceData.rawMaterialsOther[parseInt(source.material.split('_')[1])] || source.material
                                  : source.material;
                                const sourceInfo = source.sourceType === '국내 조달' 
                                  ? source.address 
                                  : source.country === '기타' 
                                    ? source.countryOther 
                                    : source.country;
                                
                                return (
                                  <div key={index} className="flex items-center space-x-2">
                                    <span className="font-medium">{materialName}:</span>
                                    <span className={`inline-block px-2 py-1 text-xs rounded-full ${
                                      source.sourceType === '국내 조달' 
                                        ? 'bg-blue-100 text-blue-800' 
                                        : 'bg-orange-100 text-orange-800'
                                    }`}>
                                      {source.sourceType}
                                </span>
                                    <span className="text-gray-600">({sourceInfo})</span>
                                  </div>
                                );
                              })}
                                </div>
                              </td>
                           </tr>
                      </tbody>
                    </table>
                </div>
              </div>
            )}

              {/* 자동 매핑 시작 버튼 */}
              <div className="text-center">
                                     <button
                  onClick={startAutoMapping}
                  className="px-8 py-4 bg-blue-600 text-white text-lg font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
                                     >
                  🤖 자동 매핑 시작
                                     </button>
              </div>
          </div>
        )}

          {/* 엑셀 파일 업로드 모드 */}
          {uploadMode === 'excel' && (
          <div className="space-y-6">
              {/* 엑셀 파일 업로드 */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">엑셀 파일 업로드</h3>
                
                <div
                  {...getRootProps()}
                  className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                    isDragActive
                      ? 'border-green-400 bg-green-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                >
                  <input {...getInputProps()} />
                  <div className="space-y-4">
                    <div className="text-6xl">📊</div>
                    <div>
                      <h4 className="text-lg font-medium text-gray-900 mb-2">
                        {isDragActive ? '파일을 여기에 놓으세요' : '엑셀 파일을 드래그하거나 클릭하여 업로드'}
                      </h4>
                      <p className="text-sm text-gray-600">
                        .xlsx, .xls, .csv 파일을 지원합니다 (최대 10MB)
                      </p>
                                 </div>
                  </div>
                </div>
              </div>

              {/* 업로드된 파일 목록 */}
              {uploadedFiles.length > 0 && (
                <div className="space-y-6">
                  {/* 입력 현황 */}
                  <div className="bg-white shadow rounded-lg p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">입력 현황</h3>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      <div className="text-center p-4 bg-blue-50 rounded-lg">
                        <div className="text-2xl font-bold text-blue-600">
                          {uploadedFiles.length}개
                      </div>
                        <div className="text-sm text-blue-600">업로드 파일</div>
                    </div>
                      <div className="text-center p-4 bg-green-50 rounded-lg">
                        <div className="text-2xl font-bold text-green-600">1개</div>
                        <div className="text-sm text-green-600">업로드 완료</div>
                    </div>
                      <div className="text-center p-4 bg-gray-50 rounded-lg">
                        <div className="text-2xl font-bold text-gray-600">
                          {(uploadedFiles.reduce((total, file) => total + file.size, 0) / (1024 * 1024)).toFixed(1)}MB
                        </div>
                        <div className="text-sm text-gray-600">총 용량</div>
                  </div>
                </div>
              </div>

                  {/* 업로드된 파일 목록 */}
                  <div className="bg-white shadow rounded-lg p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">업로드된 파일 ({uploadedFiles.length}개)</h3>
                    <div className="space-y-3">
                      {uploadedFiles.map((file) => (
                        <div key={file.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                          <div className="flex items-center space-x-3">
                            <span className="text-3xl">📊</span>
                            <div>
                              <div className="text-sm font-medium text-gray-900">{file.name}</div>
                              <div className="text-xs text-gray-500">
                                {(file.size / 1024 / 1024).toFixed(2)} MB • {new Date(file.uploadedAt).toLocaleString()}
                      </div>
                    </div>
                    </div>
                          <span className="text-xs text-green-600 bg-green-100 px-3 py-1 rounded-full">
                            업로드 완료
                          </span>
                  </div>
                      ))}
                  </div>
              </div>
                </div>
              )}

              {/* 자동 매핑 시작 버튼 */}
              <div className="text-center">
                <button
                  onClick={startAutoMapping}
                  className="px-8 py-4 bg-blue-600 text-white text-lg font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
                >
                  🤖 자동 매핑 시작
                </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* 히스토리 탭 콘텐츠 */}
        {activeTab === 'history' && (
          <div className="space-y-6">
            {/* 히스토리 서브 탭 - 가로로 넓은 디자인 */}
            <div className="bg-white shadow-lg rounded-2xl overflow-hidden">
              <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4">
                <div className="flex justify-center">
                  <div className="flex w-full max-w-6xl bg-white rounded-xl p-2 shadow-md">
                    {[
                      { id: "history", name: "업로드 히스토리", icon: "📁", color: "blue", desc: "파일 업로드 현황 및 처리 상태" },
                      { id: "substances", name: "물질 데이터", icon: "🧪", color: "indigo", desc: "등록된 물질 정보 관리" },
                      { id: "analytics", name: "분석 통계", icon: "📊", color: "purple", desc: "데이터 분석 및 통계 리포트" },
                    ].map((tab) => (
                      <button
                        key={tab.id}
                        onClick={() => setHistorySubTab(tab.id as 'history' | 'substances' | 'analytics')}
                        className={`flex-1 flex items-center gap-4 px-5 py-4 rounded-lg font-medium transition-all duration-200 ${
                          historySubTab === tab.id
                            ? (tab.color === 'blue' ? 'bg-blue-500 text-white shadow-lg' :
                               tab.color === 'indigo' ? 'bg-indigo-500 text-white shadow-lg' :
                               'bg-purple-500 text-white shadow-lg')
                            : "text-gray-600 hover:text-gray-800 hover:bg-gray-50"
                        }`}
                      >
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg transition-all duration-200 flex-shrink-0 ${
                          historySubTab === tab.id 
                            ? 'bg-white/20 shadow-lg' 
                            : 'bg-gray-100'
                        }`}>
                          {tab.icon}
                        </div>
                        <div className="flex-1 text-left">
                          <div className="font-semibold text-sm mb-1">{tab.name}</div>
                          <div className={`text-xs opacity-75 leading-relaxed ${
                            historySubTab === tab.id ? 'text-white/80' : 'text-gray-500'
                          }`}>
                            {tab.desc}
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* 업로드 히스토리 서브탭 */}
              {historySubTab === "history" && (
                <div className="p-6">
                  <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold text-gray-900">업로드 히스토리</h2>
                    <div className="flex items-center space-x-4">
                      {/* Search */}
                      <div className="relative">
                        <input
                          type="text"
                          placeholder="파일명, 업로드자 검색..."
                          value={searchTerm}
                          onChange={(e) => setSearchTerm(e.target.value)}
                          className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <svg className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                      </div>

                      {/* Period filter */}
                      <select
                        value={selectedPeriod}
                        onChange={(e) => setSelectedPeriod(e.target.value)}
                        className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="all">전체 기간</option>
                        <option value="today">오늘</option>
                        <option value="week">최근 7일</option>
                        <option value="month">최근 30일</option>
                      </select>
                    </div>
                  </div>

                  {/* Statistics */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-blue-50 rounded-lg p-4">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                            <span className="text-blue-600 text-lg">📁</span>
                      </div>
                    </div>
                        <div className="ml-4">
                          <p className="text-sm font-medium text-gray-600">총 업로드</p>
                          <p className="text-2xl font-bold text-gray-900">{getFilteredHistory().length}</p>
                  </div>
                </div>
              </div>

                    <div className="bg-green-50 rounded-lg p-4">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                        <span className="text-green-600 text-lg">✅</span>
                      </div>
                    </div>
                        <div className="ml-4">
                          <p className="text-sm font-medium text-gray-600">성공</p>
                          <p className="text-2xl font-bold text-gray-900">
                            {getFilteredHistory().filter(item => item.status === 'completed').length}
                          </p>
                  </div>
                </div>
              </div>

                    <div className="bg-yellow-50 rounded-lg p-4">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
                            <span className="text-yellow-600 text-lg">⏳</span>
                      </div>
                    </div>
                        <div className="ml-4">
                          <p className="text-sm font-medium text-gray-600">처리중</p>
                          <p className="text-2xl font-bold text-gray-900">
                            {getFilteredHistory().filter(item => item.status === 'processing').length}
                          </p>
                  </div>
                </div>
              </div>

                    <div className="bg-red-50 rounded-lg p-4">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                          <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
                            <span className="text-red-600 text-lg">❌</span>
                      </div>
                    </div>
                        <div className="ml-4">
                          <p className="text-sm font-medium text-gray-600">실패</p>
                          <p className="text-2xl font-bold text-gray-900">
                            {getFilteredHistory().filter(item => item.status === 'failed').length}
                </p>
                    </div>
                  </div>
                </div>
              </div>

                  {/* Upload History Table */}
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">파일 정보</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">업로드 정보</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">처리 결과</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">상태</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">작업</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {getFilteredHistory().map((item) => (
                          <tr key={item.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center">
                                                                <div className="flex-shrink-0 h-10 w-10">
                                  {item.fileType === 'Excel' ? (
                                    <span className="text-green-600 text-2xl">📊</span>
                                  ) : item.fileType === 'CSV' ? (
                                    <span className="text-blue-600 text-2xl">📄</span>
                                  ) : item.fileType === 'Manual' ? (
                                    <span className="text-purple-600 text-2xl">✏️</span>
                                  ) : (
                                    <span className="text-gray-600 text-2xl">📁</span>
                                  )}
                      </div>
                                <div className="ml-4">
                                  <div className="text-sm font-medium text-gray-900">{item.fileName}</div>
                                  <div className="text-sm text-gray-500">
                                    {item.fileType} • {formatFileSize(item.fileSize)}
                      </div>
                                  {item.description && (
                                    <div className="text-xs text-gray-400 mt-1">{item.description}</div>
                                  )}
                      </div>
                    </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-900">{item.uploadedBy}</div>
                              <div className="text-sm text-gray-500">{formatDate(item.uploadDate)}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-900">
                                {item.substanceCount > 0 ? `${item.substanceCount}개 물질` : '-'}
        </div>
                              <div className="text-sm text-gray-500">{item.processingTime}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(item.status)}`}>
                                {getStatusText(item.status)}
                              </span>
                            </td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                              <div className="flex space-x-2">
                                <button 
                                  onClick={() => openDetailView(item)}
                                  className="text-blue-600 hover:text-blue-900"
                                >
                                  상세보기
                                </button>
                                {item.status === 'completed' && (
                                  <button 
                                    onClick={() => downloadMappingResult(item)}
                                    className="text-green-600 hover:text-green-900"
                                  >
                                    다운로드
                                  </button>
                                )}
                                {item.status === 'processing' && (
                                  <button 
                                    onClick={() => openMappingReview(item)}
                                    className="text-orange-600 hover:text-orange-900"
                                  >
                                    매핑검토
                                  </button>
                                )}
                                {item.status === 'failed' && (
                                  <button className="text-red-600 hover:text-red-900">재시도</button>
                                )}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
            </div>

                  {getFilteredHistory().length === 0 && (
                    <div className="text-center py-8">
                      <div className="text-4xl mb-4">📁</div>
                      <p className="text-gray-500">업로드 히스토리가 없습니다.</p>
                      </div>
                  )}
                      </div>
              )}

              {/* 물질 데이터 서브탭 */}
              {historySubTab === "substances" && (
                <div className="p-6">
                  <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold text-gray-900">물질 데이터 히스토리</h2>
                    
                    {/* 선택된 항목 삭제 버튼 */}
                    {selectedSubstances.size > 0 && (
                      <div className="flex items-center space-x-4">
                        <span className="text-sm text-gray-600">
                          {selectedSubstances.size}개 항목 선택됨
                        </span>
                        <button
                          onClick={deleteSelectedSubstances}
                          className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                          <span>선택한 물질 삭제</span>
                        </button>
                      </div>
                    )}
                    </div>
                  
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            <input
                              type="checkbox"
                              checked={selectedSubstances.size === substanceHistory.length && substanceHistory.length > 0}
                              onChange={(e) => e.target.checked ? selectAllSubstances() : deselectAllSubstances()}
                              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                            />
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">제품명</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">납품처</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">제조일</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">용량</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">재활용</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">입력 방식</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">업로드일</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {substanceHistory.map((substance) => (
                          <tr key={substance.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <input
                                type="checkbox"
                                checked={selectedSubstances.has(substance.id)}
                                onChange={() => toggleSelectSubstance(substance.id)}
                                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                              />
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {substance.productName}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {substance.supplier}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {substance.manufacturingDate}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {substance.capacity}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                substance.recycledMaterial 
                                  ? 'bg-green-100 text-green-800' 
                                  : 'bg-gray-100 text-gray-800'
                              }`}>
                                {substance.recycledMaterial ? '예' : '아니오'}
                             </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                substance.source === 'manual' 
                                  ? 'bg-blue-100 text-blue-800' 
                                  : 'bg-purple-100 text-purple-800'
                              }`}>
                                {substance.source === 'manual' ? '직접 입력' : '엑셀 업로드'}
                               </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {formatDate(substance.uploadDate)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* 분석 통계 서브탭 */}
              {historySubTab === "analytics" && (
                <div className="p-6">
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">분석 통계</h2>
                  
                  {/* 월별 업로드 통계 */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">월별 업로드 현황</h3>
                      <div className="space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">1월</span>
                          <div className="flex items-center space-x-2">
                            <div className="w-20 bg-gray-200 rounded-full h-2">
                              <div className="bg-blue-600 h-2 rounded-full" style={{ width: '80%' }}></div>
                      </div>
                            <span className="text-sm font-medium">4건</span>
                      </div>
                      </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">12월</span>
                          <div className="flex items-center space-x-2">
                            <div className="w-20 bg-gray-200 rounded-full h-2">
                              <div className="bg-blue-600 h-2 rounded-full" style={{ width: '60%' }}></div>
                             </div>
                            <span className="text-sm font-medium">3건</span>
                           </div>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">11월</span>
                           <div className="flex items-center space-x-2">
                            <div className="w-20 bg-gray-200 rounded-full h-2">
                              <div className="bg-blue-600 h-2 rounded-full" style={{ width: '40%' }}></div>
                           </div>
                            <span className="text-sm font-medium">2건</span>
                         </div>
                      </div>
                    </div>
                  </div>

                    <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">파일 유형별 분포</h3>
                      <div className="space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Excel 파일</span>
                          <div className="flex items-center space-x-2">
                            <div className="w-20 bg-gray-200 rounded-full h-2">
                              <div className="bg-green-600 h-2 rounded-full" style={{ width: '75%' }}></div>
                      </div>
                            <span className="text-sm font-medium">75%</span>
                      </div>
                      </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">CSV 파일</span>
                          <div className="flex items-center space-x-2">
                            <div className="w-20 bg-gray-200 rounded-full h-2">
                              <div className="bg-green-600 h-2 rounded-full" style={{ width: '25%' }}></div>
                    </div>
                            <span className="text-sm font-medium">25%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

                  {/* 처리 성공률 */}
                  <div className="bg-white border rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">처리 성공률</h3>
                    <div className="flex items-center justify-center">
                      <div className="relative w-32 h-32">
                        <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 36 36">
                          <path
                            d="M18 2.0845
                              a 15.9155 15.9155 0 0 1 0 31.831
                              a 15.9155 15.9155 0 0 1 0 -31.831"
                            fill="none"
                            stroke="#e5e7eb"
                            strokeWidth="3"
                          />
                          <path
                            d="M18 2.0845
                              a 15.9155 15.9155 0 0 1 0 31.831
                              a 15.9155 15.9155 0 0 1 0 -31.831"
                            fill="none"
                            stroke="#10b981"
                            strokeWidth="3"
                            strokeDasharray="75, 100"
                          />
                        </svg>
                        <div className="absolute inset-0 flex items-center justify-center">
                          <span className="text-2xl font-bold text-gray-900">75%</span>
              </div>
            </div>
                    </div>
                    <p className="text-center text-gray-600 mt-4">
                      총 4건 중 3건 성공 (1건 처리중)
                    </p>
          </div>
        </div>
      )}
            </div>
          </div>
        )}
      </main>

      {/* 매핑 검토 모달 */}
      {showMappingModal && selectedMappingData && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">
                  입력 후 매핑 → 신뢰도 표시, 사용자 수정 거쳐서 DB 저장
                </h2>
                <button
                  onClick={() => setShowMappingModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">파일: {selectedMappingData.fileName}</h3>
                <p className="text-gray-600">총 {selectedMappingData.totalItems}개 항목</p>
              </div>

              {/* 매핑된 필드 (신뢰도 70% 이상) */}
              <div className="mb-8">
                <div className="flex items-center mb-4">
                  <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium mr-3">
                    ✅ 매핑된 필드 ({selectedMappingData.mappedItems.filter((item: any) => item.status === 'auto').length})
                  </span>
                  </div>
                
                <div className="space-y-3">
                  {selectedMappingData.mappedItems
                    .filter((item: any) => item.status === 'auto')
                    .map((item: any) => (
                    <div key={item.id} className="border border-green-200 rounded-lg p-4 bg-green-50">
                      <div className="flex justify-between items-center">
                        <div className="flex-1">
                          <div className="flex items-center space-x-4">
                            <span className="font-medium text-gray-900">원본: {item.original}</span>
                            <span className="text-gray-400">→</span>
                            <span className="text-green-700 font-medium">매핑: {item.mapped}</span>
                  </div>
                          <div className="mt-2 flex items-center space-x-4">
                            <span className="text-sm text-gray-600">
                              CAS: 124-38-9 | 단위: tonCO2eq
                            </span>
                            <span className="text-sm text-gray-600">
                              영문: Carbon dioxide | MSDS: 이산화탄소
                            </span>
                  </div>
                        </div>
                        <div className="flex items-center space-x-3">
                          <span className="text-green-600 font-bold">{item.confidence}%</span>
                          <select className="px-3 py-1 border border-gray-300 rounded text-sm">
                            <option>{item.mapped}</option>
                            <option>ENERGY-CONSUMPTION</option>
                            <option>WASTE-GENERATION</option>
                          </select>
                          <button className="text-red-600 hover:text-red-800 text-sm px-2 py-1 border border-red-300 rounded">
                            해제
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 검토가 필요한 필드 (신뢰도 40-70%) */}
              <div className="mb-8">
                <div className="flex items-center mb-4">
                  <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-medium mr-3">
                    ⚠️ 검토가 필요한 필드 ({selectedMappingData.mappedItems.filter((item: any) => item.status === 'review').length})
                  </span>
                </div>
                
                <div className="space-y-3">
                  {selectedMappingData.mappedItems
                    .filter((item: any) => item.status === 'review')
                    .map((item: any) => (
                    <div key={item.id} className="border border-yellow-200 rounded-lg p-4 bg-yellow-50">
                      <div className="flex justify-between items-center">
                        <div className="flex-1">
                          <div className="flex items-center space-x-4">
                            <span className="font-medium text-gray-900">원본: {item.original}</span>
                            <span className="text-gray-400">→</span>
                            <span className="text-yellow-700 font-medium">
                              매핑: {item.mapped || '선택 필요'}
                            </span>
                          </div>
                          <div className="mt-2 flex items-center space-x-4">
                            <span className="text-sm text-gray-600">
                              사유: 매핑 신뢰도 낮음 (50% 미만)
                            </span>
                            <span className="text-sm text-gray-600">
                              CAS: 2551-62-4 | 영문: Sulfur hexafluoride
                            </span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-3">
                          <span className="text-yellow-600 font-bold">{item.confidence}%</span>
                          <select className="px-3 py-1 border border-gray-300 rounded text-sm bg-white">
                            <option value="">매핑될 선택</option>
                            <option>GHG-HFCs (수소불화탄소)</option>
                            <option>ENERGY-CONSUMPTION</option>
                            <option>WASTE-GENERATION</option>
                          </select>
                          <button className="text-red-600 hover:text-red-800 text-sm px-2 py-1 border border-red-300 rounded">
                            해제
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 액션 버튼 */}
              <div className="flex justify-end space-x-4 pt-6 border-t">
                <button
                  onClick={() => setShowMappingModal(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                >
                  취소
                </button>
                <button
                  onClick={saveMappingResults}
                  className="px-6 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-lg transition-colors font-medium"
                >
                  매핑 저장
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 상세보기 모달 */}
      {showDetailModal && selectedDetailData && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">물질 상세 정보</h2>
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="mb-6">
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <span className="text-sm font-medium text-gray-500">파일명</span>
                    <p className="text-gray-900">{selectedDetailData.fileName}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">파일 유형</span>
                    <p className="text-gray-900">{selectedDetailData.fileType}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">업로드 일시</span>
                    <p className="text-gray-900">{formatDate(selectedDetailData.uploadDate)}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">업로드자</span>
                    <p className="text-gray-900">{selectedDetailData.uploadedBy}</p>
                  </div>
                </div>
              </div>

              {/* 기본 정보 */}
              <div className="border rounded-lg p-6 bg-gray-50 mb-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 border-b border-gray-300 pb-2">
                  기본 정보
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm font-medium text-gray-500">제품명</span>
                    <p className="text-gray-900">{selectedDetailData.substanceData.productName}</p>
                             </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">납품처</span>
                    <p className="text-gray-900">{selectedDetailData.substanceData.supplier}</p>
                             </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">제조일</span>
                    <p className="text-gray-900">{selectedDetailData.substanceData.manufacturingDate}</p>
                             </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">제조 번호</span>
                    <p className="text-gray-900">{selectedDetailData.substanceData.manufacturingNumber}</p>
                             </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">안전 인증 정보</span>
                    <p className="text-gray-900">{selectedDetailData.substanceData.safetyInformation}</p>
                           </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">재활용 자재 사용</span>
                    <span className={`inline-block px-2 py-1 text-xs rounded-full ${
                      selectedDetailData.substanceData.recycledMaterial 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {selectedDetailData.substanceData.recycledMaterial ? '예' : '아니오'}
                             </span>
                           </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">용량</span>
                    <p className="text-gray-900">{selectedDetailData.substanceData.capacity}</p>
                         </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">에너지밀도</span>
                    <p className="text-gray-900">{selectedDetailData.substanceData.energyDensity}</p>
                         </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">제조국</span>
                    <p className="text-gray-900">{selectedDetailData.substanceData.manufacturingCountry}</p>
                       </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">생산공장</span>
                    <p className="text-gray-900">{selectedDetailData.substanceData.productionPlant}</p>
                  </div>
                  </div>
                </div>

              {/* 원재료 정보 */}
              <div className="border rounded-lg p-6 bg-gray-50 mb-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 border-b border-gray-300 pb-2">
                  원재료 정보
                </h3>
                <div className="mb-4">
                  <span className="text-sm font-medium text-gray-500 block mb-2">주요 원재료</span>
                  <div className="flex flex-wrap gap-2">
                    {selectedDetailData.substanceData.rawMaterials.map((material: string, index: number) => (
                      <span key={index} className="inline-block bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full">
                        {material}
                      </span>
                    ))}
                             </div>
                             </div>
                <div>
                  <span className="text-sm font-medium text-gray-500 block mb-2">원재료별 출처</span>
                  <div className="space-y-2">
                    {selectedDetailData.substanceData.rawMaterialSources.map((source: any, index: number) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-white rounded border">
                        <span className="font-medium">{source.material}</span>
                             <span className={`px-2 py-1 text-xs rounded-full ${
                          source.sourceType === '국내 조달' 
                            ? 'bg-blue-100 text-blue-800' 
                            : 'bg-orange-100 text-orange-800'
                        }`}>
                          {source.sourceType}
                             </span>
                        <span className="text-gray-600">
                          {source.sourceType === '국내 조달' ? source.address : source.country}
                               </span>
                           </div>
                    ))}
                         </div>
                         </div>
              </div>

              {/* 온실가스 배출량 */}
              <div className="border rounded-lg p-6 bg-gray-50 mb-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 border-b border-gray-300 pb-2">
                  온실가스 배출량
                </h3>
                <div className="space-y-2">
                  {selectedDetailData.substanceData.greenhouseGasEmissions.map((emission: any, index: number) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-white rounded border">
                      <span className="font-medium">{emission.materialName}</span>
                      <span className="text-gray-900">{emission.amount} {emission.unit}</span>
                       </div>
                     ))}
                   </div>
                 </div>

              {/* 화학물질 구성 비율 */}
              <div className="border rounded-lg p-6 bg-gray-50 mb-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 border-b border-gray-300 pb-2">
                  화학물질 구성 비율
                </h3>
                <p className="text-gray-900">{selectedDetailData.substanceData.chemicalComposition}</p>
                         </div>

              {/* 처리 방법 */}
              <div className="border rounded-lg p-6 bg-gray-50">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 border-b border-gray-300 pb-2">
                  처리 방법
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm font-medium text-gray-500">폐기 방법</span>
                    <p className="text-gray-900">{selectedDetailData.substanceData.disposalMethod}</p>
                         </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">재활용 방법</span>
                    <p className="text-gray-900">{selectedDetailData.substanceData.recyclingMethod}</p>
                           </div>
                 </div>
               </div>

              {/* 닫기 버튼 */}
              <div className="flex justify-end pt-6 border-t mt-6">
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="px-6 py-2 bg-gray-100 text-gray-700 hover:bg-gray-200 rounded-lg transition-colors"
                >
                  닫기
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}