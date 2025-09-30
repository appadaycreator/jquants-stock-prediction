/**
 * 最適化されたキャッシュ管理システム
 * インテリジェントキャッシュ、差分更新、自動無効化機能
 */

interface CacheConfig {
  maxSize: number; // MB
  ttl: number; // ミリ秒
  compressionEnabled: boolean;
  autoCleanup: boolean;
  cleanupInterval: number; // ミリ秒
  priorityWeights: {
    frequency: number;
    recency: number;
    size: number;
  };
}

interface CacheEntry<T = any> {
  key: string;
  data: T;
  metadata: {
    createdAt: string;
    lastAccessed: string;
    accessCount: number;
    size: number;
    ttl: number;
    priority: number;
    tags: string[];
  };
}

interface CacheStats {
  totalEntries: number;
  totalSize: number;
  hitRate: number;
  missRate: number;
  evictionCount: number;
  compressionRatio: number;
  averageAccessTime: number;
}

interface CacheStrategy {
  type: 'lru' | 'lfu' | 'fifo' | 'adaptive';
  maxAge: number;
  maxSize: number;
  compressionThreshold: number;
}

class OptimizedCacheManager {
  private db: IDBDatabase | null = null;
  private readonly DB_NAME = 'optimized_cache';
  private readonly DB_VERSION = 3;
  private readonly STORE_NAME = 'cache_entries';
  private readonly STATS_STORE = 'cache_stats';

  private config: CacheConfig;
  private stats: CacheStats;
  private cleanupInterval: NodeJS.Timeout | null = null;
  private accessTimes: Map<string, number> = new Map();

  constructor(config: Partial<CacheConfig> = {}) {
    this.config = {
      maxSize: config.maxSize || 100, // 100MB
      ttl: config.ttl || 24 * 60 * 60 * 1000, // 24時間
      compressionEnabled: config.compressionEnabled !== false,
      autoCleanup: config.autoCleanup !== false,
      cleanupInterval: config.cleanupInterval || 60 * 60 * 1000, // 1時間
      priorityWeights: {
        frequency: config.priorityWeights?.frequency || 0.4,
        recency: config.priorityWeights?.recency || 0.3,
        size: config.priorityWeights?.size || 0.3,
      }
    };

    this.stats = {
      totalEntries: 0,
      totalSize: 0,
      hitRate: 0,
      missRate: 0,
      evictionCount: 0,
      compressionRatio: 0,
      averageAccessTime: 0
    };

    this.initDB();
  }

  /**
   * IndexedDBの初期化
   */
  private async initDB(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.DB_NAME, this.DB_VERSION);
      
      request.onerror = () => {
        console.error('キャッシュDB初期化エラー:', request.error);
        reject(request.error);
      };
      
      request.onsuccess = () => {
        this.db = request.result;
        console.info('最適化キャッシュDB初期化完了');
        this.loadStats();
        if (this.config.autoCleanup) {
          this.startCleanup();
        }
        resolve();
      };
      
      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        
        // キャッシュエントリストア
        if (!db.objectStoreNames.contains(this.STORE_NAME)) {
          const store = db.createObjectStore(this.STORE_NAME, { keyPath: 'key' });
          store.createIndex('lastAccessed', 'metadata.lastAccessed', { unique: false });
          store.createIndex('accessCount', 'metadata.accessCount', { unique: false });
          store.createIndex('size', 'metadata.size', { unique: false });
          store.createIndex('priority', 'metadata.priority', { unique: false });
          store.createIndex('tags', 'metadata.tags', { unique: false, multiEntry: true });
        }
        
        // 統計ストア
        if (!db.objectStoreNames.contains(this.STATS_STORE)) {
          db.createObjectStore(this.STATS_STORE, { keyPath: 'id' });
        }
      };
    });
  }

  /**
   * データの取得（最適化版）
   */
  async get<T>(key: string): Promise<T | null> {
    if (!this.db) {
      return null;
    }

    const startTime = performance.now();

    try {
      const entry = await this.getEntry(key);
      if (!entry) {
        this.updateStats('miss');
        return null;
      }

      // TTLチェック
      const now = Date.now();
      const entryAge = now - new Date(entry.metadata.createdAt).getTime();
      if (entryAge > entry.metadata.ttl) {
        await this.delete(key);
        this.updateStats('miss');
        return null;
      }

      // アクセス情報の更新
      entry.metadata.lastAccessed = new Date().toISOString();
      entry.metadata.accessCount++;
      await this.updateEntry(entry);

      this.updateStats('hit', performance.now() - startTime);
      return entry.data;
    } catch (error) {
      console.error('キャッシュ取得エラー:', error);
      this.updateStats('miss');
      return null;
    }
  }

  /**
   * データの保存（最適化版）
   */
  async set<T>(
    key: string, 
    data: T, 
    options: {
      ttl?: number;
      tags?: string[];
      priority?: number;
      compress?: boolean;
    } = {}
  ): Promise<void> {
    if (!this.db) {
      return;
    }

    try {
      const startTime = performance.now();
      const size = this.calculateSize(data);
      const shouldCompress = options.compress !== false && this.config.compressionEnabled && size > 1024;

      let processedData = data;
      if (shouldCompress) {
        processedData = await this.compress(data);
      }

      const entry: CacheEntry<T> = {
        key,
        data: processedData,
        metadata: {
          createdAt: new Date().toISOString(),
          lastAccessed: new Date().toISOString(),
          accessCount: 0,
          size: shouldCompress ? this.calculateSize(processedData) : size,
          ttl: options.ttl || this.config.ttl,
          priority: options.priority || this.calculatePriority(key, size),
          tags: options.tags || []
        }
      };

      // 容量チェック
      await this.ensureCapacity(entry.metadata.size);

      await this.saveEntry(entry);
      this.updateStats('set', performance.now() - startTime);
    } catch (error) {
      console.error('キャッシュ保存エラー:', error);
    }
  }

  /**
   * データの削除
   */
  async delete(key: string): Promise<void> {
    if (!this.db) {
      return;
    }

    try {
      const transaction = this.db.transaction([this.STORE_NAME], 'readwrite');
      const store = transaction.objectStore(this.STORE_NAME);
      await store.delete(key);
    } catch (error) {
      console.error('キャッシュ削除エラー:', error);
    }
  }

  /**
   * タグによる一括削除
   */
  async deleteByTags(tags: string[]): Promise<number> {
    if (!this.db) {
      return 0;
    }

    try {
      const entries = await this.getEntriesByTags(tags);
      let deletedCount = 0;

      for (const entry of entries) {
        await this.delete(entry.key);
        deletedCount++;
      }

      return deletedCount;
    } catch (error) {
      console.error('タグ別削除エラー:', error);
      return 0;
    }
  }

  /**
   * 差分更新の実行
   */
  async incrementalUpdate<T>(
    key: string,
    newData: T,
    mergeStrategy: 'replace' | 'merge' | 'append' = 'merge'
  ): Promise<void> {
    try {
      const existingData = await this.get<T>(key);
      if (!existingData) {
        await this.set(key, newData);
        return;
      }

      let mergedData: T;
      switch (mergeStrategy) {
        case 'replace':
          mergedData = newData;
          break;
        case 'merge':
          mergedData = this.mergeData(existingData, newData);
          break;
        case 'append':
          mergedData = this.appendData(existingData, newData);
          break;
        default:
          mergedData = newData;
      }

      await this.set(key, mergedData);
    } catch (error) {
      console.error('差分更新エラー:', error);
    }
  }

  /**
   * データのマージ
   */
  private mergeData<T>(existing: T, newData: T): T {
    if (Array.isArray(existing) && Array.isArray(newData)) {
      return [...existing, ...newData] as T;
    }

    if (typeof existing === 'object' && typeof newData === 'object' && existing !== null && newData !== null) {
      return { ...existing, ...newData } as T;
    }

    return newData;
  }

  /**
   * データの追加
   */
  private appendData<T>(existing: T, newData: T): T {
    if (Array.isArray(existing) && Array.isArray(newData)) {
      return [...existing, ...newData] as T;
    }

    return newData;
  }

  /**
   * 容量の確保
   */
  private async ensureCapacity(requiredSize: number): Promise<void> {
    const currentSize = await this.getTotalSize();
    const maxSizeBytes = this.config.maxSize * 1024 * 1024;

    if (currentSize + requiredSize > maxSizeBytes) {
      const toFree = (currentSize + requiredSize) - maxSizeBytes;
      await this.evictEntries(toFree);
    }
  }

  /**
   * エントリの削除（LRU + LFU + サイズベース）
   */
  private async evictEntries(sizeToFree: number): Promise<void> {
    if (!this.db) {
      return;
    }

    try {
      const entries = await this.getAllEntries();
      const sortedEntries = this.sortEntriesForEviction(entries);

      let freedSize = 0;
      for (const entry of sortedEntries) {
        if (freedSize >= sizeToFree) break;

        await this.delete(entry.key);
        freedSize += entry.metadata.size;
        this.stats.evictionCount++;
      }

      console.info('キャッシュエントリを削除しました', { 
        freedSize, 
        evictedCount: this.stats.evictionCount 
      });
    } catch (error) {
      console.error('エントリ削除エラー:', error);
    }
  }

  /**
   * 削除用エントリのソート
   */
  private sortEntriesForEviction(entries: CacheEntry[]): CacheEntry[] {
    return entries.sort((a, b) => {
      const scoreA = this.calculateEvictionScore(a);
      const scoreB = this.calculateEvictionScore(b);
      return scoreA - scoreB; // 低いスコアから削除
    });
  }

  /**
   * 削除スコアの計算
   */
  private calculateEvictionScore(entry: CacheEntry): number {
    const now = Date.now();
    const age = now - new Date(entry.metadata.createdAt).getTime();
    const lastAccess = now - new Date(entry.metadata.lastAccessed).getTime();

    // アクセス頻度（低いほど削除対象）
    const frequencyScore = 1 / (entry.metadata.accessCount + 1);
    
    // 最終アクセス時間（古いほど削除対象）
    const recencyScore = lastAccess / (24 * 60 * 60 * 1000); // 日数
    
    // サイズ（大きいほど削除対象）
    const sizeScore = entry.metadata.size / (1024 * 1024); // MB

    return (
      frequencyScore * this.config.priorityWeights.frequency +
      recencyScore * this.config.priorityWeights.recency +
      sizeScore * this.config.priorityWeights.size
    );
  }

  /**
   * データの圧縮
   */
  private async compress<T>(data: T): Promise<T> {
    try {
      const jsonString = JSON.stringify(data);
      const compressed = await this.compressString(jsonString);
      return compressed as T;
    } catch (error) {
      console.warn('データ圧縮に失敗しました:', error);
      return data;
    }
  }

  /**
   * 文字列の圧縮
   */
  private async compressString(str: string): Promise<string> {
    // 簡易的な圧縮（実際の実装ではLZ4やBrotliを使用）
    return btoa(str);
  }

  /**
   * データの解凍
   */
  private async decompress<T>(compressedData: T): Promise<T> {
    try {
      const jsonString = atob(compressedData as string);
      return JSON.parse(jsonString);
    } catch (error) {
      console.warn('データ解凍に失敗しました:', error);
      return compressedData;
    }
  }

  /**
   * サイズの計算
   */
  private calculateSize(data: any): number {
    return new Blob([JSON.stringify(data)]).size;
  }

  /**
   * 優先度の計算
   */
  private calculatePriority(key: string, size: number): number {
    // キーの重要度に基づく優先度計算
    let priority = 0.5; // デフォルト

    if (key.includes('critical')) priority = 1.0;
    else if (key.includes('important')) priority = 0.8;
    else if (key.includes('normal')) priority = 0.5;
    else if (key.includes('low')) priority = 0.2;

    // サイズによる調整
    if (size > 1024 * 1024) priority *= 0.8; // 1MB以上は優先度を下げる
    else if (size < 1024) priority *= 1.2; // 1KB未満は優先度を上げる

    return Math.max(0, Math.min(1, priority));
  }

  /**
   * 統計の更新
   */
  private updateStats(type: 'hit' | 'miss' | 'set', accessTime?: number): void {
    const total = this.stats.hitRate + this.stats.missRate;
    
    if (type === 'hit') {
      this.stats.hitRate++;
    } else if (type === 'miss') {
      this.stats.missRate++;
    }

    if (accessTime !== undefined) {
      const totalTime = this.stats.averageAccessTime * (this.stats.hitRate + this.stats.missRate - 1) + accessTime;
      this.stats.averageAccessTime = total > 0 ? totalTime / (this.stats.hitRate + this.stats.missRate) : 0;
    }

    // 統計の保存
    this.saveStats();
  }

  /**
   * 統計の取得
   */
  getStats(): CacheStats {
    return { ...this.stats };
  }

  /**
   * 統計の保存
   */
  private async saveStats(): Promise<void> {
    if (!this.db) return;

    try {
      const transaction = this.db.transaction([this.STATS_STORE], 'readwrite');
      const store = transaction.objectStore(this.STATS_STORE);
      await store.put({ id: 'current', ...this.stats });
    } catch (error) {
      console.error('統計保存エラー:', error);
    }
  }

  /**
   * 統計の読み込み
   */
  private async loadStats(): Promise<void> {
    if (!this.db) return;

    try {
      const transaction = this.db.transaction([this.STATS_STORE], 'readonly');
      const store = transaction.objectStore(this.STATS_STORE);
      const request = store.get('current');

      request.onsuccess = () => {
        if (request.result) {
          this.stats = { ...this.stats, ...request.result };
        }
      };
    } catch (error) {
      console.error('統計読み込みエラー:', error);
    }
  }

  /**
   * 自動クリーンアップの開始
   */
  private startCleanup(): void {
    this.cleanupInterval = setInterval(() => {
      this.performCleanup();
    }, this.config.cleanupInterval);
  }

  /**
   * クリーンアップの実行
   */
  private async performCleanup(): Promise<void> {
    try {
      const expiredEntries = await this.getExpiredEntries();
      let cleanedCount = 0;

      for (const entry of expiredEntries) {
        await this.delete(entry.key);
        cleanedCount++;
      }

      if (cleanedCount > 0) {
        console.info('期限切れキャッシュをクリーンアップしました', { cleanedCount });
      }
    } catch (error) {
      console.error('クリーンアップエラー:', error);
    }
  }

  /**
   * 期限切れエントリの取得
   */
  private async getExpiredEntries(): Promise<CacheEntry[]> {
    if (!this.db) return [];

    try {
      const allEntries = await this.getAllEntries();
      const now = Date.now();

      return allEntries.filter(entry => {
        const age = now - new Date(entry.metadata.createdAt).getTime();
        return age > entry.metadata.ttl;
      });
    } catch (error) {
      console.error('期限切れエントリ取得エラー:', error);
      return [];
    }
  }

  /**
   * 全エントリの取得
   */
  private async getAllEntries(): Promise<CacheEntry[]> {
    if (!this.db) return [];

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.STORE_NAME], 'readonly');
      const store = transaction.objectStore(this.STORE_NAME);
      const request = store.getAll();

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * タグ別エントリの取得
   */
  private async getEntriesByTags(tags: string[]): Promise<CacheEntry[]> {
    if (!this.db) return [];

    try {
      const allEntries = await this.getAllEntries();
      return allEntries.filter(entry => 
        tags.some(tag => entry.metadata.tags.includes(tag))
      );
    } catch (error) {
      console.error('タグ別エントリ取得エラー:', error);
      return [];
    }
  }

  /**
   * エントリの取得
   */
  private async getEntry(key: string): Promise<CacheEntry | null> {
    if (!this.db) return null;

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.STORE_NAME], 'readonly');
      const store = transaction.objectStore(this.STORE_NAME);
      const request = store.get(key);

      request.onsuccess = () => resolve(request.result || null);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * エントリの保存
   */
  private async saveEntry(entry: CacheEntry): Promise<void> {
    if (!this.db) return;

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.STORE_NAME], 'readwrite');
      const store = transaction.objectStore(this.STORE_NAME);
      const request = store.put(entry);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * エントリの更新
   */
  private async updateEntry(entry: CacheEntry): Promise<void> {
    await this.saveEntry(entry);
  }

  /**
   * 総サイズの取得
   */
  private async getTotalSize(): Promise<number> {
    if (!this.db) return 0;

    try {
      const entries = await this.getAllEntries();
      return entries.reduce((total, entry) => total + entry.metadata.size, 0);
    } catch (error) {
      console.error('総サイズ取得エラー:', error);
      return 0;
    }
  }

  /**
   * キャッシュのクリア
   */
  async clear(): Promise<void> {
    if (!this.db) return;

    try {
      const transaction = this.db.transaction([this.STORE_NAME], 'readwrite');
      const store = transaction.objectStore(this.STORE_NAME);
      await store.clear();

      this.stats = {
        totalEntries: 0,
        totalSize: 0,
        hitRate: 0,
        missRate: 0,
        evictionCount: 0,
        compressionRatio: 0,
        averageAccessTime: 0
      };

      await this.saveStats();
      console.info('キャッシュをクリアしました');
    } catch (error) {
      console.error('キャッシュクリアエラー:', error);
    }
  }

  /**
   * 設定の更新
   */
  updateConfig(newConfig: Partial<CacheConfig>): void {
    this.config = { ...this.config, ...newConfig };
    console.info('キャッシュ設定を更新しました', this.config);
  }

  /**
   * クリーンアップの停止
   */
  stopCleanup(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
      this.cleanupInterval = null;
    }
  }
}

export default OptimizedCacheManager;
export type { CacheConfig, CacheEntry, CacheStats, CacheStrategy };
