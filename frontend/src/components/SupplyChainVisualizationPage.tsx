"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Building2 } from 'lucide-react';
import SupplyChainVisualization from './SupplyChainVisualization';
import EnvironmentalDataDisplay from './EnvironmentalDataDisplay';
import axios from 'axios';

export default function SupplyChainVisualizationPage() {
  const [selectedCompany, setSelectedCompany] = useState<any>(null);
  const [isLegendExpanded, setIsLegendExpanded] = useState(false);
  const [partners, setPartners] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const handleCompanySelect = (company: any) => {
    setSelectedCompany(company);
  };

  // 협력사 목록 가져오기
  useEffect(() => {
    const fetchPartners = async () => {
      try {
        setIsLoading(true);
        const response = await axios.get('/api/monitoring/partners', {
          params: {
            company_name: 'LG에너지솔루션'
          }
        });
        
        if (response.data.status === 'success') {
          setPartners(response.data.data);
        }
      } catch (error) {
        console.error('협력사 목록 조회 실패:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPartners();
  }, []);

  // 헬퍼 함수들
  const isStrategicPartner = (companyName: string): boolean => {
    const strategicPartners = ['에코프로비엠', '천보', 'SK아이이테크놀로지'];
    return strategicPartners.includes(companyName);
  };

  const getIndustryFromCompanyName = (companyName: string): string => {
    if (companyName.includes('에너지') || companyName.includes('배터리')) return '배터리';
    if (companyName.includes('화학') || companyName.includes('소재')) return '화학소재';
    if (companyName.includes('전자') || companyName.includes('테크')) return '전자소재';
    if (companyName.includes('재활용') || companyName.includes('그린')) return '재활용';
    if (companyName.includes('원료') || companyName.includes('에코')) return '원료공급';
    return '기타';
  };

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="w-5 h-5" />
            공급망 도식화 및 환경데이터
          </CardTitle>
          <CardDescription>
            공급망 네트워크를 시각화하고 각 기업을 클릭하여 환경데이터를 확인하세요.
          </CardDescription>
        </CardHeader>
      </Card>

             {/* 공급망 도식화 */}
       <div className="relative">
         {/* 왼쪽: 공급망 도식화 */}
         <Card>
           <CardHeader>
             <CardTitle>공급망 네트워크</CardTitle>
             <CardDescription>
               기업을 클릭하면 하단에 상세한 환경데이터가 표시됩니다.
             </CardDescription>
           </CardHeader>
           <CardContent className="p-0">
             <div className="relative h-[500px]">
               <SupplyChainVisualization 
                 onCompanySelect={handleCompanySelect} 
                 isLegendExpanded={isLegendExpanded}
                 setIsLegendExpanded={setIsLegendExpanded}
               />
             </div>
           </CardContent>
         </Card>

                   
     </div>

             {/* 하단: 협력사 리스트 + 환경데이터 */}
       <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
         {/* 왼쪽: 협력사 리스트 */}
         <Card>
           <CardHeader>
             <CardTitle>협력사 목록</CardTitle>
             <CardDescription>
               협력사를 클릭하면 오른쪽에 환경데이터가 표시됩니다.
             </CardDescription>
           </CardHeader>
           <CardContent>
             <div className="space-y-3 max-h-96 overflow-y-auto">
               {isLoading ? (
                 <div className="flex items-center justify-center py-8">
                   <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                   <span className="ml-2 text-gray-600">로딩 중...</span>
                 </div>
               ) : partners.length > 0 ? (
                 partners.map((partner, index) => (
                   <div 
                     key={partner.id || index}
                     className={`p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors ${
                       isStrategicPartner(partner.tier1) ? 'bg-yellow-50 border-yellow-200' : ''
                     }`}
                     onClick={() => handleCompanySelect({
                       id: partner.id,
                       label: partner.tier1,
                       tier: '1차사',
                       industry: getIndustryFromCompanyName(partner.tier1),
                       isStrategic: isStrategicPartner(partner.tier1)
                     })}
                   >
                     <div className="flex items-center justify-between">
                       <div className="flex items-center gap-2">
                         <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                           {partner.tier1.charAt(0)}
                         </div>
                         <div>
                           <div className="flex items-center gap-1">
                             <h4 className="font-semibold text-sm">{partner.tier1}</h4>
                             {isStrategicPartner(partner.tier1) && (
                               <span className="text-yellow-600 text-xs">⭐</span>
                             )}
                           </div>
                           <p className="text-xs text-gray-600">1차사 • {getIndustryFromCompanyName(partner.tier1)}</p>
                         </div>
                       </div>
                     </div>
                   </div>
                 ))
               ) : (
                 <div className="text-center py-8 text-gray-500">
                   <p>협력사 데이터가 없습니다.</p>
                 </div>
               )}
             </div>
           </CardContent>
         </Card>

         {/* 오른쪽: 환경데이터 표시 */}
         <Card>
           <CardHeader>
             <CardTitle>환경데이터 상세 정보</CardTitle>
             <CardDescription>
               {selectedCompany 
                 ? `${selectedCompany.label}의 환경데이터 및 지속가능성 정보` 
                 : '왼쪽 협력사 목록에서 기업을 선택하여 환경데이터를 확인하세요.'
               }
             </CardDescription>
           </CardHeader>
           <CardContent>
             <EnvironmentalDataDisplay selectedCompany={selectedCompany} />
           </CardContent>
         </Card>
       </div>
    </div>
  );
}
