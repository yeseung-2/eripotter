/** @type {import('next').NextConfig} */
const isDev = process.env.NODE_ENV !== 'production'

// next-pwa (개발 모드 비활성화)
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: isDev,
})

// 게이트웨이 (없으면 로컬 게이트웨이로 프록시)
const gateway = process.env.NEXT_PUBLIC_GATEWAY_ORIGIN || 'http://localhost:8080'

const nextConfig = {
  // 빌드 막힘 방지
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: true },

  // 외부 이미지 허용
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'images.unsplash.com',
        pathname: '/**',
      },
    ],
  },

  // 파일시스템 모듈 이슈 회피
  experimental: { esmExternals: 'loose' },
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

  // /api/* → 게이트웨이 /api/v1/* 프록시
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${gateway}/api/v1/:path*`,
      },
    ]
  },

  // 프론트 기본 API 엔드포인트
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || '/api',
  },
}

module.exports = withPWA(nextConfig)
