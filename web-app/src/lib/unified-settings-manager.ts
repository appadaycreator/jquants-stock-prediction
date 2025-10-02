/**
 * 統一設定マネージャー（リファクタリング版）
 * 全設定機能を一元管理し、最適化された設定管理を提供
 */

export interface Settings {
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
  hyperparameters?: {
    [key: string]: any;
  };
  version: string;
}

export interface RiskCustomizationSettings {
  riskTolerance: {
    level: string;
    maxDrawdown: number;
    volatilityTolerance: number;
    varTolerance: number;
  };
  targetReturn: {
    annual: number;
    monthly: number;
    useRiskAdjusted: boolean;
  };
  individualStockSettings: {
    [symbol: string]: {
      targetPrice?: number;
      stopLossPrice?: number;
      stopLossPercent?: number;
      maxPositionSize?: number;
      riskLevel?: string;
    };
  };
  notifications: {
    priceAlerts: boolean;
    riskAlerts: boolean;
    email: string;
    slack: string;
  };
  display: {
    showRiskMetrics: boolean;
    showPerformanceMetrics: boolean;
    showTechnicalIndicators: boolean;
  };
}

export interface NotificationConfig {
  email: {
    enabled: boolean;
    smtp: {
      host: string;
      port: number;
      secure: boolean;
      auth: {
        user: string;
        pass: string;
      };
    };
    to: string[];
    from: string;
  };
  slack: {
    enabled: boolean;
    webhookUrl: string;
    channel: string;
  };
  alerts: {
    priceChange: {
      enabled: boolean;
      threshold: number;
    };
    volumeSpike: {
      enabled: boolean;
      threshold: number;
    };
    riskExceeded: {
      enabled: boolean;
      threshold: number;
    };
  };
}

export interface SettingsValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

export interface SettingsMigrationResult {
  success: boolean;
  migratedSettings: Settings;
  changes: string[];
}

class UnifiedSettingsManager {
  private settings: Settings;
  private riskSettings: RiskCustomizationSettings;
  private notificationConfig: NotificationConfig;
  private defaultSettings: Settings;
  private defaultRiskSettings: RiskCustomizationSettings;
  private defaultNotificationConfig: NotificationConfig;

  constructor() {
    this.defaultSettings = {
      prediction: { days: 30 },
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
      version: "1.0.0",
    };

    this.defaultRiskSettings = {
      riskTolerance: {
        level: "medium",
        maxDrawdown: 10,
        volatilityTolerance: 20,
        varTolerance: 5,
      },
      targetReturn: {
        annual: 10,
        monthly: 0.8,
        useRiskAdjusted: true,
      },
      individualStockSettings: {},
      notifications: {
        priceAlerts: true,
        riskAlerts: true,
        email: "",
        slack: "",
      },
      display: {
        showRiskMetrics: true,
        showPerformanceMetrics: true,
        showTechnicalIndicators: true,
      },
    };

    this.defaultNotificationConfig = {
      email: {
        enabled: false,
        smtp: {
          host: "",
          port: 587,
          secure: false,
          auth: { user: "", pass: "" },
        },
        to: [],
        from: "",
      },
      slack: {
        enabled: false,
        webhookUrl: "",
        channel: "",
      },
      alerts: {
        priceChange: { enabled: true, threshold: 5 },
        volumeSpike: { enabled: true, threshold: 200 },
        riskExceeded: { enabled: true, threshold: 10 },
      },
    };

    this.settings = { ...this.defaultSettings };
    this.riskSettings = { ...this.defaultRiskSettings };
    this.notificationConfig = { ...this.defaultNotificationConfig };
  }

  /**
   * 設定の読み込み
   */
  async loadSettings(): Promise<void> {
    try {
      // メイン設定の読み込み
      const savedSettings = localStorage.getItem("jquants-settings");
      if (savedSettings) {
        const parsedSettings = JSON.parse(savedSettings);
        this.settings = this.normalizeSettings(parsedSettings);
      }

      // リスク設定の読み込み
      const savedRiskSettings = localStorage.getItem("jquants-risk-settings");
      if (savedRiskSettings) {
        const parsedRiskSettings = JSON.parse(savedRiskSettings);
        this.riskSettings = this.normalizeRiskSettings(parsedRiskSettings);
      }

      // 通知設定の読み込み
      const savedNotificationConfig = localStorage.getItem("jquants-notification-config");
      if (savedNotificationConfig) {
        const parsedNotificationConfig = JSON.parse(savedNotificationConfig);
        this.notificationConfig = this.normalizeNotificationConfig(parsedNotificationConfig);
      }
    } catch (error) {
      console.error("設定の読み込みに失敗:", error);
      this.settings = { ...this.defaultSettings };
      this.riskSettings = { ...this.defaultRiskSettings };
      this.notificationConfig = { ...this.defaultNotificationConfig };
    }
  }

  /**
   * 設定の保存
   */
  async saveSettings(): Promise<void> {
    try {
      localStorage.setItem("jquants-settings", JSON.stringify(this.settings));
      localStorage.setItem("jquants-risk-settings", JSON.stringify(this.riskSettings));
      localStorage.setItem("jquants-notification-config", JSON.stringify(this.notificationConfig));
    } catch (error) {
      console.error("設定保存エラー:", error);
      throw error;
    }
  }

  /**
   * 設定の更新
   */
  updateSettings(newSettings: Partial<Settings>): void {
    this.settings = { ...this.settings, ...newSettings };
  }

  /**
   * リスク設定の更新
   */
  updateRiskSettings(newRiskSettings: Partial<RiskCustomizationSettings>): void {
    this.riskSettings = this.mergeRiskSettings(this.riskSettings, newRiskSettings);
  }

  /**
   * 通知設定の更新
   */
  updateNotificationConfig(newNotificationConfig: Partial<NotificationConfig>): void {
    this.notificationConfig = this.mergeNotificationConfig(this.notificationConfig, newNotificationConfig);
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
  getRiskSettings(): RiskCustomizationSettings {
    return { ...this.riskSettings };
  }

  /**
   * 通知設定の取得
   */
  getNotificationConfig(): NotificationConfig {
    return { ...this.notificationConfig };
  }

  /**
   * 設定の検証
   */
  validateSettings(): SettingsValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];

    // 予測設定の検証
    if (this.settings.prediction.days < 1 || this.settings.prediction.days > 365) {
      errors.push("予測期間は1日から365日の間で設定してください");
    }

    // モデル設定の検証
    if (!["all", "single"].includes(this.settings.model.type)) {
      errors.push("モデルタイプは'all'または'single'を選択してください");
    }

    if (!["xgboost", "random_forest", "linear", "svr"].includes(this.settings.model.primary_model)) {
      errors.push("プライマリモデルは有効なモデルを選択してください");
    }

    // データ設定の検証
    if (this.settings.data.max_data_points < 100 || this.settings.data.max_data_points > 10000) {
      warnings.push("データポイント数は100から10000の間で設定することを推奨します");
    }

    // UI設定の検証
    if (this.settings.ui.refresh_rate < 5 || this.settings.ui.refresh_rate > 300) {
      warnings.push("更新間隔は5秒から300秒の間で設定することを推奨します");
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
  migrateSettings(oldSettings: any): SettingsMigrationResult {
    try {
      const migratedSettings = this.normalizeSettings(oldSettings);
      const changes: string[] = [];

      // バージョン1.0.0へのマイグレーション
      if (!oldSettings.version || oldSettings.version === "0.9.0") {
        changes.push("バージョン1.0.0へのマイグレーションを実行");
        
        if (oldSettings.prediction && !migratedSettings.prediction) {
          migratedSettings.prediction = { days: 30 };
          changes.push("予測設定をデフォルト値で初期化");
        }

        if (oldSettings.features && !migratedSettings.features) {
          migratedSettings.features = { selected: this.defaultSettings.features.selected };
          changes.push("特徴量設定をデフォルト値で初期化");
        }
      }

      migratedSettings.version = "1.0.0";

      return {
        success: true,
        migratedSettings,
        changes,
      };
    } catch (error) {
      console.error("設定マイグレーションエラー:", error);
      return {
        success: false,
        migratedSettings: this.defaultSettings,
        changes: ["マイグレーションに失敗しました"],
      };
    }
  }

  /**
   * 設定のリセット
   */
  resetSettings(): void {
    this.settings = { ...this.defaultSettings };
    this.riskSettings = { ...this.defaultRiskSettings };
    this.notificationConfig = { ...this.defaultNotificationConfig };
  }

  /**
   * 設定のエクスポート
   */
  exportSettings(): string {
    return JSON.stringify({
      settings: this.settings,
      riskSettings: this.riskSettings,
      notificationConfig: this.notificationConfig,
      exportDate: new Date().toISOString(),
    }, null, 2);
  }

  /**
   * 設定のインポート
   */
  importSettings(settingsJson: string): SettingsValidationResult {
    try {
      const imported = JSON.parse(settingsJson);
      
      if (imported.settings) {
        this.settings = this.normalizeSettings(imported.settings);
      }
      
      if (imported.riskSettings) {
        this.riskSettings = this.normalizeRiskSettings(imported.riskSettings);
      }
      
      if (imported.notificationConfig) {
        this.notificationConfig = this.normalizeNotificationConfig(imported.notificationConfig);
      }

      return this.validateSettings();
    } catch (error) {
      console.error("設定インポートエラー:", error);
      return {
        isValid: false,
        errors: ["設定ファイルの形式が正しくありません"],
        warnings: [],
      };
    }
  }

  /**
   * 設定の正規化
   */
  private normalizeSettings(settings: any): Settings {
    const normalized = { ...this.defaultSettings };

    if (settings.prediction) {
      normalized.prediction = { ...this.defaultSettings.prediction, ...settings.prediction };
    }

    if (settings.model) {
      normalized.model = { ...this.defaultSettings.model, ...settings.model };
    }

    if (settings.data) {
      normalized.data = { ...this.defaultSettings.data, ...settings.data };
    }

    if (settings.features) {
      normalized.features = { ...this.defaultSettings.features, ...settings.features };
    }

    if (settings.ui) {
      normalized.ui = { ...this.defaultSettings.ui, ...settings.ui };
    }

    if (settings.hyperparameters) {
      normalized.hyperparameters = { ...this.defaultSettings.hyperparameters, ...settings.hyperparameters };
    }

    normalized.version = settings.version || "1.0.0";

    return normalized;
  }

  /**
   * リスク設定の正規化
   */
  private normalizeRiskSettings(riskSettings: any): RiskCustomizationSettings {
    const normalized = { ...this.defaultRiskSettings };

    if (riskSettings.riskTolerance) {
      normalized.riskTolerance = { ...this.defaultRiskSettings.riskTolerance, ...riskSettings.riskTolerance };
    }

    if (riskSettings.targetReturn) {
      normalized.targetReturn = { ...this.defaultRiskSettings.targetReturn, ...riskSettings.targetReturn };
    }

    if (riskSettings.individualStockSettings) {
      normalized.individualStockSettings = { ...this.defaultRiskSettings.individualStockSettings, ...riskSettings.individualStockSettings };
    }

    if (riskSettings.notifications) {
      normalized.notifications = { ...this.defaultRiskSettings.notifications, ...riskSettings.notifications };
    }

    if (riskSettings.display) {
      normalized.display = { ...this.defaultRiskSettings.display, ...riskSettings.display };
    }

    return normalized;
  }

  /**
   * 通知設定の正規化
   */
  private normalizeNotificationConfig(notificationConfig: any): NotificationConfig {
    const normalized = { ...this.defaultNotificationConfig };

    if (notificationConfig.email) {
      normalized.email = { ...this.defaultNotificationConfig.email, ...notificationConfig.email };
    }

    if (notificationConfig.slack) {
      normalized.slack = { ...this.defaultNotificationConfig.slack, ...notificationConfig.slack };
    }

    if (notificationConfig.alerts) {
      normalized.alerts = { ...this.defaultNotificationConfig.alerts, ...notificationConfig.alerts };
    }

    return normalized;
  }

  /**
   * リスク設定のマージ
   */
  private mergeRiskSettings(
    base: RiskCustomizationSettings,
    override: Partial<RiskCustomizationSettings>,
  ): RiskCustomizationSettings {
    return {
      riskTolerance: { ...base.riskTolerance, ...override.riskTolerance },
      targetReturn: { ...base.targetReturn, ...override.targetReturn },
      individualStockSettings: { ...base.individualStockSettings, ...override.individualStockSettings },
      notifications: { ...base.notifications, ...override.notifications },
      display: { ...base.display, ...override.display },
    };
  }

  /**
   * 通知設定のマージ
   */
  private mergeNotificationConfig(
    base: NotificationConfig,
    override: Partial<NotificationConfig>,
  ): NotificationConfig {
    return {
      email: { ...base.email, ...override.email },
      slack: { ...base.slack, ...override.slack },
      alerts: { ...base.alerts, ...override.alerts },
    };
  }
}

// シングルトンインスタンス
export const unifiedSettingsManager = new UnifiedSettingsManager();

export default unifiedSettingsManager;
