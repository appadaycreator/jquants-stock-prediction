/** @type {import('next').NextConfig} */
const repo = 'jquants-stock-prediction';
const isProd = process.env.NODE_ENV === 'production';

const nextConfig = {
  output: 'export',
  basePath: isProd ? `/${repo}` : '',
  assetPrefix: isProd ? `https://appadaycreator.github.io/${repo}/` : '',
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
};

module.exports = nextConfig;