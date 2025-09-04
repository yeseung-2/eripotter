"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Building2, 
  Search, 
  Filter, 
  MoreVertical, 
  Star, 
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Clock,
  Users,
  BarChart3,
  Network
} from 'lucide-react';

interface Company {
  id: string;
  name: string;
  tier: string;
  industry: string;
  isStrategic: boolean;
  status: 'active' | 'pending' | 'inactive';
  dataSharing: {
    totalRequests: number;
    approvedRequests: number;
    pendingRequests: number;
    rejectedRequests: number;
    lastRequest: string;
  };
  environmentalScore: number;
  lastContact: string;
  relationship: string;
}

export default function CompanyManagementPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'pending' | 'inactive'>('all');
  const [sortBy, setSortBy] = useState<'name' | 'score' | 'lastContact'>('name');

  // Mock data - 실제로는 API에서 가져와야 함
  useEffect(() => {
    const mockCompanies: Company[] = [
      {
        id: '1',
        name: '엔팜',
        tier: '2차사',
        industry: '화학소재',
        isStrategic: true,
        status: 'active',
        dataSharing: {
          totalRequests: 24,
          approvedRequests: 20,
          pendingRequests: 2,
          rejectedRequests: 2,
          lastRequest: '2024-08-30'
        },
        environmentalScore: 85,
        lastContact: '2024-08-30',
        relationship: 'direct'
      },
      {
        id: '2',
        name: '코스모신소재',
        tier: '2차사',
        industry: '전자소재',
        isStrategic: false,
        status: 'active',
        dataSharing: {
          totalRequests: 18,
          approvedRequests: 15,
          pendingRequests: 1,
          rejectedRequests: 2,
          lastRequest: '2024-08-29'
        },
        environmentalScore: 72,
        lastContact: '2024-08-29',
        relationship: 'direct'
      },
      {
        id: '3',
        name: '에코머티리얼',
        tier: '3차사',
        industry: '원료공급',
        isStrategic: true,
        status: 'pending',
        dataSharing: {
          totalRequests: 8,
          approvedRequests: 6,
          pendingRequests: 2,
          rejectedRequests: 0,
          lastRequest: '2024-08-28'
        },
        environmentalScore: 91,
        lastContact: '2024-08-28',
        relationship: 'indirect'
      },
      {
        id: '4',
        name: '그린테크솔루션',
        tier: '2차사',
        industry: '재활용',
        isStrategic: false,
        status: 'active',
        dataSharing: {
          totalRequests: 12,
          approvedRequests: 10,
          pendingRequests: 0,
          rejectedRequests: 2,
          lastRequest: '2024-08-27'
        },
        environmentalScore: 78,
        lastContact: '2024-08-27',
        relationship: 'direct'
      }
    ];
    setCompanies(mockCompanies);
  }, []);

  const filteredCompanies = companies
    .filter(company => 
      company.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      company.industry.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .filter(company => filterStatus === 'all' || company.status === filterStatus)
    .sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'score':
          return b.environmentalScore - a.environmentalScore;
        case 'lastContact':
          return new Date(b.lastContact).getTime() - new Date(a.lastContact).getTime();
        default:
          return 0;
      }
    });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-100 text-green-800">활성</Badge>;
      case 'pending':
        return <Badge className="bg-yellow-100 text-yellow-800">대기</Badge>;
      case 'inactive':
        return <Badge className="bg-gray-100 text-gray-800">비활성</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const toggleStrategic = (companyId: string) => {
    setCompanies(prev => 
      prev.map(company => 
        company.id === companyId 
          ? { ...company, isStrategic: !company.isStrategic }
          : company
      )
    );
  };

  // 통계 계산
  const stats = {
    total: companies.length,
    strategic: companies.filter(c => c.isStrategic).length,
    active: companies.filter(c => c.status === 'active').length,
    avgScore: Math.round(companies.reduce((sum, c) => sum + c.environmentalScore, 0) / companies.length || 0)
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* 헤더 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">고객사 목록 관리</h1>
          <p className="text-gray-600">협력사 정보와 데이터 공유 현황을 관리합니다.</p>
        </div>

        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <Building2 className="w-8 h-8 text-blue-600" />
                <div>
                  <p className="text-sm text-gray-600">총 협력사</p>
                  <p className="text-2xl font-bold">{stats.total}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <Star className="w-8 h-8 text-yellow-600" />
                <div>
                  <p className="text-sm text-gray-600">핵심 협력사</p>
                  <p className="text-2xl font-bold">{stats.strategic}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <CheckCircle className="w-8 h-8 text-green-600" />
                <div>
                  <p className="text-sm text-gray-600">활성 협력사</p>
                  <p className="text-2xl font-bold">{stats.active}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <BarChart3 className="w-8 h-8 text-purple-600" />
                <div>
                  <p className="text-sm text-gray-600">평균 환경점수</p>
                  <p className="text-2xl font-bold">{stats.avgScore}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 검색 및 필터 */}
        <Card className="mb-6">
          <CardContent className="p-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="협력사명 또는 업종으로 검색..."
                  className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              
              <div className="flex gap-2">
                <select
                  className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value as any)}
                >
                  <option value="all">모든 상태</option>
                  <option value="active">활성</option>
                  <option value="pending">대기</option>
                  <option value="inactive">비활성</option>
                </select>
                
                <select
                  className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                >
                  <option value="name">이름순</option>
                  <option value="score">환경점수순</option>
                  <option value="lastContact">최근연락순</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 협력사 목록 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredCompanies.map((company) => (
            <Card key={company.id} className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                      <Building2 className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{company.name}</CardTitle>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="outline">{company.tier}</Badge>
                        {getStatusBadge(company.status)}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => toggleStrategic(company.id)}
                      className={`p-1 rounded ${
                        company.isStrategic 
                          ? 'text-yellow-500 hover:text-yellow-600' 
                          : 'text-gray-300 hover:text-yellow-500'
                      }`}
                    >
                      <Star className={`w-5 h-5 ${company.isStrategic ? 'fill-current' : ''}`} />
                    </button>
                    <button className="p-1 text-gray-400 hover:text-gray-600">
                      <MoreVertical className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm text-gray-600 mb-1">업종</p>
                  <p className="font-medium">{company.industry}</p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-600 mb-2">환경 점수</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          company.environmentalScore >= 80 ? 'bg-green-500' :
                          company.environmentalScore >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${company.environmentalScore}%` }}
                      />
                    </div>
                    <span className={`text-sm font-bold ${getScoreColor(company.environmentalScore)}`}>
                      {company.environmentalScore}
                    </span>
                  </div>
                </div>
                
                <div>
                  <p className="text-sm text-gray-600 mb-2">데이터 공유 현황</p>
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div className="text-center">
                      <p className="font-bold text-blue-600">{company.dataSharing.totalRequests}</p>
                      <p className="text-gray-500">총 요청</p>
                    </div>
                    <div className="text-center">
                      <p className="font-bold text-green-600">{company.dataSharing.approvedRequests}</p>
                      <p className="text-gray-500">승인</p>
                    </div>
                    <div className="text-center">
                      <p className="font-bold text-yellow-600">{company.dataSharing.pendingRequests}</p>
                      <p className="text-gray-500">대기</p>
                    </div>
                  </div>
                </div>
                
                <div className="flex justify-between text-sm text-gray-600">
                  <span>최근 연락: {company.lastContact}</span>
                  <span>{company.relationship === 'direct' ? '직접' : '간접'} 관계</span>
                </div>
                
                <div className="flex gap-2 pt-2">
                  <button className="flex-1 px-3 py-2 text-sm bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors">
                    상세보기
                  </button>
                  <button className="flex-1 px-3 py-2 text-sm bg-gray-50 text-gray-600 rounded-lg hover:bg-gray-100 transition-colors">
                    데이터 요청
                  </button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {filteredCompanies.length === 0 && (
          <div className="text-center py-12">
            <Building2 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">검색 결과가 없습니다</h3>
            <p className="text-gray-600">다른 검색어나 필터를 사용해보세요.</p>
          </div>
        )}
      </div>
    </div>
  );
}