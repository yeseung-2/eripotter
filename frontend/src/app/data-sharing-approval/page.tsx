"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  AlertCircle,
  TrendingUp
} from "lucide-react";

import { api } from "@/lib/api";

const DataSharingPage = () => {
  // ✅ 필요한 상태값 정의
  const [activeTab, setActiveTab] = useState("all");
  const [stats, setStats] = useState({
    urgent_pending_requests: 0,
    total_requests: 0,
    pending_requests: 0,
    approved_requests: 0,
    rejected_requests: 0,
    completed_requests: 0,
  });
  const [currentCompanyName, setCurrentCompanyName] = useState("우리회사 A");

  // ✅ 더미 데이터 로드 함수
  const loadData = () => {
    console.log("데이터 새로고침 실행");
    // 실제 API 호출 대신 임시값만 갱신
    setStats({
      urgent_pending_requests: 1,
      total_requests: 5,
      pending_requests: 2,
      approved_requests: 1,
      rejected_requests: 1,
      completed_requests: 1,
    });
  };

  useEffect(() => {
    loadData();
  }, []);

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
              데이터 공유 요청을 검토하고 승인/거부를 결정할 수 있습니다.
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
              새로고침
            </Button>
          </div>
        </div>

        {/* 이하 전체 코드 (탭, 카드, 요청 리스트 등) 연결 */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="all">전체</TabsTrigger>
            <TabsTrigger value="pending">대기</TabsTrigger>
            <TabsTrigger value="approved">승인</TabsTrigger>
            <TabsTrigger value="rejected">거부</TabsTrigger>
            <TabsTrigger value="completed">완료</TabsTrigger>
          </TabsList>
          <TabsContent value="all">
            <Card>
              <CardContent className="p-6">
                <p className="text-gray-700">전체 요청 목록</p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default DataSharingPage;
