/**
 * 予測結果とモデル比較結果のキャッシュ管理システム
 * IndexedDBを使用した高性能キャッシュシステム
 */

interface CacheEntry<T> {
  key: string;
  data: T;
  metadata: {
    createdAt: string;
    lastAccessed: string;
    accessCount: number;
    size: number;
    ttl: number;
    tags: string[];
    version: string;
  };
}

export interface PredictionCacheData {
  predictions: any[];
  modelComparison: any[];
  performance: {
    mae: number;
    rmse: number;
    r2: number;
  };
  timestamp: string;
  modelName: string;
  parameters: Record<string, any>;
}

export interface ModelComparisonCacheData {
  models: Array<{
    name: string;
    mae: number;
    rmse: number;
    r2: number;
    type: string;
  }>;
  bestModel: string;
  comparisonTimestamp: string;
  parameters: Record<string, any>;
}

export class PredictionCacheManager {
  private db: IDBDatabase | null = null;
  private readonly DB_NAME = "PredictionCacheDB";
  private readonly VERSION = 1;
  private readonly PREDICTION_STORE = "predictions";
  private readonly COMPARISON_STORE = "modelComparisons";
  private readonly METADATA_STORE = "metadata";

  private config = {
    maxCacheSize: 50 * 1024 * 1024, // 50MB
    defaultTTL: 24 * 60 * 60 * 1000, // 24時間
    compressionEnabled: true,
    version: "2.0",
  };

  private stats = {
    hits: 0,
    misses: 0,
    sets: 0,
    deletes: 0,
    compressions: 0,
  };

  /**
   * データベースの初期化
   */
  async initialize(): Promise<boolean> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.DB_NAME, this.VERSION);

      request.onerror = () => {
        console.error("キャッシュデータベースの初期化に失敗:", request.error);
        reject(request.error);
      };

      request.onsuccess = () => {
        this.db = request.result;
        console.log("✅ 予測キャッシュシステム初期化完了");
        resolve(true);
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        // 予測結果ストア
        if (!db.objectStoreNames.contains(this.PREDICTION_STORE)) {
          const predictionStore = db.createObjectStore(this.PREDICTION_STORE, { keyPath: "key" });
          predictionStore.createIndex("timestamp", "metadata.createdAt", { unique: false });
          predictionStore.createIndex("modelName", "data.modelName", { unique: false });
          predictionStore.createIndex("tags", "metadata.tags", { unique: false, multiEntry: true });
        }

        // モデル比較ストア
        if (!db.objectStoreNames.contains(this.COMPARISON_STORE)) {
          const comparisonStore = db.createObjectStore(this.COMPARISON_STORE, { keyPath: "key" });
          comparisonStore.createIndex("timestamp", "metadata.createdAt", { unique: false });
          comparisonStore.createIndex("bestModel", "data.bestModel", { unique: false });
        }

        // メタデータストア
        if (!db.objectStoreNames.contains(this.METADATA_STORE)) {
          db.createObjectStore(this.METADATA_STORE, { keyPath: "key" });
        }
      };
    });
  }

  /**
   * 予測結果のキャッシュ保存
   */
  async cachePrediction(
    key: string,
    data: PredictionCacheData,
    options: {
      ttl?: number;
      tags?: string[];
      priority?: number;
    } = {},
  ): Promise<void> {
    if (!this.db) {
      console.warn("データベースが初期化されていません");
      return;
    }

    try {
      const startTime = performance.now();
      const size = this.calculateSize(data);
      const shouldCompress = options.priority !== 1 && this.config.compressionEnabled && size > 1024;

      let processedData = data;
      if (shouldCompress) {
        processedData = await this.compress(data);
        this.stats.compressions++;
      }

      const entry: CacheEntry<PredictionCacheData> = {
        key,
        data: processedData,
        metadata: {
          createdAt: new Date().toISOString(),
          lastAccessed: new Date().toISOString(),
          accessCount: 0,
          size: shouldCompress ? this.calculateSize(processedData) : size,
          ttl: options.ttl || this.config.defaultTTL,
          tags: options.tags || ["prediction"],
          version: this.config.version,
        },
      };

      // 容量チェック
      await this.ensureCapacity(entry.metadata.size);

      await this.saveEntry(entry, this.PREDICTION_STORE);
      this.stats.sets++;
      this.updateStats("set", performance.now() - startTime);

    } catch (error) {
      console.error("予測結果キャッシュ保存エラー:", error);
    }
  }

  /**
   * 予測結果のキャッシュ取得
   */
  async getCachedPrediction(key: string): Promise<PredictionCacheData | null> {
    if (!this.db) {
      return null;
    }

    try {
      const entry = await this.getEntry(key, this.PREDICTION_STORE);
      if (!entry) {
        this.stats.misses++;
        return null;
      }

      // TTLチェック
      if (this.isExpired(entry)) {
        await this.deleteEntry(key, this.PREDICTION_STORE);
        this.stats.misses++;
        return null;
      }

      // アクセス統計更新
      entry.metadata.lastAccessed = new Date().toISOString();
      entry.metadata.accessCount++;
      await this.saveEntry(entry, this.PREDICTION_STORE);

      this.stats.hits++;
      return entry.data;

    } catch (error) {
      console.error("予測結果キャッシュ取得エラー:", error);
      this.stats.misses++;
      return null;
    }
  }

  /**
   * モデル比較結果のキャッシュ保存
   */
  async cacheModelComparison(
    key: string,
    data: ModelComparisonCacheData,
    options: {
      ttl?: number;
      tags?: string[];
      priority?: number;
    } = {},
  ): Promise<void> {
    if (!this.db) {
      console.warn("データベースが初期化されていません");
      return;
    }

    try {
      const startTime = performance.now();
      const size = this.calculateSize(data);
      const shouldCompress = options.priority !== 1 && this.config.compressionEnabled && size > 1024;

      let processedData = data;
      if (shouldCompress) {
        processedData = await this.compress(data);
        this.stats.compressions++;
      }

      const entry: CacheEntry<ModelComparisonCacheData> = {
        key,
        data: processedData,
        metadata: {
          createdAt: new Date().toISOString(),
          lastAccessed: new Date().toISOString(),
          accessCount: 0,
          size: shouldCompress ? this.calculateSize(processedData) : size,
          ttl: options.ttl || this.config.defaultTTL,
          tags: options.tags || ["modelComparison"],
          version: this.config.version,
        },
      };

      // 容量チェック
      await this.ensureCapacity(entry.metadata.size);

      await this.saveEntry(entry, this.COMPARISON_STORE);
      this.stats.sets++;
      this.updateStats("set", performance.now() - startTime);

    } catch (error) {
      console.error("モデル比較キャッシュ保存エラー:", error);
    }
  }

  /**
   * モデル比較結果のキャッシュ取得
   */
  async getCachedModelComparison(key: string): Promise<ModelComparisonCacheData | null> {
    if (!this.db) {
      return null;
    }

    try {
      const entry = await this.getEntry(key, this.COMPARISON_STORE);
      if (!entry) {
        this.stats.misses++;
        return null;
      }

      // TTLチェック
      if (this.isExpired(entry)) {
        await this.deleteEntry(key, this.COMPARISON_STORE);
        this.stats.misses++;
        return null;
      }

      // アクセス統計更新
      entry.metadata.lastAccessed = new Date().toISOString();
      entry.metadata.accessCount++;
      await this.saveEntry(entry, this.COMPARISON_STORE);

      this.stats.hits++;
      return entry.data;

    } catch (error) {
      console.error("モデル比較キャッシュ取得エラー:", error);
      this.stats.misses++;
      return null;
    }
  }

  /**
   * キャッシュキーの生成
   */
  generateCacheKey(
    type: "prediction" | "comparison",
    parameters: Record<string, any>,
    modelName?: string,
  ): string {
    const paramString = JSON.stringify(parameters);
    const hash = this.simpleHash(paramString);
    const timestamp = new Date().toISOString().split("T")[0]; // 日付のみ
    
    if (type === "prediction" && modelName) {
      return `${type}_${modelName}_${hash}_${timestamp}`;
    }
    return `${type}_${hash}_${timestamp}`;
  }

  /**
   * キャッシュの検索（タグベース）
   */
  async searchCache(
    type: "prediction" | "comparison",
    tags: string[],
  ): Promise<Array<{ key: string; data: any; metadata: any }>> {
    if (!this.db) {
      return [];
    }

    try {
      const storeName = type === "prediction" ? this.PREDICTION_STORE : this.COMPARISON_STORE;
      const transaction = this.db.transaction([storeName], "readonly");
      const store = transaction.objectStore(storeName);
      const index = store.index("tags");
      
      const results: Array<{ key: string; data: any; metadata: any }> = [];
      
      for (const tag of tags) {
        const request = index.getAll(tag);
        const entries = await new Promise<any[]>((resolve, reject) => {
          request.onsuccess = () => resolve(request.result);
          request.onerror = () => reject(request.error);
        });

        for (const entry of entries) {
          if (!this.isExpired(entry)) {
            results.push({
              key: entry.key,
              data: entry.data,
              metadata: entry.metadata,
            });
          }
        }
      }

      return results;

    } catch (error) {
      console.error("キャッシュ検索エラー:", error);
      return [];
    }
  }

  /**
   * キャッシュのクリア
   */
  async clearCache(type?: "prediction" | "comparison"): Promise<void> {
    if (!this.db) {
      return;
    }

    try {
      if (type) {
        const storeName = type === "prediction" ? this.PREDICTION_STORE : this.COMPARISON_STORE;
        const transaction = this.db.transaction([storeName], "readwrite");
        const store = transaction.objectStore(storeName);
        await store.clear();
      } else {
        // 全キャッシュをクリア
        const stores = [this.PREDICTION_STORE, this.COMPARISON_STORE];
        for (const storeName of stores) {
          const transaction = this.db.transaction([storeName], "readwrite");
          const store = transaction.objectStore(storeName);
          await store.clear();
        }
      }

      console.log(`🧹 キャッシュをクリアしました: ${type || "all"}`);

    } catch (error) {
      console.error("キャッシュクリアエラー:", error);
    }
  }

  /**
   * キャッシュ統計の取得
   */
  getCacheStats(): {
    hits: number;
    misses: number;
    hitRate: number;
    totalSize: number;
    entryCount: number;
  } {
    const hitRate = this.stats.hits + this.stats.misses > 0 
      ? this.stats.hits / (this.stats.hits + this.stats.misses) 
      : 0;

    return {
      hits: this.stats.hits,
      misses: this.stats.misses,
      hitRate: Math.round(hitRate * 100) / 100,
      totalSize: 0, // 実装が必要
      entryCount: 0, // 実装が必要
    };
  }

  // プライベートメソッド

  private async getEntry(key: string, storeName: string): Promise<CacheEntry<any> | null> {
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([storeName], "readonly");
      const store = transaction.objectStore(storeName);
      const request = store.get(key);

      request.onsuccess = () => {
        resolve(request.result || null);
      };
      request.onerror = () => {
        reject(request.error);
      };
    });
  }

  private async saveEntry(entry: CacheEntry<any>, storeName: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([storeName], "readwrite");
      const store = transaction.objectStore(storeName);
      const request = store.put(entry);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  private async deleteEntry(key: string, storeName: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([storeName], "readwrite");
      const store = transaction.objectStore(storeName);
      const request = store.delete(key);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  private isExpired(entry: CacheEntry<any>): boolean {
    const now = new Date().getTime();
    const createdAt = new Date(entry.metadata.createdAt).getTime();
    return (now - createdAt) > entry.metadata.ttl;
  }

  private calculateSize(data: any): number {
    return new Blob([JSON.stringify(data)]).size;
  }

  private async compress(data: any): Promise<any> {
    // 簡易的な圧縮（実際の実装ではLZ4やGzipを使用）
    return data;
  }

  private async ensureCapacity(newSize: number): Promise<void> {
    // 容量管理の実装
    // 必要に応じて古いエントリを削除
  }

  private simpleHash(str: string): string {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // 32bit整数に変換
    }
    return Math.abs(hash).toString(36);
  }

  private updateStats(operation: string, duration: number): void {
    // 統計更新の実装
  }
}

// シングルトンインスタンス
export const predictionCacheManager = new PredictionCacheManager();
