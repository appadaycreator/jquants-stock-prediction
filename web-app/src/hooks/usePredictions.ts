"use client";

import { useState, useEffect } from "react";
import { fetchJson } from "@/lib/fetcher";

export interface Prediction {
  symbol: string;
  name: string;
  currentPrice: number;
  predictedPrice: number;
  confidence: number;
  recommendation: "BUY" | "SELL" | "HOLD";
  timeframe: string;
  lastUpdated: string;
}

export interface PredictionsData {
  predictions: Prediction[];
  lastUpdated: string;
  totalPredictions: number;
}

export function usePredictions() {
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  const fetchPredictions = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const data = await fetchJson<PredictionsData>("/api/predictions");
      setPredictions(data.predictions);
      setLastUpdated(data.lastUpdated);
    } catch (err) {
      setError(err instanceof Error ? err.message : "予測データの取得に失敗しました");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPredictions();
  }, []);

  return {
    predictions,
    isLoading,
    error,
    lastUpdated,
    refetch: fetchPredictions,
  };
}
