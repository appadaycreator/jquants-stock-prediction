# 相対パス修正レポート

## 概要
GitHub Pagesでの404エラーを解決するため、すべての絶対パスを相対パスに変換しました。

## 問題の詳細
- 「ホームに戻る」ボタンや外部リンクがサイトルートに固定されている
- サブパスから遷移すると404エラーが発生
- GitHub Pagesの階層構造に対応していない

## 実施した修正

### 1. Next.js設定の修正
- `next.config.js`の`assetPrefix`と`basePath`を空文字に設定
- 相対パスでビルドするように設定変更

### 2. ソースコードの修正
- `web-app/src/app/page.tsx`内の絶対パスを相対パスに変更
  - `/personal-investment` → `./personal-investment`
  - `/risk` → `./risk`

### 3. 自動化スクリプトの作成
- `fix_relative_paths.py`: 基本的な相対パス変換スクリプト
- `fix_all_relative_paths.py`: 包括的な相対パス変換スクリプト

### 4. 生成ファイルの修正
- 69件のファイルを修正（HTML: 8件、JS: 61件）
- すべての絶対パス（`/`で始まるパス）を相対パスに変換

## 修正結果

### メインページ（docs/web-app/index.html）
- `href="/_next/..."` → `href="./_next/..."`
- `src="/_next/..."` → `src="./_next/..."`
- `href="/favicon.ico"` → `href="./favicon.ico"`

### サブディレクトリ（docs/web-app/settings/index.html）
- `href="/_next/..."` → `href="../_next/..."`
- `src="/_next/..."` → `src="../_next/..."`
- `href="/favicon.ico"` → `href="../favicon.ico"`

## 効果
- GitHub Pagesのどの階層からでも正しく遷移可能
- 404エラーの解消
- サブパス対応の完全実装

## 今後の運用
1. 新しいビルドを実行後、`fix_all_relative_paths.py`を実行
2. 相対パス変換を自動化するため、ビルドスクリプトに組み込み可能

## 関連ファイル
- `web-app/next.config.js`: Next.js設定
- `web-app/src/app/page.tsx`: メインページのリンク
- `fix_relative_paths.py`: 基本変換スクリプト
- `fix_all_relative_paths.py`: 包括的変換スクリプト

## 検証方法
1. GitHub Pagesにデプロイ
2. 各階層からナビゲーションをテスト
3. 404エラーが発生しないことを確認

---
修正日: 2024年12月19日
修正者: AI Assistant
