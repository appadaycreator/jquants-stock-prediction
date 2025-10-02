/**
 * 段階的データ読み込みシステム
 * 大量データの段階的読み込みとメモリ最適化
 */

interface ProgressiveLoadingConfig {
  batchSize: number;
  maxConcurrent: number;
  enableMemoryOptimization: boolean;
  enableDataCompression: boolean;
  enableCaching: boolean;
  maxCacheSize: number; // MB
  retryAttempts: number;
  retryDelay: number; // ms
  memoryThreshold: number; // MB
}

interface LoadingProgress {
  loaded: number;
  total: number;
  percentage: number;
  currentBatch: number;
  totalBatches: number;
  memoryUsage: number;
  estimatedTimeRemaining: number; // ms
}

interface LoadingResult<T> {
  data: T[];
  metadata: {
    totalLoaded: number;
    loadingTime: number;
    memoryPeak: number;
    compressionRatio: number;
    batchesProcessed: number;
  };
}

class ProgressiveDataLoader {
  private config: ProgressiveLoadingConfig;
  private loadingQueue: Map<string, Promise<any>> = new Map();
  private cache: Map<string, any> = new Map();
  private memoryHistory: number[] = [];
  private compressionCache: Map<string, any> = new Map();

  constructor(config: ProgressiveLoadingConfig) {
    this.config = config;
    this.startMemoryMonitoring();
  }

  /**
   * メモリ監視の開始
   */
  private startMemoryMonitoring(): void {
    if (typeof window === "undefined") return;

    setInterval(() => {
      const memory = this.getCurrentMemoryUsage();
      this.memoryHistory.push(memory);

      // 履歴の制限（最新50件）
      if (this.memoryHistory.length > 50) {
        this.memoryHistory.shift();
      }

      // メモリ閾値のチェック
      if (memory > this.config.memoryThreshold) {
        console.warn(`メモリ使用量が閾値を超過: ${memory}MB > ${this.config.memoryThreshold}MB`);
        this.optimizeMemory();
      }
    }, 5000);
  }

  /**
   * 現在のメモリ使用量を取得
   */
  private getCurrentMemoryUsage(): number {
    if (!("memory" in performance)) return 0;
    
    const memory = (performance as any).memory;
    return Math.round(memory.usedJSHeapSize / 1024 / 1024);
  }

  /**
   * 段階的データ読み込み
   */
  async loadDataProgressively<T>(
    dataLoader: (offset: number, limit: number) => Promise<T[]>,
    options: {
      cacheKey?: string;
      onProgress?: (progress: LoadingProgress) => void;
      onBatchComplete?: (batch: T[], batchIndex: number) => void;
      onError?: (error: Error, batchIndex: number) => void;
    } = {},
  ): Promise<LoadingResult<T>> {
    const { cacheKey, onProgress, onBatchComplete, onError } = options;
    const startTime = performance.now();
    const allData: T[] = [];
    let offset = 0;
    let batchIndex = 0;
    let hasMore = true;
    let totalEstimated = 0;

    // キャッシュの確認
    if (cacheKey && this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (this.isCacheValid(cached)) {
        console.info("キャッシュからデータを取得:", {
          cacheKey,
          dataLength: cached.data.length,
          age: Date.now() - cached.timestamp,
        });
        return cached;
      }
    }

    // 最初のバッチで総数を推定
    try {
      const firstBatch = await this.loadBatchWithRetry(dataLoader, 0, this.config.batchSize);
      totalEstimated = firstBatch.length * 10; // 簡易的な推定
      allData.push(...firstBatch);
      batchIndex++;

      onBatchComplete?.(firstBatch, 0);
    } catch (error) {
      console.error("最初のバッチ読み込みエラー:", error);
      onError?.(error as Error, 0);
      throw error;
    }

    // 残りのバッチを並行読み込み
    while (hasMore) {
      const promises: Promise<T[]>[] = [];
      const batchOffsets: number[] = [];

      // 並行読み込みの準備
      for (let i = 0; i < this.config.maxConcurrent && hasMore; i++) {
        const currentOffset = offset;
        batchOffsets.push(currentOffset);
        
        promises.push(
          this.loadBatchWithRetry(dataLoader, currentOffset, this.config.batchSize)
        );
        
        offset += this.config.batchSize;
      }

      try {
        // 並行読み込みの実行
        const results = await Promise.all(promises);
        const batchData = results.flat();
        
        if (batchData.length === 0) {
          hasMore = false;
        } else {
          allData.push(...batchData);
          
          // バッチ完了の通知
          results.forEach((batch, index) => {
            onBatchComplete?.(batch, batchIndex + index);
          });
          
          batchIndex += results.length;

          // 進捗の通知
          const progress: LoadingProgress = {
            loaded: allData.length,
            total: totalEstimated,
            percentage: Math.min((allData.length / totalEstimated) * 100, 100),
            currentBatch: batchIndex,
            totalBatches: Math.ceil(totalEstimated / this.config.batchSize),
            memoryUsage: this.getCurrentMemoryUsage(),
            estimatedTimeRemaining: this.estimateTimeRemaining(startTime, allData.length, totalEstimated),
          };

          onProgress?.(progress);

          // メモリ最適化の実行
          if (this.config.enableMemoryOptimization) {
            await this.optimizeMemoryIfNeeded();
          }
        }
      } catch (error) {
        console.error("バッチ読み込みエラー:", error);
        onError?.(error as Error, batchIndex);
        
        // リトライの実装
        if (this.config.retryAttempts > 0) {
          console.info("リトライを実行:", {
            attempts: this.config.retryAttempts,
            delay: this.config.retryDelay,
          });
          
          await new Promise(resolve => setTimeout(resolve, this.config.retryDelay));
          this.config.retryAttempts--;
        } else {
          throw error;
        }
      }
    }

    const loadingTime = performance.now() - startTime;
    const memoryPeak = Math.max(...this.memoryHistory);
    const compressionRatio = this.calculateCompressionRatio(allData);

    const result: LoadingResult<T> = {
      data: allData,
      metadata: {
        totalLoaded: allData.length,
        loadingTime,
        memoryPeak,
        compressionRatio,
        batchesProcessed: batchIndex,
      },
    };

    // キャッシュへの保存
    if (cacheKey && this.config.enableCaching) {
      this.cache.set(cacheKey, {
        data: result,
        timestamp: Date.now(),
        metadata: result.metadata,
      });
    }

    console.info("段階的データ読み込み完了:", {
      totalLoaded: allData.length,
      loadingTime: `${loadingTime.toFixed(2)}ms`,
      memoryPeak: `${memoryPeak}MB`,
      compressionRatio: `${(compressionRatio * 100).toFixed(1)}%`,
      batchesProcessed: batchIndex,
    });

    return result;
  }

  /**
   * リトライ機能付きバッチ読み込み
   */
  private async loadBatchWithRetry<T>(
    dataLoader: (offset: number, limit: number) => Promise<T[]>,
    offset: number,
    limit: number,
    retryCount: number = 0,
  ): Promise<T[]> {
    try {
      return await dataLoader(offset, limit);
    } catch (error) {
      if (retryCount < 3) {
        console.warn(`バッチ読み込みリトライ ${retryCount + 1}/3:`, {
          offset,
          limit,
          error: (error as Error).message,
        });
        
        await new Promise(resolve => setTimeout(resolve, 1000 * (retryCount + 1)));
        return this.loadBatchWithRetry(dataLoader, offset, limit, retryCount + 1);
      }
      
      throw error;
    }
  }

  /**
   * 残り時間の推定
   */
  private estimateTimeRemaining(
    startTime: number,
    loaded: number,
    total: number,
  ): number {
    const elapsed = performance.now() - startTime;
    const rate = loaded / elapsed;
    const remaining = total - loaded;
    
    return remaining / rate;
  }

  /**
   * 圧縮率の計算
   */
  private calculateCompressionRatio(data: any[]): number {
    if (data.length === 0) return 1;
    
    const originalSize = JSON.stringify(data).length;
    const compressedSize = this.compressData(data).length;
    
    return compressedSize / originalSize;
  }

  /**
   * データの圧縮
   */
  private compressData(data: any[]): string {
    // 簡易的な圧縮（実際の実装ではLZ4等を使用）
    const json = JSON.stringify(data);
    return json;
  }

  /**
   * メモリ最適化の実行
   */
  private async optimizeMemoryIfNeeded(): Promise<void> {
    const currentMemory = this.getCurrentMemoryUsage();
    
    if (currentMemory > this.config.memoryThreshold * 0.8) {
      console.info("メモリ最適化を実行:", {
        current: `${currentMemory}MB`,
        threshold: `${this.config.memoryThreshold}MB`,
      });

      // ガベージコレクションの強制実行
      if ("gc" in window) {
        (window as any).gc();
      }

      // 古いキャッシュの削除
      this.cleanupOldCache();

      // 圧縮キャッシュの最適化
      this.optimizeCompressionCache();
    }
  }

  /**
   * 古いキャッシュのクリーンアップ
   */
  private cleanupOldCache(): void {
    const now = Date.now();
    const maxAge = 30 * 60 * 1000; // 30分

    for (const [key, value] of this.cache) {
      if (now - value.timestamp > maxAge) {
        this.cache.delete(key);
      }
    }

    console.debug("古いキャッシュをクリーンアップ:", {
      remaining: this.cache.size,
    });
  }

  /**
   * 圧縮キャッシュの最適化
   */
  private optimizeCompressionCache(): void {
    if (this.compressionCache.size > 100) {
      const entries = Array.from(this.compressionCache.entries());
      entries.sort((a, b) => a[1].timestamp - b[1].timestamp);
      
      const toDelete = Math.floor(entries.length * 0.3);
      for (let i = 0; i < toDelete; i++) {
        this.compressionCache.delete(entries[i][0]);
      }
    }
  }

  /**
   * キャッシュの有効性チェック
   */
  private isCacheValid(cached: any): boolean {
    const maxAge = 30 * 60 * 1000; // 30分
    return Date.now() - cached.timestamp < maxAge;
  }

  /**
   * データの段階的更新
   */
  async updateDataProgressively<T>(
    dataUpdater: (offset: number, limit: number) => Promise<T[]>,
    existingData: T[],
    options: {
      updateStrategy?: "append" | "replace" | "merge";
      onUpdate?: (updatedData: T[], updateIndex: number) => void;
    } = {},
  ): Promise<T[]> {
    const { updateStrategy = "append", onUpdate } = options;
    const updatedData = [...existingData];
    let offset = 0;
    let updateIndex = 0;

    while (true) {
      try {
        const batch = await dataUpdater(offset, this.config.batchSize);
        
        if (batch.length === 0) break;

        switch (updateStrategy) {
          case "append":
            updatedData.push(...batch);
            break;
          case "replace":
            if (updateIndex === 0) {
              updatedData.splice(0, updatedData.length, ...batch);
            } else {
              updatedData.push(...batch);
            }
            break;
          case "merge":
            // 重複を避けてマージ
            const newItems = batch.filter(item => 
              !updatedData.some(existing => 
                JSON.stringify(existing) === JSON.stringify(item)
              )
            );
            updatedData.push(...newItems);
            break;
        }

        onUpdate?.(updatedData, updateIndex);
        offset += this.config.batchSize;
        updateIndex++;

        // メモリ最適化
        if (this.config.enableMemoryOptimization) {
          await this.optimizeMemoryIfNeeded();
        }
      } catch (error) {
        console.error("データ更新エラー:", error);
        break;
      }
    }

    return updatedData;
  }

  /**
   * データの並行読み込み
   */
  async loadDataConcurrently<T>(
    dataLoaders: Array<(offset: number, limit: number) => Promise<T[]>>,
    options: {
      onProgress?: (progress: { completed: number; total: number }) => void;
      onError?: (error: Error, loaderIndex: number) => void;
    } = {},
  ): Promise<T[][]> {
    const { onProgress, onError } = options;
    const results: T[][] = [];
    let completed = 0;

    const promises = dataLoaders.map(async (loader, index) => {
      try {
        const data = await loader(0, this.config.batchSize);
        results[index] = data;
        completed++;
        onProgress?.({ completed, total: dataLoaders.length });
        return data;
      } catch (error) {
        console.error(`データローダー ${index} エラー:`, error);
        onError?.(error as Error, index);
        return [];
      }
    });

    await Promise.all(promises);
    return results;
  }

  /**
   * パフォーマンスレポートの生成
   */
  generatePerformanceReport(): {
    memoryUsage: {
      current: number;
      peak: number;
      average: number;
    };
    cache: {
      size: number;
      hitRate: number;
    };
    loading: {
      totalBatches: number;
      averageBatchTime: number;
      compressionRatio: number;
    };
    recommendations: string[];
  } {
    const currentMemory = this.getCurrentMemoryUsage();
    const peakMemory = Math.max(...this.memoryHistory);
    const averageMemory = this.memoryHistory.reduce((a, b) => a + b, 0) / this.memoryHistory.length;

    const recommendations: string[] = [];
    
    if (peakMemory > this.config.memoryThreshold) {
      recommendations.push("メモリ使用量のピークが閾値を超えています。バッチサイズの削減を推奨します。");
    }
    
    if (this.cache.size > 100) {
      recommendations.push("キャッシュサイズが大きすぎます。古いデータの削除を推奨します。");
    }

    return {
      memoryUsage: {
        current: currentMemory,
        peak: peakMemory,
        average: averageMemory,
      },
      cache: {
        size: this.cache.size,
        hitRate: 0, // 実際の実装では計算
      },
      loading: {
        totalBatches: 0, // 実際の実装では追跡
        averageBatchTime: 0, // 実際の実装では追跡
        compressionRatio: 0, // 実際の実装では計算
      },
      recommendations,
    };
  }

  /**
   * クリーンアップ
   */
  cleanup(): void {
    this.loadingQueue.clear();
    this.cache.clear();
    this.compressionCache.clear();
    this.memoryHistory = [];
  }
}

// デフォルト設定
const defaultConfig: ProgressiveLoadingConfig = {
  batchSize: 100,
  maxConcurrent: 3,
  enableMemoryOptimization: true,
  enableDataCompression: true,
  enableCaching: true,
  maxCacheSize: 50, // 50MB
  retryAttempts: 3,
  retryDelay: 1000,
  memoryThreshold: 100, // 100MB
};

export const progressiveDataLoader = new ProgressiveDataLoader(defaultConfig);
export default ProgressiveDataLoader;
export type { ProgressiveLoadingConfig, LoadingProgress, LoadingResult };
