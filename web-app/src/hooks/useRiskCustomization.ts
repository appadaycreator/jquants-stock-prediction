/**
 * リスク管理カスタマイズフック
 * リスク管理設定の状態管理と操作を提供
 */

import { useState, useEffect, useCallback } from "react";
// risk-customization-store は削除され、統合設定管理を使用
// 一時的にローカル状態管理に変更
interface RiskCustomizationSettings {
  riskTolerance: {
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
    riskAlerts: boolean;
    returnAlerts: boolean;
    drawdownAlerts: boolean;
  };
  display: {
    showRiskMetrics: boolean;
    showReturnMetrics: boolean;
    showAlerts: boolean;
  };
}

// 簡易的なローカルストレージベースの実装
const riskCustomizationStore = {
  getState: () => ({
    settings: {
      riskTolerance: { maxDrawdown: 0.1, volatilityTolerance: 0.2, varTolerance: 0.05 },
      targetReturn: { annual: 0.08, monthly: 0.006, riskAdjusted: true },
      notifications: { riskAlerts: true, returnAlerts: true, drawdownAlerts: true },
      display: { showRiskMetrics: true, showReturnMetrics: true, showAlerts: true },
    },
    isLoading: false,
    error: null,
    lastUpdated: new Date().toISOString(),
  }),
  subscribe: (callback: () => void) => () => {},
  updateSettings: (settings: Partial<RiskCustomizationSettings>) => {
    // ローカルストレージに保存
    localStorage.setItem("risk-customization", JSON.stringify(settings));
  },
  saveToLocalStorage: () => {},
  resetSettings: () => {
    localStorage.removeItem("risk-customization");
  },
  getSettings: () => {
    const stored = localStorage.getItem("risk-customization");
    return stored ? JSON.parse(stored) : {
      riskTolerance: { maxDrawdown: 0.1, volatilityTolerance: 0.2, varTolerance: 0.05 },
      targetReturn: { annual: 0.08, monthly: 0.006, riskAdjusted: true },
      notifications: { riskAlerts: true, returnAlerts: true, drawdownAlerts: true },
      display: { showRiskMetrics: true, showReturnMetrics: true, showAlerts: true },
    };
  },
};

export function useRiskCustomization() {
  const [state, setState] = useState(riskCustomizationStore.getState());

  // ストアの変更を監視
  useEffect(() => {
    const unsubscribe = riskCustomizationStore.subscribe(() => {
      setState(riskCustomizationStore.getState());
    });

    return unsubscribe;
  }, []);

  // 設定の更新
  const updateSettings = useCallback((settings: Partial<RiskCustomizationSettings>) => {
    riskCustomizationStore.updateSettings(settings);
    riskCustomizationStore.saveToLocalStorage();
  }, []);

  // 設定のリセット
  const resetSettings = useCallback(() => {
    riskCustomizationStore.resetSettings();
    riskCustomizationStore.saveToLocalStorage();
  }, []);

  // リスク閾値の取得
  const getRiskThresholds = useCallback(() => {
    const settings = riskCustomizationStore.getSettings();
    return {
      maxDrawdown: settings.riskTolerance.maxDrawdown,
      volatilityTolerance: settings.riskTolerance.volatilityTolerance,
      varTolerance: settings.riskTolerance.varTolerance,
    };
  }, []);

  // 目標リターンの取得
  const getReturnTargets = useCallback(() => {
    const settings = riskCustomizationStore.getSettings();
    return {
      annual: settings.targetReturn.annual,
      monthly: settings.targetReturn.monthly,
      riskAdjusted: settings.targetReturn.riskAdjusted,
    };
  }, []);

  // 通知設定の取得
  const getNotificationSettings = useCallback(() => {
    const settings = riskCustomizationStore.getSettings();
    return settings.notifications;
  }, []);

  // 表示設定の取得
  const getDisplaySettings = useCallback(() => {
    const settings = riskCustomizationStore.getSettings();
    return settings.display;
  }, []);

  // リスクレベルの判定
  const getRiskLevel = useCallback((metrics: {
    maxDrawdown: number;
    volatility: number;
    var: number;
  }) => {
    const settings = riskCustomizationStore.getSettings();
    const { maxDrawdown, volatilityTolerance, varTolerance } = settings.riskTolerance;

    let riskScore = 0;
    
    // ドローダウンベースのスコア
    if (metrics.maxDrawdown <= maxDrawdown * 0.5) riskScore += 1;
    else if (metrics.maxDrawdown <= maxDrawdown) riskScore += 2;
    else if (metrics.maxDrawdown <= maxDrawdown * 1.5) riskScore += 3;
    else riskScore += 4;

    // ボラティリティベースのスコア
    if (metrics.volatility <= volatilityTolerance * 0.5) riskScore += 1;
    else if (metrics.volatility <= volatilityTolerance) riskScore += 2;
    else if (metrics.volatility <= volatilityTolerance * 1.5) riskScore += 3;
    else riskScore += 4;

    // VaRベースのスコア
    if (metrics.var <= varTolerance * 0.5) riskScore += 1;
    else if (metrics.var <= varTolerance) riskScore += 2;
    else if (metrics.var <= varTolerance * 1.5) riskScore += 3;
    else riskScore += 4;

    // リスクレベルの判定
    if (riskScore <= 3) return "VERY_LOW";
    if (riskScore <= 6) return "LOW";
    if (riskScore <= 9) return "MEDIUM";
    if (riskScore <= 12) return "HIGH";
    if (riskScore <= 15) return "VERY_HIGH";
    return "CRITICAL";
  }, []);

  // リスク警告の生成
  const getRiskWarnings = useCallback((metrics: {
    maxDrawdown: number;
    volatility: number;
    var: number;
  }) => {
    const settings = riskCustomizationStore.getSettings();
    const warnings: string[] = [];

    if (metrics.maxDrawdown > settings.riskTolerance.maxDrawdown) {
      warnings.push(`最大ドローダウンが許容値を超過しています (${(metrics.maxDrawdown * 100).toFixed(1)}% > ${(settings.riskTolerance.maxDrawdown * 100).toFixed(1)}%)`);
    }

    if (metrics.volatility > settings.riskTolerance.volatilityTolerance) {
      warnings.push(`ボラティリティが許容値を超過しています (${(metrics.volatility * 100).toFixed(1)}% > ${(settings.riskTolerance.volatilityTolerance * 100).toFixed(1)}%)`);
    }

    if (metrics.var > settings.riskTolerance.varTolerance) {
      warnings.push(`VaRが許容値を超過しています (${(metrics.var * 100).toFixed(1)}% > ${(settings.riskTolerance.varTolerance * 100).toFixed(1)}%)`);
    }

    return warnings;
  }, []);

  return {
    settings: state.settings,
    isLoading: state.isLoading,
    error: state.error,
    lastUpdated: state.lastUpdated,
    updateSettings,
    resetSettings,
    getRiskThresholds,
    getReturnTargets,
    getNotificationSettings,
    getDisplaySettings,
    getRiskLevel,
    getRiskWarnings,
  };
}