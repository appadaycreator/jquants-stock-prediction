/** @type {import('next').NextConfig} */
const nextConfig = {
  // 開発環境では通常のNext.js設定を使用
  ...(process.env.NODE_ENV === 'production' && {
    output: 'export',
    trailingSlash: true,
    skipTrailingSlashRedirect: true,
    distDir: 'dist',
    images: {
      unoptimized: true
    },
    // GitHub Pages用の設定（相対パス使用）
    assetPrefix: '.',
    basePath: '',
    // 静的エクスポート用の設定
    generateBuildId: async () => {
      return 'build'
    }
  }),
  // faviconとNext.js内部ファイルの相対パス化
  experimental: {
    optimizePackageImports: ['lucide-react']
  }
}

module.exports = nextConfig
