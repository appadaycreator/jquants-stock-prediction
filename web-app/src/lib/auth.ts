/**
 * 認証トークン管理
 * GitHub Actionsとローカル環境の両方に対応
 */

interface AuthConfig {
  email?: string;
  password?: string;
  idToken?: string;
}

export class AuthManager {
  private static instance: AuthManager;
  private config: AuthConfig = {};

  private constructor() {
    this.loadConfig();
  }

  static getInstance(): AuthManager {
    if (!AuthManager.instance) {
      AuthManager.instance = new AuthManager();
    }
    return AuthManager.instance;
  }

  private loadConfig(): void {
    // 環境変数から認証情報を取得（.envファイルから読み込み）
    if (typeof window !== "undefined") {
      // クライアントサイド（NEXT_PUBLIC_プレフィックスが必要）
      this.config = {
        email: process.env.NEXT_PUBLIC_JQUANTS_EMAIL,
        password: process.env.NEXT_PUBLIC_JQUANTS_PASSWORD,
        idToken: process.env.NEXT_PUBLIC_JQUANTS_ID_TOKEN,
      };
    } else {
      // サーバーサイド（.envファイルから直接読み込み）
      this.config = {
        email: process.env.JQUANTS_EMAIL,
        password: process.env.JQUANTS_PASSWORD,
        idToken: process.env.JQUANTS_ID_TOKEN,
      };
    }
  }

  /**
   * 認証トークンを取得（環境変数のみ）
   */
  async getAuthToken(): Promise<string | null> {
    // 1. 環境変数から直接IDトークンを取得
    if (this.config.idToken) {
      return this.config.idToken;
    }

    // 2. メール/パスワードからトークンを取得
    if (this.config.email && this.config.password) {
      return await this.authenticateWithCredentials(
        this.config.email,
        this.config.password,
      );
    }

    // 手動入力機能は削除 - 環境変数からの認証のみ
    return null;
  }

  /**
   * 認証情報でトークンを取得
   */
  private async authenticateWithCredentials(
    email: string,
    password: string,
  ): Promise<string | null> {
    try {
      // J-Quants APIにログインしてトークンを取得
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const data = await response.json();
        const token = data.id_token;
        
        // 手動入力機能は削除 - 環境変数のみを使用
        // ローカルストレージへの保存は削除
        
        return token;
      }
    } catch (error) {
      console.error("認証エラー:", error);
    }

    return null;
  }

  /**
   * 認証状態をチェック
   */
  async isAuthenticated(): Promise<boolean> {
    const token = await this.getAuthToken();
    return token !== null;
  }

  /**
   * トークンをクリア（環境変数のみ）
   */
  clearToken(): void {
    // 手動入力機能は削除 - 環境変数のみを使用
    this.config = {};
  }

  /**
   * 認証情報を更新
   */
  updateConfig(config: Partial<AuthConfig>): void {
    this.config = { ...this.config, ...config };
  }
}

// シングルトンインスタンスをエクスポート
export const authManager = AuthManager.getInstance();
