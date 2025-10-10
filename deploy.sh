#!/bin/bash

# J-Quants株価予測システム デプロイメントスクリプト
# GitHub Pages用の静的サイト生成

set -e

echo "🚀 J-Quants株価予測システム デプロイメント開始"

# 1. Python環境のセットアップとデータ生成
echo "📊 データ生成中..."
python -m pip install --upgrade pip
pip install -r requirements-deploy.txt
echo "Web data generation skipped - using static data for deployment"

# 2. Webアプリケーションのビルド
echo "🏗️ Webアプリケーションをビルド中..."
cd web-app

# 依存関係のインストール
npm ci --legacy-peer-deps --prefer-offline --no-audit --no-fund
npm install react-is --save

# クリーンアップ
npm run clean

# 本番ビルド
NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 NEXT_BUILD_WORKERS=2 npm run build

# 3. ビルド成果物をdocsディレクトリにコピー
echo "📁 ビルド成果物をコピー中..."
cd ..
cp -r web-app/out/* docs/

echo "✅ デプロイメント完了"
echo "📝 変更をコミットしてプッシュしてください:"
echo "   git add ."
echo "   git commit -m 'Update deployment'"
echo "   git push origin main"