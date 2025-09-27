# ⚡ 3分でGitHub Pages設定完了

## 🚨 現在のエラー
```
Get Pages site failed. Please verify that the repository has Pages enabled
```

## ✅ 簡単解決法 (3ステップ)

### Step 1: GitHub Pages有効化
1. **このリポジトリページで**: Settings → Pages
2. **Source**: "GitHub Actions" を選択
3. **Save** をクリック

### Step 2: 再実行
1. **Actions** タブをクリック
2. **"Update GitHub Pages"** を選択
3. **"Re-run all jobs"** をクリック

### Step 3: 確認
- 5分後に `https://appadaycreator.github.io/jquants-stock-prediction/` にアクセス

## 🔧 代替方法 (フォールバック)

GitHub Actionsが失敗し続ける場合：

### 方法A: gh-pagesブランチ使用
1. Actions実行後、`gh-pages` ブランチが作成される
2. Settings → Pages → Source: "Deploy from a branch"
3. Branch: "gh-pages" を選択
4. Save

### 方法B: 手動アップロード
```bash
# ローカルで実行
python3 generate_web_data.py
cd web-app && npm run build
cp -r dist ../docs/web-app

# GitHubにプッシュ
git add docs/
git commit -m "Manual deploy"
git push

# Settings → Pages → Source: "Deploy from a branch"
# Branch: "main", Folder: "/docs"
```

## 📱 期待される結果

設定完了後:
- ✅ 美しい株価予測ダッシュボード
- ✅ インタラクティブチャート
- ✅ モデル性能比較
- ✅ 詳細分析レポート

## 🆘 まだ動かない場合

1. **リポジトリがPublic**であることを確認
2. **Actions権限**を確認: Settings → Actions → General → Workflow permissions
3. **Issues**で質問を投稿

---

🎯 **最も重要**: Settings → Pages → Source = "GitHub Actions" の設定!
