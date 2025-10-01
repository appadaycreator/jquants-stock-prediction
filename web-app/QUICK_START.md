# 🚀 クイックスタートガイド

## 📋 認証設定の簡単手順

### 1. 環境変数ファイルの作成

```bash
# web-appディレクトリで実行
cd web-app

# サンプルファイルをコピー
cp env.sample .env
```

### 2. 認証情報の設定

`.env`ファイルを編集して、以下のいずれかの方法で認証情報を設定：

#### 方法1: 直接IDトークンを設定（推奨）

```bash
# .envファイルを編集
nano .env

# 以下の行を編集
JQUANTS_ID_TOKEN=your_actual_id_token_here
```

#### 方法2: メール/パスワードで自動認証

```bash
# .envファイルを編集
nano .env

# 以下の行を編集
JQUANTS_EMAIL=your_email@example.com
JQUANTS_PASSWORD=your_password
```

### 3. サーバーの起動

```bash
# 開発サーバーを起動
npm run dev

# ブラウザで http://localhost:3000 を開く
```

## 🔍 認証状態の確認

### 認証が正しく設定されているか確認

```typescript
// ブラウザのコンソールで実行
import { authManager } from '@/lib/auth';

// 認証状態をチェック
const isAuth = await authManager.isAuthenticated();
console.log('認証状態:', isAuth);

// トークンを取得
const token = await authManager.getAuthToken();
console.log('トークン:', token ? '取得済み' : '未設定');
```

## ⚠️ トラブルシューティング

### よくある問題

1. **認証エラーが発生する**
   - `.env`ファイルの値が正しいか確認
   - サーバーを再起動してください

2. **環境変数が読み込まれない**
   - `.env`ファイルが正しい場所にあるか確認
   - ファイル名が`.env`（ピリオド付き）であることを確認

3. **J-Quants APIエラーが発生する**
   - 認証情報が有効か確認
   - トークンの有効期限を確認

### デバッグ方法

```bash
# 環境変数の確認
echo $JQUANTS_ID_TOKEN

# .envファイルの内容確認
cat .env
```

## 📝 まとめ

- ✅ `.env`ファイルで認証情報を管理
- ✅ 手動入力機能は削除済み
- ✅ 環境変数からの自動認証のみ
- ✅ セキュアな認証フロー
