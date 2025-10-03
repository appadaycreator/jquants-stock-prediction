/**
 * オフライン機能管理
 * 最後の正常データを使用してオフライン時も機能を継続
 */

export interface OfflineData {
  data: any;
  timestamp: string;
  type: 'stock_data' | 'prediction' | 'analysis';
}

export class OfflineManager {
  private static readonly STORAGE_KEY = 'jquants_offline_data';
  private static readonly MAX_AGE = 24 * 60 * 60 * 1000; // 24時間

  /**
   * オフラインデータの保存
   */
  static async saveOfflineData(data: any, type: OfflineData['type']): Promise<void> {
    try {
      const offlineData: OfflineData = {
        data,
        timestamp: new Date().toISOString(),
        type,
      };

      localStorage.setItem(
        `${OfflineManager.STORAGE_KEY}_${type}`,
        JSON.stringify(offlineData)
      );
    } catch (error) {
      console.error('オフラインデータ保存エラー:', error);
    }
  }

  /**
   * オフラインデータの取得
   */
  static async getOfflineData(type: OfflineData['type']): Promise<any | null> {
    try {
      const stored = localStorage.getItem(`${OfflineManager.STORAGE_KEY}_${type}`);
      if (!stored) {
        return null;
      }

      const offlineData: OfflineData = JSON.parse(stored);
      const age = Date.now() - new Date(offlineData.timestamp).getTime();

      // データが古すぎる場合は無効
      if (age > OfflineManager.MAX_AGE) {
        localStorage.removeItem(`${OfflineManager.STORAGE_KEY}_${type}`);
        return null;
      }

      return offlineData.data;
    } catch (error) {
      console.error('オフラインデータ取得エラー:', error);
      return null;
    }
  }

  /**
   * ネットワーク状態の確認
   */
  static isOnline(): boolean {
    return navigator.onLine;
  }

  /**
   * ネットワーク状態の監視
   */
  static onNetworkChange(callback: (isOnline: boolean) => void): () => void {
    const handleOnline = () => callback(true);
    const handleOffline = () => callback(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // クリーンアップ関数を返す
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }

  /**
   * オフライン時のフォールバック処理
   */
  static async getDataWithFallback<T>(
    fetchFunction: () => Promise<T>,
    type: OfflineData['type'],
    fallbackMessage?: string
  ): Promise<{ data: T | null; isOffline: boolean; message?: string }> {
    try {
      // オンラインの場合は通常の取得を試行
      if (OfflineManager.isOnline()) {
        const data = await fetchFunction();
        await OfflineManager.saveOfflineData(data, type);
        return { data, isOffline: false };
      }
    } catch (error) {
      console.error('データ取得エラー:', error);
    }

    // オフラインまたはエラーの場合はキャッシュデータを使用
    const offlineData = await OfflineManager.getOfflineData(type);
    
    if (offlineData) {
      return {
        data: offlineData,
        isOffline: true,
        message: fallbackMessage || 'オフライン中です。最後の正常データを表示しています。',
      };
    }

    return {
      data: null,
      isOffline: true,
      message: 'データが利用できません。ネットワーク接続を確認してください。',
    };
  }

  /**
   * オフラインデータのクリア
   */
  static clearOfflineData(type?: OfflineData['type']): void {
    if (type) {
      localStorage.removeItem(`${OfflineManager.STORAGE_KEY}_${type}`);
    } else {
      // 全てのオフラインデータをクリア
      Object.values(['stock_data', 'prediction', 'analysis']).forEach(t => {
        localStorage.removeItem(`${OfflineManager.STORAGE_KEY}_${t}`);
      });
    }
  }

  /**
   * オフラインデータの統計情報
   */
  static getOfflineStats(): { [key: string]: { exists: boolean; age: number } } {
    const types: OfflineData['type'][] = ['stock_data', 'prediction', 'analysis'];
    const stats: { [key: string]: { exists: boolean; age: number } } = {};

    types.forEach(type => {
      try {
        const stored = localStorage.getItem(`${OfflineManager.STORAGE_KEY}_${type}`);
        if (stored) {
          const offlineData: OfflineData = JSON.parse(stored);
          const age = Date.now() - new Date(offlineData.timestamp).getTime();
          stats[type] = { exists: true, age };
        } else {
          stats[type] = { exists: false, age: 0 };
        }
      } catch (error) {
        stats[type] = { exists: false, age: 0 };
      }
    });

    return stats;
  }
}
