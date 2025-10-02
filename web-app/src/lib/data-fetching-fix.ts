/**
 * データ取得システムの修正版
 * 404エラー解消とリアルタイムデータ取得の実装
 */

import FixedJQuantsAdapter from './fixed-jquants-adapter';
import { StockData } from './fixed-jquants-adapter';

interface DataFetchingConfig {
  enableCache: boolean;
  cacheTimeout: number;
  maxRetries: number;
  retryDelay: number;
  enableFallback: boolean;
}

interface DataFetchingResult<T> {
  data: T;
  fromCache: boolean;
  timestamp: number;
  source: 'api' | 'cache' | 'fallback';
  error?: string;
}

class DataFetchingFix {
  private adapter: FixedJQuantsAdapter;
  private config: DataFetchingConfig;
  private isInitialized: boolean = false;

  constructor(config: Partial<DataFetchingConfig> = {}) {
    this.config = {
      enableCache: true,
      cacheTimeout: 60 * 60 * 1000, // 1時間
      maxRetries: 3,
      retryDelay: 1000,
      enableFallback: true,
      ...config,
    };
    
    this.adapter = new FixedJQuantsAdapter();
  }

  /**
   * 初期化
   */
  async initialize(): Promise<{ success: boolean; message: string }> {
    try {
      console.info("データ取得システム初期化開始");
      
      const result = await this.adapter.initialize();
      
      if (result.success) {
        this.isInitialized = true;
        console.info("データ取得システム初期化完了");
      }
      
      return result;
    } catch (error) {
      console.error("データ取得システム初期化エラー:", error);
      return {
        success: false,
        message: `初期化に失敗しました: ${error instanceof Error ? error.message : "不明なエラー"}`
      };
    }
  }

  /**
   * 株価データの取得（修正版）
   */
  async getStockData(
    symbol: string,
    startDate: string,
    endDate: string,
    options: {
      useCache?: boolean;
      enableFallback?: boolean;
      forceRefresh?: boolean;
    } = {}
  ): Promise<DataFetchingResult<StockData[]>> {
    const useCache = options.useCache !== false;
    const enableFallback = options.enableFallback !== false;
    const forceRefresh = options.forceRefresh === true;

    try {
      console.info("株価データ取得開始", { symbol, startDate, endDate, useCache, forceRefresh });

      if (!this.isInitialized) {
        const initResult = await this.initialize();
        if (!initResult.success) {
          throw new Error(initResult.message);
        }
      }

      // 強制リフレッシュの場合はキャッシュをスキップ
      if (forceRefresh) {
        console.info("強制リフレッシュ: キャッシュをスキップ");
        return await this.fetchFromAPI(symbol, startDate, endDate);
      }

      // キャッシュから取得を試行
      if (useCache) {
        const cachedResult = await this.getCachedData(symbol, startDate, endDate);
        if (cachedResult.data.length > 0) {
          console.info("キャッシュからデータ取得", { 
            symbol, 
            count: cachedResult.data.length,
            age: Date.now() - cachedResult.timestamp,
          });
          return cachedResult;
        }
      }

      // APIから取得
      const apiResult = await this.fetchFromAPI(symbol, startDate, endDate);
      
      // キャッシュに保存
      if (useCache && apiResult.data.length > 0) {
        await this.saveToCache(symbol, apiResult.data, startDate, endDate);
      }

      return apiResult;
    } catch (error) {
      console.error("株価データ取得エラー:", error);
      
      // フォールバック処理
      if (enableFallback) {
        const fallbackResult = await this.handleFallback(symbol, startDate, endDate);
        if (fallbackResult.data.length > 0) {
          console.warn("フォールバック: 代替データを取得", { 
            symbol, 
            count: fallbackResult.data.length,
          });
          return fallbackResult;
        }
      }
      
      throw error;
    }
  }

  /**
   * APIからデータ取得
   */
  private async fetchFromAPI(
    symbol: string,
    startDate: string,
    endDate: string
  ): Promise<DataFetchingResult<StockData[]>> {
    try {
      const data = await this.adapter.getStockData(symbol, startDate, endDate, false);
      
      return {
        data,
        fromCache: false,
        timestamp: Date.now(),
        source: 'api',
      };
    } catch (error) {
      console.error("API取得エラー:", error);
      throw error;
    }
  }

  /**
   * キャッシュからデータ取得
   */
  private async getCachedData(
    symbol: string,
    startDate: string,
    endDate: string
  ): Promise<DataFetchingResult<StockData[]>> {
    try {
      const cacheKey = `stock_${symbol}_${startDate}_${endDate}`;
      const cached = localStorage.getItem(cacheKey);
      
      if (cached) {
        const { data, timestamp } = JSON.parse(cached);
        const now = Date.now();
        const cacheAge = now - timestamp;
        
        if (cacheAge < this.config.cacheTimeout) {
          return {
            data,
            fromCache: true,
            timestamp,
            source: 'cache',
          };
        }
      }
      
      return {
        data: [],
        fromCache: false,
        timestamp: 0,
        source: 'cache',
      };
    } catch (error) {
      console.error("キャッシュ取得エラー:", error);
      return {
        data: [],
        fromCache: false,
        timestamp: 0,
        source: 'cache',
      };
    }
  }

  /**
   * キャッシュにデータ保存
   */
  private async saveToCache(
    symbol: string,
    data: StockData[],
    startDate: string,
    endDate: string
  ): Promise<void> {
    try {
      const cacheKey = `stock_${symbol}_${startDate}_${endDate}`;
      const cacheData = {
        data,
        timestamp: Date.now(),
        symbol,
        startDate,
        endDate,
      };
      
      localStorage.setItem(cacheKey, JSON.stringify(cacheData));
      console.info("キャッシュに保存完了", { symbol, count: data.length });
    } catch (error) {
      console.error("キャッシュ保存エラー:", error);
    }
  }

  /**
   * フォールバック処理
   */
  private async handleFallback(
    symbol: string,
    startDate: string,
    endDate: string
  ): Promise<DataFetchingResult<StockData[]>> {
    try {
      // 古いキャッシュを探す
      const cacheKey = `stock_${symbol}_${startDate}_${endDate}`;
      const cached = localStorage.getItem(cacheKey);
      
      if (cached) {
        const { data, timestamp } = JSON.parse(cached);
        return {
          data,
          fromCache: true,
          timestamp,
          source: 'fallback',
          error: '最新データの取得に失敗しました。前回の結果を表示しています。',
        };
      }
      
      // サンプルデータを生成
      const sampleData = this.generateSampleData(symbol, startDate, endDate);
      return {
        data: sampleData,
        fromCache: false,
        timestamp: Date.now(),
        source: 'fallback',
        error: 'データ取得に失敗しました。サンプルデータを表示しています。',
      };
    } catch (error) {
      console.error("フォールバック処理エラー:", error);
      return {
        data: [],
        fromCache: false,
        timestamp: 0,
        source: 'fallback',
        error: 'データ取得に失敗しました。',
      };
    }
  }

  /**
   * サンプルデータの生成
   */
  private generateSampleData(symbol: string, startDate: string, endDate: string): StockData[] {
    const data: StockData[] = [];
    const start = new Date(startDate);
    const end = new Date(endDate);
    const days = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
    
    let currentPrice = 1000 + Math.random() * 500;
    
    for (let i = 0; i < days; i++) {
      const date = new Date(start);
      date.setDate(date.getDate() + i);
      
      const change = (Math.random() - 0.5) * 50;
      currentPrice = Math.max(currentPrice + change, 100);
      
      const open = currentPrice + (Math.random() - 0.5) * 20;
      const high = Math.max(open, currentPrice) + Math.random() * 10;
      const low = Math.min(open, currentPrice) - Math.random() * 10;
      const close = currentPrice;
      const volume = Math.floor(Math.random() * 1000000) + 100000;
      
      data.push({
        date: date.toISOString().split('T')[0],
        code: symbol,
        open: Math.round(open * 100) / 100,
        high: Math.round(high * 100) / 100,
        low: Math.round(low * 100) / 100,
        close: Math.round(close * 100) / 100,
        volume,
      });
    }
    
    return data;
  }

  /**
   * 接続テスト
   */
  async testConnection(): Promise<{ success: boolean; message: string }> {
    try {
      if (!this.isInitialized) {
        const initResult = await this.initialize();
        if (!initResult.success) {
          return initResult;
        }
      }
      
      return await this.adapter.testConnection();
    } catch (error) {
      console.error("接続テストエラー:", error);
      return {
        success: false,
        message: `接続テストに失敗しました: ${error instanceof Error ? error.message : "不明なエラー"}`
      };
    }
  }

  /**
   * システムヘルスチェック
   */
  getSystemHealth(): { status: string; issues: string[]; isInitialized: boolean } {
    const health = this.adapter.getSystemHealth();
    
    return {
      status: health.status,
      issues: health.issues,
      isInitialized: this.isInitialized,
    };
  }

  /**
   * キャッシュクリア
   */
  clearCache(): void {
    try {
      const keys = Object.keys(localStorage);
      const stockKeys = keys.filter(key => key.startsWith('stock_'));
      
      stockKeys.forEach(key => {
        localStorage.removeItem(key);
      });
      
      console.info("キャッシュクリア完了", { clearedKeys: stockKeys.length });
    } catch (error) {
      console.error("キャッシュクリアエラー:", error);
    }
  }
}

export default DataFetchingFix;
export type { DataFetchingConfig, DataFetchingResult };
