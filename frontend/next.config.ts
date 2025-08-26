/** @type {import('next').NextConfig} */
const nextConfig = {
  // 빌드 시 오류 무시 (Vercel 배포용)
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },

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

  // 🖼️ 외부 이미지 도메인 허용
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'images.unsplash.com',
        port: '',
        pathname: '/**',
      },
    ],
  },
};

module.exports = nextConfig;
