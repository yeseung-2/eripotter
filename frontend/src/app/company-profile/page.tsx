'use client';

import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import Link from "next/link";
import { useState, useEffect } from "react";
import axios from '@/lib/axios';
import { useAuthStore } from '@/store/useStore';

export default function CompanyProfilePage() {
  const { user } = useAuthStore();
  const [isEditing, setIsEditing] = useState(false);
  const [showSuccessMessage, setShowSuccessMessage] = useState(false);
  const [loading, setLoading] = useState(false);
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

  // URL에서 토큰 가져오기 (useSearchParams 대신 window.location.search 사용)
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search);
      const token = urlParams.get('token');
      if (token) {
        // 토큰을 localStorage에 저장
        localStorage.setItem('access_token', token);
        console.log('Token saved:', token);
        setShowSuccessMessage(true);
        // 3초 후 메시지 숨기기
        setTimeout(() => setShowSuccessMessage(false), 3000);
      }
    }
  }, []);

  // 기존 프로필 데이터 로드
  useEffect(() => {
    const loadProfile = async () => {
      // user가 없어도 account 테이블에서 데이터를 가져올 수 있도록 수정
      try {
        // localStorage에서 oauth_sub 가져오기 (Google OAuth 로그인 시 저장됨)
        const oauth_sub = localStorage.getItem('oauth_sub');
        if (!oauth_sub) {
          console.log('OAuth sub가 없습니다. 로그인이 필요합니다.');
          return;
        }

        const response = await axios.get(`/api/account/me?oauth_sub=${oauth_sub}`);
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
      // localStorage에서 oauth_sub 가져오기
      const oauth_sub = localStorage.getItem('oauth_sub');
      if (!oauth_sub) {
        alert('로그인이 필요합니다.');
        return;
      }

      const profileData = {
        ...formData,
        employee_count: formData.employee_count ? parseInt(formData.employee_count) : null,
        factory_count: formData.factory_count ? parseInt(formData.factory_count) : null
      };

      console.log('저장할 프로필 데이터:', profileData);
      await axios.put(`/api/account/me/profile?oauth_sub=${oauth_sub}`, profileData);
      
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
    <div className="container mx-auto py-8 px-4">
      {/* 성공 메시지 */}
      {showSuccessMessage && (
        <div className="mb-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
          <div className="flex items-center">
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span>로그인이 성공했습니다! 이제 회사 정보를 입력해주세요.</span>
          </div>
        </div>
      )}
      
      {/* 상단 서비스 네비게이션 */}
      <div className="mb-8 bg-white rounded-xl shadow-lg p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* AI 상담 */}
          <Link href="/chat" className="group">
            <Card className="hover:shadow-md transition-all cursor-pointer h-full">
              <CardContent className="p-6 flex flex-col items-center text-center">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-4 group-hover:bg-blue-200 transition-colors">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold mb-2">AI 상담</h3>
                <p className="text-sm text-gray-600">생산성 향상을 위한 AI 전문가와 상담하세요</p>
              </CardContent>
            </Card>
          </Link>

          {/* 생산성 자가진단 */}
          <Link href="/assessment" className="group">
            <Card className="hover:shadow-md transition-all cursor-pointer h-full">
              <CardContent className="p-6 flex flex-col items-center text-center">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-4 group-hover:bg-green-200 transition-colors">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold mb-2">자가진단</h3>
                <p className="text-sm text-gray-600">곻급망 실사 대응</p>
              </CardContent>
            </Card>
          </Link>

          {/* 데이터 업로드 */}
          <Link href="/data-upload" className="group">
            <Card className="hover:shadow-md transition-all cursor-pointer h-full">
              <CardContent className="p-6 flex flex-col items-center text-center">
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mb-4 group-hover:bg-purple-200 transition-colors">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold mb-2">데이터 업로드</h3>
                <p className="text-sm text-gray-600">생산성 분석을 위한 데이터를 업로드하세요</p>
              </CardContent>
            </Card>
          </Link>
        </div>
      </div>

      {/* 기업 프로필 카드 */}
      <Card className="mb-8">
        <CardContent className="pt-6">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-2xl font-bold">기업 프로필</h1>
            <Button 
              variant={isEditing ? "outline" : "default"}
              onClick={() => setIsEditing(!isEditing)}
            >
              {isEditing ? "취소" : "프로필 수정"}
            </Button>
          </div>

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
                      <SelectValue placeholder="기업 구분 선택" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="startup">스타트업</SelectItem>
                      <SelectItem value="sme">중소기업</SelectItem>
                      <SelectItem value="large">대기업</SelectItem>
                      <SelectItem value="public">공공기관</SelectItem>
                      <SelectItem value="other">기타</SelectItem>
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
                  <Label htmlFor="business_number">사업자 등록 번호</Label>
                  <Input 
                    id="business_number" 
                    placeholder="000-00-00000" 
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
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
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
                  <Label htmlFor="employee_count">종업원 수</Label>
                  <Input 
                    id="employee_count" 
                    type="number" 
                    placeholder="0" 
                    disabled={!isEditing}
                    value={formData.employee_count}
                    onChange={(e) => handleInputChange('employee_count', e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="annual_revenue">연간 매출액</Label>
                  <Input 
                    id="annual_revenue" 
                    placeholder="예: 1000만원" 
                    disabled={!isEditing}
                    value={formData.annual_revenue}
                    onChange={(e) => handleInputChange('annual_revenue', e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="business_area">사업 분야</Label>
                  <Input 
                    id="business_area" 
                    placeholder="주요 사업 분야를 입력하세요" 
                    disabled={!isEditing}
                    value={formData.business_area}
                    onChange={(e) => handleInputChange('business_area', e.target.value)}
                  />
                </div>
              </div>
            </div>

            {/* 생산공장 정보 */}
            <div className="space-y-4">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
                생산공장 정보
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="factory_count">생산공장 수</Label>
                  <Input 
                    id="factory_count" 
                    type="number" 
                    placeholder="0" 
                    disabled={!isEditing}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="factory_address">주요 생산공장 위치</Label>
                  <Input 
                    id="factory_address" 
                    placeholder="주요 생산공장 주소를 입력하세요" 
                    disabled={!isEditing}
                  />
                </div>

                <div className="col-span-2 space-y-2">
                  <Label htmlFor="production_items">주요 생산품목</Label>
                  <Textarea 
                    id="production_items" 
                    placeholder="주요 생산품목을 입력하세요" 
                    disabled={!isEditing}
                  />
                </div>
              </div>
            </div>

            {/* 담당자 정보 */}
            <div className="space-y-4">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                담당자 정보
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="department">부서/직책</Label>
                  <Input 
                    id="department" 
                    placeholder="부서와 직책을 입력하세요" 
                    disabled={!isEditing}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone_number">연락처</Label>
                  <Input 
                    id="phone_number" 
                    placeholder="000-0000-0000" 
                    disabled={!isEditing}
                  />
                </div>
              </div>
            </div>

            {/* 저장 버튼 */}
            {isEditing && (
              <div className="flex justify-end space-x-4">
                <Button 
                  type="submit" 
                  className="bg-blue-600 hover:bg-blue-700"
                  disabled={loading}
                >
                  {loading ? '저장 중...' : '변경사항 저장'}
                </Button>
              </div>
            )}
          </form>
        </CardContent>
      </Card>
    </div>
  );
}