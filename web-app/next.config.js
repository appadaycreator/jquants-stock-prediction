/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  skipTrailingSlashRedirect: true,
  distDir: 'dist',
  images: {
    unoptimized: true
  },
  // GitHub Pages用の設定を簡素化
  assetPrefix: '',
  basePath: '',
}

module.exports = nextConfig
