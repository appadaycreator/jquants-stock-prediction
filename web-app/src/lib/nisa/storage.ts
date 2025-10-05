/**
 * 新NISA枠管理機能のデータストレージ管理
 * ローカルストレージとIndexedDBを使用したデータ永続化
 */

import {
  NisaData,
  NisaTransaction,
  NisaUserProfile,
  NisaSettings,
  NisaQuotaStatus,
  NisaPortfolio,
  QuotaOptimization,
  TaxCalculation,
  QuotaAlert,
  InvestmentOpportunity,
  NisaCalculationResult,
  NisaStatistics,
  ValidationResult,
} from "./types";

export class NisaStorageManager {
  private readonly STORAGE_KEY = "nisa_data";
  private readonly VERSION = "1.0.0";

  /**
   * データを保存
   */
  async saveData(data: NisaData): Promise<boolean> {
    try {
      const dataWithVersion = {
        ...data,
        version: this.VERSION,
        lastSaved: new Date().toISOString(),
      };

      // ローカルストレージに保存
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(dataWithVersion));

      // IndexedDBにも保存（より大きなデータ用）
      await this.saveToIndexedDB(dataWithVersion);

      return true;
    } catch (error) {
      console.error("データ保存エラー:", error);
      return false;
    }
  }

  /**
   * データを読み込み
   */
  async loadData(): Promise<NisaData | null> {
    try {
      // まずローカルストレージから読み込み
      const localData = localStorage.getItem(this.STORAGE_KEY);
      if (localData) {
        const parsed = JSON.parse(localData);
        return this.validateAndMigrateData(parsed);
      }

      // IndexedDBから読み込み
      const indexedData = await this.loadFromIndexedDB();
      if (indexedData) {
        return this.validateAndMigrateData(indexedData);
      }

      return null;
    } catch (error) {
      console.error("データ読み込みエラー:", error);
      return null;
    }
  }

  /**
   * データを削除
   */
  async clearData(): Promise<boolean> {
    try {
      localStorage.removeItem(this.STORAGE_KEY);
      await this.clearIndexedDB();
      return true;
    } catch (error) {
      console.error("データ削除エラー:", error);
      return false;
    }
  }

  /**
   * 取引記録を追加
   */
  async addTransaction(transaction: Omit<NisaTransaction, "id" | "createdAt" | "updatedAt">): Promise<ValidationResult> {
    try {
      const data = await this.loadData();
      if (!data) {
        return {
          isValid: false,
          errors: ["データが見つかりません"],
          warnings: [],
        };
      }

      const newTransaction: NisaTransaction = {
        ...transaction,
        id: `tx_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      data.transactions.push(newTransaction);
      data.lastUpdated = new Date().toISOString();

      await this.saveData(data);

      return {
        isValid: true,
        errors: [],
        warnings: [],
      };
    } catch (error) {
      console.error("取引追加エラー:", error);
      return {
        isValid: false,
        errors: ["取引の追加に失敗しました"],
        warnings: [],
      };
    }
  }

  /**
   * 取引記録を更新
   */
  async updateTransaction(id: string, updates: Partial<NisaTransaction>): Promise<ValidationResult> {
    try {
      const data = await this.loadData();
      if (!data) {
        return {
          isValid: false,
          errors: ["データが見つかりません"],
          warnings: [],
        };
      }

      const transactionIndex = data.transactions.findIndex(t => t.id === id);
      if (transactionIndex === -1) {
        return {
          isValid: false,
          errors: ["取引が見つかりません"],
          warnings: [],
        };
      }

      data.transactions[transactionIndex] = {
        ...data.transactions[transactionIndex],
        ...updates,
        updatedAt: new Date().toISOString(),
      };
      data.lastUpdated = new Date().toISOString();

      await this.saveData(data);

      return {
        isValid: true,
        errors: [],
        warnings: [],
      };
    } catch (error) {
      console.error("取引更新エラー:", error);
      return {
        isValid: false,
        errors: ["取引の更新に失敗しました"],
        warnings: [],
      };
    }
  }

  /**
   * 取引記録を削除
   */
  async deleteTransaction(id: string): Promise<ValidationResult> {
    try {
      const data = await this.loadData();
      if (!data) {
        return {
          isValid: false,
          errors: ["データが見つかりません"],
          warnings: [],
        };
      }

      const transactionIndex = data.transactions.findIndex(t => t.id === id);
      if (transactionIndex === -1) {
        return {
          isValid: false,
          errors: ["取引が見つかりません"],
          warnings: [],
        };
      }

      data.transactions.splice(transactionIndex, 1);
      data.lastUpdated = new Date().toISOString();

      await this.saveData(data);

      return {
        isValid: true,
        errors: [],
        warnings: [],
      };
    } catch (error) {
      console.error("取引削除エラー:", error);
      return {
        isValid: false,
        errors: ["取引の削除に失敗しました"],
        warnings: [],
      };
    }
  }

  /**
   * 設定を更新
   */
  async updateSettings(settings: Partial<NisaSettings>): Promise<ValidationResult> {
    try {
      const data = await this.loadData();
      if (!data) {
        return {
          isValid: false,
          errors: ["データが見つかりません"],
          warnings: [],
        };
      }

      data.settings = {
        ...data.settings,
        ...settings,
      };
      data.lastUpdated = new Date().toISOString();

      await this.saveData(data);

      return {
        isValid: true,
        errors: [],
        warnings: [],
      };
    } catch (error) {
      console.error("設定更新エラー:", error);
      return {
        isValid: false,
        errors: ["設定の更新に失敗しました"],
        warnings: [],
      };
    }
  }

  /**
   * ユーザープロファイルを更新
   */
  async updateUserProfile(profile: Partial<NisaUserProfile>): Promise<ValidationResult> {
    try {
      const data = await this.loadData();
      if (!data) {
        return {
          isValid: false,
          errors: ["データが見つかりません"],
          warnings: [],
        };
      }

      data.userProfile = {
        ...data.userProfile,
        ...profile,
        updatedAt: new Date().toISOString(),
      };
      data.lastUpdated = new Date().toISOString();

      await this.saveData(data);

      return {
        isValid: true,
        errors: [],
        warnings: [],
      };
    } catch (error) {
      console.error("プロファイル更新エラー:", error);
      return {
        isValid: false,
        errors: ["プロファイルの更新に失敗しました"],
        warnings: [],
      };
    }
  }

  /**
   * データのバックアップを作成
   */
  async createBackup(): Promise<string | null> {
    try {
      const data = await this.loadData();
      if (!data) {
        return null;
      }

      const backup = {
        ...data,
        backupCreated: new Date().toISOString(),
        version: this.VERSION,
      };

      return JSON.stringify(backup, null, 2);
    } catch (error) {
      console.error("バックアップ作成エラー:", error);
      return null;
    }
  }

  /**
   * バックアップから復元
   */
  async restoreFromBackup(backupData: string): Promise<ValidationResult> {
    try {
      const parsed = JSON.parse(backupData);
      const validated = this.validateAndMigrateData(parsed);

      if (!validated) {
        return {
          isValid: false,
          errors: ["バックアップデータが無効です"],
          warnings: [],
        };
      }

      await this.saveData(validated);

      return {
        isValid: true,
        errors: [],
        warnings: [],
      };
    } catch (error) {
      console.error("バックアップ復元エラー:", error);
      return {
        isValid: false,
        errors: ["バックアップの復元に失敗しました"],
        warnings: [],
      };
    }
  }

  /**
   * データの整合性をチェック
   */
  async validateDataIntegrity(): Promise<ValidationResult> {
    try {
      const data = await this.loadData();
      if (!data) {
        return {
          isValid: false,
          errors: ["データが見つかりません"],
          warnings: [],
        };
      }

      const errors: string[] = [];
      const warnings: string[] = [];

      // 基本データの検証
      if (!data.userProfile || !data.userProfile.userId) {
        errors.push("ユーザープロファイルが無効です");
      }

      if (!data.quotas) {
        errors.push("投資枠情報が無効です");
      }

      if (!Array.isArray(data.transactions)) {
        errors.push("取引履歴が無効です");
      }

      if (!data.portfolio) {
        errors.push("ポートフォリオ情報が無効です");
      }

      // 取引データの整合性チェック
      for (const transaction of data.transactions) {
        if (!transaction.id || !transaction.symbol || !transaction.type) {
          errors.push(`無効な取引データ: ${transaction.id || "unknown"}`);
        }
      }

      // ポートフォリオデータの整合性チェック
      if (data.portfolio.positions) {
        for (const position of data.portfolio.positions) {
          if (!position.symbol || position.quantity < 0) {
            warnings.push(`疑わしいポジションデータ: ${position.symbol}`);
          }
        }
      }

      return {
        isValid: errors.length === 0,
        errors,
        warnings,
      };
    } catch (error) {
      console.error("データ整合性チェックエラー:", error);
      return {
        isValid: false,
        errors: ["データの整合性チェックに失敗しました"],
        warnings: [],
      };
    }
  }

  /**
   * データをエクスポート
   */
  async exportData(): Promise<string | null> {
    try {
      const data = await this.loadData();
      if (!data) {
        return null;
      }

      const exportData = {
        ...data,
        exportedAt: new Date().toISOString(),
        version: this.VERSION,
      };

      return JSON.stringify(exportData, null, 2);
    } catch (error) {
      console.error("データエクスポートエラー:", error);
      return null;
    }
  }

  /**
   * データをインポート
   */
  async importData(importData: string): Promise<ValidationResult> {
    try {
      const parsed = JSON.parse(importData);
      const validated = this.validateAndMigrateData(parsed);

      if (!validated) {
        return {
          isValid: false,
          errors: ["インポートデータが無効です"],
          warnings: [],
        };
      }

      await this.saveData(validated);

      return {
        isValid: true,
        errors: [],
        warnings: [],
      };
    } catch (error) {
      console.error("データインポートエラー:", error);
      return {
        isValid: false,
        errors: ["データのインポートに失敗しました"],
        warnings: [],
      };
    }
  }

  /**
   * IndexedDBに保存
   */
  private async saveToIndexedDB(data: any): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open("NisaDB", 1);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        const db = request.result;
        const transaction = db.transaction(["nisaData"], "readwrite");
        const store = transaction.objectStore("nisaData");
        
        store.put(data, "main");
        transaction.oncomplete = () => resolve();
        transaction.onerror = () => reject(transaction.error);
      };

      request.onupgradeneeded = () => {
        const db = request.result;
        if (!db.objectStoreNames.contains("nisaData")) {
          db.createObjectStore("nisaData");
        }
      };
    });
  }

  /**
   * IndexedDBから読み込み
   */
  private async loadFromIndexedDB(): Promise<any> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open("NisaDB", 1);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        const db = request.result;
        const transaction = db.transaction(["nisaData"], "readonly");
        const store = transaction.objectStore("nisaData");
        
        const getRequest = store.get("main");
        getRequest.onsuccess = () => resolve(getRequest.result);
        getRequest.onerror = () => reject(getRequest.error);
      };

      request.onupgradeneeded = () => {
        const db = request.result;
        if (!db.objectStoreNames.contains("nisaData")) {
          db.createObjectStore("nisaData");
        }
      };
    });
  }

  /**
   * IndexedDBをクリア
   */
  private async clearIndexedDB(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.deleteDatabase("NisaDB");
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * データの検証とマイグレーション
   */
  private validateAndMigrateData(data: any): NisaData | null {
    try {
      // 基本的なデータ構造の検証
      if (!data || typeof data !== "object") {
        return null;
      }

      // デフォルト値の設定
      const defaultData: NisaData = {
        userProfile: {
          userId: data.userProfile?.userId || `user_${Date.now()}`,
          startDate: data.userProfile?.startDate || new Date().toISOString(),
          taxYear: data.userProfile?.taxYear || new Date().getFullYear(),
          preferences: {
            autoRebalancing: data.userProfile?.preferences?.autoRebalancing || false,
            alertThresholds: {
              growthWarning: data.userProfile?.preferences?.alertThresholds?.growthWarning || 70,
              accumulationWarning: data.userProfile?.preferences?.alertThresholds?.accumulationWarning || 70,
            },
            notifications: {
              email: data.userProfile?.preferences?.notifications?.email || false,
              browser: data.userProfile?.preferences?.notifications?.browser || true,
              push: data.userProfile?.preferences?.notifications?.push || false,
            },
          },
          createdAt: data.userProfile?.createdAt || new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
        quotas: data.quotas || {
          growthInvestment: {
            annualLimit: 2_400_000,
            taxFreeLimit: 12_000_000,
            usedAmount: 0,
            availableAmount: 2_400_000,
            utilizationRate: 0,
          },
          accumulationInvestment: {
            annualLimit: 400_000,
            taxFreeLimit: 2_000_000,
            usedAmount: 0,
            availableAmount: 400_000,
            utilizationRate: 0,
          },
          quotaReuse: {
            growthAvailable: 0,
            accumulationAvailable: 0,
            nextYearAvailable: 0,
          },
        },
        transactions: Array.isArray(data.transactions) ? data.transactions : [],
        portfolio: data.portfolio || {
          positions: [],
          totalValue: 0,
          totalCost: 0,
          unrealizedProfitLoss: 0,
          realizedProfitLoss: 0,
          taxFreeProfitLoss: 0,
          lastUpdated: new Date().toISOString(),
        },
        settings: {
          autoRebalancing: data.settings?.autoRebalancing || false,
          alertThresholds: {
            growthWarning: data.settings?.alertThresholds?.growthWarning || 70,
            accumulationWarning: data.settings?.alertThresholds?.accumulationWarning || 70,
          },
          notifications: {
            email: data.settings?.notifications?.email || false,
            browser: data.settings?.notifications?.browser || true,
            push: data.settings?.notifications?.push || false,
          },
        },
        lastUpdated: new Date().toISOString(),
      };

      return defaultData;
    } catch (error) {
      console.error("データ検証エラー:", error);
      return null;
    }
  }
}
