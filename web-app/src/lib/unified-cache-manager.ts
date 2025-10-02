/**
 * 統一されたキャッシュマネージャー
 * アプリケーション全体で使用されるキャッシュ機能を提供
 * 予測結果、モデル比較、データ品質管理を含む包括的なキャッシュシステム
 */

export interface CacheOptions {
  ttl?: number; // Time to live in milliseconds
  tags?: string[]; // Cache tags for invalidation
  priority?: number; // Cache priority (0-1)
  maxSize?: number; // Maximum cache size in bytes
  compression?: boolean; // Enable compression for large data
}

// 予測結果キャッシュ用のデータ型
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

// モデル比較キャッシュ用のデータ型
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

export interface CacheEntry<T = any> {
  data: T;
  timestamp: number;
  ttl: number;
  tags: string[];
  priority: number;
  size: number;
}

class UnifiedCacheManager {
  private cache = new Map<string, CacheEntry>();
  private maxSize = 50 * 1024 * 1024; // 50MB default
  private currentSize = 0;
  private cleanupInterval: NodeJS.Timeout | null = null;
  private stats = {
    hits: 0,
    misses: 0,
    sets: 0,
    deletes: 0,
    compressions: 0,
  };

  constructor() {
    this.startCleanup();
  }

  // キャッシュからデータを取得
  async get<T>(key: string): Promise<T | null> {
    const entry = this.cache.get(key);
    
    if (!entry) {
      this.stats.misses++;
      return null;
    }

    // TTLチェック
    if (this.isExpired(entry)) {
      this.delete(key);
      this.stats.misses++;
      return null;
    }

    // アクセス時間を更新
    entry.timestamp = Date.now();
    this.stats.hits++;
    return entry.data as T;
  }

  // キャッシュにデータを保存
  async set<T>(key: string, data: T, options: CacheOptions = {}): Promise<void> {
    const {
      ttl = 300000, // 5分デフォルト
      tags = [],
      priority = 0.5,
      maxSize = 1024 * 1024, // 1MBデフォルト
      compression = false,
    } = options;

    let processedData = data;
    let serializedData = JSON.stringify(data);
    let size = new Blob([serializedData]).size;

    // 圧縮が有効でデータが大きい場合
    if (compression && size > 1024) {
      processedData = await this.compress(data);
      serializedData = JSON.stringify(processedData);
      size = new Blob([serializedData]).size;
      this.stats.compressions++;
    }

    if (size > maxSize) {
      console.warn(`Cache entry ${key} exceeds maximum size limit`);
      return;
    }

    // サイズ制限チェック
    if (this.currentSize + size > this.maxSize) {
      await this.evictLeastPriority();
    }

    const entry: CacheEntry<T> = {
      data: processedData,
      timestamp: Date.now(),
      ttl,
      tags,
      priority,
      size,
    };

    this.cache.set(key, entry);
    this.currentSize += size;
    this.stats.sets++;
  }

  // キャッシュから削除
  async delete(key: string): Promise<boolean> {
    const entry = this.cache.get(key);
    if (entry) {
      this.currentSize -= entry.size;
      this.stats.deletes++;
      return this.cache.delete(key);
    }
    return false;
  }

  // タグに基づいてキャッシュをクリア
  async clearByTags(tags: string[]): Promise<number> {
    let clearedCount = 0;
    
    for (const [key, entry] of this.cache.entries()) {
      if (tags.some(tag => entry.tags.includes(tag))) {
        this.currentSize -= entry.size;
        this.cache.delete(key);
        clearedCount++;
      }
    }
    
    return clearedCount;
  }

  // 全キャッシュをクリア
  async clear(): Promise<void> {
    this.cache.clear();
    this.currentSize = 0;
  }

  // キャッシュ統計を取得
  getStats(): {
    size: number;
    count: number;
    maxSize: number;
    hitRate: number;
    hits: number;
    misses: number;
    sets: number;
    deletes: number;
    compressions: number;
  } {
    const totalRequests = this.stats.hits + this.stats.misses;
    const hitRate = totalRequests > 0 ? this.stats.hits / totalRequests : 0;
    
    return {
      size: this.currentSize,
      count: this.cache.size,
      maxSize: this.maxSize,
      hitRate: Math.round(hitRate * 100) / 100,
      hits: this.stats.hits,
      misses: this.stats.misses,
      sets: this.stats.sets,
      deletes: this.stats.deletes,
      compressions: this.stats.compressions,
    };
  }

  // 期限切れチェック
  private isExpired(entry: CacheEntry): boolean {
    return Date.now() - entry.timestamp > entry.ttl;
  }

  // 優先度の低いエントリを削除
  private async evictLeastPriority(): Promise<void> {
    const entries = Array.from(this.cache.entries());
    entries.sort((a, b) => a[1].priority - b[1].priority);
    
    // 最低優先度のエントリを削除
    const [key, entry] = entries[0];
    this.currentSize -= entry.size;
    this.cache.delete(key);
  }

  // 定期的なクリーンアップ
  private startCleanup(): void {
    this.cleanupInterval = setInterval(() => {
      this.cleanup();
    }, 60000); // 1分ごと
  }

  // 期限切れエントリのクリーンアップ
  private cleanup(): void {
    const now = Date.now();
    for (const [key, entry] of this.cache.entries()) {
      if (now - entry.timestamp > entry.ttl) {
        this.currentSize -= entry.size;
        this.cache.delete(key);
      }
    }
  }

  // 予測結果のキャッシュ保存
  async cachePrediction(
    key: string,
    data: PredictionCacheData,
    options: CacheOptions = {}
  ): Promise<void> {
    await this.set(key, data, {
      ...options,
      tags: [...(options.tags || []), 'prediction'],
      ttl: options.ttl || 24 * 60 * 60 * 1000, // 24時間
    });
  }

  // 予測結果のキャッシュ取得
  async getCachedPrediction(key: string): Promise<PredictionCacheData | null> {
    return await this.get<PredictionCacheData>(key);
  }

  // モデル比較結果のキャッシュ保存
  async cacheModelComparison(
    key: string,
    data: ModelComparisonCacheData,
    options: CacheOptions = {}
  ): Promise<void> {
    await this.set(key, data, {
      ...options,
      tags: [...(options.tags || []), 'modelComparison'],
      ttl: options.ttl || 24 * 60 * 60 * 1000, // 24時間
    });
  }

  // モデル比較結果のキャッシュ取得
  async getCachedModelComparison(key: string): Promise<ModelComparisonCacheData | null> {
    return await this.get<ModelComparisonCacheData>(key);
  }

  // データ圧縮（簡易実装）
  private async compress(data: any): Promise<any> {
    // 実際の実装ではLZ4やGzipを使用
    return data;
  }

  // リソースのクリーンアップ
  destroy(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
      this.cleanupInterval = null;
    }
    this.cache.clear();
    this.currentSize = 0;
  }
}

// シングルトンインスタンス
export const unifiedCacheManager = new UnifiedCacheManager();
