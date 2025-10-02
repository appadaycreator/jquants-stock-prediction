/**
 * 最適化された統合設定マネージャー
 * 重複した設定機能を統合し、パフォーマンスを最適化
 */

export interface SettingsConfig {
  prediction: {
    period: number;
    models: string[];
    features: string[];
  };
  risk: {
    level: string;
    maxDrawdown: number;
    volatility: number;
    var: number;
  };
  notification: {
    enabled: boolean;
    email: string;
    slack: string;
    frequency: string;
  };
  cache: {
    enabled: boolean;
    ttl: number;
    maxSize: number;
  };
  ui: {
    theme: string;
    language: string;
    autoRefresh: boolean;
    refreshInterval: number;
  };
}

export interface SettingsValidation {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

export interface SettingsMigration {
  fromVersion: string;
  toVersion: string;
  changes: string[];
}

export interface SettingsStatistics {
  totalSettings: number;
  lastModified: string;
  version: string;
  migrationCount: number;
}

class OptimizedSettingsManager {
  private settings: SettingsConfig;
  private listeners: Map<string, (settings: SettingsConfig) => void> = new Map();
  private validationRules: Map<string, (value: any) => boolean> = new Map();
  private migrationHistory: SettingsMigration[] = [];
  private currentVersion = "2.8.0";

  constructor() {
    this.settings = this.getDefaultSettings();
    this.initializeValidationRules();
    this.loadSettings();
  }

  /**
   * 設定の取得
   */
  get<K extends keyof SettingsConfig>(key: K): SettingsConfig[K] {
    return this.settings[key];
  }

  /**
   * 設定の更新
   */
  set<K extends keyof SettingsConfig>(key: K, value: SettingsConfig[K]): boolean {
    const oldValue = this.settings[key];
    this.settings[key] = value;
    
    // バリデーション
    const validation = this.validateSettings();
    if (!validation.isValid) {
      this.settings[key] = oldValue;
      console.error("設定のバリデーションに失敗しました:", validation.errors);
      return false;
    }

    // リスナーに通知
    this.notifyListeners();
    
    // 永続化
    this.saveSettings();
    
    return true;
  }

  /**
   * 設定の一括更新
   */
  updateSettings(updates: Partial<SettingsConfig>): boolean {
    const oldSettings = { ...this.settings };
    
    try {
      Object.assign(this.settings, updates);
      
      // バリデーション
      const validation = this.validateSettings();
      if (!validation.isValid) {
        this.settings = oldSettings;
        console.error("設定のバリデーションに失敗しました:", validation.errors);
        return false;
      }

      // リスナーに通知
      this.notifyListeners();
      
      // 永続化
      this.saveSettings();
      
      return true;
    } catch (error) {
      this.settings = oldSettings;
      console.error("設定の更新に失敗しました:", error);
      return false;
    }
  }

  /**
   * 設定のリセット
   */
  reset(): void {
    this.settings = this.getDefaultSettings();
    this.notifyListeners();
    this.saveSettings();
  }

  /**
   * 設定の検証
   */
  validateSettings(): SettingsValidation {
    const errors: string[] = [];
    const warnings: string[] = [];

    // 予測設定の検証
    if (this.settings.prediction.period < 1 || this.settings.prediction.period > 365) {
      errors.push("予測期間は1-365日の範囲で設定してください");
    }

    if (this.settings.prediction.models.length === 0) {
      errors.push("少なくとも1つのモデルを選択してください");
    }

    if (this.settings.prediction.features.length === 0) {
      errors.push("少なくとも1つの特徴量を選択してください");
    }

    // リスク設定の検証
    if (this.settings.risk.maxDrawdown < 0 || this.settings.risk.maxDrawdown > 100) {
      errors.push("最大ドローダウンは0-100%の範囲で設定してください");
    }

    if (this.settings.risk.volatility < 0 || this.settings.risk.volatility > 100) {
      errors.push("ボラティリティは0-100%の範囲で設定してください");
    }

    if (this.settings.risk.var < 0 || this.settings.risk.var > 100) {
      errors.push("VaRは0-100%の範囲で設定してください");
    }

    // 通知設定の検証
    if (this.settings.notification.enabled) {
      if (!this.settings.notification.email && !this.settings.notification.slack) {
        warnings.push("通知が有効ですが、メールまたはSlackの設定がありません");
      }
    }

    // キャッシュ設定の検証
    if (this.settings.cache.ttl < 0) {
      errors.push("キャッシュTTLは0以上である必要があります");
    }

    if (this.settings.cache.maxSize < 0) {
      errors.push("キャッシュ最大サイズは0以上である必要があります");
    }

    // UI設定の検証
    if (this.settings.ui.refreshInterval < 1000) {
      warnings.push("更新間隔が短すぎる可能性があります（1000ms以上推奨）");
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
    };
  }

  /**
   * 設定のエクスポート
   */
  exportSettings(): string {
    const exportData = {
      settings: this.settings,
      version: this.currentVersion,
      timestamp: new Date().toISOString(),
    };
    
    return JSON.stringify(exportData, null, 2);
  }

  /**
   * 設定のインポート
   */
  importSettings(jsonData: string): boolean {
    try {
      const importData = JSON.parse(jsonData);
      
      if (!importData.settings) {
        console.error("無効な設定データです");
        return false;
      }

      // バージョン互換性チェック
      if (importData.version && importData.version !== this.currentVersion) {
        const migration = this.migrateSettings(importData.version, this.currentVersion);
        if (!migration) {
          console.error("設定の移行に失敗しました");
          return false;
        }
      }

      // 設定の更新
      return this.updateSettings(importData.settings);
    } catch (error) {
      console.error("設定のインポートに失敗しました:", error);
      return false;
    }
  }

  /**
   * 設定の移行
   */
  private migrateSettings(fromVersion: string, toVersion: string): boolean {
    try {
      const migration: SettingsMigration = {
        fromVersion,
        toVersion,
        changes: [],
      };

      // バージョン固有の移行ロジック
      if (fromVersion.startsWith("2.7") && toVersion.startsWith("2.8")) {
        // 2.7から2.8への移行
        if (!this.settings.cache) {
          this.settings.cache = {
            enabled: true,
            ttl: 300000, // 5分
            maxSize: 50 * 1024 * 1024, // 50MB
          };
          migration.changes.push("キャッシュ設定を追加");
        }

        if (!this.settings.ui) {
          this.settings.ui = {
            theme: "auto",
            language: "ja",
            autoRefresh: true,
            refreshInterval: 30000, // 30秒
          };
          migration.changes.push("UI設定を追加");
        }
      }

      this.migrationHistory.push(migration);
      return true;
    } catch (error) {
      console.error("設定の移行に失敗しました:", error);
      return false;
    }
  }

  /**
   * リスナーの登録
   */
  addListener(id: string, callback: (settings: SettingsConfig) => void): void {
    this.listeners.set(id, callback);
  }

  /**
   * リスナーの削除
   */
  removeListener(id: string): void {
    this.listeners.delete(id);
  }

  /**
   * リスナーへの通知
   */
  private notifyListeners(): void {
    for (const callback of this.listeners.values()) {
      try {
        callback(this.settings);
      } catch (error) {
        console.error("設定リスナーの通知に失敗しました:", error);
      }
    }
  }

  /**
   * デフォルト設定の取得
   */
  private getDefaultSettings(): SettingsConfig {
    return {
      prediction: {
        period: 30,
        models: ["random_forest", "xgboost"],
        features: ["close", "volume", "sma_5", "sma_25"],
      },
      risk: {
        level: "medium",
        maxDrawdown: 20,
        volatility: 30,
        var: 5,
      },
      notification: {
        enabled: false,
        email: "",
        slack: "",
        frequency: "daily",
      },
      cache: {
        enabled: true,
        ttl: 300000, // 5分
        maxSize: 50 * 1024 * 1024, // 50MB
      },
      ui: {
        theme: "auto",
        language: "ja",
        autoRefresh: true,
        refreshInterval: 30000, // 30秒
      },
    };
  }

  /**
   * バリデーションルールの初期化
   */
  private initializeValidationRules(): void {
    this.validationRules.set("prediction.period", (value) => 
      typeof value === "number" && value >= 1 && value <= 365
    );
    
    this.validationRules.set("prediction.models", (value) => 
      Array.isArray(value) && value.length > 0
    );
    
    this.validationRules.set("prediction.features", (value) => 
      Array.isArray(value) && value.length > 0
    );
    
    this.validationRules.set("risk.maxDrawdown", (value) => 
      typeof value === "number" && value >= 0 && value <= 100
    );
    
    this.validationRules.set("risk.volatility", (value) => 
      typeof value === "number" && value >= 0 && value <= 100
    );
    
    this.validationRules.set("risk.var", (value) => 
      typeof value === "number" && value >= 0 && value <= 100
    );
  }

  /**
   * 設定の読み込み
   */
  private loadSettings(): void {
    try {
      if (typeof window !== "undefined") {
        const stored = localStorage.getItem("optimized_settings");
        if (stored) {
          const data = JSON.parse(stored);
          this.settings = { ...this.getDefaultSettings(), ...data.settings };
          
          // バージョン移行
          if (data.version && data.version !== this.currentVersion) {
            this.migrateSettings(data.version, this.currentVersion);
          }
        }
      }
    } catch (error) {
      console.warn("設定の読み込みに失敗しました:", error);
      this.settings = this.getDefaultSettings();
    }
  }

  /**
   * 設定の保存
   */
  private saveSettings(): void {
    try {
      if (typeof window !== "undefined") {
        const data = {
          settings: this.settings,
          version: this.currentVersion,
          timestamp: new Date().toISOString(),
        };
        localStorage.setItem("optimized_settings", JSON.stringify(data));
      }
    } catch (error) {
      console.error("設定の保存に失敗しました:", error);
    }
  }

  /**
   * 設定統計の取得
   */
  getStatistics(): SettingsStatistics {
    return {
      totalSettings: Object.keys(this.settings).length,
      lastModified: new Date().toISOString(),
      version: this.currentVersion,
      migrationCount: this.migrationHistory.length,
    };
  }

  /**
   * 移行履歴の取得
   */
  getMigrationHistory(): SettingsMigration[] {
    return [...this.migrationHistory];
  }
}

// シングルトンインスタンス
export const optimizedSettingsManager = new OptimizedSettingsManager();

// 便利な関数
export const getSettings = <K extends keyof SettingsConfig>(key: K): SettingsConfig[K] => 
  optimizedSettingsManager.get(key);

export const setSettings = <K extends keyof SettingsConfig>(key: K, value: SettingsConfig[K]): boolean => 
  optimizedSettingsManager.set(key, value);

export const updateSettings = (updates: Partial<SettingsConfig>): boolean => 
  optimizedSettingsManager.updateSettings(updates);

export const resetSettings = (): void => 
  optimizedSettingsManager.reset();

export const validateSettings = (): SettingsValidation => 
  optimizedSettingsManager.validateSettings();

export const exportSettings = (): string => 
  optimizedSettingsManager.exportSettings();

export const importSettings = (jsonData: string): boolean => 
  optimizedSettingsManager.importSettings(jsonData);

export const addSettingsListener = (id: string, callback: (settings: SettingsConfig) => void): void => 
  optimizedSettingsManager.addListener(id, callback);

export const removeSettingsListener = (id: string): void => 
  optimizedSettingsManager.removeListener(id);

export const getSettingsStatistics = (): SettingsStatistics => 
  optimizedSettingsManager.getStatistics();
