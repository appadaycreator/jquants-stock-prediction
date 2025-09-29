# 🚀 GitHub Pages デプロイガイド

## 📋 404エラー解決方法

### 問題の原因
GitHub Pagesの404エラーは以下の原因で発生していました：
1. GitHub Pages設定が正しくない
2. ベースパス設定の問題
3. 静的ファイルの配置場所が不適切

### 🔧 解決策

#### 1. GitHub Pages設定 (最重要)
1. **GitHubリポジトリページ** → **Settings** → **Pages**
2. **Source**: "Deploy from a branch" を選択
3. **Branch**: "main" を選択  
4. **Folder**: "/docs" を選択 ⚠️ (ここが重要!)
5. **Save** をクリック

#### 2. ファイル構成
```
docs/
├── index.html          # ランディングページ (リダイレクト)
├── .nojekyll           # GitHub Pages設定
├── README.md           # ドキュメント
└── web-app/            # Next.js ビルド済みファイル
    ├── index.html      # メインダッシュボード
    ├── reports/        # レポートページ
    ├── settings/       # 設定ページ
    └── _next/          # Next.js アセット
```

#### 3. アクセスURL
- **メインサイト**: `https://[ユーザー名].github.io/jquants-stock-prediction`
- **ダッシュボード**: `https://[ユーザー名].github.io/jquants-stock-prediction/web-app/`
- **レポート**: `https://[ユーザー名].github.io/jquants-stock-prediction/web-app/reports/`

## 🛠 デプロイ手順

### 方法 1: 手動デプロイ
```bash
# 1. データ生成
python3 generate_web_data.py

# 2. Webアプリビルド（修正版）
cd web-app
npm install
NODE_ENV=production npm run build

# 3. docsフォルダ更新
cd ..
rm -rf docs/web-app
cp -r web-app/dist docs/web-app
touch docs/.nojekyll

# 4. Git push
git add docs/
git commit -m "🚀 Update GitHub Pages"
git push origin main
```

### 方法 2: 自動デプロイスクリプト
```bash
# デプロイスクリプト実行
./deploy.sh
```

### 方法 3: GitHub Actions (自動)
- mainブランチへのpushで自動実行
- 手動実行も可能 (Actions → Update GitHub Pages → Run workflow)

## 🔍 トラブルシューティング

### 404エラーが続く場合
1. **GitHub Pages設定確認**
   - Settings → Pages → Source: "Deploy from a branch"
   - Branch: "main", Folder: "/docs" になっているか

2. **ファイル存在確認**
   ```bash
   # docs/index.html が存在するか確認
   ls -la docs/
   ```

3. **キャッシュクリア**
   - ブラウザのキャッシュをクリア
   - 5-10分待ってから再アクセス

### ビルドエラーの場合
```bash
# ローカルでビルドテスト
cd web-app
npm install
npm run build
npm run dev  # ローカル確認
```

## ⚠️ GitHub Pages の制約（重要）

- GitHub Pages は静的ホスティングのため、Next.js の `/api/*` や SSR/Edge 機能は動作しません。
- 静的環境では以下のフォールバックを実装済みです：
  - `web-app/src/app/api/auto-update-status/route.ts` は `unsupported` 固定レスポンス
  - `web-app/src/app/api/start-auto-update/route.ts` は 400 を返却
  - `web-app/src/app/api/stop-auto-update/route.ts` は 400 を返却
- 本リポジトリでは、静的エクスポート可能な API ルートには `export const dynamic = 'force-static'` を設定しています。
- `Service Worker` の background-sync は静的環境では無効化しています（`web-app/public/sw.js`）。
- 実サーバーが必要な機能（例: Python スクリプト実行、プロセス監視など）は、別ホスティングを利用してください。
  - 推奨: Vercel（Serverless Functions/Edge Functions）、Cloudflare Pages Functions、Render、Fly.io など

### 代替構成例

1. Web: GitHub Pages（`docs/` 配信）
2. API: Vercel（`/api/*` を同一パスで提供）
3. フロントの API 呼び出し: `NEXT_PUBLIC_API_BASE` などの環境変数でベースURLを切り替え

### データが表示されない場合
```bash
# データファイルの存在確認
ls -la web-app/public/data/
python3 generate_web_data.py  # 再生成
```

## ✅ 正常動作の確認

### チェックリスト
- [ ] `https://[ユーザー名].github.io/jquants-stock-prediction` にアクセス可能
- [ ] ランディングページが表示される
- [ ] 自動リダイレクトが動作する
- [ ] ダッシュボードが正常に表示される
- [ ] チャートが表示される
- [ ] レポートページにアクセス可能
- [ ] 設定ページにアクセス可能

### デバッグ情報
```bash
# GitHub Actionsログ確認
# GitHub → Actions → Update GitHub Pages → 最新の実行結果

# ローカルサーバーでテスト
cd web-app
npm run dev
# http://localhost:3000 でアクセス
```

## 📞 サポート

### よくある質問

**Q: ページが白紙で表示される**
A: ブラウザの開発者ツール(F12)でコンソールエラーを確認してください

**Q: データが古い**
A: `python3 generate_web_data.py` を実行してデータを再生成してください

**Q: スマホで表示が崩れる**
A: レスポンシブ対応済みです。キャッシュをクリアしてください

### 技術サポート
- GitHub Issues: プロジェクトのIssueページで質問
- ローカル確認: `npm run dev` でローカル開発サーバー起動

---
📅 最終更新: 2024年9月27日
🔧 バージョン: v1.0.0
