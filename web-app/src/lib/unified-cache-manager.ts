/**
 * 統一キャッシュマネージャー（リファクタリング版）
 * 全キャッシュ機能を一元管理し、最適化されたキャッシュ戦略を提供
 */

export interface CacheOptions {
  ttl?: number;
  tags?: string[];
  priority?: number;
  fallbackData?: any;
  maxSize?: number;
}

export interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
  tags: string[];
  priority: number;
  accessCount: number;
  lastAccessed: number;
}

export interface CacheStats {
  hits: number;
  misses: number;
  totalRequests: number;
  hitRate: number;
  size: number;
  maxSize: number;
  memoryUsage: number;
}

export interface CacheStrategyConfig {
  maxSize: number;
  defaultTtl: number;
  compressionEnabled: boolean;
  deduplicationEnabled: boolean;
  lruEnabled: boolean;
  memoryThreshold: number;
}

class UnifiedCacheManager {
  private cache: Map<string, CacheEntry<any>> = new Map();
  private config: CacheStrategyConfig;
  private stats: CacheStats;
  private compressionEnabled: boolean;
  private deduplicationEnabled: boolean;
  private lruEnabled: boolean;

  constructor(config: Partial<CacheStrategyConfig> = {}) {
    this.config = {
      maxSize: config.maxSize || 1000,
      defaultTtl: config.defaultTtl || 60 * 60 * 1000, // 1時間
      compressionEnabled: config.compressionEnabled !== false,
      deduplicationEnabled: config.deduplicationEnabled !== false,
      lruEnabled: config.lruEnabled !== false,
      memoryThreshold: config.memoryThreshold || 50 * 1024 * 1024, // 50MB
    };

    this.stats = {
      hits: 0,
      misses: 0,
      totalRequests: 0,
      hitRate: 0,
      size: 0,
      maxSize: this.config.maxSize,
      memoryUsage: 0,
    };

    this.compressionEnabled = this.config.compressionEnabled;
    this.deduplicationEnabled = this.config.deduplicationEnabled;
    this.lruEnabled = this.config.lruEnabled;

    // メモリ監視の開始
    this.startMemoryMonitoring();
  }

  /**
   * データの取得
   */
  async get<T>(key: string): Promise<T | null> {
    this.stats.totalRequests++;

    const entry = this.cache.get(key);
    if (!entry) {
      this.stats.misses++;
      this.updateHitRate();
      return null;
    }

    // TTLチェック
    if (this.isExpired(entry)) {
      this.cache.delete(key);
      this.stats.misses++;
      this.updateHitRate();
      return null;
    }

    // アクセス統計の更新
    entry.accessCount++;
    entry.lastAccessed = Date.now();
    this.stats.hits++;
    this.updateHitRate();

    return entry.data;
  }

  /**
   * データの保存
   */
  async set<T>(
    key: string,
    data: T,
    options: CacheOptions = {},
  ): Promise<void> {
    const ttl = options.ttl || this.config.defaultTtl;
    const tags = options.tags || [];
    const priority = options.priority || 0.5;

    // メモリ使用量チェック
    if (this.shouldEvict()) {
      await this.evictEntries();
    }

    // 重複データの削除
    if (this.deduplicationEnabled) {
      await this.deduplicateData();
    }

    // データの圧縮
    let processedData = data;
    if (this.compressionEnabled && this.shouldCompress(data)) {
      processedData = await this.compressData(data);
    }

    const entry: CacheEntry<T> = {
      data: processedData,
      timestamp: Date.now(),
      ttl,
      tags,
      priority,
      accessCount: 0,
      lastAccessed: Date.now(),
    };

    this.cache.set(key, entry);
    this.updateStats();
  }

  /**
   * データの削除
   */
  async remove(key: string): Promise<boolean> {
    const deleted = this.cache.delete(key);
    this.updateStats();
    return deleted;
  }

  /**
   * タグによる一括削除
   */
  async removeByTags(tags: string[]): Promise<number> {
    let removedCount = 0;

    for (const [key, entry] of this.cache) {
      if (tags.some(tag => entry.tags.includes(tag))) {
        this.cache.delete(key);
        removedCount++;
      }
    }

    this.updateStats();
    return removedCount;
  }

  /**
   * キャッシュのクリア
   */
  async clear(): Promise<void> {
    this.cache.clear();
    this.updateStats();
  }

  /**
   * キャッシュの最適化
   */
  async optimize(): Promise<void> {
    // 期限切れエントリの削除
    await this.removeExpiredEntries();

    // 重複データの削除
    if (this.deduplicationEnabled) {
      await this.deduplicateData();
    }

    // LRUによる削除
    if (this.lruEnabled) {
      await this.evictLRUEntries();
    }

    // メモリ使用量の最適化
    await this.optimizeMemoryUsage();
  }

  /**
   * キャッシュ統計の取得
   */
  getStats(): CacheStats {
    return { ...this.stats };
  }

  /**
   * キャッシュの状態確認
   */
  getStatus(): {
    size: number;
    maxSize: number;
    memoryUsage: number;
    hitRate: number;
    expiredEntries: number;
  } {
    const expiredEntries = Array.from(this.cache.values()).filter(entry => this.isExpired(entry)).length;

    return {
      size: this.cache.size,
      maxSize: this.config.maxSize,
      memoryUsage: this.stats.memoryUsage,
      hitRate: this.stats.hitRate,
      expiredEntries,
    };
  }

  /**
   * エントリの期限切れチェック
   */
  private isExpired(entry: CacheEntry<any>): boolean {
    return Date.now() - entry.timestamp > entry.ttl;
  }

  /**
   * ヒット率の更新
   */
  private updateHitRate(): void {
    this.stats.hitRate = this.stats.totalRequests > 0 
      ? this.stats.hits / this.stats.totalRequests 
      : 0;
  }

  /**
   * 統計の更新
   */
  private updateStats(): void {
    this.stats.size = this.cache.size;
    this.stats.memoryUsage = this.calculateMemoryUsage();
  }

  /**
   * メモリ使用量の計算
   */
  private calculateMemoryUsage(): number {
    let totalSize = 0;
    for (const [key, entry] of this.cache) {
      totalSize += key.length * 2; // 文字列のサイズ（UTF-16）
      totalSize += JSON.stringify(entry.data).length * 2;
    }
    return totalSize;
  }

  /**
   * エビクションが必要かチェック
   */
  private shouldEvict(): boolean {
    return this.cache.size >= this.config.maxSize || 
           this.stats.memoryUsage >= this.config.memoryThreshold;
  }

  /**
   * エントリのエビクション
   */
  private async evictEntries(): Promise<void> {
    if (this.lruEnabled) {
      await this.evictLRUEntries();
    } else {
      await this.evictRandomEntries();
    }
  }

  /**
   * LRUによるエビクション
   */
  private async evictLRUEntries(): Promise<void> {
    const entries = Array.from(this.cache.entries());
    entries.sort((a, b) => a[1].lastAccessed - b[1].lastAccessed);

    const toRemove = Math.floor(entries.length * 0.1); // 10%を削除
    for (let i = 0; i < toRemove; i++) {
      this.cache.delete(entries[i][0]);
    }
  }

  /**
   * ランダムエビクション
   */
  private async evictRandomEntries(): Promise<void> {
    const keys = Array.from(this.cache.keys());
    const toRemove = Math.floor(keys.length * 0.1); // 10%を削除
    
    for (let i = 0; i < toRemove; i++) {
      const randomIndex = Math.floor(Math.random() * keys.length);
      this.cache.delete(keys[randomIndex]);
      keys.splice(randomIndex, 1);
    }
  }

  /**
   * 期限切れエントリの削除
   */
  private async removeExpiredEntries(): Promise<void> {
    const expiredKeys: string[] = [];
    
    for (const [key, entry] of this.cache) {
      if (this.isExpired(entry)) {
        expiredKeys.push(key);
      }
    }

    expiredKeys.forEach(key => this.cache.delete(key));
  }

  /**
   * 重複データの削除
   */
  private async deduplicateData(): Promise<void> {
    const seen = new Set<string>();
    const duplicates: string[] = [];

    for (const [key, entry] of this.cache) {
      const hash = this.hashData(entry.data);
      if (seen.has(hash)) {
        duplicates.push(key);
      } else {
        seen.add(hash);
      }
    }

    duplicates.forEach(key => this.cache.delete(key));

    if (duplicates.length > 0) {
      console.debug("重複データを削除:", {
        duplicates: duplicates.length,
        remaining: this.cache.size,
      });
    }
  }

  /**
   * データのハッシュ化
   */
  private hashData(data: any): string {
    return JSON.stringify(data);
  }

  /**
   * データの圧縮が必要かチェック
   */
  private shouldCompress(data: any): boolean {
    const dataSize = JSON.stringify(data).length;
    return dataSize > 1024; // 1KB以上の場合
  }

  /**
   * データの圧縮
   */
  private async compressData(data: any): Promise<any> {
    // 簡易的な圧縮（実際の実装ではLZ4やGzipを使用）
    try {
      const jsonString = JSON.stringify(data);
      const compressed = btoa(jsonString); // Base64エンコード
      return { compressed: true, data: compressed };
    } catch (error) {
      console.warn("データ圧縮に失敗:", error);
      return data;
    }
  }

  /**
   * メモリ使用量の最適化
   */
  private async optimizeMemoryUsage(): Promise<void> {
    if (this.stats.memoryUsage > this.config.memoryThreshold) {
      // メモリ使用量が閾値を超えた場合、古いエントリを削除
      const entries = Array.from(this.cache.entries());
      entries.sort((a, b) => a[1].timestamp - b[1].timestamp);

      const toRemove = Math.floor(entries.length * 0.2); // 20%を削除
      for (let i = 0; i < toRemove; i++) {
        this.cache.delete(entries[i][0]);
      }
    }
  }

  /**
   * メモリ監視の開始
   */
  private startMemoryMonitoring(): void {
    setInterval(() => {
      this.updateStats();
      if (this.shouldEvict()) {
        this.optimize();
      }
    }, 30000); // 30秒ごとにチェック
  }
}

// シングルトンインスタンス
export const unifiedCacheManager = new UnifiedCacheManager();

// 便利な関数
export async function getCachedData<T>(
  key: string,
  fetchFn: () => Promise<T>,
  options: CacheOptions = {},
): Promise<{ data: T; fromCache: boolean; error?: string }> {
  try {
    // まずキャッシュをチェック
    const cached = await unifiedCacheManager.get<T>(key);
    if (cached) {
      return { data: cached, fromCache: true };
    }

    // キャッシュがない場合は関数から取得
    const freshData = await fetchFn();
    await unifiedCacheManager.set(key, freshData, options);
    return { data: freshData, fromCache: false };
  } catch (error) {
    console.error(`データ取得に失敗 (${key}):`, error);
    
    // エラー時はキャッシュを再確認
    const cached = await unifiedCacheManager.get<T>(key);
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

export default unifiedCacheManager;
