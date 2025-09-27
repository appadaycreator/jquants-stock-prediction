# 🚀 GitHub Pages 有効化手順

## 🔧 現在の状況
GitHub Pagesが **"currently disabled"** 状態になっています。

## ✅ 有効化手順

### 手順 1: GitHub Pages を有効化

1. **GitHubリポジトリ** → **Settings** → **Pages**
2. **"Select a source below to enable GitHub Pages"** の下で選択
3. **Source** → **"GitHub Actions"** を選択
4. **Save** をクリック

### 手順 2: 初回デプロイの実行

GitHub Pages を有効化した後、以下の方法でデプロイを実行：

**方法 A: 手動トリガー**
1. **Actions** タブに移動
2. **"Update GitHub Pages"** ワークフローを選択
3. **"Run workflow"** → **"Run workflow"** をクリック

**方法 B: プッシュトリガー**
```bash
# 何らかの軽微な変更をコミット
git add .
git commit -m "🚀 Enable GitHub Pages"
git push origin main
```

### 手順 3: 確認

1. **Actions** タブで実行状況を確認
2. 緑色の ✅ が表示されれば成功
3. **Settings** → **Pages** で URL を確認

## 🌐 期待される結果

有効化後、以下のURLでアクセス可能になります：
```
https://appadaycreator.github.io/jquants-stock-prediction/
```

## 🔍 トラブルシューティング

### Pages が有効化されない場合
- リポジトリが **Public** であることを確認
- **main** ブランチが存在することを確認
- `.github/workflows/deploy.yml` が正しくプッシュされていることを確認

### Actions が失敗する場合
1. **Actions** → **"Update GitHub Pages"** で詳細ログを確認
2. 権限エラーの場合: Source を "GitHub Actions" に設定されているか確認
3. ビルドエラーの場合: ローカルで `./deploy.sh` をテスト実行

### アクセスできない場合
- GitHub Pages の有効化から 5-10分待つ
- ブラウザのキャッシュをクリア
- HTTPS で アクセスしていることを確認

## 📋 設定確認チェックリスト

- [ ] Settings → Pages → Source = "GitHub Actions"
- [ ] リポジトリが Public
- [ ] `.github/workflows/deploy.yml` が存在
- [ ] Actions タブで "Update GitHub Pages" ワークフロー表示
- [ ] 初回実行の完了

---

この手順により、GitHub Pages が正常に有効化され、株価予測ダッシュボードが表示されるようになります！
