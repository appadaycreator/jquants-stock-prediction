/**
 * 最適化された統合設定マネージャー
 * 重複した設定管理機能を統合し、パフォーマンスを最適化
 */

interface Settings {
  prediction: {
    days: number;
  };
  model: {
    type: string;
    primary_model: string;
    compare_models: boolean;
    auto_retrain: boolean;
    retrain_frequency: string;
  };
  data: {
    refresh_interval: string;
    max_data_points: number;
    include_technical_indicators: boolean;
  };
  features: {
    selected: string[];
  };
  ui: {
    theme: string;
    refresh_rate: number;
    show_tooltips: boolean;
  };
  risk: {
    tolerance: string;
    maxDrawdown: number;
    volatilityLimit: number;
    varLimit: number;
    targetReturn: number;
  };
  notifications: {
    enabled: boolean;
    email: string;
    slack: string;
    browser: boolean;
  };
  hyperparameters?: {
    [key: string]: any;
  };
  version: string;
}

interface RiskCustomizationSettings {
  riskTolerance: "VERY_LOW" | "LOW" | "MEDIUM" | "HIGH" | "VERY_HIGH" | "CRITICAL";
  maxDrawdownTolerance: number;
  volatilityTolerance: number;
  varTolerance: number;
  targetReturn: number;
  individualStockSettings: {
    [symbol: string]: {
      targetPrice?: number;
      stopLossPrice?: number;
      positionSize?: number;
      riskLevel?: string;
    };
  };
}

interface NotificationSettings {
  enabled: boolean;
  email: string;
  slack: string;
  browser: boolean;
  autoUpdate: boolean;
  updateInterval: number;
  alertThresholds: {
    priceChange: number;
    volumeSpike: number;
    riskLevel: string;
  };
}

interface SettingsValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

interface SettingsMigrationResult {
  success: boolean;
  migratedSettings: Settings;
  changes: string[];
}

class OptimizedSettingsManager {
  private settings: Settings;
  private riskSettings: RiskCustomizationSettings | null = null;
  private notificationSettings: NotificationSettings | null = null;
  private listeners: Set<(settings: Settings) => void> = new Set();
  private isInitialized = false;
  private version = "2.7.0";

  constructor() {
    this.settings = this.getDefaultSettings();
    this.initializeSettings();
  }

  /**
   * デフォルト設定の取得
   */
  private getDefaultSettings(): Settings {
    return {
      prediction: {
        days: 30,
      },
      model: {
        type: "all",
        primary_model: "xgboost",
        compare_models: true,
        auto_retrain: false,
        retrain_frequency: "weekly",
      },
      data: {
        refresh_interval: "daily",
        max_data_points: 1000,
        include_technical_indicators: true,
      },
      features: {
        selected: ["sma_5", "sma_10", "sma_25", "sma_50", "rsi", "macd"],
      },
      ui: {
        theme: "light",
        refresh_rate: 30,
        show_tooltips: true,
      },
      risk: {
        tolerance: "MEDIUM",
        maxDrawdown: 10,
        volatilityLimit: 20,
        varLimit: 5,
        targetReturn: 15,
      },
      notifications: {
        enabled: true,
        email: "",
        slack: "",
        browser: true,
      },
      version: this.version,
    };
  }

  /**
   * 設定の初期化
   */
  private async initializeSettings(): Promise<void> {
    try {
      await this.loadSettings();
      await this.loadRiskSettings();
      await this.loadNotificationSettings();
      this.isInitialized = true;
      this.notifyListeners();
    } catch (error) {
      console.error("設定の初期化に失敗:", error);
      this.isInitialized = true;
    }
  }

  /**
   * 設定の読み込み
   */
  async loadSettings(): Promise<void> {
    try {
      const savedSettings = localStorage.getItem("jquants-settings");
      if (savedSettings) {
        const parsedSettings = JSON.parse(savedSettings);
        this.settings = this.migrateSettings(parsedSettings);
      }
    } catch (error) {
      console.error("設定の読み込みに失敗:", error);
      this.settings = this.getDefaultSettings();
    }
  }

  /**
   * リスク設定の読み込み
   */
  async loadRiskSettings(): Promise<void> {
    try {
      const savedRiskSettings = localStorage.getItem("jquants-risk-settings");
      if (savedRiskSettings) {
        this.riskSettings = JSON.parse(savedRiskSettings);
      }
    } catch (error) {
      console.error("リスク設定の読み込みに失敗:", error);
    }
  }

  /**
   * 通知設定の読み込み
   */
  async loadNotificationSettings(): Promise<void> {
    try {
      const savedNotificationSettings = localStorage.getItem("jquants-notification-settings");
      if (savedNotificationSettings) {
        this.notificationSettings = JSON.parse(savedNotificationSettings);
      }
    } catch (error) {
      console.error("通知設定の読み込みに失敗:", error);
    }
  }

  /**
   * 設定の保存
   */
  async saveSettings(): Promise<void> {
    try {
      this.settings.version = this.version;
      localStorage.setItem("jquants-settings", JSON.stringify(this.settings));
      this.notifyListeners();
    } catch (error) {
      console.error("設定の保存に失敗:", error);
      throw error;
    }
  }

  /**
   * リスク設定の保存
   */
  async saveRiskSettings(riskSettings: RiskCustomizationSettings): Promise<void> {
    try {
      this.riskSettings = riskSettings;
      localStorage.setItem("jquants-risk-settings", JSON.stringify(riskSettings));
    } catch (error) {
      console.error("リスク設定の保存に失敗:", error);
      throw error;
    }
  }

  /**
   * 通知設定の保存
   */
  async saveNotificationSettings(notificationSettings: NotificationSettings): Promise<void> {
    try {
      this.notificationSettings = notificationSettings;
      localStorage.setItem("jquants-notification-settings", JSON.stringify(notificationSettings));
    } catch (error) {
      console.error("通知設定の保存に失敗:", error);
      throw error;
    }
  }

  /**
   * 設定の更新
   */
  updateSettings(newSettings: Partial<Settings>): void {
    this.settings = { ...this.settings, ...newSettings };
    this.notifyListeners();
  }

  /**
   * 設定の取得
   */
  getSettings(): Settings {
    return { ...this.settings };
  }

  /**
   * リスク設定の取得
   */
  getRiskSettings(): RiskCustomizationSettings | null {
    return this.riskSettings ? { ...this.riskSettings } : null;
  }

  /**
   * 通知設定の取得
   */
  getNotificationSettings(): NotificationSettings | null {
    return this.notificationSettings ? { ...this.notificationSettings } : null;
  }

  /**
   * 設定の検証
   */
  validateSettings(settings: any): SettingsValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];

    // 必須フィールドの検証
    if (!settings.prediction || typeof settings.prediction.days !== "number") {
      errors.push("予測期間が正しく設定されていません");
    }

    if (!settings.model || !settings.model.primary_model) {
      errors.push("主要モデルが設定されていません");
    }

    if (!settings.data || typeof settings.data.max_data_points !== "number") {
      errors.push("データポイント数が正しく設定されていません");
    }

    if (!settings.features || !Array.isArray(settings.features.selected)) {
      errors.push("特徴量が正しく設定されていません");
    }

    // 値の範囲チェック
    if (settings.prediction?.days < 1 || settings.prediction?.days > 365) {
      errors.push("予測期間は1日から365日の間で設定してください");
    }

    if (settings.data?.max_data_points < 100 || settings.data?.max_data_points > 10000) {
      warnings.push("データポイント数は100から10000の間で設定することを推奨します");
    }

    if (settings.ui?.refresh_rate < 10 || settings.ui?.refresh_rate > 300) {
      warnings.push("更新間隔は10秒から300秒の間で設定することを推奨します");
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
    };
  }

  /**
   * 設定のマイグレーション
   */
  private migrateSettings(settings: any): Settings {
    const defaultSettings = this.getDefaultSettings();
    const migratedSettings = { ...defaultSettings, ...settings };

    // バージョン固有のマイグレーション
    if (!migratedSettings.version || migratedSettings.version < "2.7.0") {
      // 新しいフィールドの追加
      if (!migratedSettings.risk) {
        migratedSettings.risk = defaultSettings.risk;
      }

      if (!migratedSettings.notifications) {
        migratedSettings.notifications = defaultSettings.notifications;
      }

      // 古いフィールドの削除
      if (migratedSettings.legacy_field) {
        delete migratedSettings.legacy_field;
      }
    }

    return migratedSettings;
  }

  /**
   * 設定のリセット
   */
  resetSettings(): void {
    this.settings = this.getDefaultSettings();
    this.riskSettings = null;
    this.notificationSettings = null;
    this.notifyListeners();
  }

  /**
   * 設定のエクスポート
   */
  exportSettings(): string {
    const exportData = {
      settings: this.settings,
      riskSettings: this.riskSettings,
      notificationSettings: this.notificationSettings,
      exportDate: new Date().toISOString(),
      version: this.version,
    };

    return JSON.stringify(exportData, null, 2);
  }

  /**
   * 設定のインポート
   */
  async importSettings(settingsJson: string): Promise<SettingsMigrationResult> {
    try {
      const importData = JSON.parse(settingsJson);
      const changes: string[] = [];

      // 設定の検証
      const validation = this.validateSettings(importData.settings);
      if (!validation.isValid) {
        throw new Error(`設定の検証に失敗: ${validation.errors.join(", ")}`);
      }

      // 設定の適用
      if (importData.settings) {
        this.settings = this.migrateSettings(importData.settings);
        changes.push("メイン設定をインポートしました");
      }

      if (importData.riskSettings) {
        this.riskSettings = importData.riskSettings;
        changes.push("リスク設定をインポートしました");
      }

      if (importData.notificationSettings) {
        this.notificationSettings = importData.notificationSettings;
        changes.push("通知設定をインポートしました");
      }

      // 保存
      await this.saveSettings();
      if (this.riskSettings) {
        await this.saveRiskSettings(this.riskSettings);
      }
      if (this.notificationSettings) {
        await this.saveNotificationSettings(this.notificationSettings);
      }

      this.notifyListeners();

      return {
        success: true,
        migratedSettings: this.settings,
        changes,
      };
    } catch (error) {
      console.error("設定のインポートに失敗:", error);
      return {
        success: false,
        migratedSettings: this.settings,
        changes: [],
      };
    }
  }

  /**
   * リスナーの追加
   */
  addListener(listener: (settings: Settings) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  /**
   * リスナーへの通知
   */
  private notifyListeners(): void {
    this.listeners.forEach(listener => {
      try {
        listener(this.settings);
      } catch (error) {
        console.error("設定リスナーの通知に失敗:", error);
      }
    });
  }

  /**
   * 設定のバックアップ
   */
  async backupSettings(): Promise<string> {
    const backup = {
      settings: this.settings,
      riskSettings: this.riskSettings,
      notificationSettings: this.notificationSettings,
      backupDate: new Date().toISOString(),
      version: this.version,
    };

    return JSON.stringify(backup, null, 2);
  }

  /**
   * 設定の復元
   */
  async restoreSettings(backupJson: string): Promise<boolean> {
    try {
      const backup = JSON.parse(backupJson);
      
      if (backup.settings) {
        this.settings = this.migrateSettings(backup.settings);
      }

      if (backup.riskSettings) {
        this.riskSettings = backup.riskSettings;
      }

      if (backup.notificationSettings) {
        this.notificationSettings = backup.notificationSettings;
      }

      await this.saveSettings();
      if (this.riskSettings) {
        await this.saveRiskSettings(this.riskSettings);
      }
      if (this.notificationSettings) {
        await this.saveNotificationSettings(this.notificationSettings);
      }

      this.notifyListeners();
      return true;
    } catch (error) {
      console.error("設定の復元に失敗:", error);
      return false;
    }
  }

  /**
   * 初期化状態の確認
   */
  isReady(): boolean {
    return this.isInitialized;
  }

  /**
   * 設定の統計情報
   */
  getSettingsStats(): {
    totalSettings: number;
    riskSettingsConfigured: boolean;
    notificationSettingsConfigured: boolean;
    lastModified: string;
  } {
    return {
      totalSettings: Object.keys(this.settings).length,
      riskSettingsConfigured: this.riskSettings !== null,
      notificationSettingsConfigured: this.notificationSettings !== null,
      lastModified: new Date().toISOString(),
    };
  }
}

// シングルトンインスタンス
const optimizedSettingsManager = new OptimizedSettingsManager();

export default optimizedSettingsManager;
export type { Settings, RiskCustomizationSettings, NotificationSettings, SettingsValidationResult, SettingsMigrationResult };
