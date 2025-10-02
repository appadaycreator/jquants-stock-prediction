/**
 * J-Quants APIクライアントファクトリー
 * 環境変数から設定を読み込み、シングルトンインスタンスを提供
 */

import JQuantsAdapter, { type JQuantsConfig } from "./jquants-adapter";

class JQuantsClientFactory {
  private static instance: JQuantsAdapter | null = null;

  /**
   * 静的データから取得するヘルパー（APIルートの代わり）
   */
  private static async callServer<T>(action: string, payload: Record<string, unknown> = {}): Promise<T> {
    if (typeof window === "undefined") {
      throw new Error("callServer should only be used in browser context");
    }

    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => controller.abort(), 30_000);

    try {
      // 静的データファイルから取得
      let dataUrl: string;
      
      switch (action) {
        case "getAllSymbols":
        case "getMarketInfo":
          dataUrl = "/data/listed_index.json";
          break;
        case "getStockPrices":
          // 価格データは個別ファイルから取得する必要がある
          return {
            data: [],
            message: "価格データは個別銘柄ファイルから取得してください",
          } as T;
        default:
          dataUrl = "/data/listed_index.json";
      }

      const response = await fetch(dataUrl, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json() as T;
    } finally {
      window.clearTimeout(timeoutId);
    }
  }

  /**
   * JQuantsアダプターのシングルトンインスタンスを取得
   */
  static getInstance(): JQuantsAdapter {
    if (typeof window === "undefined") {
      // サーバーサイドでは新しいインスタンスを都度作成
      return this.createInstance();
    }
    
    if (!this.instance) {
      this.instance = this.createInstance();
    }
    return this.instance;
  }

  /**
   * 新しいインスタンスを作成
   */
  private static createInstance(): JQuantsAdapter {
    // ブラウザサイドとサーバーサイドの環境変数を適切に処理
    const getEnvVar = (name: string): string | undefined => {
      if (typeof window === "undefined") {
        // サーバーサイド
        return process.env[name] || process.env[`NEXT_PUBLIC_${name}`];
      } else {
        // クライアントサイド - NEXT_PUBLIC_ プリフィックス付きのみアクセス可能
        return process.env[`NEXT_PUBLIC_${name}`];
      }
    };

    // デバッグ: 環境変数の状態を確認
    if (typeof window !== "undefined") {
      console.log("🔍 Client-side env debug:", {
        isClient: true,
        NODE_ENV: process.env.NODE_ENV,
        allEnvKeys: Object.keys(process.env),
        jquantsVars: {
          email: process.env.NEXT_PUBLIC_JQUANTS_EMAIL,
          password: process.env.NEXT_PUBLIC_JQUANTS_PASSWORD ? "***" : undefined,
          token: process.env.NEXT_PUBLIC_JQUANTS_ID_TOKEN ? "***" : undefined,
          baseUrl: process.env.NEXT_PUBLIC_JQUANTS_BASE_URL,
          timeout: process.env.NEXT_PUBLIC_JQUANTS_TIMEOUT,
        },
      });
    }

    const config: JQuantsConfig = {
      email: getEnvVar("JQUANTS_EMAIL"),
      password: getEnvVar("JQUANTS_PASSWORD"),
      token: getEnvVar("JQUANTS_ID_TOKEN"),
      baseUrl: getEnvVar("JQUANTS_BASE_URL") || "https://api.jquants.com/v1",
      timeout: parseInt(getEnvVar("JQUANTS_TIMEOUT") || "30000"),
    };

    return new JQuantsAdapter(config);
  }

  /**
   * インスタンスをリセット（テスト用）
   */
  static reset(): void {
    this.instance = null;
  }

  /**
   * 接続テストを実行
   */
  static async testConnection(): Promise<{ success: boolean; message: string }> {
    if (typeof window !== "undefined") {
      try {
        return await this.callServer<{ success: boolean; message: string }>("testConnection");
      } catch (error) {
        console.error("クライアント側接続テストエラー:", error);
        return {
          success: false,
          message: error instanceof Error ? error.message : "接続テストに失敗しました",
        };
      }
    }

    try {
      const client = this.getInstance();
      return await client.testConnection();
    } catch (error) {
      return {
        success: false,
        message: `接続テスト失敗: ${error instanceof Error ? error.message : "不明なエラー"}`,
      };
    }
  }

  /**
   * 全銘柄一覧を取得
   */
  static async getAllSymbols(): Promise<Array<{ code: string; name: string; sector?: string }>> {
    if (typeof window !== "undefined") {
      try {
        return await this.callServer<Array<{ code: string; name: string; sector?: string }>>("getAllSymbols");
      } catch (error) {
        console.error("クライアント側全銘柄一覧取得エラー:", error);
        return [];
      }
    }

    try {
      const client = this.getInstance();
      return await client.getAllSymbols();
    } catch (error) {
      console.error("全銘柄一覧取得エラー:", error);
      return [];
    }
  }

  /**
   * 株価データを取得
   */
  static async getStockData(
    symbol: string,
    startDate: string,
    endDate: string,
    useCache: boolean = true,
  ): Promise<import("./jquants-adapter").StockData[]> {
    if (typeof window !== "undefined") {
      try {
        return await this.callServer<import("./jquants-adapter").StockData[]>("getStockData", {
          symbol,
          startDate,
          endDate,
          useCache,
        });
      } catch (error) {
        console.error("クライアント側株価データ取得エラー:", error);
        return [];
      }
    }

    try {
      const client = this.getInstance();
      return await client.getStockData(symbol, startDate, endDate, useCache);
    } catch (error) {
      console.error("株価データ取得エラー:", error);
      return [];
    }
  }

  /**
   * 差分更新データを取得
   */
  static async getIncrementalData(symbol: string): Promise<import("./jquants-adapter").StockData[]> {
    if (typeof window !== "undefined") {
      try {
        return await this.callServer<import("./jquants-adapter").StockData[]>("getIncrementalData", { symbol });
      } catch (error) {
        console.error("クライアント側差分更新エラー:", error);
        return [];
      }
    }

    try {
      const client = this.getInstance();
      return await client.getIncrementalData(symbol);
    } catch (error) {
      console.error("差分更新エラー:", error);
      return [];
    }
  }

  /**
   * キャッシュをクリア
   */
  static async clearCache(symbol?: string): Promise<void> {
    if (typeof window !== "undefined") {
      try {
        await this.callServer<{ success: boolean }>("clearCache", { symbol });
        return;
      } catch (error) {
        console.error("クライアント側キャッシュクリアエラー:", error);
        return;
      }
    }

    try {
      const client = this.getInstance();
      await client.clearCache(symbol);
    } catch (error) {
      console.error("キャッシュクリアエラー:", error);
    }
  }

  /**
   * キャッシュ統計情報を取得
   */
  static async getCacheStats(): Promise<{ totalRecords: number; symbols: string[]; lastUpdated: string }> {
    if (typeof window !== "undefined") {
      try {
        return await this.callServer<{ totalRecords: number; symbols: string[]; lastUpdated: string }>("getCacheStats");
      } catch (error) {
        console.error("クライアント側キャッシュ統計取得エラー:", error);
        return { totalRecords: 0, symbols: [], lastUpdated: "" };
      }
    }

    try {
      const client = this.getInstance();
      return await client.getCacheStats();
    } catch (error) {
      console.error("キャッシュ統計取得エラー:", error);
      return { totalRecords: 0, symbols: [], lastUpdated: "" };
    }
  }
}

// デフォルトエクスポート
export default JQuantsClientFactory;

// 便利な関数を安全にエクスポート
export const testConnection = (...args: Parameters<typeof JQuantsClientFactory.testConnection>) => 
  JQuantsClientFactory.testConnection(...args);
export const getAllSymbols = (...args: Parameters<typeof JQuantsClientFactory.getAllSymbols>) => 
  JQuantsClientFactory.getAllSymbols(...args);
export const getStockData = (...args: Parameters<typeof JQuantsClientFactory.getStockData>) => 
  JQuantsClientFactory.getStockData(...args);
export const getIncrementalData = (...args: Parameters<typeof JQuantsClientFactory.getIncrementalData>) => 
  JQuantsClientFactory.getIncrementalData(...args);
export const clearCache = (...args: Parameters<typeof JQuantsClientFactory.clearCache>) => 
  JQuantsClientFactory.clearCache(...args);
export const getCacheStats = (...args: Parameters<typeof JQuantsClientFactory.getCacheStats>) => 
  JQuantsClientFactory.getCacheStats(...args);
