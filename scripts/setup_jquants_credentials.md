# jQuants API認証情報の設定ガイド

## 初回データ取得のための認証情報設定

### 1. 環境変数の設定

以下のいずれかの方法でjQuants API認証情報を設定してください。

#### 方法A: 環境変数として設定

```bash
# ターミナルで実行
export JQUANTS_EMAIL="your_email@example.com"
export JQUANTS_PASSWORD="your_password"
# または直接IDトークンを設定
export JQUANTS_ID_TOKEN="your_id_token"
```

#### 方法B: .envファイルの作成

```bash
# プロジェクトルートで実行
cp env.example .env
# .envファイルを編集して実際の認証情報を設定
```

`.env`ファイルの内容例：
```
JQUANTS_EMAIL=your_email@example.com
JQUANTS_PASSWORD=your_password
# または
JQUANTS_ID_TOKEN=your_id_token
```

### 2. jQuants IDトークンの取得方法

#### 方法A: Webインターフェースを使用（推奨）

1. Webアプリケーションを起動
```bash
cd web-app
npm run dev
```

2. ブラウザで `http://localhost:3000/token-reissue` にアクセス
3. 認証情報を入力してトークンを再発行

#### 方法B: コマンドラインスクリプトを使用

```bash
# 仮想環境を作成・アクティベート
python3 -m venv venv_token
source venv_token/bin/activate

# 必要なライブラリをインストール
pip install requests

# トークン再発行スクリプトを実行
python3 reissue_jquants_token.py
```

#### 方法C: 手動でAPIを呼び出し

```bash
# Step 1: リフレッシュトークンを取得
curl -X POST "https://api.jquants.com/v1/token/auth_user" \
  -H "Content-Type: application/json" \
  -d '{"mailaddress": "your_email@example.com", "password": "your_password"}'

# Step 2: IDトークンを取得（上記のレスポンスからrefreshTokenを取得）
curl -X POST "https://api.jquants.com/v1/token/auth_refresh" \
  -H "Content-Type: application/json" \
  -d '{"refreshtoken": "your_refresh_token_here"}'
```

### 3. 初回データ取得の実行

認証情報を設定後、以下のコマンドで初回データ取得を実行：

```bash
# 環境変数を設定してから実行
export JQUANTS_EMAIL="your_email@example.com"
export JQUANTS_PASSWORD="your_password"
python3 scripts/initial_data_fetch.py
```

または、IDトークンを直接設定：

```bash
export JQUANTS_ID_TOKEN="your_id_token"
python3 scripts/initial_data_fetch.py
```

### 4. 実行結果の確認

データ取得が完了すると、以下のファイルが生成されます：

```
docs/data/
├── stock_data.json          # メインデータファイル
├── stocks/                  # 個別銘柄ファイル
│   ├── 7203.json
│   ├── 6758.json
│   └── ...
├── index.json               # インデックスファイル
└── metadata/                # メタデータ
    └── basic.json
```

### 5. Webアプリケーションでの確認

```bash
cd web-app
npm run dev
# http://localhost:3000/test-data でテストページにアクセス
```

### 6. トラブルシューティング

#### 認証エラーの場合
- メールアドレスとパスワードが正しいか確認
- jQuantsアカウントが有効か確認
- ネットワーク接続を確認

#### データ取得エラーの場合
- API制限に達していないか確認
- 認証トークンの有効期限を確認（24時間）
- ログファイル（`logs/initial_data_fetch.log`）を確認

#### ファイル保存エラーの場合
- `docs/data/`ディレクトリの書き込み権限を確認
- ディスク容量を確認

### 7. 定期実行の設定

初回データ取得が成功したら、GitHub Actionsで定期実行を設定：

```yaml
# .github/workflows/update-stock-data.yml
# 平日9時・15時に自動実行されるように設定済み
```

### 8. 注意事項

- **IDトークンの有効期限**: 24時間で期限切れになるため、定期的な再発行が必要
- **API制限**: jQuants APIの利用制限に注意
- **セキュリティ**: 認証情報は環境変数で管理し、リポジトリにコミットしない
- **データ品質**: 取得したデータの品質を確認し、必要に応じて手動調整

## 成功例

認証情報を正しく設定し、初回データ取得が成功すると、以下のような出力が表示されます：

```
2025-10-02 15:04:36 - INFO - === 初回データ取得開始 ===
2025-10-02 15:04:36 - INFO - 認証が完了しました
2025-10-02 15:04:36 - INFO - 銘柄一覧を取得中...
2025-10-02 15:04:37 - INFO - 銘柄一覧取得完了: 5000銘柄
2025-10-02 15:04:37 - INFO - 株価データの処理開始 (最大30銘柄)
2025-10-02 15:04:37 - INFO - 処理中: 1/30 - トヨタ自動車 (7203)
2025-10-02 15:04:38 - INFO - 銘柄 7203 の価格データ取得完了: 30件
...
2025-10-02 15:04:45 - INFO - 株価データの処理完了: 30銘柄
2025-10-02 15:04:45 - INFO - メインファイル保存完了: docs/data/stock_data.json
2025-10-02 15:04:45 - INFO - 個別銘柄ファイル保存完了: 30ファイル
2025-10-02 15:04:45 - INFO - インデックスファイル保存完了: docs/data/index.json
2025-10-02 15:04:45 - INFO - メタデータファイル保存完了: docs/data/metadata/basic.json
2025-10-02 15:04:45 - INFO - === 初回データ取得完了 ===
2025-10-02 15:04:45 - INFO - 初回データ取得が正常に完了しました
```
