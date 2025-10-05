import { StaticApiClient } from "./api/StaticApiClient";
import { UnifiedApiClient } from "./unified-api-client";

/**
 * 環境に応じて適切なAPIクライアントを選択するファクトリー
 */
export class ApiClientFactory {
  private static instance: ApiClientFactory;
  private client: StaticApiClient | UnifiedApiClient | null = null;

  private constructor() {}

  static getInstance(): ApiClientFactory {
    if (!ApiClientFactory.instance) {
      ApiClientFactory.instance = new ApiClientFactory();
    }
    return ApiClientFactory.instance;
  }

  /**
   * 環境に応じて適切なAPIクライアントを取得
   */
  getClient(): StaticApiClient | UnifiedApiClient {
    if (this.client) {
      return this.client;
    }

    // 静的サイトかどうかを判定
    if (this.isStaticSite()) {
      this.client = new StaticApiClient();
    } else {
      this.client = new UnifiedApiClient();
    }

    return this.client;
  }

  /**
   * 静的サイトかどうかを判定
   */
  private isStaticSite(): boolean {
    if (typeof window === "undefined") return true;
    
    // GitHub Pages のドメインパターンをチェック
    const hostname = window.location.hostname;
    return hostname.includes("github.io") || 
           hostname.includes("netlify.app") || 
           hostname.includes("vercel.app") ||
           hostname.includes("appadaycreator.github.io");
  }

  /**
   * クライアントをリセット（テスト用）
   */
  reset(): void {
    this.client = null;
  }
}

// シングルトンインスタンス
export const apiClientFactory = ApiClientFactory.getInstance();

// 便利な関数としてエクスポート
export const getApiClient = () => apiClientFactory.getClient();
export const testConnection = async () => {
  const client = getApiClient();
  if ("testConnection" in client) {
    return await client.testConnection();
  } else {
    // StaticApiClientの場合は常に成功を返す
    return { success: true, message: "静的サイトモード: モックデータを使用中" };
  }
};
