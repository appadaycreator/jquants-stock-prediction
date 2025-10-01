/**
 * 強化されたパフォーマンス最適化システム
 * フロントエンドのUI最適化と遅延読み込みを実装
 */

interface EnhancedPerformanceConfig {
  maxDataPoints: number;
  enableLazyLoading: boolean;
  enableCodeSplitting: boolean;
  enableImageOptimization: boolean;
  enableFontOptimization: boolean;
  enableVirtualScrolling: boolean;
  enableMemoization: boolean;
  enableDebouncing: boolean;
  enableIntersectionObserver: boolean;
  enableServiceWorker: boolean;
  targetLCP: number; // 最大LCP時間（ms）
  targetFID: number; // 最大FID時間（ms）
  targetCLS: number; // 最大CLS値
}

interface PerformanceMetrics {
  lcp: number;
  fid: number;
  cls: number;
  fcp: number;
  ttfb: number;
  memoryUsage: number;
  renderTime: number;
  bundleSize: number;
}

interface OptimizationResult {
  success: boolean;
  improvements: string[];
  metrics: PerformanceMetrics;
  recommendations: string[];
}

class EnhancedPerformanceOptimizer {
  private config: EnhancedPerformanceConfig;
  private performanceObserver: PerformanceObserver | null = null;
  private memoryObserver: PerformanceObserver | null = null;
  private intersectionObserver: IntersectionObserver | null = null;
  private debounceTimers: Map<string, NodeJS.Timeout> = new Map();
  private memoizedResults: Map<string, any> = new Map();
  private lazyLoadQueue: Set<HTMLElement> = new Set();
  private virtualScrollCache: Map<number, HTMLElement> = new Map();

  constructor(config: EnhancedPerformanceConfig) {
    this.config = config;
    this.initPerformanceMonitoring();
    this.initLazyLoading();
    this.initServiceWorker();
  }

  /**
   * パフォーマンス監視の初期化
   */
  private initPerformanceMonitoring(): void {
    if (typeof window === "undefined") return;

    // Core Web Vitals監視
    this.observeCoreWebVitals();
    
    // メモリ使用量監視
    this.observeMemoryUsage();
    
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
      this.performanceObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lcp = entries[entries.length - 1];
        
        if (lcp.startTime > this.config.targetLCP) {
          console.warn(`LCPが目標値を超過: ${lcp.startTime.toFixed(2)}ms > ${this.config.targetLCP}ms`);
          this.optimizeLCP();
        }
      });
      
      this.performanceObserver.observe({ entryTypes: ["largest-contentful-paint"] });

      // FID監視
      this.performanceObserver.observe({ entryTypes: ["first-input"] });

      // CLS監視
      this.performanceObserver.observe({ entryTypes: ["layout-shift"] });

    } catch (error) {
      console.warn("Core Web Vitals監視の初期化に失敗:", error);
    }
  }

  /**
   * メモリ使用量監視
   */
  private observeMemoryUsage(): void {
    if (!("memory" in performance)) return;

    setInterval(() => {
      const memory = (performance as any).memory;
      const usedMB = Math.round(memory.usedJSHeapSize / 1024 / 1024);
      const totalMB = Math.round(memory.totalJSHeapSize / 1024 / 1024);
      
      if (usedMB > 100) {
        console.warn(`メモリ使用量が高すぎます: ${usedMB}MB / ${totalMB}MB`);
        this.optimizeMemory();
      }
    }, 30000);
  }

  /**
   * レンダリング監視
   */
  private observeRendering(): void {
    if (!("PerformanceObserver" in window)) return;

    try {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach(entry => {
          if (entry.duration > 16) { // 60fps未満
            console.warn(`レンダリングが遅い: ${entry.duration.toFixed(2)}ms`);
            this.optimizeRendering();
          }
        });
      });
      
      observer.observe({ entryTypes: ["measure", "navigation"] });
    } catch (error) {
      console.warn("レンダリング監視の初期化に失敗:", error);
    }
  }

  /**
   * 遅延読み込みの初期化
   */
  private initLazyLoading(): void {
    if (!this.config.enableLazyLoading) return;

    this.intersectionObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.loadElement(entry.target as HTMLElement);
          this.intersectionObserver?.unobserve(entry.target);
        }
      });
    }, {
      rootMargin: "50px",
    });

    // 既存の遅延読み込み要素を監視
    document.querySelectorAll("[data-lazy]").forEach(el => {
      this.intersectionObserver?.observe(el);
    });
  }

  /**
   * 要素の遅延読み込み処理
   */
  private loadElement(element: HTMLElement): void {
    // 画像要素の場合
    if (element.tagName === "IMG") {
      const img = element as HTMLImageElement;
      const dataSrc = img.getAttribute("data-src");
      if (dataSrc) {
        img.src = dataSrc;
        img.removeAttribute("data-src");
        img.classList.add("loaded");
      }
    }
    
    // 背景画像の場合
    const bgImage = element.getAttribute("data-bg");
    if (bgImage) {
      element.style.backgroundImage = `url(${bgImage})`;
      element.removeAttribute("data-bg");
      element.classList.add("loaded");
    }
    
    // カスタム遅延読み込み要素
    const lazyData = element.getAttribute("data-lazy");
    if (lazyData) {
      try {
        const data = JSON.parse(lazyData);
        if (data.src) {
          if (element.tagName === "IMG") {
            (element as HTMLImageElement).src = data.src;
          } else {
            element.style.backgroundImage = `url(${data.src})`;
          }
        }
        element.removeAttribute("data-lazy");
        element.classList.add("loaded");
      } catch (error) {
        console.warn("遅延読み込みデータの解析に失敗:", error);
      }
    }
    
    // 遅延読み込み完了イベントを発火
    element.dispatchEvent(new CustomEvent("lazyLoaded", {
      detail: { element },
    }));
  }

  /**
   * Service Worker初期化
   */
  private initServiceWorker(): void {
    if (!this.config.enableServiceWorker) return;

    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("/sw.js")
        .then(registration => {
          console.log("Service Worker登録成功:", registration);
        })
        .catch(error => {
          console.warn("Service Worker登録失敗:", error);
        });
    }
  }

  /**
   * チャートデータのダウンサンプリング（強化版）
   */
  downsampleChartData(
    data: any[], 
    maxPoints: number = this.config.maxDataPoints,
    strategy: "uniform" | "adaptive" | "smart" = "smart",
  ): any[] {
    if (data.length <= maxPoints) {
      return data;
    }

    let sampledData: any[];

    switch (strategy) {
      case "uniform":
        sampledData = this.uniformSampling(data, maxPoints);
        break;
      case "adaptive":
        sampledData = this.adaptiveSampling(data, maxPoints);
        break;
      case "smart":
        sampledData = this.smartSampling(data, maxPoints);
        break;
      default:
        sampledData = this.smartSampling(data, maxPoints);
    }

    console.info("チャートダウンサンプリング完了:", {
      original: data.length,
      sampled: sampledData.length,
      strategy,
      compressionRatio: `${(sampledData.length / data.length * 100).toFixed(1)}%`,
    });

    return sampledData;
  }

  /**
   * 均等サンプリング
   */
  private uniformSampling(data: any[], maxPoints: number): any[] {
    const step = Math.ceil(data.length / maxPoints);
    const sampled = [];
    
    for (let i = 0; i < data.length; i += step) {
      sampled.push(data[i]);
    }
    
    // 最後のデータポイントを必ず含める
    if (sampled[sampled.length - 1] !== data[data.length - 1]) {
      sampled.push(data[data.length - 1]);
    }
    
    return sampled;
  }

  /**
   * 適応的サンプリング
   */
  private adaptiveSampling(data: any[], maxPoints: number): any[] {
    // 価格変動の大きい箇所を優先的に保持
    const changes = data.map((item, index) => {
      if (index === 0) return 0;
      return Math.abs(item.close - data[index - 1].close);
    });

    const threshold = changes.sort((a, b) => b - a)[Math.floor(maxPoints * 0.3)];
    const importantIndices = changes.map((change, index) => 
      change >= threshold ? index : -1,
    ).filter(index => index !== -1);

    const sampled = importantIndices.map(index => data[index]);
    
    // 不足分を均等サンプリングで補完
    if (sampled.length < maxPoints) {
      const remaining = maxPoints - sampled.length;
      const step = Math.ceil(data.length / remaining);
      
      for (let i = 0; i < data.length; i += step) {
        if (!sampled.includes(data[i])) {
          sampled.push(data[i]);
          if (sampled.length >= maxPoints) break;
        }
      }
    }
    
    return sampled.slice(0, maxPoints);
  }

  /**
   * スマートサンプリング
   */
  private smartSampling(data: any[], maxPoints: number): any[] {
    // 複数の戦略を組み合わせ
    const uniform = this.uniformSampling(data, maxPoints);
    const adaptive = this.adaptiveSampling(data, maxPoints);
    
    // 重要度に基づいて統合
    const combined = [...new Set([...uniform, ...adaptive])];
    
    return combined.slice(0, maxPoints);
  }

  /**
   * 動的インポートによるコード分割（強化版）
   */
  async loadComponent(
    componentPath: string,
    fallback?: React.ComponentType,
  ): Promise<any> {
    if (!this.config.enableCodeSplitting) {
      return require(componentPath);
    }

    try {
      const startTime = performance.now();
      
      // プリロードの確認
      if (this.isComponentPreloaded(componentPath)) {
        const component = await import(componentPath);
        return component;
      }

      // 遅延読み込み
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
      
      if (fallback) {
        console.info("フォールバックコンポーネントを使用");
        return fallback;
      }
      
      throw error;
    }
  }

  /**
   * コンポーネントのプリロード確認
   */
  private isComponentPreloaded(componentPath: string): boolean {
    // 実際の実装では、プリロードされたコンポーネントのリストを管理
    return false;
  }

  /**
   * 仮想スクロールの実装
   */
  createVirtualScroll(
    container: HTMLElement,
    items: any[],
    itemHeight: number,
    renderItem: (item: any, index: number) => HTMLElement,
  ): void {
    if (!this.config.enableVirtualScrolling) {
      // 通常のレンダリング
      items.forEach((item, index) => {
        container.appendChild(renderItem(item, index));
      });
      return;
    }

    const visibleCount = Math.ceil(container.clientHeight / itemHeight);
    const bufferSize = Math.min(10, Math.floor(visibleCount / 2));
    
    let startIndex = 0;
    let endIndex = Math.min(startIndex + visibleCount + bufferSize, items.length);

    const renderVisibleItems = () => {
      // 既存の要素をクリア
      container.innerHTML = "";
      
      // 可視範囲の要素のみレンダリング
      for (let i = startIndex; i < endIndex; i++) {
        if (this.virtualScrollCache.has(i)) {
          container.appendChild(this.virtualScrollCache.get(i)!);
        } else {
          const element = renderItem(items[i], i);
          this.virtualScrollCache.set(i, element);
          container.appendChild(element);
        }
      }
    };

    // スクロールイベントの最適化
    const handleScroll = this.debounce(() => {
      const scrollTop = container.scrollTop;
      const newStartIndex = Math.floor(scrollTop / itemHeight);
      const newEndIndex = Math.min(newStartIndex + visibleCount + bufferSize, items.length);

      if (newStartIndex !== startIndex || newEndIndex !== endIndex) {
        startIndex = newStartIndex;
        endIndex = newEndIndex;
        renderVisibleItems();
      }
    }, 16); // 60fps

    container.addEventListener("scroll", handleScroll);
    renderVisibleItems();
  }

  /**
   * メモ化の実装
   */
  memoize<T extends (...args: any[]) => any>(
    fn: T,
    keyGenerator?: (...args: Parameters<T>) => string,
  ): T {
    if (!this.config.enableMemoization) {
      return fn;
    }

    return ((...args: Parameters<T>) => {
      const key = keyGenerator ? keyGenerator(...args) : JSON.stringify(args);
      
      if (this.memoizedResults.has(key)) {
        console.debug("メモ化キャッシュヒット:", key);
        return this.memoizedResults.get(key);
      }

      const result = fn(...args);
      this.memoizedResults.set(key, result);
      
      // キャッシュサイズ制限
      if (this.memoizedResults.size > 100) {
        const firstKey = this.memoizedResults.keys().next().value;
        if (firstKey !== undefined) {
          this.memoizedResults.delete(firstKey);
        }
      }

      return result;
    }) as T;
  }

  /**
   * デバウンスの実装
   */
  debounce<T extends (...args: any[]) => any>(
    func: T,
    delay: number = 300,
  ): T {
    if (!this.config.enableDebouncing) {
      return func;
    }

    return ((...args: Parameters<T>) => {
      const key = func.name || "anonymous";
      
      if (this.debounceTimers.has(key)) {
        clearTimeout(this.debounceTimers.get(key)!);
      }

      const timer = setTimeout(() => {
        func(...args);
        this.debounceTimers.delete(key);
      }, delay);

      this.debounceTimers.set(key, timer);
    }) as T;
  }

  /**
   * 画像の遅延読み込み（強化版）
   */
  createLazyImage(
    src: string,
    alt: string,
    className?: string,
    placeholder?: string,
  ): HTMLImageElement {
    const img = document.createElement("img");
    img.alt = alt;
    img.className = className || "";
    img.loading = "lazy";
    img.decoding = "async";
    
    // プレースホルダー画像
    if (placeholder) {
      img.src = placeholder;
    }

    // Intersection Observer で遅延読み込み
    if (this.intersectionObserver) {
      this.intersectionObserver.observe(img);
      
      img.addEventListener("load", () => {
        this.intersectionObserver?.unobserve(img);
      });
    } else {
      // フォールバック
      img.src = src;
    }

    // 実際の画像読み込み
    const loadImage = () => {
      img.src = src;
    };

    img.addEventListener("intersect", loadImage);
    
    return img;
  }

  /**
   * LCP最適化
   */
  private optimizeLCP(): void {
    console.info("LCP最適化を実行");
    
    // 重要なリソースのプリロード
    this.preloadCriticalResources();
    
    // 画像の最適化
    this.optimizeImages();
    
    // フォントの最適化
    this.optimizeFonts();
  }

  /**
   * メモリ最適化
   */
  private optimizeMemory(): void {
    console.info("メモリ最適化を実行");
    
    // ガベージコレクションの強制実行
    if ("gc" in window) {
      (window as any).gc();
    }

    // 不要なキャッシュのクリア
    this.memoizedResults.clear();
    this.virtualScrollCache.clear();
    
    // イベントリスナーのクリーンアップ
    this.cleanupEventListeners();
  }

  /**
   * レンダリング最適化
   */
  private optimizeRendering(): void {
    console.info("レンダリング最適化を実行");
    
    // 不要なDOM要素の削除
    this.cleanupUnusedElements();
    
    // CSS最適化
    this.optimizeCSS();
    
    // アニメーション最適化
    this.optimizeAnimations();
  }

  /**
   * 重要なリソースのプリロード
   */
  private preloadCriticalResources(): void {
    const criticalResources = [
      "/fonts/main.woff2",
      "/images/logo.png",
      "/css/critical.css",
    ];

    criticalResources.forEach(resource => {
      const link = document.createElement("link");
      link.rel = "preload";
      link.href = resource;
      link.as = resource.endsWith(".css") ? "style" : "image";
      document.head.appendChild(link);
    });
  }

  /**
   * 画像最適化
   */
  private optimizeImages(): void {
    const images = document.querySelectorAll("img[data-src]");
    images.forEach(img => {
      if (img.getAttribute("loading") !== "lazy") {
        img.setAttribute("loading", "lazy");
      }
    });
  }

  /**
   * フォント最適化
   */
  private optimizeFonts(): void {
    // フォントのプリロード
    const fontLink = document.createElement("link");
    fontLink.rel = "preload";
    fontLink.as = "font";
    fontLink.type = "font/woff2";
    fontLink.href = "/fonts/main.woff2";
    fontLink.crossOrigin = "anonymous";
    document.head.appendChild(fontLink);
  }

  /**
   * 不要なDOM要素のクリーンアップ
   */
  private cleanupUnusedElements(): void {
    // 非表示要素の削除
    const hiddenElements = document.querySelectorAll("[style*=\"display: none\"]");
    hiddenElements.forEach(el => {
      if (el.getAttribute("data-keep") !== "true") {
        el.remove();
      }
    });
  }

  /**
   * CSS最適化
   */
  private optimizeCSS(): void {
    // 未使用のCSSルールの削除
    const styleSheets = Array.from(document.styleSheets);
    styleSheets.forEach(sheet => {
      try {
        const rules = Array.from(sheet.cssRules);
        rules.forEach(rule => {
          if (rule.type === CSSRule.STYLE_RULE) {
            const selector = (rule as CSSStyleRule).selectorText;
            if (!document.querySelector(selector)) {
              sheet.deleteRule(Array.from(sheet.cssRules).indexOf(rule));
            }
          }
        });
      } catch (error) {
        // クロスオリジンのスタイルシートは無視
      }
    });
  }

  /**
   * アニメーション最適化
   */
  private optimizeAnimations(): void {
    // 重いアニメーションの無効化
    const heavyAnimations = document.querySelectorAll("[data-heavy-animation]");
    heavyAnimations.forEach(el => {
      (el as HTMLElement).style.animation = "none";
    });
  }

  /**
   * イベントリスナーのクリーンアップ
   */
  private cleanupEventListeners(): void {
    // 実際の実装では、イベントリスナーの追跡が必要
    console.info("イベントリスナークリーンアップ実行");
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
      optimizations: {
        lazyLoading: this.config.enableLazyLoading,
        codeSplitting: this.config.enableCodeSplitting,
        virtualScrolling: this.config.enableVirtualScrolling,
        memoization: this.config.enableMemoization,
        debouncing: this.config.enableDebouncing,
      },
      recommendations: this.generateRecommendations(),
    };
  }

  /**
   * 推奨事項の生成
   */
  private generateRecommendations(): string[] {
    const recommendations: string[] = [];
    const report = this.generatePerformanceReport();

    if (report.lcp > this.config.targetLCP) {
      recommendations.push("LCPが目標値を超えています。画像の最適化とコード分割を推奨します。");
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
    if (this.performanceObserver) {
      this.performanceObserver.disconnect();
    }
    if (this.memoryObserver) {
      this.memoryObserver.disconnect();
    }
    if (this.intersectionObserver) {
      this.intersectionObserver.disconnect();
    }

    // タイマーのクリア
    this.debounceTimers.forEach(timer => clearTimeout(timer));
    this.debounceTimers.clear();

    // キャッシュのクリア
    this.memoizedResults.clear();
    this.virtualScrollCache.clear();
    this.lazyLoadQueue.clear();
  }
}

// デフォルト設定
const defaultConfig: EnhancedPerformanceConfig = {
  maxDataPoints: 3000,
  enableLazyLoading: true,
  enableCodeSplitting: true,
  enableImageOptimization: true,
  enableFontOptimization: true,
  enableVirtualScrolling: true,
  enableMemoization: true,
  enableDebouncing: true,
  enableIntersectionObserver: true,
  enableServiceWorker: true,
  targetLCP: 3000,
  targetFID: 100,
  targetCLS: 0.1,
};

export const enhancedPerformanceOptimizer = new EnhancedPerformanceOptimizer(defaultConfig);
export default EnhancedPerformanceOptimizer;
export type { EnhancedPerformanceConfig, PerformanceMetrics, OptimizationResult };
