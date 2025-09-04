"use client";

import React, { useState, useEffect } from 'react';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { 
  Tabs, 
  TabsContent, 
  TabsList, 
  TabsTrigger 
} from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { 
  Building2, 
  Users, 
  TrendingUp, 
  Calendar
} from 'lucide-react';
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
                    <TrendingUp className="w-6 h-6 text-green-600" />
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
                <TabsTrigger value="overview" className="data-[state=active]:bg-white data-[state=active]:shadow-sm data-[state=active]:text-blue-600 rounded-none h-full border-r border-gray-100">
                  <div className="flex flex-col items-center gap-1">
                    <TrendingUp className="w-5 h-5" />
                    <span className="text-sm font-medium">개요</span>
                  </div>
                </TabsTrigger>
                <TabsTrigger value="company-profile" className="data-[state=active]:bg-white data-[state=active]:shadow-sm data-[state=active]:text-blue-600 rounded-none h-full border-r border-gray-100">
                  <div className="flex flex-col items-center gap-1">
                    <Users className="w-5 h-5" />
                    <span className="text-sm font-medium">기업 프로필</span>
                  </div>
                </TabsTrigger>
                <TabsTrigger value="company-management" className="data-[state=active]:bg-white data-[state=active]:shadow-sm data-[state=active]:text-blue-600 rounded-none h-full border-r border-gray-100">
                  <div className="flex flex-col items-center gap-1">
                    <Building2 className="w-5 h-5" />
                    <span className="text-sm font-medium">협력사 관리</span>
                  </div>
                </TabsTrigger>
                <TabsTrigger value="supply-chain" className="data-[state=active]:bg-white data-[state=active]:shadow-sm data-[state=active]:text-blue-600 rounded-none h-full border-r border-gray-100">
                  <div className="flex flex-col items-center gap-1">
                    <TrendingUp className="w-5 h-5" />
                    <span className="text-sm font-medium">공급망 도식화</span>
                  </div>
                </TabsTrigger>
                <TabsTrigger value="settings" className="data-[state=active]:bg-white data-[state=active]:shadow-sm data-[state=active]:text-blue-600 rounded-none h-full">
                  <div className="flex flex-col items-center gap-1">
                    <Building2 className="w-5 h-5" />
                    <span className="text-sm font-medium">설정</span>
                  </div>
                </TabsTrigger>
              </TabsList>
            </div>

            {/* 이하 로직 동일 */}
            {/* ... */}
          </Tabs>
        </div>
      </div>
    </div>
  );
}
