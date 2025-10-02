# jQuants IDトークン再発行ガイド

## 概要
jQuantsのIDトークンは24時間で期限切れになるため、定期的な再発行が必要です。

## 手動でのトークン再発行手順

### 1. jQuants APIに直接アクセス

以下のURLにアクセスしてトークンを取得してください：

#### Step 1: リフレッシュトークンの取得
```bash
curl -X POST "https://api.jquants.com/v1/token/auth_user" \
  -H "Content-Type: application/json" \
  -d '{
    "mailaddress": "your_email@example.com",
    "password": "your_password"
  }'
```

#### Step 2: IDトークンの取得
上記のレスポンスから `refreshToken` を取得し、以下のコマンドを実行：

```bash
curl -X POST "https://api.jquants.com/v1/token/auth_refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refreshtoken": "your_refresh_token_here"
  }'
```

### 2. 環境変数ファイルの更新

取得したIDトークンを `.env` ファイルに設定：

```bash
# .env ファイルを作成または更新
echo "JQUANTS_EMAIL=your_email@example.com" >> .env
echo "JQUANTS_PASSWORD=your_password" >> .env
echo "JQUANTS_ID_TOKEN=your_id_token_here" >> .env
```

### 3. トークンのテスト

```bash
# トークンが正しく動作するかテスト
curl -H "Authorization: Bearer your_id_token_here" \
  "https://api.jquants.com/v1/listed/info"
```

## 自動化スクリプトの使用

### 前提条件
- Python 3.7以上
- requests ライブラリ

### インストール
```bash
# 仮想環境の作成とライブラリのインストール
python3 -m venv venv_token
source venv_token/bin/activate
pip install requests
```

### 実行
```bash
# 仮想環境をアクティベートしてスクリプトを実行
source venv_token/bin/activate
python3 reissue_jquants_token.py
```

## 注意事項

1. **セキュリティ**: パスワードとトークンは機密情報です。`.env` ファイルをGitにコミットしないでください。

2. **有効期限**: IDトークンは24時間で期限切れになります。定期的な更新が必要です。

3. **環境変数の設定**: アプリケーションを再起動して新しい環境変数を読み込んでください。

## トラブルシューティング

### よくあるエラー

1. **認証エラー (401)**
   - メールアドレスとパスワードを確認
   - jQuantsアカウントが有効か確認

2. **トークン取得エラー**
   - リフレッシュトークンが正しいか確認
   - ネットワーク接続を確認

3. **API接続エラー**
   - トークンの有効期限を確認
   - 正しいAuthorizationヘッダーが設定されているか確認

### ログの確認
```bash
# アプリケーションのログを確認
tail -f logs/jquants.log
```

## 自動更新の設定

### cronジョブの設定（推奨）
```bash
# 毎日午前2時にトークンを更新
0 2 * * * cd /path/to/your/project && source venv_token/bin/activate && python3 reissue_jquants_token.py
```

### GitHub Actionsでの自動更新
```yaml
name: Update JQuants Token
on:
  schedule:
    - cron: '0 2 * * *'  # 毎日午前2時
  workflow_dispatch:

jobs:
  update-token:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Update Token
        run: |
          python3 -m venv venv_token
          source venv_token/bin/activate
          pip install requests
          python3 reissue_jquants_token.py
```

## サポート

問題が解決しない場合は、以下を確認してください：

1. jQuants APIの公式ドキュメント
2. アプリケーションのログファイル
3. ネットワーク接続状況
4. 認証情報の正確性
