"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Building2, Users, Activity, BarChart3, Settings } from 'lucide-react';
import Link from 'next/link';
import SupplyChainVisualizationPage from '@/components/SupplyChainVisualizationPage';

export default function MyPage() {
  const [activeTab, setActiveTab] = useState('overview');

  // 사용자 정보 (실제로는 API에서 가져와야 함)
  const userInfo = {
    name: "LG에너지솔루션",
    tier: "원청사",
    role: "플랫폼 관리자",
    totalSuppliers: 24,
    activeRequests: 12,
    pendingApprovals: 8
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* 헤더 */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center">
              <Building2 className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{userInfo.name}</h1>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant="outline">{userInfo.tier}</Badge>
                <Badge variant="secondary">{userInfo.role}</Badge>
              </div>
            </div>
          </div>
          
          {/* 통계 카드 */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <Users className="w-8 h-8 text-blue-600" />
                  <div>
                    <p className="text-sm text-gray-600">총 협력사 수</p>
                    <p className="text-2xl font-bold">{userInfo.totalSuppliers}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <BarChart3 className="w-8 h-8 text-green-600" />
                  <div>
                    <p className="text-sm text-gray-600">활성 요청</p>
                    <p className="text-2xl font-bold">{userInfo.activeRequests}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <Activity className="w-8 h-8 text-orange-600" />
                  <div>
                    <p className="text-sm text-gray-600">승인 대기</p>
                    <p className="text-2xl font-bold">{userInfo.pendingApprovals}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* 메인 콘텐츠 */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">개요</TabsTrigger>
            <TabsTrigger value="company-management">협력사 관리</TabsTrigger>
            <TabsTrigger value="supply-chain">공급망 도식화</TabsTrigger>
            <TabsTrigger value="settings">설정</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>최근 활동</CardTitle>
                  <CardDescription>지난 7일간의 주요 활동 요약</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="text-sm">신규 데이터 요청 5건 승인</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      <span className="text-sm">협력사 3곳 새로 등록</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                      <span className="text-sm">환경 데이터 8건 업데이트</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>빠른 작업</CardTitle>
                  <CardDescription>자주 사용하는 기능들</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-3">
                    <Link href="/data-sharing-request">
                      <div className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
                        <BarChart3 className="w-6 h-6 text-blue-600 mb-2" />
                        <p className="text-sm font-medium">데이터 요청</p>
                      </div>
                    </Link>
                    
                    <Link href="/data-sharing-approval">
                      <div className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
                        <Users className="w-6 h-6 text-green-600 mb-2" />
                        <p className="text-sm font-medium">승인 관리</p>
                      </div>
                    </Link>
                    
                    <div 
                      className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                      onClick={() => setActiveTab('company-management')}
                    >
                      <Building2 className="w-6 h-6 text-orange-600 mb-2" />
                      <p className="text-sm font-medium">협력사 관리</p>
                    </div>
                    
                    <div 
                      className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                      onClick={() => setActiveTab('supply-chain')}
                    >
                      <Activity className="w-6 h-6 text-purple-600 mb-2" />
                      <p className="text-sm font-medium">공급망 도식화</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="company-management">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building2 className="w-5 h-5" />
                  협력사 목록 관리
                </CardTitle>
                <CardDescription>
                  하위 협력사 정보를 관리하고 데이터 공유 현황을 확인할 수 있습니다.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <Building2 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">협력사 관리 기능 구현 중</h3>
                  <p className="text-gray-600">
                    곧 하위 협력사 목록 조회, 편집, 데이터 공유 현황 등을 관리할 수 있습니다.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="supply-chain">
            <SupplyChainVisualizationPage />
          </TabsContent>

          <TabsContent value="settings">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="w-5 h-5" />
                  설정
                </CardTitle>
                <CardDescription>
                  계정 및 시스템 설정을 관리합니다.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div>
                    <h4 className="text-sm font-medium mb-3">계정 정보</h4>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">회사명</span>
                        <span className="text-sm font-medium">{userInfo.name}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">계층</span>
                        <Badge variant="outline">{userInfo.tier}</Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">역할</span>
                        <Badge variant="secondary">{userInfo.role}</Badge>
                      </div>
                    </div>
                  </div>
                  
                  <div className="border-t pt-6">
                    <h4 className="text-sm font-medium mb-3">알림 설정</h4>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">데이터 요청 알림</span>
                        <Badge variant="default">활성</Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">승인 알림</span>
                        <Badge variant="default">활성</Badge>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
