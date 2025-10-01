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
      const response = await fetch("/api/signals", {
        method: "GET",
        headers: { "Content-Type": "application/json" },
        cache: "no-store",
      });
      
      if (response.ok) {
        const data = await response.json();
        
        if (data.analysisRequired) {
          // 分析が未実行の場合
          setSignals([]);
          setError(data.error?.message || "分析を実行してからお試しください");
          setLastUpdate(new Date());
          return;
        }
        
        if (data.signals && data.signals.length > 0) {
          setSignals(data.signals);
          setLastUpdate(new Date());
          saveSignalsToCache(data.signals);
        } else {
          // シグナルが空の場合、モックデータを生成
          const mockSignals = generateMockSignals();
          setSignals(mockSignals);
          setIsUsingFallback(true);
          setError("シグナルデータがありません。サンプルデータを表示しています。");
          setLastUpdate(new Date());
          saveSignalsToCache(mockSignals);
        }
      } else {
        // HTTPエラーの場合
        const errorData = await response.json().catch(() => ({}));
        
        // キャッシュを確認
        const cachedSignals = getCachedSignals();
        if (cachedSignals) {
          setSignals(cachedSignals);
          setIsUsingFallback(true);
          setError(errorData.error?.message || "最新データの取得に失敗しました。前回の結果を表示しています。");
          setLastUpdate(new Date());
        } else {
          // キャッシュもない場合はモックデータを生成
          const fallbackSignals = generateMockSignals();
          setSignals(fallbackSignals);
          setIsUsingFallback(true);
          setError(errorData.error?.message || "データ取得に失敗しました。サンプルデータを表示しています。");
          setLastUpdate(new Date());
          saveSignalsToCache(fallbackSignals);
        }
      }
    } catch (err) {
      console.error("シグナル取得エラー:", err);
      
      // ネットワークエラーの場合、キャッシュを確認
      const cachedSignals = getCachedSignals();
      if (cachedSignals) {
        setSignals(cachedSignals);
        setIsUsingFallback(true);
        setError("ネットワークエラーが発生しました。前回の結果を表示しています。");
        setLastUpdate(new Date());
      } else {
        // キャッシュもない場合はモックデータを生成
        const fallbackSignals = generateMockSignals();
        setSignals(fallbackSignals);
        setIsUsingFallback(true);
        setError("ネットワーク接続を確認してください。サンプルデータを表示しています。");
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
