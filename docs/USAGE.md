# 使い方ガイド（フル版）

このドキュメントは、本リポジトリのセットアップから日次運用（1日5分ルーティン）までを一気通貫で案内します。Web配信の使い方ページ（`/usage`）と内容を整合させています。

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

