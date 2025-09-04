"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { 
  Plus, 
  Send, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  FileText, 
  Building2, 
  Calendar,
  Search,
  Download,
  Eye,
  Users,
  Target,
  ArrowLeft,
  Star
} from "lucide-react";
import {
  api,
  getSharingRequestsByRequester,
  getSharingStats,
  createSharingRequest,
  toggleStrategicSupplier as apiToggleStrategicSupplier,
  getStrategicSuppliers,
  getCompanies
} from "@/lib/api";

// 타입 정의
interface SharingRequest {
  id: string;
  requester_company_id: string;
  requester_company_name: string;
  provider_company_id: string;
  provider_company_name: string;
  data_type: string;
  data_category: string;
  data_description?: string;
  purpose: string;
  usage_period?: string;
  urgency_level: "low" | "normal" | "high";
  status: "pending" | "approved" | "rejected" | "completed";
  requested_at: string;
  reviewed_at?: string;
  approved_at?: string;
  completed_at?: string;
  reviewer_id?: string;
  reviewer_name?: string;
  review_comment?: string;
  data_url?: string;
  expiry_date?: string;
  requested_fields?: string;
}

interface CompanyChain {
  id: string;
  parent_company_id: string;
  child_company_id: string;
  child_company_name: string;
  chain_level: number;
  relationship_type: string;
}

interface SupplierData {
  id: string;
  name: string;
  icon: string;
  level: number;
  relationship: string;
  priority: "high" | "normal" | "low";
  status: "approved" | "pending" | "completed" | "rejected";
  lastRequestType: string;
  lastRequestDate: string;
  isStrategic: boolean;
}

interface RequestForm {
  provider_company_id: string;
  provider_company_name: string;
  data_type: string;
  data_category: string;
  data_description: string;
  requested_fields: string;
  purpose: string;
  usage_period: string;
  urgency_level: string;
}

// 동적 Mock 데이터 생성 함수 (요청한 데이터들)
const generateMockMyRequests = (companyInfo: any): SharingRequest[] => {
  if (!companyInfo.hasLowerTier) {
    return [];
  }
  
  return [
    {
      id: "my-req-001",
      requester_company_id: companyInfo.companyId,
      requester_company_name: companyInfo.companyName, 
      provider_company_id: `TIER${companyInfo.lowerTier}_L2MAN`,
      provider_company_name: `⚙️ L2 MAN (${companyInfo.lowerTier}차 협력사)`,
      data_type: "sustainability",
      data_category: "온실가스 배출량 데이터",
      data_description: "18650 배터리 셀 제조공정에서 발생하는 온실가스 배출량 (Scope 1,2,3 포함) - 제조단계별 세부 배출량 및 원재료별 탄소발자국",
      purpose: "배터리 LCA 분석 및 탄소발자국 계산을 위한 ESG 보고서 작성",
      urgency_level: "high",
      status: "pending" as const,
      requested_at: "2025-08-30T14:20:00Z",
      requested_fields: JSON.stringify(["greenhouse_gas_emissions", "raw_materials", "manufacturing_country", "energy_density", "production_plant"])
      // pending 상태에서는 reviewed_at, reviewer_id, reviewer_name, review_comment 없음
    },
    {
      id: "my-req-002",
      requester_company_id: companyInfo.companyId, 
      requester_company_name: companyInfo.companyName,
      provider_company_id: `TIER${companyInfo.lowerTier}_CONVERTER`,
      provider_company_name: `🔄 컨버터 (${companyInfo.lowerTier}차 협력사)`,
      data_type: "sustainability",
      data_category: "제품 안전정보 및 재활용 데이터",
      data_description: "리튬이온 배터리 18650 셀의 UN38.3 안전성 시험성적서, MSDS, 재활용 소재 함량비율 및 폐배터리 처리방법 가이드라인",
      purpose: "제품 안전성 검증 및 순환경제 보고서 작성",
      urgency_level: "normal",
      status: "approved" as const,
      requested_at: "2025-08-29T09:30:00Z",
      reviewed_at: "2025-08-30T10:15:00Z",
      approved_at: "2025-08-30T10:15:00Z",
      reviewer_id: `reviewer_converter_${companyInfo.lowerTier}`,
      reviewer_name: `이품질 (컨버터 ${companyInfo.lowerTier}차)`,
      review_comment: "UN38.3 인증서 및 최신 MSDS 문서를 포함하여 제공하겠습니다.",
      requested_fields: JSON.stringify(["safety_information", "recycled_material", "disposal_method", "recycling_method", "product_name", "capacity"])
    },
    {
      id: "my-req-003",
      requester_company_id: companyInfo.companyId,
      requester_company_name: companyInfo.companyName,
      provider_company_id: `TIER${companyInfo.lowerTier}_ACTIVATED_CARBON`, 
      provider_company_name: `🌿 활성탄 (${companyInfo.lowerTier}차 협력사)`,
      data_type: "sustainability",
      data_category: "원재료 공급원 추적 데이터",
      data_description: "배터리 양극재 및 음극재에 사용되는 리튬, 니켈, 코발트, 흑연의 원산지 추적정보 - 광산별 채굴 조건 및 ESG 인증현황 포함",
      purpose: "공급망 투명성 확보 및 원재료 ESG 리스크 평가",
      urgency_level: "normal",
      status: "completed" as const,
      requested_at: "2025-08-28T11:00:00Z",
      reviewed_at: "2025-08-28T16:30:00Z",
      approved_at: "2025-08-28T16:30:00Z", 
      completed_at: "2025-08-29T09:00:00Z",
      reviewer_id: `reviewer_activated_carbon_${companyInfo.lowerTier}`,
      reviewer_name: `박생산 (활성탄 ${companyInfo.lowerTier}차)`,
      review_comment: "리튬 광산별 ESG 인증현황 및 추적 데이터 전송 완료했습니다.",
      data_url: `https://material-tracking-tier${companyInfo.lowerTier}.company.com/download/lithium-source-tracking-2024`,
      requested_fields: JSON.stringify(["raw_materials", "raw_material_sources", "manufacturing_country", "production_plant"]),
      expiry_date: "2025-09-29T08:45:00Z"
    },
    {
      id: "my-req-004",
      requester_company_id: companyInfo.companyId,
      requester_company_name: companyInfo.companyName,
      provider_company_id: `TIER${companyInfo.lowerTier}_REJECTED_TEST`,
      provider_company_name: `🔧 전극코팅업체 (${companyInfo.lowerTier}차 협력사)`,
      data_type: "sustainability",
      data_category: "화학물질 구성 데이터",
      data_description: "배터리 전극 활물질 및 바인더의 화학적 조성 정보 - 납, 카드뮴, 수은 등 유해물질 함량 및 REACH 규제 준수현황",
      purpose: "제품 안전성 평가 및 규제 준수 확인",
      urgency_level: "low",
      status: "rejected" as const,
      requested_at: "2025-08-25T13:45:00Z",
      reviewed_at: "2025-08-26T11:20:00Z",
      reviewer_id: `reviewer_test_${companyInfo.lowerTier}`,
      reviewer_name: `김기밀 (전극코팅 ${companyInfo.lowerTier}차)`,
      review_comment: "전극 활물질의 정확한 화학조성은 핵심 기술정보로 분류되어 공유가 어렵습니다. 유해물질 함량 테스트 결과서로 대체 제공 가능합니다.",
      requested_fields: JSON.stringify(["chemical_composition", "safety_information"])
    }
  ];
};

// 동적 위 협력사 목록 생성 함수 (한 계단 아래만)
const generateMockSubSuppliers = (companyInfo: any) => {
  if (!companyInfo.hasLowerTier) {
    return [];
  }
  
  // 바로 아래 차수(lowerTier)의 협력사들만 반환
  return [
        // 핵심 협력사
    { 
      id: `TIER${companyInfo.lowerTier}_L2MAN`, 
      name: `⚙️ L2 MAN (${companyInfo.lowerTier}차 협력사)`, 
      icon: "⚙️",
      level: companyInfo.lowerTier, 
      relationship: "핵심공정",
      priority: "high" as const,
      status: "pending" as const,
      lastRequestType: "배터리 셀 제조공정 온실가스 배출량",
      lastRequestDate: "2025-08-30",
      isStrategic: true
    },
    { 
      id: `TIER${companyInfo.lowerTier}_CONVERTER`, 
      name: `🔄 컨버터 (${companyInfo.lowerTier}차 협력사)`, 
      icon: "🔄",
      level: companyInfo.lowerTier, 
      relationship: "변환공정",
      priority: "high" as const,
      status: "approved" as const,
      lastRequestType: "제품 안전정보 및 UN38.3 인증서",
      lastRequestDate: "2025-08-29",
      isStrategic: true
    },
    { 
      id: `TIER${companyInfo.lowerTier}_ACTIVATED_CARBON`, 
      name: `🌿 활성탄 (${companyInfo.lowerTier}차 협력사)`, 
      icon: "🌿",
      level: companyInfo.lowerTier, 
      relationship: "핵심소재",
      priority: "high" as const,
      status: "completed" as const,
      lastRequestType: "리튬 원재료 공급원 추적데이터",
      lastRequestDate: "2025-08-28",
      isStrategic: false
    },
    
    // 일반 협력사
    { 
      id: `TIER${companyInfo.lowerTier}_COATING`, 
      name: "전극코팅업체", 
      icon: "🎨",
      level: companyInfo.lowerTier, 
      relationship: "전극코팅",
      priority: "normal" as const,
      status: "approved" as const,
      lastRequestType: "전극 화학물질 구성정보",
      lastRequestDate: "2025-08-27",
      isStrategic: false
    },
    { 
      id: `TIER${companyInfo.lowerTier}_MATERIAL_SUPPLIER`, 
      name: "니켈공급사", 
      icon: "📦",
      level: companyInfo.lowerTier, 
      relationship: "원자재",
      priority: "normal" as const,
      status: "rejected" as const,
      lastRequestType: "니켈 원재료 ESG 인증서",
      lastRequestDate: "2025-08-15",
      isStrategic: false
    },
    { 
      id: `TIER${companyInfo.lowerTier}_LOGISTICS`, 
      name: "배터리운송업체", 
      icon: "🚛",
      level: companyInfo.lowerTier, 
      relationship: "운송",
      priority: "normal" as const,
      status: "approved" as const,
      lastRequestType: "운송중 안전성 및 온도관리 데이터",
      lastRequestDate: "2025-08-25",
      isStrategic: false
    }
  ];
};

// Mock 통계 데이터 (자동 계산)
const calculateMockStats = (requests: SharingRequest[]) => {
  return {
    total_requests: requests.length,
    pending_requests: requests.filter(r => r.status === 'pending').length,
    approved_requests: requests.filter(r => r.status === 'approved').length,
    rejected_requests: requests.filter(r => r.status === 'rejected').length,
    completed_requests: requests.filter(r => r.status === 'completed').length,
    avg_response_time_hours: 22.3
  };
};

const SupplierRequestPage = () => {
  const [myRequests, setMyRequests] = useState<SharingRequest[]>([]);
  const [supplierChains, setSupplierChains] = useState<CompanyChain[]>([]);
  const [stats, setStats] = useState({
    total_requests: 0,
    pending_requests: 0,
    approved_requests: 0,
    rejected_requests: 0,
    completed_requests: 0,
    avg_response_time_hours: 0
  });
  const [loading, setLoading] = useState(true);
  const [showRequestForm, setShowRequestForm] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState<SharingRequest | null>(null);
  const [activeTab, setActiveTab] = useState("dashboard");
  const [searchTerm, setSearchTerm] = useState("");
  const [suppliers, setSuppliers] = useState<SupplierData[]>([]);
  const [currentCompany, setCurrentCompany] = useState<{name: string, tier1: string} | null>(null);
  
  // 동적 회사 정보 설정 (클라이언트 사이드만)
  const [companyInfo, setCompanyInfo] = useState({
    companyId: "TIER4_LG",
    companyName: "🏭 LG에너지솔루션 (원청사)",
    companyTier: 4,
    companyCode: "LG",
    userId: "USER_TIER4_LG_001",
    userName: "김담당 (LG에너지솔루션 데이터 관리자)",
    upperTier: 3,
    lowerTier: 5,
    hasUpperTier: true,
    hasLowerTier: false
  });

  // URL 파라미터 기반 회사 정보 설정 (클라이언트에서만 실행)
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const roleParam = urlParams.get('role');
    
    let companyTier;
    if (roleParam === 'prime') {
      companyTier = 0; // 원청사
    } else if (roleParam === 'tier1') {
      companyTier = 1; // 1차사
    } else if (roleParam === 'tier2') {
      companyTier = 2; // 2차사
    } else if (roleParam === 'tier3') {
      companyTier = 3; // 3차사
    } else if (roleParam === 'tier4') {
      companyTier = 4; // 최하위
    } else {
      companyTier = 4; // 기본값: 최하위 (테스트용)
    }
    
    const companyCode = "LG"; // LG에너지솔루션
    const companyId = `TIER${companyTier}_${companyCode}`;
    
    setCompanyInfo({
      companyId,
      companyName: `🏭 LG에너지솔루션 (원청사)`,
      companyTier,
      companyCode,
      userId: `USER_${companyId}_001`,
      userName: `김담당 (LG에너지솔루션 데이터 관리자)`,
      upperTier: companyTier - 1,
      lowerTier: companyTier + 1,
      hasUpperTier: companyTier > 0,
      hasLowerTier: companyTier < 4
    });
  }, []);

  // 페이지 접근 권한 체크
  const isBottomTier = !companyInfo.hasLowerTier;
  const hasRequestPageAccess = companyInfo.hasLowerTier; // 하위 tier가 있어야 요청 페이지 사용 가능

  // 회사 목록을 가져와서 현재 회사 설정 (접근 권한이 있을 때만)
  useEffect(() => {
    if (!hasRequestPageAccess) {
      // 접근 권한이 없으면 API 호출하지 않고 기본값 설정
      setCurrentCompany({
        name: "LG에너지솔루션",
        tier1: "에코프로비엠"
      });
      return;
    }

    const fetchCompanies = async () => {
      try {
        const response = await getCompanies();
        const companies = response.data?.companies || [];
        
        // 첫 번째 회사를 현재 회사로 설정 (실제로는 로그인 정보에서)
        if (companies.length > 0) {
          setCurrentCompany({
            name: companies[0].company_name,
            tier1: companies[0].tier1
          });
        }
      } catch (error) {
        console.error("회사 목록 조회 실패:", error);
        // API 실패시 기본값 사용
        setCurrentCompany({
          name: "LG에너지솔루션",
          tier1: "에코프로비엠"
        });
      }
    };

    fetchCompanies();
  }, [hasRequestPageAccess]);

  // 핵심 협력사 토글 함수
  const toggleStrategicSupplier = async (supplierId: string) => {
    if (!hasRequestPageAccess) {
      alert("접근 권한이 없습니다.");
      return;
    }

    try {
      // 현재 상태 찾기
      const currentSupplier = suppliers.find(s => s.id === supplierId);
      if (!currentSupplier) return;

      const newIsStrategic = !currentSupplier.isStrategic;
      
      // 실제 API 호출
      console.log(`🔧 핵심 협력사 토글: ${supplierId} -> ${newIsStrategic}`);
      const response = await apiToggleStrategicSupplier(supplierId, newIsStrategic);
      console.log("API 응답:", response);
      
      if (response?.status === "success") {
        // 성공시 로컬 상태 업데이트
        setSuppliers(prev => 
          prev.map(supplier => 
            supplier.id === supplierId 
              ? { ...supplier, isStrategic: newIsStrategic }
              : supplier
          )
        );
        
        console.log(`✅ ${currentSupplier.name} 핵심 협력사 상태 ${newIsStrategic ? '지정' : '해제'} 완료`);
      } else {
        console.error("❌ 핵심 협력사 상태 변경 실패");
        alert("핵심 협력사 상태 변경에 실패했습니다.");
      }

      console.log(`${currentSupplier.name} ${newIsStrategic ? '핵심 협력사로 지정' : '일반 협력사로 변경'}`);
    } catch (error) {
      console.error('핵심 협력사 상태 변경 실패:', error);
    }
  };
  const currentCompanyId = currentCompany?.name || "LG에너지솔루션";
  const currentCompanyName = currentCompany?.name || "LG에너지솔루션";
  
  // 동적으로 생성된 Mock 데이터
  const MOCK_MY_REQUESTS = generateMockMyRequests(companyInfo);
  const MOCK_SUB_SUPPLIERS = generateMockSubSuppliers(companyInfo);

  // suppliers 상태 초기화
  useEffect(() => {
    const mockSuppliers = generateMockSubSuppliers(companyInfo);
    setSuppliers(mockSuppliers);
  }, [companyInfo.companyTier, companyInfo.hasLowerTier]);
  
  // 요청 폼 상태
  const [requestForm, setRequestForm] = useState<RequestForm>({
    provider_company_id: "",
    provider_company_name: "",
    data_type: "sustainability",
    data_category: "",
    data_description: "",
    requested_fields: "",
    purpose: "",
    usage_period: "",
    urgency_level: "normal"
  });

  // 데이터 로드
  useEffect(() => {
    if (suppliers.length > 0 && hasRequestPageAccess) {
    loadData();
    }
  }, [suppliers, hasRequestPageAccess]);

  const loadData = async () => {
    try {
      setLoading(true);
      const useMockData = false; // 실제 API 사용으로 변경
      
      if (useMockData) {
        // Mock 데이터 사용 (기존 코드)
        const mockRequests = MOCK_MY_REQUESTS;
        setMyRequests(mockRequests);
        setSupplierChains(suppliers.map(supplier => ({
          id: supplier.id,
            parent_company_id: currentCompanyId,
          child_company_id: supplier.id,
          child_company_name: `${supplier.icon} ${supplier.name} (${supplier.level}차)`,
          chain_level: supplier.level,
          relationship_type: supplier.relationship
        })));
        setStats(calculateMockStats(mockRequests));
        await new Promise(resolve => setTimeout(resolve, 500));
      } else {
        // 실제 API 호출
        console.log("🔧 실제 API 호출 시작...");
        
        // 1. 내가 보낸 요청들 조회
        const requests = await getSharingRequestsByRequester(currentCompanyId);
        console.log("요청 데이터:", requests);
        setMyRequests(requests.data?.requests || []);
        
        // 2. 통계 조회
        const stats = await getSharingStats(currentCompanyId);
        console.log("통계 데이터:", stats);
        setStats(stats.data || {
          total_requests: 0,
          pending_requests: 0,
          approved_requests: 0,
          rejected_requests: 0,
          completed_requests: 0
        });
        
        // 3. 협력사 관계는 Mock 데이터 유지 (현재 API 미구현)
        setSupplierChains(suppliers.map(supplier => ({
          id: supplier.id,
            parent_company_id: currentCompanyId,
          child_company_id: supplier.id,
          child_company_name: `${supplier.icon} ${supplier.name} (${supplier.level}차)`,
          chain_level: supplier.level,
          relationship_type: supplier.relationship
        })));
      }
    } catch (error) {
      console.error("데이터 로드 실패:", error);
      setMyRequests([]);
      setSupplierChains([]);
      setStats({
        total_requests: 0,
        pending_requests: 0,
        approved_requests: 0,
        rejected_requests: 0,
        completed_requests: 0,
        avg_response_time_hours: 0
      });
    } finally {
      setLoading(false);
    }
  };

  // 새 요청 생성
  const handleCreateRequest = async () => {
    if (!hasRequestPageAccess) {
      alert("접근 권한이 없습니다.");
      return;
    }

    try {
      const requestData = {
        ...requestForm,
        requester_company_id: currentCompanyId,
        requester_company_name: currentCompanyName,
      };
      
      const response = await api('/sharing/', {
        method: 'POST',
        body: JSON.stringify(requestData),
      });
      
      if (response && typeof response === 'object' && 'status' in response && response.status === "success") {
        alert("데이터 공유 요청이 성공적으로 전송되었습니다.");
        setShowRequestForm(false);
        setRequestForm({
          provider_company_id: "",
          provider_company_name: "",
          data_type: "sustainability",
          data_category: "",
          data_description: "",
          requested_fields: "",
          purpose: "",
          usage_period: "",
          urgency_level: "normal"
        });
        loadData();
      } else {
        alert("요청 전송 중 오류가 발생했습니다.");
      }
    } catch (error) {
      console.error("요청 생성 실패:", error);
      alert("요청 전송 중 오류가 발생했습니다.");
    }
  };

  // 협력사 선택
  const handleSelectSupplier = (supplier: CompanyChain) => {
    setRequestForm({
      ...requestForm,
      provider_company_id: supplier.child_company_id,
      provider_company_name: supplier.child_company_name
    });
  };

  // 상태 확인 함수
  const handleStatusCheck = (supplier: CompanyChain) => {
    const supplierData = suppliers.find(s => s.id === supplier.child_company_id);
    if (!supplierData) return;

    // 해당 협력사의 요청 찾기
    const relatedRequest = myRequests.find(req => req.provider_company_id === supplier.child_company_id);
    
    if (relatedRequest) {
      setSelectedRequest(relatedRequest);
    } else {
      alert(`${supplierData.name}에 대한 요청 정보를 찾을 수 없습니다.`);
    }
  };

  // 상태별 색상 및 아이콘
  const getStatusInfo = (status: string) => {
    switch (status) {
      case 'pending':
        return { color: '!bg-yellow-100 !text-yellow-800 border-yellow-200', icon: Clock, text: '승인 대기중' };
      case 'approved':
        return { color: '!bg-blue-100 !text-blue-800 border-blue-200', icon: CheckCircle, text: '공유 승인' };
      case 'rejected':
        return { color: '!bg-red-100 !text-red-800 border-red-200', icon: XCircle, text: '공유 거부' };
      case 'completed':
        return { color: '!bg-green-100 !text-green-800 border-green-200', icon: CheckCircle, text: '데이터 수신' };
      default:
        return { color: '!bg-gray-100 !text-gray-800 border-gray-200', icon: AlertCircle, text: '알 수 없음' };
    }
  };

  // 긴급도별 색상
  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'normal': return 'bg-blue-100 text-blue-800';
      case 'low': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // 통계 계산 (실제 데이터 우선, 백업으로 stats 사용)
  const displayStats = {
    total: myRequests.length || stats.total_requests,
    pending: myRequests.filter(r => r.status === 'pending').length || stats.pending_requests,
    approved: myRequests.filter(r => r.status === 'approved').length || stats.approved_requests,
    rejected: myRequests.filter(r => r.status === 'rejected').length || stats.rejected_requests,
    completed: myRequests.filter(r => r.status === 'completed').length || stats.completed_requests,
  };

  // 필터링 및 정렬된 요청 목록
  const filteredRequests = myRequests
    .filter(request =>
    request.provider_company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    request.data_category.toLowerCase().includes(searchTerm.toLowerCase()) ||
    request.purpose.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      // 핵심 협력사 여부 확인
      const aIsStrategic = suppliers.find(s => s.name === a.provider_company_name)?.isStrategic || false;
      const bIsStrategic = suppliers.find(s => s.name === b.provider_company_name)?.isStrategic || false;
      
      // 긴급도 확인
      const aIsUrgent = a.urgency_level === 'high';
      const bIsUrgent = b.urgency_level === 'high';
      
      // 1. 긴급 + 핵심 협력사 (최우선)
      const aUrgentStrategic = aIsUrgent && aIsStrategic;
      const bUrgentStrategic = bIsUrgent && bIsStrategic;
      if (aUrgentStrategic && !bUrgentStrategic) return -1;
      if (!aUrgentStrategic && bUrgentStrategic) return 1;
      
      // 2. 긴급 요청
      if (aIsUrgent && !bIsUrgent) return -1;
      if (!aIsUrgent && bIsUrgent) return 1;
      
      // 3. 핵심 협력사 (pending 상태)
      const aPendingStrategic = a.status === 'pending' && aIsStrategic;
      const bPendingStrategic = b.status === 'pending' && bIsStrategic;
      if (aPendingStrategic && !bPendingStrategic) return -1;
      if (!aPendingStrategic && bPendingStrategic) return 1;
      
      // 4. 나머지는 날짜순 (최신순)
      return new Date(b.requested_at).getTime() - new Date(a.requested_at).getTime();
    });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">데이터를 로드하는 중...</p>
        </div>
      </div>
    );
  }

  // 최하위 tier 접근 제한 (하위 협력사가 없는 경우)
  if (!hasRequestPageAccess) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center">
        <Card className="max-w-md mx-auto">
          <CardContent className="p-8 text-center">
            <div className="mb-6">
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Building2 className="w-8 h-8 text-orange-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">최하위 협력사</h2>
              <p className="text-gray-600">
                하위 협력사가 없어 데이터 요청 페이지를 사용할 수 없습니다.
              </p>
            </div>
            <div className="space-y-4">
              <p className="text-sm text-gray-500">
                최하위 협력사는 상위 협력사의 요청에만 응답합니다.
              </p>
              <div className="space-y-2">
                <Button 
                  onClick={() => {
                    // URL 파라미터로 1차사 역할로 접근
                    window.open('/data-sharing-approval?role=tier1', '_blank');
                  }} 
                  className="w-full"
                >
                  데이터 승인 페이지로 이동 (1차사 역할)
                </Button>
                <p className="text-xs text-gray-400 text-center">
                  테스트용: 1차사 관점에서 승인 페이지 체험
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200">
      {/* 네비게이션 바 */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-xl font-bold text-gray-900">ERI Potter</h1>
              </div>
              <div className="hidden md:ml-6 md:flex md:space-x-8">
                <a href="/company-profile" className="text-gray-500 hover:text-gray-700 px-3 py-2 text-sm font-medium">
                  회사 프로필
                </a>
                <a href="/assessment" className="text-gray-500 hover:text-gray-700 px-3 py-2 text-sm font-medium">
                  평가
                </a>
                <a href="/report" className="text-gray-500 hover:text-gray-700 px-3 py-2 text-sm font-medium">
                  보고서
                </a>
                <a href="/data-sharing-approval" className="text-gray-500 hover:text-gray-700 px-3 py-2 text-sm font-medium">
                  데이터 승인
                </a>
                <a href="/data-sharing-request" className="text-blue-600 border-b-2 border-blue-600 px-3 py-2 text-sm font-medium">
                  데이터 요청
                </a>
                <a href="/chat" className="text-gray-500 hover:text-gray-700 px-3 py-2 text-sm font-medium">
                  챗봇
                </a>
              </div>
            </div>
            <div className="flex items-center">
              <span className="text-sm text-gray-600 mr-4">{currentCompanyName}</span>
              <Button variant="outline" size="sm" onClick={() => window.location.href = '/'}>
                로그아웃
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* 헤더 */}
        <div className="flex items-center justify-between mb-8">
          <div>
                         <h1 className="text-3xl font-bold text-gray-900 mb-2">
               {activeTab === 'dashboard' && '협력사 데이터 수집 관리'}
               {activeTab === 'all' && '전체 데이터 요청'}
               {activeTab === 'pending' && '데이터 요청 및 공유 승인 대기중'}
               {activeTab === 'approved' && '데이터 공유 승인됨'}
               {activeTab === 'rejected' && '데이터 공유 거부됨'}
               {activeTab === 'completed' && '데이터 수신 완료'}
             </h1>
            <p className="text-gray-600">
              {activeTab === 'dashboard' && (
                companyInfo.hasLowerTier ?
                  `원청사로서 직속 1차 협력사들로부터 필요한 ESG 데이터를 수집합니다. 1차 협력사들은 다시 2차, 3차 협력사에게 요청하여 계층적으로 데이터를 취합합니다.` :
                  '최하위 차수로 요청할 하위 협력사가 없습니다.'
              )}
              {activeTab === 'all' && '협력사들에게 요청한 모든 데이터 요청 목록입니다.'}
              {activeTab === 'pending' && '협력사들에게 데이터 요청을 보냈으나 아직 승인 대기중인 목록입니다.'}
              {activeTab === 'approved' && '협력사들이 승인한 데이터 공유 요청 목록입니다. 데이터 수집이 진행 중입니다.'}
              {activeTab === 'rejected' && '협력사들이 거부한 데이터 공유 요청 목록입니다. 재요청이나 대안을 검토해보세요.'}
              {activeTab === 'completed' && '데이터 수신이 완료된 요청 목록입니다. 수집된 데이터를 확인할 수 있습니다.'}
            </p>
          </div>

        </div>

        {/* 협력사 목록으로 가기 버튼 (요청 목록 탭에서만 표시) */}
        {activeTab !== 'dashboard' && (
          <div className="flex justify-end mb-4">
          <Button
              variant="default"
              onClick={() => setActiveTab("dashboard")}
              className="flex items-center gap-2 bg-gray-600 hover:bg-gray-700 text-white shadow-lg px-6 py-2 text-sm font-medium"
          >
              <ArrowLeft className="h-4 w-4" />
              협력사 목록으로
          </Button>
        </div>
        )}

        {/* 통계 카드 (항상 표시) */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
              <Card className="hover:shadow-lg transition-all duration-200 cursor-pointer hover:scale-105">
                <CardContent className="p-4" onClick={() => setActiveTab("all")}>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">전체 요청</p>
                      <p className="text-2xl font-bold text-gray-900">{displayStats.total}</p>
                    </div>
                    <FileText className="h-8 w-8 text-gray-400" />
                  </div>
                  <div className="mt-2">
                    <div className="w-full h-1 bg-gray-200 rounded-full">
                      <div className="h-1 bg-gray-500 rounded-full" style={{ width: '100%' }}></div>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="hover:shadow-lg transition-all duration-200 cursor-pointer hover:scale-105 hover:bg-yellow-50">
                <CardContent className="p-4" onClick={() => setActiveTab("pending")}>
                  <div className="flex items-center justify-between">
                    <div>
                                             <p className="text-sm font-medium text-gray-600">데이터 요청 및 승인 대기중</p>
                      <p className="text-2xl font-bold text-yellow-600">{displayStats.pending}</p>
                    </div>
                    <Clock className="h-8 w-8 text-yellow-400" />
                  </div>
                  <div className="mt-2">
                    <div className="w-full h-1 bg-yellow-200 rounded-full">
                      <div 
                        className="h-1 bg-yellow-500 rounded-full transition-all duration-300" 
                        style={{ width: `${displayStats.total > 0 ? (displayStats.pending / displayStats.total) * 100 : 0}%` }}
                      ></div>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="hover:shadow-lg transition-all duration-200 cursor-pointer hover:scale-105 hover:bg-blue-50">
                <CardContent className="p-4" onClick={() => setActiveTab("approved")}>
                  <div className="flex items-center justify-between">
                    <div>
                                             <p className="text-sm font-medium text-gray-600">데이터 공유 승인</p>
                      <p className="text-2xl font-bold text-blue-600">{displayStats.approved}</p>
                    </div>
                    <CheckCircle className="h-8 w-8 text-blue-400" />
                  </div>
                  <div className="mt-2">
                    <div className="w-full h-1 bg-blue-200 rounded-full">
                      <div 
                        className="h-1 bg-blue-500 rounded-full transition-all duration-300" 
                        style={{ width: `${displayStats.total > 0 ? (displayStats.approved / displayStats.total) * 100 : 0}%` }}
                      ></div>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="hover:shadow-lg transition-all duration-200 cursor-pointer hover:scale-105 hover:bg-red-50">
                <CardContent className="p-4" onClick={() => setActiveTab("rejected")}>
                  <div className="flex items-center justify-between">
                    <div>
                                             <p className="text-sm font-medium text-gray-600">데이터 공유 거부</p>
                      <p className="text-2xl font-bold text-red-600">{displayStats.rejected}</p>
                    </div>
                    <XCircle className="h-8 w-8 text-red-400" />
                  </div>
                  <div className="mt-2">
                    <div className="w-full h-1 bg-red-200 rounded-full">
                      <div 
                        className="h-1 bg-red-500 rounded-full transition-all duration-300" 
                        style={{ width: `${displayStats.total > 0 ? (displayStats.rejected / displayStats.total) * 100 : 0}%` }}
                      ></div>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="hover:shadow-lg transition-all duration-200 cursor-pointer hover:scale-105 hover:bg-green-50">
                <CardContent className="p-4" onClick={() => setActiveTab("completed")}>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">데이터 수신</p>
                      <p className="text-2xl font-bold text-green-600">{displayStats.completed}</p>
                    </div>
                    <CheckCircle className="h-8 w-8 text-green-400" />
                  </div>
                  <div className="mt-2">
                    <div className="w-full h-1 bg-green-200 rounded-full">
                      <div 
                        className="h-1 bg-green-500 rounded-full transition-all duration-300" 
                        style={{ width: `${displayStats.total > 0 ? (displayStats.completed / displayStats.total) * 100 : 0}%` }}
                      ></div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

        {/* 새 요청 생성 버튼 */}
        <div className="mb-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="lg:col-start-2 lg:col-span-3 md:col-span-2">
            <Button
              onClick={() => setShowRequestForm(true)}
              size="lg"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 text-lg font-semibold shadow-md hover:shadow-lg transition-all duration-200 rounded-lg border-2 border-blue-600 hover:border-blue-700 flex items-center justify-center"
            >
              <Plus className="h-5 w-5 mr-2" />
              새 데이터 요청 생성
            </Button>
          </div>
        </div>

        {/* 검색 및 필터 */}
        <div className="flex flex-col sm:flex-row gap-4 mb-8">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
            <Input
              placeholder="협력사명, 데이터 카테고리, 사용 목적으로 검색..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-12 py-4 text-lg border-2 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-opacity-20 shadow-sm rounded-lg"
            />
          </div>
        </div>

        {/* 탭 컨테이너 (네비게이션 바 제거) */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">

          {/* 전체 요청 탭 */}
          <TabsContent value="all" className="space-y-4">
            {renderRequestList(filteredRequests, searchTerm, setSearchTerm, setSelectedRequest, getStatusInfo, getUrgencyColor, suppliers)}
          </TabsContent>

          {/* 대시보드 탭 */}
          <TabsContent value="dashboard" className="space-y-6">
            {/* 하위 협력사 목록 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  직속 1차 협력사 목록
                </CardTitle>
                <CardDescription>
                  직속 1차 협력사들입니다. 이들은 다시 2차, 3차 협력사에게 요청하여 계층적으로 데이터를 수집합니다.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {/* 핵심 협력사 섹션 */}
                <div className="mb-8">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                      <h3 className="text-lg font-semibold text-gray-900">핵심 협력사</h3>
                      <Badge className="bg-red-100 text-red-800">
                        {supplierChains.filter(s => suppliers.find(sup => sup.id === s.child_company_id)?.isStrategic).length}개
                      </Badge>
                    </div>
                    
                    {/* 핵심 협력사 상태 요약 */}
                    <div className="flex items-center gap-2 text-sm">
                      {(() => {
                        const strategicSuppliers = supplierChains.filter(s => 
                          suppliers.find(sup => sup.id === s.child_company_id)?.isStrategic
                        );
                        const pending = strategicSuppliers.filter(s => 
                          suppliers.find(sup => sup.id === s.child_company_id)?.status === 'pending'
                        ).length;
                        const completed = strategicSuppliers.filter(s => 
                          suppliers.find(sup => sup.id === s.child_company_id)?.status === 'completed'
                        ).length;
                        
                        return (
                          <>
                            {pending > 0 && (
                              <Badge className="bg-yellow-100 text-yellow-800 animate-pulse">
                                <Clock className="h-3 w-3 mr-1" />
                                대기 {pending}
                              </Badge>
                            )}
                            {completed > 0 && (
                              <Badge className="bg-green-100 text-green-800">
                                <CheckCircle className="h-3 w-3 mr-1" />
                                완료 {completed}
                              </Badge>
                            )}
                          </>
                        );
                      })()}
                    </div>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {supplierChains
                      .filter(supplier => {
                        const supplierData = suppliers.find(s => s.id === supplier.child_company_id);
                        return supplierData?.isStrategic === true;
                      })
                      .map((supplier) => {
                        const supplierData = suppliers.find(s => s.id === supplier.child_company_id);
                        return (
                          <Card key={supplier.id} className={`hover:shadow-lg transition-all duration-300 cursor-pointer border-l-4 ${
                            supplierData?.status === 'completed' ? 'border-l-green-500 bg-green-50' :
                            supplierData?.status === 'pending' ? 'border-l-yellow-500 bg-yellow-50' :
                            supplierData?.status === 'approved' ? 'border-l-blue-500 bg-blue-50' :
                            'border-l-gray-300'
                          }`}>
                            <CardContent className="p-6">
                              <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-3">
                                  <div>
                                    <div className="flex items-center gap-2">
                                      <h3 className="text-lg font-bold text-gray-900">{supplierData?.name}</h3>
                                      <Button
                                        variant="ghost"
                                        size="sm"
                                        className="p-1 h-6 w-6 hover:bg-yellow-100"
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          toggleStrategicSupplier(supplier.child_company_id);
                                        }}
                                      >
                                        <Star 
                                          className={`h-4 w-4 ${
                                            suppliers.find(s => s.id === supplier.child_company_id)?.isStrategic 
                                              ? 'fill-yellow-400 text-yellow-400' 
                                              : 'text-gray-300 hover:text-yellow-400'
                                          }`}
                                        />
                                      </Button>
                                    </div>
                                    <p className="text-sm text-gray-600">{supplier.chain_level}차 협력사</p>
                                  </div>
                                </div>
                                <div className="flex flex-col items-end gap-2">
                                  <Badge className={
                                    supplierData?.status === 'completed' ? '!bg-green-100 !text-green-800' :
                                    supplierData?.status === 'pending' ? '!bg-yellow-100 !text-yellow-800' :
                                    supplierData?.status === 'approved' ? '!bg-blue-100 !text-blue-800' :
                                    supplierData?.status === 'rejected' ? '!bg-red-100 !text-red-800' :
                                    '!bg-gray-100 !text-gray-800'
                                  }>
                                    {supplierData?.status === 'completed' ? '데이터 수신' :
                                     supplierData?.status === 'pending' ? '승인 대기중' :
                                     supplierData?.status === 'approved' ? '공유 승인' : '공유 거부'}
                                  </Badge>

                                </div>
                              </div>
                              
                              <div className="space-y-3 mb-4">
                                <div className="space-y-1">
                                  <div className="text-sm text-gray-600">최근 요청</div>
                                  <div className="text-sm text-gray-900 font-medium">{supplierData?.lastRequestType}</div>
                                </div>
                                <div className="space-y-1">
                                  <div className="text-sm text-gray-600">요청 날짜</div>
                                  <div className="text-sm text-gray-900">{supplierData?.lastRequestDate}</div>
                                </div>
                              </div>
                              
                              <Button
                                size="sm"
                                className={`w-full transition-all duration-200 ${
                                  supplierData?.status === 'completed' ? 'bg-green-600 hover:bg-green-700' :
                                  supplierData?.status === 'pending' ? 'bg-yellow-600 hover:bg-yellow-700' :
                                  'bg-blue-600 hover:bg-blue-700'
                                }`}
                                onClick={() => {
                                  if (supplierData?.status === 'pending') {
                                    handleStatusCheck(supplier);
                                  } else {
                                    handleSelectSupplier(supplier);
                                    setShowRequestForm(true);
                                  }
                                }}
                              >
                                <Send className="h-4 w-4 mr-2" />
                                {supplierData?.status === 'completed' ? '추가 요청' :
                                 supplierData?.status === 'pending' ? '상태 확인' : 
                                 supplierData?.status === 'approved' ? '추가 요청' : '데이터 요청'}
                              </Button>
                            </CardContent>
                          </Card>
                        );
                      })}
                  </div>
                </div>

                {/* 일반 협력사 섹션 */}
                <div className="mt-12">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                      <h3 className="text-lg font-semibold text-gray-900">일반 협력사</h3>
                      <Badge className="bg-blue-100 text-blue-800">
                        {supplierChains.filter(s => !suppliers.find(sup => sup.id === s.child_company_id)?.isStrategic).length}개
                      </Badge>
                    </div>
                    
                    {/* 일반 협력사 상태 요약 */}
                    <div className="flex items-center gap-2 text-sm">
                      {(() => {
                        const normalSuppliers = supplierChains.filter(s => 
                          !suppliers.find(sup => sup.id === s.child_company_id)?.isStrategic
                        );
                        const pending = normalSuppliers.filter(s => 
                          suppliers.find(sup => sup.id === s.child_company_id)?.status === 'pending'
                        ).length;
                        const completed = normalSuppliers.filter(s => 
                          suppliers.find(sup => sup.id === s.child_company_id)?.status === 'completed'
                        ).length;
                        const approved = normalSuppliers.filter(s => 
                          suppliers.find(sup => sup.id === s.child_company_id)?.status === 'approved'
                        ).length;
                        
                        return (
                          <>
                            {pending > 0 && (
                              <Badge className="bg-yellow-100 text-yellow-800">
                                <Clock className="h-3 w-3 mr-1" />
                                대기 {pending}
                              </Badge>
                            )}
                          </>
                        );
                      })()}
                    </div>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {supplierChains
                      .filter(supplier => {
                        const supplierData = suppliers.find(s => s.id === supplier.child_company_id);
                        return supplierData?.isStrategic === false;
                      })
                      .map((supplier) => {
                        const supplierData = suppliers.find(s => s.id === supplier.child_company_id);
                        return (
                          <Card key={supplier.id} className="hover:shadow-md transition-all duration-200 cursor-pointer">
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between mb-3">
                                <div className="flex items-center gap-2">
                                  <span className="text-lg">{supplierData?.icon}</span>
                          <div>
                                    <div className="flex items-center gap-1">
                                      <h3 className="font-semibold text-gray-900">{supplierData?.name}</h3>
                                      <Button
                                        variant="ghost"
                                        size="sm"
                                        className="p-0.5 h-5 w-5 hover:bg-yellow-100"
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          toggleStrategicSupplier(supplier.child_company_id);
                                        }}
                                      >
                                        <Star 
                                          className={`h-3 w-3 ${
                                            suppliers.find(s => s.id === supplier.child_company_id)?.isStrategic 
                                              ? 'fill-yellow-400 text-yellow-400' 
                                              : 'text-gray-300 hover:text-yellow-400'
                                          }`}
                                        />
                                      </Button>
                          </div>
                                    <p className="text-xs text-gray-600">{supplier.chain_level}차 협력사</p>
                        </div>
                                </div>
                                <Badge className={
                                  supplierData?.status === 'completed' ? '!bg-green-100 !text-green-800' :
                                  supplierData?.status === 'pending' ? '!bg-yellow-100 !text-yellow-800' :
                                  supplierData?.status === 'approved' ? '!bg-blue-100 !text-blue-800' :
                                  supplierData?.status === 'rejected' ? '!bg-red-100 !text-red-800' :
                                  '!bg-gray-100 !text-gray-800'
                                }>
                                  {supplierData?.status === 'completed' ? '데이터 수신' :
                                   supplierData?.status === 'pending' ? '승인 대기중' :
                                   supplierData?.status === 'approved' ? '공유 승인' : '공유 거부'}
                                </Badge>
                              </div>
                              
                              <div className="space-y-1 mb-3">
                                <div className="text-xs text-gray-600">
                                  <span className="font-medium">최근 요청:</span> {supplierData?.lastRequestType}
                                </div>
                                <div className="text-xs text-gray-500">
                                  {supplierData?.lastRequestDate}
                                </div>
                              </div>
                              
                        <Button
                          size="sm"
                          className="w-full"
                          onClick={() => {
                                  if (supplierData?.status === 'pending') {
                                    handleStatusCheck(supplier);
                                  } else {
                            handleSelectSupplier(supplier);
                            setShowRequestForm(true);
                                  }
                                }}
                              >
                                <Send className="h-3 w-3 mr-1" />
                                {supplierData?.status === 'completed' ? '추가 요청' :
                                 supplierData?.status === 'pending' ? '상태 확인' : 
                                 supplierData?.status === 'approved' ? '추가 요청' : '데이터 요청'}
                        </Button>
                      </CardContent>
                    </Card>
                        );
                      })}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* 최근 요청 현황 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  최근 요청 현황
                </CardTitle>
              </CardHeader>
              <CardContent>
                {myRequests.slice(0, 5).map((request) => {
                  const statusInfo = getStatusInfo(request.status);
                  const StatusIcon = statusInfo.icon;
                  
                  return (
                    <div key={request.id} className="flex items-center justify-between py-5 px-2 border-b last:border-b-0">
                      <div className="flex items-center gap-3 flex-1">
                        <StatusIcon className="h-4 w-4 text-gray-400" />
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                          <p className="font-medium text-gray-900">{request.data_category}</p>
                            <Badge className="bg-gray-100 text-gray-800 text-xs px-2 py-0.5">
                              {request.data_type}
                            </Badge>
                        </div>
                          <p className="text-sm text-gray-600 mb-1">{request.provider_company_name}</p>
                          <p className="text-xs text-gray-500">목적: {request.purpose}</p>
                      </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Badge className={statusInfo.color}>
                          {statusInfo.text}
                        </Badge>
                        <span className="text-sm text-gray-500">
                          {new Date(request.requested_at).toLocaleDateString('ko-KR')}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          </TabsContent>

          {/* 검토 대기 탭 */}
          <TabsContent value="pending" className="space-y-4">
            {renderRequestList(filteredRequests.filter(r => r.status === 'pending'), searchTerm, setSearchTerm, setSelectedRequest, getStatusInfo, getUrgencyColor, suppliers)}
          </TabsContent>

          {/* 승인됨 탭 */}
          <TabsContent value="approved" className="space-y-4">
            {renderRequestList(filteredRequests.filter(r => r.status === 'approved'), searchTerm, setSearchTerm, setSelectedRequest, getStatusInfo, getUrgencyColor, suppliers)}
          </TabsContent>

          {/* 거부됨 탭 */}
          <TabsContent value="rejected" className="space-y-4">
            {renderRequestList(filteredRequests.filter(r => r.status === 'rejected'), searchTerm, setSearchTerm, setSelectedRequest, getStatusInfo, getUrgencyColor, suppliers)}
          </TabsContent>

          {/* 완료됨 탭 */}
          <TabsContent value="completed" className="space-y-4">
            {renderRequestList(filteredRequests.filter(r => r.status === 'completed'), searchTerm, setSearchTerm, setSelectedRequest, getStatusInfo, getUrgencyColor, suppliers)}
          </TabsContent>
        </Tabs>
      </div>

      {/* 요청 생성 모달 */}
      {showRequestForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                    <Plus className="h-5 w-5 text-blue-600" />
                    새 데이터 요청 생성
                  </h2>
                </div>
                <Button
                  variant="ghost"
                  onClick={() => setShowRequestForm(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </Button>
              </div>
              

              
              <div className="space-y-4">
                {/* 협력사 선택 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">요청 대상 협력사</label>
                  {requestForm.provider_company_name ? (
                    <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                      <p className="font-medium text-blue-900">{requestForm.provider_company_name}</p>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setRequestForm({...requestForm, provider_company_id: "", provider_company_name: ""})}
                        className="mt-2"
                      >
                        다른 협력사 선택
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {supplierChains.map((supplier) => (
                        <div
                          key={supplier.id}
                          className="p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
                          onClick={() => handleSelectSupplier(supplier)}
                        >
                          <p className="font-medium">{supplier.child_company_name}</p>
                          <p className="text-sm text-gray-600">{supplier.chain_level}차 협력사</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* 데이터 타입 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">데이터 타입</label>
                  <select
                    value={requestForm.data_type}
                    onChange={(e) => setRequestForm({...requestForm, data_type: e.target.value})}
                    className="w-full p-2 border border-gray-300 rounded-lg"
                  >
                    <option value="sustainability">지속가능성 (ESG)</option>
                  </select>
                  <p className="text-xs text-gray-500 mt-1">현재는 ESG 관련 데이터만 요청 가능합니다</p>
                </div>

                {/* 데이터 카테고리 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">데이터 카테고리</label>
                  <select
                    value={requestForm.data_category}
                    onChange={(e) => setRequestForm({...requestForm, data_category: e.target.value, requested_fields: ''})}
                    className="w-full p-2 border border-gray-300 rounded-lg"
                  >
                    <option value="">카테고리를 선택하세요</option>
                    <option value="온실가스 배출량 데이터">온실가스 배출량 데이터</option>
                    <option value="제품 안전정보 및 재활용 데이터">제품 안전정보 및 재활용 데이터</option>
                    <option value="원재료 공급원 추적 데이터">원재료 공급원 추적 데이터</option>
                    <option value="화학물질 구성 데이터">화학물질 구성 데이터</option>
                  </select>
                </div>

                {/* 데이터 설명 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">데이터 설명</label>
                  <Textarea
                    placeholder="필요한 데이터에 대한 상세 설명을 입력하세요..."
                    value={requestForm.data_description}
                    onChange={(e) => setRequestForm({...requestForm, data_description: e.target.value})}
                    rows={3}
                  />
                </div>

                {/* 요청 필드 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">요청 필드 (복수 선택 가능)</label>
                  {requestForm.data_category ? (
                    <div className="grid grid-cols-2 gap-2 p-3 border border-gray-300 rounded-lg">
                      {(() => {
                        const fieldsByCategory: Record<string, Array<{id: string, label: string}>> = {
                          '온실가스 배출량 데이터': [
                            { id: 'greenhouse_gas_emissions', label: '온실가스 배출량' },
                            { id: 'raw_materials', label: '원재료 정보' },
                            { id: 'manufacturing_country', label: '제조 국가' },
                            { id: 'production_plant', label: '생산 공장' },
                            { id: 'energy_density', label: '에너지 밀도' },
                            { id: 'manufacturing_date', label: '제조 일자' }
                          ],
                          '제품 안전정보 및 재활용 데이터': [
                            { id: 'safety_information', label: '안전 정보' },
                            { id: 'recycled_material', label: '재활용 소재 여부' },
                            { id: 'disposal_method', label: '폐기 방법' },
                            { id: 'recycling_method', label: '재활용 방법' },
                            { id: 'product_name', label: '제품명' },
                            { id: 'capacity', label: '용량' }
                          ],
                          '원재료 공급원 추적 데이터': [
                            { id: 'raw_materials', label: '원재료 정보' },
                            { id: 'raw_material_sources', label: '원재료 공급원' },
                            { id: 'manufacturing_country', label: '제조 국가' },
                            { id: 'production_plant', label: '생산 공장' },
                            { id: 'product_name', label: '제품명' },
                            { id: 'manufacturing_date', label: '제조 일자' }
                          ],
                          '화학물질 구성 데이터': [
                            { id: 'chemical_composition', label: '화학물질 구성' },
                            { id: 'safety_information', label: '안전 정보' },
                            { id: 'product_name', label: '제품명' },
                            { id: 'raw_materials', label: '원재료 정보' },
                            { id: 'manufacturing_date', label: '제조 일자' },
                            { id: 'capacity', label: '용량' }
                          ]
                        };
                        
                        const availableFields = fieldsByCategory[requestForm.data_category] || [];
                        
                        return availableFields.map((field: {id: string, label: string}) => (
                          <label key={field.id} className="flex items-center space-x-2 text-sm">
                            <input
                              type="checkbox"
                              checked={requestForm.requested_fields.includes(field.id)}
                              onChange={(e) => {
                                const updatedFields = e.target.checked
                                  ? [...requestForm.requested_fields.split(',').filter(f => f), field.id]
                                  : requestForm.requested_fields.split(',').filter(f => f !== field.id);
                                setRequestForm({...requestForm, requested_fields: updatedFields.join(',')});
                              }}
                              className="rounded"
                            />
                            <span>{field.label}</span>
                          </label>
                        ));
                      })()}
                    </div>
                  ) : (
                    <div className="p-3 border border-gray-300 rounded-lg bg-gray-50">
                      <p className="text-sm text-gray-500">먼저 데이터 카테고리를 선택해주세요</p>
                    </div>
                  )}
                </div>

                {/* 사용 목적 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">사용 목적</label>
                  <select
                    value={requestForm.purpose}
                    onChange={(e) => setRequestForm({...requestForm, purpose: e.target.value})}
                    className="w-full p-2 border border-gray-300 rounded-lg"
                  >
                    <option value="">사용 목적을 선택하세요</option>
                    <option value="배터리 LCA 분석 및 탄소발자국 계산을 위한 ESG 보고서 작성">배터리 LCA 분석 및 탄소발자국 계산</option>
                    <option value="제품 안전성 검증 및 순환경제 보고서 작성">제품 안전성 검증 및 순환경제 보고서 작성</option>
                    <option value="공급망 투명성 확보 및 원재료 ESG 리스크 평가">공급망 투명성 확보 및 ESG 리스크 평가</option>
                    <option value="제품 안전성 평가 및 규제 준수 확인">제품 안전성 평가 및 규제 준수 확인</option>
                    <option value="기타">기타 (직접 입력)</option>
                  </select>
                  {requestForm.purpose === '기타' && (
                    <Textarea
                      placeholder="기타 사용 목적을 상세히 입력해주세요..."
                      className="mt-2"
                      rows={2}
                    />
                  )}
                </div>

                {/* 사용 기간 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">사용 기간 (선택사항)</label>
                  <Input
                    placeholder="예: 2024년 1분기, 6개월간 등"
                    value={requestForm.usage_period}
                    onChange={(e) => setRequestForm({...requestForm, usage_period: e.target.value})}
                  />
                </div>

                {/* 긴급도 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">긴급도</label>
                  <select
                    value={requestForm.urgency_level}
                    onChange={(e) => setRequestForm({...requestForm, urgency_level: e.target.value})}
                    className="w-full p-2 border border-gray-300 rounded-lg"
                  >
                    <option value="low">낮음</option>
                    <option value="normal">보통</option>
                    <option value="high">높음</option>
                  </select>
                </div>
              </div>
              
              <div className="flex gap-3 mt-6">
                <Button
                  onClick={handleCreateRequest}
                  className="flex-1 bg-blue-600 hover:bg-blue-700"
                  disabled={!requestForm.provider_company_id || !requestForm.data_category || !requestForm.purpose}
                >
                  <Send className="h-4 w-4 mr-2" />
                  요청 전송
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setShowRequestForm(false)}
                  className="flex-1"
                >
                  취소
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 상세보기 모달 */}
      {selectedRequest && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">요청 상세 정보</h2>
                <Button
                  variant="ghost"
                  onClick={() => setSelectedRequest(null)}
                >
                  ✕
                </Button>
              </div>
              
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700">요청 대상</label>
                    <p className="text-sm text-gray-900">{selectedRequest.provider_company_name}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">요청일</label>
                    <p className="text-sm text-gray-900">
                      {new Date(selectedRequest.requested_at).toLocaleString('ko-KR')}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">데이터 타입</label>
                    <p className="text-sm text-gray-900">{selectedRequest.data_type}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">상태</label>
                    <Badge className={getStatusInfo(selectedRequest.status).color}>
                      {getStatusInfo(selectedRequest.status).text}
                    </Badge>
                  </div>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-700">데이터 카테고리</label>
                  <p className="text-sm text-gray-900 mt-1">{selectedRequest.data_category}</p>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-700">사용 목적</label>
                  <p className="text-sm text-gray-900 mt-1">{selectedRequest.purpose}</p>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-700">데이터 설명</label>
                  <p className="text-sm text-gray-900 mt-1">{selectedRequest.data_description}</p>
                </div>

                {selectedRequest.review_comment && (
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <label className="text-sm font-medium text-gray-700">검토 의견</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedRequest.review_comment}</p>
                    {selectedRequest.reviewer_name && (
                      <p className="text-xs text-gray-500 mt-1">
                        검토자: {selectedRequest.reviewer_name}
                      </p>
                    )}
                  </div>
                )}

                {selectedRequest.status === 'completed' && selectedRequest.data_url && (
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <label className="text-sm font-medium text-blue-700">데이터 다운로드</label>
                    <div className="mt-2">
                      <Button
                        onClick={() => window.open(selectedRequest.data_url, '_blank')}
                        className="bg-blue-600 hover:bg-blue-700"
                      >
                        <Download className="h-4 w-4 mr-2" />
                        데이터 다운로드
                      </Button>
                      {selectedRequest.expiry_date && (
                        <p className="text-xs text-blue-600 mt-1">
                          만료일: {new Date(selectedRequest.expiry_date).toLocaleString('ko-KR')}
                        </p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

  // 요청 목록 렌더링 함수
function renderRequestList(
  requests: SharingRequest[], 
  searchTerm: string, 
  setSearchTerm: (term: string) => void, 
  setSelectedRequest: (request: SharingRequest | null) => void, 
  getStatusInfo: (status: string) => any, 
  getUrgencyColor: (urgency: string) => string,
  suppliers: SupplierData[]
) {
    if (requests.length === 0) {
      return (
        <Card>
          <CardContent className="p-8 text-center">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">해당하는 요청이 없습니다.</p>
          </CardContent>
        </Card>
      );
    }

    return (
      <>
        {/* 검색 */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder="협력사명, 데이터 카테고리, 사용 목적으로 검색..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>

        {requests.map((request) => {
          const statusInfo = getStatusInfo(request.status);
          const StatusIcon = statusInfo.icon;
        const isStrategicSupplier = suppliers.find((s: SupplierData) => s.name === request.provider_company_name)?.isStrategic;
          
          return (
          <Card key={request.id} className={`hover:shadow-md transition-shadow ${
            isStrategicSupplier 
              ? (() => {
                  const supplierData = suppliers.find(s => s.name === request.provider_company_name);
                  const status = supplierData?.status;
                  return status === 'completed' ? 'bg-green-50 border-l-4 border-l-green-500' :
                         status === 'pending' ? 'bg-yellow-50 border-l-4 border-l-yellow-500' :
                         status === 'approved' ? 'bg-blue-50 border-l-4 border-l-blue-500' :
                         'bg-yellow-50 border-l-4 border-l-yellow-500'; // 기본값
                })()
              : ''
          }`}>
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {request.data_category}
                      </h3>
                      <Badge className={statusInfo.color}>
                        <StatusIcon className="h-3 w-3 mr-1" />
                        {statusInfo.text}
                      </Badge>
                      <Badge className={getUrgencyColor(request.urgency_level)}>
                        {request.urgency_level === 'high' ? '긴급' : 
                         request.urgency_level === 'normal' ? '보통' : '낮음'}
                      </Badge>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
                      <div className="flex items-center gap-2">
                        <Building2 className="h-4 w-4" />
                        <span>요청 대상: {request.provider_company_name}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4" />
                        <span>요청일: {new Date(request.requested_at).toLocaleDateString('ko-KR')}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4" />
                        <span>데이터 타입: {request.data_type}</span>
                      </div>
                      {request.usage_period && (
                        <div className="flex items-center gap-2">
                          <Clock className="h-4 w-4" />
                          <span>사용 기간: {request.usage_period}</span>
                        </div>
                      )}
                    </div>
                    
                    <div className="mt-3">
                      <p className="text-sm text-gray-700">
                        <span className="font-medium">사용 목적:</span> {request.purpose}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex flex-col gap-2 ml-4">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setSelectedRequest(request)}
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      상세보기
                    </Button>
                    
                    {request.status === 'completed' && request.data_url && (
                      <Button
                        size="sm"
                        onClick={() => window.open(request.data_url, '_blank')}
                        className="bg-blue-600 hover:bg-blue-700"
                      >
                        <Download className="h-4 w-4 mr-1" />
                        다운로드
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </>
    );
  }

export default SupplierRequestPage;