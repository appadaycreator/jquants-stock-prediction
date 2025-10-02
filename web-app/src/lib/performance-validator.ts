/**
 * パフォーマンス指標検証システム
 * 初回読み込み3秒、チャート描画1秒、メモリ50%削減の検証
 */

interface PerformanceTargets {
  initialLoadTime: number; // ms
  chartRenderTime: number; // ms
  memoryReduction: number; // percentage
  lcp: number; // ms
  fid: number; // ms
  cls: number; // score
}

interface PerformanceMetrics {
  initialLoadTime: number;
  chartRenderTime: number;
  memoryUsage: {
    before: number;
    after: number;
    reduction: number;
  };
  coreWebVitals: {
    lcp: number;
    fid: number;
    cls: number;
  };
  bundleSize: number;
  renderTime: number;
}

interface ValidationResult {
  success: boolean;
  score: number; // 0-100
  passed: string[];
  failed: string[];
  recommendations: string[];
  metrics: PerformanceMetrics;
}

class PerformanceValidator {
  private targets: PerformanceTargets;
  private metrics: PerformanceMetrics | null = null;
  private observers: PerformanceObserver[] = [];
  private startTime: number = 0;
  private memoryBefore: number = 0;
  private memoryAfter: number = 0;

  constructor(targets: PerformanceTargets) {
    this.targets = targets;
    this.initPerformanceMonitoring();
  }

  /**
   * パフォーマンス監視の初期化
   */
  private initPerformanceMonitoring(): void {
    if (typeof window === "undefined") return;

    this.startTime = performance.now();
    this.memoryBefore = this.getCurrentMemoryUsage();

    // Core Web Vitals監視
    this.observeCoreWebVitals();
    
    // ナビゲーション監視
    this.observeNavigation();
    
    // レンダリング監視
    this.observeRendering();
  }

  /**
   * Core Web Vitals監視
   */
  private observeCoreWebVitals(): void {
    if (!("PerformanceObserver" in window)) return;

    try {
      // LCP監視
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lcp = entries[entries.length - 1];
        this.recordLCP(lcp.startTime);
      });
      lcpObserver.observe({ entryTypes: ["largest-contentful-paint"] });
      this.observers.push(lcpObserver);

      // FID監視
      const fidObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach(entry => {
          this.recordFID(entry.processingStart - entry.startTime);
        });
      });
      fidObserver.observe({ entryTypes: ["first-input"] });
      this.observers.push(fidObserver);

      // CLS監視
      const clsObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach(entry => {
          this.recordCLS(entry.value);
        });
      });
      clsObserver.observe({ entryTypes: ["layout-shift"] });
      this.observers.push(clsObserver);

    } catch (error) {
      console.warn("Core Web Vitals監視の初期化に失敗:", error);
    }
  }

  /**
   * ナビゲーション監視
   */
  private observeNavigation(): void {
    if (!("PerformanceObserver" in window)) return;

    try {
      const navObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach(entry => {
          if (entry.entryType === "navigation") {
            this.recordNavigationTiming(entry as PerformanceNavigationTiming);
          }
        });
      });
      navObserver.observe({ entryTypes: ["navigation"] });
      this.observers.push(navObserver);
    } catch (error) {
      console.warn("ナビゲーション監視の初期化に失敗:", error);
    }
  }

  /**
   * レンダリング監視
   */
  private observeRendering(): void {
    if (!("PerformanceObserver" in window)) return;

    try {
      const renderObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach(entry => {
          if (entry.entryType === "measure") {
            this.recordRenderTime(entry.duration);
          }
        });
      });
      renderObserver.observe({ entryTypes: ["measure"] });
      this.observers.push(renderObserver);
    } catch (error) {
      console.warn("レンダリング監視の初期化に失敗:", error);
    }
  }

  /**
   * LCPの記録
   */
  private recordLCP(lcp: number): void {
    if (!this.metrics) {
      this.metrics = this.createEmptyMetrics();
    }
    this.metrics.coreWebVitals.lcp = lcp;
  }

  /**
   * FIDの記録
   */
  private recordFID(fid: number): void {
    if (!this.metrics) {
      this.metrics = this.createEmptyMetrics();
    }
    this.metrics.coreWebVitals.fid = fid;
  }

  /**
   * CLSの記録
   */
  private recordCLS(cls: number): void {
    if (!this.metrics) {
      this.metrics = this.createEmptyMetrics();
    }
    this.metrics.coreWebVitals.cls += cls;
  }

  /**
   * ナビゲーションタイミングの記録
   */
  private recordNavigationTiming(navigation: PerformanceNavigationTiming): void {
    if (!this.metrics) {
      this.metrics = this.createEmptyMetrics();
    }
    
    this.metrics.initialLoadTime = navigation.loadEventEnd - navigation.fetchStart;
  }

  /**
   * レンダリング時間の記録
   */
  private recordRenderTime(renderTime: number): void {
    if (!this.metrics) {
      this.metrics = this.createEmptyMetrics();
    }
    
    this.metrics.renderTime = Math.max(this.metrics.renderTime, renderTime);
  }

  /**
   * 空のメトリクスオブジェクトの作成
   */
  private createEmptyMetrics(): PerformanceMetrics {
    return {
      initialLoadTime: 0,
      chartRenderTime: 0,
      memoryUsage: {
        before: this.memoryBefore,
        after: 0,
        reduction: 0,
      },
      coreWebVitals: {
        lcp: 0,
        fid: 0,
        cls: 0,
      },
      bundleSize: 0,
      renderTime: 0,
    };
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
   * チャート描画時間の記録
   */
  recordChartRenderTime(renderTime: number): void {
    if (!this.metrics) {
      this.metrics = this.createEmptyMetrics();
    }
    
    this.metrics.chartRenderTime = renderTime;
  }

  /**
   * バンドルサイズの記録
   */
  recordBundleSize(size: number): void {
    if (!this.metrics) {
      this.metrics = this.createEmptyMetrics();
    }
    
    this.metrics.bundleSize = size;
  }

  /**
   * メモリ使用量の最終記録
   */
  recordFinalMemoryUsage(): void {
    this.memoryAfter = this.getCurrentMemoryUsage();
    
    if (this.metrics) {
      this.metrics.memoryUsage.after = this.memoryAfter;
      this.metrics.memoryUsage.reduction = 
        ((this.memoryBefore - this.memoryAfter) / this.memoryBefore) * 100;
    }
  }

  /**
   * パフォーマンス検証の実行
   */
  validate(): ValidationResult {
    if (!this.metrics) {
      this.metrics = this.createEmptyMetrics();
    }

    const passed: string[] = [];
    const failed: string[] = [];
    const recommendations: string[] = [];

    // 初回読み込み時間の検証
    if (this.metrics.initialLoadTime <= this.targets.initialLoadTime) {
      passed.push(`初回読み込み時間: ${this.metrics.initialLoadTime.toFixed(2)}ms <= ${this.targets.initialLoadTime}ms`);
    } else {
      failed.push(`初回読み込み時間: ${this.metrics.initialLoadTime.toFixed(2)}ms > ${this.targets.initialLoadTime}ms`);
      recommendations.push("初回読み込み時間を改善するため、コード分割とバンドル最適化を推奨します。");
    }

    // チャート描画時間の検証
    if (this.metrics.chartRenderTime <= this.targets.chartRenderTime) {
      passed.push(`チャート描画時間: ${this.metrics.chartRenderTime.toFixed(2)}ms <= ${this.targets.chartRenderTime}ms`);
    } else {
      failed.push(`チャート描画時間: ${this.metrics.chartRenderTime.toFixed(2)}ms > ${this.targets.chartRenderTime}ms`);
      recommendations.push("チャート描画時間を改善するため、データの最適化とレンダリング最適化を推奨します。");
    }

    // メモリ削減の検証
    if (this.metrics.memoryUsage.reduction >= this.targets.memoryReduction) {
      passed.push(`メモリ削減: ${this.metrics.memoryUsage.reduction.toFixed(1)}% >= ${this.targets.memoryReduction}%`);
    } else {
      failed.push(`メモリ削減: ${this.metrics.memoryUsage.reduction.toFixed(1)}% < ${this.targets.memoryReduction}%`);
      recommendations.push("メモリ削減を改善するため、データ圧縮とキャッシュ最適化を推奨します。");
    }

    // LCPの検証
    if (this.metrics.coreWebVitals.lcp <= this.targets.lcp) {
      passed.push(`LCP: ${this.metrics.coreWebVitals.lcp.toFixed(2)}ms <= ${this.targets.lcp}ms`);
    } else {
      failed.push(`LCP: ${this.metrics.coreWebVitals.lcp.toFixed(2)}ms > ${this.targets.lcp}ms`);
      recommendations.push("LCPを改善するため、重要なリソースのプリロードと画像最適化を推奨します。");
    }

    // FIDの検証
    if (this.metrics.coreWebVitals.fid <= this.targets.fid) {
      passed.push(`FID: ${this.metrics.coreWebVitals.fid.toFixed(2)}ms <= ${this.targets.fid}ms`);
    } else {
      failed.push(`FID: ${this.metrics.coreWebVitals.fid.toFixed(2)}ms > ${this.targets.fid}ms`);
      recommendations.push("FIDを改善するため、JavaScriptの最適化とイベントハンドラーの最適化を推奨します。");
    }

    // CLSの検証
    if (this.metrics.coreWebVitals.cls <= this.targets.cls) {
      passed.push(`CLS: ${this.metrics.coreWebVitals.cls.toFixed(3)} <= ${this.targets.cls}`);
    } else {
      failed.push(`CLS: ${this.metrics.coreWebVitals.cls.toFixed(3)} > ${this.targets.cls}`);
      recommendations.push("CLSを改善するため、レイアウトシフトの原因となる要素の最適化を推奨します。");
    }

    // スコアの計算
    const totalTests = passed.length + failed.length;
    const score = totalTests > 0 ? (passed.length / totalTests) * 100 : 0;

    const success = failed.length === 0;

    console.info("パフォーマンス検証結果:", {
      success,
      score: `${score.toFixed(1)}%`,
      passed: passed.length,
      failed: failed.length,
      recommendations: recommendations.length,
    });

    return {
      success,
      score,
      passed,
      failed,
      recommendations,
      metrics: this.metrics,
    };
  }

  /**
   * パフォーマンスレポートの生成
   */
  generateReport(): {
    summary: {
      success: boolean;
      score: number;
      totalTests: number;
      passedTests: number;
      failedTests: number;
    };
    metrics: PerformanceMetrics;
    targets: PerformanceTargets;
    recommendations: string[];
    nextSteps: string[];
  } {
    const result = this.validate();
    
    const nextSteps: string[] = [];
    
    if (!result.success) {
      nextSteps.push("失敗したテストの修正を優先してください");
      nextSteps.push("推奨事項の実装を検討してください");
    } else {
      nextSteps.push("パフォーマンス監視の継続を推奨します");
      nextSteps.push("定期的なパフォーマンステストの実施を推奨します");
    }

    return {
      summary: {
        success: result.success,
        score: result.score,
        totalTests: result.passed.length + result.failed.length,
        passedTests: result.passed.length,
        failedTests: result.failed.length,
      },
      metrics: this.metrics!,
      targets: this.targets,
      recommendations: result.recommendations,
      nextSteps,
    };
  }

  /**
   * パフォーマンス比較レポートの生成
   */
  generateComparisonReport(baseline: PerformanceMetrics): {
    improvements: {
      initialLoadTime: number;
      chartRenderTime: number;
      memoryReduction: number;
      lcp: number;
      fid: number;
      cls: number;
    };
    overallImprovement: number;
    recommendations: string[];
  } {
    if (!this.metrics) {
      throw new Error("メトリクスが記録されていません");
    }

    const improvements = {
      initialLoadTime: ((baseline.initialLoadTime - this.metrics.initialLoadTime) / baseline.initialLoadTime) * 100,
      chartRenderTime: ((baseline.chartRenderTime - this.metrics.chartRenderTime) / baseline.chartRenderTime) * 100,
      memoryReduction: this.metrics.memoryUsage.reduction - baseline.memoryUsage.reduction,
      lcp: ((baseline.coreWebVitals.lcp - this.metrics.coreWebVitals.lcp) / baseline.coreWebVitals.lcp) * 100,
      fid: ((baseline.coreWebVitals.fid - this.metrics.coreWebVitals.fid) / baseline.coreWebVitals.fid) * 100,
      cls: ((baseline.coreWebVitals.cls - this.metrics.coreWebVitals.cls) / baseline.coreWebVitals.cls) * 100,
    };

    const overallImprovement = Object.values(improvements).reduce((sum, val) => sum + val, 0) / Object.keys(improvements).length;

    const recommendations: string[] = [];
    
    if (improvements.initialLoadTime < 0) {
      recommendations.push("初回読み込み時間の改善が必要です");
    }
    
    if (improvements.chartRenderTime < 0) {
      recommendations.push("チャート描画時間の改善が必要です");
    }
    
    if (improvements.memoryReduction < 0) {
      recommendations.push("メモリ削減の改善が必要です");
    }

    return {
      improvements,
      overallImprovement,
      recommendations,
    };
  }

  /**
   * クリーンアップ
   */
  cleanup(): void {
    this.observers.forEach(observer => observer.disconnect());
    this.observers = [];
  }
}

// デフォルト目標値
const defaultTargets: PerformanceTargets = {
  initialLoadTime: 3000, // 3秒
  chartRenderTime: 1000, // 1秒
  memoryReduction: 50, // 50%
  lcp: 2500, // 2.5秒
  fid: 100, // 100ms
  cls: 0.1, // 0.1
};

export const performanceValidator = new PerformanceValidator(defaultTargets);
export default PerformanceValidator;
export type { PerformanceTargets, PerformanceMetrics, ValidationResult };
