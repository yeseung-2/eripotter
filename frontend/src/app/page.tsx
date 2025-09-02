'use client';

import { useRouter } from 'next/navigation';
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import Image from 'next/image';

// === ADD: API base util ===
const BASE = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "";
const join = (p: string) => (BASE ? `${BASE}${p}` : p);
// ==========================

export default function LoginPage() {
  const router = useRouter();

  const handleGoogleLogin = () => {
    // Google OAuth 로그인 엔드포인트로 리다이렉트
    window.location.href = join("/api/auth/google/login");  // URL 패턴 수정
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Side - Background Image and Branding */}
      <div className="hidden lg:flex lg:w-2/3 relative bg-gradient-to-br from-blue-100/30 to-cyan-300/40">
        {/* Background Image */}
        <div className="absolute inset-0">
          <Image
            src="/background.jpg"
            alt="Background"
            fill
            className="object-cover opacity-30"
            priority
          />
        </div>
        
        {/* Overlay with branding content */}
        <div className="relative z-10 flex flex-col justify-between h-full p-12 text-white">
          {/* Center section with main message */}
          <div className="flex-1 flex flex-col justify-center">
            <h1 className="text-5xl font-bold mb-6 leading-tight">
              공급망 관리를 위한<br />
              <span className="bg-gradient-to-r from-white to-cyan-200 bg-clip-text text-transparent">
                첫걸음
              </span>
            </h1>
            <p className="text-xl text-cyan-100 mb-8">
              ESG Realationship Interaction
            </p>
            <div className="w-16 h-1 bg-cyan-300 mb-8"></div>
            <p className="text-lg text-cyan-100">
              Global Supply Chain Leader<br />
              ERI와 함께합니다.
            </p>
          </div>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="w-full lg:w-1/3 flex items-center justify-center p-8 bg-white">
        <div className="w-full max-w-sm">
          {/* Large Logo */}
          <div className="flex justify-center mb-8">
            <div className="w-24 h-24 relative">
              <Image
                src="/logo.png"
                alt="ERI Logo"
                fill
                className="object-contain"
              />
            </div>
          </div>

          {/* Mobile logo (visible only on mobile) */}
          <div className="lg:hidden flex items-center justify-center mb-8">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 relative">
                <Image
                  src="/logo.png"
                  alt="ERI Logo"
                  fill
                  className="object-contain"
                />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">ERI</h2>
                <p className="text-sm text-gray-600">Environmental Risk Intelligence</p>
              </div>
            </div>
          </div>

          {/* Login Form */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              로그인
            </h1>
            <p className="text-gray-600">
              계정에 로그인하여 서비스를 이용하세요
            </p>
          </div>

          {/* Google Login Button */}
          <Button
            onClick={handleGoogleLogin}
            className="w-full py-4 mb-6 bg-white hover:bg-gray-50 text-gray-800 border border-gray-300 rounded-xl flex items-center justify-center space-x-3 text-base font-medium shadow-sm"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path
                className="text-[#4285F4]"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                className="text-[#34A853]"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                className="text-[#FBBC05]"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                className="text-[#EA4335]"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            <span>Google 계정으로 로그인</span>
          </Button>

          {/* Terms and Privacy */}
          <div className="text-center text-sm text-gray-600">
            로그인 시{" "}
            <a href="/terms" className="text-blue-600 hover:underline">
              이용약관
            </a>
            과{" "}
            <a href="/privacy" className="text-blue-600 hover:underline">
              개인정보처리방침
            </a>
            에 동의하게 됩니다.
          </div>

          {/* Support Links */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <div className="space-y-3">
              <h3 className="text-sm font-medium text-gray-900 mb-3">지원센터</h3>
              <div className="space-y-2">
                <a href="/support" className="block text-sm text-gray-600 hover:text-blue-600">
                  • 1:1 문의
                </a>
                <a href="/help" className="block text-sm text-gray-600 hover:text-blue-600">
                  • 도움말
                </a>
                <a href="/contact" className="block text-sm text-gray-600 hover:text-blue-600">
                  • 담당자 연락처
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}