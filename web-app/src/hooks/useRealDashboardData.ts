/**
 * 実際のJQuantsデータを使用したダッシュボードフック
 */

import { useCallback, useEffect, useState } from "react";
import { testConnection } from "@/lib/unified-api-client";
import { generateMarketSummary, type AnalysisResult, type MarketSummary } from "@/lib/stock-analysis";

export interface RealDashboardState {
  isLoading: boolean;
  error: string | null;
  connectionStatus: { success: boolean; message: string } | null;
  marketSummary: MarketSummary | null;
  lastUpdated: string | null;
  analysisResults: AnalysisResult[];
}

export function useRealDashboardData() {
  const [state, setState] = useState<RealDashboardState>({
    isLoading: true,
    error: null,
    connectionStatus: null,
    marketSummary: null,
    lastUpdated: null,
    analysisResults: [],
  });

  const refresh = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      // 1. 接続テスト
      console.log("ダッシュボード: JQuants接続テスト開始...");
      const connectionStatus = await testConnection();
      setState(prev => ({ ...prev, connectionStatus }));

      if (!connectionStatus.success) {
        setState(prev => ({ 
          ...prev, 
          isLoading: false, 
          error: `API接続失敗: ${connectionStatus.message}` 
        }));
        return;
      }

      // 2. 市場サマリーを生成
      console.log("ダッシュボード: 市場分析実行中...");
      const marketSummary = await generateMarketSummary();

      if (!marketSummary) {
        setState(prev => ({ 
          ...prev, 
          isLoading: false, 
          error: "市場サマリーの生成に失敗しました" 
        }));
        return;
      }

      const lastUpdated = new Date().toISOString();

      setState(prev => ({
        ...prev,
        isLoading: false,
        marketSummary,
        lastUpdated,
        error: null,
      }));

      console.log("ダッシュボードデータ更新完了:", {
        analyzedSymbols: marketSummary.analyzedSymbols,
        totalRecommendations: Object.values(marketSummary.recommendations).reduce((a, b) => a + b, 0),
        topGainers: marketSummary.topGainers.length,
        topLosers: marketSummary.topLosers.length,
      });

    } catch (error) {
      console.error("ダッシュボードデータ取得エラー:", error);
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : "不明なエラーが発生しました",
      }));
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return {
    ...state,
    actions: {
      refresh,
    },
  };
}

export type UseRealDashboardDataReturn = ReturnType<typeof useRealDashboardData>;