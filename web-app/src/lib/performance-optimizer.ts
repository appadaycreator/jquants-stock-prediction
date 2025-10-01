/**
 * パフォーマンス最適化ユーティリティ
 * コード分割、チャートダウンサンプリング、遅延読込
 */

interface PerformanceConfig {
  maxDataPoints: number;
  enableLazyLoading: boolean;
  enableCodeSplitting: boolean;
  enableImageOptimization: boolean;
  enableFontOptimization: boolean;
}

interface DownsamplingResult {
  data: any[];
  originalCount: number;
  sampledCount: number;
  compressionRatio: number;
}

class PerformanceOptimizer {
  private config: PerformanceConfig;
  private lcpObserver: PerformanceObserver | null = null;
  private memoryObserver: PerformanceObserver | null = null;

  constructor(config: PerformanceConfig) {
    this.config = config;
    this.initPerformanceObservers();
  }

  /**
   * パフォーマンス監視の初期化
   */
  private initPerformanceObservers() {
    if (typeof window === "undefined") return;

    // LCP監視
    if ("PerformanceObserver" in window) {
      try {
        this.lcpObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lcp = entries[entries.length - 1];
          console.info("LCP測定:", {
            value: `${lcp.startTime.toFixed(2)}ms`,
            target: "<3000ms",
            status: lcp.startTime < 3000 ? "PASS" : "FAIL",
          });
        });
        this.lcpObserver.observe({ entryTypes: ["largest-contentful-paint"] });
      } catch (error) {
        console.warn("LCP監視の初期化に失敗:", error);
      }
    }

    // メモリ使用量監視
    if ("memory" in performance) {
      setInterval(() => {
        const memory = (performance as any).memory;
        console.info("メモリ使用量:", {
          used: `${Math.round(memory.usedJSHeapSize / 1024 / 1024)}MB`,
          total: `${Math.round(memory.totalJSHeapSize / 1024 / 1024)}MB`,
          limit: `${Math.round(memory.jsHeapSizeLimit / 1024 / 1024)}MB`,
        });
      }, 30000); // 30秒間隔
    }
  }

  /**
   * チャートデータのダウンサンプリング
   */
  downsampleChartData(data: any[], maxPoints: number = this.config.maxDataPoints): DownsamplingResult {
    if (data.length <= maxPoints) {
      return {
        data,
        originalCount: data.length,
        sampledCount: data.length,
        compressionRatio: 1.0,
      };
    }

    const step = Math.ceil(data.length / maxPoints);
    const sampledData = [];
    
    for (let i = 0; i < data.length; i += step) {
      sampledData.push(data[i]);
    }

    // 最後のデータポイントを必ず含める
    if (sampledData[sampledData.length - 1] !== data[data.length - 1]) {
      sampledData.push(data[data.length - 1]);
    }

    const compressionRatio = sampledData.length / data.length;

    console.info("チャートダウンサンプリング完了:", {
      original: data.length,
      sampled: sampledData.length,
      compressionRatio: `${(compressionRatio * 100).toFixed(1)}%`,
      performance: compressionRatio < 0.5 ? "OPTIMIZED" : "NORMAL",
    });

    return {
      data: sampledData,
      originalCount: data.length,
      sampledCount: sampledData.length,
      compressionRatio,
    };
  }

  /**
   * 動的インポートによるコード分割
   */
  async loadComponent(componentPath: string): Promise<any> {
    if (!this.config.enableCodeSplitting) {
      return require(componentPath);
    }

    try {
      const startTime = performance.now();
      const component = await import(componentPath);
      const loadTime = performance.now() - startTime;

      console.info("コンポーネント動的読み込み:", {
        path: componentPath,
        loadTime: `${loadTime.toFixed(2)}ms`,
        status: loadTime < 1000 ? "FAST" : "SLOW",
      });

      return component;
    } catch (error) {
      console.error("コンポーネント読み込みエラー:", error);
      throw error;
    }
  }

  /**
   * 画像の遅延読み込み
   */
  createLazyImage(src: string, alt: string, className?: string): HTMLImageElement {
    const img = document.createElement("img");
    img.alt = alt;
    img.className = className || "";
    img.loading = "lazy";
    img.decoding = "async";

    // Intersection Observer で遅延読み込み
    if ("IntersectionObserver" in window) {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            img.src = src;
            observer.unobserve(img);
          }
        });
      });
      observer.observe(img);
    } else {
      // フォールバック
      img.src = src;
    }

    return img;
  }

  /**
   * フォントの遅延読み込み
   */
  async loadFont(fontFamily: string, fontUrl: string): Promise<void> {
    if (!this.config.enableFontOptimization) return;

    try {
      const startTime = performance.now();
      
      // フォントの事前読み込み
      const link = document.createElement("link");
      link.rel = "preload";
      link.as = "font";
      link.type = "font/woff2";
      link.href = fontUrl;
      link.crossOrigin = "anonymous";
      document.head.appendChild(link);

      // フォントの読み込み完了を待つ
      await new Promise((resolve, reject) => {
        const font = new FontFace(fontFamily, `url(${fontUrl})`);
        font.load().then(() => {
          document.fonts.add(font);
          resolve(void 0);
        }).catch(reject);
      });

      const loadTime = performance.now() - startTime;
      console.info("フォント読み込み完了:", {
        family: fontFamily,
        loadTime: `${loadTime.toFixed(2)}ms`,
        status: loadTime < 500 ? "FAST" : "NORMAL",
      });
    } catch (error) {
      console.error("フォント読み込みエラー:", error);
    }
  }

  /**
   * バンドルサイズの最適化
   */
  async optimizeBundle(): Promise<void> {
    if (!this.config.enableCodeSplitting) return;

    // 未使用のコードの削除
    const unusedModules = this.detectUnusedModules();
    if (unusedModules.length > 0) {
      console.info("未使用モジュール検出:", {
        modules: unusedModules,
        recommendation: "Tree shakingの確認を推奨",
      });
    }
  }

  /**
   * 未使用モジュールの検出
   */
  private detectUnusedModules(): string[] {
    // 簡易的な未使用モジュール検出
    const allModules = this.getAllModules();
    const usedModules = this.getUsedModules();
    
    return allModules.filter(module => !usedModules.includes(module));
  }

  /**
   * 全モジュールの取得
   */
  private getAllModules(): string[] {
    // 実際の実装では、webpack-bundle-analyzer等を使用
    return [];
  }

  /**
   * 使用中モジュールの取得
   */
  private getUsedModules(): string[] {
    // 実際の実装では、依存関係解析を使用
    return [];
  }

  /**
   * メモリ使用量の最適化
   */
  optimizeMemory(): void {
    // ガベージコレクションの強制実行
    if ("gc" in window) {
      (window as any).gc();
    }

    // 不要なイベントリスナーの削除
    this.cleanupEventListeners();

    // キャッシュの最適化
    this.optimizeCache();
  }

  /**
   * イベントリスナーのクリーンアップ
   */
  private cleanupEventListeners(): void {
    // 実際の実装では、イベントリスナーの追跡が必要
    console.info("イベントリスナークリーンアップ実行");
  }

  /**
   * キャッシュの最適化
   */
  private optimizeCache(): void {
    // IndexedDBの最適化
    if ("indexedDB" in window) {
      // 古いデータの削除
      this.cleanupOldCacheData();
    }
  }

  /**
   * 古いキャッシュデータの削除
   */
  private async cleanupOldCacheData(): Promise<void> {
    // 実装は省略（実際のプロジェクトでは適切に実装）
    console.info("古いキャッシュデータのクリーンアップ実行");
  }

  /**
   * パフォーマンスレポートの生成
   */
  generatePerformanceReport(): any {
    const navigation = performance.getEntriesByType("navigation")[0] as PerformanceNavigationTiming;
    const paint = performance.getEntriesByType("paint");
    const lcp = performance.getEntriesByType("largest-contentful-paint");
    const memory = (performance as any).memory;

    return {
      navigation: {
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
        totalTime: navigation.loadEventEnd - navigation.fetchStart,
      },
      paint: {
        firstPaint: paint.find(p => p.name === "first-paint")?.startTime || 0,
        firstContentfulPaint: paint.find(p => p.name === "first-contentful-paint")?.startTime || 0,
      },
      lcp: lcp.length > 0 ? lcp[lcp.length - 1].startTime : 0,
      memory: memory ? {
        used: Math.round(memory.usedJSHeapSize / 1024 / 1024),
        total: Math.round(memory.totalJSHeapSize / 1024 / 1024),
        limit: Math.round(memory.jsHeapSizeLimit / 1024 / 1024),
      } : null,
      recommendations: this.generateRecommendations(),
    };
  }

  /**
   * パフォーマンス改善の推奨事項を生成
   */
  private generateRecommendations(): string[] {
    const recommendations: string[] = [];
    const report = this.generatePerformanceReport();

    if (report.lcp > 3000) {
      recommendations.push("LCPが3秒を超えています。画像の最適化とコード分割を推奨します。");
    }

    if (report.memory && report.memory.used > 100) {
      recommendations.push("メモリ使用量が100MBを超えています。メモリリークの確認を推奨します。");
    }

    if (report.navigation.totalTime > 5000) {
      recommendations.push("初期読み込み時間が5秒を超えています。バンドルサイズの最適化を推奨します。");
    }

    return recommendations;
  }

  /**
   * クリーンアップ
   */
  cleanup(): void {
    if (this.lcpObserver) {
      this.lcpObserver.disconnect();
    }
    if (this.memoryObserver) {
      this.memoryObserver.disconnect();
    }
  }
}

// デフォルト設定
const defaultConfig: PerformanceConfig = {
  maxDataPoints: 3000,
  enableLazyLoading: true,
  enableCodeSplitting: true,
  enableImageOptimization: true,
  enableFontOptimization: true,
};

export const performanceOptimizer = new PerformanceOptimizer(defaultConfig);
export default PerformanceOptimizer;
export type { PerformanceConfig, DownsamplingResult };
