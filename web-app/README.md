# J-Quants 株価予測 Webダッシュボード

React/Next.jsベースのインタラクティブな株価予測ダッシュボードです。

## 機能

### 📊 ダッシュボード
- **リアルタイム株価チャート**: 移動平均線付きの価格推移
- **パフォーマンス指標**: MAE、R²、予測精度などの主要指標
- **インタラクティブグラフ**: Rechartsを使用した動的チャート
- **レスポンシブデザイン**: デスクトップ・モバイル対応

### 📈 予測結果
- **実際値 vs 予測値**: 比較グラフ表示
- **予測誤差分布**: バーチャートでの誤差可視化
- **散布図**: 実測値と予測値の相関分析

### 🏆 モデル比較
- **性能ランキング**: MAE、RMSE、R²での自動ランキング
- **詳細メトリクス**: 各モデルの包括的評価
- **ベストモデル選択**: 最優秀モデルの自動識別

### 🔍 分析
- **特徴量重要度**: バーチャートと円グラフでの可視化
- **データ分布**: 統計情報の詳細表示
- **トレンド分析**: 時系列パターンの解析

### 📄 レポート機能
- **エグゼクティブサマリー**: 主要指標の要約
- **詳細分析レポート**: モデル性能と市場インサイト
- **リスク評価**: 投資リスクとその軽減策
- **レポートエクスポート**: JSON形式でのダウンロード

### ⚙️ 設定
- **モデル設定**: プライマリモデル選択、再訓練設定
- **データ設定**: 更新間隔、データポイント数制限
- **UI設定**: テーマ、更新頻度、表示オプション

## 技術スタック

- **Frontend**: React 18, Next.js 15
- **UI Framework**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **Build**: Turbopack
- **Deployment**: GitHub Pages
- **CI/CD**: GitHub Actions

## 開発

### 必要な環境
- Node.js 18+
- npm または yarn

### ローカル開発
```bash
# 依存関係インストール
npm install

# 開発サーバー起動
npm run dev

# ビルド
npm run build

# 静的エクスポート（GitHub Pages用）
npm run build && npm run export
```

### 環境変数
Next.js設定で自動的にGitHub Pages用のパスが設定されます：
- 本番環境: `/jquants-stock-prediction`
- 開発環境: `/`

## デプロイ

### GitHub Pages
1. GitHub リポジトリの Settings → Pages
2. Source: GitHub Actions を選択
3. メインブランチにプッシュすると自動デプロイ

### 手動デプロイ
```bash
# ビルド
npm run build

# dist フォルダを任意の静的ホスティングサービスにアップロード
```

## データフロー

1. **Python Backend**: 
   - `generate_web_data.py` が予測結果をJSON形式で生成
   - `web-app/public/data/` に各種データファイルを出力

2. **Frontend**: 
   - Next.jsアプリが JSON データを読み込み
   - React コンポーネントでインタラクティブな UI を提供

3. **CI/CD**: 
   - GitHub Actions がPython処理とNext.jsビルドを自動実行
   - 静的ファイルをGitHub Pagesにデプロイ

## カスタマイズ

### 新しいチャートの追加
`src/app/page.tsx` にRechartsコンポーネントを追加

### 新しいページの追加
`src/app/[ページ名]/page.tsx` ファイルを作成

### スタイリングの変更
Tailwind CSSクラスを使用してスタイリング

## パフォーマンス

- **バンドルサイズ**: 約226KB (First Load JS)
- **静的生成**: 全ページ事前生成
- **画像最適化**: Next.js自動最適化
- **コード分割**: 自動的なチャンク分割

## ブラウザサポート

- Chrome (最新)
- Firefox (最新) 
- Safari (最新)
- Edge (最新)

## ライセンス

MIT License