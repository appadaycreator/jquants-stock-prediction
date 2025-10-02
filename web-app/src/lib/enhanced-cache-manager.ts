/**
 * 強化されたキャッシュマネージャー
 * IndexedDB、LocalStorage、メモリキャッシュを統合
 */

interface CacheItem<T> {
  data: T;
  timestamp: number;
  ttl: number;
  tags: string[];
  priority: number;
  accessCount: number;
  lastAccessed: number;
}

interface CacheConfig {
  maxSize: number;
  defaultTtl: number;
  cleanupInterval: number;
  compressionEnabled: boolean;
  persistenceEnabled: boolean;
}

interface CacheStats {
  totalItems: number;
  hitRate: number;
  missRate: number;
  totalSize: number;
  averageAccessTime: number;
  oldestItem: number;
  newestItem: number;
}

class EnhancedCacheManager {
  private memoryCache: Map<string, CacheItem<any>> = new Map();
  private config: CacheConfig;
  private db: IDBDatabase | null = null;
  private cleanupTimer: NodeJS.Timeout | null = null;
  private stats = {
    hits: 0,
    misses: 0,
    totalRequests: 0,
  };

  constructor(config: Partial<CacheConfig> = {}) {
    this.config = {
      maxSize: config.maxSize || 1000,
      defaultTtl: config.defaultTtl || 300000, // 5分
      cleanupInterval: config.cleanupInterval || 60000, // 1分
      compressionEnabled: config.compressionEnabled !== false,
      persistenceEnabled: config.persistenceEnabled !== false,
    };

    this.initIndexedDB();
    this.startCleanup();
  }

  /**
   * IndexedDBの初期化
   */
  private async initIndexedDB(): Promise<void> {
    if (!this.config.persistenceEnabled) return;

    return new Promise((resolve, reject) => {
      const request = indexedDB.open('enhanced_cache_db', 1);
      
      request.onerror = () => {
        console.error('IndexedDB初期化エラー:', request.error);
        reject(request.error);
      };
      
      request.onsuccess = () => {
        this.db = request.result;
        console.info('IndexedDB初期化完了');
        resolve();
      };
      
      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        
        if (!db.objectStoreNames.contains('cache')) {
          const store = db.createObjectStore('cache', { keyPath: 'key' });
          store.createIndex('timestamp', 'timestamp', { unique: false });
          store.createIndex('tags', 'tags', { unique: false, multiEntry: true });
          store.createIndex('priority', 'priority', { unique: false });
        }
      };
    });
  }

  /**
   * データの取得
   */
  async get<T>(key: string): Promise<T | null> {
    this.stats.totalRequests++;
    
    // メモリキャッシュから取得
    const memoryItem = this.memoryCache.get(key);
    if (memoryItem && this.isValid(memoryItem)) {
      this.updateAccessStats(memoryItem);
      this.stats.hits++;
      return memoryItem.data;
    }

    // IndexedDBから取得
    if (this.db) {
      try {
        const dbItem = await this.getFromIndexedDB(key);
        if (dbItem && this.isValid(dbItem)) {
          // メモリキャッシュに追加
          this.memoryCache.set(key, dbItem);
          this.updateAccessStats(dbItem);
          this.stats.hits++;
          return dbItem.data;
        }
      } catch (error) {
        console.warn('IndexedDB取得エラー:', error);
      }
    }

    this.stats.misses++;
    return null;
  }

  /**
   * データの保存
   */
  async set<T>(
    key: string,
    data: T,
    options: {
      ttl?: number;
      tags?: string[];
      priority?: number;
    } = {}
  ): Promise<void> {
    const now = Date.now();
    const item: CacheItem<T> = {
      data,
      timestamp: now,
      ttl: options.ttl || this.config.defaultTtl,
      tags: options.tags || [],
      priority: options.priority || 0.5,
      accessCount: 0,
      lastAccessed: now,
    };

    // メモリキャッシュに保存
    this.memoryCache.set(key, item);

    // IndexedDBに保存
    if (this.db) {
      try {
        await this.saveToIndexedDB(key, item);
      } catch (error) {
        console.warn('IndexedDB保存エラー:', error);
      }
    }

    // サイズ制限チェック
    if (this.memoryCache.size > this.config.maxSize) {
      this.evictLeastUsed();
    }
  }

  /**
   * データの削除
   */
  async delete(key: string): Promise<void> {
    this.memoryCache.delete(key);
    
    if (this.db) {
      try {
        await this.deleteFromIndexedDB(key);
      } catch (error) {
        console.warn('IndexedDB削除エラー:', error);
      }
    }
  }

  /**
   * タグによる削除
   */
  async deleteByTags(tags: string[]): Promise<void> {
    const keysToDelete: string[] = [];
    
    for (const [key, item] of this.memoryCache.entries()) {
      if (tags.some(tag => item.tags.includes(tag))) {
        keysToDelete.push(key);
      }
    }
    
    for (const key of keysToDelete) {
      await this.delete(key);
    }
  }

  /**
   * キャッシュのクリア
   */
  async clear(): Promise<void> {
    this.memoryCache.clear();
    
    if (this.db) {
      try {
        await this.clearIndexedDB();
      } catch (error) {
        console.warn('IndexedDBクリアエラー:', error);
      }
    }
  }

  /**
   * 統計情報の取得
   */
  getStats(): CacheStats {
    const now = Date.now();
    const items = Array.from(this.memoryCache.values());
    
    return {
      totalItems: this.memoryCache.size,
      hitRate: this.stats.totalRequests > 0 ? this.stats.hits / this.stats.totalRequests : 0,
      missRate: this.stats.totalRequests > 0 ? this.stats.misses / this.stats.totalRequests : 0,
      totalSize: this.calculateTotalSize(),
      averageAccessTime: this.calculateAverageAccessTime(),
      oldestItem: items.length > 0 ? Math.min(...items.map(item => item.timestamp)) : now,
      newestItem: items.length > 0 ? Math.max(...items.map(item => item.timestamp)) : now,
    };
  }

  /**
   * アイテムの有効性チェック
   */
  private isValid(item: CacheItem<any>): boolean {
    const now = Date.now();
    return now - item.timestamp < item.ttl;
  }

  /**
   * アクセス統計の更新
   */
  private updateAccessStats(item: CacheItem<any>): void {
    item.accessCount++;
    item.lastAccessed = Date.now();
  }

  /**
   * 使用頻度の低いアイテムの削除
   */
  private evictLeastUsed(): void {
    const items = Array.from(this.memoryCache.entries());
    items.sort((a, b) => {
      const scoreA = a[1].priority * a[1].accessCount / (Date.now() - a[1].lastAccessed + 1);
      const scoreB = b[1].priority * b[1].accessCount / (Date.now() - b[1].lastAccessed + 1);
      return scoreA - scoreB;
    });

    const toDelete = Math.floor(this.config.maxSize * 0.1); // 10%削除
    for (let i = 0; i < toDelete && i < items.length; i++) {
      this.memoryCache.delete(items[i][0]);
    }
  }

  /**
   * 定期的なクリーンアップ
   */
  private startCleanup(): void {
    this.cleanupTimer = setInterval(() => {
      this.cleanup();
    }, this.config.cleanupInterval);
  }

  /**
   * クリーンアップの実行
   */
  private cleanup(): void {
    const now = Date.now();
    const expiredKeys: string[] = [];

    for (const [key, item] of this.memoryCache.entries()) {
      if (!this.isValid(item)) {
        expiredKeys.push(key);
      }
    }

    for (const key of expiredKeys) {
      this.memoryCache.delete(key);
    }

    if (expiredKeys.length > 0) {
      console.info(`キャッシュクリーンアップ完了: ${expiredKeys.length}件の期限切れアイテムを削除`);
    }
  }

  /**
   * IndexedDBからの取得
   */
  private async getFromIndexedDB(key: string): Promise<CacheItem<any> | null> {
    if (!this.db) return null;

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['cache'], 'readonly');
      const store = transaction.objectStore('cache');
      const request = store.get(key);

      request.onsuccess = () => {
        resolve(request.result);
      };

      request.onerror = () => {
        reject(request.error);
      };
    });
  }

  /**
   * IndexedDBへの保存
   */
  private async saveToIndexedDB(key: string, item: CacheItem<any>): Promise<void> {
    if (!this.db) return;

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['cache'], 'readwrite');
      const store = transaction.objectStore('cache');
      const request = store.put({ key, ...item });

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * IndexedDBからの削除
   */
  private async deleteFromIndexedDB(key: string): Promise<void> {
    if (!this.db) return;

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['cache'], 'readwrite');
      const store = transaction.objectStore('cache');
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
      const transaction = this.db!.transaction(['cache'], 'readwrite');
      const store = transaction.objectStore('cache');
      const request = store.clear();

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * 総サイズの計算
   */
  private calculateTotalSize(): number {
    let totalSize = 0;
    for (const item of this.memoryCache.values()) {
      totalSize += JSON.stringify(item).length;
    }
    return totalSize;
  }

  /**
   * 平均アクセス時間の計算
   */
  private calculateAverageAccessTime(): number {
    const items = Array.from(this.memoryCache.values());
    if (items.length === 0) return 0;
    
    const totalTime = items.reduce((sum, item) => sum + (Date.now() - item.lastAccessed), 0);
    return totalTime / items.length;
  }

  /**
   * システムの停止
   */
  stopCleanup(): void {
    if (this.cleanupTimer) {
      clearInterval(this.cleanupTimer);
      this.cleanupTimer = null;
    }
  }
}

// シングルトンインスタンス
const cacheManager = new EnhancedCacheManager({
  maxSize: 1000,
  defaultTtl: 300000, // 5分
  cleanupInterval: 60000, // 1分
  compressionEnabled: true,
  persistenceEnabled: true,
});

export default cacheManager;
export type { CacheConfig, CacheStats, CacheItem };
