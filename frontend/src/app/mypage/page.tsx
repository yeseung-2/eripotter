"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Building2, Users, TrendingUp, BarChart3, Settings2, User, Plus, XCircle, Edit, Search, FileText, CheckCircle, AlertCircle, Calendar, Target } from 'lucide-react';
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
import { useStore } from "@/store/useStore";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";

interface Partner {
  id: number;
  company_name: string;
  tier1: string;
}

export default function MyPage() {
  const router = useRouter();
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
  const [partners, setPartners] = useState<Partner[]>([]);
  const [newPartnerName, setNewPartnerName] = useState("");
  const [isAddingPartner, setIsAddingPartner] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [editingPartner, setEditingPartner] = useState<Partner | null>(null);

  // 사용자 정보 (실제로는 API에서 가져와야 함)
  const mockUserInfo = {
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

  // 협력사 목록 조회 (API 호출)
  const fetchPartners = async () => {
    try {
      const response = await axios.get(`/api/monitoring/partners?company_name=${encodeURIComponent("LG에너지솔루션")}`);
      if (response.data.status === "success") {
        setPartners(response.data.data);
      } else {
        console.error("협력사 목록 조회 실패:", response.data.message);
        setPartners([]);
      }
    } catch (error) {
      console.error("협력사 목록 조회 실패:", error);
      // 오류 시 빈 배열로 설정
      setPartners([]);
    }
  };

  // 협력사 추가 (API 호출)
  const addPartner = async () => {
    if (!newPartnerName.trim()) return;
    
    setIsAddingPartner(true);
    try {
      const response = await axios.post("/api/monitoring/partners", null, {
        params: {
          company_name: "LG에너지솔루션",
          partner_name: newPartnerName.trim()
        }
      });
      
      if (response.data.status === "success") {
        // 성공 시 목록 다시 조회
        await fetchPartners();
        setNewPartnerName("");
        console.log("협력사 추가 완료:", newPartnerName.trim());
      } else {
        console.error("협력사 추가 실패:", response.data.message);
      }
    } catch (error) {
      console.error("협력사 추가 실패:", error);
    } finally {
      setIsAddingPartner(false);
    }
  };

  // 협력사 삭제 (API 호출)
  const deletePartner = async (partnerId: number) => {
    try {
      const response = await axios.delete(`/api/monitoring/partners/${partnerId}`);
      
      if (response.data.status === "success") {
        // 성공 시 목록 다시 조회
        await fetchPartners();
        console.log("협력사 삭제 완료:", partnerId);
      } else {
        console.error("협력사 삭제 실패:", response.data.message);
      }
    } catch (error) {
      console.error("협력사 삭제 실패:", error);
    }
  };

  // 협력사 수정 (API 호출)
  const updatePartner = async () => {
    if (!editingPartner || !editingPartner.tier1.trim()) return;
    
    try {
      const response = await axios.put(`/api/monitoring/partners/${editingPartner.id}`, null, {
        params: {
          partner_name: editingPartner.tier1.trim()
        }
      });
      
      if (response.data.status === "success") {
        // 성공 시 목록 다시 조회
        await fetchPartners();
        setEditingPartner(null);
        console.log("협력사 수정 완료:", editingPartner);
      } else {
        console.error("협력사 수정 실패:", response.data.message);
      }
    } catch (error) {
      console.error("협력사 수정 실패:", error);
    }
  };

  // 필터링된 협력사 목록
  const filteredPartners = partners.filter(partner =>
    partner.tier1.toLowerCase().includes(searchTerm.toLowerCase())
  );

  useEffect(() => {
    fetchPartners();
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
            <img 
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
              <FileText className="w-4 h-4" />
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
              <h1 className="text-3xl font-bold text-gray-900">{mockUserInfo.name}</h1>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant="outline">{mockUserInfo.tier}</Badge>
                <Badge variant="secondary">{mockUserInfo.role}</Badge>
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
                    <p className="text-2xl font-bold">{mockUserInfo.totalSuppliers}</p>
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
                    <p className="text-2xl font-bold">{mockUserInfo.activeRequests}</p>
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
                    <p className="text-2xl font-bold">{mockUserInfo.pendingApprovals}</p>
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
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span className="text-sm">신규 데이터 요청 5건 승인</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Users className="w-4 h-4 text-blue-500" />
                      <span className="text-sm">협력사 3곳 새로 등록</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <BarChart3 className="w-4 h-4 text-orange-500" />
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
                         <FileText className="w-6 h-6 text-blue-600 mb-2" />
                         <p className="text-sm font-medium">데이터 요청</p>
                       </div>
                     </Link>
                    
                    <Link href="/data-sharing-approval">
                      <div className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
                        <CheckCircle className="w-6 h-6 text-green-600 mb-2" />
                        <p className="text-sm font-medium">승인 관리</p>
                      </div>
                    </Link>
                    
                    <div 
                      className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                      onClick={() => setActiveTab('company-management')}
                    >
                      <Users className="w-6 h-6 text-orange-600 mb-2" />
                      <p className="text-sm font-medium">협력사 관리</p>
                    </div>
                    
                    <div 
                      className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                      onClick={() => setActiveTab('supply-chain')}
                    >
                      <Target className="w-6 h-6 text-purple-600 mb-2" />
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
                      <CheckCircle className="w-5 h-5 mr-2" />
                      <span>프로필이 성공적으로 저장되었습니다!</span>
                    </div>
                  </div>
                )}

                <form className="space-y-6" onSubmit={handleSubmit}>
                  {/* 기업 기본 정보 */}
                  <div className="space-y-4">
                    <h2 className="text-xl font-semibold flex items-center gap-2">
                      <Building2 className="h-5 w-5 text-blue-500" />
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
                      <BarChart3 className="h-5 w-5 text-green-500" />
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
                      <Target className="h-5 w-5 text-purple-500" />
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
                <div className="space-y-6">
                  {/* 협력사 추가 섹션 */}
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-medium">협력사 목록</h3>
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button>
                          <Plus className="w-4 h-4 mr-2" />
                          협력사 추가
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>새로운 협력사 추가</DialogTitle>
                          <DialogDescription>
                            하위 협력사 정보를 입력해주세요.
                          </DialogDescription>
                        </DialogHeader>
                        <div className="space-y-4">
                          <div>
                            <Label htmlFor="partner-name">협력사명</Label>
                            <Input
                              id="partner-name"
                              value={newPartnerName}
                              onChange={(e) => setNewPartnerName(e.target.value)}
                              placeholder="협력사명을 입력하세요"
                            />
                          </div>
                        </div>
                        <DialogFooter>
                          <Button
                            onClick={addPartner}
                            disabled={isAddingPartner || !newPartnerName.trim()}
                          >
                            {isAddingPartner ? "추가 중..." : "추가"}
                          </Button>
                        </DialogFooter>
                      </DialogContent>
                    </Dialog>
                  </div>

                  {/* 검색 */}
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <Input
                      placeholder="협력사명으로 검색..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>

                  {/* 협력사 목록 */}
                  {filteredPartners.length > 0 ? (
                    <div className="space-y-3">
                      {filteredPartners.map((partner) => (
                        <div
                          key={partner.id}
                          className="flex items-center justify-between p-4 border rounded-lg bg-gray-50"
                        >
                          <div className="flex items-center gap-3">
                            <Building2 className="w-5 h-5 text-blue-600" />
                            <div>
                              <p className="font-medium">{partner.tier1}</p>
                              <p className="text-sm text-gray-500">하위 협력사</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Dialog>
                              <DialogTrigger asChild>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => setEditingPartner(partner)}
                                >
                                                                     <Edit className="w-4 h-4" />
                                </Button>
                              </DialogTrigger>
                              <DialogContent>
                                <DialogHeader>
                                  <DialogTitle>협력사 정보 수정</DialogTitle>
                                  <DialogDescription>
                                    협력사명을 수정할 수 있습니다.
                                  </DialogDescription>
                                </DialogHeader>
                                <div className="space-y-4">
                                  <div>
                                    <Label htmlFor="edit-partner-name">협력사명</Label>
                                    <Input
                                      id="edit-partner-name"
                                      value={editingPartner?.tier1 || ""}
                                      onChange={(e) => setEditingPartner(prev => 
                                        prev ? { ...prev, tier1: e.target.value } : null
                                      )}
                                      placeholder="협력사명을 입력하세요"
                                    />
                                  </div>
                                </div>
                                <DialogFooter>
                                  <Button
                                    onClick={updatePartner}
                                    disabled={!editingPartner?.tier1.trim()}
                                  >
                                    수정
                                  </Button>
                                </DialogFooter>
                              </DialogContent>
                            </Dialog>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => deletePartner(partner.id)}
                              className="text-red-600 hover:text-red-700"
                            >
                                                             <XCircle className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-12">
                      <Building2 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        {searchTerm ? "검색 결과가 없습니다" : "등록된 협력사가 없습니다"}
                      </h3>
                      <p className="text-gray-600">
                        {searchTerm 
                          ? "다른 검색어를 시도해보세요."
                          : "협력사 추가 버튼을 눌러 첫 번째 협력사를 등록해보세요."
                        }
                      </p>
                    </div>
                  )}
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
                  <Settings2 className="w-5 h-5" />
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
                        <span className="text-sm font-medium">{mockUserInfo.name}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">계층</span>
                        <Badge variant="outline">{mockUserInfo.tier}</Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">역할</span>
                        <Badge variant="secondary">{mockUserInfo.role}</Badge>
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