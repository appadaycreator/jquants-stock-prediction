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
  // 静的エクスポート時の設定
  distDir: isProd ? 'docs' : '.next',
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
      {
        source: '/favicon.ico',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },
  // APIルートの設定（静的エクスポート時は無効）
  async rewrites() {
    if (isProd) {
      return [];
    }
    return [
      {
        source: '/api/:path*',
        destination: '/api/:path*',
      },
    ];
  },
};

module.exports = nextConfig;