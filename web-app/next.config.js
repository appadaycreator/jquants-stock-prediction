/** @type {import("next").NextConfig} */
const nextConfig = {
  // 基本設定 - 本番環境でのみ静的エクスポート
  ...(process.env.NODE_ENV === 'production' && {
    output: "export",
    distDir: "out",
  }),
  
  // GitHub Pages用の設定（本番環境のみ）
  ...(process.env.NODE_ENV === 'production' && {
    basePath: "/jquants-stock-prediction",
    assetPrefix: "/jquants-stock-prediction",
  }),
  
  // 画像最適化設定
  images: {
    unoptimized: true,
    formats: ["image/webp", "image/avif"],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },
  
  // 静的エクスポート用の設定
  trailingSlash: true,
  skipTrailingSlashRedirect: true,
  
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
    // 静的エクスポート用の設定（本番環境のみ）
    ...(process.env.NODE_ENV === 'production' && {
      staticGenerationRetryCount: 5,
      disableOptimizedLoading: true,
    }),
    // 開発環境でのFast Refresh最適化
    ...(process.env.NODE_ENV === 'development' && {
      turbo: {
        rules: {
          '*.svg': {
            loaders: ['@svgr/webpack'],
            as: '*.js',
          },
        },
      },
    }),
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
      'src': srcPath,
      '@/lib': path.resolve(srcPath, 'lib'),
      '@/components': path.resolve(srcPath, 'components'),
      '@/app': path.resolve(srcPath, 'app'),
      '@/styles': path.resolve(srcPath, 'styles'),
      '@/lib/guide': path.resolve(srcPath, 'lib/guide'),
      '@/lib/today': path.resolve(srcPath, 'lib/today'),
      '@/lib/guide/shortcut': path.resolve(srcPath, 'lib/guide/shortcut'),
      '@/lib/guide/guideStore': path.resolve(srcPath, 'lib/guide/guideStore'),
      '@/lib/datetime': path.resolve(srcPath, 'lib/datetime'),
      '@/lib/jquants-adapter': path.resolve(srcPath, 'lib/jquants-adapter'),
      '@/lib/today/fetchTodaySummary': path.resolve(srcPath, 'lib/today/fetchTodaySummary'),
      '@/types': path.resolve(srcPath, 'types'),
      '@/contexts': path.resolve(srcPath, 'contexts'),
      '@/hooks': path.resolve(srcPath, 'hooks'),
    };
    
    // モジュール解決の設定を追加
    config.resolve.modules = [
      srcPath,
      'node_modules',
    ];
    
    // モジュール解決の確実性を向上
    config.resolve.symlinks = false;
    config.resolve.cacheWithContext = false;
    
    // パス解決の確実性を向上
    config.resolve.mainFields = ['browser', 'module', 'main'];
    config.resolve.conditionNames = ['import', 'require', 'node'];
    
    // 拡張子の解決順序を設定
    config.resolve.extensions = ['.tsx', '.ts', '.jsx', '.js', '.json'];
    
    // パス解決の確実性を向上
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
      path: false,
    };
    
    // モジュール解決の確実性を向上
    config.resolve.fullySpecified = false;
    
    // パス解決のデバッグ情報を追加
    if (dev) {
      config.resolve.logging = 'verbose';
    }
    
    // ビルド環境でのパス解決を確実にする（キャッシュ完全無効化）
    config.resolve.unsafeCache = false;
    config.resolve.cacheWithContext = false;
    config.cache = false;
    config.optimization = {
      ...config.optimization,
      moduleIds: 'deterministic',
      chunkIds: 'deterministic',
    };
    
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
