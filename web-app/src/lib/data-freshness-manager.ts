/**
 * データ鮮度管理システム
 * データの鮮度を判定し、適切な表示を行うためのユーティリティ
 */

export interface DataFreshnessInfo {
  isFresh: boolean;
  lastUpdated: Date;
  ageMinutes: number;
  cacheStatus: 'fresh' | 'stale' | 'expired' | 'unknown';
  source: 'api' | 'cache' | 'fallback';
  ttlMinutes?: number;
  nextRefresh?: Date;
}

export interface FreshnessConfig {
  freshThresholdMinutes: number; // フレッシュとみなす時間（分）
  staleThresholdMinutes: number; // ステイルとみなす時間（分）
  expiredThresholdMinutes: number; // 期限切れとみなす時間（分）
  defaultTtlMinutes: number; // デフォルトTTL（分）
}

export class DataFreshnessManager {
  private static instance: DataFreshnessManager;
  private config: FreshnessConfig;

  constructor(config?: Partial<FreshnessConfig>) {
    this.config = {
      freshThresholdMinutes: 15, // 15分以内はフレッシュ
      staleThresholdMinutes: 60, // 1時間以内はステイル
      expiredThresholdMinutes: 240, // 4時間以上は期限切れ
      defaultTtlMinutes: 60, // デフォルト1時間
      ...config,
    };
  }

  static getInstance(config?: Partial<FreshnessConfig>): DataFreshnessManager {
    if (!DataFreshnessManager.instance) {
      DataFreshnessManager.instance = new DataFreshnessManager(config);
    }
    return DataFreshnessManager.instance;
  }

  /**
   * データの鮮度情報を取得
   */
  getFreshnessInfo(
    lastUpdated: Date | string | number,
    source: 'api' | 'cache' | 'fallback' = 'cache',
    ttlMinutes?: number
  ): DataFreshnessInfo {
    const now = new Date();
    const updateTime = new Date(lastUpdated);
    const ageMinutes = Math.floor((now.getTime() - updateTime.getTime()) / (1000 * 60));
    const ttl = ttlMinutes || this.config.defaultTtlMinutes;

    let cacheStatus: DataFreshnessInfo['cacheStatus'];
    let isFresh: boolean;

    if (ageMinutes <= this.config.freshThresholdMinutes) {
      cacheStatus = 'fresh';
      isFresh = true;
    } else if (ageMinutes <= this.config.staleThresholdMinutes) {
      cacheStatus = 'stale';
      isFresh = false;
    } else if (ageMinutes <= this.config.expiredThresholdMinutes) {
      cacheStatus = 'stale';
      isFresh = false;
    } else {
      cacheStatus = 'expired';
      isFresh = false;
    }

    // TTLを超えている場合は期限切れ
    if (ageMinutes > ttl) {
      cacheStatus = 'expired';
      isFresh = false;
    }

    // APIから直接取得した場合は常にフレッシュ
    if (source === 'api') {
      cacheStatus = 'fresh';
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
   * キャッシュメタデータから鮮度情報を取得
   */
  getFreshnessFromCacheMeta(
    cacheMeta: { exists: boolean; timestamp?: number; ttl?: number },
    source: 'api' | 'cache' | 'fallback' = 'cache'
  ): DataFreshnessInfo | null {
    if (!cacheMeta.exists || !cacheMeta.timestamp) {
      return null;
    }

    return this.getFreshnessInfo(
      cacheMeta.timestamp,
      source,
      cacheMeta.ttl
    );
  }

  /**
   * 複数のデータソースの鮮度情報を統合
   */
  getCombinedFreshnessInfo(
    freshnessInfos: DataFreshnessInfo[]
  ): {
    overallStatus: 'all_fresh' | 'mixed' | 'all_stale' | 'all_expired';
    oldestData: DataFreshnessInfo | null;
    freshCount: number;
    staleCount: number;
    expiredCount: number;
    totalCount: number;
  } {
    if (freshnessInfos.length === 0) {
      return {
        overallStatus: 'all_expired',
        oldestData: null,
        freshCount: 0,
        staleCount: 0,
        expiredCount: 0,
        totalCount: 0,
      };
    }

    const freshCount = freshnessInfos.filter(info => info.isFresh).length;
    const staleCount = freshnessInfos.filter(info => info.cacheStatus === 'stale').length;
    const expiredCount = freshnessInfos.filter(info => info.cacheStatus === 'expired').length;
    const totalCount = freshnessInfos.length;

    const oldestData = freshnessInfos.reduce((oldest, current) => 
      current.ageMinutes > oldest.ageMinutes ? current : oldest
    );

    let overallStatus: 'all_fresh' | 'mixed' | 'all_stale' | 'all_expired';
    if (freshCount === totalCount) {
      overallStatus = 'all_fresh';
    } else if (expiredCount === totalCount) {
      overallStatus = 'all_expired';
    } else if (staleCount === totalCount) {
      overallStatus = 'all_stale';
    } else {
      overallStatus = 'mixed';
    }

    return {
      overallStatus,
      oldestData,
      freshCount,
      staleCount,
      expiredCount,
      totalCount,
    };
  }

  /**
   * 鮮度バッジのスタイルを取得
   */
  getFreshnessBadgeStyle(cacheStatus: DataFreshnessInfo['cacheStatus']): {
    className: string;
    icon: string;
    text: string;
    color: string;
  } {
    switch (cacheStatus) {
      case 'fresh':
        return {
          className: 'bg-green-100 text-green-800 border-green-200',
          icon: '✓',
          text: 'Fresh',
          color: 'green',
        };
      case 'stale':
        return {
          className: 'bg-yellow-100 text-yellow-800 border-yellow-200',
          icon: '⚠',
          text: 'Stale',
          color: 'yellow',
        };
      case 'expired':
        return {
          className: 'bg-red-100 text-red-800 border-red-200',
          icon: '✗',
          text: 'Expired',
          color: 'red',
        };
      default:
        return {
          className: 'bg-gray-100 text-gray-800 border-gray-200',
          icon: '?',
          text: 'Unknown',
          color: 'gray',
        };
    }
  }

  /**
   * 相対時間の表示文字列を取得
   */
  getRelativeTimeString(ageMinutes: number): string {
    if (ageMinutes < 1) {
      return 'たった今';
    } else if (ageMinutes < 60) {
      return `${ageMinutes}分前`;
    } else if (ageMinutes < 1440) {
      const hours = Math.floor(ageMinutes / 60);
      return `${hours}時間前`;
    } else {
      const days = Math.floor(ageMinutes / 1440);
      return `${days}日前`;
    }
  }

  /**
   * 次の更新時刻の表示文字列を取得
   */
  getNextRefreshString(nextRefresh: Date): string {
    const now = new Date();
    const diffMinutes = Math.floor((nextRefresh.getTime() - now.getTime()) / (1000 * 60));
    
    if (diffMinutes <= 0) {
      return '更新が必要';
    } else if (diffMinutes < 60) {
      return `${diffMinutes}分後に更新`;
    } else {
      const hours = Math.floor(diffMinutes / 60);
      return `${hours}時間後に更新`;
    }
  }
}

// デフォルトインスタンス
export const freshnessManager = DataFreshnessManager.getInstance();
