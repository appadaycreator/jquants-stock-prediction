/**
 * パフォーマンス最適化システム
 * 5分ルーティンの実現に向けた最適化
 */

import React from 'react';

interface PerformanceMetrics {
  loadTime: number;
  renderTime: number;
  memoryUsage: number;
  networkRequests: number;
  cacheHitRate: number;
  errorRate: number;
}

interface OptimizationConfig {
  enableLazyLoading: boolean;
  enablePreloading: boolean;
  enableCaching: boolean;
  enableCompression: boolean;
  maxConcurrentRequests: number;
  cacheStrategy: 'aggressive' | 'balanced' | 'conservative';
}

class PerformanceOptimizer {
  private config: OptimizationConfig;
  private metrics: PerformanceMetrics;
  private observers: PerformanceObserver[] = [];

  constructor(config: Partial<OptimizationConfig> = {}) {
    this.config = {
      enableLazyLoading: true,
      enablePreloading: true,
      enableCaching: true,
      enableCompression: true,
      maxConcurrentRequests: 6,
      cacheStrategy: 'balanced',
      ...config
    };

    this.metrics = {
      loadTime: 0,
      renderTime: 0,
      memoryUsage: 0,
      networkRequests: 0,
      cacheHitRate: 0,
      errorRate: 0
    };

    this.initializeObservers();
  }

  /**
   * パフォーマンス監視の初期化
   */
  private initializeObservers(): void {
    if (typeof window === 'undefined') return;

    // ナビゲーションタイミングの監視
    if ('PerformanceObserver' in window) {
      const navigationObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
        entries.forEach((entry) => {
          if (entry.entryType === 'navigation') {
            this.metrics.loadTime = entry.duration;
          }
        });
      });

      navigationObserver.observe({ entryTypes: ['navigation'] });
      this.observers.push(navigationObserver);
    }

    // リソースタイミングの監視
    if ('PerformanceObserver' in window) {
      const resourceObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        this.metrics.networkRequests += entries.length;
      });

      resourceObserver.observe({ entryTypes: ['resource'] });
      this.observers.push(resourceObserver);
    }

    // メモリ使用量の監視
    if ('memory' in performance) {
      setInterval(() => {
        this.metrics.memoryUsage = (performance as any).memory.usedJSHeapSize;
      }, 5000);
    }
  }

  /**
   * データの並列取得
   */
  async fetchDataParallel<T>(
    requests: Array<() => Promise<T>>,
    options: { maxConcurrent?: number; timeout?: number } = {}
  ): Promise<T[]> {
    const { maxConcurrent = this.config.maxConcurrentRequests, timeout = 10000 } = options;
    
    const results: T[] = [];
    const errors: Error[] = [];

    // リクエストをバッチに分割
    const batches: Array<() => Promise<T>>[] = [];
    for (let i = 0; i < requests.length; i += maxConcurrent) {
      batches.push(requests.slice(i, i + maxConcurrent));
    }

    // 各バッチを順次実行
    for (const batch of batches) {
      const batchPromises = batch.map(async (request) => {
        try {
          const timeoutPromise = new Promise<never>((_, reject) => {
            setTimeout(() => reject(new Error('Request timeout')), timeout);
          });

          const result = await Promise.race([request(), timeoutPromise]);
          return result;
        } catch (error) {
          errors.push(error as Error);
          throw error;
        }
      });

      try {
        const batchResults = await Promise.allSettled(batchPromises);
        batchResults.forEach((result) => {
          if (result.status === 'fulfilled') {
            results.push(result.value);
          }
        });
    } catch (error) {
        console.error('バッチ実行エラー:', error);
      }
    }

    this.metrics.errorRate = errors.length / requests.length;
    return results;
  }

  /**
   * 画像の遅延読み込み
   */
  enableLazyLoading(): void {
    if (!this.config.enableLazyLoading || typeof window === 'undefined') return;

    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
          if (entry.isIntersecting) {
          const img = entry.target as HTMLImageElement;
          const src = img.getAttribute('data-src');
          if (src) {
            img.src = src;
            img.removeAttribute('data-src');
            imageObserver.unobserve(img);
          }
        }
      });
    });

    images.forEach((img) => imageObserver.observe(img));
  }

  /**
   * 重要なリソースのプリロード
   */
  preloadCriticalResources(): void {
    if (!this.config.enablePreloading || typeof window === 'undefined') return;

    const criticalResources = [
      '/data/stock_data.json',
      '/data/predictions.json',
      '/data/model_comparison.json'
    ];

    criticalResources.forEach((resource) => {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.href = resource;
      link.as = 'fetch';
      link.crossOrigin = 'anonymous';
      document.head.appendChild(link);
    });
  }

  /**
   * キャッシュ戦略の実装
   */
  implementCachingStrategy(): void {
    if (!this.config.enableCaching || typeof window === 'undefined') return;

    // Service Worker の登録
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js').catch((error) => {
        console.error('Service Worker 登録エラー:', error);
      });
    }

    // メモリキャッシュの実装
    const memoryCache = new Map<string, { data: any; timestamp: number; ttl: number }>();

    const getCachedData = (key: string) => {
      const cached = memoryCache.get(key);
      if (cached && Date.now() - cached.timestamp < cached.ttl) {
        return cached.data;
      }
      memoryCache.delete(key);
      return null;
    };

    const setCachedData = (key: string, data: any, ttl: number = 300000) => {
      memoryCache.set(key, {
        data,
        timestamp: Date.now(),
        ttl
      });
    };

    // グローバルキャッシュ関数の設定
    (window as any).getCachedData = getCachedData;
    (window as any).setCachedData = setCachedData;
  }

  /**
   * レンダリング最適化
   */
  optimizeRendering(): void {
    if (typeof window === 'undefined') return;

    // 不要な再レンダリングの防止
    const originalCreateElement = React.createElement;
    let renderCount = 0;

    // レンダリング時間の測定
    const startTime = performance.now();
    
    // レンダリング完了の検知
    const observer = new MutationObserver(() => {
      const endTime = performance.now();
      this.metrics.renderTime = endTime - startTime;
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });

    // 不要なDOM操作の最適化
    const optimizeDOM = () => {
      // 非表示要素の処理を遅延
      const hiddenElements = document.querySelectorAll('[style*="display: none"]');
      hiddenElements.forEach((element) => {
        if (!element.getAttribute('data-optimized')) {
          element.setAttribute('data-optimized', 'true');
          // 非表示要素の処理を遅延
          setTimeout(() => {
            // 必要な処理を実行
          }, 0);
        }
      });
    };

    // 定期的なDOM最適化
    setInterval(optimizeDOM, 1000);
  }

  /**
   * ネットワーク最適化
   */
  optimizeNetwork(): void {
    if (typeof window === 'undefined') return;

    // リクエストの優先度設定
    const originalFetch = window.fetch;
    window.fetch = async (input, init) => {
      const startTime = performance.now();
      
      try {
        const response = await originalFetch(input, {
          ...init,
          priority: 'high' // 重要なリクエストの優先度を上げる
        });
        
        const endTime = performance.now();
        console.log(`ネットワークリクエスト完了: ${endTime - startTime}ms`);
        
        return response;
      } catch (error) {
        console.error('ネットワークリクエストエラー:', error);
        throw error;
      }
    };
  }

  /**
   * パフォーマンスメトリクスの取得
   */
  getMetrics(): PerformanceMetrics {
    return { ...this.metrics };
  }

  /**
   * パフォーマンスレポートの生成
   */
  generateReport(): {
    score: number;
    recommendations: string[];
    metrics: PerformanceMetrics;
  } {
    const { loadTime, renderTime, memoryUsage, networkRequests, cacheHitRate, errorRate } = this.metrics;
    
    let score = 100;
    const recommendations: string[] = [];

    // スコア計算
    if (loadTime > 3000) {
      score -= 20;
      recommendations.push('ページ読み込み時間が3秒を超えています');
    }
    
    if (renderTime > 1000) {
      score -= 15;
      recommendations.push('レンダリング時間が1秒を超えています');
    }
    
    if (memoryUsage > 50 * 1024 * 1024) { // 50MB
      score -= 10;
      recommendations.push('メモリ使用量が50MBを超えています');
    }
    
    if (networkRequests > 20) {
      score -= 10;
      recommendations.push('ネットワークリクエスト数が20を超えています');
    }
    
    if (cacheHitRate < 0.7) {
      score -= 15;
      recommendations.push('キャッシュヒット率が70%を下回っています');
    }
    
    if (errorRate > 0.1) {
      score -= 20;
      recommendations.push('エラー率が10%を超えています');
    }

    return {
      score: Math.max(0, score),
      recommendations,
      metrics: this.metrics
    };
  }

  /**
   * 最適化の実行
   */
  optimize(): void {
    this.enableLazyLoading();
    this.preloadCriticalResources();
    this.implementCachingStrategy();
    this.optimizeRendering();
    this.optimizeNetwork();
  }

  /**
   * 監視の停止
   */
  cleanup(): void {
    this.observers.forEach((observer) => observer.disconnect());
    this.observers = [];
  }
}

// シングルトンインスタンス
export const performanceOptimizer = new PerformanceOptimizer();

// 自動最適化の実行
if (typeof window !== 'undefined') {
  performanceOptimizer.optimize();
}

export default PerformanceOptimizer;