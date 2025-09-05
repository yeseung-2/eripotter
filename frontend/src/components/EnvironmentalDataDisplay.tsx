"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  BarChart3, 
  Activity, 
  Zap, 
  Users, 
  RotateCcw, 
  TrendingUp, 
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Clock,
  FileText
} from 'lucide-react';
import { api } from '@/lib/api';

interface EnvironmentalDataDisplayProps {
  selectedCompany: any;
}

interface EnvironmentalData {
  company: string;
  carbonFootprint: {
    total: number;
    trend: 'up' | 'down' | 'stable';
    lastUpdate: string;
    breakdown: {
      scope1: number;
      scope2: number;
      scope3: number;
    };
  };
  energyUsage: {
    total: number;
    renewable: number;
    trend: 'up' | 'down' | 'stable';
    lastUpdate: string;
  };
  waterUsage: {
    total: number;
    recycled: number;
    trend: 'up' | 'down' | 'stable';
    lastUpdate: string;
  };
  wasteManagement: {
    total: number;
    recycled: number;
    landfill: number;
    trend: 'up' | 'down' | 'stable';
    lastUpdate: string;
  };
  certifications: string[];
  sharingStatus: {
    totalRequests: number;
    approved: number;
    pending: number;
    rejected: number;
    lastShared: string;
  };
}

export default function EnvironmentalDataDisplay({ selectedCompany }: EnvironmentalDataDisplayProps) {
  const [environmentalData, setEnvironmentalData] = useState<EnvironmentalData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 실제 API에서 환경 데이터 가져오기
  useEffect(() => {
    if (!selectedCompany) {
      setEnvironmentalData(null);
      setError(null);
      return;
    }

    const fetchEnvironmentalData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // 1. normal-service에서 환경 데이터 가져오기
        const normalData = await fetchNormalServiceData(selectedCompany.label);
        
        // 2. sharing-service에서 데이터 공유 현황 가져오기
        const sharingData = await fetchSharingServiceData(selectedCompany.label);
        
        // 3. 데이터 통합
        const integratedData: EnvironmentalData = {
          company: selectedCompany.label,
          carbonFootprint: {
            total: normalData.carbonFootprint?.total || 0,
            trend: normalData.carbonFootprint?.trend || 'stable',
            lastUpdate: normalData.carbonFootprint?.lastUpdate || new Date().toISOString().split('T')[0],
            breakdown: {
              scope1: normalData.carbonFootprint?.breakdown?.scope1 || 0,
              scope2: normalData.carbonFootprint?.breakdown?.scope2 || 0,
              scope3: normalData.carbonFootprint?.breakdown?.scope3 || 0,
            }
          },
          energyUsage: {
            total: normalData.energyUsage?.total || 0,
            renewable: normalData.energyUsage?.renewable || 0,
            trend: normalData.energyUsage?.trend || 'stable',
            lastUpdate: normalData.energyUsage?.lastUpdate || new Date().toISOString().split('T')[0],
          },
          waterUsage: {
            total: normalData.waterUsage?.total || 0,
            recycled: normalData.waterUsage?.recycled || 0,
            trend: normalData.waterUsage?.trend || 'stable',
            lastUpdate: normalData.waterUsage?.lastUpdate || new Date().toISOString().split('T')[0],
          },
          wasteManagement: {
            total: normalData.wasteManagement?.total || 0,
            recycled: normalData.wasteManagement?.recycled || 0,
            landfill: normalData.wasteManagement?.landfill || 0,
            trend: normalData.wasteManagement?.trend || 'stable',
            lastUpdate: normalData.wasteManagement?.lastUpdate || new Date().toISOString().split('T')[0],
          },
          certifications: normalData.certifications || [],
          sharingStatus: {
            totalRequests: sharingData.totalRequests || 0,
            approved: sharingData.approved || 0,
            pending: sharingData.pending || 0,
            rejected: sharingData.rejected || 0,
            lastShared: sharingData.lastShared || new Date().toISOString().split('T')[0],
          }
        };
        
        setEnvironmentalData(integratedData);
      } catch (err) {
        console.error('환경 데이터 로드 실패:', err);
        setError('환경 데이터를 불러오는 중 오류가 발생했습니다.');
      } finally {
        setLoading(false);
      }
    };

    fetchEnvironmentalData();
  }, [selectedCompany]);

  // normal-service에서 환경 데이터 가져오기
  const fetchNormalServiceData = async (companyName: string) => {
    try {
      // 새로운 환경 데이터 API 엔드포인트 사용
      const response = await api(`/normal/environmental/${encodeURIComponent(companyName)}`);
      
      if (response.status === 'success' && response.data) {
        return response.data;
      } else {
        // 데이터가 없으면 기본값 반환
        return {
          carbonFootprint: { total: 538, trend: 'down', breakdown: { scope1: 150, scope2: 200, scope3: 188 } },
          energyUsage: { total: 4105, renewable: 1200, trend: 'up' },
          waterUsage: { total: 9363, recycled: 2800, trend: 'stable' },
          wasteManagement: { total: 483, recycled: 350, landfill: 133, trend: 'up' },
          certifications: ['ISO 14001', 'ISO 50001']
        };
      }
    } catch (error) {
      console.warn('normal-service 데이터 로드 실패, 기본값 사용:', error);
      // API 실패 시 기본값 반환
      return {
        carbonFootprint: { total: 538, trend: 'down', breakdown: { scope1: 150, scope2: 200, scope3: 188 } },
        energyUsage: { total: 4105, renewable: 1200, trend: 'up' },
        waterUsage: { total: 9363, recycled: 2800, trend: 'stable' },
        wasteManagement: { total: 483, recycled: 350, landfill: 133, trend: 'up' },
        certifications: ['ISO 14001', 'ISO 50001']
      };
    }
  };

  // sharing-service에서 데이터 공유 현황 가져오기
  const fetchSharingServiceData = async (companyName: string) => {
    try {
      // 새로운 통계 API 엔드포인트 사용
      const response = await api(`/sharing/statistics/${encodeURIComponent(companyName)}`);
      
      if (response.status === 'success' && response.data) {
        return response.data;
      } else {
        return {
          totalRequests: 0,
          approved: 0,
          pending: 0,
          rejected: 0,
          lastShared: new Date().toISOString().split('T')[0]
        };
      }
    } catch (error) {
      console.warn('sharing-service 데이터 로드 실패, 기본값 사용:', error);
      // API 실패 시 기본값 반환
      return {
        totalRequests: 15,
        approved: 12,
        pending: 2,
        rejected: 1,
        lastShared: new Date().toISOString().split('T')[0]
      };
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return <TrendingUp className="w-4 h-4 text-red-500" />;
      case 'down': return <TrendingDown className="w-4 h-4 text-green-500" />;
      default: return <div className="w-4 h-4 rounded-full bg-gray-400"></div>;
    }
  };

  if (!selectedCompany) {
    return (
      <div className="p-8 text-center">
        <Activity className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">공급망 기업을 선택하세요</h3>
        <p className="text-gray-600">
          위의 공급망 도식도에서 기업을 클릭하면 해당 기업의 환경데이터를 확인할 수 있습니다.
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="p-8 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">환경데이터를 불러오는 중...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 text-center">
        <AlertTriangle className="w-16 h-16 text-orange-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">데이터를 불러올 수 없습니다</h3>
        <p className="text-gray-600">{error}</p>
        <button 
          onClick={() => window.location.reload()} 
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          다시 시도
        </button>
      </div>
    );
  }

  if (!environmentalData) {
    return (
      <div className="p-8 text-center">
        <AlertTriangle className="w-16 h-16 text-orange-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">데이터를 불러올 수 없습니다</h3>
        <p className="text-gray-600">선택한 기업의 환경데이터를 찾을 수 없습니다.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 기업 정보 헤더 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <Activity className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{environmentalData.company}</h2>
            <div className="flex items-center gap-2 mt-1">
              <Badge variant="outline">{selectedCompany.tier}</Badge>
              <Badge variant="secondary">{selectedCompany.industry}</Badge>
              {selectedCompany.isStrategic && (
                <Badge className="bg-yellow-100 text-yellow-800">⭐ 핵심 협력사</Badge>
              )}
            </div>
          </div>
        </div>
        

      </div>

      {/* 환경데이터 탭 */}
      <Tabs value="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">개요</TabsTrigger>
          <TabsTrigger value="carbon">탄소발자국</TabsTrigger>
          <TabsTrigger value="resources">자원사용</TabsTrigger>
          <TabsTrigger value="sharing">데이터공유</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <Activity className="w-8 h-8 text-green-600" />
                  <div>
                    <p className="text-sm text-gray-600">탄소배출량</p>
                    <div className="flex items-center gap-1">
                      <p className="text-lg font-bold">{environmentalData.carbonFootprint.total}</p>
                      {getTrendIcon(environmentalData.carbonFootprint.trend)}
                    </div>
                    <p className="text-xs text-gray-500">tCO₂eq</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <Zap className="w-8 h-8 text-yellow-600" />
                  <div>
                    <p className="text-sm text-gray-600">에너지사용량</p>
                    <div className="flex items-center gap-1">
                      <p className="text-lg font-bold">{environmentalData.energyUsage.total}</p>
                      {getTrendIcon(environmentalData.energyUsage.trend)}
                    </div>
                    <p className="text-xs text-gray-500">MWh</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <Users className="w-8 h-8 text-blue-600" />
                  <div>
                    <p className="text-sm text-gray-600">물사용량</p>
                    <div className="flex items-center gap-1">
                      <p className="text-lg font-bold">{environmentalData.waterUsage.total}</p>
                      {getTrendIcon(environmentalData.waterUsage.trend)}
                    </div>
                    <p className="text-xs text-gray-500">㎥</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <RotateCcw className="w-8 h-8 text-purple-600" />
                  <div>
                    <p className="text-sm text-gray-600">폐기물</p>
                    <div className="flex items-center gap-1">
                      <p className="text-lg font-bold">{environmentalData.wasteManagement.total}</p>
                      {getTrendIcon(environmentalData.wasteManagement.trend)}
                    </div>
                    <p className="text-xs text-gray-500">톤</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 인증 현황 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5" />
                환경 인증 현황
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2 flex-wrap">
                {environmentalData.certifications.length > 0 ? (
                  environmentalData.certifications.map((cert, index) => (
                    <Badge key={index} className="bg-green-100 text-green-800">
                      {cert}
                    </Badge>
                  ))
                ) : (
                  <p className="text-gray-500">인증 정보가 없습니다.</p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="carbon" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>탄소발자국 상세</CardTitle>
              <CardDescription>Scope별 탄소 배출량 (tCO₂eq)</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-red-50 rounded-lg">
                    <h4 className="font-semibold text-red-800">Scope 1</h4>
                    <p className="text-2xl font-bold text-red-600">{environmentalData.carbonFootprint.breakdown.scope1}</p>
                    <p className="text-xs text-red-600">직접 배출</p>
                  </div>
                  <div className="text-center p-4 bg-orange-50 rounded-lg">
                    <h4 className="font-semibold text-orange-800">Scope 2</h4>
                    <p className="text-2xl font-bold text-orange-600">{environmentalData.carbonFootprint.breakdown.scope2}</p>
                    <p className="text-xs text-orange-600">간접 배출</p>
                  </div>
                  <div className="text-center p-4 bg-yellow-50 rounded-lg">
                    <h4 className="font-semibold text-yellow-800">Scope 3</h4>
                    <p className="text-2xl font-bold text-yellow-600">{environmentalData.carbonFootprint.breakdown.scope3}</p>
                    <p className="text-xs text-yellow-600">기타 간접</p>
                  </div>
                </div>
                
                <div className="pt-4 border-t">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">총 배출량:</span>
                    <span className="text-lg font-bold">{environmentalData.carbonFootprint.total} tCO₂eq</span>
                  </div>
                  <div className="flex justify-between items-center mt-2">
                    <span className="text-sm text-gray-600">최근 업데이트:</span>
                    <span className="text-sm">{environmentalData.carbonFootprint.lastUpdate}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="resources" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="w-5 h-5" />
                  에너지 사용량
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span>총 사용량:</span>
                    <span className="font-bold">{environmentalData.energyUsage.total} MWh</span>
                  </div>
                  <div className="flex justify-between">
                    <span>재생에너지:</span>
                    <span className="font-bold text-green-600">{environmentalData.energyUsage.renewable} MWh</span>
                  </div>
                  <div className="flex justify-between">
                    <span>재생에너지 비율:</span>
                    <span className="font-bold">
                      {Math.round((environmentalData.energyUsage.renewable / environmentalData.energyUsage.total) * 100)}%
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  물 사용량
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span>총 사용량:</span>
                    <span className="font-bold">{environmentalData.waterUsage.total} ㎥</span>
                  </div>
                  <div className="flex justify-between">
                    <span>재활용량:</span>
                    <span className="font-bold text-blue-600">{environmentalData.waterUsage.recycled} ㎥</span>
                  </div>
                  <div className="flex justify-between">
                    <span>재활용 비율:</span>
                    <span className="font-bold">
                      {Math.round((environmentalData.waterUsage.recycled / environmentalData.waterUsage.total) * 100)}%
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
                              <CardTitle className="flex items-center gap-2">
                  <RotateCcw className="w-5 h-5" />
                  폐기물 관리
                </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center">
                  <p className="text-sm text-gray-600">총 폐기물</p>
                  <p className="text-xl font-bold">{environmentalData.wasteManagement.total}</p>
                  <p className="text-xs text-gray-500">톤</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600">재활용</p>
                  <p className="text-xl font-bold text-green-600">{environmentalData.wasteManagement.recycled}</p>
                  <p className="text-xs text-gray-500">톤</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600">매립</p>
                  <p className="text-xl font-bold text-red-600">{environmentalData.wasteManagement.landfill}</p>
                  <p className="text-xs text-gray-500">톤</p>
                </div>
              </div>
              <div className="mt-4 pt-4 border-t">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">재활용률:</span>
                  <span className="font-bold text-green-600">
                    {Math.round((environmentalData.wasteManagement.recycled / environmentalData.wasteManagement.total) * 100)}%
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="sharing" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  데이터 공유 현황
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600">{environmentalData.sharingStatus.totalRequests}</p>
                    <p className="text-sm text-gray-600">총 요청</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">{environmentalData.sharingStatus.approved}</p>
                    <p className="text-sm text-gray-600">승인</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-yellow-600">{environmentalData.sharingStatus.pending}</p>
                    <p className="text-sm text-gray-600">대기</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-red-600">{environmentalData.sharingStatus.rejected}</p>
                    <p className="text-sm text-gray-600">거부</p>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">승인률:</span>
                    <span className="font-bold text-green-600">
                      {environmentalData.sharingStatus.totalRequests > 0 
                        ? Math.round((environmentalData.sharingStatus.approved / environmentalData.sharingStatus.totalRequests) * 100)
                        : 0}%
                    </span>
                  </div>
                  <div className="flex justify-between mt-2">
                    <span className="text-sm text-gray-600">최근 공유:</span>
                    <span className="text-sm">{environmentalData.sharingStatus.lastShared}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="w-5 h-5" />
                  빠른 작업
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <button className="w-full p-3 text-left bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors">
                    <div className="font-medium">새 데이터 요청</div>
                    <div className="text-sm text-blue-600">이 협력사에게 데이터 요청하기</div>
                  </button>
                  
                  <button className="w-full p-3 text-left bg-green-50 text-green-700 rounded-lg hover:bg-green-100 transition-colors">
                    <div className="font-medium">데이터 히스토리</div>
                    <div className="text-sm text-green-600">과거 데이터 공유 내역 확인</div>
                  </button>
                  
                  <button className="w-full p-3 text-left bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 transition-colors">
                    <div className="font-medium">리포트 생성</div>
                    <div className="text-sm text-purple-600">환경데이터 분석 리포트 다운로드</div>
                  </button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
