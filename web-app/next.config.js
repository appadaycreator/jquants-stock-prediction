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
    },
    // GitHub Pagesでの配信最適化
    compress: false,
    poweredByHeader: false,
    // RSCファイルの配信設定
    experimental: {
      optimizePackageImports: ['lucide-react'],
      // RSCファイルの配信を無効化（GitHub Pagesで問題を回避）
      serverComponentsExternalPackages: []
    },
    // GitHub Pages用の追加設定
    trailingSlash: true
  }),
  // 開発環境での設定
  experimental: {
    optimizePackageImports: ['lucide-react']
  }
}

module.exports = nextConfig
