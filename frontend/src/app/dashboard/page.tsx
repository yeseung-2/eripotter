'use client'

import React, { useState, useEffect } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { AlertTriangle } from "lucide-react";

// --- Color System ------------------------------------------------------------
const STATUS = {
  EXCELLENT: {
    text: "우수",
    color: "text-green-600",
    shadow: "shadow-[0_4px_12px_rgba(34,197,94,0.35)]",
    chip: "bg-green-50 text-green-600",
  },
  FAIR: {
    text: "양호",
    color: "text-yellow-600",
    shadow: "shadow-[0_4px_12px_rgba(234,179,8,0.35)]",
    chip: "bg-yellow-50 text-yellow-600",
  },
  RISK: {
    text: "위험",
    color: "text-red-600",
    shadow: "shadow-[0_4px_12px_rgba(239,68,68,0.35)]",
    chip: "bg-red-50 text-red-600",
  },
};

// Calm navy/blue foundation
const THEME = {
  pageBg: "bg-slate-50",
  cardBg: "bg-white",
  navyCard: "bg-slate-900",
  navyPanel: "bg-slate-800",
  border: "border-slate-200",
  navyBorder: "border-slate-700",
  textStrong: "text-slate-900",
  text: "text-slate-700",
  textMuted: "text-slate-500",
  navyText: "text-slate-100",
  navyMuted: "text-slate-400",
  blueA: "#93c5fd",
  blueB: "#60a5fa",
  blueC: "#3b82f6",
};

// --- Types -----------------------------------------------------------------
type ScorePoint = { month: string; E: number; S: number; G: number };

type TimelineItem = {
  id: number;
  company: string;
  status: string;
  score: number | null;
  time: string;
};

type CompanyRow = {
  id: number;
  name: string;
  progress: number;
  status: string;
  lastUpdate: string;
  score: number | null;
};

// --- Helpers -----------------------------------------------------------------
function getStatusInfo(score: number) {
  if (score >= 80) return STATUS.EXCELLENT;
  if (score >= 60) return STATUS.FAIR;
  return STATUS.RISK;
}

// Mock data (replace with real API data)
const defaultScores = {
  environmental: { score: 82 },
  social: { score: 67 },
  governance: { score: 54 },
};

const defaultScoreSeries: ScorePoint[] = [
  { month: "3월", E: 74, S: 58, G: 45 },
  { month: "4월", E: 76, S: 60, G: 48 },
  { month: "5월", E: 79, S: 61, G: 50 },
  { month: "6월", E: 80, S: 63, G: 52 },
  { month: "7월", E: 81, S: 65, G: 53 },
  { month: "8월", E: 82, S: 67, G: 54 },
];

const defaultRecent: TimelineItem[] = [
  { id: 1, company: "에코머티리얼즈", status: "완료", score: 84, time: "8월 21일 14:20" },
  { id: 2, company: "블루팩토리", status: "진행중", score: null, time: "8월 20일 09:15" },
  { id: 3, company: "그린솔루션", status: "완료", score: 76, time: "8월 18일 17:40" },
];

const defaultCompanies: CompanyRow[] = [
  { id: 1, name: "에코머티리얼즈", progress: 100, status: "완료", lastUpdate: "8월 21일", score: 84 },
  { id: 2, name: "블루팩토리", progress: 62, status: "진행중", lastUpdate: "8월 20일", score: null },
  { id: 3, name: "씨엔에너지", progress: 100, status: "완료", lastUpdate: "8월 19일", score: 73 },
  { id: 4, name: "네이비텍", progress: 28, status: "진행중", lastUpdate: "8월 18일", score: null },
];

// --- Components --------------------------------------------------------------
function StatCard({ title, score }: { title: string; score: number }) {
  const s = getStatusInfo(score);
  return (
    <div className="flex flex-col items-center text-center">
      <div className={`w-40 h-40 rounded-full border border-gray-300/50 flex items-center justify-center flex-col bg-white ${s.shadow} transition-shadow duration-300`}>
        <div className={`text-lg font-medium ${s.color}`}>{s.text}</div>
        <div className="text-5xl font-bold text-gray-900 mt-2">{score}</div>
      </div>
      <div className="text-base text-gray-600 mt-4">{title}</div>
    </div>
  );
}

function TrendChart({ data }: { data: ScorePoint[] }) {
  const minY = 0;
  const maxY = 100;
  return (
    <div className="bg-white rounded-xl shadow-sm">
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold text-gray-800">ESG 점수 변화 추이</h3>
          <div className="flex items-center gap-3 text-sm text-gray-600">
            <span className="inline-flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-blue-500" />
              환경(E)
            </span>
            <span className="inline-flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-blue-400" />
              사회(S)
            </span>
            <span className="inline-flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-blue-300" />
              지배구조(G)
            </span>
          </div>
        </div>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid stroke="#f1f5f9" vertical={false} />
              <XAxis dataKey="month" tick={{ fill: "#64748b", fontSize: 12 }} axisLine={{ stroke: "#e2e8f0" }} tickLine={false} />
              <YAxis domain={[minY, maxY]} tick={{ fill: "#64748b", fontSize: 12 }} axisLine={{ stroke: "#e2e8f0" }} tickLine={false} />
              <Tooltip contentStyle={{ borderRadius: 8, borderColor: "#e2e8f0" }} />
              <Line type="monotone" dataKey="E" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4, fill: "#3b82f6" }} activeDot={{ r: 6 }} strokeOpacity={0.6} />
              <Line type="monotone" dataKey="S" stroke="#60a5fa" strokeWidth={2} dot={{ r: 4, fill: "#60a5fa" }} activeDot={{ r: 6 }} strokeOpacity={0.6} />
              <Line type="monotone" dataKey="G" stroke="#93c5fd" strokeWidth={2} dot={{ r: 4, fill: "#93c5fd" }} activeDot={{ r: 6 }} strokeOpacity={0.6} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

function Timeline({ items }: { items: TimelineItem[] }) {
  return (
    <div className={`rounded-2xl border ${THEME.border} ${THEME.cardBg} p-6 shadow-sm`}>
      <h3 className="text-lg font-semibold text-slate-900 mb-4">최근 활동</h3>
      <ol className="relative border-s border-slate-200">
        {items.map((a) => (
          <li key={a.id} className="ms-6 py-4">
            <span
              className={`absolute -start-2.5 mt-1 flex h-5 w-5 items-center justify-center rounded-full ring-4 ring-white ${
                a.status === "완료" ? "bg-blue-500" : "bg-blue-300"
              }`}
            >
              <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
              </svg>
            </span>
            <div className="flex items-center justify-between">
              <div className="text-sm">
                <span className="font-semibold text-slate-900">{a.company}</span>
                <span
                  className={`ml-2 px-2 py-0.5 rounded-full text-xs font-semibold ${
                    a.status === "완료" ? STATUS.EXCELLENT.chip : STATUS.FAIR.chip
                  }`}
                >
                  {a.status}
                </span>
                {a.score !== null && <span className="ml-2 text-slate-600">점수: {a.score}점</span>}
              </div>
              <time className="text-sm text-slate-500">{a.time}</time>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}

function CompanyTable({ rows }: { rows: CompanyRow[] }) {
  return (
    <div className={`rounded-2xl border ${THEME.border} ${THEME.cardBg} shadow-sm overflow-hidden`}>
      <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-900">협력사 자가진단 현황</h3>
        <div className="text-xs text-slate-500">완료≥80: 우수(초록) · ≥60: 양호(노랑) · 그 외: 위험(빨강)</div>
      </div>
      <div className="overflow-auto">
        <table className="min-w-full">
          <thead className="bg-slate-50 text-slate-600 text-xs">
            <tr>
              <th className="px-6 py-3 text-left font-medium">기업명</th>
              <th className="px-6 py-3 text-left font-medium">진행률</th>
              <th className="px-6 py-3 text-left font-medium">상태</th>
              <th className="px-6 py-3 text-left font-medium">최근 업데이트</th>
              <th className="px-6 py-3 text-left font-medium">점수</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 text-sm">
            {rows.map((company) => {
              const statusInfo =
                company.status === "완료" && company.score != null ? getStatusInfo(company.score) : null;
              return (
                <tr key={company.id} className="hover:bg-slate-50/70">
                  <td className="px-6 py-3 font-medium text-slate-900">{company.name}</td>
                  <td className="px-6 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-full bg-slate-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            company.status === "완료" ? "bg-blue-600" : "bg-blue-400"
                          }`}
                          style={{ width: `${company.progress}%` }}
                        />
                      </div>
                      <span className="tabular-nums text-slate-600">{company.progress}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-3">
                    <span
                      className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        company.status === "완료" ? STATUS.EXCELLENT.chip : STATUS.FAIR.chip
                      }`}
                    >
                      {company.status}
                    </span>
                  </td>
                  <td className="px-6 py-3 text-slate-600">{company.lastUpdate}</td>
                  <td className="px-6 py-3 font-medium text-slate-900">
                    {company.status === "완료" && company.score != null ? (
                      <span className="inline-flex items-center gap-2">
                        <span className="tabular-nums">{company.score}점</span>
                        <span className="inline-block h-2 w-2 rounded-full" style={{ background: statusInfo?.color }} />
                      </span>
                    ) : (
                      <span className="text-slate-400">-</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// --- Page --------------------------------------------------------------------
export default function SupplyChainDashboardPage() {
  const [activeTab, setActiveTab] = useState("overview");
  const [mounted, setMounted] = useState(false);
  const router = useRouter();

  useEffect(() => setMounted(true), []);

  const handleNavigation = (path: string) => {
    if (mounted) router.push(path);
  };

  // Replace with props / fetched data
  const esgScores = defaultScores;
  const scoreSeries = defaultScoreSeries;
  const recentAssessments = defaultRecent;
  const companyAssessments = defaultCompanies;

  return (
    <div className={`min-h-screen ${THEME.pageBg}`}>
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center -ml-15">
              <Image src="/logo.png" alt="ERI Logo" width={140} height={140} />
            </div>
            <div className="flex items-center space-x-4">
              {/* ESG 데이터 업로드 버튼 */}
              <button
                onClick={() => handleNavigation("/data-upload")}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2"
              >
                <span>📊</span>
                <span>ESG 데이터 업로드</span>
              </button>

              {/* 알림 */}
              <div className="relative">
                <button className="p-2 text-gray-400 hover:text-gray-500 transition-colors">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                    />
                  </svg>
                  <span className="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-400 ring-2 ring-white"></span>
                </button>
              </div>

              {/* 챗봇 */}
              <button
                onClick={() => handleNavigation("/chat")}
                className="p-2 text-gray-400 hover:text-gray-500 transition-colors relative"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                  />
                </svg>
                <span className="absolute -top-1 -right-1 block h-4 w-4 rounded-full bg-blue-500 text-white text-xs flex items-center justify-center">AI</span>
              </button>

              {/* 프로필 */}
              <div className="flex items-center space-x-3">
                <div className="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center">
                  <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <span className="text-sm font-medium text-gray-700">관리자</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {[
              { id: "overview", name: "전체 현황" },
              { id: "industry", name: "산업별 현황" },
              { id: "company", name: "협력사별 현황" },
              { id: "reports", name: "리포트" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? "border-blue-600 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                {tab.name}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {activeTab === "overview" && (
          <div className="space-y-6">
            {/* ESG Score Summary */}
            <div className="bg-white rounded-xl shadow-sm mb-10">
              <h3 className="text-2xl font-bold text-gray-800 mb-12 p-8 pb-0 text-center">공급망실사 자가진단 현황</h3>
              <div className="flex flex-wrap justify-center gap-32 px-8">
                <StatCard title="환경(E)" score={esgScores.environmental.score} />
                <StatCard title="사회(S)" score={esgScores.social.score} />
                <StatCard title="지배구조(G)" score={esgScores.governance.score} />
              </div>
              <div className="flex justify-between items-center p-8 pt-12">
                <button
                  onClick={() => handleNavigation("/assessment")}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 font-medium"
                >
                  <span>📋</span>
                  <span>자가진단 실시하기</span>
                </button>
                <p className="text-sm text-gray-500">자가진단 실시일: 2024.02.15</p>
              </div>
            </div>
            <hr className="border-t border-gray-200 mb-6" />

            {/* Chart + Timeline */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <TrendChart data={scoreSeries} />
              <Timeline items={recentAssessments} />
            </div>

            {/* Table */}
            <CompanyTable rows={companyAssessments} />

            {/* Risk banner */}
            <div className="rounded-2xl border border-slate-200 bg-white p-5 flex items-start gap-3">
              <div className="mt-0.5">
                <AlertTriangle className="w-5 h-5 text-red-500" />
              </div>
              <div>
                <div className="font-semibold text-slate-900">주의가 필요한 항목</div>
                <div className="text-sm text-slate-600 mt-1">
                  60점 미만 항목은 개선 계획을 요청하거나 현장 실사를 권고하세요. 리포트 탭에서 자동 생성된 권고안을 확인할 수 있습니다.
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === "industry" && (
          <div className={`rounded-2xl border ${THEME.border} ${THEME.cardBg} p-6 shadow-sm`}>
            <h2 className="text-xl font-semibold text-slate-900 mb-2">산업별 현황</h2>
            <p className="text-slate-600">업종별(배터리 소재, 전기전자, 금속가공 등) 자가진단 점수 분포와 리스크 집중도를 제공할 예정입니다.</p>
          </div>
        )}

        {activeTab === "company" && (
          <div className={`rounded-2xl border ${THEME.border} ${THEME.cardBg} p-6 shadow-sm`}>
            <h2 className="text-xl font-semibold text-slate-900 mb-2">협력사별 현황</h2>
            <p className="text-slate-600">협력사 상세 페이지(자가진단 결과, 제출 증빙, 개선 과제, 실사 체크리스트)가 여기에 연결됩니다.</p>
          </div>
        )}

        {activeTab === "reports" && (
          <div className={`rounded-2xl border ${THEME.border} ${THEME.cardBg} p-6 shadow-sm`}>
            <h2 className="text-xl font-semibold text-slate-900 mb-2">리포트</h2>
            <p className="text-slate-600">점수 추세, 산업 벤치마크, 개선 권고안(양호/위험/우수별) PDF 내보내기 기능이 제공됩니다.</p>
          </div>
        )}
      </main>
    </div>
  );
}
