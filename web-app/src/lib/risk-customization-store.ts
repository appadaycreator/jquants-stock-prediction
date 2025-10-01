/**
 * リスク管理・個人投資ダッシュボードのカスタマイズ設定を管理するストア
 */

export interface RiskCustomizationSettings {
  // 許容リスクレベル設定
  riskTolerance: {
    level: 'VERY_LOW' | 'LOW' | 'MEDIUM' | 'HIGH' | 'VERY_HIGH' | 'CRITICAL';
    maxDrawdown: number; // 最大ドローダウン許容値（0-1）
    volatilityTolerance: number; // ボラティリティ許容値（0-1）
    varTolerance: number; // VaR許容値（0-1）
  };
  
  // 目標リターン設定
  targetReturn: {
    annual: number; // 年間目標リターン（0-1）
    monthly: number; // 月間目標リターン（0-1）
    riskAdjusted: boolean; // リスク調整後リターンを使用するか
  };
  
  // 個別銘柄設定
  individualStockSettings: {
    [symbol: string]: {
      targetPrice?: number; // 目標価格
      stopLossPrice?: number; // 損切ライン
      maxPositionSize?: number; // 最大ポジションサイズ
      riskLevel?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
      notificationEnabled: boolean; // 通知有効化
    };
  };
  
  // 通知設定
  notifications: {
    targetPriceReached: boolean; // 目標価格到達通知
    stopLossTriggered: boolean; // 損切ライン到達通知
    riskLevelChanged: boolean; // リスクレベル変更通知
    dailySummary: boolean; // 日次サマリー通知
  };
  
  // 表示設定
  display: {
    showRiskDetails: boolean; // リスク詳細表示
    showRecommendationReasons: boolean; // 推奨理由表示
    showTechnicalIndicators: boolean; // テクニカル指標表示
    showSentimentAnalysis: boolean; // センチメント分析表示
  };
}

const DEFAULT_SETTINGS: RiskCustomizationSettings = {
  riskTolerance: {
    level: 'MEDIUM',
    maxDrawdown: 0.15, // 15%
    volatilityTolerance: 0.25, // 25%
    varTolerance: 0.05, // 5%
  },
  targetReturn: {
    annual: 0.10, // 10%
    monthly: 0.008, // 0.8%
    riskAdjusted: true,
  },
  individualStockSettings: {},
  notifications: {
    targetPriceReached: true,
    stopLossTriggered: true,
    riskLevelChanged: true,
    dailySummary: false,
  },
  display: {
    showRiskDetails: true,
    showRecommendationReasons: true,
    showTechnicalIndicators: true,
    showSentimentAnalysis: true,
  },
};

const STORAGE_KEY = 'risk_customization_settings';

export class RiskCustomizationStore {
  private static instance: RiskCustomizationStore;
  private settings: RiskCustomizationSettings;

  private constructor() {
    this.settings = this.loadSettings();
  }

  public static getInstance(): RiskCustomizationStore {
    if (!RiskCustomizationStore.instance) {
      RiskCustomizationStore.instance = new RiskCustomizationStore();
    }
    return RiskCustomizationStore.instance;
  }

  /**
   * 設定を読み込み
   */
  private loadSettings(): RiskCustomizationSettings {
    try {
      if (typeof window === 'undefined') {
        return DEFAULT_SETTINGS;
      }

      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        // デフォルト設定とマージして、不足している項目を補完
        return this.mergeSettings(DEFAULT_SETTINGS, parsed);
      }
    } catch (error) {
      console.error('設定の読み込みに失敗:', error);
    }
    return DEFAULT_SETTINGS;
  }

  /**
   * 設定を保存
   */
  public saveSettings(settings: Partial<RiskCustomizationSettings>): void {
    try {
      this.settings = this.mergeSettings(this.settings, settings);
      
      if (typeof window !== 'undefined') {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(this.settings));
      }
    } catch (error) {
      console.error('設定の保存に失敗:', error);
    }
  }

  /**
   * 現在の設定を取得
   */
  public getSettings(): RiskCustomizationSettings {
    return { ...this.settings };
  }

  /**
   * 個別銘柄設定を更新
   */
  public updateIndividualStockSettings(
    symbol: string, 
    settings: Partial<RiskCustomizationSettings['individualStockSettings'][string]>
  ): void {
    this.settings.individualStockSettings[symbol] = {
      ...this.settings.individualStockSettings[symbol],
      ...settings,
    };
    this.saveSettings({});
  }

  /**
   * 個別銘柄設定を削除
   */
  public removeIndividualStockSettings(symbol: string): void {
    delete this.settings.individualStockSettings[symbol];
    this.saveSettings({});
  }

  /**
   * 設定をリセット
   */
  public resetSettings(): void {
    this.settings = { ...DEFAULT_SETTINGS };
    this.saveSettings({});
  }

  /**
   * 設定をマージ（深いマージ）
   */
  private mergeSettings(
    base: RiskCustomizationSettings, 
    override: Partial<RiskCustomizationSettings>
  ): RiskCustomizationSettings {
    return {
      riskTolerance: { ...base.riskTolerance, ...override.riskTolerance },
      targetReturn: { ...base.targetReturn, ...override.targetReturn },
      individualStockSettings: { 
        ...base.individualStockSettings, 
        ...override.individualStockSettings 
      },
      notifications: { ...base.notifications, ...override.notifications },
      display: { ...base.display, ...override.display },
    };
  }

  /**
   * リスクレベルに基づく閾値を取得
   */
  public getRiskThresholds() {
    const { level, maxDrawdown, volatilityTolerance, varTolerance } = this.settings.riskTolerance;
    
    // リスクレベルに応じた閾値の調整
    const levelMultipliers = {
      'VERY_LOW': 0.5,
      'LOW': 0.7,
      'MEDIUM': 1.0,
      'HIGH': 1.3,
      'VERY_HIGH': 1.6,
      'CRITICAL': 2.0,
    };

    const multiplier = levelMultipliers[level];

    return {
      maxDrawdown: maxDrawdown * multiplier,
      volatilityTolerance: volatilityTolerance * multiplier,
      varTolerance: varTolerance * multiplier,
      level,
    };
  }

  /**
   * 目標リターンに基づく評価基準を取得
   */
  public getReturnTargets() {
    const { annual, monthly, riskAdjusted } = this.settings.targetReturn;
    
    return {
      annual,
      monthly,
      riskAdjusted,
      // 日次目標リターン（月次から計算）
      daily: monthly / 22, // 営業日ベース
    };
  }
}

// シングルトンインスタンスをエクスポート
export const riskCustomizationStore = RiskCustomizationStore.getInstance();
