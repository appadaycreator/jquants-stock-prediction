/**
 * 統合API信頼性システム
 * 強化されたJ-Quantsアダプタ、品質監視、最適化キャッシュを統合
 */

import EnhancedJQuantsAdapter, { JQuantsConfig, StockData, ApiMetrics, DataQualityReport } from "./enhanced-jquants-adapter";
import DataQualityMonitor, { QualityMetrics, QualityReport } from "./data-quality-monitor";
import OptimizedCacheManager, { CacheConfig } from "./optimized-cache-manager";

interface ReliableApiSystemConfig {
  jquants: Partial<JQuantsConfig>;
  cache: Partial<CacheConfig>;
  quality: {
    enableMonitoring: boolean;
    monitoringInterval: number;
    thresholds: {
      minQualityScore: number;
      maxErrorRate: number;
      maxResponseTime: number;
    };
  };
}

interface SystemHealth {
  overall: "healthy" | "degraded" | "unhealthy";
  api: {
    status: string;
    metrics: ApiMetrics;
    lastSuccess: string;
    consecutiveFailures: number;
  };
  cache: {
    hitRate: number;
    totalSize: number;
    efficiency: number;
  };
  quality: {
    overallScore: number;
    activeAnomalies: number;
    trends: {
      quality: "improving" | "stable" | "declining";
      performance: "improving" | "stable" | "declining";
    };
  };
  recommendations: string[];
}

class ReliableApiSystem {
  private adapter: EnhancedJQuantsAdapter;
  private qualityMonitor: DataQualityMonitor;
  private cacheManager: OptimizedCacheManager;
  private config: ReliableApiSystemConfig;
  private isInitialized: boolean = false;

  constructor(config: ReliableApiSystemConfig) {
    this.config = {
      jquants: {
        token: "",
        baseUrl: "https://api.jquants.com/v1",
        timeout: 30000,
        maxRetries: 3,
        retryDelay: 1000,
        rateLimitDelay: 100,
        enableDataValidation: true,
        enableQualityMonitoring: true,
        ...config.jquants,
      },
      cache: {
        maxSize: 100,
        ttl: 24 * 60 * 60 * 1000,
        compressionEnabled: true,
        autoCleanup: true,
        cleanupInterval: 60 * 60 * 1000,
        ...config.cache,
      },
      quality: {
        enableMonitoring: config.quality?.enableMonitoring ?? true,
        monitoringInterval: config.quality?.monitoringInterval ?? 60000,
        thresholds: {
          minQualityScore: config.quality?.thresholds?.minQualityScore ?? 90,
          maxErrorRate: config.quality?.thresholds?.maxErrorRate ?? 5,
          maxResponseTime: config.quality?.thresholds?.maxResponseTime ?? 5000,
        },
      },
    };

    this.adapter = new EnhancedJQuantsAdapter(this.config.jquants);
    this.qualityMonitor = new DataQualityMonitor(this.config.quality.thresholds);
    this.cacheManager = new OptimizedCacheManager(this.config.cache);
  }

  /**
   * システムの初期化
   */
  async initialize(): Promise<{ success: boolean; message: string }> {
    try {
      console.info("信頼性APIシステムの初期化を開始");

      // 接続テスト
      const connectionTest = await this.adapter.testConnection();
      if (!connectionTest.success) {
        throw new Error(`接続テスト失敗: ${connectionTest.message}`);
      }

      // 品質監視の開始
      if (this.config.quality.enableMonitoring) {
        this.qualityMonitor.startMonitoring(this.config.quality.monitoringInterval);
      }

      this.isInitialized = true;
      console.info("信頼性APIシステムの初期化完了");

      return {
        success: true,
        message: "システムが正常に初期化されました",
      };
    } catch (error) {
      console.error("システム初期化エラー:", error);
      return {
        success: false,
        message: `初期化失敗: ${error instanceof Error ? error.message : "不明なエラー"}`,
      };
    }
  }

  /**
   * 株価データの取得（統合版）
   */
  async getStockData(
    symbol: string,
    startDate: string,
    endDate: string,
    options: {
      useCache?: boolean;
      validateData?: boolean;
      monitorQuality?: boolean;
    } = {},
  ): Promise<{
    data: StockData[];
    fromCache: boolean;
    qualityScore?: number;
    metrics?: QualityMetrics;
  }> {
    const startTime = performance.now();
    const useCache = options.useCache !== false;
    const validateData = options.validateData !== false;
    const monitorQuality = options.monitorQuality !== false;

    try {
      console.info("株価データ取得開始", { symbol, startDate, endDate, useCache });

      // キャッシュから取得を試行
      let data: StockData[] = [];
      let fromCache = false;

      if (useCache) {
        const cacheKey = `stock_${symbol}_${startDate}_${endDate}`;
        const cachedData = await this.cacheManager.get<StockData[]>(cacheKey);
        
        if (cachedData && cachedData.length > 0) {
          data = cachedData;
          fromCache = true;
          console.info("キャッシュからデータ取得", { symbol, count: data.length });
        }
      }

      // APIから取得（キャッシュにない場合）
      if (!fromCache) {
        data = await this.adapter.getStockData(symbol, startDate, endDate, false);
        
        // キャッシュに保存
        if (useCache && data.length > 0) {
          const cacheKey = `stock_${symbol}_${startDate}_${endDate}`;
          await this.cacheManager.set(cacheKey, data, {
            ttl: 60 * 60 * 1000, // 1時間
            tags: ["stock_data", symbol],
            priority: 0.8,
          });
        }
      }

      // 品質監視
      let qualityScore: number | undefined;
      let metrics: QualityMetrics | undefined;

      if (monitorQuality && data.length > 0) {
        const responseTime = performance.now() - startTime;
        const errorRate = fromCache ? 0 : 5; // キャッシュの場合はエラー率0
        const dataCompleteness = (data.length / Math.max(1, this.estimateExpectedRecords(startDate, endDate))) * 100;
        const dataAccuracy = this.calculateDataAccuracy(data);

        qualityScore = this.calculateOverallQualityScore(data, responseTime, errorRate, dataCompleteness, dataAccuracy);

        metrics = {
          timestamp: new Date().toISOString(),
          symbol,
          totalRecords: data.length,
          validRecords: data.filter(d => this.isValidRecord(d)).length,
          invalidRecords: data.filter(d => !this.isValidRecord(d)).length,
          qualityScore,
          responseTime,
          errorRate,
          dataCompleteness,
          dataAccuracy,
        };

        this.qualityMonitor.recordMetrics(symbol, metrics);
      }

      console.info("株価データ取得完了", { 
        symbol, 
        count: data.length, 
        fromCache, 
        qualityScore, 
      });

      return {
        data,
        fromCache,
        qualityScore,
        metrics,
      };
    } catch (error) {
      console.error("株価データ取得エラー:", error);
      throw error;
    }
  }

  /**
   * 全銘柄一覧の取得（統合版）
   */
  async getAllSymbols(useCache: boolean = true): Promise<{
    symbols: Array<{ code: string; name: string; sector?: string }>;
    fromCache: boolean;
  }> {
    try {
      if (useCache) {
        const cacheKey = "all_symbols";
        const cachedSymbols = await this.cacheManager.get<Array<{ code: string; name: string; sector?: string }>>(cacheKey);
        
        if (cachedSymbols && cachedSymbols.length > 0) {
          return {
            symbols: cachedSymbols,
            fromCache: true,
          };
        }
      }

      const symbols = await this.adapter.getAllSymbols();
      
      if (useCache && symbols.length > 0) {
        const cacheKey = "all_symbols";
        await this.cacheManager.set(cacheKey, symbols, {
          ttl: 24 * 60 * 60 * 1000, // 24時間
          tags: ["symbols", "reference"],
          priority: 0.9,
        });
      }

      return {
        symbols,
        fromCache: false,
      };
    } catch (error) {
      console.error("全銘柄一覧取得エラー:", error);
      throw error;
    }
  }

  /**
   * システムヘルスチェック
   */
  getSystemHealth(): SystemHealth {
    const apiHealth = this.adapter.getSystemHealth();
    const cacheStats = this.cacheManager.getStats();
    const qualityStatus = this.qualityMonitor.getCurrentQualityStatus();

    // 全体の健康状態の判定
    let overall: "healthy" | "degraded" | "unhealthy" = "healthy";
    const issues: string[] = [];

    if (apiHealth.status === "unhealthy" || qualityStatus.overallHealth === "unhealthy") {
      overall = "unhealthy";
    } else if (apiHealth.status === "degraded" || qualityStatus.overallHealth === "degraded") {
      overall = "degraded";
    }

    // 推奨事項の生成
    const recommendations: string[] = [];

    if (cacheStats.hitRate < 80) {
      recommendations.push("キャッシュヒット率が低いです。キャッシュ戦略の見直しを推奨します。");
    }

    if (apiHealth.metrics.consecutiveFailures > 3) {
      recommendations.push("API接続が不安定です。接続設定の確認を推奨します。");
    }

    if (qualityStatus.activeAnomalies > 5) {
      recommendations.push("データ品質に問題があります。品質監視の強化を推奨します。");
    }

    if (apiHealth.metrics.averageResponseTime > 5000) {
      recommendations.push("応答時間が長いです。ネットワーク最適化を推奨します。");
    }

    return {
      overall,
      api: {
        status: apiHealth.status,
        metrics: apiHealth.metrics,
        lastSuccess: apiHealth.metrics.lastRequestTime,
        consecutiveFailures: apiHealth.metrics.consecutiveFailures,
      },
      cache: {
        hitRate: cacheStats.hitRate,
        totalSize: cacheStats.totalSize,
        efficiency: cacheStats.hitRate / (cacheStats.hitRate + cacheStats.missRate),
      },
      quality: {
        overallScore: qualityStatus.recentMetrics.length > 0 
          ? qualityStatus.recentMetrics.reduce((sum, m) => sum + m.qualityScore, 0) / qualityStatus.recentMetrics.length
          : 100,
        activeAnomalies: qualityStatus.activeAnomalies,
        trends: {
          quality: "stable", // 簡易実装
          performance: "stable",
        },
      },
      recommendations,
    };
  }

  /**
   * 品質レポートの生成
   */
  generateQualityReport(
    timeRange: { start: string; end: string },
    symbols?: string[],
  ): QualityReport {
    return this.qualityMonitor.generateQualityReport(timeRange, symbols);
  }

  /**
   * キャッシュ統計の取得
   */
  getCacheStats() {
    return this.cacheManager.getStats();
  }

  /**
   * キャッシュのクリア
   */
  async clearCache(symbol?: string): Promise<void> {
    if (symbol) {
      await this.cacheManager.deleteByTags([symbol]);
    } else {
      await this.cacheManager.clear();
    }
  }

  /**
   * 設定の更新
   */
  updateConfig(newConfig: Partial<ReliableApiSystemConfig>): void {
    this.config = {
      ...this.config,
      ...newConfig,
    };

    if (newConfig.cache) {
      this.cacheManager.updateConfig(newConfig.cache);
    }

    if (newConfig.quality?.thresholds) {
      this.qualityMonitor.updateThresholds(newConfig.quality.thresholds);
    }

    console.info("システム設定を更新しました", this.config);
  }

  /**
   * システムの停止
   */
  async shutdown(): Promise<void> {
    try {
      this.qualityMonitor.stopMonitoring();
      this.cacheManager.stopCleanup();
      console.info("信頼性APIシステムを停止しました");
    } catch (error) {
      console.error("システム停止エラー:", error);
    }
  }

  // プライベートメソッド

  /**
   * 期待されるレコード数の推定
   */
  private estimateExpectedRecords(startDate: string, endDate: string): number {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffTime = end.getTime() - start.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    // 営業日のみを考慮（土日を除く）
    const businessDays = Math.floor(diffDays * 5 / 7);
    return Math.max(1, businessDays);
  }

  /**
   * データ精度の計算
   */
  private calculateDataAccuracy(data: StockData[]): number {
    if (data.length === 0) return 0;

    let validCount = 0;
    for (const record of data) {
      if (this.isValidRecord(record)) {
        validCount++;
      }
    }

    return (validCount / data.length) * 100;
  }

  /**
   * レコードの妥当性チェック
   */
  private isValidRecord(record: StockData): boolean {
    return (
      record.open > 0 &&
      record.high > 0 &&
      record.low > 0 &&
      record.close > 0 &&
      record.volume >= 0 &&
      record.high >= record.low &&
      record.high >= record.open &&
      record.high >= record.close &&
      record.low <= record.open &&
      record.low <= record.close
    );
  }

  /**
   * 全体品質スコアの計算
   */
  private calculateOverallQualityScore(
    data: StockData[],
    responseTime: number,
    errorRate: number,
    dataCompleteness: number,
    dataAccuracy: number,
  ): number {
    // 各要素の重み付けスコア
    const responseScore = Math.max(0, 100 - (responseTime / 100)); // 応答時間スコア
    const errorScore = Math.max(0, 100 - errorRate * 10); // エラー率スコア
    const completenessScore = dataCompleteness; // 完全性スコア
    const accuracyScore = dataAccuracy; // 精度スコア

    // 重み付け平均
    const weights = {
      response: 0.2,
      error: 0.3,
      completeness: 0.25,
      accuracy: 0.25,
    };

    return Math.round(
      responseScore * weights.response +
      errorScore * weights.error +
      completenessScore * weights.completeness +
      accuracyScore * weights.accuracy,
    );
  }
}

export default ReliableApiSystem;
export type { ReliableApiSystemConfig, SystemHealth };
