/**
 * 包括的なキャッシュ管理システム
 * 今日の指示・シグナル取得のエラー処理とフォールバック機能を提供
 */

interface CacheItem<T> {
  data: T;
  timestamp: string;
  version: string;
}

interface CacheOptions {
  ttlHours?: number;
  version?: string;
  fallbackData?: any;
}

class CacheManager {
  private static instance: CacheManager;
  private readonly CACHE_PREFIX = "jquants_cache_";
  private readonly DEFAULT_TTL_HOURS = 6;

  static getInstance(): CacheManager {
    if (!CacheManager.instance) {
      CacheManager.instance = new CacheManager();
    }
    return CacheManager.instance;
  }

  /**
   * データをキャッシュに保存
   */
  set<T>(key: string, data: T, options: CacheOptions = {}): void {
    try {
      const cacheItem: CacheItem<T> = {
        data,
        timestamp: new Date().toISOString(),
        version: options.version || "1.0",
      };
      
      localStorage.setItem(
        `${this.CACHE_PREFIX}${key}`,
        JSON.stringify(cacheItem),
      );
    } catch (error) {
      console.warn(`キャッシュ保存に失敗 (${key}):`, error);
    }
  }

  /**
   * キャッシュからデータを取得
   */
  get<T>(key: string, options: CacheOptions = {}): T | null {
    try {
      const cached = localStorage.getItem(`${this.CACHE_PREFIX}${key}`);
      if (!cached) return null;

      const cacheItem: CacheItem<T> = JSON.parse(cached);
      
      // TTLチェック
      const ttlHours = options.ttlHours || this.DEFAULT_TTL_HOURS;
      const cacheTime = new Date(cacheItem.timestamp);
      const now = new Date();
      const hoursDiff = (now.getTime() - cacheTime.getTime()) / (1000 * 60 * 60);
      
      if (hoursDiff > ttlHours) {
        this.remove(key);
        return null;
      }

      // バージョンチェック
      if (options.version && cacheItem.version !== options.version) {
        this.remove(key);
        return null;
      }

      return cacheItem.data;
    } catch (error) {
      console.warn(`キャッシュ読み込みに失敗 (${key}):`, error);
      return null;
    }
  }

  /**
   * キャッシュを削除
   */
  remove(key: string): void {
    try {
      localStorage.removeItem(`${this.CACHE_PREFIX}${key}`);
    } catch (error) {
      console.warn(`キャッシュ削除に失敗 (${key}):`, error);
    }
  }

  /**
   * キャッシュの有効性をチェック
   */
  isValid(key: string, ttlHours: number = this.DEFAULT_TTL_HOURS): boolean {
    try {
      const cached = localStorage.getItem(`${this.CACHE_PREFIX}${key}`);
      if (!cached) return false;

      const cacheItem: CacheItem<any> = JSON.parse(cached);
      const cacheTime = new Date(cacheItem.timestamp);
      const now = new Date();
      const hoursDiff = (now.getTime() - cacheTime.getTime()) / (1000 * 60 * 60);
      
      return hoursDiff <= ttlHours;
    } catch (error) {
      return false;
    }
  }

  /**
   * フォールバック付きデータ取得
   */
  async getWithFallback<T>(
    key: string,
    fetchFn: () => Promise<T>,
    options: CacheOptions = {},
  ): Promise<{ data: T; fromCache: boolean; error?: string }> {
    try {
      // まずキャッシュをチェック
      const cached = this.get<T>(key, options);
      if (cached) {
        return { data: cached, fromCache: true };
      }

      // キャッシュがない場合はAPIから取得
      const freshData = await fetchFn();
      this.set(key, freshData, options);
      return { data: freshData, fromCache: false };
    } catch (error) {
      console.error(`データ取得に失敗 (${key}):`, error);
      
      // エラー時はキャッシュを再確認
      const cached = this.get<T>(key);
      if (cached) {
        return { 
          data: cached, 
          fromCache: true, 
          error: "最新データの取得に失敗しました。前回の結果を表示しています。", 
        };
      }

      // キャッシュもない場合はフォールバックデータを使用
      if (options.fallbackData) {
        return { 
          data: options.fallbackData, 
          fromCache: true, 
          error: "データ取得に失敗しました。サンプルデータを表示しています。", 
        };
      }

      throw error;
    }
  }

  /**
   * 分析結果のキャッシュ管理
   */
  async getAnalysisResults(): Promise<{
    hasAnalysis: boolean;
    lastAnalysisTime?: string;
    analysisStatus?: "completed" | "failed" | "not_started";
  }> {
    const cacheKey = "analysis_status";
    const cached = this.get<{
      hasAnalysis: boolean;
      lastAnalysisTime?: string;
      analysisStatus?: "completed" | "failed" | "not_started";
    }>(cacheKey);

    if (cached) {
      return cached;
    }

    // APIルートが削除されているため、デフォルト値を返す
    const result = {
      hasAnalysis: false,
      analysisStatus: "not_started" as const,
    };
    this.set(cacheKey, result, { ttlHours: 1 }); // 1時間キャッシュ
    return result;
  }

  /**
   * 今日の指示のキャッシュ管理
   */
  async getTodayActions(): Promise<{
    data: any;
    fromCache: boolean;
    error?: string;
  }> {
    // APIルートが削除されているため、フォールバックデータを直接返す
    const fallbackData = {
      analysisRequired: true,
      analysisStatus: "not_started",
      error: {
        code: "API_UNAVAILABLE",
        message: "APIが利用できません。サンプルデータを表示しています。",
      },
    };
    
    return {
      data: fallbackData,
      fromCache: false,
      error: "APIが利用できません。サンプルデータを表示しています。",
    };
  }

  /**
   * シグナルのキャッシュ管理
   */
  async getSignals(): Promise<{
    data: any;
    fromCache: boolean;
    error?: string;
  }> {
    // APIルートが削除されているため、フォールバックデータを直接返す
    const fallbackData = {
      signals: [],
      analysisRequired: true,
      error: {
        code: "API_UNAVAILABLE",
        message: "APIが利用できません。サンプルデータを表示しています。",
      },
    };
    
    return {
      data: fallbackData,
      fromCache: false,
      error: "APIが利用できません。サンプルデータを表示しています。",
    };
  }

  /**
   * キャッシュをクリア
   */
  clearAll(): void {
    try {
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.startsWith(this.CACHE_PREFIX)) {
          localStorage.removeItem(key);
        }
      });
    } catch (error) {
      console.warn("キャッシュクリアに失敗:", error);
    }
  }

  /**
   * キャッシュ統計を取得
   */
  getStats(): {
    totalItems: number;
    totalSize: number;
    items: Array<{
      key: string;
      size: number;
      timestamp: string;
      isValid: boolean;
    }>;
  } {
    const items: Array<{
      key: string;
      size: number;
      timestamp: string;
      isValid: boolean;
    }> = [];

    let totalSize = 0;

    try {
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.startsWith(this.CACHE_PREFIX)) {
          const value = localStorage.getItem(key);
          if (value) {
            const size = new Blob([value]).size;
            totalSize += size;
            
            try {
              const cacheItem = JSON.parse(value);
              items.push({
                key: key.replace(this.CACHE_PREFIX, ""),
                size,
                timestamp: cacheItem.timestamp,
                isValid: this.isValid(key.replace(this.CACHE_PREFIX, "")),
              });
            } catch (e) {
              // 無効なキャッシュアイテム
            }
          }
        }
      });
    } catch (error) {
      console.warn("キャッシュ統計の取得に失敗:", error);
    }

    return {
      totalItems: items.length,
      totalSize,
      items,
    };
  }
}

export default CacheManager;
