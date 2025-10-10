/** @type {import('next').NextConfig} */
const repo = "jquants-stock-prediction";
const isProd = process.env.NODE_ENV === "production";
const isGitHubPages = process.env.GITHUB_ACTIONS === "true";

const nextConfig = {
  // 開発環境ではAPIルートを有効にする
  output: isProd ? "export" : undefined,
  // GitHub Pages用の設定
  basePath: isGitHubPages ? `/${repo}` : "",
  assetPrefix: isGitHubPages ? `/${repo}/` : "",
  // クライアント側で basePath を解決するために公開環境変数を注入
  env: {
    NEXT_PUBLIC_BASE_PATH: isGitHubPages ? `/${repo}` : "",
  },
  images: { 
    unoptimized: true, 
  },
  trailingSlash: true,
  experimental: { 
    instrumentationHook: false,
    // Next.js 15互換性のための設定
    serverComponentsExternalPackages: [],
    // ビルド最適化
    optimizeCss: true,
    optimizePackageImports: ['lucide-react', '@radix-ui/react-icons'],
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  // 静的エクスポート時の設定
  distDir: isProd ? "docs" : ".next",
  // 静的エクスポート時の出力ディレクトリを設定
  ...(isProd && { output: "export" }),
  // 静的アセットのパス設定
  async headers() {
    return [
      {
        source: "/_next/static/:path*",
        headers: [
          {
            key: "Cache-Control",
            value: "public, max-age=31536000, immutable",
          },
        ],
      },
      {
        source: "/favicon.ico",
        headers: [
          {
            key: "Cache-Control",
            value: "public, max-age=31536000, immutable",
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
    return [];
  },
  // Next.js 15互換性のための設定
  webpack: (config, { isServer, dev }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };
    }
    
    // 本番ビルド時の最適化
    if (!dev) {
      config.optimization = {
        ...config.optimization,
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            vendor: {
              test: /[\\/]node_modules[\\/]/,
              name: 'vendors',
              chunks: 'all',
            },
          },
        },
      };
    }
    
    return config;
  },
};

module.exports = nextConfig;