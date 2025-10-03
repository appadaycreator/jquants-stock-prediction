/** @type {import('next').NextConfig} */
const nextConfig = {
  // 開発環境では静的エクスポートを無効化
  ...(process.env.NODE_ENV === "production" && { output: "export" }),
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  assetPrefix: process.env.NODE_ENV === "production" ? "/jquants-stock-prediction" : "",
  basePath: process.env.NODE_ENV === "production" ? "/jquants-stock-prediction" : "",
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
};

module.exports = nextConfig;