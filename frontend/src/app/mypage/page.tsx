"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Building2, Users, TrendingUp, BarChart3, Settings, User } from 'lucide-react';
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

      const profileData = {
        ...formData,
        employee_count: formData.employee_count ? parseInt(formData.employee_count) : null,
        factory_count: formData.factory_count ? parseInt(formData.factory_count) : null,
        company_name: formData.company_name || null,
        company_type: formData.company_type || null,
        industry: formData.industry || null,
        business_number: formData.business_number || null,
        establishment_date: formData.establishment_date || null,
        annual_revenue: formData.annual_revenue || null,
        business_area: formData.business_area || null,
        factory_address: formData.factory_address || null,
        production_items: formData.production_items || null,
        department: formData.department || null,
        phone_number: formData.phone_number || null
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
    <div className="min-h-screen bg-gray-50">
    {/* Header */}
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          {/* 로고 클릭 시 main으로 이동 */}
          <button
            onClick={() => router.push('/main')}
            className="flex items-center space-x-3 hover:opacity-80 transition-opacity"
          >
            <Image 
              src="/logo.png" 
              alt="ERI Logo" 
              width={40} 
              height={40}
              className="w-10 h-10"
            />
            <h1 className="text-2xl font-bold text-gray-900">ERI</h1>
          </button>
          <div className="border-l border-gray-300 h-6"></div>
          <h2 className="text-xl font-semibold text-gray-700">마이페이지</h2>
        </div>
        
        {/* User Actions */}
        <div className="flex items-center space-x-4">
          {/* Chat */}
          <Link href="/chat">
            <Button variant="outline" className="flex items-center space-x-2">
              <span>💬</span>
              <span>챗봇</span>
            </Button>
          </Link>
          
          {/* My Page */}
          <Link href="/mypage">
            <Button variant="outline" className="flex items-center space-x-2">
              <Users className="w-4 h-4" />
              <span>마이페이지</span>
            </Button>
          </Link>
          
          {/* Profile Image */}
          <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
            <Users className="w-5 h-5 text-white" />
          </div>
        </div>
      </div>
    </header>

    {/* Main Content */}
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        {/* 기존 헤더 내용을 여기로 이동 */}
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
                  <TrendingUp className="w-8 h-8 text-orange-600" />
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
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview">개요</TabsTrigger>
            <TabsTrigger value="company-profile">기업 프로필</TabsTrigger>
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
                      <TrendingUp className="w-6 h-6 text-purple-600 mb-2" />
                      <p className="text-sm font-medium">공급망 도식화</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="company-profile">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="w-5 h-5" />
                  기업 프로필
                </CardTitle>
                <CardDescription>
                  기업 정보를 입력하고 관리할 수 있습니다.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {/* 성공 메시지 */}
                {showSuccessMessage && (
                  <div className="mb-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
                    <div className="flex items-center">
                      <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <span>프로필이 성공적으로 저장되었습니다!</span>
                    </div>
                  </div>
                )}

                <form className="space-y-6" onSubmit={handleSubmit}>
                  {/* 기업 기본 정보 */}
                  <div className="space-y-4">
                    <h2 className="text-xl font-semibold flex items-center gap-2">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                      </svg>
                      기업 기본 정보
                    </h2>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="company_name">기업명</Label>
                        <Input 
                          id="company_name" 
                          placeholder="기업명을 입력하세요" 
                          disabled={!isEditing}
                          value={formData.company_name}
                          onChange={(e) => handleInputChange('company_name', e.target.value)}
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="company_type">기업 구분</Label>
                        <Select 
                          disabled={!isEditing}
                          value={formData.company_type}
                          onValueChange={(value) => handleInputChange('company_type', value)}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="기업 구분을 선택하세요" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="협력사">협력사</SelectItem>
                            <SelectItem value="고객사">고객사</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="industry">업종</Label>
                        <Input 
                          id="industry" 
                          placeholder="업종을 입력하세요" 
                          disabled={!isEditing}
                          value={formData.industry}
                          onChange={(e) => handleInputChange('industry', e.target.value)}
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="business_number">사업자등록번호</Label>
                        <Input 
                          id="business_number" 
                          placeholder="사업자등록번호를 입력하세요" 
                          disabled={!isEditing}
                          value={formData.business_number}
                          onChange={(e) => handleInputChange('business_number', e.target.value)}
                        />
                      </div>
                    </div>
                  </div>

                  {/* 기업 상세 정보 */}
                  <div className="space-y-4">
                    <h2 className="text-xl font-semibold flex items-center gap-2">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                      기업 상세 정보
                    </h2>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="establishment_date">설립일</Label>
                        <Input 
                          id="establishment_date" 
                          type="date" 
                          disabled={!isEditing}
                          value={formData.establishment_date}
                          onChange={(e) => handleInputChange('establishment_date', e.target.value)}
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="employee_count">직원 수</Label>
                        <Input 
                          id="employee_count" 
                          type="number" 
                          placeholder="직원 수를 입력하세요" 
                          disabled={!isEditing}
                          value={formData.employee_count}
                          onChange={(e) => handleInputChange('employee_count', e.target.value)}
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="annual_revenue">연매출</Label>
                        <Input 
                          id="annual_revenue" 
                          placeholder="연매출을 입력하세요" 
                          disabled={!isEditing}
                          value={formData.annual_revenue}
                          onChange={(e) => handleInputChange('annual_revenue', e.target.value)}
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="business_area">사업 영역</Label>
                        <Input 
                          id="business_area" 
                          placeholder="사업 영역을 입력하세요" 
                          disabled={!isEditing}
                          value={formData.business_area}
                          onChange={(e) => handleInputChange('business_area', e.target.value)}
                        />
                      </div>
                    </div>
                  </div>

                  {/* 공장 정보 */}
                  <div className="space-y-4">
                    <h2 className="text-xl font-semibold flex items-center gap-2">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                      </svg>
                      공장 정보
                    </h2>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="factory_count">공장 수</Label>
                        <Input 
                          id="factory_count" 
                          type="number" 
                          placeholder="공장 수를 입력하세요" 
                          disabled={!isEditing}
                          value={formData.factory_count}
                          onChange={(e) => handleInputChange('factory_count', e.target.value)}
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="factory_address">공장 주소</Label>
                        <Input 
                          id="factory_address" 
                          placeholder="공장 주소를 입력하세요" 
                          disabled={!isEditing}
                          value={formData.factory_address}
                          onChange={(e) => handleInputChange('factory_address', e.target.value)}
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="production_items">생산 품목</Label>
                        <Textarea 
                          id="production_items" 
                          placeholder="생산 품목을 입력하세요" 
                          disabled={!isEditing}
                          value={formData.production_items}
                          onChange={(e) => handleInputChange('production_items', e.target.value)}
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="department">담당 부서</Label>
                        <Input 
                          id="department" 
                          placeholder="담당 부서를 입력하세요" 
                          disabled={!isEditing}
                          value={formData.department}
                          onChange={(e) => handleInputChange('department', e.target.value)}
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="phone_number">연락처</Label>
                        <Input 
                          id="phone_number" 
                          placeholder="연락처를 입력하세요" 
                          disabled={!isEditing}
                          value={formData.phone_number}
                          onChange={(e) => handleInputChange('phone_number', e.target.value)}
                        />
                      </div>
                    </div>
                  </div>

                  {/* 버튼 */}
                  <div className="flex justify-end space-x-4">
                    <Button 
                      type="button"
                      variant={isEditing ? "outline" : "default"}
                      onClick={() => setIsEditing(!isEditing)}
                    >
                      {isEditing ? "취소" : "프로필 수정"}
                    </Button>
                    {isEditing && (
                      <Button type="submit" disabled={loading}>
                        {loading ? "저장 중..." : "저장"}
                      </Button>
                    )}
                  </div>
                </form>
              </CardContent>
            </Card>
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
    </div>
  );
}