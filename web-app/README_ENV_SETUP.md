# 🔐 環境変数設定ガイド

## 📋 概要

認証情報をリポジトリ管理から除外し、`.env`ファイルで安全に管理します。

## 🚀 セットアップ手順

### 1. 環境変数ファイルの作成

```bash
# web-appディレクトリで実行
cd web-app

# サンプルファイルをコピー
cp env.sample .env

# .envファイルを編集
nano .env
```

### 2. 認証情報の設定

`.env`ファイルに以下のいずれかの方法で認証情報を設定：

#### 方法1: 直接IDトークンを設定（推奨）

```bash
# サーバーサイド用
JQUANTS_ID_TOKEN=your_actual_id_token_here

# クライアントサイド用（必要に応じて）
NEXT_PUBLIC_JQUANTS_ID_TOKEN=your_actual_id_token_here
```

#### 方法2: メール/パスワードで自動認証

```bash
# サーバーサイド用
JQUANTS_EMAIL=your_email@example.com
JQUANTS_PASSWORD=your_password

# クライアントサイド用（機密情報は含めない）
NEXT_PUBLIC_JQUANTS_EMAIL=your_email@example.com
NEXT_PUBLIC_JQUANTS_PASSWORD=your_password
```

### 3. セキュリティ設定の確認

```bash
# .gitignoreに.env*が含まれていることを確認
grep -n "\.env" .gitignore

# 出力例:
# 34:.env*
```

## 🔒 セキュリティ考慮事項

### ✅ 安全な設定

- **`.env`ファイル**: リポジトリに含まれない（`.gitignore`で除外）
- **サーバーサイド変数**: `JQUANTS_*`（機密情報）
- **クライアントサイド変数**: `NEXT_PUBLIC_*`（ブラウザで公開される）

### ⚠️ 注意事項

1. **クライアントサイド変数は公開される**
   - `NEXT_PUBLIC_*`で始まる変数はブラウザで公開されます
   - 機密情報（パスワード、トークン）は含めないでください

2. **本番環境での設定**
   - GitHub ActionsではSecrets and Variablesを使用
   - ローカル開発時のみ`.env`ファイルを使用

3. **ファイルの権限設定**
   ```bash
   # .envファイルの権限を制限
   chmod 600 .env
   ```

## 🚀 使用方法

### コードでの使用例

```typescript
import { authManager } from '@/lib/auth';

// 認証状態をチェック
const isAuthenticated = await authManager.isAuthenticated();

// トークンを取得
const token = await authManager.getAuthToken();

// 認証情報を更新
authManager.updateConfig({
  idToken: 'new_token_here'
});
```

### APIエンドポイントでの使用

```typescript
// /api/auth/login で自動認証
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'your_email@example.com',
    password: 'your_password'
  })
});

const { id_token } = await response.json();
```

## 🔍 トラブルシューティング

### よくある問題

1. **環境変数が読み込まれない**
   ```bash
   # サーバーを再起動
   npm run dev
   ```

2. **クライアントサイドで変数が未定義**
   - `NEXT_PUBLIC_`プレフィックスが必要
   - サーバーサイド変数はクライアントサイドで使用不可

3. **認証エラーが発生**
   - `.env`ファイルの値が正しいか確認
   - J-Quants APIの認証情報が有効か確認

### デバッグ方法

```typescript
// 環境変数の確認（開発時のみ）
console.log('Server env:', {
  email: process.env.JQUANTS_EMAIL,
  hasToken: !!process.env.JQUANTS_ID_TOKEN
});

// クライアントサイドの確認
console.log('Client env:', {
  email: process.env.NEXT_PUBLIC_JQUANTS_EMAIL,
  hasToken: !!process.env.NEXT_PUBLIC_JQUANTS_ID_TOKEN
});
```

## 📝 まとめ

- ✅ `.env`ファイルで認証情報を管理
- ✅ リポジトリに含まれない（`.gitignore`で除外）
- ✅ サーバーサイドとクライアントサイドで適切に分離
- ✅ セキュアな認証フローを実装
