"use client";

import { useState, useEffect, useCallback } from "react";

interface SignalData {
  symbol: string;
  signal_type: string;
  confidence: number;
  price: number;
  timestamp: string;
  reason: string;
  category?: string;
  expected_holding_period?: number;
}

interface UseSignalWithFallbackReturn {
  signals: SignalData[];
  loading: boolean;
  error: string | null;
  isUsingFallback: boolean;
  lastUpdate: Date | null;
  refresh: () => Promise<void>;
  clearError: () => void;
}

const FALLBACK_KEY = "signal_fallback_data";
const CACHE_EXPIRY_HOURS = 6;

export function useSignalWithFallback(symbols: string[] = []) {
  const [signals, setSignals] = useState<SignalData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isUsingFallback, setIsUsingFallback] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const getCachedSignals = useCallback(() => {
    try {
      const cached = localStorage.getItem(FALLBACK_KEY);
      if (cached) {
        const data = JSON.parse(cached);
        const cacheTime = new Date(data.timestamp);
        const now = new Date();
        const hoursDiff = (now.getTime() - cacheTime.getTime()) / (1000 * 60 * 60);
        
        if (hoursDiff < CACHE_EXPIRY_HOURS) {
          return data.signals;
        }
      }
    } catch (e) {
      console.warn("キャッシュデータの読み込みに失敗:", e);
    }
    return null;
  }, []);

  const saveSignalsToCache = useCallback((signals: SignalData[]) => {
    try {
      const cacheData = {
        signals,
        timestamp: new Date().toISOString(),
      };
      localStorage.setItem(FALLBACK_KEY, JSON.stringify(cacheData));
    } catch (e) {
      console.warn("キャッシュデータの保存に失敗:", e);
    }
  }, []);

  const generateMockSignals = useCallback((): SignalData[] => {
    const categories = ["上昇トレンド発生", "下落トレンド注意", "出来高急増", "リスクリターン改善", "テクニカルブレイクアウト"];
    const signalTypes = ["BUY", "SELL", "HOLD"];
    const targetSymbols = symbols.length > 0 ? symbols : ["7203.T", "6758.T", "9984.T"];
    
    return targetSymbols.map(symbol => ({
      symbol,
      signal_type: signalTypes[Math.floor(Math.random() * signalTypes.length)],
      confidence: Math.random() * 0.4 + 0.6,
      price: 1000 + Math.random() * 2000,
      timestamp: new Date().toISOString(),
      reason: `${categories[Math.floor(Math.random() * categories.length)]}によるシグナル`,
      category: categories[Math.floor(Math.random() * categories.length)],
      expected_holding_period: 30,
    }));
  }, [symbols]);

  const fetchSignals = useCallback(async () => {
    setLoading(true);
    setError(null);
    setIsUsingFallback(false);

    try {
      // 実際のAPI呼び出しをシミュレート
      // 本番環境では、ここで実際のAPIエンドポイントを呼び出す
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // ランダムにエラーを発生させてフォールバック機能をテスト
      if (Math.random() < 0.3) {
        throw new Error("API取得に失敗しました");
      }

      const mockSignals = generateMockSignals();
      setSignals(mockSignals);
      setLastUpdate(new Date());
      saveSignalsToCache(mockSignals);
      
    } catch (err) {
      console.error("シグナル取得エラー:", err);
      
      // フォールバック: キャッシュされたデータを使用
      const cachedSignals = getCachedSignals();
      if (cachedSignals) {
        setSignals(cachedSignals);
        setIsUsingFallback(true);
        setError("最新データの取得に失敗しました。前回の結果を表示しています。");
        setLastUpdate(new Date());
      } else {
        // キャッシュもない場合はモックデータを生成
        const fallbackSignals = generateMockSignals();
        setSignals(fallbackSignals);
        setIsUsingFallback(true);
        setError("データ取得に失敗しました。サンプルデータを表示しています。");
        setLastUpdate(new Date());
        saveSignalsToCache(fallbackSignals);
      }
    } finally {
      setLoading(false);
    }
  }, [generateMockSignals, getCachedSignals, saveSignalsToCache]);

  const clearError = useCallback(() => {
    setError(null);
    setIsUsingFallback(false);
  }, []);

  useEffect(() => {
    fetchSignals();
  }, [fetchSignals]);

  return {
    signals,
    loading,
    error,
    isUsingFallback,
    lastUpdate,
    refresh: fetchSignals,
    clearError,
  };
}
