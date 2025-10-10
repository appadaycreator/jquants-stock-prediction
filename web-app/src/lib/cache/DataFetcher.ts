"use client";

import { cacheService } from "./CacheService";
import { sampleDataProvider } from "../providers/SampleDataProvider";
import { SampleDataValidator } from "../validators/sample-data-validator";

export interface StockData {
  code: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  timestamp: string;
}

export interface ListedData {
  code: string;
  name: string;
  market: string;
  sector: string;
  listingDate: string;
}

export interface CacheConfig {
  dailyQuotes: {
    ttl: number; // 1日
    version: string;
  };
  listedData: {
    ttl: number; // 1週間
    version: string;
  };
  sampleData: {
    ttl: number; // 1ヶ月
    version: string;
  };
}

export class DataFetcher {
  private static readonly CACHE_CONFIG: CacheConfig = {
    dailyQuotes: {
      ttl: 24 * 60 * 60 * 1000, // 1日
      version: "1.0",
    },
    listedData: {
      ttl: 7 * 24 * 60 * 60 * 1000, // 1週間
      version: "1.0",
    },
    sampleData: {
      ttl: 30 * 24 * 60 * 60 * 1000, // 1ヶ月
      version: "1.0",
    },
  };

  private static readonly MAX_RETRIES = 3;
  private static readonly RETRY_DELAY = 1000; // 1秒

  /**
   * リトライ機能付きAPI呼び出し
   */
  private static async fetchWithRetry(
    url: string,
    options: RequestInit = {},
    retries: number = this.MAX_RETRIES,
  ): Promise<Response> {
    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const response = await fetch(url, options);
        
        // 成功時は即座に返す
        if (response.ok) {
          return response;
        }

        // 401エラーの場合は認証エラーとして扱い、リトライしない
        if (response.status === 401) {
          console.error(`認証エラー (401): ${url}`);
          throw new Error(`認証エラー: ${response.status}`);
        }

        // その他のエラーはリトライ
        if (attempt < retries) {
          console.warn(`API呼び出し失敗 (${response.status}): ${url}, リトライ ${attempt}/${retries}`);
          await this.delay(this.RETRY_DELAY * attempt);
        } else {
          throw new Error(`API呼び出し失敗: ${response.status}`);
        }
      } catch (error: unknown) {
        if (attempt === retries) {
          throw (error instanceof Error) ? error : new Error(String(error));
        }
        console.warn(`API呼び出しエラー: ${url}, リトライ ${attempt}/${retries}`, error instanceof Error ? error.message : String(error));
        await this.delay(this.RETRY_DELAY * attempt);
      }
    }
    
    throw new Error("最大リトライ回数に達しました");
  }

  /**
   * 遅延処理
   */
  private static delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * 日足データの取得（キャッシュ付き）
   */
  static async getDailyQuotes(
    date?: string,
    forceRefresh: boolean = false,
  ): Promise<StockData[]> {
    const cacheKey = `daily_quotes_${date || "latest"}`;
    
    return cacheService.getOrFetch(
      cacheKey,
      async () => {
        try {
          // リトライ機能付きAPI呼び出し
          const response = await this.fetchWithRetry("/api/jquants-proxy/prices/daily_quotes", {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
            },
          });

          const data = await response.json();
          return data.daily_quotes || [];
        } catch (error) {
          console.error("日足データ取得エラー:", error);
          // フォールバック: サンプルデータを使用
          return this.getSampleDailyQuotes();
        }
      },
      {
        ttl: this.CACHE_CONFIG.dailyQuotes.ttl,
        version: this.CACHE_CONFIG.dailyQuotes.version,
        forceRefresh,
      },
    );
  }

  /**
   * 上場銘柄データの取得（キャッシュ付き）
   */
  static async getListedData(
    forceRefresh: boolean = false,
  ): Promise<ListedData[]> {
    const cacheKey = "listed_data";
    
    return cacheService.getOrFetch(
      cacheKey,
      async () => {
        try {
          // リトライ機能付きAPI呼び出し
          const response = await this.fetchWithRetry("/api/jquants-proxy/prices/listed_info", {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
            },
          });

          if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(`API Error ${response.status}: ${errorData.message || response.statusText}`);
          }

          const data = await response.json();
          
          // データの妥当性チェック
          if (!data || typeof data !== "object") {
            throw new Error("Invalid response format: expected object");
          }
          
          return data.listed_info || [];
        } catch (error: unknown) {
          console.error("上場銘柄データ取得エラー:", {
            error: error instanceof Error ? error.message : String(error),
            stack: error instanceof Error ? error.stack : undefined,
            timestamp: new Date().toISOString(),
          });
          // フォールバック: サンプルデータを使用
          return this.getSampleListedData();
        }
      },
      {
        ttl: this.CACHE_CONFIG.listedData.ttl,
        version: this.CACHE_CONFIG.listedData.version,
        forceRefresh,
      },
    );
  }

  /**
   * サンプル日足データの取得
   */
  private static async getSampleDailyQuotes(): Promise<StockData[]> {
    try {
      const sampleData = await sampleDataProvider.getDailyQuotes();
      
      // バリデーション実行
      const validation = SampleDataValidator.validateDailyQuotes(sampleData);
      if (!validation.isValid) {
        console.warn("サンプル日足データのバリデーションエラー:", validation.errors);
      }

      // データ変換
      return sampleData.daily_quotes.map(quote => ({
        code: quote.code,
        name: quote.name,
        price: quote.close,
        change: quote.close - quote.open,
        changePercent: quote.change_percent,
        volume: quote.volume,
        timestamp: quote.timestamp,
      }));
    } catch (error: unknown) {
      console.error("サンプル日足データ取得エラー:", error instanceof Error ? error.message : String(error));
      
      // 最終フォールバック: ハードコードされたサンプルデータ
      return [
        {
          code: "7203",
          name: "トヨタ自動車",
          price: 2500,
          change: 50,
          changePercent: 2.04,
          volume: 1000000,
          timestamp: new Date().toISOString(),
        },
        {
          code: "6758",
          name: "ソニーグループ",
          price: 12000,
          change: -100,
          changePercent: -0.83,
          volume: 500000,
          timestamp: new Date().toISOString(),
        },
      ];
    }
  }

  /**
   * サンプル上場銘柄データの取得
   */
  private static async getSampleListedData(): Promise<ListedData[]> {
    try {
      const sampleData = await sampleDataProvider.getListedData();
      
      // バリデーション実行
      const validation = SampleDataValidator.validateListedData(sampleData);
      if (!validation.isValid) {
        console.warn("サンプル上場銘柄データのバリデーションエラー:", validation.errors);
      }

      // データ変換
      return sampleData.listed_data.map(stock => ({
        code: stock.code,
        name: stock.name,
        market: stock.market,
        sector: stock.sector17_name,
        listingDate: stock.listing_date,
      }));
    } catch (error: unknown) {
      console.error("サンプル上場銘柄データ取得エラー:", error instanceof Error ? error.message : String(error));
      
      // 最終フォールバック: ハードコードされたサンプルデータ
      return [
        {
          code: "7203",
          name: "トヨタ自動車",
          market: "東証プライム",
          sector: "自動車",
          listingDate: "1949-05-16",
        },
        {
          code: "6758",
          name: "ソニーグループ",
          market: "東証プライム",
          sector: "電気機器",
          listingDate: "1958-12-23",
        },
      ];
    }
  }

  /**
   * アプリ起動時の初期化
   */
  static async initialize(): Promise<void> {
    try {
      if (process.env.NODE_ENV === 'development') {
        console.log("🚀 データキャッシュ初期化開始");
      }
      
      // 期限切れデータのクリーンアップ
      const deletedCount = await cacheService.cleanup();
      if (process.env.NODE_ENV === 'development' && deletedCount > 0) {
        console.log(`🧹 期限切れデータ削除: ${deletedCount}件`);
      }

      // キャッシュサイズの確認
      const cacheSize = await cacheService.getSize();
      if (process.env.NODE_ENV === 'development') {
        console.log(`📦 キャッシュサイズ: ${cacheSize}件`);
      }

      // メトリクスの出力
      cacheService.logMetrics();

      if (process.env.NODE_ENV === 'development') {
        console.log("✅ データキャッシュ初期化完了");
      }
    } catch (error: unknown) {
      console.error("❌ データキャッシュ初期化エラー:", error instanceof Error ? error.message : String(error));
    }
  }

  /**
   * オフライン状態の確認
   */
  static isOffline(): boolean {
    return !navigator.onLine;
  }

  /**
   * ネットワーク状態の監視
   */
  static onNetworkChange(callback: (isOnline: boolean) => void): () => void {
    const handleOnline = () => callback(true);
    const handleOffline = () => callback(false);

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    // クリーンアップ関数を返す
    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }

  /**
   * 強制リフレッシュ（全キャッシュクリア）
   */
  static async forceRefresh(): Promise<void> {
    try {
      console.log("🔄 全キャッシュの強制リフレッシュ");
      await cacheService.clear();
      console.log("✅ 全キャッシュクリア完了");
    } catch (error) {
      console.error("❌ 強制リフレッシュエラー:", error);
    }
  }
}
