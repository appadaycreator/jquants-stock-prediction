/**
 * リスク管理カスタマイズ設定を管理するカスタムフック
 */

import { useState, useEffect, useCallback } from "react";
import { 
  RiskCustomizationSettings, 
  riskCustomizationStore, 
} from "@/lib/risk-customization-store";

export function useRiskCustomization() {
  const [settings, setSettings] = useState<RiskCustomizationSettings>(
    riskCustomizationStore.getSettings(),
  );
  const [isLoading, setIsLoading] = useState(false);

  // 設定を更新
  const updateSettings = useCallback((newSettings: Partial<RiskCustomizationSettings>) => {
    setIsLoading(true);
    try {
      riskCustomizationStore.saveSettings(newSettings);
      setSettings(riskCustomizationStore.getSettings());
    } catch (error) {
      console.error("設定の更新に失敗:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 個別銘柄設定を更新
  const updateIndividualStockSettings = useCallback((
    symbol: string, 
    stockSettings: Partial<RiskCustomizationSettings["individualStockSettings"][string]>,
  ) => {
    setIsLoading(true);
    try {
      riskCustomizationStore.updateIndividualStockSettings(symbol, stockSettings);
      setSettings(riskCustomizationStore.getSettings());
    } catch (error) {
      console.error("個別銘柄設定の更新に失敗:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 個別銘柄設定を削除
  const removeIndividualStockSettings = useCallback((symbol: string) => {
    setIsLoading(true);
    try {
      riskCustomizationStore.removeIndividualStockSettings(symbol);
      setSettings(riskCustomizationStore.getSettings());
    } catch (error) {
      console.error("個別銘柄設定の削除に失敗:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 設定をリセット
  const resetSettings = useCallback(() => {
    setIsLoading(true);
    try {
      riskCustomizationStore.resetSettings();
      setSettings(riskCustomizationStore.getSettings());
    } catch (error) {
      console.error("設定のリセットに失敗:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // リスク閾値を取得
  const getRiskThresholds = useCallback(() => {
    return riskCustomizationStore.getRiskThresholds();
  }, []);

  // 目標リターンを取得
  const getReturnTargets = useCallback(() => {
    return riskCustomizationStore.getReturnTargets();
  }, []);

  // 個別銘柄設定を取得
  const getIndividualStockSettings = useCallback((symbol: string) => {
    return settings.individualStockSettings[symbol] || null;
  }, [settings.individualStockSettings]);

  // 設定変更の監視
  useEffect(() => {
    const handleStorageChange = () => {
      setSettings(riskCustomizationStore.getSettings());
    };

    if (typeof window !== "undefined") {
      window.addEventListener("storage", handleStorageChange);
      return () => window.removeEventListener("storage", handleStorageChange);
    }
  }, []);

  return {
    settings,
    isLoading,
    updateSettings,
    updateIndividualStockSettings,
    removeIndividualStockSettings,
    resetSettings,
    getRiskThresholds,
    getReturnTargets,
    getIndividualStockSettings,
  };
}
