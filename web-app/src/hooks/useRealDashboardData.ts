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

      // 接続テストが失敗しても続行（フォールバック機能）
      if (!connectionStatus.success) {
        console.warn("API接続失敗、サンプルデータを使用します:", connectionStatus.message);
      }

      // 2. 市場サマリーを生成（フォールバック機能付き）
      console.log("ダッシュボード: 市場分析実行中...");
      const marketSummary = await generateMarketSummary();

      if (!marketSummary) {
        setState(prev => ({ 
          ...prev, 
          isLoading: false, 
          error: "市場サマリーの生成に失敗しました。サンプルデータも利用できません。", 
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
        isSampleData: marketSummary.analyzedSymbols <= 5, // サンプルデータかどうかの判定
      });

    } catch (error) {
      console.error("ダッシュボードデータ取得エラー:", error);
      
      // 最終的なフォールバック: サンプルデータを強制的に生成
      try {
        console.log("最終フォールバック: サンプルデータを生成します");
        const sampleSummary = {
          totalSymbols: 5,
          analyzedSymbols: 5,
          recommendations: {
            STRONG_BUY: 1,
            BUY: 2,
            HOLD: 1,
            SELL: 1,
            STRONG_SELL: 0,
          },
          topGainers: [],
          topLosers: [],
          lastUpdated: new Date().toISOString(),
        };

        setState(prev => ({
          ...prev,
          isLoading: false,
          marketSummary: sampleSummary,
          lastUpdated: new Date().toISOString(),
          error: "サンプルデータを使用しています",
        }));
      } catch (fallbackError) {
        console.error("サンプルデータ生成も失敗:", fallbackError);
        setState(prev => ({
          ...prev,
          isLoading: false,
          error: "データの取得に完全に失敗しました。ページを再読み込みしてください。",
        }));
      }
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