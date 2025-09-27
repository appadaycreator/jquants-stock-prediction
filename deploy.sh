#!/bin/bash

# J-Quants株価予測システム GitHub Pages デプロイスクリプト

echo "🚀 GitHub Pages デプロイを開始します..."

# 1. Pythonデータ生成
echo "📊 Web表示用データを生成中..."
python3 generate_web_data.py

# 2. Web-appディレクトリに移動
cd web-app

# 3. 依存関係インストール（初回のみ必要）
if [ ! -d "node_modules" ]; then
    echo "📦 依存関係をインストール中..."
    npm install
fi

# 4. Next.jsビルド
echo "🔨 Webアプリケーションをビルド中..."
npm run build

# 5. .nojekyllファイルを追加（GitHub Pagesで_から始まるファイルを有効化）
touch dist/.nojekyll

# 6. GitHub PagesのためのCNAMEファイル（カスタムドメインがある場合）
# echo "your-domain.com" > dist/CNAME

echo "✅ ビルド完了！"
echo ""
echo "📁 デプロイ用ファイルは web-app/dist/ にあります"
echo "🌐 GitHub リポジトリにプッシュしてGitHub Pagesを有効化してください"
echo ""
echo "GitHub Pages設定手順："
echo "1. GitHubリポジトリ → Settings → Pages"
echo "2. Source: Deploy from a branch"
echo "3. Branch: main"
echo "4. Folder: / (root)"
echo "5. Save"
echo ""
echo "または GitHub Actions を使用する場合："
echo "1. GitHubリポジトリ → Settings → Pages" 
echo "2. Source: GitHub Actions"
