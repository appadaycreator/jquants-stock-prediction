/**
 * 最適化された統合キャッシュマネージャー
 * 重複したキャッシュ機能を統合し、パフォーマンスを最適化
 */

export interface CacheItem<T = any> {
  data: T;
  timestamp: number;
  ttl: number;
  accessCount: number;
  lastAccessed: number;
  size: number;
}

export interface CacheOptions {
  ttl?: number;
  maxSize?: number;
  compression?: boolean;
  persistence?: boolean;
}

export interface CacheStatistics {
  hitRate: number;
  missRate: number;
  totalItems: number;
  totalSize: number;
  memoryUsage: number;
  evictionCount: number;
}

export interface CacheConfig {
  defaultTtl: number;
  maxMemorySize: number;
  maxItems: number;
  compressionThreshold: number;
  persistenceEnabled: boolean;
  evictionPolicy: "lru" | "lfu" | "fifo";
}

class OptimizedCacheManager {
  private cache: Map<string, CacheItem> = new Map();
  private accessOrder: string[] = [];
  private config: CacheConfig;
  private statistics: CacheStatistics;
  private compressionEnabled: boolean = false;

  constructor(config: Partial<CacheConfig> = {}) {
    this.config = {
      defaultTtl: 5 * 60 * 1000, // 5分
      maxMemorySize: 50 * 1024 * 1024, // 50MB
      maxItems: 1000,
      compressionThreshold: 1024, // 1KB
      persistenceEnabled: true,
      evictionPolicy: "lru",
      ...config,
    };

    this.statistics = {
      hitRate: 0,
      missRate: 0,
      totalItems: 0,
      totalSize: 0,
      memoryUsage: 0,
      evictionCount: 0,
    };

    this.initializePersistence();
  }

  /**
   * データの取得
   */
  get<T>(key: string): T | null {
    const item = this.cache.get(key);
    
    if (!item) {
      this.updateStatistics(false);
      return null;
    }

    // TTLチェック
    if (this.isExpired(item)) {
      this.cache.delete(key);
      this.removeFromAccessOrder(key);
      this.updateStatistics(false);
      return null;
    }

    // アクセス情報の更新
    item.accessCount++;
    item.lastAccessed = Date.now();
    this.updateAccessOrder(key);
    this.updateStatistics(true);

    return item.data as T;
  }

  /**
   * データの保存
   */
  set<T>(key: string, data: T, options: CacheOptions = {}): void {
    const ttl = options.ttl || this.config.defaultTtl;
    const size = this.calculateSize(data);
    
    // メモリ制限チェック
    if (this.shouldEvict(size)) {
      this.evictItems(size);
    }

    // データの圧縮
    const processedData = this.processData(data, options);

    const item: CacheItem<T> = {
      data: processedData,
      timestamp: Date.now(),
      ttl,
      accessCount: 0,
      lastAccessed: Date.now(),
      size,
    };

    this.cache.set(key, item);
    this.updateAccessOrder(key);
    this.updateStatistics(false);

    // 永続化
    if (this.config.persistenceEnabled && options.persistence !== false) {
      this.saveToPersistence(key, item);
    }
  }

  /**
   * データの削除
   */
  delete(key: string): boolean {
    const deleted = this.cache.delete(key);
    this.removeFromAccessOrder(key);
    
    if (deleted && this.config.persistenceEnabled) {
      this.removeFromPersistence(key);
    }

    return deleted;
  }

  /**
   * キャッシュのクリア
   */
  clear(): void {
    this.cache.clear();
    this.accessOrder = [];
    this.statistics = {
      hitRate: 0,
      missRate: 0,
      totalItems: 0,
      totalSize: 0,
      memoryUsage: 0,
      evictionCount: 0,
    };

    if (this.config.persistenceEnabled) {
      this.clearPersistence();
    }
  }

  /**
   * キャッシュの存在確認
   */
  has(key: string): boolean {
    const item = this.cache.get(key);
    return item ? !this.isExpired(item) : false;
  }

  /**
   * キャッシュサイズの取得
   */
  size(): number {
    return this.cache.size;
  }

  /**
   * キャッシュ統計の取得
   */
  getStatistics(): CacheStatistics {
    this.updateMemoryUsage();
    return { ...this.statistics };
  }

  /**
   * キャッシュの最適化
   */
  optimize(): void {
    // 期限切れアイテムの削除
    this.removeExpiredItems();

    // メモリ使用量の最適化
    if (this.statistics.memoryUsage > this.config.maxMemorySize) {
      this.evictItems(0);
    }

    // アクセス頻度の低いアイテムの削除
    this.removeLowAccessItems();
  }

  /**
   * データの処理（圧縮など）
   */
  private processData<T>(data: T, options: CacheOptions): T {
    if (options.compression && this.shouldCompress(data)) {
      return this.compress(data);
    }
    return data;
  }

  /**
   * データサイズの計算
   */
  private calculateSize(data: any): number {
    try {
      return JSON.stringify(data).length * 2; // 概算
    } catch {
      return 0;
    }
  }

  /**
   * 期限切れチェック
   */
  private isExpired(item: CacheItem): boolean {
    return Date.now() - item.timestamp > item.ttl;
  }

  /**
   * エビクションが必要かチェック
   */
  private shouldEvict(newItemSize: number): boolean {
    return this.cache.size >= this.config.maxItems || 
           this.statistics.memoryUsage + newItemSize > this.config.maxMemorySize;
  }

  /**
   * アイテムのエビクション
   */
  private evictItems(requiredSpace: number): void {
    const itemsToEvict: string[] = [];
    let freedSpace = 0;

    // エビクションポリシーに基づいてアイテムを選択
    switch (this.config.evictionPolicy) {
      case "lru":
        itemsToEvict.push(...this.getLRUItems());
        break;
      case "lfu":
        itemsToEvict.push(...this.getLFUItems());
        break;
      case "fifo":
        itemsToEvict.push(...this.getFIFOItems());
        break;
    }

    // アイテムの削除
    for (const key of itemsToEvict) {
      const item = this.cache.get(key);
      if (item) {
        freedSpace += item.size;
        this.cache.delete(key);
        this.removeFromAccessOrder(key);
        this.statistics.evictionCount++;
      }

      if (freedSpace >= requiredSpace) {
        break;
      }
    }
  }

  /**
   * LRUアイテムの取得
   */
  private getLRUItems(): string[] {
    return this.accessOrder.slice(0, Math.floor(this.cache.size * 0.1));
  }

  /**
   * LFUアイテムの取得
   */
  private getLFUItems(): string[] {
    const items = Array.from(this.cache.entries())
      .sort(([, a], [, b]) => a.accessCount - b.accessCount)
      .slice(0, Math.floor(this.cache.size * 0.1))
      .map(([key]) => key);
    
    return items;
  }

  /**
   * FIFOアイテムの取得
   */
  private getFIFOItems(): string[] {
    const items = Array.from(this.cache.entries())
      .sort(([, a], [, b]) => a.timestamp - b.timestamp)
      .slice(0, Math.floor(this.cache.size * 0.1))
      .map(([key]) => key);
    
    return items;
  }

  /**
   * アクセス順序の更新
   */
  private updateAccessOrder(key: string): void {
    this.removeFromAccessOrder(key);
    this.accessOrder.push(key);
  }

  /**
   * アクセス順序からの削除
   */
  private removeFromAccessOrder(key: string): void {
    const index = this.accessOrder.indexOf(key);
    if (index > -1) {
      this.accessOrder.splice(index, 1);
    }
  }

  /**
   * 期限切れアイテムの削除
   */
  private removeExpiredItems(): void {
    const expiredKeys: string[] = [];
    
    for (const [key, item] of this.cache.entries()) {
      if (this.isExpired(item)) {
        expiredKeys.push(key);
      }
    }

    expiredKeys.forEach(key => {
      this.cache.delete(key);
      this.removeFromAccessOrder(key);
    });
  }

  /**
   * 低アクセスアイテムの削除
   */
  private removeLowAccessItems(): void {
    const lowAccessItems = Array.from(this.cache.entries())
      .filter(([, item]) => item.accessCount < 2)
      .sort(([, a], [, b]) => a.lastAccessed - b.lastAccessed)
      .slice(0, Math.floor(this.cache.size * 0.05))
      .map(([key]) => key);

    lowAccessItems.forEach(key => {
      this.cache.delete(key);
      this.removeFromAccessOrder(key);
    });
  }

  /**
   * 統計情報の更新
   */
  private updateStatistics(hit: boolean): void {
    const total = this.statistics.hitRate + this.statistics.missRate + 1;
    
    if (hit) {
      this.statistics.hitRate++;
    } else {
      this.statistics.missRate++;
    }

    this.statistics.totalItems = this.cache.size;
    this.updateMemoryUsage();
  }

  /**
   * メモリ使用量の更新
   */
  private updateMemoryUsage(): void {
    let totalSize = 0;
    for (const item of this.cache.values()) {
      totalSize += item.size;
    }
    this.statistics.totalSize = totalSize;
    this.statistics.memoryUsage = totalSize;
  }

  /**
   * データの圧縮が必要かチェック
   */
  private shouldCompress(data: any): boolean {
    const size = this.calculateSize(data);
    return size > this.config.compressionThreshold;
  }

  /**
   * データの圧縮
   */
  private compress<T>(data: T): T {
    // 簡易的な圧縮（実際の実装では適切な圧縮ライブラリを使用）
    try {
      const compressed = JSON.stringify(data);
      return JSON.parse(compressed) as T;
    } catch {
      return data;
    }
  }

  /**
   * 永続化の初期化
   */
  private initializePersistence(): void {
    if (this.config.persistenceEnabled && typeof window !== "undefined") {
      this.loadFromPersistence();
    }
  }

  /**
   * 永続化からの読み込み
   */
  private loadFromPersistence(): void {
    try {
      const stored = localStorage.getItem("optimized_cache");
      if (stored) {
        const data = JSON.parse(stored);
        this.cache = new Map(data.cache || []);
        this.accessOrder = data.accessOrder || [];
      }
    } catch (error) {
      console.warn("キャッシュの永続化読み込みに失敗しました:", error);
    }
  }

  /**
   * 永続化への保存
   */
  private saveToPersistence(key: string, item: CacheItem): void {
    try {
      const data = {
        cache: Array.from(this.cache.entries()),
        accessOrder: this.accessOrder,
      };
      localStorage.setItem("optimized_cache", JSON.stringify(data));
    } catch (error) {
      console.warn("キャッシュの永続化保存に失敗しました:", error);
    }
  }

  /**
   * 永続化からの削除
   */
  private removeFromPersistence(key: string): void {
    this.saveToPersistence(key, {} as CacheItem);
  }

  /**
   * 永続化のクリア
   */
  private clearPersistence(): void {
    try {
      localStorage.removeItem("optimized_cache");
    } catch (error) {
      console.warn("キャッシュの永続化クリアに失敗しました:", error);
    }
  }
}

// シングルトンインスタンス
export const optimizedCacheManager = new OptimizedCacheManager();

// 便利な関数
export const getCache = <T>(key: string): T | null => 
  optimizedCacheManager.get<T>(key);

export const setCache = <T>(key: string, data: T, options?: CacheOptions): void => 
  optimizedCacheManager.set(key, data, options);

export const deleteCache = (key: string): boolean => 
  optimizedCacheManager.delete(key);

export const clearCache = (): void => 
  optimizedCacheManager.clear();

export const hasCache = (key: string): boolean => 
  optimizedCacheManager.has(key);

export const getCacheStatistics = (): CacheStatistics => 
  optimizedCacheManager.getStatistics();

export const optimizeCache = (): void => 
  optimizedCacheManager.optimize();
