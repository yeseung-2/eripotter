"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Building2, Users, TrendingUp, BarChart3, Cog, User, Calendar, MapPin, Phone, Mail, Globe, Shield, Activity } from 'lucide-react';
import Link from 'next/link';
import SupplyChainVisualizationPage from '@/components/SupplyChainVisualizationPage';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import axios from '@/lib/axios';

export default function MyPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [isEditing, setIsEditing] = useState(false);
  const [showSuccessMessage, setShowSuccessMessage] = useState(false);
  const [loading, setLoading] = useState(false);
  const [oauthSub, setOauthSub] = useState<string>('');
  const [formData, setFormData] = useState({
    company_name: '',
    company_type: '',
    industry: '',
    business_number: '',
    establishment_date: '',
    employee_count: '',
    annual_revenue: '',
    business_area: '',
    factory_count: '',
    factory_address: '',
    production_items: '',
    department: '',
    phone_number: ''
  });

  // 사용자 정보 (실제로는 API에서 가져와야 함)
  const userInfo = {
    name: "LG에너지솔루션",
    tier: "원청사",
    role: "플랫폼 관리자",
    totalSuppliers: 24,
    activeRequests: 12,
    pendingApprovals: 8
  };

  // JWT 토큰에서 oauth_sub 추출하는 함수
  const extractOauthSubFromToken = (token: string) => {
    try {
      const payload = token.split('.')[1];
      const decodedPayload = JSON.parse(atob(payload));
      console.log('JWT Payload:', decodedPayload);
      return decodedPayload.oauth_sub;
    } catch (error) {
      console.error('JWT 토큰 파싱 실패:', error);
      return null;
    }
  };

  // 프로필 데이터 로드
  useEffect(() => {
    const loadProfile = async () => {
      try {
        let oauth_sub = '';
        if (typeof window !== 'undefined') {
          oauth_sub = localStorage.getItem('oauth_sub') || '';
        }
        
        if (!oauth_sub) {
          console.log('OAuth sub가 없습니다. 로그인이 필요합니다.');
          return;
        }
        setOauthSub(oauth_sub);

        const response = await axios.get(`/api/account/accounts/me?oauth_sub=${oauth_sub}`);
        if (response.data) {
          const profile = response.data;
          console.log('로드된 프로필 데이터:', profile);
          setFormData({
            company_name: profile.company_name || '',
            company_type: profile.company_type || '',
            industry: profile.industry || '',
            business_number: profile.business_number || '',
            establishment_date: profile.establishment_date || '',
            employee_count: profile.employee_count?.toString() || '',
            annual_revenue: profile.annual_revenue || '',
            business_area: profile.business_area || '',
            factory_count: profile.factory_count?.toString() || '',
            factory_address: profile.factory_address || '',
            production_items: profile.production_items || '',
            department: profile.department || '',
            phone_number: profile.phone_number || ''
          });
        }
      } catch (error) {
        console.error('프로필 로드 실패:', error);
      }
    };

    loadProfile();
  }, []);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    setLoading(true);
    try {
      let oauth_sub = '';
      if (typeof window !== 'undefined') {
        oauth_sub = localStorage.getItem('oauth_sub') || '';
      }
      
      if (!oauth_sub) {
        alert('로그인이 필요합니다.');
        return;
      }

      // 빈 문자열을 null로 변환하는 함수
      const cleanValue = (value: string) => {
        if (value === undefined || value === null || value.trim() === '') {
          return null;
        }
        return value.trim();
      };

      const profileData = {
        company_name: cleanValue(formData.company_name),
        company_type: cleanValue(formData.company_type),
        industry: cleanValue(formData.industry),
        business_number: cleanValue(formData.business_number),
        establishment_date: cleanValue(formData.establishment_date),
        employee_count: formData.employee_count ? parseInt(formData.employee_count) : null,
        annual_revenue: cleanValue(formData.annual_revenue),
        business_area: cleanValue(formData.business_area),
        factory_count: formData.factory_count ? parseInt(formData.factory_count) : null,
        factory_address: cleanValue(formData.factory_address),
        production_items: cleanValue(formData.production_items),
        department: cleanValue(formData.department),
        phone_number: cleanValue(formData.phone_number)
      };

      console.log('저장할 프로필 데이터:', profileData);
      await axios.post(`/api/account/accounts/profile?oauth_sub=${oauth_sub}`, profileData);
      
      setShowSuccessMessage(true);
      setIsEditing(false);
      setTimeout(() => setShowSuccessMessage(false), 3000);
    } catch (error) {
      console.error('프로필 저장 실패:', error);
      alert('프로필 저장에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 헤더 섹션 */}
        <div className="mb-12">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 mb-8">
            <div className="flex flex-col lg:flex-row items-start lg:items-center gap-6">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-600 to-blue-700 rounded-2xl flex items-center justify-center shadow-lg">
                <Building2 className="w-10 h-10 text-white" />
              </div>
              <div className="flex-1">
                <h1 className="text-4xl font-bold text-gray-900 mb-3">{userInfo.name}</h1>
                <div className="flex flex-wrap items-center gap-3">
                  <Badge className="bg-blue-100 text-blue-800 border-blue-200 px-3 py-1 text-sm font-medium">
                    {userInfo.tier}
                  </Badge>
                  <Badge className="bg-green-100 text-green-800 border-green-200 px-3 py-1 text-sm font-medium">
                    {userInfo.role}
                  </Badge>
                </div>
              </div>
            </div>
          </div>
          
          {/* 통계 카드 */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="bg-white border-0 shadow-sm hover:shadow-md transition-all duration-300 rounded-xl">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                    <Users className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">총 협력사 수</p>
                    <p className="text-3xl font-bold text-gray-900">{userInfo.totalSuppliers}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-white border-0 shadow-sm hover:shadow-md transition-all duration-300 rounded-xl">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                    <BarChart3 className="w-6 h-6 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">활성 요청</p>
                    <p className="text-3xl font-bold text-gray-900">{userInfo.activeRequests}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-white border-0 shadow-sm hover:shadow-md transition-all duration-300 rounded-xl">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center">
                    <TrendingUp className="w-6 h-6 text-orange-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">승인 대기</p>
                    <p className="text-3xl font-bold text-gray-900">{userInfo.pendingApprovals}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* 메인 콘텐츠 */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <div className="border-b border-gray-100 bg-gray-50/50">
              <TabsList className="grid w-full grid-cols-5 h-16 bg-transparent border-0 p-0">
                <TabsTrigger 
                  value="overview" 
                  className="data-[state=active]:bg-white data-[state=active]:shadow-sm data-[state=active]:text-blue-600 rounded-none h-full border-r border-gray-100"
                >
                  <div className="flex flex-col items-center gap-1">
                    <Activity className="w-5 h-5" />
                    <span className="text-sm font-medium">개요</span>
                  </div>
                </TabsTrigger>
                <TabsTrigger 
                  value="company-profile" 
                  className="data-[state=active]:bg-white data-[state=active]:shadow-sm data-[state=active]:text-blue-600 rounded-none h-full border-r border-gray-100"
                >
                  <div className="flex flex-col items-center gap-1">
                    <User className="w-5 h-5" />
                    <span className="text-sm font-medium">기업 프로필</span>
                  </div>
                </TabsTrigger>
                <TabsTrigger 
                  value="company-management" 
                  className="data-[state=active]:bg-white data-[state=active]:shadow-sm data-[state=active]:text-blue-600 rounded-none h-full border-r border-gray-100"
                >
                  <div className="flex flex-col items-center gap-1">
                    <Building2 className="w-5 h-5" />
                    <span className="text-sm font-medium">협력사 관리</span>
                  </div>
                </TabsTrigger>
                <TabsTrigger 
                  value="supply-chain" 
                  className="data-[state=active]:bg-white data-[state=active]:shadow-sm data-[state=active]:text-blue-600 rounded-none h-full border-r border-gray-100"
                >
                  <div className="flex flex-col items-center gap-1">
                    <TrendingUp className="w-5 h-5" />
                    <span className="text-sm font-medium">공급망 도식화</span>
                  </div>
                </TabsTrigger>
                <TabsTrigger 
                  value="settings" 
                  className="data-[state=active]:bg-white data-[state=active]:shadow-sm data-[state=active]:text-blue-600 rounded-none h-full"
                >
                  <div className="flex flex-col items-center gap-1">
                    <Cog className="w-5 h-5" />
                    <span className="text-sm font-medium">설정</span>
                  </div>
                </TabsTrigger>
              </TabsList>
            </div>

            <div className="p-8">
              <TabsContent value="overview" className="space-y-8 mt-0">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  <Card className="border-0 shadow-sm bg-gradient-to-br from-blue-50 to-indigo-50">
                    <CardHeader className="pb-4">
                      <CardTitle className="flex items-center gap-2 text-gray-900">
                        <Activity className="w-5 h-5 text-blue-600" />
                        최근 활동
                      </CardTitle>
                      <CardDescription className="text-gray-600">지난 7일간의 주요 활동 요약</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div className="flex items-center gap-3 p-3 bg-white/60 rounded-lg">
                          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                          <span className="text-sm font-medium text-gray-700">신규 데이터 요청 5건 승인</span>
                        </div>
                        <div className="flex items-center gap-3 p-3 bg-white/60 rounded-lg">
                          <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                          <span className="text-sm font-medium text-gray-700">협력사 3곳 새로 등록</span>
                        </div>
                        <div className="flex items-center gap-3 p-3 bg-white/60 rounded-lg">
                          <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                          <span className="text-sm font-medium text-gray-700">환경 데이터 8건 업데이트</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="border-0 shadow-sm bg-gradient-to-br from-green-50 to-emerald-50">
                    <CardHeader className="pb-4">
                      <CardTitle className="flex items-center gap-2 text-gray-900">
                        <TrendingUp className="w-5 h-5 text-green-600" />
                        빠른 작업
                      </CardTitle>
                      <CardDescription className="text-gray-600">자주 사용하는 기능들</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 gap-4">
                        <Link href="/data-sharing-request">
                          <div className="p-4 bg-white/60 rounded-xl hover:bg-white/80 cursor-pointer transition-all duration-200 border border-white/20 hover:border-white/40">
                            <BarChart3 className="w-8 h-8 text-blue-600 mb-3" />
                            <p className="text-sm font-semibold text-gray-800">데이터 요청</p>
                          </div>
                        </Link>
                        
                        <Link href="/data-sharing-approval">
                          <div className="p-4 bg-white/60 rounded-xl hover:bg-white/80 cursor-pointer transition-all duration-200 border border-white/20 hover:border-white/40">
                            <Users className="w-8 h-8 text-green-600 mb-3" />
                            <p className="text-sm font-semibold text-gray-800">승인 관리</p>
                          </div>
                        </Link>
                        
                        <div 
                          className="p-4 bg-white/60 rounded-xl hover:bg-white/80 cursor-pointer transition-all duration-200 border border-white/20 hover:border-white/40"
                          onClick={() => setActiveTab('company-management')}
                        >
                          <Building2 className="w-8 h-8 text-orange-600 mb-3" />
                          <p className="text-sm font-semibold text-gray-800">협력사 관리</p>
                        </div>
                        
                        <div 
                          className="p-4 bg-white/60 rounded-xl hover:bg-white/80 cursor-pointer transition-all duration-200 border border-white/20 hover:border-white/40"
                          onClick={() => setActiveTab('supply-chain')}
                        >
                          <TrendingUp className="w-8 h-8 text-purple-600 mb-3" />
                          <p className="text-sm font-semibold text-gray-800">공급망 도식화</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="company-profile" className="mt-0">
                {/* 성공 메시지 */}
                {showSuccessMessage && (
                  <div className="mb-6 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 text-green-800 px-6 py-4 rounded-xl">
                    <div className="flex items-center">
                      <div className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center mr-3">
                        <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                      <span className="font-medium">프로필이 성공적으로 저장되었습니다!</span>
                    </div>
                  </div>
                )}

                <form className="space-y-8" onSubmit={handleSubmit}>
                  {/* 기업 기본 정보 */}
                  <div className="space-y-6">
                    <div className="flex items-center gap-3 pb-4 border-b border-gray-200">
                      <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
                        <Building2 className="w-5 h-5 text-blue-600" />
                      </div>
                      <h2 className="text-xl font-semibold text-gray-900">기업 기본 정보</h2>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <Label htmlFor="company_name" className="text-sm font-medium text-gray-700">기업명</Label>
                        <Input 
                          id="company_name" 
                          placeholder="기업명을 입력하세요" 
                          disabled={!isEditing}
                          value={formData.company_name}
                          onChange={(e) => handleInputChange('company_name', e.target.value)}
                          className="h-11 border-gray-200 focus:border-blue-500 focus:ring-blue-500/20 rounded-lg"
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="industry" className="text-sm font-medium text-gray-700">업종</Label>
                        <Input 
                          id="industry" 
                          placeholder="업종을 입력하세요" 
                          disabled={!isEditing}
                          value={formData.industry}
                          onChange={(e) => handleInputChange('industry', e.target.value)}
                          className="h-11 border-gray-200 focus:border-blue-500 focus:ring-blue-500/20 rounded-lg"
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="business_number" className="text-sm font-medium text-gray-700">사업자등록번호</Label>
                        <Input 
                          id="business_number" 
                          placeholder="사업자등록번호를 입력하세요" 
                          disabled={!isEditing}
                          value={formData.business_number}
                          onChange={(e) => handleInputChange('business_number', e.target.value)}
                          className="h-11 border-gray-200 focus:border-blue-500 focus:ring-blue-500/20 rounded-lg"
                        />
                      </div>
                    </div>
                  </div>

                  {/* 기업 상세 정보 */}
                  <div className="space-y-6">
                    <div className="flex items-center gap-3 pb-4 border-b border-gray-200">
                      <div className="w-10 h-10 bg-green-100 rounded-xl flex items-center justify-center">
                        <BarChart3 className="w-5 h-5 text-green-600" />
                      </div>
                      <h2 className="text-xl font-semibold text-gray-900">기업 상세 정보</h2>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <Label htmlFor="establishment_date" className="text-sm font-medium text-gray-700">설립일</Label>
                        <Input 
                          id="establishment_date" 
                          type="date" 
                          disabled={!isEditing}
                          value={formData.establishment_date}
                          onChange={(e) => handleInputChange('establishment_date', e.target.value)}
                          className="h-11 border-gray-200 focus:border-blue-500 focus:ring-blue-500/20 rounded-lg"
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="employee_count" className="text-sm font-medium text-gray-700">직원 수</Label>
                        <Input 
                          id="employee_count" 
                          type="number" 
                          placeholder="직원 수를 입력하세요" 
                          disabled={!isEditing}
                          value={formData.employee_count}
                          onChange={(e) => handleInputChange('employee_count', e.target.value)}
                          className="h-11 border-gray-200 focus:border-blue-500 focus:ring-blue-500/20 rounded-lg"
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="annual_revenue" className="text-sm font-medium text-gray-700">연매출</Label>
                        <Input 
                          id="annual_revenue" 
                          placeholder="연매출을 입력하세요" 
                          disabled={!isEditing}
                          value={formData.annual_revenue}
                          onChange={(e) => handleInputChange('annual_revenue', e.target.value)}
                          className="h-11 border-gray-200 focus:border-blue-500 focus:ring-blue-500/20 rounded-lg"
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="business_area" className="text-sm font-medium text-gray-700">사업 영역</Label>
                        <Input 
                          id="business_area" 
                          placeholder="사업 영역을 입력하세요" 
                          disabled={!isEditing}
                          value={formData.business_area}
                          onChange={(e) => handleInputChange('business_area', e.target.value)}
                          className="h-11 border-gray-200 focus:border-blue-500 focus:ring-blue-500/20 rounded-lg"
                        />
                      </div>
                    </div>
                  </div>

                  {/* 공장 정보 */}
                  <div className="space-y-6">
                    <div className="flex items-center gap-3 pb-4 border-b border-gray-200">
                      <div className="w-10 h-10 bg-purple-100 rounded-xl flex items-center justify-center">
                        <MapPin className="w-5 h-5 text-purple-600" />
                      </div>
                      <h2 className="text-xl font-semibold text-gray-900">공장 정보</h2>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <Label htmlFor="factory_count" className="text-sm font-medium text-gray-700">공장 수</Label>
                        <Input 
                          id="factory_count" 
                          type="number" 
                          placeholder="공장 수를 입력하세요" 
                          disabled={!isEditing}
                          value={formData.factory_count}
                          onChange={(e) => handleInputChange('factory_count', e.target.value)}
                          className="h-11 border-gray-200 focus:border-blue-500 focus:ring-blue-500/20 rounded-lg"
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="factory_address" className="text-sm font-medium text-gray-700">공장 주소</Label>
                        <Input 
                          id="factory_address" 
                          placeholder="공장 주소를 입력하세요" 
                          disabled={!isEditing}
                          value={formData.factory_address}
                          onChange={(e) => handleInputChange('factory_address', e.target.value)}
                          className="h-11 border-gray-200 focus:border-blue-500 focus:ring-blue-500/20 rounded-lg"
                        />
                      </div>
                      
                      <div className="space-y-2 md:col-span-2">
                        <Label htmlFor="production_items" className="text-sm font-medium text-gray-700">생산 품목</Label>
                        <Textarea 
                          id="production_items" 
                          placeholder="생산 품목을 입력하세요" 
                          disabled={!isEditing}
                          value={formData.production_items}
                          onChange={(e) => handleInputChange('production_items', e.target.value)}
                          className="border-gray-200 focus:border-blue-500 focus:ring-blue-500/20 rounded-lg resize-none"
                          rows={3}
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="department" className="text-sm font-medium text-gray-700">담당 부서</Label>
                        <Input 
                          id="department" 
                          placeholder="담당 부서를 입력하세요" 
                          disabled={!isEditing}
                          value={formData.department}
                          onChange={(e) => handleInputChange('department', e.target.value)}
                          className="h-11 border-gray-200 focus:border-blue-500 focus:ring-blue-500/20 rounded-lg"
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="phone_number" className="text-sm font-medium text-gray-700">연락처</Label>
                        <Input 
                          id="phone_number" 
                          placeholder="연락처를 입력하세요" 
                          disabled={!isEditing}
                          value={formData.phone_number}
                          onChange={(e) => handleInputChange('phone_number', e.target.value)}
                          className="h-11 border-gray-200 focus:border-blue-500 focus:ring-blue-500/20 rounded-lg"
                        />
                      </div>
                    </div>
                  </div>

                  {/* 버튼 */}
                  <div className="flex justify-end space-x-4 pt-6 border-t border-gray-200">
                    <Button 
                      type="button"
                      variant={isEditing ? "outline" : "default"}
                      onClick={() => setIsEditing(!isEditing)}
                      className="px-6 py-2 rounded-lg"
                    >
                      {isEditing ? "취소" : "프로필 수정"}
                    </Button>
                    {isEditing && (
                      <Button type="submit" disabled={loading} className="px-6 py-2 rounded-lg bg-blue-600 hover:bg-blue-700">
                        {loading ? "저장 중..." : "저장"}
                      </Button>
                    )}
                  </div>
                </form>
              </TabsContent>

              <TabsContent value="company-management" className="mt-0">
                <Card className="border-0 shadow-sm bg-gradient-to-br from-orange-50 to-amber-50">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-gray-900">
                      <Building2 className="w-5 h-5 text-orange-600" />
                      협력사 목록 관리
                    </CardTitle>
                    <CardDescription className="text-gray-600">
                      하위 협력사 정보를 관리하고 데이터 공유 현황을 확인할 수 있습니다.
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="text-center py-16">
                      <div className="w-20 h-20 bg-orange-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                        <Building2 className="w-10 h-10 text-orange-600" />
                      </div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-3">협력사 관리 기능 구현 중</h3>
                      <p className="text-gray-600 max-w-md mx-auto">
                        곧 하위 협력사 목록 조회, 편집, 데이터 공유 현황 등을 관리할 수 있습니다.
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="supply-chain" className="mt-0">
                <SupplyChainVisualizationPage />
              </TabsContent>

              <TabsContent value="settings" className="mt-0">
                <Card className="border-0 shadow-sm bg-gradient-to-br from-gray-50 to-slate-50">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-gray-900">
                      <Cog className="w-5 h-5 text-gray-600" />
                      설정
                    </CardTitle>
                    <CardDescription className="text-gray-600">
                      계정 및 시스템 설정을 관리합니다.
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-8">
                      <div>
                        <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                          <Shield className="w-5 h-5 text-blue-600" />
                          계정 정보
                        </h4>
                        <div className="space-y-4">
                          <div className="flex justify-between items-center p-4 bg-white/60 rounded-lg">
                            <span className="text-sm font-medium text-gray-700">회사명</span>
                            <span className="text-sm font-semibold text-gray-900">{userInfo.name}</span>
                          </div>
                          <div className="flex justify-between items-center p-4 bg-white/60 rounded-lg">
                            <span className="text-sm font-medium text-gray-700">계층</span>
                            <Badge className="bg-blue-100 text-blue-800 border-blue-200 px-3 py-1">
                              {userInfo.tier}
                            </Badge>
                          </div>
                          <div className="flex justify-between items-center p-4 bg-white/60 rounded-lg">
                            <span className="text-sm font-medium text-gray-700">역할</span>
                            <Badge className="bg-green-100 text-green-800 border-green-200 px-3 py-1">
                              {userInfo.role}
                            </Badge>
                          </div>
                        </div>
                      </div>
                      
                      <div className="border-t border-gray-200 pt-8">
                        <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                          <Activity className="w-5 h-5 text-green-600" />
                          알림 설정
                        </h4>
                        <div className="space-y-4">
                          <div className="flex justify-between items-center p-4 bg-white/60 rounded-lg">
                            <span className="text-sm font-medium text-gray-700">데이터 요청 알림</span>
                            <Badge className="bg-green-100 text-green-800 border-green-200 px-3 py-1">
                              활성
                            </Badge>
                          </div>
                          <div className="flex justify-between items-center p-4 bg-white/60 rounded-lg">
                            <span className="text-sm font-medium text-gray-700">승인 알림</span>
                            <Badge className="bg-green-100 text-green-800 border-green-200 px-3 py-1">
                              활성
                            </Badge>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </div>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
