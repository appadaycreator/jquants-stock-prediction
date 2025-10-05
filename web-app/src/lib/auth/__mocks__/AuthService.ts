/**
 * AuthServiceのモック実装
 * テスト用の擬似認証システム
 */

import { AuthService, AuthCredentials, AuthTokens, AuthStatus } from "../AuthService";

export class MockAuthService {
  private static mockTokens: AuthTokens | null = null;
  private static mockStatus: AuthStatus = {
    isConnected: false,
    tokenType: null,
    expiresAt: null,
    timeRemaining: null,
    lastUpdate: null,
  };

  static async saveCredentials(credentials: AuthCredentials): Promise<void> {
    // モック実装: 常に成功
    console.log("Mock: 認証情報を保存", { hasRefreshToken: !!credentials.refreshToken });
  }

  static async getStoredCredentials(): Promise<AuthCredentials | null> {
    // モック実装: テスト用のリフレッシュトークンを返す
    return { refreshToken: "mock_refresh_token_12345" };
  }

  static clearCredentials(): void {
    // モック実装: 状態をリセット
    MockAuthService.mockTokens = null;
    MockAuthService.mockStatus = {
      isConnected: false,
      tokenType: null,
      expiresAt: null,
      timeRemaining: null,
      lastUpdate: null,
    };
  }

  static async refreshIdToken(refreshToken: string): Promise<AuthTokens> {
    // モック実装: 擬似トークンを生成
    const tokens: AuthTokens = {
      idToken: `mock_id_token_${Date.now()}`,
      refreshToken: `mock_refresh_token_${Date.now()}`,
      expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
      tokenType: "Bearer",
    };

    MockAuthService.mockTokens = tokens;
    MockAuthService.mockStatus = {
      isConnected: true,
      tokenType: "id",
      expiresAt: tokens.expiresAt,
      timeRemaining: 24 * 60 * 60,
      lastUpdate: new Date().toISOString(),
    };

    return tokens;
  }

  static async getRefreshToken(email: string, password: string): Promise<AuthTokens> {
    // モック実装: 認証情報を検証
    if (email === "test@example.com" && password === "password123") {
      return await MockAuthService.refreshIdToken("mock_refresh_token");
    }
    throw new Error("認証に失敗しました");
  }

  static async checkAuthStatus(): Promise<AuthStatus> {
    // モック実装: 現在の状態を返す
    return MockAuthService.mockStatus;
  }

  static async testConnection(credentials: AuthCredentials): Promise<boolean> {
    // モック実装: 接続テスト
    if (credentials.email === "test@example.com" && credentials.password === "password123") {
      return true;
    }
    if (credentials.refreshToken) {
      return true;
    }
    return false;
  }

  static async autoRefresh(): Promise<boolean> {
    // モック実装: 自動更新
    try {
      await MockAuthService.refreshIdToken("mock_refresh_token");
      return true;
    } catch (error) {
      return false;
    }
  }

  static async getOfflineData(): Promise<any> {
    // モック実装: オフラインデータ
    return {
      stocks: [
        { code: "7203", name: "トヨタ自動車", price: 2500 },
        { code: "6758", name: "ソニーグループ", price: 12000 },
      ],
      timestamp: new Date().toISOString(),
    };
  }

  static async saveOfflineData(data: any): Promise<void> {
    // モック実装: オフラインデータ保存
    console.log("Mock: オフラインデータを保存", data);
  }

  // テスト用のヘルパーメソッド
  static setMockStatus(status: Partial<AuthStatus>): void {
    MockAuthService.mockStatus = { ...MockAuthService.mockStatus, ...status };
  }

  static getMockStatus(): AuthStatus {
    return MockAuthService.mockStatus;
  }

  static setMockTokens(tokens: AuthTokens | null): void {
    MockAuthService.mockTokens = tokens;
  }

  static getMockTokens(): AuthTokens | null {
    return MockAuthService.mockTokens;
  }
}
