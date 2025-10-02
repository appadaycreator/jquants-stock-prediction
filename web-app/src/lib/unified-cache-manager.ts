/**
 * 統一されたキャッシュマネージャー
 * アプリケーション全体で使用されるキャッシュ機能を提供
 */

export interface CacheOptions {
  ttl?: number; // Time to live in milliseconds
  tags?: string[]; // Cache tags for invalidation
  priority?: number; // Cache priority (0-1)
  maxSize?: number; // Maximum cache size in bytes
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

  constructor() {
    this.startCleanup();
  }

  // キャッシュからデータを取得
  async get<T>(key: string): Promise<T | null> {
    const entry = this.cache.get(key);
    
    if (!entry) {
      return null;
    }

    // TTLチェック
    if (this.isExpired(entry)) {
      this.delete(key);
      return null;
    }

    // アクセス時間を更新
    entry.timestamp = Date.now();
    return entry.data as T;
  }

  // キャッシュにデータを保存
  async set<T>(key: string, data: T, options: CacheOptions = {}): Promise<void> {
    const {
      ttl = 300000, // 5分デフォルト
      tags = [],
      priority = 0.5,
      maxSize = 1024 * 1024, // 1MBデフォルト
    } = options;

    const serializedData = JSON.stringify(data);
    const size = new Blob([serializedData]).size;

    if (size > maxSize) {
      console.warn(`Cache entry ${key} exceeds maximum size limit`);
      return;
    }

    // サイズ制限チェック
    if (this.currentSize + size > this.maxSize) {
      await this.evictLeastPriority();
    }

    const entry: CacheEntry<T> = {
      data,
      timestamp: Date.now(),
      ttl,
      tags,
      priority,
      size,
    };

    this.cache.set(key, entry);
    this.currentSize += size;
  }

  // キャッシュから削除
  async delete(key: string): Promise<boolean> {
    const entry = this.cache.get(key);
    if (entry) {
      this.currentSize -= entry.size;
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
  } {
    return {
      size: this.currentSize,
      count: this.cache.size,
      maxSize: this.maxSize,
      hitRate: 0, // TODO: 実装
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
