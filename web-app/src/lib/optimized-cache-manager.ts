/**
 * 最適化された統合キャッシュマネージャー
 * 重複したキャッシュ機能を統合し、パフォーマンスを最適化
 */

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
  tags?: string[];
  priority?: number;
  compressed?: boolean;
  size?: number;
}

interface CacheConfig {
  maxSize: number;
  defaultTtl: number;
  cleanupInterval: number;
  compressionEnabled: boolean;
  persistenceEnabled: boolean;
  lruEnabled: boolean;
  memoryThreshold: number;
  compressionThreshold: number;
}

interface CacheStats {
  hits: number;
  misses: number;
  totalRequests: number;
  hitRate: number;
  size: number;
  maxSize: number;
  memoryUsage: number;
  compressionRatio: number;
  evictions: number;
  oldestItem: number;
  newestItem: number;
}

interface CacheOptions {
  ttl?: number;
  tags?: string[];
  priority?: number;
  compress?: boolean;
  persist?: boolean;
}

class OptimizedCacheManager {
  private memoryCache: Map<string, CacheEntry<any>> = new Map();
  private config: CacheConfig;
  private db: IDBDatabase | null = null;
  private cleanupTimer: NodeJS.Timeout | null = null;
  private stats: CacheStats;
  private compressionEnabled: boolean;
  private persistenceEnabled: boolean;
  private lruEnabled: boolean;

  constructor(config: Partial<CacheConfig> = {}) {
    this.config = {
      maxSize: config.maxSize || 1000,
      defaultTtl: config.defaultTtl || 300000, // 5分
      cleanupInterval: config.cleanupInterval || 60000, // 1分
      compressionEnabled: config.compressionEnabled !== false,
      persistenceEnabled: config.persistenceEnabled !== false,
      lruEnabled: config.lruEnabled !== false,
      memoryThreshold: config.memoryThreshold || 50 * 1024 * 1024, // 50MB
      compressionThreshold: config.compressionThreshold || 1024, // 1KB
    };

    this.stats = {
      hits: 0,
      misses: 0,
      totalRequests: 0,
      hitRate: 0,
      size: 0,
      maxSize: this.config.maxSize,
      memoryUsage: 0,
      compressionRatio: 0,
      evictions: 0,
      oldestItem: 0,
      newestItem: 0,
    };

    this.compressionEnabled = this.config.compressionEnabled;
    this.persistenceEnabled = this.config.persistenceEnabled;
    this.lruEnabled = this.config.lruEnabled;

    this.initIndexedDB();
    this.startCleanup();
    this.startMemoryMonitoring();
  }

  /**
   * IndexedDBの初期化
   */
  private async initIndexedDB(): Promise<void> {
    if (!this.persistenceEnabled) return;
    
    if (typeof window === "undefined") {
      console.warn("IndexedDBはクライアントサイドでのみ利用可能です");
      return;
    }

    return new Promise((resolve, reject) => {
      const request = indexedDB.open("optimized_cache_db", 1);
      
      request.onerror = () => {
        console.error("IndexedDB初期化エラー:", request.error);
        reject(request.error);
      };
      
      request.onsuccess = () => {
        this.db = request.result;
        console.info("IndexedDB初期化完了");
        resolve();
      };
      
      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        
        if (!db.objectStoreNames.contains("cache")) {
          const store = db.createObjectStore("cache", { keyPath: "key" });
          store.createIndex("timestamp", "timestamp", { unique: false });
          store.createIndex("tags", "tags", { unique: false, multiEntry: true });
          store.createIndex("priority", "priority", { unique: false });
        }
      };
    });
  }

  /**
   * データの取得
   */
  async get<T>(key: string, options: CacheOptions = {}): Promise<T | null> {
    this.stats.totalRequests++;

    // メモリキャッシュから取得
    const memoryEntry = this.memoryCache.get(key);
    if (memoryEntry && this.isValid(memoryEntry)) {
      this.stats.hits++;
      this.updateAccessTime(key);
      return memoryEntry.data as T;
    }

    // 永続化キャッシュから取得
    if (this.persistenceEnabled && this.db) {
      try {
        const persistentEntry = await this.getFromIndexedDB(key);
        if (persistentEntry && this.isValid(persistentEntry)) {
          // メモリキャッシュに復元
          this.memoryCache.set(key, persistentEntry);
          this.stats.hits++;
          this.updateAccessTime(key);
          return persistentEntry.data as T;
        }
      } catch (error) {
        console.warn("永続化キャッシュからの取得に失敗:", error);
      }
    }

    this.stats.misses++;
    return null;
  }

  /**
   * データの設定
   */
  async set<T>(key: string, data: T, options: CacheOptions = {}): Promise<void> {
    const ttl = options.ttl || this.config.defaultTtl;
    const tags = options.tags || [];
    const priority = options.priority || 0;
    const compress = options.compress !== false && this.shouldCompress(data);
    const persist = options.persist !== false && this.persistenceEnabled;

    const entry: CacheEntry<T> = {
      data: compress ? await this.compress(data) : data,
      timestamp: Date.now(),
      ttl,
      tags,
      priority,
      compressed: compress,
      size: this.calculateSize(data),
    };

    // メモリキャッシュに保存
    this.memoryCache.set(key, entry);
    this.updateStats();

    // 永続化キャッシュに保存
    if (persist && this.db) {
      try {
        await this.saveToIndexedDB(key, entry);
      } catch (error) {
        console.warn("永続化キャッシュへの保存に失敗:", error);
      }
    }

    // キャッシュサイズの制限チェック
    if (this.memoryCache.size > this.config.maxSize) {
      await this.evictEntries();
    }
  }

  /**
   * データの削除
   */
  async remove(key: string): Promise<void> {
    this.memoryCache.delete(key);

    if (this.persistenceEnabled && this.db) {
      try {
        await this.removeFromIndexedDB(key);
      } catch (error) {
        console.warn("永続化キャッシュからの削除に失敗:", error);
      }
    }
  }

  /**
   * タグによる一括削除
   */
  async removeByTags(tags: string[]): Promise<void> {
    const keysToRemove: string[] = [];

    for (const [key, entry] of this.memoryCache) {
      if (entry.tags && entry.tags.some(tag => tags.includes(tag))) {
        keysToRemove.push(key);
      }
    }

    for (const key of keysToRemove) {
      await this.remove(key);
    }
  }

  /**
   * キャッシュのクリア
   */
  async clear(): Promise<void> {
    this.memoryCache.clear();

    if (this.persistenceEnabled && this.db) {
      try {
        await this.clearIndexedDB();
      } catch (error) {
        console.warn("永続化キャッシュのクリアに失敗:", error);
      }
    }

    this.resetStats();
  }

  /**
   * エントリの有効性チェック
   */
  private isValid(entry: CacheEntry<any>): boolean {
    return Date.now() - entry.timestamp < entry.ttl;
  }

  /**
   * アクセス時間の更新
   */
  private updateAccessTime(key: string): void {
    const entry = this.memoryCache.get(key);
    if (entry) {
      entry.timestamp = Date.now();
    }
  }

  /**
   * データサイズの計算
   */
  private calculateSize(data: any): number {
    return JSON.stringify(data).length;
  }

  /**
   * 圧縮が必要かどうかの判定
   */
  private shouldCompress(data: any): boolean {
    if (!this.compressionEnabled) return false;
    const size = this.calculateSize(data);
    return size > this.config.compressionThreshold;
  }

  /**
   * データの圧縮
   */
  private async compress(data: any): Promise<any> {
    // 簡易的な圧縮実装（実際の実装ではLZ4やGzipを使用）
    const jsonString = JSON.stringify(data);
    return btoa(jsonString); // Base64エンコード
  }

  /**
   * データの展開
   */
  private async decompress(data: any): Promise<any> {
    try {
      const jsonString = atob(data); // Base64デコード
      return JSON.parse(jsonString);
    } catch (error) {
      console.warn("データの展開に失敗:", error);
      return data;
    }
  }

  /**
   * IndexedDBからの取得
   */
  private async getFromIndexedDB(key: string): Promise<CacheEntry<any> | null> {
    if (!this.db) return null;

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(["cache"], "readonly");
      const store = transaction.objectStore("cache");
      const request = store.get(key);

      request.onsuccess = () => {
        const result = request.result;
        if (result) {
          resolve(result.entry);
        } else {
          resolve(null);
        }
      };

      request.onerror = () => {
        reject(request.error);
      };
    });
  }

  /**
   * IndexedDBへの保存
   */
  private async saveToIndexedDB(key: string, entry: CacheEntry<any>): Promise<void> {
    if (!this.db) return;

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(["cache"], "readwrite");
      const store = transaction.objectStore("cache");
      const request = store.put({ key, entry, timestamp: Date.now() });

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * IndexedDBからの削除
   */
  private async removeFromIndexedDB(key: string): Promise<void> {
    if (!this.db) return;

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(["cache"], "readwrite");
      const store = transaction.objectStore("cache");
      const request = store.delete(key);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * IndexedDBのクリア
   */
  private async clearIndexedDB(): Promise<void> {
    if (!this.db) return;

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(["cache"], "readwrite");
      const store = transaction.objectStore("cache");
      const request = store.clear();

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * エントリの削除（LRU）
   */
  private async evictEntries(): Promise<void> {
    if (!this.lruEnabled) return;

    const entries = Array.from(this.memoryCache.entries())
      .sort(([, a], [, b]) => a.timestamp - b.timestamp);

    const toEvict = entries.slice(0, Math.floor(this.config.maxSize * 0.1));
    
    for (const [key] of toEvict) {
      this.memoryCache.delete(key);
      this.stats.evictions++;
    }
  }

  /**
   * 期限切れエントリの削除
   */
  private async removeExpiredEntries(): Promise<void> {
    const now = Date.now();
    const expiredKeys: string[] = [];

    for (const [key, entry] of this.memoryCache) {
      if (now - entry.timestamp >= entry.ttl) {
        expiredKeys.push(key);
      }
    }

    expiredKeys.forEach(key => this.memoryCache.delete(key));
  }

  /**
   * 重複データの削除
   */
  private async deduplicateData(): Promise<void> {
    const seen = new Set<string>();
    const duplicates: string[] = [];

    for (const [key, entry] of this.memoryCache) {
      const hash = this.hashData(entry.data);
      if (seen.has(hash)) {
        duplicates.push(key);
      } else {
        seen.add(hash);
      }
    }

    duplicates.forEach(key => this.memoryCache.delete(key));

    if (duplicates.length > 0) {
      console.debug("重複データを削除:", {
        duplicates: duplicates.length,
        remaining: this.memoryCache.size,
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
   * クリーンアップの開始
   */
  private startCleanup(): void {
    this.cleanupTimer = setInterval(async () => {
      await this.removeExpiredEntries();
      await this.deduplicateData();
      this.updateStats();
    }, this.config.cleanupInterval);
  }

  /**
   * メモリ監視の開始
   */
  private startMemoryMonitoring(): void {
    if (typeof window === "undefined") return;

    setInterval(() => {
      this.updateStats();
      
      if (this.stats.memoryUsage > this.config.memoryThreshold) {
        this.evictEntries();
      }
    }, 30000); // 30秒ごと
  }

  /**
   * 統計の更新
   */
  private updateStats(): void {
    this.stats.size = this.memoryCache.size;
    this.stats.hitRate = this.stats.totalRequests > 0 
      ? (this.stats.hits / this.stats.totalRequests) * 100 
      : 0;

    // メモリ使用量の計算
    let totalSize = 0;
    let oldestTime = Date.now();
    let newestTime = 0;

    for (const [, entry] of this.memoryCache) {
      totalSize += entry.size || 0;
      oldestTime = Math.min(oldestTime, entry.timestamp);
      newestTime = Math.max(newestTime, entry.timestamp);
    }

    this.stats.memoryUsage = totalSize;
    this.stats.oldestItem = oldestTime;
    this.stats.newestItem = newestTime;
  }

  /**
   * 統計のリセット
   */
  private resetStats(): void {
    this.stats = {
      hits: 0,
      misses: 0,
      totalRequests: 0,
      hitRate: 0,
      size: 0,
      maxSize: this.config.maxSize,
      memoryUsage: 0,
      compressionRatio: 0,
      evictions: 0,
      oldestItem: 0,
      newestItem: 0,
    };
  }

  /**
   * 統計の取得
   */
  getStats(): CacheStats {
    return { ...this.stats };
  }

  /**
   * 設定の取得
   */
  getConfig(): CacheConfig {
    return { ...this.config };
  }

  /**
   * 設定の更新
   */
  updateConfig(newConfig: Partial<CacheConfig>): void {
    this.config = { ...this.config, ...newConfig };
    
    if (newConfig.maxSize && this.memoryCache.size > newConfig.maxSize) {
      this.evictEntries();
    }
  }

  /**
   * クリーンアップの停止
   */
  destroy(): void {
    if (this.cleanupTimer) {
      clearInterval(this.cleanupTimer);
      this.cleanupTimer = null;
    }

    if (this.db) {
      this.db.close();
      this.db = null;
    }
  }
}

// シングルトンインスタンス
const optimizedCacheManager = new OptimizedCacheManager();

export default optimizedCacheManager;
export type { CacheEntry, CacheConfig, CacheStats, CacheOptions };