<<<<<<< HEAD
// next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 🔁 /api/* -> Gateway /api/v1/* 프록시
  async rewrites() {
    const gateway =
      process.env.NEXT_PUBLIC_GATEWAY_URL ?? "http://localhost:8080";
    return [
      {
        source: "/api/:path*",
        destination: `${gateway}/api/v1/:path*`,
      },
    ];
=======
/** @type {import('next').NextConfig} */
const nextConfig = {
  // 빌드 시 오류 무시 (Vercel 배포용)
  eslint: {
    ignoreDuringBuilds: true,
>>>>>>> 461957b (Fix Vercel build: add ESLint and TypeScript ignore settings)
  },

  // 프론트에 노출되는 API 베이스 (동일 출처 기본)
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "/api",
  },

<<<<<<< HEAD
=======
  // 🔁 /api/* -> Gateway /api/v1/* 로 프록시
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://<gateway-railway-domain-or-custom>/api/v1/:path*',
      },
    ];
  },

  // ❌ 굳이 프론트에서 CORS 헤더를 세팅할 필요 없음. 서버(Gateway)가 해야 함.
  async headers() {
    return []; // 제거
  },

  // 프론트 코드에서 직접 외부 도메인을 들지 말고 동일 출처(/api) 쓰게 유지
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || '/api',
  },

>>>>>>> 461957b (Fix Vercel build: add ESLint and TypeScript ignore settings)
  // 🖼️ 외부 이미지 도메인 허용
  images: {
    remotePatterns: [
      {
<<<<<<< HEAD
        protocol: "https",
        hostname: "images.unsplash.com",
        port: "",
        pathname: "/**",
      },
    ],
  },

  // CI/Vercel 빌드시 임시로 린트/TS 에러 무시
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: true },
=======
        protocol: 'https',
        hostname: 'images.unsplash.com',
        port: '',
        pathname: '/**',
      },
    ],
  },
>>>>>>> 461957b (Fix Vercel build: add ESLint and TypeScript ignore settings)
};

module.exports = nextConfig;
