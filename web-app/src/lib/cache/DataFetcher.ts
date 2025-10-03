'use client';

import { cacheService } from './CacheService';

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
      version: '1.0'
    },
    listedData: {
      ttl: 7 * 24 * 60 * 60 * 1000, // 1週間
      version: '1.0'
    },
    sampleData: {
      ttl: 30 * 24 * 60 * 60 * 1000, // 1ヶ月
      version: '1.0'
    }
  };

  /**
   * 日足データの取得（キャッシュ付き）
   */
  static async getDailyQuotes(
    date?: string,
    forceRefresh: boolean = false
  ): Promise<StockData[]> {
    const cacheKey = `daily_quotes_${date || 'latest'}`;
    
    return cacheService.getOrFetch(
      cacheKey,
      async () => {
        try {
          // 実際のAPI呼び出し
          const response = await fetch('/api/jquants-proxy/prices/daily_quotes', {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
          });

          if (!response.ok) {
            throw new Error(`API呼び出し失敗: ${response.status}`);
          }

          const data = await response.json();
          return data.daily_quotes || [];
        } catch (error) {
          console.error('日足データ取得エラー:', error);
          // フォールバック: サンプルデータを使用
          return this.getSampleDailyQuotes();
        }
      },
      {
        ttl: this.CACHE_CONFIG.dailyQuotes.ttl,
        version: this.CACHE_CONFIG.dailyQuotes.version,
        forceRefresh
      }
    );
  }

  /**
   * 上場銘柄データの取得（キャッシュ付き）
   */
  static async getListedData(
    forceRefresh: boolean = false
  ): Promise<ListedData[]> {
    const cacheKey = 'listed_data';
    
    return cacheService.getOrFetch(
      cacheKey,
      async () => {
        try {
          // 実際のAPI呼び出し
          const response = await fetch('/api/jquants-proxy/prices/listed_info', {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
          });

          if (!response.ok) {
            throw new Error(`API呼び出し失敗: ${response.status}`);
          }

          const data = await response.json();
          return data.listed_info || [];
        } catch (error) {
          console.error('上場銘柄データ取得エラー:', error);
          // フォールバック: サンプルデータを使用
          return this.getSampleListedData();
        }
      },
      {
        ttl: this.CACHE_CONFIG.listedData.ttl,
        version: this.CACHE_CONFIG.listedData.version,
        forceRefresh
      }
    );
  }

  /**
   * サンプル日足データの取得
   */
  private static async getSampleDailyQuotes(): Promise<StockData[]> {
    try {
      const response = await fetch('/docs/data/sample_daily_quotes.json');
      if (response.ok) {
        const data = await response.json();
        return data.daily_quotes || [];
      }
    } catch (error) {
      console.error('サンプル日足データ取得エラー:', error);
    }

    // 最終フォールバック: ハードコードされたサンプルデータ
    return [
      {
        code: '7203',
        name: 'トヨタ自動車',
        price: 2500,
        change: 50,
        changePercent: 2.04,
        volume: 1000000,
        timestamp: new Date().toISOString()
      },
      {
        code: '6758',
        name: 'ソニーグループ',
        price: 12000,
        change: -100,
        changePercent: -0.83,
        volume: 500000,
        timestamp: new Date().toISOString()
      }
    ];
  }

  /**
   * サンプル上場銘柄データの取得
   */
  private static async getSampleListedData(): Promise<ListedData[]> {
    try {
      const response = await fetch('/docs/data/sample_listed_data.json');
      if (response.ok) {
        const data = await response.json();
        return data.listed_data || [];
      }
    } catch (error) {
      console.error('サンプル上場銘柄データ取得エラー:', error);
    }

    // 最終フォールバック: ハードコードされたサンプルデータ
    return [
      {
        code: '7203',
        name: 'トヨタ自動車',
        market: '東証プライム',
        sector: '自動車',
        listingDate: '1949-05-16'
      },
      {
        code: '6758',
        name: 'ソニーグループ',
        market: '東証プライム',
        sector: '電気機器',
        listingDate: '1958-12-23'
      }
    ];
  }

  /**
   * アプリ起動時の初期化
   */
  static async initialize(): Promise<void> {
    try {
      console.log('🚀 データキャッシュ初期化開始');
      
      // 期限切れデータのクリーンアップ
      const deletedCount = await cacheService.cleanup();
      console.log(`🧹 期限切れデータ削除: ${deletedCount}件`);

      // キャッシュサイズの確認
      const cacheSize = await cacheService.getSize();
      console.log(`📦 キャッシュサイズ: ${cacheSize}件`);

      // メトリクスの出力
      cacheService.logMetrics();

      console.log('✅ データキャッシュ初期化完了');
    } catch (error) {
      console.error('❌ データキャッシュ初期化エラー:', error);
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

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // クリーンアップ関数を返す
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }

  /**
   * 強制リフレッシュ（全キャッシュクリア）
   */
  static async forceRefresh(): Promise<void> {
    try {
      console.log('🔄 全キャッシュの強制リフレッシュ');
      await cacheService.clear();
      console.log('✅ 全キャッシュクリア完了');
    } catch (error) {
      console.error('❌ 強制リフレッシュエラー:', error);
    }
  }
}
