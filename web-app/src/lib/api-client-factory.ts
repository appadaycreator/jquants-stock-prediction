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
    // SSR中に生成したクライアントをクライアント側へ持ち込まないように、
    // ブラウザ環境で初回アクセス時に再判定して固定化する。
    if (typeof window === "undefined") {
      // サーバー側では常にStaticを返すが、キャッシュはしない
      return new StaticApiClient();
    }

    if (this.client) {
      return this.client;
    }

    // 静的サイトかどうかを判定（ブラウザでのみ実行）
    this.client = this.isStaticSite() ? new StaticApiClient() : new UnifiedApiClient();
    return this.client;
  }

  /**
   * 静的サイトかどうかを判定
   */
  private isStaticSite(): boolean {
    if (typeof window === "undefined") return true;

    // 実データ強制オーバーライド（環境変数）
    // NEXT_PUBLIC_FORCE_REAL_API=true で常に UnifiedApiClient を使う
    if (process.env.NEXT_PUBLIC_FORCE_REAL_API === "true") {
      return false;
    }

    // 実データ強制オーバーライド（URLクエリ）例: ?forceReal=1 / ?forceReal=true
    try {
      const params = new URLSearchParams(window.location.search);
      const forceReal = params.get("forceReal");
      if (forceReal && ["1", "true", "on", "yes"].includes(forceReal.toLowerCase())) {
        return false;
      }
    } catch (_) {}
    
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
