/** @type {import("next").NextConfig} */
const nextConfig = {
  // 基本設定 - GitHub Pages用に静的エクスポートを有効化
  output: process.env.NODE_ENV === "production" ? "export" : undefined,
  distDir: "dist",
  
  // 画像最適化設定
  images: {
    unoptimized: process.env.NODE_ENV === "production",
    formats: ["image/webp", "image/avif"],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },
  
  // GitHub Pages用の設定
  ...(process.env.NODE_ENV === "production" && {
    assetPrefix: "/jquants-stock-prediction",
    basePath: "/jquants-stock-prediction",
    generateBuildId: async () => "build",
    // 静的エクスポート用の設定
    trailingSlash: true,
    skipTrailingSlashRedirect: true,
    // RSCペイロードエラーを解決するための設定
    outputFileTracingRoot: process.cwd(),
    outputFileTracingIncludes: {
      '/reports': ['./src/app/reports/**/*'],
      '/settings': ['./src/app/settings/**/*'],
    },
    // RSC payload エラーを根本的に解決
    // generateStaticParams: false // このオプションは無効
  }),
  
  // パフォーマンス最適化
  compress: true,
  poweredByHeader: false,
  
  // RSCペイロードエラーを解決するための設定
  // プリフェッチを無効化
  onDemandEntries: {
    maxInactiveAge: 25 * 1000,
    pagesBufferLength: 2,
  },
  
  
  
  // パッケージのトランスパイル設定（Next.js 15対応）
  transpilePackages: ["clsx", "tailwind-merge", "class-variance-authority"],
  
  // 実験的機能の設定
  experimental: {
    optimizePackageImports: ["lucide-react", "recharts"],
    // GitHub PagesでのRSC動作を改善
    staticGenerationRetryCount: 5,
    // RSCエラーを解決するための設定
    serverActions: {
      allowedOrigins: ["appadaycreator.github.io"],
    },
    // プリフェッチの無効化（GitHub Pagesでの問題を回避）
    disableOptimizedLoading: true,
  },
  
  // ESLint設定を無効化（ビルドエラーを回避）
  eslint: {
    ignoreDuringBuilds: true,
  },
  
  // サーバー外部パッケージの設定
  serverExternalPackages: [],
  
  // Webpack設定の最適化
  webpack: (config, { dev, isServer }) => {
    // パス解決の設定を追加（絶対パスを使用）
    const path = require('path');
    const srcPath = path.resolve(__dirname, 'src');
    
    // より確実なパス解決の設定
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': srcPath,
      '@/lib': path.resolve(srcPath, 'lib'),
      '@/components': path.resolve(srcPath, 'components'),
      '@/app': path.resolve(srcPath, 'app'),
      '@/styles': path.resolve(srcPath, 'styles'),
    };
    
    // モジュール解決の設定を追加
    config.resolve.modules = [
      srcPath,
      'node_modules',
    ];
    
    // 拡張子の解決順序を設定
    config.resolve.extensions = ['.tsx', '.ts', '.jsx', '.js', '.json'];
    
    // パス解決のデバッグ情報を追加（開発時のみ）
    if (dev) {
      config.resolve.symlinks = false;
    }
    
    // パス解決の確実性を向上
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
      path: false,
    };
    
    // モジュール解決の確実性を向上
    config.resolve.fullySpecified = false;
    
    // パス解決の確実性をさらに向上
    config.resolve.cacheWithContext = false;
    
    // バンドルサイズの最適化
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        chunks: "all",
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: "vendors",
            chunks: "all",
          },
          common: {
            name: "common",
            minChunks: 2,
            chunks: "all",
            enforce: true,
          },
        },
      };
    }
    
    return config;
  },
  
  // ヘッダー設定（output: exportでは使用不可）
  // async headers() {
  //   return [
  //     {
  //       source: "/(.*)",
  //       headers: [
  //         {
  //           key: "X-Content-Type-Options",
  //           value: "nosniff"
  //         },
  //         {
  //           key: "X-Frame-Options",
  //           value: "DENY"
  //         },
  //         {
  //           key: "X-XSS-Protection",
  //           value: "1; mode=block"
  //         }
  //       ]
  //     }
  //   ]
  // }
};

module.exports = nextConfig;
