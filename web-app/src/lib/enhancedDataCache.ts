/**
 * 強化されたデータキャッシュシステム
 * TTL設定、フォールバック機能、差分更新対応
 */

export interface CacheItem<T> {
  data: T;
  timestamp: number;
  ttl: number;
  version: string;
  source: "api" | "cache" | "fallback";
}

export interface StockData {
  code: string;
  name: string;
  last_price: number;
  change: number;
  change_percent: number;
  volume: number;
  updated_at: string;
  created_at?: string;
  changes?: string[];
}

export interface StockDataResponse {
  metadata: {
    last_updated: string;
    total_stocks: number;
    version: string;
    data_source: string;
  };
  stocks: Record<string, StockData>;
}

export class EnhancedDataCache {
  private static readonly CACHE_PREFIX = "jquants_enhanced_";
  private static readonly DEFAULT_TTL = 30 * 60 * 1000; // 30分
  private static readonly FALLBACK_TTL = 24 * 60 * 60 * 1000; // 24時間
  private static readonly VERSION = "2.0";

  /**
   * キャッシュからデータを取得
   */
  static async getStockData(symbol?: string): Promise<StockDataResponse | null> {
    const cacheKey = `${this.CACHE_PREFIX}stock_data${symbol ? `_${symbol}` : ""}`;
    
    try {
      const cached = localStorage.getItem(cacheKey);
      if (cached) {
        const cacheItem: CacheItem<StockDataResponse> = JSON.parse(cached);
        
        // TTLチェック
        if (this.isCacheValid(cacheItem)) {
          console.log(`キャッシュからデータ取得: ${symbol || "all"}`);
          return cacheItem.data;
        } else {
          console.log(`キャッシュが期限切れ: ${symbol || "all"}`);
          localStorage.removeItem(cacheKey);
        }
      }
    } catch (error) {
      console.warn("キャッシュ読み込みエラー:", error);
    }
    
    return null;
  }

  /**
   * サーバーからデータを取得
   */
  static async fetchFromServer(symbol?: string): Promise<StockDataResponse | null> {
    try {
      const url = symbol 
        ? `/data/stocks/${symbol}.json`
        : "/data/stock_data.json";
      
      console.log(`サーバーからデータ取得: ${url}`);
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data: StockDataResponse = await response.json();
      
      // キャッシュに保存
      await this.saveToCache(data, symbol);
      
      return data;
    } catch (error) {
      console.error("サーバーからのデータ取得エラー:", error);
      return null;
    }
  }

  /**
   * フォールバックデータを取得
   */
  static async getFallbackData(symbol?: string): Promise<StockDataResponse | null> {
    const cacheKey = `${this.CACHE_PREFIX}fallback${symbol ? `_${symbol}` : ""}`;
    
    try {
      const cached = localStorage.getItem(cacheKey);
      if (cached) {
        const cacheItem: CacheItem<StockDataResponse> = JSON.parse(cached);
        
        // フォールバックは長期間有効
        if (Date.now() - cacheItem.timestamp < this.FALLBACK_TTL) {
          console.log(`フォールバックデータを使用: ${symbol || "all"}`);
          return cacheItem.data;
        }
      }
    } catch (error) {
      console.warn("フォールバックデータ読み込みエラー:", error);
    }
    
    return null;
  }

  /**
   * データを取得（キャッシュ → サーバー → フォールバックの順）
   */
  static async getData(symbol?: string, forceRefresh: boolean = false): Promise<StockDataResponse | null> {
    // 1. キャッシュから取得（強制更新でない場合）
    if (!forceRefresh) {
      const cachedData = await this.getStockData(symbol);
      if (cachedData) {
        return cachedData;
      }
    }

    // 2. サーバーから取得
    const serverData = await this.fetchFromServer(symbol);
    if (serverData) {
      return serverData;
    }

    // 3. フォールバックデータを使用
    const fallbackData = await this.getFallbackData(symbol);
    if (fallbackData) {
      console.warn("フォールバックデータを使用しています");
      return fallbackData;
    }

    console.error("データを取得できませんでした");
    return null;
  }

  /**
   * キャッシュにデータを保存
   */
  static async saveToCache(data: StockDataResponse, symbol?: string): Promise<void> {
    const cacheKey = `${this.CACHE_PREFIX}stock_data${symbol ? `_${symbol}` : ""}`;
    const fallbackKey = `${this.CACHE_PREFIX}fallback${symbol ? `_${symbol}` : ""}`;
    
    const cacheItem: CacheItem<StockDataResponse> = {
      data,
      timestamp: Date.now(),
      ttl: this.DEFAULT_TTL,
      version: this.VERSION,
      source: "api",
    };

    try {
      // 通常のキャッシュに保存
      localStorage.setItem(cacheKey, JSON.stringify(cacheItem));
      
      // フォールバック用にも保存
      const fallbackItem: CacheItem<StockDataResponse> = {
        ...cacheItem,
        source: "fallback",
      };
      localStorage.setItem(fallbackKey, JSON.stringify(fallbackItem));
      
      console.log(`データをキャッシュに保存: ${symbol || "all"}`);
    } catch (error) {
      console.error("キャッシュ保存エラー:", error);
    }
  }

  /**
   * キャッシュの有効性をチェック
   */
  private static isCacheValid(cacheItem: CacheItem<any>): boolean {
    const now = Date.now();
    const age = now - cacheItem.timestamp;
    return age < cacheItem.ttl;
  }

  /**
   * キャッシュをクリア
   */
  static clearCache(symbol?: string): void {
    const keys = [
      `${this.CACHE_PREFIX}stock_data${symbol ? `_${symbol}` : ""}`,
      `${this.CACHE_PREFIX}fallback${symbol ? `_${symbol}` : ""}`,
    ];
    
    keys.forEach(key => {
      localStorage.removeItem(key);
    });
    
    console.log(`キャッシュをクリア: ${symbol || "all"}`);
  }

  /**
   * キャッシュ統計を取得
   */
  static getCacheStats(): {
    totalItems: number;
    validItems: number;
    expiredItems: number;
    totalSize: number;
  } {
    let totalItems = 0;
    let validItems = 0;
    let expiredItems = 0;
    let totalSize = 0;

    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(this.CACHE_PREFIX)) {
        totalItems++;
        
        try {
          const item = JSON.parse(localStorage.getItem(key) || "{}");
          totalSize += JSON.stringify(item).length;
          
          if (this.isCacheValid(item)) {
            validItems++;
          } else {
            expiredItems++;
          }
        } catch (error) {
          console.warn(`キャッシュアイテムの解析エラー: ${key}`);
        }
      }
    }

    return {
      totalItems,
      validItems,
      expiredItems,
      totalSize,
    };
  }

  /**
   * 期限切れキャッシュをクリーンアップ
   */
  static cleanupExpiredCache(): void {
    const keysToRemove: string[] = [];

    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(this.CACHE_PREFIX)) {
        try {
          const item = JSON.parse(localStorage.getItem(key) || "{}");
          if (!this.isCacheValid(item)) {
            keysToRemove.push(key);
          }
        } catch (error) {
          // 解析できないアイテムは削除
          keysToRemove.push(key);
        }
      }
    }

    keysToRemove.forEach(key => {
      localStorage.removeItem(key);
    });

    console.log(`期限切れキャッシュをクリーンアップ: ${keysToRemove.length}件`);
  }
}
