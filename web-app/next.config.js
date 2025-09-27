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
  assetPrefix: '.',
  basePath: '',
}

module.exports = nextConfig
