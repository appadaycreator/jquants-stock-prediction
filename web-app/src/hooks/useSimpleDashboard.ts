import { useState, useEffect, useCallback } from "react";

// データ型定義
interface SimpleRecommendation {
  id: string;
  symbol: string;
  symbolName: string;
  action: "BUY" | "SELL" | "HOLD";
  reason: string;
  confidence: number;
  expectedReturn: number;
  priority: "HIGH" | "MEDIUM" | "LOW";
  timeframe: string;
}

interface SimplePortfolioSummary {
  totalInvestment: number;
  currentValue: number;
  unrealizedPnL: number;
  unrealizedPnLPercent: number;
  bestPerformer: {
    symbol: string;
    symbolName: string;
    return: number;
  };
  worstPerformer: {
    symbol: string;
    symbolName: string;
    return: number;
  };
}

interface SimplePosition {
  symbol: string;
  symbolName: string;
  quantity: number;
  averagePrice: number;
  currentPrice: number;
  cost: number;
  currentValue: number;
  unrealizedPnL: number;
  unrealizedPnLPercent: number;
  action: "BUY_MORE" | "SELL" | "HOLD";
  confidence: number;
}

interface SimpleDashboardData {
  lastUpdate: string;
  recommendations: SimpleRecommendation[];
  portfolioSummary: SimplePortfolioSummary;
  positions: SimplePosition[];
  marketStatus: {
    isOpen: boolean;
    nextOpen: string;
  };
}

interface UseSimpleDashboardReturn {
  data: SimpleDashboardData | null;
  loading: boolean;
  error: string | null;
  refreshData: () => Promise<void>;
  lastUpdate: string | null;
}

export const useSimpleDashboard = (): UseSimpleDashboardReturn => {
  const [data, setData] = useState<SimpleDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string | null>(null);

  const fetchData = useCallback(async (forceRefresh = false) => {
    try {
      setLoading(true);
      setError(null);

      const url = forceRefresh 
        ? "/api/simple-dashboard?refresh=true"
        : "/api/simple-dashboard";

      const response = await fetch(url, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
        cache: forceRefresh ? "no-cache" : "default",
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (!result.success) {
        throw new Error(result.error?.message || "データの取得に失敗しました");
      }

      setData(result.data);
      setLastUpdate(result.data.lastUpdate);
    } catch (err) {
      console.error("シンプルダッシュボードデータ取得エラー:", err);
      setError(err instanceof Error ? err.message : "データの取得に失敗しました");
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshData = useCallback(async () => {
    await fetchData(true);
  }, [fetchData]);

  // 初期データ読み込み
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // 自動更新（30秒間隔）
  useEffect(() => {
    const interval = setInterval(() => {
      fetchData();
    }, 30000);

    return () => clearInterval(interval);
  }, [fetchData]);

  return {
    data,
    loading,
    error,
    refreshData,
    lastUpdate,
  };
};
