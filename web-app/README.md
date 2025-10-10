# J-Quants 株価予測 Webダッシュボード

> バージョン注記（2025-10-10）
> - 本ドキュメントは Next.js 14.2.18 / React 18.3.1 を前提に確認済みです。
> - 静的配信（GitHub Pages）時は `@/lib/path` の `resolveStaticPath()` を用いたデータ参照を徹底してください。
> - 使い方ガイドの導線を `/usage`（Web）と `../docs/USAGE.md` に統一しました。

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
 - **通知設定**: ローカル通知/メール/スケジュールの設定（ブラウザローカル保存）

### 🧪 テストカバレッジ
- **テスト実行**: ワンクリックでテストスイート実行
- **カバレッジ分析**: ステートメント、ブランチ、関数、行のカバレッジ表示
- **リアルタイム結果**: テスト結果の詳細表示とエラーログ
- **進捗可視化**: プログレスバーとパーセンテージ表示
- **テスト安定性**: 全180テストが成功（21テストスイート）
- **モック機能**: 包括的なモック設定とAPIテスト

## 技術スタック

- **Frontend**: React 18, Next.js 15
- **UI Framework**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **Build**: Turbopack
- **Deployment**: GitHub Pages
- **CI/CD**: GitHub Actions

## 📦 開発

### 必要な環境
- **Node.js 18+** (推奨: 18.17.0以上)
- **npm 9+** または **yarn 1.22+**
- **Git** (コード管理)

### クイックスタート

#### 1. リポジトリクローンとセットアップ
```bash
# メインプロジェクトから開始
cd jquants-stock-prediction

# Python環境でデータ生成
source venv/bin/activate
python3 generate_web_data.py

# Webアプリディレクトリに移動
cd web-app

# 依存関係インストール
npm install
# 追加で必要な依存関係（エラーバウンダリ）
npm install react-error-boundary
```

#### 2. ローカル開発
```bash
# 開発サーバー起動（ホットリロード有効）
npm run dev

# ブラウザで http://localhost:3000 を開く
```

#### 3. 本番ビルド
```bash
# 本番用ビルド
npm run build

# ビルド結果確認
npm run start

# 静的エクスポート（GitHub Pages用）
npm run export
```

### ✅ ポートフォリオ/ウォッチリストの見方

- **ページ**: `ポートフォリオ` → `/portfolio`, `ウォッチリスト` → `/watchlist`
  - サイドバー（デスクトップ）/ボトムナビ（モバイル）から遷移可能。
  - 直接アクセス: `http://localhost:3000/portfolio`, `http://localhost:3000/watchlist`
- **保存場所（ブラウザ）**:
  - ポートフォリオ: `localStorage` キー `user_portfolio`
  - ウォッチリスト: `localStorage` キー `user_watchlist`
- **追加手順**:
  - 銘柄詳細から「ポートフォリオに追加」「ウォッチリストに追加」を実行。
  - 実装: `src/components/StockDetailModal.tsx`（`handleAddToPortfolio`/`handleAddToWatchlist`）。
- **表示実装**:
  - `src/app/portfolio/page.tsx` と `src/app/watchlist/page.tsx` がクライアント側で読み込み・表示。
  - 空の場合は案内と `銘柄一覧を見る` ボタンを表示。

### 開発ワークフロー

#### データ更新付き開発
```bash
# 1. 最新の予測データを生成（Pythonプロジェクトルートから）
cd ../
python3 jquants_stock_prediction.py
python3 generate_web_data.py

# 個人投資ダッシュボード用データ（/personal-investment）も生成（通常版+日付別）
python3 generate_personal_investment_data.py

# 2. Webアプリを開発モードで起動
cd web-app
npm run dev
```

#### ファイル監視とホットリロード
開発サーバー起動中は以下が自動監視されます：
- `src/` 配下のTSX/TSファイル
- `public/data/` 配下のJSONファイル
- CSS/Tailwindクラス
- 設定ファイル変更

### 環境変数
Next.js設定で自動的にGitHub Pages用のパスが設定されます：
- 本番環境: `/jquants-stock-prediction`
- 開発環境: `/`

#### 個人投資ダッシュボードデータの配置仕様（重要）
- 優先: `/data/{YYYYMMDD}/personal_investment_dashboard.json`
- フォールバック: `/data/personal_investment_dashboard.json`
- 生成手順: リポジトリルートで `python3 generate_personal_investment_data.py`
  - 出力先:
    - `web-app/public/data/personal_investment_dashboard.json`
    - `web-app/public/data/{YYYYMMDD}/personal_investment_dashboard.json`
  - 開発サーバー起動中（`npm run dev`）はホットリロードで即時反映されます

### 通知設定の保存場所とデフォルト
- 保存先: ブラウザのローカルストレージ `notification-config`
- 初回アクセスで設定が未保存の場合:
  - 開発環境: アプリが安全なデフォルト設定を自動生成して保存します（通知は無効、スケジュールは 09:00/15:00、タイムゾーンは `Asia/Tokyo`）。
  - 本番環境: 未設定でもアプリは安全なデフォルト（すべての通知チャネル無効）にフォールバックして継続します。必要に応じて設定画面から有効化してください。
- 編集方法:
  - 画面右上「設定」→「通知」タブ（URL: `/settings#notifications`）
  - 変更後は自動的にローカルストレージへ保存されます

#### 通知の前提条件
- プッシュ通知を利用するには、ブラウザで通知許可が必要です
- Service Worker `public/sw.js` が登録されます（静的ホスティングでもローカル通知用途で動作）
- VAPID鍵は空のままではPush購読されません（ローカル通知のみ有効）

## デプロイ

### 静的エクスポート時の注意（GitHub Pages）
- 本プロジェクトは `next.config.js` で `output: "export"` を有効化しています（静的ホスティング向け）。
- `app/api/*` のルートは極力使用せず、静的JSON（`public/data/*.json`）を直接取得してください。
- やむを得ず `app/api/*` を使う場合は、静的互換のために `export const dynamic = 'force-static'` を宣言し、動的パラメータを持つルートは基本的に避けてください（静的エクスポート非対応）。
- 静的ホスティングではサーバー実行がないため、API ルート内でのファイル書き込み（`fs.writeFileSync` 等）は行わないでください。必要なデータは `public/data/*.json` に事前生成してください。
- クライアントからの取得は `/data/xxx.json` へ直接フェッチするフォールバックを用意しています（例: `src/lib/today/fetchTodaySummary.ts`）。

#### 個人投資ダッシュボードのデータ取得仕様
- 優先: `/data/{YYYYMMDD}/personal_investment_dashboard.json`
- フォールバック: `/data/personal_investment_dashboard.json`
- 日付の決定: `src/lib/dataClient.ts` の `getLatestIndex` と `resolveBusinessDate` を使用
- 実装参照: `src/app/personal-investment/page.tsx`

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

### 使い方ガイドの導線

- Web版ガイド: `/usage`（アプリ内のサイドバーから遷移可能）
- リポジトリ内ガイド: `../docs/USAGE.md`（クイックスタート/5分ルーティン/認証/トラブル）

## 🔄 データフロー

### 1. Python Backend
- `jquants_data_fetch.py` → J-Quants APIから株価データ取得
- `jquants_data_preprocessing.py` → 特徴量エンジニアリング  
- `jquants_stock_prediction.py` → 機械学習による予測実行
- `generate_web_data.py` → Web表示用JSONデータ生成

### 2. データファイル構造
```
web-app/public/data/
├── stock_data.json           # 基本株価データ
├── predictions.json          # 予測結果
├── model_comparison.json     # モデル比較結果
├── feature_analysis.json     # 特徴量重要度分析
├── performance_metrics.json  # 性能指標
└── dashboard_summary.json    # ダッシュボードサマリー
└── today_summary.json        # 今日のタスクページ用サマリー
```

### 3. Frontend処理
- **Next.js App Router** → 静的サイト生成（SSG）
- **React コンポーネント** → インタラクティブUI
- **Recharts** → チャート描画とアニメーション
- **Tailwind CSS** → レスポンシブスタイリング

### 5. 今日の5分ルーチン（/today）
- 目的: 毎日やることを3クリック以内で完了
- UI構成（縦スクロールのみ）
  1) チェック：データ更新状況（最終更新・鮮度バッジ Fresh/Stale）
  2) 候補：上位5銘柄（根拠＝シグナル＋予測上位＋リスク下位）
  3) アクション：保有中銘柄の「継続/利確/損切り」提案（数量 25%/50%）
  4) メモ：その日の決定を1行メモ（ローカル保存）

- データ取得:
  - 開発環境/本番共通: `src/lib/today/fetchTodaySummary.ts` が `public/data/today_summary.json` を安全取得（キャッシュ・フォールバック）

- 実装参照:
  - フック: `src/hooks/useFiveMinRoutine.ts`（候補選定ロジック＋UI状態）
  - ページ: `src/app/today/page.tsx`（旧カードを「詳細へ」リンク化して集約表示）

- DoD:
  - 新規ユーザーでも1分で結果に到達
  - 各ステップが上下方向スクロールだけで完結

### 6. パーソナライズ機能（個別投資家向け）
- ユーザー入力: 資金量、リスク許容度、興味セクター、ESG志向、目標銘柄数、除外銘柄
- 保存: ローカルストレージ（ブラウザ）に自動保存され、再訪時に復元
- 配分エンジン: リスクに応じた現金比率を確保しつつ、候補銘柄へ均等配分をベースにスコアで±20%微調整
- 候補ソース: `personal_investment_dashboard.json` のポジション/推奨から重複排除した簡易候補を生成
- UI: `個人投資` ページの「パーソナライズ」タブから編集・配分結果を確認

実装参照:
- コンテキスト: `src/contexts/UserProfileContext.tsx`
- 入力フォーム: `src/components/personalization/UserProfileForm.tsx`
- 配分ロジック: `src/lib/personalization/allocation.ts`
- 統合: `src/app/personal-investment/page.tsx`（Tabs → personalize）

### 4. CI/CD パイプライン
- **GitHub Actions** → Python処理 + Next.jsビルド自動実行
- **GitHub Pages** → 静的ファイル自動デプロイ
- **自動データ更新** → プッシュ時にデータ再生成

## 📊 使い方ガイド

### 基本的な操作

#### ダッシュボード画面
1. **株価チャート**: 移動平均線付きの価格推移を表示
2. **KPI指標**: MAE、R²、予測精度などの主要指標
3. **リアルタイム更新**: データ変更時の自動リフレッシュ

#### 予測結果画面 (`/predictions`)
1. **実測値vs予測値**: 比較グラフとテーブル
2. **散布図**: 予測精度の視覚化
3. **誤差分析**: 残差プロットと統計

#### モデル比較画面 (`/models`) 
1. **性能ランキング**: 各モデルの評価指標比較
2. **詳細メトリクス**: MAE、RMSE、R²の詳細分析
3. **ベストモデル表示**: 最優秀モデルのハイライト

#### 分析画面 (`/analysis`)
1. **特徴量重要度**: バーチャートとドーナツチャート
2. **データ統計**: 基本統計量と分布
3. **相関分析**: 特徴量間の相関マトリックス

#### レポート画面 (`/reports`)
1. **エグゼクティブサマリー**: 投資判断に必要な要約
2. **詳細レポート**: 技術的分析と市場インサイト
3. **リスク評価**: 投資リスクと軽減策
4. **PDF/JSONエクスポート**: レポートのダウンロード

#### 設定画面 (`/settings`)
1. **モデル設定**: プライマリモデル選択、再訓練設定
2. **データ設定**: 更新間隔、データポイント数制限
3. **UI設定**: ダークモード、チャート設定、表示オプション

#### テストカバレッジ画面 (`/test-coverage`)
1. **テスト実行**: 通常テスト、カバレッジ付きテストの実行
2. **カバレッジ分析**: ステートメント、ブランチ、関数、行の詳細カバレッジ
3. **結果表示**: テスト出力、エラーログ、成功/失敗ステータス
4. **進捗表示**: リアルタイムのプログレスバーとパーセンテージ

### インタラクティブ機能

#### チャート操作
- **ズーム**: マウスホイールまたはピンチ
- **パン**: ドラッグで移動
- **ツールチップ**: ポイントホバーで詳細表示
- **レジェンド**: クリックでデータ系列の表示/非表示

#### データフィルタリング
- **日付範囲選択**: カレンダーピッカー
- **モデル選択**: ドロップダウンメニュー
- **メトリクス選択**: チェックボックス
- **リアルタイム更新**: 自動リフレッシュ設定

#### エクスポート機能
- **グラフ画像**: PNG、SVG形式でダウンロード
- **データテーブル**: CSV、JSON形式でエクスポート
- **レポート**: PDF形式でのフルレポート
- **設定**: 設定ファイルのJSONエクスポート

### モバイル対応

#### レスポンシブデザイン
- **ブレークポイント**: sm(640px), md(768px), lg(1024px), xl(1280px)
- **フレキシブルレイアウト**: グリッドとフレックスボックス
- **タッチ操作**: スワイプ、ピンチズーム対応
- **縦画面最適化**: ポートレートモード専用レイアウト

#### モバイル専用機能
- **スワイプナビゲーション**: 画面間の直感的移動
- **プルトゥリフレッシュ**: データ更新の簡単操作
- **ハンバーガーメニュー**: コンパクトなナビゲーション
- **フルスクリーンチャート**: モバイル専用表示モード

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
## トラブルシューティング

### ビルド時に `Module not found: Can't resolve 'react-error-boundary'`
- 対応: `npm i react-error-boundary` を実行してください。
- 使用箇所: `src/components/GlobalErrorBoundary.tsx`

### `output: "export"` 使用時に API ルートでビルドが失敗する
- 症状: `Page "/api/..." is missing "generateStaticParams()"` や `export const dynamic = "force-static"/export const revalidate not configured` など。
- 原因: 動的パラメータ付きの API ルートは静的エクスポート非対応です。
- 対応:
  - 動的 API ルートを削除し、クライアント側で `public/data/*.json` を読み込みます。
  - 指標計算などは `src/lib/indicators.ts` を用いてクライアント側で実行します（例: `enrichWithIndicators` + `sliceByRange`）。
  - どうしても API を使う場合は、動的パラメータを持たないルートに限定し、`export const dynamic = 'force-static'` を宣言してください。

### Next.js 15 の Route Handler 型エラー
- 症状: `invalid "GET" export: Type "{ params: Record<string,string> }" is not a valid type`。
- 対応: 2引数目の型を厳密にせず `{ params }: any` を受ける、または `export async function GET(request: Request, { params }: { params: { id: string } })` など Next.js 仕様に整合する形へ更新してください。


### 学習コンテンツへの導線
- 使い方ガイド（Web）: `/usage`（サイドバーに「機械学習モデルの仕組み」「予測指標の読み方」「J‑Quants API 概要」「FAQ/動画」）
- クイックヘルプ: 画面右上の「ヘルプ」または F1 キー
- ツアー（オンボーディング）: 右上「ガイド」からいつでも再開可能。未完了の場合は新しいセッション開始時に自動表示