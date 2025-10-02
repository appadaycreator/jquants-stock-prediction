/**
 * リスク管理カスタマイズ設定ストア
 * ユーザーのリスク管理設定を統一的に管理
 */

export interface RiskCustomizationSettings {
  riskTolerance: {
    level: "VERY_LOW" | "LOW" | "MEDIUM" | "HIGH" | "VERY_HIGH" | "CRITICAL";
    maxDrawdown: number;
    volatilityTolerance: number;
    varTolerance: number;
  };
  targetReturn: {
    annual: number;
    monthly: number;
    riskAdjusted: boolean;
  };
  notifications: {
    targetPriceReached: boolean;
    stopLossTriggered: boolean;
    riskLevelChanged: boolean;
    dailySummary: boolean;
  };
  display: {
    showRiskDetails: boolean;
    showRecommendationReasons: boolean;
    showTechnicalIndicators: boolean;
    showSentimentAnalysis: boolean;
  };
}

export interface RiskCustomizationState {
  settings: RiskCustomizationSettings;
  isLoading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

class RiskCustomizationStore {
  private state: RiskCustomizationState = {
    settings: this.getDefaultSettings(),
    isLoading: false,
    error: null,
    lastUpdated: null,
  };

  private listeners: Set<() => void> = new Set();

  private getDefaultSettings(): RiskCustomizationSettings {
    return {
      riskTolerance: {
        level: "MEDIUM",
        maxDrawdown: 0.15,
        volatilityTolerance: 0.20,
        varTolerance: 0.05,
      },
      targetReturn: {
        annual: 0.08,
        monthly: 0.006,
        riskAdjusted: true,
      },
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
  }

  // 設定の取得
  getSettings(): RiskCustomizationSettings {
    return this.state.settings;
  }

  // 設定の更新
  updateSettings(settings: Partial<RiskCustomizationSettings>): void {
    this.state.settings = {
      ...this.state.settings,
      ...settings,
    };
    this.state.lastUpdated = new Date();
    this.notifyListeners();
  }

  // 設定のリセット
  resetSettings(): void {
    this.state.settings = this.getDefaultSettings();
    this.state.lastUpdated = new Date();
    this.notifyListeners();
  }

  // ローディング状態の設定
  setLoading(isLoading: boolean): void {
    this.state.isLoading = isLoading;
    this.notifyListeners();
  }

  // エラー状態の設定
  setError(error: string | null): void {
    this.state.error = error;
    this.notifyListeners();
  }

  // リスナーの追加
  subscribe(listener: () => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  // リスナーへの通知
  private notifyListeners(): void {
    this.listeners.forEach(listener => listener());
  }

  // 現在の状態の取得
  getState(): RiskCustomizationState {
    return { ...this.state };
  }

  // 設定の検証
  validateSettings(settings: RiskCustomizationSettings): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    // リスク許容度の検証
    if (settings.riskTolerance.maxDrawdown < 0 || settings.riskTolerance.maxDrawdown > 1) {
      errors.push("最大ドローダウン許容値は0-1の範囲で設定してください");
    }

    if (settings.riskTolerance.volatilityTolerance < 0 || settings.riskTolerance.volatilityTolerance > 1) {
      errors.push("ボラティリティ許容値は0-1の範囲で設定してください");
    }

    if (settings.riskTolerance.varTolerance < 0 || settings.riskTolerance.varTolerance > 1) {
      errors.push("VaR許容値は0-1の範囲で設定してください");
    }

    // 目標リターンの検証
    if (settings.targetReturn.annual < 0 || settings.targetReturn.annual > 1) {
      errors.push("年間目標リターンは0-1の範囲で設定してください");
    }

    if (settings.targetReturn.monthly < 0 || settings.targetReturn.monthly > 1) {
      errors.push("月間目標リターンは0-1の範囲で設定してください");
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  // 設定の保存（ローカルストレージ）
  saveToLocalStorage(): void {
    try {
      localStorage.setItem('risk-customization-settings', JSON.stringify(this.state.settings));
    } catch (error) {
      console.error('設定の保存に失敗しました:', error);
    }
  }

  // 設定の読み込み（ローカルストレージ）
  loadFromLocalStorage(): void {
    try {
      const saved = localStorage.getItem('risk-customization-settings');
      if (saved) {
        const settings = JSON.parse(saved);
        const validation = this.validateSettings(settings);
        if (validation.isValid) {
          this.state.settings = settings;
          this.state.lastUpdated = new Date();
          this.notifyListeners();
        }
      }
    } catch (error) {
      console.error('設定の読み込みに失敗しました:', error);
    }
  }
}

// シングルトンインスタンス
export const riskCustomizationStore = new RiskCustomizationStore();

// 初期化時にローカルストレージから設定を読み込み
if (typeof window !== 'undefined') {
  riskCustomizationStore.loadFromLocalStorage();
}
