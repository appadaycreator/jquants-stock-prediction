# 使い方ガイド（フル版）

このドキュメントは、本リポジトリのセットアップから日次運用（1日5分ルーティン）までを一気通貫で案内します。Web配信の使い方ページ（`/usage`）と内容を整合させています。

### 共有ホバー説明（全画面）
画面内の任意の要素に `data-help` / `data-tooltip` / `aria-label` / `title` のいずれかを付与すると、ホバー（またはキーボードフォーカス）で説明がポップ表示されます。追加のラップや特定コンポーネントの導入は不要です。

- 優先順位: `data-help` > `data-tooltip` > `aria-label` > `title`
- 実装箇所: `web-app/src/components/GlobalHoverHelp.tsx`（`app/layout.tsx` に常時マウント）
- 設計意図: 既存の `EnhancedTooltip` など個別ツールチップの邪魔をせず、属性を付けるだけで最低限の説明を即時提供
- サンプル:
  ```tsx
  <button data-help="次の分析を再実行します">再実行</button>
  <input aria-label="銘柄コードを入力" />
  <span title="予測スコアの詳細">スコア</span>
  ```

## クイックスタート（最短3分）

1) 仮想環境と依存導入（Python）
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2) 認証設定（最終方針に準拠）
```bash
cp env.example .env
# .env を編集（メール/パスワードのみを設定。IDトークンは保存しない）
# JQUANTS_EMAIL=your_email@example.com
# JQUANTS_PASSWORD=your_password

# Webアプリ用
cd web-app && cp env.sample .env.local
```

3) データ生成とWeb起動
```bash
cd ..
python3 generate_web_data.py
cd web-app
npm install
npm run dev
# ブラウザで http://localhost:3000 を開く
```

リンク:
- Web使い方ページ: `/usage`
- リポジトリのトップ: `README.md`（最新の要点・変更点）

## 1日5分ルーティン（推奨ワークフロー）

ホーム → 「5分ルーティン」で以下の順に進めます。
1. 健全性バッジ確認（OK/警告/停止）
2. 分析を実行（ワンクリック）
3. Top5候補と判断パネルで「EV>0/RR>1.2/流動性OK」のみチェック
4. 「メモ保存」で本日の決定を保存（IndexedDB）

関連ページ:
- 詳細分析: `/analysis`（例: `/analysis?symbol=7203`）
- ポートフォリオ/ウォッチリスト: `/portfolio`, `/watchlist`
- 分析履歴: `/analysis-history`
- 設定 → 通知: `/settings#notifications`

## 銘柄一覧（/listed-data）の使い方（追加）

### クイックフィルタ（新）
- 上昇/下落: 当日騰落がプラス/マイナスの銘柄をワンクリック抽出
- 高出来高: 出来高の上位約25%を抽出（ページング・他フィルタと併用可）
- 市場ショートカット: プライム/スタンダード/グロースをトグルで切替

### 検索・詳細フィルタ
- 検索: 銘柄名/コード（全角半角自動正規化）
- セクター/市場: プルダウンで絞り込み
- 詳細フィルタ: 価格範囲／出来高範囲の数値入力

### ソート（騰落率を追加）
- 列ヘッダクリックで昇順/降順を切替
- 対応列: コード／会社名／セクター／市場／価格／出来高／騰落率（新）

### URLクエリ同期（新）
- 検索・フィルタ・ソート・ページがURLに同期され、共有・再現が容易
- 例: `?q=トヨタ&sector=自動車&sortBy=changePercent&sortOrder=desc&up=1&hv=1`

### CSVエクスポート（新）
- 画面右上「CSVエクスポート」で、現在の絞り込み・ソート結果をダウンロード

### ウォッチリスト追加（新）
- 各行「ウォッチ追加」で `localStorage:user_watchlist` に保存（後方互換）

### テーブル列固定（表示改善）
- 左側の2列（銘柄コード・会社名）をスクロール時も固定し、後続列（例: セクター/市場/価格）が常に視認可能です。
- 実装仕様（参考）:
  - 1列目: `w-[8rem] sticky left-0 z-10` + 背景 `bg-gray-50/bg-white`
  - 2列目: `sticky left-[11rem] z-10`
  - 列幅変更時は 2列目の `left-[..]` を1列目の合計幅に揃えてください。

## 認証とセキュリティ（最終方針）

- 原則: IDトークンは環境変数に保存しません（短期キャッシュのみ）。
- 運用: メール/パスワード（またはリフレッシュトークン）で毎回再取得。
- 参考: `docs/AUTH_FINAL_GUIDE.md`

## GitHub Pages（静的配信）での重要ポイント

- パス解決: すべての静的取得は `@/lib/path` の `resolveStaticPath()` を使用。
- API制約: 静的環境では `/api/*` は原則使えません（必要なデータは `public/data/*.json` を事前生成）。
- データ配置: `web-app/public/data/`（ビルドで `web-app/docs/data/` に同期され配信）。

## トラブルシューティング

- 404（データ参照）: 参照URLが `resolveStaticPath("/data/xxx.json")` を経由しているか確認。
- APIが使えない: クライアントで `public/data/*.json` フォールバックが機能しているか確認。
- Python依存不足: `pip install -r requirements.txt` を実行。UIはモックで継続します。
- Next.js ルート型エラー: Route Handler の型定義をNext.js仕様に合わせて更新。

## よく使うコマンド集

```bash
# 仮想環境起動
source venv/bin/activate

# データ生成
python3 generate_web_data.py

# Web起動
cd web-app && npm run dev

# 本番ビルド
npm run build && npm run start
```

## 次に読む（横展開の確認）

- 全体仕様: `SPECIFICATIONS.md`
- 新NISA: `SPECIFICATIONS_NISA.md`, `SPECIFICATIONS_NISA_OPTIMIZATION.md`
- 個人投資ダッシュボード: リポジトリ `README.md` の該当セクション
- 認証最終方針: `docs/AUTH_FINAL_GUIDE.md`

