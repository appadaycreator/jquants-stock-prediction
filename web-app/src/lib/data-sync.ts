/**
 * データ同期システム
 * PythonバックエンドとWebアプリの連携を管理
 */

interface DataSyncStatus {
  lastUpdate: string;
  status: 'success' | 'error' | 'pending';
  dataSources: {
    stockData: boolean;
    predictions: boolean;
    modelHealth: boolean;
    todayActions: boolean;
    yesterdaySummary: boolean;
  };
  errors: string[];
}

interface DataSyncConfig {
  autoSync: boolean;
  syncInterval: number; // ミリ秒
  retryAttempts: number;
  fallbackEnabled: boolean;
}

class DataSyncManager {
  private config: DataSyncConfig;
  private status: DataSyncStatus;
  private syncTimer: NodeJS.Timeout | null = null;

  constructor(config: Partial<DataSyncConfig> = {}) {
    this.config = {
      autoSync: true,
      syncInterval: 5 * 60 * 1000, // 5分
      retryAttempts: 3,
      fallbackEnabled: true,
      ...config
    };

    this.status = {
      lastUpdate: new Date().toISOString(),
      status: 'pending',
      dataSources: {
        stockData: false,
        predictions: false,
        modelHealth: false,
        todayActions: false,
        yesterdaySummary: false
      },
      errors: []
    };
  }

  /**
   * データ同期の開始
   */
  startSync(): void {
    if (this.config.autoSync) {
      this.syncTimer = setInterval(() => {
        this.performSync();
      }, this.config.syncInterval);
    }
  }

  /**
   * データ同期の停止
   */
  stopSync(): void {
    if (this.syncTimer) {
      clearInterval(this.syncTimer);
      this.syncTimer = null;
    }
  }

  /**
   * 手動データ同期
   */
  async performSync(): Promise<DataSyncStatus> {
    console.log('データ同期開始:', new Date().toISOString());
    this.status.status = 'pending';
    this.status.errors = [];

    try {
      // 各データソースの同期を並列実行
      const syncPromises = [
        this.syncStockData(),
        this.syncPredictions(),
        this.syncModelHealth(),
        this.syncTodayActions(),
        this.syncYesterdaySummary()
      ];

      const results = await Promise.allSettled(syncPromises);
      
      // 結果の評価
      let successCount = 0;
      results.forEach((result, index) => {
        const dataSource = Object.keys(this.status.dataSources)[index] as keyof typeof this.status.dataSources;
        
        if (result.status === 'fulfilled') {
          this.status.dataSources[dataSource] = true;
          successCount++;
        } else {
          this.status.dataSources[dataSource] = false;
          this.status.errors.push(`${dataSource}: ${result.reason}`);
        }
      });

      this.status.status = successCount > 0 ? 'success' : 'error';
      this.status.lastUpdate = new Date().toISOString();

      console.log('データ同期完了:', {
        success: successCount,
        total: results.length,
        errors: this.status.errors
      });

    } catch (error) {
      console.error('データ同期エラー:', error);
      this.status.status = 'error';
      this.status.errors.push(`同期エラー: ${error}`);
    }

    return this.status;
  }

  /**
   * 株価データの同期
   */
  private async syncStockData(): Promise<void> {
    try {
      const response = await fetch('/data/stock_data.json');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      
      // データの検証
      if (!data || !Array.isArray(data)) {
        throw new Error('無効なデータ形式');
      }

      console.log('株価データ同期成功:', data.length, '件');
    } catch (error) {
      console.error('株価データ同期エラー:', error);
      throw error;
    }
  }

  /**
   * 予測データの同期
   */
  private async syncPredictions(): Promise<void> {
    try {
      const response = await fetch('/data/predictions.json');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      
      // データの検証
      if (!data || !data.predictions) {
        throw new Error('無効な予測データ形式');
      }

      console.log('予測データ同期成功:', data.predictions.length, '件');
    } catch (error) {
      console.error('予測データ同期エラー:', error);
      throw error;
    }
  }

  /**
   * モデル健全性の同期
   */
  private async syncModelHealth(): Promise<void> {
    try {
      const response = await fetch('/api/model-health');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      
      // データの検証
      if (!data || !data.status) {
        throw new Error('無効なモデル健全性データ形式');
      }

      console.log('モデル健全性同期成功:', data.status);
    } catch (error) {
      console.error('モデル健全性同期エラー:', error);
      throw error;
    }
  }

  /**
   * 今日のアクションの同期
   */
  private async syncTodayActions(): Promise<void> {
    try {
      const response = await fetch('/api/today-actions');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      
      // データの検証
      if (!data || !data.actions) {
        throw new Error('無効な今日のアクションデータ形式');
      }

      console.log('今日のアクション同期成功:', data.actions.length, '件');
    } catch (error) {
      console.error('今日のアクション同期エラー:', error);
      throw error;
    }
  }

  /**
   * 昨日のサマリーの同期
   */
  private async syncYesterdaySummary(): Promise<void> {
    try {
      const response = await fetch('/api/yesterday-summary');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      
      // データの検証
      if (!data || !data.date) {
        throw new Error('無効な昨日のサマリーデータ形式');
      }

      console.log('昨日のサマリー同期成功:', data.date);
    } catch (error) {
      console.error('昨日のサマリー同期エラー:', error);
      throw error;
    }
  }

  /**
   * 同期状況の取得
   */
  getStatus(): DataSyncStatus {
    return { ...this.status };
  }

  /**
   * 設定の更新
   */
  updateConfig(newConfig: Partial<DataSyncConfig>): void {
    this.config = { ...this.config, ...newConfig };
    
    // 自動同期の設定変更時は再設定
    if (this.config.autoSync !== undefined) {
      this.stopSync();
      if (this.config.autoSync) {
        this.startSync();
      }
    }
  }
}

// シングルトンインスタンス
export const dataSyncManager = new DataSyncManager();

// デフォルト設定での自動開始
if (typeof window !== 'undefined') {
  dataSyncManager.startSync();
}

export default DataSyncManager;
