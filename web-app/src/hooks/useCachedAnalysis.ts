"use client";

import { useState, useCallback, useEffect } from "react";
import { predictionCacheManager, PredictionCacheData, ModelComparisonCacheData } from "@/lib/prediction-cache-manager";

interface AnalysisParameters {
  symbol: string;
  days: number;
  modelType: string;
  features: string[];
  hyperparameters?: Record<string, any>;
}

interface CachedAnalysisResult {
  predictions: any[];
  modelComparison: any[];
  performance: {
    mae: number;
    rmse: number;
    r2: number;
  };
  fromCache: boolean;
  cacheKey: string;
  timestamp: string;
}

export function useCachedAnalysis() {
  const [isInitialized, setIsInitialized] = useState(false);
  const [cacheStats, setCacheStats] = useState({
    hits: 0,
    misses: 0,
    hitRate: 0,
    totalSize: 0,
    entryCount: 0,
  });

  // キャッシュシステムの初期化
  useEffect(() => {
    const initializeCache = async () => {
      try {
        await predictionCacheManager.initialize();
        setIsInitialized(true);
        updateCacheStats();
      } catch (error) {
        console.error("キャッシュシステム初期化エラー:", error);
      }
    };

    initializeCache();
  }, []);

  const updateCacheStats = useCallback(() => {
    const stats = predictionCacheManager.getCacheStats();
    setCacheStats(stats);
  }, []);

  /**
   * キャッシュされた分析結果の取得
   */
  const getCachedAnalysis = useCallback(async (
    parameters: AnalysisParameters,
  ): Promise<CachedAnalysisResult | null> => {
    if (!isInitialized) {
      console.warn("キャッシュシステムが初期化されていません");
      return null;
    }

    try {
      const cacheKey = predictionCacheManager.generateCacheKey(
        "prediction",
        parameters,
        parameters.modelType,
      );

      // 予測結果の取得
      const predictionData = await predictionCacheManager.getCachedPrediction(cacheKey);
      if (!predictionData) {
        return null;
      }

      // モデル比較結果の取得
      const comparisonKey = predictionCacheManager.generateCacheKey(
        "comparison",
        parameters,
      );
      const comparisonData = await predictionCacheManager.getCachedModelComparison(comparisonKey);

      updateCacheStats();

      return {
        predictions: predictionData.predictions,
        modelComparison: comparisonData?.models || [],
        performance: predictionData.performance,
        fromCache: true,
        cacheKey,
        timestamp: predictionData.timestamp,
      };

    } catch (error) {
      console.error("キャッシュ取得エラー:", error);
      return null;
    }
  }, [isInitialized, updateCacheStats]);

  /**
   * 分析結果のキャッシュ保存
   */
  const cacheAnalysisResult = useCallback(async (
    parameters: AnalysisParameters,
    result: {
      predictions: any[];
      modelComparison: any[];
      performance: { mae: number; rmse: number; r2: number };
    },
  ): Promise<void> => {
    if (!isInitialized) {
      console.warn("キャッシュシステムが初期化されていません");
      return;
    }

    try {
      const predictionKey = predictionCacheManager.generateCacheKey(
        "prediction",
        parameters,
        parameters.modelType,
      );

      const comparisonKey = predictionCacheManager.generateCacheKey(
        "comparison",
        parameters,
      );

      // 予測結果のキャッシュ
      const predictionData: PredictionCacheData = {
        predictions: result.predictions,
        modelComparison: result.modelComparison,
        performance: result.performance,
        timestamp: new Date().toISOString(),
        modelName: parameters.modelType,
        parameters,
      };

      await predictionCacheManager.cachePrediction(
        predictionKey,
        predictionData,
        {
          ttl: 24 * 60 * 60 * 1000, // 24時間
          tags: ["analysis", parameters.symbol, parameters.modelType],
          priority: 1,
        },
      );

      // モデル比較結果のキャッシュ
      const comparisonData: ModelComparisonCacheData = {
        models: result.modelComparison,
        bestModel: result.modelComparison[0]?.name || "",
        comparisonTimestamp: new Date().toISOString(),
        parameters,
      };

      await predictionCacheManager.cacheModelComparison(
        comparisonKey,
        comparisonData,
        {
          ttl: 24 * 60 * 60 * 1000, // 24時間
          tags: ["modelComparison", parameters.symbol],
          priority: 1,
        },
      );

      updateCacheStats();
      console.log("✅ 分析結果をキャッシュに保存しました");

    } catch (error) {
      console.error("キャッシュ保存エラー:", error);
    }
  }, [isInitialized, updateCacheStats]);

  /**
   * キャッシュの検索
   */
  const searchCache = useCallback(async (
    tags: string[],
  ): Promise<Array<{ key: string; data: any; metadata: any }>> => {
    if (!isInitialized) {
      return [];
    }

    try {
      const results = await predictionCacheManager.searchCache("prediction", tags);
      return results;
    } catch (error) {
      console.error("キャッシュ検索エラー:", error);
      return [];
    }
  }, [isInitialized]);

  /**
   * キャッシュのクリア
   */
  const clearCache = useCallback(async (type?: "prediction" | "comparison"): Promise<void> => {
    if (!isInitialized) {
      return;
    }

    try {
      await predictionCacheManager.clearCache(type);
      updateCacheStats();
      console.log(`🧹 キャッシュをクリアしました: ${type || "all"}`);
    } catch (error) {
      console.error("キャッシュクリアエラー:", error);
    }
  }, [isInitialized, updateCacheStats]);

  /**
   * キャッシュの最適化
   */
  const optimizeCache = useCallback(async (): Promise<void> => {
    if (!isInitialized) {
      return;
    }

    try {
      // 古いエントリの削除
      const oldEntries = await searchCache(["analysis"]);
      const oneWeekAgo = new Date();
      oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);

      for (const entry of oldEntries) {
        const createdAt = new Date(entry.metadata.createdAt);
        if (createdAt < oneWeekAgo) {
          await predictionCacheManager.clearCache("prediction");
          break;
        }
      }

      updateCacheStats();
      console.log("🔧 キャッシュを最適化しました");

    } catch (error) {
      console.error("キャッシュ最適化エラー:", error);
    }
  }, [isInitialized, searchCache, updateCacheStats]);

  /**
   * キャッシュヒット率の計算
   */
  const getCacheHitRate = useCallback((): number => {
    return cacheStats.hitRate;
  }, [cacheStats.hitRate]);

  /**
   * キャッシュサイズの取得
   */
  const getCacheSize = useCallback((): number => {
    return cacheStats.totalSize;
  }, [cacheStats.totalSize]);

  return {
    isInitialized,
    cacheStats,
    getCachedAnalysis,
    cacheAnalysisResult,
    searchCache,
    clearCache,
    optimizeCache,
    getCacheHitRate,
    getCacheSize,
    updateCacheStats,
  };
}
