/**
 * データ鮮度管理マネージャー
 * 複数のデータソースの鮮度を統合的に管理
 */

export interface DataSource {
  id: string;
  name: string;
  lastUpdated: Date;
  ttlMinutes?: number;
  source: "api" | "cache" | "fallback";
  refreshCallback?: () => Promise<void>;
}

export interface FreshnessInfo {
  dataSourceId: string;
  dataSourceName: string;
  lastUpdated: Date;
  cacheStatus: "fresh" | "stale" | "expired";
  ageMinutes: number;
  ttlMinutes?: number;
  nextRefresh?: Date;
  source: "api" | "cache" | "fallback";
}

export interface SystemHealth {
  status: "healthy" | "warning" | "critical";
  activeSources: number;
  totalSources: number;
  issues: string[];
  lastChecked: Date;
}

class EnhancedDataFreshnessManager {
  private static instance: EnhancedDataFreshnessManager;
  private dataSources: Map<string, DataSource> = new Map();
  private refreshCallbacks: Map<string, () => Promise<void>> = new Map();

  private constructor() {}

  /**
   * シングルトンインスタンスを取得
   */
  public static getInstance(): EnhancedDataFreshnessManager {
    if (!EnhancedDataFreshnessManager.instance) {
      EnhancedDataFreshnessManager.instance = new EnhancedDataFreshnessManager();
    }
    return EnhancedDataFreshnessManager.instance;
  }

  /**
   * データソースを登録
   */
  public registerDataSource(
    id: string,
    name: string,
    lastUpdated: Date,
    ttlMinutes?: number,
    source: "api" | "cache" | "fallback" = "api",
    refreshCallback?: () => Promise<void>,
  ): void {
    this.dataSources.set(id, {
      id,
      name,
      lastUpdated,
      ttlMinutes,
      source,
      refreshCallback,
    });

    if (refreshCallback) {
      this.refreshCallbacks.set(id, refreshCallback);
    }
  }

  /**
   * リフレッシュコールバックを登録
   */
  public registerRefreshCallback(id: string, callback: () => Promise<void>): void {
    this.refreshCallbacks.set(id, callback);
  }

  /**
   * データソースの鮮度情報を取得
   */
  public getFreshnessInfo(
    lastUpdated: Date | string | number,
    source: "api" | "cache" | "fallback" = "api",
    ttlMinutes?: number,
  ): FreshnessInfo {
    const now = new Date();
    const lastUpdatedDate = new Date(lastUpdated);
    const ageMinutes = Math.floor((now.getTime() - lastUpdatedDate.getTime()) / (1000 * 60));

    let cacheStatus: "fresh" | "stale" | "expired";
    let nextRefresh: Date | undefined;

    if (ttlMinutes) {
      if (ageMinutes < ttlMinutes * 0.5) {
        cacheStatus = "fresh";
      } else if (ageMinutes < ttlMinutes) {
        cacheStatus = "stale";
        nextRefresh = new Date(lastUpdatedDate.getTime() + ttlMinutes * 60 * 1000);
      } else {
        cacheStatus = "expired";
      }
    } else {
      // TTLが設定されていない場合のデフォルト判定
      if (ageMinutes < 5) {
        cacheStatus = "fresh";
      } else if (ageMinutes < 30) {
        cacheStatus = "stale";
      } else {
        cacheStatus = "expired";
      }
    }

    return {
      dataSourceId: "unknown",
      dataSourceName: "Unknown",
      lastUpdated: lastUpdatedDate,
      cacheStatus,
      ageMinutes,
      ttlMinutes,
      nextRefresh,
      source,
    };
  }

  /**
   * 特定のデータソースの鮮度情報を取得
   */
  public getDataSourceFreshnessInfo(dataSourceId: string): FreshnessInfo | null {
    const dataSource = this.dataSources.get(dataSourceId);
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
  public getAllFreshnessInfo(): Map<string, FreshnessInfo> {
    const freshnessMap = new Map<string, FreshnessInfo>();

    this.dataSources.forEach((dataSource, id) => {
      const freshnessInfo = this.getDataSourceFreshnessInfo(id);
      if (freshnessInfo) {
        freshnessInfo.dataSourceId = id;
        freshnessInfo.dataSourceName = dataSource.name;
        freshnessMap.set(id, freshnessInfo);
      }
    });

    return freshnessMap;
  }

  /**
   * システムヘルスを取得
   */
  public getSystemHealth(): SystemHealth {
    const now = new Date();
    const issues: string[] = [];
    let criticalCount = 0;
    let warningCount = 0;

    this.dataSources.forEach((dataSource) => {
      const freshnessInfo = this.getDataSourceFreshnessInfo(dataSource.id);
      if (freshnessInfo) {
        switch (freshnessInfo.cacheStatus) {
          case "expired":
            criticalCount++;
            issues.push(`${dataSource.name}: データが期限切れ`);
            break;
          case "stale":
            warningCount++;
            break;
        }
      }
    });

    let status: "healthy" | "warning" | "critical";
    if (criticalCount > 0) {
      status = "critical";
    } else if (warningCount > 0) {
      status = "warning";
    } else {
      status = "healthy";
    }

    return {
      status,
      activeSources: this.dataSources.size,
      totalSources: this.dataSources.size,
      issues,
      lastChecked: now,
    };
  }

  /**
   * 特定のデータソースをリフレッシュ
   */
  public async refreshDataSource(dataSourceId: string): Promise<void> {
    const callback = this.refreshCallbacks.get(dataSourceId);
    if (callback) {
      await callback();
    }

    // データソースの最終更新時刻を更新
    const dataSource = this.dataSources.get(dataSourceId);
    if (dataSource) {
      dataSource.lastUpdated = new Date();
      this.dataSources.set(dataSourceId, dataSource);
    }
  }

  /**
   * 全データソースをリフレッシュ
   */
  public async refreshAllDataSources(): Promise<void> {
    const refreshPromises: Promise<void>[] = [];

    this.refreshCallbacks.forEach((callback) => {
      refreshPromises.push(callback());
    });

    await Promise.all(refreshPromises);

    // 全データソースの最終更新時刻を更新
    this.dataSources.forEach((dataSource, id) => {
      dataSource.lastUpdated = new Date();
      this.dataSources.set(id, dataSource);
    });
  }

  /**
   * データソースを削除
   */
  public removeDataSource(dataSourceId: string): void {
    this.dataSources.delete(dataSourceId);
    this.refreshCallbacks.delete(dataSourceId);
  }

  /**
   * 全データソースをクリア
   */
  public clearAllDataSources(): void {
    this.dataSources.clear();
    this.refreshCallbacks.clear();
  }

  /**
   * データソース一覧を取得
   */
  public getDataSources(): DataSource[] {
    return Array.from(this.dataSources.values());
  }

  /**
   * データソース数を取得
   */
  public getDataSourceCount(): number {
    return this.dataSources.size;
  }
}

export default EnhancedDataFreshnessManager;
