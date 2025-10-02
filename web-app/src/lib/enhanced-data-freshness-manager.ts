/**
 * 強化版データ鮮度管理システム
 * リアルタイムデータの正確な表示と鮮度バッジの実装
 */

interface DataFreshnessConfig {
  freshThresholdMinutes: number;
  staleThresholdMinutes: number;
  expiredThresholdMinutes: number;
  defaultTtlMinutes: number;
  enableAutoRefresh: boolean;
  refreshIntervalMs: number;
}

interface DataFreshnessInfo {
  isFresh: boolean;
  lastUpdated: Date;
  ageMinutes: number;
  cacheStatus: "fresh" | "stale" | "expired";
  source: "api" | "cache" | "fallback";
  ttlMinutes: number;
  nextRefresh: Date;
  qualityScore?: number;
}

interface DataSource {
  id: string;
  name: string;
  lastUpdated: Date;
  ttlMinutes: number;
  source: "api" | "cache" | "fallback";
  qualityScore: number;
  isActive: boolean;
}

class EnhancedDataFreshnessManager {
  private static instance: EnhancedDataFreshnessManager;
  private config: DataFreshnessConfig;
  private dataSources: Map<string, DataSource> = new Map();
  private refreshCallbacks: Map<string, () => Promise<void>> = new Map();
  private refreshInterval: NodeJS.Timeout | null = null;

  constructor(config: Partial<DataFreshnessConfig> = {}) {
    this.config = {
      freshThresholdMinutes: 15,
      staleThresholdMinutes: 60,
      expiredThresholdMinutes: 240,
      defaultTtlMinutes: 60,
      enableAutoRefresh: true,
      refreshIntervalMs: 30000, // 30秒
      ...config,
    };

    this.startAutoRefresh();
  }

  static getInstance(config?: Partial<DataFreshnessConfig>): EnhancedDataFreshnessManager {
    if (!EnhancedDataFreshnessManager.instance) {
      EnhancedDataFreshnessManager.instance = new EnhancedDataFreshnessManager(config);
    }
    return EnhancedDataFreshnessManager.instance;
  }

  /**
   * データソースの登録
   */
  registerDataSource(
    id: string,
    name: string,
    lastUpdated: Date,
    ttlMinutes: number = this.config.defaultTtlMinutes,
    source: "api" | "cache" | "fallback" = "cache",
    qualityScore: number = 100,
  ): void {
    this.dataSources.set(id, {
      id,
      name,
      lastUpdated,
      ttlMinutes,
      source,
      qualityScore,
      isActive: true,
    });
  }

  /**
   * リフレッシュコールバックの登録
   */
  registerRefreshCallback(id: string, callback: () => Promise<void>): void {
    this.refreshCallbacks.set(id, callback);
  }

  /**
   * データの鮮度情報を取得
   */
  getFreshnessInfo(
    lastUpdated: Date | string | number,
    source: "api" | "cache" | "fallback" = "cache",
    ttlMinutes?: number,
  ): DataFreshnessInfo {
    const now = new Date();
    const updateTime = new Date(lastUpdated);
    const ageMinutes = Math.floor((now.getTime() - updateTime.getTime()) / (1000 * 60));
    const ttl = ttlMinutes || this.config.defaultTtlMinutes;

    let cacheStatus: DataFreshnessInfo["cacheStatus"];
    let isFresh: boolean;

    if (ageMinutes <= this.config.freshThresholdMinutes) {
      cacheStatus = "fresh";
      isFresh = true;
    } else if (ageMinutes <= this.config.staleThresholdMinutes) {
      cacheStatus = "stale";
      isFresh = false;
    } else if (ageMinutes <= this.config.expiredThresholdMinutes) {
      cacheStatus = "stale";
      isFresh = false;
    } else {
      cacheStatus = "expired";
      isFresh = false;
    }

    // TTLを超えている場合は期限切れ
    if (ageMinutes > ttl) {
      cacheStatus = "expired";
      isFresh = false;
    }

    // APIから直接取得した場合は常にフレッシュ
    if (source === "api") {
      cacheStatus = "fresh";
      isFresh = true;
    }

    const nextRefresh = new Date(updateTime.getTime() + (ttl * 60 * 1000));

    return {
      isFresh,
      lastUpdated: updateTime,
      ageMinutes,
      cacheStatus,
      source,
      ttlMinutes: ttl,
      nextRefresh,
    };
  }

  /**
   * データソースの鮮度情報を取得
   */
  getDataSourceFreshness(id: string): DataFreshnessInfo | null {
    const dataSource = this.dataSources.get(id);
    if (!dataSource) {
      return null;
    }

    return this.getFreshnessInfo(
      dataSource.lastUpdated,
      dataSource.source,
      dataSource.ttlMinutes,
    );
  }

  /**
   * 全データソースの鮮度情報を取得
   */
  getAllFreshnessInfo(): Map<string, DataFreshnessInfo> {
    const freshnessMap = new Map<string, DataFreshnessInfo>();
    
    this.dataSources.forEach((dataSource, id) => {
      const freshness = this.getDataSourceFreshness(id);
      if (freshness) {
        freshnessMap.set(id, freshness);
      }
    });

    return freshnessMap;
  }

  /**
   * 鮮度バッジの情報を取得
   */
  getFreshnessBadgeInfo(id: string): {
    status: "fresh" | "stale" | "expired";
    color: string;
    text: string;
    icon: string;
  } {
    const freshness = this.getDataSourceFreshness(id);
    if (!freshness) {
      return {
        status: "expired",
        color: "bg-red-100 text-red-800",
        text: "データなし",
        icon: "❌",
      };
    }

    switch (freshness.cacheStatus) {
      case "fresh":
        return {
          status: "fresh",
          color: "bg-green-100 text-green-800",
          text: `Fresh (${freshness.ageMinutes}分前)`,
          icon: "🟢",
        };
      case "stale":
        return {
          status: "stale",
          color: "bg-yellow-100 text-yellow-800",
          text: `Stale (${freshness.ageMinutes}分前)`,
          icon: "🟡",
        };
      case "expired":
        return {
          status: "expired",
          color: "bg-red-100 text-red-800",
          text: `Expired (${freshness.ageMinutes}分前)`,
          icon: "🔴",
        };
      default:
        return {
          status: "expired",
          color: "bg-gray-100 text-gray-800",
          text: "不明",
          icon: "❓",
        };
    }
  }

  /**
   * データソースの更新
   */
  updateDataSource(
    id: string,
    lastUpdated: Date,
    source: "api" | "cache" | "fallback" = "api",
    qualityScore: number = 100,
  ): void {
    const dataSource = this.dataSources.get(id);
    if (dataSource) {
      dataSource.lastUpdated = lastUpdated;
      dataSource.source = source;
      dataSource.qualityScore = qualityScore;
      this.dataSources.set(id, dataSource);
    }
  }

  /**
   * 自動リフレッシュの開始
   */
  private startAutoRefresh(): void {
    if (!this.config.enableAutoRefresh) {
      return;
    }

    this.refreshInterval = setInterval(() => {
      this.performAutoRefresh();
    }, this.config.refreshIntervalMs);
  }

  /**
   * 自動リフレッシュの実行
   */
  private async performAutoRefresh(): Promise<void> {
    const now = new Date();
    const staleDataSources: string[] = [];

    // 古いデータソースを特定
    this.dataSources.forEach((dataSource, id) => {
      if (!dataSource.isActive) {
        return;
      }

      const freshness = this.getDataSourceFreshness(id);
      if (freshness && freshness.cacheStatus === "stale") {
        staleDataSources.push(id);
      }
    });

    // 古いデータソースをリフレッシュ
    for (const id of staleDataSources) {
      const callback = this.refreshCallbacks.get(id);
      if (callback) {
        try {
          await callback();
          console.info(`データソース ${id} の自動リフレッシュ完了`);
        } catch (error) {
          console.error(`データソース ${id} の自動リフレッシュエラー:`, error);
        }
      }
    }
  }

  /**
   * 手動リフレッシュ
   */
  async refreshDataSource(id: string): Promise<boolean> {
    const callback = this.refreshCallbacks.get(id);
    if (!callback) {
      console.warn(`データソース ${id} のリフレッシュコールバックが見つかりません`);
      return false;
    }

    try {
      await callback();
      this.updateDataSource(id, new Date(), "api");
      console.info(`データソース ${id} の手動リフレッシュ完了`);
      return true;
    } catch (error) {
      console.error(`データソース ${id} の手動リフレッシュエラー:`, error);
      return false;
    }
  }

  /**
   * 全データソースのリフレッシュ
   */
  async refreshAllDataSources(): Promise<{ success: number; failed: number }> {
    let success = 0;
    let failed = 0;

    for (const [id, dataSource] of this.dataSources) {
      if (!dataSource.isActive) {
        continue;
      }

      const result = await this.refreshDataSource(id);
      if (result) {
        success++;
      } else {
        failed++;
      }
    }

    return { success, failed };
  }

  /**
   * データソースの無効化
   */
  deactivateDataSource(id: string): void {
    const dataSource = this.dataSources.get(id);
    if (dataSource) {
      dataSource.isActive = false;
      this.dataSources.set(id, dataSource);
    }
  }

  /**
   * データソースの有効化
   */
  activateDataSource(id: string): void {
    const dataSource = this.dataSources.get(id);
    if (dataSource) {
      dataSource.isActive = true;
      this.dataSources.set(id, dataSource);
    }
  }

  /**
   * システムヘルスチェック
   */
  getSystemHealth(): {
    status: "healthy" | "warning" | "critical";
    totalSources: number;
    activeSources: number;
    freshSources: number;
    staleSources: number;
    expiredSources: number;
    issues: string[];
  } {
    const totalSources = this.dataSources.size;
    let activeSources = 0;
    let freshSources = 0;
    let staleSources = 0;
    let expiredSources = 0;
    const issues: string[] = [];

    this.dataSources.forEach((dataSource, id) => {
      if (!dataSource.isActive) {
        return;
      }

      activeSources++;
      const freshness = this.getDataSourceFreshness(id);
      
      if (freshness) {
        switch (freshness.cacheStatus) {
          case "fresh":
            freshSources++;
            break;
          case "stale":
            staleSources++;
            break;
          case "expired":
            expiredSources++;
            issues.push(`データソース ${id} が期限切れです`);
            break;
        }
      }
    });

    let status: "healthy" | "warning" | "critical" = "healthy";
    
    if (expiredSources > 0) {
      status = "critical";
    } else if (staleSources > activeSources * 0.5) {
      status = "warning";
    }

    return {
      status,
      totalSources,
      activeSources,
      freshSources,
      staleSources,
      expiredSources,
      issues,
    };
  }

  /**
   * クリーンアップ
   */
  destroy(): void {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
      this.refreshInterval = null;
    }
    
    this.dataSources.clear();
    this.refreshCallbacks.clear();
  }
}

export default EnhancedDataFreshnessManager;
export type { DataFreshnessConfig, DataFreshnessInfo, DataSource };
