"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { 
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
  ArrowLeft,
  TrendingUp
} from "lucide-react";
import { api } from "@/lib/api";
import Navigation from "@/components/Navigation"; // Added Navigation import

// 동적 Mock 데이터 생성 함수
const generateMockRequests = (companyInfo: any): SharingRequest[] => {
  if (!companyInfo.hasUpperTier) {
    // 원청사는 요청을 받지 않음
    return [];
  }
  
  const upperTierInfo = {
    id: `TIER${companyInfo.upperTier}_MAIN`,
    name: `${companyInfo.upperTier === 0 ? "🏭 원청사" : `${["", "🔧", "⚙️", "🔩", "📦"][companyInfo.upperTier]} ${companyInfo.upperTier}차사`} (메인)`
  };
  
  return [
    {
      id: "req-001",
      requester_company_id: upperTierInfo.id,
      requester_company_name: upperTierInfo.name,
      provider_company_id: companyInfo.companyId,
      provider_company_name: companyInfo.companyName,
      data_type: "sustainability",
      data_category: `배터리 공급망 통합 온실가스 배출량`,
      data_description: `${companyInfo.companyTier}차사 직접 생산 + 하위 협력사들로부터 취합한 18650 배터리 셀 제조공정별 온실가스 배출량 통합 데이터 (Scope 1,2,3 포함)`,
      purpose: "배터리 LCA 분석 및 탄소중립 로드맵 수립을 위한 전체 공급망 탄소발자국 계산",
      urgency_level: "high",
      status: "pending",
      requested_at: "2025-08-30T10:30:00Z",
      requested_fields: JSON.stringify([
        `tier${companyInfo.companyTier}_direct_emissions`, 
        `tier${companyInfo.lowerTier}_aggregated_emissions`, 
        `tier${companyInfo.lowerTier + 1}_aggregated_emissions`, 
        "total_supply_chain_emissions", 
        "data_collection_status", 
        "missing_suppliers"
      ])
    },
    {
      id: "req-002", 
      requester_company_id: upperTierInfo.id,
      requester_company_name: upperTierInfo.name,
      provider_company_id: companyInfo.companyId,
      provider_company_name: companyInfo.companyName, 
      data_type: "sustainability",
      data_category: `배터리 공급망 통합 안전정보 및 재활용 데이터`,
      data_description: `${companyInfo.companyTier}차사 + 하위 협력사들의 UN38.3 안전성 시험성적서, MSDS, 재활용 소재 함량비율 및 폐배터리 처리방법 통합 현황`,
      purpose: "배터리 제품 안전성 검증 및 순환경제 보고서 작성을 위한 공급망 전체 안전성 및 재활용 데이터 분석",
      urgency_level: "normal",
      status: "pending",
      requested_at: "2025-08-29T14:20:00Z",
      requested_fields: JSON.stringify([
        `tier${companyInfo.companyTier}_direct_capacity`, 
        `aggregated_tier${companyInfo.lowerTier}_capacity`, 
        `aggregated_tier${companyInfo.lowerTier + 1}_capacity`, 
        "bottleneck_analysis", 
        "supply_risk_assessment"
      ])
    },
    {
      id: "req-003",
      requester_company_id: upperTierInfo.id,
      requester_company_name: upperTierInfo.name,
      provider_company_id: companyInfo.companyId,
      provider_company_name: companyInfo.companyName,
      data_type: "sustainability",
      data_category: `배터리 원재료 공급원 추적 데이터`, 
      data_description: `리튬, 니켈, 코발트, 흑연 등 배터리 핵심 원재료의 원산지 추적정보 - 광산별 채굴조건 및 ESG 인증현황 통합`,
      purpose: "배터리 공급망 투명성 확보 및 원재료 ESG 리스크 평가",
      urgency_level: "normal",
      status: "approved",
      requested_at: "2025-08-28T09:15:00Z",
      reviewed_at: "2025-08-29T11:30:00Z",
      approved_at: "2025-08-29T11:30:00Z",
      reviewer_id: companyInfo.userId,
      reviewer_name: companyInfo.userName,
      review_comment: `하위 배터리 협력사들로부터 원재료 추적 데이터 취합 완료. 리튬 광산 ESG 인증현황 포함하여 ${companyInfo.companyTier}차사 직접 + ${companyInfo.lowerTier}차~${companyInfo.lowerTier + 1}차 통합 원산지 데이터 제공하겠습니다. (수집률: ${companyInfo.lowerTier}차 100%, ${companyInfo.lowerTier + 1}차 85%)`
    },
    {
      id: "req-004",
      requester_company_id: upperTierInfo.id,
      requester_company_name: upperTierInfo.name, 
      provider_company_id: companyInfo.companyId,
      provider_company_name: companyInfo.companyName,
      data_type: "sustainability",
      data_category: `배터리 화학물질 구성 데이터`,
      data_description: `배터리 전극 활물질, 바인더, 전해질의 화학적 조성정보 - 납, 카드뮴, 수은 등 유해물질 함량 및 REACH 규제 준수현황`,
      purpose: "배터리 제품 안전성 평가 및 유럽 REACH 규제 준수 확인",
      urgency_level: "low", 
      status: "rejected",
      requested_at: "2025-08-27T16:45:00Z",
      reviewed_at: "2025-08-28T10:20:00Z",
      reviewer_id: `${companyInfo.companyId}_TECH`,
      reviewer_name: `박기술 (${companyInfo.companyTier}차사 ${companyInfo.companyCode})`,
      review_comment: `배터리 전극 활물질의 정확한 화학조성은 핵심 기술정보로 분류되어 직접 공유가 어렵습니다. 대신 유해물질 함량 테스트 결과서 및 REACH 준수 인증서로 대체 제공 가능합니다.`
    },
    {
      id: "req-005",
      requester_company_id: upperTierInfo.id,
      requester_company_name: upperTierInfo.name,
      provider_company_id: companyInfo.companyId, 
      provider_company_name: companyInfo.companyName,
      data_type: "sustainability",
      data_category: `배터리 제조공정 에너지 사용현황`,
      data_description: `배터리 셀 제조공정별 에너지 사용량 (전력, 가스, 연료) 및 재생에너지 비율 - 전극코팅, 조립, 화성공정 단계별 포함`,
      purpose: "배터리 Scope 3 배출량 산정 및 RE100 달성을 위한 제조공정 에너지 현황 파악",
      urgency_level: "high",
      status: "completed",
      requested_at: "2025-08-26T08:00:00Z",
      reviewed_at: "2025-08-26T15:30:00Z", 
      approved_at: "2025-08-26T15:30:00Z",
      completed_at: "2025-08-27T09:00:00Z",
      reviewer_id: companyInfo.userId,
      reviewer_name: companyInfo.userName,
      review_comment: `하위 배터리 협력사들의 제조공정별 에너지 데이터 취합 완료. ${companyInfo.companyTier}차사 직접 생산공정 + ${companyInfo.lowerTier}차(4개사) + ${companyInfo.lowerTier + 1}차(8개사) 통합 에너지 사용량 및 재생에너지 비율 데이터 전송 완료. 수집률 98%`,
      data_url: `https://${companyInfo.companyId.toLowerCase()}-data.company.com/download/supply-chain-energy-2023`,
      expiry_date: "2025-09-27T09:00:00Z"
    }
  ];
};
// 동적으로 생성된 Mock 데이터 사용 (컴포넌트 내부에서 호출)

// Mock 통계 데이터 (자동 계산)
const calculateMockStats = (requests: SharingRequest[]) => {
  const pendingRequests = requests.filter(r => r.status === 'pending');
  const urgentPendingRequests = pendingRequests.filter(r => r.urgency_level === 'high');
  
  // 실제 응답 시간 계산 (처리된 요청들만)
  const processedRequests = requests.filter(r => r.reviewed_at && r.requested_at);
  let avgResponseTime = 0;
  
  if (processedRequests.length > 0) {
    const totalResponseTime = processedRequests.reduce((sum, request) => {
      const requestedTime = new Date(request.requested_at).getTime();
      const reviewedTime = new Date(request.reviewed_at!).getTime();
      const diffHours = (reviewedTime - requestedTime) / (1000 * 60 * 60);
      return sum + diffHours;
    }, 0);
    avgResponseTime = Math.round((totalResponseTime / processedRequests.length) * 10) / 10;
  }
  
  return {
    total_requests: requests.length,
    pending_requests: pendingRequests.length,
    urgent_pending_requests: urgentPendingRequests.length, // 긴급 검토 필요한 것들
    approved_requests: requests.filter(r => r.status === 'approved').length,
    rejected_requests: requests.filter(r => r.status === 'rejected').length,
    completed_requests: requests.filter(r => r.status === 'completed').length,
    avg_response_time_hours: avgResponseTime || 16.2 // 기본값으로 fallback
  };
};

// 타입 정의
interface SharingRequest {
  id: string;
  requester_company_id: string;
  requester_company_name: string;
  provider_company_id: string;
  provider_company_name: string;
  data_type: string;
  data_category: string;
  data_description: string;
  requested_fields?: string;
  purpose: string;
  usage_period?: string;
  urgency_level: string;
  status: 'pending' | 'approved' | 'rejected' | 'completed';
  requested_at: string;
  reviewed_at?: string;
  approved_at?: string;
  completed_at?: string;
  reviewer_id?: string;
  reviewer_name?: string;
  review_comment?: string;
  data_url?: string;
  expiry_date?: string;
}

interface Stats {
  total_requests: number;
  pending_requests: number;
  urgent_pending_requests: number;
  approved_requests: number;
  rejected_requests: number;
  completed_requests: number;
  avg_response_time_hours: number;
}

const DataSharingPage = () => {
  const [requests, setRequests] = useState<SharingRequest[]>([]);
  const [stats, setStats] = useState<Stats>({
    total_requests: 0,
    pending_requests: 0,
    urgent_pending_requests: 0,
    approved_requests: 0,
    rejected_requests: 0,
    completed_requests: 0,
    avg_response_time_hours: 0
  });
  const [loading, setLoading] = useState(true);
  const [selectedRequest, setSelectedRequest] = useState<SharingRequest | null>(null);
  const [activeTab, setActiveTab] = useState("pending");
  const [searchTerm, setSearchTerm] = useState("");
  const [reviewComment, setReviewComment] = useState("");
  
  // 동적 회사 정보 설정 (클라이언트 사이드만)
  const [companyInfo, setCompanyInfo] = useState({
    companyId: "TIER0_A",
    companyName: "🏭 원청사 A (우리회사)",
    companyTier: 0,
    companyCode: "A",
    userId: "USER_TIER0_A_001",
    userName: "김담당 (원청사 A 데이터 관리자)",
    upperTier: -1,
    lowerTier: 1,
    hasUpperTier: false,
    hasLowerTier: true
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
    } else {
      companyTier = 0; // 기본값: 원청사
    }
    
    const companyCode = "A"; // A, B, C 등
    const companyId = `TIER${companyTier}_${companyCode}`;
    
    const tierNames = {
      0: "원청사",
      1: "1차사",
      2: "2차사",
      3: "3차사",
      4: "4차사"
    };
    
    const tierIcons = {
      0: "🏭",
      1: "🔧",
      2: "⚙️",
      3: "🔩",
      4: "📦"
    };
    
    setCompanyInfo({
      companyId,
      companyName: `${tierIcons[companyTier]} ${tierNames[companyTier]} ${companyCode} (우리회사)`,
      companyTier,
      companyCode,
      userId: `USER_${companyId}_001`,
      userName: `김담당 (${tierNames[companyTier]} ${companyCode} 데이터 관리자)`,
      upperTier: companyTier - 1,
      lowerTier: companyTier + 1,
      hasUpperTier: companyTier > 0,
      hasLowerTier: companyTier < 4 // 최대 4차까지 가정
    });
  }, []);
const currentCompanyId = companyInfo.companyId;
const currentCompanyName = companyInfo.companyName;
const currentUserId = companyInfo.userId;

// 원청사 접근 권한 체크
const isOriginalEquipmentManufacturer = companyInfo.companyTier === 0;
const hasApprovalPageAccess = companyInfo.hasUpperTier; // 상위 tier가 있어야 승인 페이지 사용 가능
const currentUserName = companyInfo.userName;

// 동적으로 생성된 Mock 데이터
const MOCK_REQUESTS = generateMockRequests(companyInfo);

  // 데이터 로드
  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Mock 데이터 사용 (백엔드 연결 전까지)
      const useMockData = true; // 나중에 false로 변경
      
      if (useMockData) {
        // Mock 데이터 필터링
        let filteredRequests = MOCK_REQUESTS;
        if (activeTab !== "all") {
          filteredRequests = MOCK_REQUESTS.filter(req => req.status === activeTab);
        }
        
        setRequests(filteredRequests);
        // 실제 요청 데이터를 기반으로 통계 자동 계산
        setStats(calculateMockStats(MOCK_REQUESTS));
        
        // 실제 API 호출 시뮬레이션을 위한 지연
        await new Promise(resolve => setTimeout(resolve, 500));
      } else {
        // 실제 API 호출 (백엔드 연결 시 사용)
        const statusFilter = activeTab === "all" ? undefined : activeTab;
        const requestsResponse = await api(`/sharing/provider/${currentCompanyId}${statusFilter ? `?status=${statusFilter}` : ''}`);
        
        if (requestsResponse.status === "success") {
          setRequests(requestsResponse.data.requests || []);
        }
        
        // 통계 조회
        const statsResponse = await api(`/sharing/stats/${currentCompanyId}`);
        if (statsResponse.status === "success") {
          setStats(statsResponse.data);
        }
      }
      
    } catch (error) {
      console.error("데이터 로드 실패:", error);
      // 사용자 친화적 에러 메시지
      alert("⚠️ 데이터를 불러오는 중 문제가 발생했습니다.\n잠시 후 다시 시도해주세요.");
      
      // 오류 시 빈 데이터로 초기화
      setRequests([]);
      setStats({
        total_requests: 0,
        pending_requests: 0,
        urgent_pending_requests: 0,
        approved_requests: 0,
        rejected_requests: 0,
        completed_requests: 0,
        avg_response_time_hours: 0
      });
    } finally {
      setLoading(false);
    }
  };

  // 요청 승인
  const handleApprove = async (requestId: string) => {
    try {
      // Mock 모드에서는 API 호출 없이 성공 처리
      const useMockData = true;
      
      if (useMockData) {
        // Mock 데이터에서 상태 변경 시뮬레이션
        setRequests(prev => prev.map(req => 
          req.id === requestId 
            ? { 
                ...req, 
                status: 'approved' as const,
                reviewed_at: new Date().toISOString(),
                approved_at: new Date().toISOString(),
                reviewer_id: currentUserId,
                reviewer_name: currentUserName,
                review_comment: reviewComment || "승인되었습니다."
              }
            : req
        ));
        
        // 통계 자동 업데이트
        setStats(prevStats => ({
          ...prevStats,
          pending_requests: Math.max(0, prevStats.pending_requests - 1),
          approved_requests: prevStats.approved_requests + 1
        }));
        
        alert("✅ 요청이 승인되었습니다!\n하위 협력사들로부터 데이터 수집을 시작합니다.");
        setSelectedRequest(null);
        setReviewComment("");
        return;
      }
      
      const response = await api(`/sharing/${requestId}/approve?reviewer_id=${currentUserId}&reviewer_name=${encodeURIComponent(currentUserName)}&comment=${encodeURIComponent(reviewComment)}`, {
        method: 'PUT'
      });
      
      if (response.status === "success") {
        alert("요청이 승인되었습니다.");
        setSelectedRequest(null);
        setReviewComment("");
        loadData();
      } else {
        alert("❌ 승인 처리 중 문제가 발생했습니다.\n네트워크 상태를 확인하고 다시 시도해주세요.");
      }
    } catch (error) {
      console.error("승인 처리 실패:", error);
      alert("❌ 승인 처리 중 문제가 발생했습니다.\n네트워크 상태를 확인하고 다시 시도해주세요.");
    }
  };

  // 요청 거부
  const handleReject = async (requestId: string) => {
    if (!reviewComment.trim()) {
      alert("⚠️ 거부 사유를 입력해주세요.\n명확한 사유를 작성하면 협력사가 이해하기 쉽습니다.");
      return;
    }
    
    try {
      // Mock 모드에서는 API 호출 없이 성공 처리
      const useMockData = true;
      
      if (useMockData) {
        // Mock 데이터에서 상태 변경 시뮬레이션
        setRequests(prev => prev.map(req => 
          req.id === requestId 
            ? { 
                ...req, 
                status: 'rejected' as const,
                reviewed_at: new Date().toISOString(),
                reviewer_id: currentUserId,
                reviewer_name: currentUserName,
                review_comment: reviewComment
              }
            : req
        ));
        
        // 통계 자동 업데이트
        setStats(prevStats => ({
          ...prevStats,
          pending_requests: Math.max(0, prevStats.pending_requests - 1),
          rejected_requests: prevStats.rejected_requests + 1
        }));
        
        alert("⚠️ 요청이 거부되었습니다.\n거부 사유가 요청사에게 전달되었습니다.");
        setSelectedRequest(null);
        setReviewComment("");
        return;
      }
      
      const response = await api(`/sharing/${requestId}/reject?reviewer_id=${currentUserId}&reviewer_name=${encodeURIComponent(currentUserName)}&comment=${encodeURIComponent(reviewComment)}`, {
        method: 'PUT'
      });
      
      if (response.status === "success") {
        alert("요청이 거부되었습니다.");
        setSelectedRequest(null);
        setReviewComment("");
        loadData();
      } else {
        alert("거부 처리 중 오류가 발생했습니다.");
      }
    } catch (error) {
      console.error("거부 처리 실패:", error);
      alert("거부 처리 중 오류가 발생했습니다.");
    }
  };

  // 데이터 전송 (승인된 요청에 대해)
  const handleSendData = async (requestId: string) => {
    try {
      // Mock 모드에서는 API 호출 없이 성공 처리
      const useMockData = true;
      
      if (useMockData) {
        // Mock 데이터에서 상태 변경 시뮬레이션
        setRequests(prev => prev.map(req => 
          req.id === requestId 
            ? { 
                ...req, 
                status: 'completed' as const,
                completed_at: new Date().toISOString(),
                data_url: `https://mock-data-${requestId}.company.com/download`,
                expiry_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString() // 30일 후
              }
            : req
        ));
        
        // 통계 자동 업데이트
        setStats(prevStats => ({
          ...prevStats,
          approved_requests: Math.max(0, prevStats.approved_requests - 1),
          completed_requests: prevStats.completed_requests + 1
        }));
        
        alert("📤 데이터가 성공적으로 전송되었습니다!\n요청사가 다운로드할 수 있습니다.");
        return;
      }
      
      // 실제로는 데이터를 준비하고 URL을 생성해야 함
      const dataUrl = `https://data.example.com/download/${requestId}`;
      
      const response = await api(`/sharing/${requestId}/send?data_url=${encodeURIComponent(dataUrl)}`, {
        method: 'POST'
      });
      
      if (response.status === "success") {
        alert("데이터가 성공적으로 전송되었습니다.");
        loadData();
      } else {
        alert("데이터 전송 중 오류가 발생했습니다.");
      }
    } catch (error) {
      console.error("데이터 전송 실패:", error);
      alert("데이터 전송 중 오류가 발생했습니다.");
    }
  };

  // 상태별 색상 및 아이콘
  const getStatusInfo = (status: string) => {
    switch (status) {
      case 'pending':
        return { color: 'bg-yellow-100 text-yellow-800', icon: Clock, text: '검토 대기' };
      case 'approved':
        return { color: 'bg-green-100 text-green-800', icon: CheckCircle, text: '승인됨' };
      case 'rejected':
        return { color: 'bg-red-100 text-red-800', icon: XCircle, text: '거부됨' };
      case 'completed':
        return { color: 'bg-blue-100 text-blue-800', icon: CheckCircle, text: '전송완료' };
      default:
        return { color: 'bg-gray-100 text-gray-800', icon: AlertCircle, text: '알 수 없음' };
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

  // 필터링 및 정렬된 요청 목록
  const filteredRequests = requests
    .filter(request =>
      request.requester_company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      request.data_category.toLowerCase().includes(searchTerm.toLowerCase()) ||
      request.purpose.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      // 긴급도 확인
      const aIsUrgent = a.urgency_level === 'high';
      const bIsUrgent = b.urgency_level === 'high';
      
      // pending 상태 확인
      const aIsPending = a.status === 'pending';
      const bIsPending = b.status === 'pending';
      
      // 1. 긴급 + pending (최우선)
      const aUrgentPending = aIsUrgent && aIsPending;
      const bUrgentPending = bIsUrgent && bIsPending;
      if (aUrgentPending && !bUrgentPending) return -1;
      if (!aUrgentPending && bUrgentPending) return 1;
      
      // 2. 긴급 요청
      if (aIsUrgent && !bIsUrgent) return -1;
      if (!aIsUrgent && bIsUrgent) return 1;
      
      // 3. pending 상태 (검토 대기)
      if (aIsPending && !bIsPending) return -1;
      if (!aIsPending && bIsPending) return 1;
      
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

  // 원청사 접근 제한
  if (!hasApprovalPageAccess) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
        <Card className="max-w-md mx-auto">
          <CardContent className="p-8 text-center">
            <div className="mb-6">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Building2 className="w-8 h-8 text-blue-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">원청사 계정</h2>
              <p className="text-gray-600">
                원청사는 데이터 승인 페이지에 접근할 수 없습니다.
              </p>
            </div>
            <div className="space-y-4">
              <p className="text-sm text-gray-500">
                원청사는 협력사들에게 데이터를 요청하는 역할만 수행합니다.
              </p>
              <div className="space-y-2">
                <Button 
                  onClick={() => {
                    // URL 파라미터로 원청사 역할로 접근
                    window.open('/data-sharing-request?role=prime', '_blank');
                  }} 
                  className="w-full"
                >
                  데이터 요청 페이지로 이동 (원청사 역할)
                </Button>
                <p className="text-xs text-gray-400 text-center">
                  테스트용: 원청사 관점에서 요청 페이지 체험
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
                <a href="/data-sharing-approval" className="text-blue-600 border-b-2 border-blue-600 px-3 py-2 text-sm font-medium">
                  데이터 승인
                </a>
                <a href="/data-sharing-request" className="text-gray-500 hover:text-gray-700 px-3 py-2 text-sm font-medium">
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
            <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
              {activeTab === 'all' && '데이터 공유 승인'}
              {activeTab === 'pending' && (
                <>
                  <AlertCircle className="h-8 w-8 text-yellow-500 animate-pulse" />
                  검토 대기 중인 요청
                </>
              )}
              {activeTab === 'approved' && '승인된 요청'}
              {activeTab === 'rejected' && '거부된 요청'}
              {activeTab === 'completed' && '전송 완료된 요청'}
            </h1>
            <p className="text-gray-600">
              {activeTab === 'all' && (
                companyInfo.hasUpperTier ? 
                  `상위 ${companyInfo.upperTier === 0 ? '원청사' : '협력사'}로부터 받은 통합 데이터 요청을 검토합니다. 승인 시 하위 협력사들로부터 계층적으로 데이터를 수집하여 통합 데이터를 제공합니다.` :
                  '원청사는 데이터 요청을 받지 않습니다.'
              )}
              {activeTab === 'pending' && '상위 협력사로부터 받은 데이터 요청 중 검토가 필요한 목록입니다.'}
              {activeTab === 'approved' && '승인한 데이터 요청 목록입니다. 하위 협력사들로부터 데이터를 수집 중입니다.'}
              {activeTab === 'rejected' && '거부한 데이터 요청 목록입니다. 거부 사유를 확인할 수 있습니다.'}
              {activeTab === 'completed' && '데이터 수집 및 전송이 완료된 요청 목록입니다.'}
            </p>
          </div>
          
          {/* 빠른 액션 버튼들 */}
          <div className="flex items-center gap-3">
            {stats.urgent_pending_requests > 0 && (
              <Button
                onClick={() => setActiveTab("pending")}
                className="bg-red-600 hover:bg-red-700 text-white shadow-lg animate-pulse"
                size="sm"
              >
                <TrendingUp className="h-4 w-4 mr-2" />
                긴급 검토 ({stats.urgent_pending_requests})
              </Button>
            )}
            
            <Button
              onClick={loadData}
              variant="outline"
              size="default"
              className="border-gray-300 hover:bg-gray-50 px-4 py-2"
            >
              <ArrowLeft className="h-5 w-5 mr-2" />
              새로고침
            </Button>
          </div>
        </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        <Card className="hover:shadow-lg transition-all duration-200 cursor-pointer hover:scale-105">
          <CardContent className="p-4" onClick={() => setActiveTab("all")}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">전체 요청</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_requests}</p>
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
        
        <Card className={`hover:shadow-lg transition-all duration-200 cursor-pointer hover:scale-105 hover:bg-yellow-50 ${
          stats.pending_requests > 0 ? 'ring-2 ring-yellow-400 ring-opacity-50 animate-pulse' : ''
        }`}>
          <CardContent className="p-4" onClick={() => setActiveTab("pending")}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 flex items-center gap-1">
                  검토 대기
                  {stats.pending_requests > 0 && <AlertCircle className="h-3 w-3 text-yellow-500" />}
                </p>
                <p className="text-2xl font-bold text-yellow-600">{stats.pending_requests}</p>
                {stats.pending_requests > 0 && (
                  <p className="text-xs text-yellow-700 font-medium">즉시 검토 필요!</p>
                )}
              </div>
              <Clock className="h-8 w-8 text-yellow-400" />
            </div>
            <div className="mt-2">
              <div className="w-full h-1 bg-yellow-200 rounded-full">
                <div 
                  className="h-1 bg-yellow-500 rounded-full transition-all duration-300" 
                  style={{ width: `${stats.total_requests > 0 ? (stats.pending_requests / stats.total_requests) * 100 : 0}%` }}
                ></div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="hover:shadow-lg transition-all duration-200 cursor-pointer hover:scale-105 hover:bg-green-50">
          <CardContent className="p-4" onClick={() => setActiveTab("approved")}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">승인됨</p>
                <p className="text-2xl font-bold text-green-600">{stats.approved_requests}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-400" />
            </div>
            <div className="mt-2">
              <div className="w-full h-1 bg-green-200 rounded-full">
                <div 
                  className="h-1 bg-green-500 rounded-full transition-all duration-300" 
                  style={{ width: `${stats.total_requests > 0 ? (stats.approved_requests / stats.total_requests) * 100 : 0}%` }}
                ></div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="hover:shadow-lg transition-all duration-200 cursor-pointer hover:scale-105 hover:bg-red-50">
          <CardContent className="p-4" onClick={() => setActiveTab("rejected")}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">거부됨</p>
                <p className="text-2xl font-bold text-red-600">{stats.rejected_requests}</p>
              </div>
              <XCircle className="h-8 w-8 text-red-400" />
            </div>
            <div className="mt-2">
              <div className="w-full h-1 bg-red-200 rounded-full">
                <div 
                  className="h-1 bg-red-500 rounded-full transition-all duration-300" 
                  style={{ width: `${stats.total_requests > 0 ? (stats.rejected_requests / stats.total_requests) * 100 : 0}%` }}
                ></div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="hover:shadow-lg transition-all duration-200 cursor-pointer hover:scale-105 hover:bg-blue-50">
          <CardContent className="p-4" onClick={() => setActiveTab("completed")}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">전송완료</p>
                <p className="text-2xl font-bold text-blue-600">{stats.completed_requests}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-blue-400" />
            </div>
            <div className="mt-2">
              <div className="w-full h-1 bg-blue-200 rounded-full">
                <div 
                  className="h-1 bg-blue-500 rounded-full transition-all duration-300" 
                  style={{ width: `${stats.total_requests > 0 ? (stats.completed_requests / stats.total_requests) * 100 : 0}%` }}
                ></div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 검색 및 필터 */}
      <div className="flex flex-col sm:flex-row gap-4 mb-8">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
          <Input
            placeholder="회사명, 데이터 카테고리, 사용 목적으로 검색..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-12 py-4 text-lg border-2 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-opacity-20 shadow-sm rounded-lg"
          />
        </div>
      </div>

      {/* 탭 컨테이너 (네비게이션 바 제거) */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">

        <TabsContent value={activeTab} className="space-y-4">
          {filteredRequests.length === 0 ? (
            <Card>
              <CardContent className="p-8 text-center">
                <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">해당하는 데이터 공유 요청이 없습니다.</p>
              </CardContent>
            </Card>
          ) : (
            filteredRequests.map((request) => {
              const statusInfo = getStatusInfo(request.status);
              const StatusIcon = statusInfo.icon;
              
              return (
                <Card key={request.id} className={`hover:shadow-md transition-shadow ${
                  request.urgency_level === 'high' && request.status === 'pending' ? 'border-2 border-red-500 shadow-lg shadow-red-200' : ''
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
                            <span>요청사: {request.requester_company_name}</span>
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
                          <p className="text-sm text-gray-700 mt-1">
                            <span className="font-medium">설명:</span> {request.data_description}
                          </p>
                        </div>

                        {request.review_comment && (
                          <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                            <p className="text-sm text-gray-700">
                              <span className="font-medium">검토 의견:</span> {request.review_comment}
                            </p>
                            {request.reviewer_name && (
                              <p className="text-xs text-gray-500 mt-1">
                                검토자: {request.reviewer_name}
                              </p>
                            )}
                          </div>
                        )}
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
                        

                        
                        {request.status === 'approved' && (
                          <Button
                            variant="default"
                            size="sm"
                            onClick={() => handleSendData(request.id)}
                            className="bg-blue-600 hover:bg-blue-700"
                          >
                            <Download className="h-4 w-4 mr-1" />
                            데이터 전송
                          </Button>
                        )}
                        
                        {request.status === 'completed' && request.data_url && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => window.open(request.data_url, '_blank')}
                          >
                            <Download className="h-4 w-4 mr-1" />
                            다운로드 링크
                          </Button>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })
          )}
        </TabsContent>
      </Tabs>

      {/* 상세보기/검토 모달 */}
      {selectedRequest && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">데이터 공유 요청 상세</h2>
                <Button
                  variant="ghost"
                  onClick={() => {
                    setSelectedRequest(null);
                    setReviewComment("");
                  }}
                >
                  ✕
                </Button>
              </div>
              
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700">요청사</label>
                    <p className="text-sm text-gray-900">{selectedRequest.requester_company_name}</p>
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
                    <label className="text-sm font-medium text-gray-700">데이터 카테고리</label>
                    <p className="text-sm text-gray-900">{selectedRequest.data_category}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">긴급도</label>
                    <Badge className={getUrgencyColor(selectedRequest.urgency_level)}>
                      {selectedRequest.urgency_level === 'high' ? '긴급' : 
                       selectedRequest.urgency_level === 'normal' ? '보통' : '낮음'}
                    </Badge>
                  </div>
                  {selectedRequest.usage_period && (
                    <div>
                      <label className="text-sm font-medium text-gray-700">사용 기간</label>
                      <p className="text-sm text-gray-900">{selectedRequest.usage_period}</p>
                    </div>
                  )}
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-700">사용 목적</label>
                  <p className="text-sm text-gray-900 mt-1">{selectedRequest.purpose}</p>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-700">데이터 설명</label>
                  <p className="text-sm text-gray-900 mt-1">{selectedRequest.data_description}</p>
                </div>
                
                {selectedRequest.requested_fields && (
                  <div>
                    <label className="text-sm font-medium text-gray-700">요청된 필드</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedRequest.requested_fields}</p>
                  </div>
                )}

                {selectedRequest.status === 'pending' && (
                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-2 block">검토 의견</label>
                    <Textarea
                      placeholder="검토 의견을 입력하세요..."
                      value={reviewComment}
                      onChange={(e) => setReviewComment(e.target.value)}
                      rows={4}
                    />
                  </div>
                )}

                {selectedRequest.review_comment && (
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <label className="text-sm font-medium text-gray-700">기존 검토 의견</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedRequest.review_comment}</p>
                    {selectedRequest.reviewer_name && (
                      <p className="text-xs text-gray-500 mt-1">
                        검토자: {selectedRequest.reviewer_name}
                      </p>
                    )}
                  </div>
                )}
              </div>
              
              {selectedRequest.status === 'pending' && (
                <div className="flex gap-3 mt-6">
                  <Button
                    onClick={() => handleApprove(selectedRequest.id)}
                    className="flex-1 bg-green-600 hover:bg-green-700 shadow-lg"
                  >
                    <CheckCircle className="h-4 w-4 mr-2" />
                    승인
                  </Button>
                  <Button
                    variant="destructive"
                    onClick={() => handleReject(selectedRequest.id)}
                    className="flex-1 shadow-lg"
                  >
                    <XCircle className="h-4 w-4 mr-2" />
                    거부
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      </div>
    </div>
  );
};

export default DataSharingPage;
