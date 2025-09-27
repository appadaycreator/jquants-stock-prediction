# 🔧 GitHub Pages 設定手順 (権限エラー解決版)

## 🚨 権限エラーの原因

GitHub Actionsで以下のエラーが発生：
```
Permission to appadaycreator/jquants-stock-prediction.git denied to github-actions[bot]
```

これは旧来の"Deploy from a branch"方式でGitHub Actionsがリポジトリにプッシュしようとしたことが原因です。

## ✅ 解決方法

### 1. GitHub Pagesの設定変更

**GitHubリポジトリで設定**:
1. **Settings** → **Pages** にアクセス
2. **Source** を **"GitHub Actions"** に変更 ⚠️ **重要**
3. **Save** をクリック

![GitHub Pages Settings](https://docs.github.com/assets/cb-20862/images/help/pages/publishing-source-drop-down.png)

### 2. 権限設定の確認

**ワークフローファイル** (`.github/workflows/deploy.yml`) に以下が含まれていることを確認:
```yaml
permissions:
  contents: write
  pages: write
  id-token: write
```

### 3. デプロイ方式の変更

**従来** (権限エラーの原因):
```yaml
# git push でファイルを直接コミット → 権限エラー
- name: Commit and push
  run: git push
```

**修正後** (GitHub Pages Actions使用):
```yaml
# GitHub Pages専用のActionsを使用 → 権限エラー解決
- name: Upload artifact
  uses: actions/upload-pages-artifact@v3
  with:
    path: ./docs

- name: Deploy to GitHub Pages
  uses: actions/deploy-pages@v4
```

## 🚀 期待される動作

設定変更後、次回のプッシュで：

1. ✅ GitHub Actionsが正常実行
2. ✅ 権限エラーなし
3. ✅ 自動でGitHub Pagesにデプロイ
4. ✅ サイトが `https://appadaycreator.github.io/jquants-stock-prediction/` で表示

## 🔍 トラブルシューティング

### GitHub Actions失敗の場合
1. **Actions** タブで実行ログを確認
2. 権限エラーの場合: Settings → Pages → Source を "GitHub Actions" に変更
3. 設定ファイルエラーの場合: `config.yaml.sample` がリポジトリにあることを確認

### 404エラーの場合  
1. GitHub Actions が成功していることを確認
2. 5-10分待ってからアクセス
3. キャッシュをクリアして再アクセス

### 手動デプロイの場合
```bash
# ローカルでテスト
./deploy.sh

# 手動でActions実行
GitHub → Actions → Update GitHub Pages → Run workflow
```

## 📋 チェックリスト

- [ ] Settings → Pages → Source = "GitHub Actions"
- [ ] `.github/workflows/deploy.yml` に適切な権限設定
- [ ] mainブランチにプッシュ
- [ ] Actions実行成功
- [ ] サイトアクセス確認

---

🎯 この設定により、GitHub Pagesの権限エラーは完全に解決されます！
