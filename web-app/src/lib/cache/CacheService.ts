"use client";

interface CacheItem<T> {
  data: T;
  timestamp: number;
  ttl: number;
  version: string;
}

interface CacheMetrics {
  hits: number;
  misses: number;
  total: number;
  hitRate: number;
}

interface CacheConfig {
  defaultTTL: number; // デフォルトTTL（ミリ秒）
  maxSize: number; // 最大キャッシュサイズ
  enableMetrics: boolean;
}

export class CacheService {
  private static instance: CacheService;
  private db: IDBDatabase | null = null;
  private metrics: CacheMetrics = {
    hits: 0,
    misses: 0,
    total: 0,
    hitRate: 0,
  };
  private config: CacheConfig = {
    defaultTTL: 24 * 60 * 60 * 1000, // 24時間
    maxSize: 100 * 1024 * 1024, // 100MB
    enableMetrics: true,
  };

  private constructor() {
    this.initDB();
  }

  static getInstance(): CacheService {
    if (!CacheService.instance) {
      CacheService.instance = new CacheService();
    }
    return CacheService.instance;
  }

  private async initDB(): Promise<void> {
    // サーバーサイドでは何もしない
    if (typeof window === "undefined" || typeof indexedDB === "undefined") {
      return Promise.resolve();
    }
    
    return new Promise((resolve, reject) => {
      const request = indexedDB.open("StockCacheDB", 1);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };
      
      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        
        // キャッシュストアの作成
        if (!db.objectStoreNames.contains("cache")) {
          const store = db.createObjectStore("cache", { keyPath: "key" });
          store.createIndex("timestamp", "timestamp", { unique: false });
          store.createIndex("ttl", "ttl", { unique: false });
        }
      };
    });
  }

  /**
   * データの取得またはフェッチ
   */
  async getOrFetch<T>(
    key: string,
    fetchFn: () => Promise<T>,
    options: {
      ttl?: number;
      version?: string;
      forceRefresh?: boolean;
    } = {},
  ): Promise<T> {
    const { ttl = this.config.defaultTTL, version = "1.0", forceRefresh = false } = options;

    try {
      // キャッシュから取得を試行
      if (!forceRefresh) {
        const cached = await this.get<T>(key);
        if (cached) {
          this.recordHit();
          return cached;
        }
      }

      // キャッシュミス - データをフェッチ
      this.recordMiss();
      const data = await fetchFn();
      
      // キャッシュに保存
      await this.set(key, data, ttl, version);
      
      return data;
    } catch (error) {
      console.error(`キャッシュ取得エラー (${key}):`, error);
      
      // エラー時は期限切れデータでも返す
      const expired = await this.get<T>(key, true);
      if (expired) {
        console.warn(`期限切れデータを使用: ${key}`);
        return expired;
      }
      
      throw error;
    }
  }

  /**
   * キャッシュからデータを取得
   */
  async get<T>(key: string, allowExpired: boolean = false): Promise<T | null> {
    // サーバーサイドでは常にnullを返す
    if (typeof window === "undefined" || typeof indexedDB === "undefined") {
      return Promise.resolve(null);
    }
    
    if (!this.db) {
      await this.initDB();
    }

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(["cache"], "readonly");
      const store = transaction.objectStore("cache");
      const request = store.get(key);

      request.onsuccess = () => {
        const result = request.result;
        if (!result) {
          resolve(null);
          return;
        }

        const now = Date.now();
        const isExpired = now > (result.timestamp + result.ttl);

        if (isExpired && !allowExpired) {
          // 期限切れデータは削除
          this.delete(key);
          resolve(null);
          return;
        }

        resolve(result.data);
      };

      request.onerror = () => reject(request.error);
    });
  }

  /**
   * キャッシュにデータを保存
   */
  async set<T>(
    key: string, 
    data: T, 
    ttl: number = this.config.defaultTTL, 
    version: string = "1.0",
  ): Promise<void> {
    // サーバーサイドでは何もしない
    if (typeof window === "undefined" || typeof indexedDB === "undefined") {
      return Promise.resolve();
    }
    
    if (!this.db) {
      await this.initDB();
    }

    const item: CacheItem<T> = {
      data,
      timestamp: Date.now(),
      ttl,
      version,
    };

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(["cache"], "readwrite");
      const store = transaction.objectStore("cache");
      const request = store.put({ key, ...item });

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * キャッシュからデータを削除
   */
  async delete(key: string): Promise<void> {
    if (!this.db) {
      await this.initDB();
    }

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(["cache"], "readwrite");
      const store = transaction.objectStore("cache");
      const request = store.delete(key);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * 期限切れデータのクリーンアップ
   */
  async cleanup(): Promise<number> {
    if (!this.db) {
      await this.initDB();
    }

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(["cache"], "readwrite");
      const store = transaction.objectStore("cache");
      const index = store.index("timestamp");
      const now = Date.now();
      let deletedCount = 0;

      const request = index.openCursor();
      request.onsuccess = (event) => {
        const cursor = (event.target as IDBRequest).result;
        if (cursor) {
          const item = cursor.value;
          if (now > (item.timestamp + item.ttl)) {
            cursor.delete();
            deletedCount++;
          }
          cursor.continue();
        } else {
          resolve(deletedCount);
        }
      };
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * キャッシュサイズの取得
   */
  async getSize(): Promise<number> {
    if (!this.db) {
      await this.initDB();
    }

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(["cache"], "readonly");
      const store = transaction.objectStore("cache");
      const request = store.count();

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * ヒット率の記録
   */
  private recordHit(): void {
    this.metrics.hits++;
    this.metrics.total++;
    this.updateHitRate();
  }

  private recordMiss(): void {
    this.metrics.misses++;
    this.metrics.total++;
    this.updateHitRate();
  }

  private updateHitRate(): void {
    this.metrics.hitRate = this.metrics.total > 0 
      ? (this.metrics.hits / this.metrics.total) * 100 
      : 0;
  }

  /**
   * メトリクスの取得
   */
  getMetrics(): CacheMetrics {
    return { ...this.metrics };
  }

  /**
   * メトリクスのリセット
   */
  resetMetrics(): void {
    this.metrics = {
      hits: 0,
      misses: 0,
      total: 0,
      hitRate: 0,
    };
  }

  /**
   * メトリクスの出力
   */
  logMetrics(): void {
    const metrics = this.getMetrics();
    console.log("📊 キャッシュメトリクス:");
    console.log(`  - ヒット率: ${metrics.hitRate.toFixed(2)}%`);
    console.log(`  - ヒット数: ${metrics.hits}`);
    console.log(`  - ミス数: ${metrics.misses}`);
    console.log(`  - 総リクエスト数: ${metrics.total}`);
  }

  /**
   * 全キャッシュのクリア
   */
  async clear(): Promise<void> {
    if (!this.db) {
      await this.initDB();
    }

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(["cache"], "readwrite");
      const store = transaction.objectStore("cache");
      const request = store.clear();

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }
}

// シングルトンインスタンスのエクスポート
export const cacheService = CacheService.getInstance();
