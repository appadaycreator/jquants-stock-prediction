/**
 * 新NISA枠管理機能のストレージ管理統合テスト
 */

import { NisaStorageManager } from "../storage";
import { NisaData, NisaTransaction } from "../types";

// モックデータ
const createMockData = (): NisaData => ({
  userProfile: {
    userId: "test-user",
    startDate: "2024-01-01",
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
    createdAt: "2024-01-01T00:00:00Z",
    updatedAt: "2024-01-01T00:00:00Z",
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
    lastUpdated: "2024-01-01T00:00:00Z",
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
  lastUpdated: "2024-01-01T00:00:00Z",
});

describe("NisaStorageManager Integration Tests", () => {
  let storage: NisaStorageManager;

  beforeEach(() => {
    storage = new NisaStorageManager();
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe("完全なデータフローのテスト", () => {
    it("データの保存・読み込み・更新・削除の完全フロー", async () => {
      const mockData = createMockData();
      
      // 1. データを保存
      const saveResult = await storage.saveData(mockData);
      expect(saveResult).toBe(true);

      // 2. データを読み込み
      const loadedData = await storage.loadData();
      expect(loadedData).not.toBeNull();
      expect(loadedData?.userProfile.userId).toBe(mockData.userProfile.userId);

      // 3. 取引を追加
      const transaction: Omit<NisaTransaction, "id" | "createdAt" | "updatedAt"> = {
        type: "BUY",
        symbol: "7203",
        symbolName: "トヨタ自動車",
        quantity: 100,
        price: 2500,
        amount: 250_000,
        quotaType: "GROWTH",
        transactionDate: "2024-01-15",
      };

      const addResult = await storage.addTransaction(transaction);
      expect(addResult.isValid).toBe(true);

      // 4. 取引が追加されたことを確認
      const updatedData = await storage.loadData();
      expect(updatedData?.transactions).toHaveLength(1);
      expect(updatedData?.transactions[0].symbol).toBe("7203");

      // 5. 取引を更新
      const transactionId = updatedData?.transactions[0].id;
      expect(transactionId).toBeDefined();

      const updateResult = await storage.updateTransaction(transactionId!, {
        quantity: 200,
        amount: 500_000,
      });
      expect(updateResult.isValid).toBe(true);

      // 6. 更新が反映されたことを確認
      const updatedData2 = await storage.loadData();
      expect(updatedData2?.transactions[0].quantity).toBe(200);
      expect(updatedData2?.transactions[0].amount).toBe(500_000);

      // 7. 取引を削除
      const deleteResult = await storage.deleteTransaction(transactionId!);
      expect(deleteResult.isValid).toBe(true);

      // 8. 削除が反映されたことを確認
      const finalData = await storage.loadData();
      expect(finalData?.transactions).toHaveLength(0);
    });

    it("設定の更新フロー", async () => {
      const mockData = createMockData();
      await storage.saveData(mockData);

      // 設定を更新
      const updateResult = await storage.updateSettings({
        autoRebalancing: true,
        alertThresholds: {
          growthWarning: 80,
          accumulationWarning: 80,
        },
      });

      expect(updateResult.isValid).toBe(true);

      // 更新が反映されたことを確認
      const updatedData = await storage.loadData();
      expect(updatedData?.settings.autoRebalancing).toBe(true);
      expect(updatedData?.settings.alertThresholds.growthWarning).toBe(80);
    });

    it("ユーザープロファイルの更新フロー", async () => {
      const mockData = createMockData();
      await storage.saveData(mockData);

      // プロファイルを更新
      const updateResult = await storage.updateUserProfile({
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

      expect(updateResult.isValid).toBe(true);

      // 更新が反映されたことを確認
      const updatedData = await storage.loadData();
      expect(updatedData?.userProfile.preferences.autoRebalancing).toBe(true);
      expect(updatedData?.userProfile.preferences.notifications.email).toBe(true);
    });
  });

  describe("バックアップと復元のテスト", () => {
    it("バックアップの作成と復元", async () => {
      const mockData = createMockData();
      await storage.saveData(mockData);

      // バックアップを作成
      const backup = await storage.createBackup();
      expect(backup).not.toBeNull();
      expect(backup).toContain("test-user");

      // データをクリア
      await storage.clearData();
      let clearedData = await storage.loadData();
      expect(clearedData).toBeNull();

      // バックアップから復元
      const restoreResult = await storage.restoreFromBackup(backup!);
      expect(restoreResult.isValid).toBe(true);

      // 復元されたデータを確認
      const restoredData = await storage.loadData();
      expect(restoredData).not.toBeNull();
      expect(restoredData?.userProfile.userId).toBe("test-user");
    });

    it("無効なバックアップの処理", async () => {
      const restoreResult = await storage.restoreFromBackup("invalid-json");
      expect(restoreResult.isValid).toBe(false);
      expect(restoreResult.errors.length).toBeGreaterThan(0);
    });
  });

  describe("データの整合性チェック", () => {
    it("正常なデータの整合性チェック", async () => {
      const mockData = createMockData();
      await storage.saveData(mockData);

      const integrityResult = await storage.validateDataIntegrity();
      expect(integrityResult.isValid).toBe(true);
      expect(integrityResult.errors).toHaveLength(0);
    });

    it("無効なデータの整合性チェック", async () => {
      // 無効なデータを直接保存
      localStorage.setItem("nisa_data", JSON.stringify({ invalid: true }));

      const integrityResult = await storage.validateDataIntegrity();
      expect(integrityResult.isValid).toBe(false);
      expect(integrityResult.errors.length).toBeGreaterThan(0);
    });
  });

  describe("エクスポートとインポートのテスト", () => {
    it("データのエクスポートとインポート", async () => {
      const mockData = createMockData();
      await storage.saveData(mockData);

      // データをエクスポート
      const exportData = await storage.exportData();
      expect(exportData).not.toBeNull();
      expect(exportData).toContain("test-user");

      // データをクリア
      await storage.clearData();
      let clearedData = await storage.loadData();
      expect(clearedData).toBeNull();

      // エクスポートデータをインポート
      const importResult = await storage.importData(exportData!);
      expect(importResult.isValid).toBe(true);

      // インポートされたデータを確認
      const importedData = await storage.loadData();
      expect(importedData).not.toBeNull();
      expect(importedData?.userProfile.userId).toBe("test-user");
    });

    it("無効なデータのインポート", async () => {
      const importResult = await storage.importData("invalid-json");
      expect(importResult.isValid).toBe(false);
      expect(importResult.errors.length).toBeGreaterThan(0);
    });
  });

  describe("エラーハンドリングのテスト", () => {
    it("存在しない取引の更新", async () => {
      const mockData = createMockData();
      await storage.saveData(mockData);

      const updateResult = await storage.updateTransaction("non-existent-id", {
        quantity: 200,
      });

      expect(updateResult.isValid).toBe(false);
      expect(updateResult.errors.length).toBeGreaterThan(0);
    });

    it("存在しない取引の削除", async () => {
      const mockData = createMockData();
      await storage.saveData(mockData);

      const deleteResult = await storage.deleteTransaction("non-existent-id");
      expect(deleteResult.isValid).toBe(false);
      expect(deleteResult.errors.length).toBeGreaterThan(0);
    });
  });

  describe("データの永続化テスト", () => {
    it("複数回の保存と読み込み", async () => {
      const mockData = createMockData();
      
      // 複数回保存
      await storage.saveData(mockData);
      await storage.saveData(mockData);
      await storage.saveData(mockData);

      // 読み込み
      const loadedData = await storage.loadData();
      expect(loadedData).not.toBeNull();
      expect(loadedData?.userProfile.userId).toBe("test-user");
    });

    it("データの上書き", async () => {
      const mockData1 = createMockData();
      mockData1.userProfile.userId = "user-1";
      await storage.saveData(mockData1);

      const mockData2 = createMockData();
      mockData2.userProfile.userId = "user-2";
      await storage.saveData(mockData2);

      const loadedData = await storage.loadData();
      expect(loadedData?.userProfile.userId).toBe("user-2");
    });
  });
});
