/**
 * jQuants認証管理クラス
 * IDトークンの有効性チェックと自動再取得機能
 */

interface AuthTokens {
  idToken: string;
  refreshToken: string;
}

interface AuthResponse {
  refreshToken?: string;
  idToken?: string;
}

export class JQuantsAuthManager {
  private static readonly AUTH_URL = "https://api.jquants.com/v1/token/auth_user";
  private static readonly REFRESH_URL = "https://api.jquants.com/v1/token/auth_refresh";
  private static readonly TEST_URL = "https://api.jquants.com/v1/listed/info";
  private static readonly TOKEN_EXPIRY_BUFFER = 300; // 5分前から更新

  /**
   * JWTトークンの有効期限をチェック
   */
  private isTokenExpired(token: string): boolean {
    try {
      const parts = token.split(".");
      if (parts.length !== 3) return true;

      const payload = parts[1];
      const missingPadding = payload.length % 4;
      const paddedPayload = missingPadding 
        ? payload + "=".repeat(4 - missingPadding)
        : payload;

      const decodedPayload = JSON.parse(atob(paddedPayload));
      const expTimestamp = decodedPayload.exp || 0;
      const currentTimestamp = Math.floor(Date.now() / 1000);

      return (expTimestamp - currentTimestamp) < JQuantsAuthManager.TOKEN_EXPIRY_BUFFER;
    } catch (error) {
      console.error("トークン解析エラー:", error);
      return true;
    }
  }

  /**
   * APIエンドポイントでトークンをテスト
   */
  private async testTokenWithAPI(token: string): Promise<boolean> {
    try {
      const response = await fetch(JQuantsAuthManager.TEST_URL, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      return response.ok;
    } catch (error) {
      console.error("APIテストエラー:", error);
      return false;
    }
  }

  /**
   * メールアドレスとパスワードで新しいトークンを取得
   */
  private async getNewTokens(email: string, password: string): Promise<AuthTokens | null> {
    try {
      console.log("新しいトークンを取得中...");

      // 認証リクエスト
      const authResponse = await fetch(JQuantsAuthManager.AUTH_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          mailaddress: email,
          password: password,
        }),
      });

      if (!authResponse.ok) {
        throw new Error(`認証エラー: HTTP ${authResponse.status}`);
      }

      const authResult: AuthResponse = await authResponse.json();
      const refreshToken = authResult.refreshToken;

      if (!refreshToken) {
        throw new Error("リフレッシュトークンの取得に失敗しました");
      }

      console.log("リフレッシュトークンを取得しました");

      // IDトークンを取得
      const refreshResponse = await fetch(JQuantsAuthManager.REFRESH_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          refreshtoken: refreshToken,
        }),
      });

      if (!refreshResponse.ok) {
        throw new Error(`トークン更新エラー: HTTP ${refreshResponse.status}`);
      }

      const refreshResult: AuthResponse = await refreshResponse.json();
      const idToken = refreshResult.idToken;

      if (!idToken) {
        throw new Error("IDトークンの取得に失敗しました");
      }

      console.log("IDトークンを取得しました");

      return {
        idToken,
        refreshToken,
      };

    } catch (error) {
      console.error("認証エラー:", error);
      return null;
    }
  }

  /**
   * リフレッシュトークンでIDトークンを更新
   */
  private async refreshIdToken(refreshToken: string): Promise<string | null> {
    try {
      console.log("リフレッシュトークンでIDトークンを更新中...");

      const response = await fetch(JQuantsAuthManager.REFRESH_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          refreshtoken: refreshToken,
        }),
      });

      if (!response.ok) {
        throw new Error(`トークン更新エラー: HTTP ${response.status}`);
      }

      const result: AuthResponse = await response.json();
      const newIdToken = result.idToken;

      if (newIdToken) {
        console.log("IDトークンの更新に成功しました");
        return newIdToken;
      } else {
        console.error("IDトークンの更新に失敗しました");
        return null;
      }

    } catch (error) {
      console.error("トークン更新エラー:", error);
      return null;
    }
  }

  /**
   * 有効なIDトークンを取得（必要に応じて更新）
   */
  async getValidToken(): Promise<string | null> {
    const currentIdToken = process.env.JQUANTS_ID_TOKEN || process.env.NEXT_PUBLIC_JQUANTS_ID_TOKEN;
    const currentRefreshToken = process.env.JQUANTS_REFRESH_TOKEN || process.env.NEXT_PUBLIC_JQUANTS_REFRESH_TOKEN;
    const email = process.env.JQUANTS_EMAIL || process.env.NEXT_PUBLIC_JQUANTS_EMAIL;
    const password = process.env.JQUANTS_PASSWORD || process.env.NEXT_PUBLIC_JQUANTS_PASSWORD;

    if (!currentIdToken) {
      console.warn("IDトークンが設定されていません");
      return null;
    }

    // 1. 現在のトークンが有効かチェック
    if (!this.isTokenExpired(currentIdToken)) {
      const isApiValid = await this.testTokenWithAPI(currentIdToken);
      if (isApiValid) {
        console.log("現在のトークンは有効です");
        return currentIdToken;
      }
    }

    // 2. リフレッシュトークンで更新を試行
    if (currentRefreshToken) {
      console.log("リフレッシュトークンで更新を試行...");
      const newIdToken = await this.refreshIdToken(currentRefreshToken);
      if (newIdToken) {
        const isApiValid = await this.testTokenWithAPI(newIdToken);
        if (isApiValid) {
          console.log("リフレッシュトークンでの更新に成功しました");
          return newIdToken;
        }
      }
    }

    // 3. メールアドレスとパスワードで新規取得
    if (email && password) {
      console.log("メールアドレスとパスワードで新規認証を試行...");
      const newTokens = await this.getNewTokens(email, password);
      if (newTokens) {
        const isApiValid = await this.testTokenWithAPI(newTokens.idToken);
        if (isApiValid) {
          console.log("新規認証に成功しました");
          return newTokens.idToken;
        }
      }
    }

    console.error("すべての認証方法が失敗しました");
    return null;
  }

  /**
   * トークンの有効性をチェック
   */
  async isTokenValid(): Promise<boolean> {
    const currentIdToken = process.env.JQUANTS_ID_TOKEN || process.env.NEXT_PUBLIC_JQUANTS_ID_TOKEN;
    
    if (!currentIdToken) {
      return false;
    }

    if (this.isTokenExpired(currentIdToken)) {
      return false;
    }

    return await this.testTokenWithAPI(currentIdToken);
  }
}

export default JQuantsAuthManager;
