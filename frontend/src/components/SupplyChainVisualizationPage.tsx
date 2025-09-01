"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Building2 } from 'lucide-react';
import SupplyChainVisualization from './SupplyChainVisualization';
import EnvironmentalDataDisplay from './EnvironmentalDataDisplay';

export default function SupplyChainVisualizationPage() {
  const [selectedCompany, setSelectedCompany] = useState<any>(null);
  const [isLegendExpanded, setIsLegendExpanded] = useState(false);

  const handleCompanySelect = (company: any) => {
    setSelectedCompany(company);
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
               {/* 1차 협력사들 */}
               <div 
                 className="p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors bg-yellow-50 border-yellow-200"
                 onClick={() => handleCompanySelect({
                   id: 'entop',
                   label: '엔탑',
                   tier: '1차사',
                   industry: '화학소재',
                   isStrategic: true
                 })}
               >
                 <div className="flex items-center justify-between">
                   <div className="flex items-center gap-2">
                     <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                       엔
                     </div>
                     <div>
                       <div className="flex items-center gap-1">
                         <h4 className="font-semibold text-sm">엔탑</h4>
                         <span className="text-yellow-600 text-xs">⭐</span>
                       </div>
                       <p className="text-xs text-gray-600">1차사 • 화학소재</p>
                     </div>
                   </div>
                 </div>
               </div>

               <div 
                 className="p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                 onClick={() => handleCompanySelect({
                   id: 'cosmo',
                   label: '코스모신소재',
                   tier: '1차사',
                   industry: '전자소재',
                   isStrategic: false
                 })}
               >
                 <div className="flex items-center justify-between">
                   <div className="flex items-center gap-2">
                     <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                       코
                     </div>
                     <div>
                       <h4 className="font-semibold text-sm">코스모신소재</h4>
                       <p className="text-xs text-gray-600">1차사 • 전자소재</p>
                     </div>
                   </div>
                 </div>
               </div>

               <div 
                 className="p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors bg-yellow-50 border-yellow-200"
                 onClick={() => handleCompanySelect({
                   id: 'greentech',
                   label: '그린테크솔루션',
                   tier: '1차사',
                   industry: '재활용',
                   isStrategic: true
                 })}
               >
                 <div className="flex items-center justify-between">
                   <div className="flex items-center gap-2">
                     <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                       그
                     </div>
                     <div>
                       <div className="flex items-center gap-1">
                         <h4 className="font-semibold text-sm">그린테크솔루션</h4>
                         <span className="text-yellow-600 text-xs">⭐</span>
                       </div>
                       <p className="text-xs text-gray-600">1차사 • 재활용</p>
                     </div>
                   </div>
                 </div>
               </div>

               {/* 2차 협력사들 */}
               <div 
                 className="p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                 onClick={() => handleCompanySelect({
                   id: 'ecomaterial',
                   label: '에코머티리얼',
                   tier: '2차사',
                   industry: '원료공급',
                   isStrategic: false
                 })}
               >
                 <div className="flex items-center justify-between">
                   <div className="flex items-center gap-2">
                     <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                       에
                     </div>
                     <div>
                       <h4 className="font-semibold text-sm">에코머티리얼</h4>
                       <p className="text-xs text-gray-600">2차사 • 원료공급</p>
                     </div>
                   </div>
                 </div>
               </div>

               <div 
                 className="p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors bg-yellow-50 border-yellow-200"
                 onClick={() => handleCompanySelect({
                   id: 'cleansolution',
                   label: '클린솔루션',
                   tier: '2차사',
                   industry: '폐기물처리',
                   isStrategic: true
                 })}
               >
                 <div className="flex items-center justify-between">
                   <div className="flex items-center gap-2">
                     <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                       클
                     </div>
                     <div>
                       <div className="flex items-center gap-1">
                         <h4 className="font-semibold text-sm">클린솔루션</h4>
                         <span className="text-yellow-600 text-xs">⭐</span>
                       </div>
                       <p className="text-xs text-gray-600">2차사 • 폐기물처리</p>
                     </div>
                   </div>
                 </div>
               </div>

               <div 
                 className="p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                 onClick={() => handleCompanySelect({
                   id: 'biomass',
                   label: '바이오매스',
                   tier: '2차사',
                   industry: '바이오연료',
                   isStrategic: false
                 })}
               >
                 <div className="flex items-center justify-between">
                   <div className="flex items-center gap-2">
                     <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                       바
                     </div>
                     <div>
                       <h4 className="font-semibold text-sm">바이오매스</h4>
                       <p className="text-xs text-gray-600">2차사 • 바이오연료</p>
                     </div>
                   </div>
                 </div>
               </div>

               <div 
                 className="p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                 onClick={() => handleCompanySelect({
                   id: 'eco-packaging',
                   label: '친환경포장',
                   tier: '2차사',
                   industry: '포장재',
                   isStrategic: false
                 })}
               >
                 <div className="flex items-center justify-between">
                   <div className="flex items-center gap-2">
                     <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                       친
                     </div>
                     <div>
                       <h4 className="font-semibold text-sm">친환경포장</h4>
                       <p className="text-xs text-gray-600">2차사 • 포장재</p>
                     </div>
                   </div>
                 </div>
               </div>
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
