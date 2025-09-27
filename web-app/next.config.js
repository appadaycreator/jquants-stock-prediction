/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  skipTrailingSlashRedirect: true,
  distDir: 'dist',
  images: {
    unoptimized: true
  },
  // GitHub Pages用の設定（相対パス使用）
  assetPrefix: process.env.NODE_ENV === 'production' ? '.' : '',
  basePath: '',
  // faviconとNext.js内部ファイルの相対パス化
  experimental: {
    optimizePackageImports: ['lucide-react']
  },
  // 静的エクスポート用の設定
  generateBuildId: async () => {
    return 'build'
  }
}

module.exports = nextConfig
