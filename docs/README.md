# J-Quants 株価予測システム - GitHub Pages

このフォルダはGitHub Pages用の静的ファイルです。

## アクセス方法

メインダッシュボード: [index.html](./index.html)

## 含まれるファイル

- `index.html` - ランディングページ（自動リダイレクト）
- `web-app/` - Next.jsビルド済みWebアプリケーション
- `.nojekyll` - GitHub Pagesで_から始まるファイルを有効化

## GitHub Pages設定

1. GitHubリポジトリ → Settings → Pages
2. Source: Deploy from a branch
3. Branch: main
4. Folder: `/docs`
5. Save

## 更新方法

```bash
# プロジェクトルートから実行
python3 generate_web_data.py  # データ生成
cd web-app && npm run build   # Webアプリビルド
cp -r web-app/dist docs/web-app  # ファイルコピー
git add docs/ && git commit -m "Update GitHub Pages" && git push
```
