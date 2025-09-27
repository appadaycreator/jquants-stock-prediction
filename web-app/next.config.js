/** @type {import('next').NextConfig} */
const nextConfig = {
  // 基本設定
  output: process.env.NODE_ENV === 'production' ? 'export' : undefined,
  distDir: 'dist',
  
  // 画像最適化設定
  images: {
    unoptimized: process.env.NODE_ENV === 'production',
    formats: ['image/webp', 'image/avif'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384]
  },
  
  // GitHub Pages用の設定
  ...(process.env.NODE_ENV === 'production' && {
    assetPrefix: '/jquants-stock-prediction',
    basePath: '/jquants-stock-prediction',
    generateBuildId: async () => 'build',
    // RSCエラーを解決するための設定
    outputFileTracing: true,
    // 静的エクスポート用の設定
    trailingSlash: true,
    skipTrailingSlashRedirect: true
  }),
  
  // パフォーマンス最適化
  compress: true,
  poweredByHeader: false,
  
  // 実験的機能の設定
  experimental: {
    optimizePackageImports: ['lucide-react', 'recharts'],
    // RSC payloadエラーを解決するための設定
    serverComponentsExternalPackages: [],
    // GitHub PagesでのRSC動作を改善
    staticGenerationRetryCount: 3,
    // RSCエラーを解決するための設定
    serverActions: {
      allowedOrigins: ['appadaycreator.github.io']
    }
  },
  
  // サーバー外部パッケージの設定（experimentalから移動）
  serverExternalPackages: [],
  
  // Webpack設定の最適化
  webpack: (config, { dev, isServer }) => {
    // バンドルサイズの最適化
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
          },
          common: {
            name: 'common',
            minChunks: 2,
            chunks: 'all',
            enforce: true
          }
        }
      }
    }
    
    return config
  },
  
  // ヘッダー設定（output: exportでは使用不可）
  // async headers() {
  //   return [
  //     {
  //       source: '/(.*)',
  //       headers: [
  //         {
  //           key: 'X-Content-Type-Options',
  //           value: 'nosniff'
  //         },
  //         {
  //           key: 'X-Frame-Options',
  //           value: 'DENY'
  //         },
  //         {
  //           key: 'X-XSS-Protection',
  //           value: '1; mode=block'
  //         }
  //       ]
  //     }
  //   ]
  // }
}

module.exports = nextConfig
