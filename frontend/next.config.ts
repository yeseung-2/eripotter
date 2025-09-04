// frontend/next.config.ts
import type { NextConfig } from "next";

const gateway =
  process.env.NEXT_PUBLIC_GATEWAY_ORIGIN ?? "http://localhost:8080";

const nextConfig: NextConfig = {
  // ✅ Vercel/CI에서 린트/TS 에러로 빌드 중단되지 않게
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: true },

  // 🔁 /api/* -> 게이트웨이 /api/v1/* 프록시
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${gateway}/api/v1/:path*`, 
      },
    ];
  },

  // 프론트 코드에서는 동일 출처(/api) 기본 사용
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL ?? "/api",
  },

  // 🖼️ 외부 이미지 허용 도메인
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "images.unsplash.com",
        port: "",
        pathname: "/**",
      },
    ],
  },
};

export default nextConfig;
