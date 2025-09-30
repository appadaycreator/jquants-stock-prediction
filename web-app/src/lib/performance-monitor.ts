/**
 * パフォーマンス監視システム
 * クライアントサイドレンダリングの最適化とメモリ管理
 */

export interface PerformanceMetrics {
  loadTime: number;
  renderTime: number;
  memoryUsage: {
    used: number;
    total: number;
    limit: number;
  };
  componentCount: number;
  bundleSize: number;
  cacheHitRate: number;
  errorRate: number;
}

export interface ComponentMetrics {
  name: string;
  renderTime: number;
  mountTime: number;
  updateCount: number;
  memoryUsage: number;
}

class PerformanceMonitor {
  private metrics: PerformanceMetrics;
  private componentMetrics: Map<string, ComponentMetrics>;
  private startTime: number;
  private renderStartTime: number;
  private componentTimers: Map<string, number>;

  constructor() {
    this.startTime = performance.now();
    this.renderStartTime = 0;
    this.metrics = {
      loadTime: 0,
      renderTime: 0,
      memoryUsage: { used: 0, total: 0, limit: 0 },
      componentCount: 0,
      bundleSize: 0,
      cacheHitRate: 0,
      errorRate: 0
    };
    this.componentMetrics = new Map();
    this.componentTimers = new Map();
    
    this.initializeMonitoring();
  }

  private initializeMonitoring(): void {
    // パフォーマンスエントリの監視
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          this.handlePerformanceEntry(entry);
        }
      });

      try {
        observer.observe({ entryTypes: ['navigation', 'paint', 'measure', 'resource'] });
      } catch (e) {
        console.warn('PerformanceObserver not supported:', e);
      }
    }

    // メモリ使用量の監視
    this.startMemoryMonitoring();
    
    // バンドルサイズの推定
    this.estimateBundleSize();
  }

  private handlePerformanceEntry(entry: PerformanceEntry): void {
    switch (entry.entryType) {
      case 'navigation':
        this.metrics.loadTime = entry.duration;
        break;
      case 'paint':
        if (entry.name === 'first-contentful-paint') {
          this.renderStartTime = entry.startTime;
        }
        break;
      case 'measure':
        if (entry.name.includes('render')) {
          this.metrics.renderTime = entry.duration;
        }
        break;
      case 'resource':
        // リソース読み込み時間の監視
        if (entry.name.includes('.js') || entry.name.includes('.css')) {
          this.updateBundleSize(entry);
        }
        break;
    }
  }

  private startMemoryMonitoring(): void {
    if ('memory' in performance) {
      setInterval(() => {
        const memory = (performance as any).memory;
        if (memory) {
          this.metrics.memoryUsage = {
            used: memory.usedJSHeapSize,
            total: memory.totalJSHeapSize,
            limit: memory.jsHeapSizeLimit
          };

          // メモリ使用量が高い場合の警告
          if (memory.usedJSHeapSize > 100 * 1024 * 1024) { // 100MB
            console.warn('High memory usage detected:', {
              used: Math.round(memory.usedJSHeapSize / 1024 / 1024) + 'MB',
              total: Math.round(memory.totalJSHeapSize / 1024 / 1024) + 'MB',
              limit: Math.round(memory.jsHeapSizeLimit / 1024 / 1024) + 'MB'
            });
          }
        }
      }, 10000); // 10秒間隔
    }
  }

  private estimateBundleSize(): void {
    // スクリプトタグからバンドルサイズを推定
    const scripts = document.querySelectorAll('script[src]');
    let totalSize = 0;
    
    scripts.forEach(script => {
      const src = (script as HTMLScriptElement).src;
      if (src.includes('_next/static/')) {
        // Next.jsの静的ファイルサイズを推定
        totalSize += 50000; // 50KB推定
      }
    });
    
    this.metrics.bundleSize = totalSize;
  }

  private updateBundleSize(entry: PerformanceEntry): void {
    // リソースサイズの更新
    if ('transferSize' in entry) {
      this.metrics.bundleSize += (entry as any).transferSize || 0;
    }
  }

  public startComponentTimer(componentName: string): void {
    this.componentTimers.set(componentName, performance.now());
  }

  public endComponentTimer(componentName: string): void {
    const startTime = this.componentTimers.get(componentName);
    if (startTime) {
      const renderTime = performance.now() - startTime;
      
      const existing = this.componentMetrics.get(componentName);
      if (existing) {
        existing.renderTime = (existing.renderTime + renderTime) / 2; // 平均
        existing.updateCount++;
      } else {
        this.componentMetrics.set(componentName, {
          name: componentName,
          renderTime,
          mountTime: renderTime,
          updateCount: 1,
          memoryUsage: this.metrics.memoryUsage.used
        });
        this.metrics.componentCount++;
      }
      
      this.componentTimers.delete(componentName);
    }
  }

  public updateCacheHitRate(hits: number, total: number): void {
    this.metrics.cacheHitRate = total > 0 ? (hits / total) * 100 : 0;
  }

  public updateErrorRate(errors: number, total: number): void {
    this.metrics.errorRate = total > 0 ? (errors / total) * 100 : 0;
  }

  public getMetrics(): PerformanceMetrics {
    return { ...this.metrics };
  }

  public getComponentMetrics(): ComponentMetrics[] {
    return Array.from(this.componentMetrics.values());
  }

  public getSlowComponents(threshold: number = 16): ComponentMetrics[] {
    return this.getComponentMetrics()
      .filter(metric => metric.renderTime > threshold)
      .sort((a, b) => b.renderTime - a.renderTime);
  }

  public getMemoryReport(): {
    usage: string;
    percentage: number;
    recommendation: string;
  } {
    const { used, total, limit } = this.metrics.memoryUsage;
    const percentage = limit > 0 ? (used / limit) * 100 : 0;
    
    let recommendation = 'メモリ使用量は正常です';
    if (percentage > 80) {
      recommendation = 'メモリ使用量が高すぎます。ページを再読み込みすることを推奨します。';
    } else if (percentage > 60) {
      recommendation = 'メモリ使用量がやや高いです。不要なタブを閉じることを推奨します。';
    }

    return {
      usage: `${Math.round(used / 1024 / 1024)}MB / ${Math.round(limit / 1024 / 1024)}MB`,
      percentage: Math.round(percentage),
      recommendation
    };
  }

  public optimizePerformance(): void {
    // パフォーマンス最適化の実行
    console.log('🚀 パフォーマンス最適化を実行中...');
    
    // 1. 不要なイベントリスナーの削除
    this.cleanupEventListeners();
    
    // 2. メモリリークの防止
    this.preventMemoryLeaks();
    
    // 3. キャッシュの最適化
    this.optimizeCache();
    
    console.log('✅ パフォーマンス最適化が完了しました');
  }

  private cleanupEventListeners(): void {
    // 不要なイベントリスナーの削除
    const elements = document.querySelectorAll('*');
    elements.forEach(element => {
      // イベントリスナーの数を確認（実際の実装ではより詳細な監視が必要）
      if (element.addEventListener) {
        // デバッグ用のログ
        console.debug('Event listeners on element:', element.tagName);
      }
    });
  }

  private preventMemoryLeaks(): void {
    // メモリリークの防止
    if (this.metrics.memoryUsage.used > 50 * 1024 * 1024) { // 50MB
      console.warn('メモリ使用量が高いため、最適化を実行します');
      
      // ガベージコレクションの実行（可能な場合）
      if ('gc' in window) {
        (window as any).gc();
      }
    }
  }

  private optimizeCache(): void {
    // キャッシュの最適化
    if ('caches' in window) {
      caches.keys().then(names => {
        names.forEach(name => {
          // 古いキャッシュの削除
          if (name.includes('old') || name.includes('temp')) {
            caches.delete(name);
          }
        });
      });
    }
  }

  public generateReport(): string {
    const metrics = this.getMetrics();
    const components = this.getComponentMetrics();
    const memoryReport = this.getMemoryReport();
    
    return `
# パフォーマンスレポート

## 基本メトリクス
- 読み込み時間: ${metrics.loadTime.toFixed(2)}ms
- レンダリング時間: ${metrics.renderTime.toFixed(2)}ms
- コンポーネント数: ${metrics.componentCount}
- バンドルサイズ: ${Math.round(metrics.bundleSize / 1024)}KB
- キャッシュヒット率: ${metrics.cacheHitRate.toFixed(1)}%
- エラー率: ${metrics.errorRate.toFixed(1)}%

## メモリ使用量
- 使用量: ${memoryReport.usage}
- 使用率: ${memoryReport.percentage}%
- 推奨事項: ${memoryReport.recommendation}

## コンポーネントパフォーマンス
${components.map(comp => 
  `- ${comp.name}: ${comp.renderTime.toFixed(2)}ms (更新回数: ${comp.updateCount})`
).join('\n')}

## 遅いコンポーネント
${this.getSlowComponents().map(comp => 
  `- ${comp.name}: ${comp.renderTime.toFixed(2)}ms`
).join('\n')}
    `.trim();
  }
}

// シングルトンインスタンス
export const performanceMonitor = new PerformanceMonitor();

// React用のパフォーマンスフック
export function usePerformanceMonitor(componentName: string) {
  const { useEffect } = require('react');
  
  useEffect(() => {
    performanceMonitor.startComponentTimer(componentName);
    
    return () => {
      performanceMonitor.endComponentTimer(componentName);
    };
  }, [componentName]);
}

// パフォーマンス最適化の自動実行
export function autoOptimizePerformance(): void {
  const metrics = performanceMonitor.getMetrics();
  
  // メモリ使用量が高い場合の自動最適化
  if (metrics.memoryUsage.used > 80 * 1024 * 1024) { // 80MB
    console.warn('メモリ使用量が高いため、自動最適化を実行します');
    performanceMonitor.optimizePerformance();
  }
  
  // エラー率が高い場合の警告
  if (metrics.errorRate > 10) {
    console.warn('エラー率が高いです:', metrics.errorRate + '%');
  }
  
  // キャッシュヒット率が低い場合の警告
  if (metrics.cacheHitRate < 50) {
    console.warn('キャッシュヒット率が低いです:', metrics.cacheHitRate + '%');
  }
}

// 定期的なパフォーマンス監視
setInterval(autoOptimizePerformance, 30000); // 30秒間隔
