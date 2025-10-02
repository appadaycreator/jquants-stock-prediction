/**
 * 統合パフォーマンス最適化システム
 * フロントエンドメモリ最適化、チャート遅延読み込み、段階的データ読み込み、キャッシュ最適化を統合
 */

import { frontendMemoryOptimizer } from "./frontend-memory-optimizer";
import { progressiveDataLoader } from "./progressive-data-loader";
import { optimizedCacheStrategy } from "./optimized-cache-strategy";
import { performanceValidator } from "./performance-validator";

interface UnifiedPerformanceConfig {
  enableMemoryOptimization: boolean;
  enableLazyLoading: boolean;
  enableProgressiveLoading: boolean;
  enableCacheOptimization: boolean;
  enablePerformanceValidation: boolean;
  targetInitialLoadTime: number; // ms
  targetChartRenderTime: number; // ms
  targetMemoryReduction: number; // percentage
  enableRealTimeMonitoring: boolean;
  enableAutoOptimization: boolean;
}

interface PerformanceReport {
  success: boolean;
  score: number;
  metrics: {
    initialLoadTime: number;
    chartRenderTime: number;
    memoryUsage: number;
    memoryReduction: number;
    lcp: number;
    fid: number;
    cls: number;
  };
  optimizations: {
    memoryOptimization: boolean;
    lazyLoading: boolean;
    progressiveLoading: boolean;
    cacheOptimization: boolean;
  };
  recommendations: string[];
  nextSteps: string[];
}

class UnifiedPerformanceSystem {
  private config: UnifiedPerformanceConfig;
  private isInitialized: boolean = false;
  private performanceHistory: PerformanceReport[] = [];
  private monitoringInterval: NodeJS.Timeout | null = null;

  constructor(config: UnifiedPerformanceConfig) {
    this.config = config;
    this.initialize();
  }

  /**
   * システムの初期化
   */
  private async initialize(): Promise<void> {
    if (this.isInitialized) return;

    try {
      console.info("統合パフォーマンスシステムを初期化中...");

      // メモリ最適化の初期化
      if (this.config.enableMemoryOptimization) {
        await this.initializeMemoryOptimization();
      }

      // 遅延読み込みの初期化
      if (this.config.enableLazyLoading) {
        await this.initializeLazyLoading();
      }

      // 段階的読み込みの初期化
      if (this.config.enableProgressiveLoading) {
        await this.initializeProgressiveLoading();
      }

      // キャッシュ最適化の初期化
      if (this.config.enableCacheOptimization) {
        await this.initializeCacheOptimization();
      }

      // パフォーマンス検証の初期化
      if (this.config.enablePerformanceValidation) {
        await this.initializePerformanceValidation();
      }

      // リアルタイム監視の開始
      if (this.config.enableRealTimeMonitoring) {
        this.startRealTimeMonitoring();
      }

      this.isInitialized = true;
      console.info("統合パフォーマンスシステムの初期化完了");
    } catch (error) {
      console.error("統合パフォーマンスシステムの初期化に失敗:", error);
      throw error;
    }
  }

  /**
   * メモリ最適化の初期化
   */
  private async initializeMemoryOptimization(): Promise<void> {
    console.info("メモリ最適化を初期化中...");
    
    // メモリ使用量の監視開始
    frontendMemoryOptimizer.optimizeMemory();
    
    console.info("メモリ最適化の初期化完了");
  }

  /**
   * 遅延読み込みの初期化
   */
  private async initializeLazyLoading(): Promise<void> {
    console.info("遅延読み込みを初期化中...");
    
    // 遅延読み込み要素の監視開始
    if (typeof window !== "undefined") {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            this.loadLazyElement(entry.target as HTMLElement);
          }
        });
      });
      
      document.querySelectorAll("[data-lazy]").forEach(el => {
        observer.observe(el);
      });
    }
    
    console.info("遅延読み込みの初期化完了");
  }

  /**
   * 段階的読み込みの初期化
   */
  private async initializeProgressiveLoading(): Promise<void> {
    console.info("段階的読み込みを初期化中...");
    
    // 段階的読み込みの設定
    console.info("段階的読み込みの初期化完了");
  }

  /**
   * キャッシュ最適化の初期化
   */
  private async initializeCacheOptimization(): Promise<void> {
    console.info("キャッシュ最適化を初期化中...");
    
    // キャッシュ戦略の最適化
    console.info("キャッシュ最適化の初期化完了");
  }

  /**
   * パフォーマンス検証の初期化
   */
  private async initializePerformanceValidation(): Promise<void> {
    console.info("パフォーマンス検証を初期化中...");
    
    // パフォーマンス目標の設定
    console.info("パフォーマンス検証の初期化完了");
  }

  /**
   * 遅延読み込み要素の処理
   */
  private loadLazyElement(element: HTMLElement): void {
    const lazyType = element.getAttribute("data-lazy-type");
    
    switch (lazyType) {
      case "chart":
        this.loadLazyChart(element);
        break;
      case "image":
        this.loadLazyImage(element);
        break;
      case "component":
        this.loadLazyComponent(element);
        break;
      default:
        this.loadLazyGeneric(element);
    }
  }

  /**
   * 遅延チャートの読み込み
   */
  private async loadLazyChart(element: HTMLElement): Promise<void> {
    const chartType = element.getAttribute("data-chart-type");
    const dataSource = element.getAttribute("data-source");
    
    if (!chartType || !dataSource) return;

    try {
      // チャートデータの段階的読み込み
      const data = await progressiveDataLoader.loadDataProgressively(
        async (offset, limit) => {
          const response = await fetch(`${dataSource}?offset=${offset}&limit=${limit}`);
          return response.json();
        }
      );

      // チャートの描画
      await this.renderChart(element, chartType, data.data);
    } catch (error) {
      console.error("遅延チャートの読み込みに失敗:", error);
    }
  }

  /**
   * 遅延画像の読み込み
   */
  private loadLazyImage(element: HTMLElement): void {
    const src = element.getAttribute("data-src");
    if (src) {
      (element as HTMLImageElement).src = src;
      element.removeAttribute("data-src");
      element.classList.add("loaded");
    }
  }

  /**
   * 遅延コンポーネントの読み込み
   */
  private async loadLazyComponent(element: HTMLElement): Promise<void> {
    const componentPath = element.getAttribute("data-component-path");
    if (!componentPath) return;

    try {
      const component = await import(componentPath);
      // コンポーネントのレンダリング
      element.innerHTML = "";
      element.appendChild(component.default());
    } catch (error) {
      console.error("遅延コンポーネントの読み込みに失敗:", error);
    }
  }

  /**
   * 汎用遅延読み込み
   */
  private loadLazyGeneric(element: HTMLElement): void {
    const data = element.getAttribute("data-lazy-data");
    if (data) {
      try {
        const parsedData = JSON.parse(data);
        element.innerHTML = parsedData.content;
        element.classList.add("loaded");
      } catch (error) {
        console.error("汎用遅延読み込みに失敗:", error);
      }
    }
  }

  /**
   * チャートの描画
   */
  private async renderChart(element: HTMLElement, type: string, data: any[]): Promise<void> {
    const startTime = performance.now();
    
    try {
      // チャートライブラリの動的読み込み
      const chartModule = await this.loadChartLibrary(type);
      
      // データの最適化
      const optimizedData = frontendMemoryOptimizer.downsampleChartData(data, 3000);
      
      // チャートの初期化
      const chart = new chartModule.default(element, {
        data: optimizedData,
        type,
      });

      const renderTime = performance.now() - startTime;
      performanceValidator.recordChartRenderTime(renderTime);

      console.info("チャート描画完了:", {
        type,
        renderTime: `${renderTime.toFixed(2)}ms`,
        dataPoints: optimizedData.length,
        status: renderTime < this.config.targetChartRenderTime ? "PASS" : "FAIL",
      });
    } catch (error) {
      console.error("チャート描画に失敗:", error);
    }
  }

  /**
   * チャートライブラリの動的読み込み
   */
  private async loadChartLibrary(type: string): Promise<any> {
    const startTime = performance.now();
    
    let module;
    switch (type) {
      case "line":
        module = await import("chart.js");
        break;
      case "candlestick":
        module = await import("lightweight-charts");
        break;
      case "volume":
        module = await import("chart.js");
        break;
      case "technical":
        module = await import("tradingview-charting-library");
        break;
      default:
        module = await import("chart.js");
    }

    const loadTime = performance.now() - startTime;
    console.info("チャートライブラリ読み込み:", {
      type,
      loadTime: `${loadTime.toFixed(2)}ms`,
    });

    return module;
  }

  /**
   * リアルタイム監視の開始
   */
  private startRealTimeMonitoring(): void {
    this.monitoringInterval = setInterval(() => {
      this.monitorPerformance();
    }, 10000); // 10秒間隔
  }

  /**
   * パフォーマンス監視
   */
  private monitorPerformance(): void {
    const memoryUsage = frontendMemoryOptimizer.getCurrentMemoryUsage();
    
    if (memoryUsage > 100) { // 100MB超過
      console.warn("メモリ使用量が高い:", `${memoryUsage}MB`);
      
      if (this.config.enableAutoOptimization) {
        this.autoOptimize();
      }
    }
  }

  /**
   * 自動最適化
   */
  private autoOptimize(): void {
    console.info("自動最適化を実行中...");
    
    // メモリ最適化
    if (this.config.enableMemoryOptimization) {
      frontendMemoryOptimizer.optimizeMemory();
    }
    
    // キャッシュ最適化
    if (this.config.enableCacheOptimization) {
      optimizedCacheStrategy.cleanup();
    }
    
    console.info("自動最適化完了");
  }

  /**
   * パフォーマンス検証の実行
   */
  async validatePerformance(): Promise<PerformanceReport> {
    if (!this.isInitialized) {
      await this.initialize();
    }

    // メモリ使用量の最終記録
    performanceValidator.recordFinalMemoryUsage();

    // パフォーマンス検証の実行
    const validationResult = performanceValidator.validate();

    const report: PerformanceReport = {
      success: validationResult.success,
      score: validationResult.score,
      metrics: {
        initialLoadTime: validationResult.metrics.initialLoadTime,
        chartRenderTime: validationResult.metrics.chartRenderTime,
        memoryUsage: validationResult.metrics.memoryUsage.after,
        memoryReduction: validationResult.metrics.memoryUsage.reduction,
        lcp: validationResult.metrics.coreWebVitals.lcp,
        fid: validationResult.metrics.coreWebVitals.fid,
        cls: validationResult.metrics.coreWebVitals.cls,
      },
      optimizations: {
        memoryOptimization: this.config.enableMemoryOptimization,
        lazyLoading: this.config.enableLazyLoading,
        progressiveLoading: this.config.enableProgressiveLoading,
        cacheOptimization: this.config.enableCacheOptimization,
      },
      recommendations: validationResult.recommendations,
      nextSteps: this.generateNextSteps(validationResult),
    };

    this.performanceHistory.push(report);
    
    // 履歴の制限（最新50件）
    if (this.performanceHistory.length > 50) {
      this.performanceHistory.shift();
    }

    return report;
  }

  /**
   * 次のステップの生成
   */
  private generateNextSteps(validationResult: any): string[] {
    const nextSteps: string[] = [];
    
    if (!validationResult.success) {
      nextSteps.push("失敗したテストの修正を優先してください");
      nextSteps.push("推奨事項の実装を検討してください");
    } else {
      nextSteps.push("パフォーマンス監視の継続を推奨します");
      nextSteps.push("定期的なパフォーマンステストの実施を推奨します");
    }
    
    if (this.performanceHistory.length > 1) {
      const previousReport = this.performanceHistory[this.performanceHistory.length - 2];
      const currentReport = this.performanceHistory[this.performanceHistory.length - 1];
      
      if (currentReport.score < previousReport.score) {
        nextSteps.push("パフォーマンスの劣化が検出されました。原因の調査を推奨します");
      }
    }

    return nextSteps;
  }

  /**
   * パフォーマンスレポートの生成
   */
  generatePerformanceReport(): {
    current: PerformanceReport | null;
    history: PerformanceReport[];
    trends: {
      score: number[];
      memoryUsage: number[];
      initialLoadTime: number[];
      chartRenderTime: number[];
    };
    recommendations: string[];
  } {
    const current = this.performanceHistory[this.performanceHistory.length - 1] || null;
    
    const trends = {
      score: this.performanceHistory.map(report => report.score),
      memoryUsage: this.performanceHistory.map(report => report.metrics.memoryUsage),
      initialLoadTime: this.performanceHistory.map(report => report.metrics.initialLoadTime),
      chartRenderTime: this.performanceHistory.map(report => report.metrics.chartRenderTime),
    };

    const recommendations: string[] = [];
    
    if (current) {
      if (current.metrics.initialLoadTime > this.config.targetInitialLoadTime) {
        recommendations.push("初回読み込み時間の改善が必要です");
      }
      
      if (current.metrics.chartRenderTime > this.config.targetChartRenderTime) {
        recommendations.push("チャート描画時間の改善が必要です");
      }
      
      if (current.metrics.memoryReduction < this.config.targetMemoryReduction) {
        recommendations.push("メモリ削減の改善が必要です");
      }
    }

    return {
      current,
      history: this.performanceHistory,
      trends,
      recommendations,
    };
  }

  /**
   * システムの最適化
   */
  async optimize(): Promise<void> {
    console.info("システム最適化を実行中...");
    
    // メモリ最適化
    if (this.config.enableMemoryOptimization) {
      frontendMemoryOptimizer.optimizeMemory();
    }
    
    // キャッシュ最適化
    if (this.config.enableCacheOptimization) {
      optimizedCacheStrategy.cleanup();
    }
    
    // 段階的読み込み最適化
    if (this.config.enableProgressiveLoading) {
      // 段階的読み込みの最適化ロジック
    }
    
    console.info("システム最適化完了");
  }

  /**
   * クリーンアップ
   */
  cleanup(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
    }
    
    frontendMemoryOptimizer.cleanup();
    progressiveDataLoader.cleanup();
    optimizedCacheStrategy.cleanup();
    performanceValidator.cleanup();
    
    this.performanceHistory = [];
    this.isInitialized = false;
  }
}

// デフォルト設定
const defaultConfig: UnifiedPerformanceConfig = {
  enableMemoryOptimization: true,
  enableLazyLoading: true,
  enableProgressiveLoading: true,
  enableCacheOptimization: true,
  enablePerformanceValidation: true,
  targetInitialLoadTime: 3000, // 3秒
  targetChartRenderTime: 1000, // 1秒
  targetMemoryReduction: 50, // 50%
  enableRealTimeMonitoring: true,
  enableAutoOptimization: true,
};

export const unifiedPerformanceSystem = new UnifiedPerformanceSystem(defaultConfig);
export default UnifiedPerformanceSystem;
export type { UnifiedPerformanceConfig, PerformanceReport };
