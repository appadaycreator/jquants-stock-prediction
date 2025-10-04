/**
 * 新NISA枠管理機能のストレージ管理テスト
 */

import { NisaStorageManager } from '../storage';
import { NisaData, NisaTransaction, QuotaType, TransactionType } from '../types';

// モックデータ
const mockData: NisaData = {
  userProfile: {
    userId: 'test-user',
    startDate: '2024-01-01',
    taxYear: 2024,
    preferences: {
      autoRebalancing: false,
      alertThresholds: {
        growthWarning: 70,
        accumulationWarning: 70,
      },
      notifications: {
        email: false,
        browser: true,
        push: false,
      },
    },
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  },
  quotas: {
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
  transactions: [],
  portfolio: {
    positions: [],
    totalValue: 0,
    totalCost: 0,
    unrealizedProfitLoss: 0,
    realizedProfitLoss: 0,
    taxFreeProfitLoss: 0,
    lastUpdated: '2024-01-01T00:00:00Z',
  },
  settings: {
    autoRebalancing: false,
    alertThresholds: {
      growthWarning: 70,
      accumulationWarning: 70,
    },
    notifications: {
      email: false,
      browser: true,
      push: false,
    },
  },
  lastUpdated: '2024-01-01T00:00:00Z',
};

const mockTransaction: Omit<NisaTransaction, 'id' | 'createdAt' | 'updatedAt'> = {
  type: 'BUY',
  symbol: '7203',
  symbolName: 'トヨタ自動車',
  quantity: 100,
  price: 2500,
  amount: 250_000,
  quotaType: 'GROWTH',
  transactionDate: '2024-01-15',
};

describe('NisaStorageManager', () => {
  let storage: NisaStorageManager;

  beforeEach(() => {
    storage = new NisaStorageManager();
    // テスト前にローカルストレージをクリア
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('データの保存と読み込み', () => {
    it('データを保存できる', async () => {
      const result = await storage.saveData(mockData);
      expect(result).toBe(true);
    });

    it('保存したデータを読み込める', async () => {
      await storage.saveData(mockData);
      const loadedData = await storage.loadData();
      
      expect(loadedData).not.toBeNull();
      expect(loadedData?.userProfile.userId).toBe(mockData.userProfile.userId);
      expect(loadedData?.quotas.growthInvestment.annualLimit).toBe(mockData.quotas.growthInvestment.annualLimit);
    });

    it('データが存在しない場合はnullを返す', async () => {
      const loadedData = await storage.loadData();
      expect(loadedData).toBeNull();
    });
  });

  describe('取引記録の管理', () => {
    beforeEach(async () => {
      await storage.saveData(mockData);
    });

    it('取引記録を追加できる', async () => {
      const result = await storage.addTransaction(mockTransaction);
      
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('追加した取引記録が保存される', async () => {
      await storage.addTransaction(mockTransaction);
      const loadedData = await storage.loadData();
      
      expect(loadedData?.transactions).toHaveLength(1);
      expect(loadedData?.transactions[0].symbol).toBe(mockTransaction.symbol);
      expect(loadedData?.transactions[0].amount).toBe(mockTransaction.amount);
    });

    it('取引記録を更新できる', async () => {
      await storage.addTransaction(mockTransaction);
      const loadedData = await storage.loadData();
      const transaction = loadedData?.transactions[0];
      
      expect(transaction).toBeDefined();
      
      const result = await storage.updateTransaction(transaction!.id, {
        quantity: 200,
        amount: 500_000,
      });
      
      expect(result.isValid).toBe(true);
      
      const updatedData = await storage.loadData();
      const updatedTransaction = updatedData?.transactions[0];
      expect(updatedTransaction?.quantity).toBe(200);
      expect(updatedTransaction?.amount).toBe(500_000);
    });

    it('取引記録を削除できる', async () => {
      await storage.addTransaction(mockTransaction);
      const loadedData = await storage.loadData();
      const transaction = loadedData?.transactions[0];
      
      expect(transaction).toBeDefined();
      
      const result = await storage.deleteTransaction(transaction!.id);
      expect(result.isValid).toBe(true);
      
      const updatedData = await storage.loadData();
      expect(updatedData?.transactions).toHaveLength(0);
    });

    it('存在しない取引の更新は失敗する', async () => {
      const result = await storage.updateTransaction('non-existent-id', {
        quantity: 200,
      });
      
      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });

    it('存在しない取引の削除は失敗する', async () => {
      const result = await storage.deleteTransaction('non-existent-id');
      
      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });
  });

  describe('設定の管理', () => {
    beforeEach(async () => {
      await storage.saveData(mockData);
    });

    it('設定を更新できる', async () => {
      const result = await storage.updateSettings({
        autoRebalancing: true,
        alertThresholds: {
          growthWarning: 80,
          accumulationWarning: 80,
        },
      });
      
      expect(result.isValid).toBe(true);
      
      const loadedData = await storage.loadData();
      expect(loadedData?.settings.autoRebalancing).toBe(true);
      expect(loadedData?.settings.alertThresholds.growthWarning).toBe(80);
    });

    it('ユーザープロファイルを更新できる', async () => {
      const result = await storage.updateUserProfile({
        preferences: {
          autoRebalancing: true,
          alertThresholds: {
            growthWarning: 80,
            accumulationWarning: 80,
          },
          notifications: {
            email: true,
            browser: true,
            push: true,
          },
        },
      });
      
      expect(result.isValid).toBe(true);
      
      const loadedData = await storage.loadData();
      expect(loadedData?.userProfile.preferences.autoRebalancing).toBe(true);
      expect(loadedData?.userProfile.preferences.notifications.email).toBe(true);
    });
  });

  describe('データの整合性チェック', () => {
    it('正常なデータの整合性チェック', async () => {
      await storage.saveData(mockData);
      const result = await storage.validateDataIntegrity();
      
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('無効なデータの整合性チェック', async () => {
      // 無効なデータを直接保存
      localStorage.setItem('nisa_data', JSON.stringify({ invalid: true }));
      const result = await storage.validateDataIntegrity();
      
      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });
  });

  describe('バックアップと復元', () => {
    it('バックアップを作成できる', async () => {
      await storage.saveData(mockData);
      const backup = await storage.createBackup();
      
      expect(backup).not.toBeNull();
      expect(backup).toContain('test-user');
    });

    it('バックアップから復元できる', async () => {
      await storage.saveData(mockData);
      const backup = await storage.createBackup();
      
      // データをクリア
      await storage.clearData();
      
      // バックアップから復元
      const result = await storage.restoreFromBackup(backup!);
      expect(result.isValid).toBe(true);
      
      const loadedData = await storage.loadData();
      expect(loadedData?.userProfile.userId).toBe(mockData.userProfile.userId);
    });

    it('無効なバックアップの復元は失敗する', async () => {
      const result = await storage.restoreFromBackup('invalid-json');
      
      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });
  });

  describe('データのエクスポートとインポート', () => {
    it('データをエクスポートできる', async () => {
      await storage.saveData(mockData);
      const exportData = await storage.exportData();
      
      expect(exportData).not.toBeNull();
      expect(exportData).toContain('test-user');
    });

    it('データをインポートできる', async () => {
      await storage.saveData(mockData);
      const exportData = await storage.exportData();
      
      // データをクリア
      await storage.clearData();
      
      // エクスポートデータをインポート
      const result = await storage.importData(exportData!);
      expect(result.isValid).toBe(true);
      
      const loadedData = await storage.loadData();
      expect(loadedData?.userProfile.userId).toBe(mockData.userProfile.userId);
    });

    it('無効なデータのインポートは失敗する', async () => {
      const result = await storage.importData('invalid-json');
      
      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });
  });

  describe('データのクリア', () => {
    it('データをクリアできる', async () => {
      await storage.saveData(mockData);
      const result = await storage.clearData();
      
      expect(result).toBe(true);
      
      const loadedData = await storage.loadData();
      expect(loadedData).toBeNull();
    });
  });
});
