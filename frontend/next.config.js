/** @type {import('next').NextConfig} */
const isDev = process.env.NODE_ENV !== 'production'

// next-pwa (개발 모드 비활성화)
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: isDev,
})

// 게이트웨이 (없으면 Railway 게이트웨이로 프록시)
const raw = process.env.NEXT_PUBLIC_API_URL || 'https://gateway-production-5d19.up.railway.app';
const gateway = raw.replace(/\/+$/, ''); // 끝 슬래시 제거

const nextConfig = {
  // 빌드 막힘 방지
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: true },

  // 외부 이미지 허용
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'images.unsplash.com', pathname: '/**' },
    ],
  },

  // 파일시스템 모듈 이슈 회피
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...(config.resolve.fallback || {}),
        fs: false,
        path: false,
      }
    }
    return config
  },

  // 💡 게이트웨이에 있는 그대로의 경로로 프록시 (v1 없음)
  async rewrites() {
    return [
      // 우선순위가 필요한 서비스는 명시적으로
      { source: '/api/normal/:path*',     destination: `${gateway}/api/normal/:path*` },
      { source: '/api/report/:path*',     destination: `${gateway}/api/report/:path*` },
      { source: '/api/account/:path*',    destination: `${gateway}/api/account/:path*` },
      { source: '/api/assessment/:path*', destination: `${gateway}/api/assessment/:path*` },
      { source: '/api/chatbot/:path*',    destination: `${gateway}/api/chatbot/:path*` },
      { source: '/sharing/:path*',        destination: `${gateway}/sharing/:path*` }, // 비-API 경로

      // 최종 폴백: /api/* -> 게이트웨이 /api/* (v1 제거)
      { source: '/api/:path*',            destination: `${gateway}/api/:path*` },
    ]
  },

  // 프론트 기본 API 엔드포인트
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || '/api',
  },
}

module.exports = withPWA(nextConfig)
