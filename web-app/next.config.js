/** @type {import('next').NextConfig} */
const repo = 'jquants-stock-prediction';
const isProd = process.env.NODE_ENV === 'production';

const nextConfig = {
  // 開発環境ではAPIルートを有効にする
  output: isProd ? 'export' : undefined,
  basePath: isProd ? `/${repo}` : '',
  assetPrefix: isProd ? `/${repo}/` : '',
  images: { 
    unoptimized: true 
  },
  trailingSlash: true,
  experimental: { 
    instrumentationHook: false 
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  // 静的アセットのパス設定
  async headers() {
    return [
      {
        source: '/_next/static/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },
  // APIルートの設定
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: '/api/:path*',
      },
    ];
  },
};

module.exports = nextConfig;