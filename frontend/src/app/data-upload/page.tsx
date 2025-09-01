'use client';

import { useState, useCallback, useMemo, useEffect } from 'react';
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

interface ProductItem {
  productName: string;
  supplier: string;
  manufacturingDate: string;
  capacity: string;
  recycledMaterial: boolean;
  created_at: string;
  updated_at: string;
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

export default function PartnerDataUploadPage() {
  const router = useRouter();
  const [substanceData, setSubstanceData] = useState<SubstanceData>(createEmptySubstance());
  const [existingProducts, setExistingProducts] = useState<ProductItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const [partnerInfo] = useState({
    name: 'LG화학',
    companyId: 'LG001',
    status: 'active',
    lastSubmission: '2024-01-15',
    nextDeadline: '2024-02-15',
    userName: '담당자'
  });

  // 기존 제품 목록 로드
  useEffect(() => {
    loadExistingProducts();
  }, []);

  const loadExistingProducts = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`/api/normal/company/${partnerInfo.name}/products`);
      if (response.ok) {
        const data = await response.json();
        if (data.status === 'success') {
          setExistingProducts(data.data);
        }
      }
    } catch (error) {
      console.error('제품 목록 로드 실패:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 자동 매핑 시작
  const startAutoMapping = async () => {
    try {
      setIsSubmitting(true);
      
      const response = await fetch('/api/normal/substance/save-and-map', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          substance_data: substanceData,
          company_id: partnerInfo.companyId,
          company_name: partnerInfo.name,
          uploaded_by: partnerInfo.userName,
        }),
      });

      if (!response.ok) {
        throw new Error('데이터 저장 및 매핑 실패');
      }

      const result = await response.json();
      console.log('자동매핑 결과:', result);
      
      alert('제품 데이터 저장 및 자동매핑 완료!');
      
      // 폼 초기화
      setSubstanceData(createEmptySubstance());
      
      // 제품 목록 새로고침
      loadExistingProducts();
      
    } catch (error) {
      console.error('자동매핑 오류:', error);
      alert(`오류가 발생했습니다: ${error instanceof Error ? error.message : '알 수 없는 오류'}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const predefinedMaterials = ['리튬', '니켈', '코발트', '망간', '알루미늄', '흑연', '형석', '기타'];
  const countries = ['한국', '중국', '일본', '미국', '독일', '프랑스', '영국', '이탈리아', '스페인', '네덜란드', '벨기에', '스위스', '오스트리아', '기타'];
  const importCountries = countries.filter(country => country !== '한국');

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">데이터 업로드</h1>
              <p className="text-gray-600 mt-1">제품 정보 및 온실가스 배출량 데이터를 입력하세요</p>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-500">파트너</div>
              <div className="font-semibold text-gray-900">{partnerInfo.name}</div>
              <div className="text-sm text-gray-500">{partnerInfo.userName}</div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* 메인 폼 */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="px-6 py-4 border-b">
                <h2 className="text-lg font-semibold text-gray-900">제품 정보 입력</h2>
                <p className="text-sm text-gray-600 mt-1">새로운 제품의 상세 정보를 입력하세요</p>
              </div>
              
              <div className="p-6 space-y-6">
                {/* 기본 정보 */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      제품명 <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={substanceData.productName}
                      onChange={(e) => setSubstanceData({...substanceData, productName: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="제품명을 입력하세요"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      공급업체
                    </label>
                    <input
                      type="text"
                      value={substanceData.supplier}
                      onChange={(e) => setSubstanceData({...substanceData, supplier: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="공급업체명을 입력하세요"
                    />
                  </div>
                </div>

                {/* 제조 정보 */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      제조일자
                    </label>
                    <input
                      type="date"
                      value={substanceData.manufacturingDate}
                      onChange={(e) => setSubstanceData({...substanceData, manufacturingDate: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      제조번호
                    </label>
                    <input
                      type="text"
                      value={substanceData.manufacturingNumber}
                      onChange={(e) => setSubstanceData({...substanceData, manufacturingNumber: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="제조번호를 입력하세요"
                    />
                  </div>
                </div>

                {/* 용량 및 에너지 밀도 */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      용량
                    </label>
                    <input
                      type="text"
                      value={substanceData.capacity}
                      onChange={(e) => setSubstanceData({...substanceData, capacity: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="예: 100Ah"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      에너지 밀도
                    </label>
                    <input
                      type="text"
                      value={substanceData.energyDensity}
                      onChange={(e) => setSubstanceData({...substanceData, energyDensity: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="예: 250Wh/kg"
                    />
                  </div>
                </div>

                {/* 온실가스 배출량 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    온실가스 배출량
                  </label>
                  <div className="space-y-3">
                    {substanceData.greenhouseGasEmissions.map((emission, index) => (
                      <div key={index} className="flex gap-3 items-end">
                        <div className="flex-1">
                          <input
                            type="text"
                            value={emission.materialName}
                            onChange={(e) => {
                              const newEmissions = [...substanceData.greenhouseGasEmissions];
                              newEmissions[index].materialName = e.target.value;
                              setSubstanceData({...substanceData, greenhouseGasEmissions: newEmissions});
                            }}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="물질명 (예: CO2, CH4)"
                          />
                        </div>
                        <div className="w-24">
                          <input
                            type="text"
                            value={emission.amount}
                            onChange={(e) => {
                              const newEmissions = [...substanceData.greenhouseGasEmissions];
                              newEmissions[index].amount = e.target.value;
                              setSubstanceData({...substanceData, greenhouseGasEmissions: newEmissions});
                            }}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="양"
                          />
                        </div>
                        <div className="w-20">
                          <input
                            type="text"
                            value={emission.unit}
                            onChange={(e) => {
                              const newEmissions = [...substanceData.greenhouseGasEmissions];
                              newEmissions[index].unit = e.target.value;
                              setSubstanceData({...substanceData, greenhouseGasEmissions: newEmissions});
                            }}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="단위"
                          />
                        </div>
                        <button
                          type="button"
                          onClick={() => {
                            const newEmissions = substanceData.greenhouseGasEmissions.filter((_, i) => i !== index);
                            setSubstanceData({...substanceData, greenhouseGasEmissions: newEmissions});
                          }}
                          className="px-3 py-2 text-red-600 hover:text-red-800"
                        >
                          삭제
                        </button>
                      </div>
                    ))}
                    <button
                      type="button"
                      onClick={() => {
                        setSubstanceData({
                          ...substanceData,
                          greenhouseGasEmissions: [...substanceData.greenhouseGasEmissions, {materialName: '', amount: '', unit: 'tonCO2eq'}]
                        });
                      }}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      + 온실가스 배출량 추가
                    </button>
                  </div>
                </div>

                {/* 제출 버튼 */}
                <div className="pt-6 border-t">
                  <button
                    onClick={startAutoMapping}
                    disabled={isSubmitting || !substanceData.productName}
                    className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
                  >
                    {isSubmitting ? '처리 중...' : '제품 추가 및 자동매핑 시작'}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* 기존 제품 목록 */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="px-6 py-4 border-b">
                <h2 className="text-lg font-semibold text-gray-900">기존 제품 목록</h2>
                <p className="text-sm text-gray-600 mt-1">{partnerInfo.name}의 등록된 제품들</p>
              </div>
              
              <div className="p-6">
                {isLoading ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="text-gray-500 mt-2">제품 목록 로딩 중...</p>
                  </div>
                ) : existingProducts.length === 0 ? (
                  <div className="text-center py-8">
                    <div className="text-gray-400 text-4xl mb-2">📦</div>
                    <p className="text-gray-500">등록된 제품이 없습니다</p>
                    <p className="text-sm text-gray-400 mt-1">새로운 제품을 추가해보세요</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {existingProducts.map((product, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <h3 className="font-medium text-gray-900">{product.productName}</h3>
                            {product.supplier && (
                              <p className="text-sm text-gray-600 mt-1">공급업체: {product.supplier}</p>
                            )}
                            {product.capacity && (
                              <p className="text-sm text-gray-600">용량: {product.capacity}</p>
                            )}
                            {product.manufacturingDate && (
                              <p className="text-sm text-gray-500 mt-1">
                                제조일: {new Date(product.manufacturingDate).toLocaleDateString('ko-KR')}
                              </p>
                            )}
                            {product.recycledMaterial && (
                              <span className="inline-block bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full mt-2">
                                재활용 소재
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
