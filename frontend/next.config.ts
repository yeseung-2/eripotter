/** @type {import('next').NextConfig} */
const nextConfig = {
  // 🔁 /api/* -> Gateway /api/v1/* 로 프록시
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8080/api/v1/:path*',
      },
    ];
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