'use client';

import { useState, useCallback, useEffect } from 'react';
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

export default function DataUploadPage() {
  const router = useRouter();
  const [substanceData, setSubstanceData] = useState<SubstanceData>(createEmptySubstance());
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const [partnerInfo] = useState({
    name: 'LG화학',
    companyId: 'LG001',
    status: 'active',
    lastSubmission: '2024-01-15',
    nextDeadline: '2024-02-15',
    userName: '담당자'
  });

  const predefinedMaterials = ['리튬', '니켈', '코발트', '망간', '알루미늄', '흑연', '형석', '기타'];
  const countries = ['한국', '중국', '일본', '미국', '독일', '프랑스', '영국', '이탈리아', '스페인', '네덜란드', '벨기에', '스위스', '오스트리아', '기타'];
  const importCountries = countries.filter(country => country !== '한국');

  // 자동 매핑 시작
  const startAutoMapping = async () => {
    try {
      if (!substanceData.productName) {
        alert('최소한 제품명은 입력해주세요.');
        return;
      }

      // 온실가스 배출량 데이터가 있는지 확인
      if (!substanceData.greenhouseGasEmissions || substanceData.greenhouseGasEmissions.length === 0) {
        alert('온실가스 배출량 데이터를 최소 1개 이상 추가해주세요. "+ 추가" 버튼을 눌러 CO2, 1 tonCO2eq 등을 입력해주세요.');
        return;
      }

      setIsSubmitting(true);
      
      // 요청 바디 구성 및 로깅
      const requestBody = {
        substance_data: substanceData,
        company_id: partnerInfo.companyId,
        company_name: partnerInfo.name,
        uploaded_by: partnerInfo.userName,
      };
      
      console.log('POST body', requestBody);
      console.log('greenhouseGasEmissions:', substanceData.greenhouseGasEmissions);
      
      // 데이터 저장 및 자동매핑 시작
      const response = await fetch('/api/normal/substance/save-and-map', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      // 비 JSON 응답 가드 추가
      const contentType = response.headers.get('content-type') || '';
      if (!contentType.includes('application/json')) {
        const text = await response.text();
        throw new Error(`비 JSON 응답: ${response.status} ${text.slice(0, 120)}`);
      }

      const result = await response.json();
      
      if (result.status === 'success' || result.status === 'partial') {
        // 매핑 수정 페이지로 이동 (normal_id 전달)
        router.push(`/data-upload/mapping-edit?normalId=${result.normal_id}`);
        
        // partial 상태인 경우 사용자에게 알림
        if (result.status === 'partial') {
          const successCount = result.success_count || 0;
          const failedCount = result.failed_count || 0;
          alert(`저장은 완료되었지만 자동매핑에 실패했습니다.\n성공: ${successCount}개, 실패: ${failedCount}개\n매핑 수정 페이지에서 수동으로 확인해주세요.`);
        }
      } else {
        alert(`오류가 발생했습니다: ${result.message || result.error}`);
      }
      
    } catch (error) {
      console.error('자동매핑 오류:', error);
      alert(`오류가 발생했습니다: ${error instanceof Error ? error.message : '알 수 없는 오류'}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const updateSubstanceData = (field: keyof SubstanceData, value: any) => {
    setSubstanceData(prev => ({ ...prev, [field]: value }));
  };

  // 원재료 관련 함수들
  const handleRawMaterialChange = (material: string, checked: boolean) => {
    setSubstanceData(prev => ({
      ...prev,
      rawMaterials: checked 
        ? [...prev.rawMaterials, material]
        : prev.rawMaterials.filter(m => m !== material)
    }));
  };

  const addOtherRawMaterial = () => {
    setSubstanceData(prev => ({
      ...prev,
      rawMaterialsOther: [...prev.rawMaterialsOther, '']
    }));
  };

  const updateOtherRawMaterial = (index: number, value: string) => {
    setSubstanceData(prev => ({
      ...prev,
      rawMaterialsOther: prev.rawMaterialsOther.map((material, i) => 
        i === index ? value : material
      )
    }));
  };

  const removeOtherRawMaterial = (index: number) => {
    setSubstanceData(prev => ({
      ...prev,
      rawMaterialsOther: prev.rawMaterialsOther.filter((_, i) => i !== index)
    }));
  };

  const getAllSelectedMaterials = () => {
    const materials = [...substanceData.rawMaterials];
    const otherMaterials = substanceData.rawMaterialsOther.filter(m => m.trim() !== '');
    return [...materials, ...otherMaterials].map(material => ({
      key: material,
      name: material
    }));
  };

  const updateMaterialSource = (material: string, field: keyof RawMaterialSource, value: string) => {
    setSubstanceData(prev => {
      const existingIndex = prev.rawMaterialSources.findIndex(s => s.material === material);
      if (existingIndex >= 0) {
        return {
          ...prev,
          rawMaterialSources: prev.rawMaterialSources.map((source, i) => 
            i === existingIndex ? { ...source, [field]: value } : source
          )
        };
      } else {
        return {
          ...prev,
          rawMaterialSources: [...prev.rawMaterialSources, { material, sourceType: '', [field]: value } as RawMaterialSource]
        };
      }
    });
  };

  const addGreenhouseGas = () => {
    setSubstanceData(prev => ({
      ...prev,
      greenhouseGasEmissions: [...prev.greenhouseGasEmissions, { materialName: '', amount: '', unit: 'tonCO2eq' }]
    }));
  };

  const updateGreenhouseGas = (index: number, field: keyof GreenhouseGasEmission, value: string) => {
    setSubstanceData(prev => ({
      ...prev,
      greenhouseGasEmissions: prev.greenhouseGasEmissions.map((gas, i) => 
        i === index ? { ...gas, [field]: value } : gas
      )
    }));
  };

  const removeGreenhouseGas = (index: number) => {
    setSubstanceData(prev => ({
      ...prev,
      greenhouseGasEmissions: prev.greenhouseGasEmissions.filter((_, i) => i !== index)
    }));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">ESG 데이터 업로드</h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                <span className="font-medium">{partnerInfo.name}</span> • {partnerInfo.userName}
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">물질 데이터 입력</h2>
            <p className="mt-1 text-sm text-gray-500">
              제품의 환경 정보를 입력하고 자동 매핑을 시작하세요.
            </p>
              </div>
              
          <div className="p-6 space-y-8">
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
                    <option value="에코프로">에코프로</option>
                    <option value="LG에너지솔루션">LG에너지솔루션</option>
                    <option value="포스코퓨처엠">포스코퓨처엠</option>
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
                    placeholder="생산공장 명칭과 위치를 입력하세요"
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
                귀사에서 관리되는 온실가스를 입력하세요.
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

                        {/* 기타 정보 섹션 */}
            <div className="border rounded-lg p-6 bg-gray-50">
              <h4 className="text-md font-semibold text-gray-800 mb-4 border-b border-gray-300 pb-2">
                기타 정보
              </h4>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">화학 조성</label>
                  <textarea
                    value={substanceData.chemicalComposition}
                    onChange={(e) => setSubstanceData(prev => ({ ...prev, chemicalComposition: e.target.value }))}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="화학 조성을 입력하세요"
                  />
                </div>
              </div>
            </div>

            {/* 제출 버튼 */}
            <div className="flex justify-end space-x-4 pt-6 border-t">
              <button
                onClick={() => router.back()}
                className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                취소
              </button>
              <button
                onClick={startAutoMapping}
                disabled={isSubmitting || !substanceData.productName}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? '처리 중...' : '자동 매핑 시작'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}