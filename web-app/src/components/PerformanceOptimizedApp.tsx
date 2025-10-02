"use client";

import React, { useEffect, useState, useCallback, useMemo } from "react";
import { unifiedPerformanceSystem } from "@/lib/unified-performance-system";
import { frontendMemoryOptimizer } from "@/lib/frontend-memory-optimizer";
import { progressiveDataLoader } from "@/lib/progressive-data-loader";
import { optimizedCacheStrategy } from "@/lib/optimized-cache-strategy";
import { performanceValidator } from "@/lib/performance-validator";

interface PerformanceOptimizedAppProps {
  children: React.ReactNode;
  enableMemoryOptimization?: boolean;
  enableLazyLoading?: boolean;
  enableProgressiveLoading?: boolean;
  enableCacheOptimization?: boolean;
  enablePerformanceValidation?: boolean;
  targetInitialLoadTime?: number;
  targetChartRenderTime?: number;
  targetMemoryReduction?: number;
  enableRealTimeMonitoring?: boolean;
  enableAutoOptimization?: boolean;
}

interface PerformanceStatus {
  isOptimized: boolean;
  memoryUsage: number;
  memoryReduction: number;
  initialLoadTime: number;
  chartRenderTime: number;
  score: number;
  recommendations: string[];
}

function PerformanceOptimizedApp({
  children,
  enableMemoryOptimization = true,
  enableLazyLoading = true,
  enableProgressiveLoading = true,
  enableCacheOptimization = true,
  enablePerformanceValidation = true,
  targetInitialLoadTime = 3000,
  targetChartRenderTime = 1000,
  targetMemoryReduction = 50,
  enableRealTimeMonitoring = true,
  enableAutoOptimization = true,
}: PerformanceOptimizedAppProps) {
  const [performanceStatus, setPerformanceStatus] = useState<PerformanceStatus>({
    isOptimized: false,
    memoryUsage: 0,
    memoryReduction: 0,
    initialLoadTime: 0,
    chartRenderTime: 0,
    score: 0,
    recommendations: [],
  });

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // パフォーマンス最適化の初期化
  useEffect(() => {
    const initializePerformance = async () => {
      try {
        setIsLoading(true);
        setError(null);

        console.info("パフォーマンス最適化システムを初期化中...");

        // 統合パフォーマンスシステムの初期化
        await unifiedPerformanceSystem.initialize();

        // メモリ最適化の実行
        if (enableMemoryOptimization) {
          frontendMemoryOptimizer.optimizeMemory();
        }

        // キャッシュ最適化の実行
        if (enableCacheOptimization) {
          optimizedCacheStrategy.cleanup();
        }

        // パフォーマンス検証の実行
        if (enablePerformanceValidation) {
          const validationResult = await unifiedPerformanceSystem.validatePerformance();
          
          setPerformanceStatus({
            isOptimized: validationResult.success,
            memoryUsage: validationResult.metrics.memoryUsage,
            memoryReduction: validationResult.metrics.memoryReduction,
            initialLoadTime: validationResult.metrics.initialLoadTime,
            chartRenderTime: validationResult.metrics.chartRenderTime,
            score: validationResult.score,
            recommendations: validationResult.recommendations,
          });
        }

        setIsLoading(false);
        console.info("パフォーマンス最適化システムの初期化完了");
      } catch (error) {
        console.error("パフォーマンス最適化システムの初期化に失敗:", error);
        setError(error instanceof Error ? error.message : "不明なエラーが発生しました");
        setIsLoading(false);
      }
    };

    initializePerformance();
  }, [
    enableMemoryOptimization,
    enableLazyLoading,
    enableProgressiveLoading,
    enableCacheOptimization,
    enablePerformanceValidation,
    targetInitialLoadTime,
    targetChartRenderTime,
    targetMemoryReduction,
    enableRealTimeMonitoring,
    enableAutoOptimization,
  ]);

  // パフォーマンス監視
  useEffect(() => {
    if (!enableRealTimeMonitoring) return;

    const monitorPerformance = () => {
      const memoryUsage = frontendMemoryOptimizer.getCurrentMemoryUsage();
      
      setPerformanceStatus(prev => ({
        ...prev,
        memoryUsage,
      }));

      // 自動最適化の実行
      if (enableAutoOptimization && memoryUsage > 100) {
        unifiedPerformanceSystem.optimize();
      }
    };

    const interval = setInterval(monitorPerformance, 10000); // 10秒間隔
    return () => clearInterval(interval);
  }, [enableRealTimeMonitoring, enableAutoOptimization]);

  // パフォーマンス最適化の実行
  const optimizePerformance = useCallback(async () => {
    try {
      console.info("パフォーマンス最適化を実行中...");
      
      await unifiedPerformanceSystem.optimize();
      
      const validationResult = await unifiedPerformanceSystem.validatePerformance();
      
      setPerformanceStatus({
        isOptimized: validationResult.success,
        memoryUsage: validationResult.metrics.memoryUsage,
        memoryReduction: validationResult.metrics.memoryReduction,
        initialLoadTime: validationResult.metrics.initialLoadTime,
        chartRenderTime: validationResult.metrics.chartRenderTime,
        score: validationResult.score,
        recommendations: validationResult.recommendations,
      });
      
      console.info("パフォーマンス最適化完了");
    } catch (error) {
      console.error("パフォーマンス最適化に失敗:", error);
    }
  }, []);

  // パフォーマンスレポートの生成
  const generatePerformanceReport = useCallback(() => {
    const report = unifiedPerformanceSystem.generatePerformanceReport();
    console.info("パフォーマンスレポート:", report);
    return report;
  }, []);

  // メモリ最適化の実行
  const optimizeMemory = useCallback(() => {
    frontendMemoryOptimizer.optimizeMemory();
  }, []);

  // キャッシュ最適化の実行
  const optimizeCache = useCallback(() => {
    optimizedCacheStrategy.cleanup();
  }, []);

  // パフォーマンス設定の最適化
  const performanceSettings = useMemo(() => ({
    memoryOptimization: enableMemoryOptimization,
    lazyLoading: enableLazyLoading,
    progressiveLoading: enableProgressiveLoading,
    cacheOptimization: enableCacheOptimization,
    performanceValidation: enablePerformanceValidation,
    realTimeMonitoring: enableRealTimeMonitoring,
    autoOptimization: enableAutoOptimization,
    targets: {
      initialLoadTime: targetInitialLoadTime,
      chartRenderTime: targetChartRenderTime,
      memoryReduction: targetMemoryReduction,
    },
  }), [
    enableMemoryOptimization,
    enableLazyLoading,
    enableProgressiveLoading,
    enableCacheOptimization,
    enablePerformanceValidation,
    enableRealTimeMonitoring,
    enableAutoOptimization,
    targetInitialLoadTime,
    targetChartRenderTime,
    targetMemoryReduction,
  ]);

  // クリーンアップ
  useEffect(() => {
    return () => {
      unifiedPerformanceSystem.cleanup();
    };
  }, []);

  // ローディング状態の表示
  if (isLoading) {
    return (
      <div className="performance-optimization-loading">
        <div className="loading-spinner" />
        <p>パフォーマンス最適化システムを初期化中...</p>
      </div>
    );
  }

  // エラー状態の表示
  if (error) {
    return (
      <div className="performance-optimization-error">
        <h3>パフォーマンス最適化システムの初期化に失敗しました</h3>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>
          再試行
        </button>
      </div>
    );
  }

  return (
    <div 
      className="performance-optimized-app"
      data-performance-settings={JSON.stringify(performanceSettings)}
      data-performance-status={JSON.stringify(performanceStatus)}
    >
      {/* パフォーマンス最適化コンテキスト */}
      <PerformanceContext.Provider value={{
        performanceStatus,
        optimizePerformance,
        generatePerformanceReport,
        optimizeMemory,
        optimizeCache,
        performanceSettings,
      }}>
        {children}
      </PerformanceContext.Provider>
      
      {/* パフォーマンス情報の表示（開発環境のみ） */}
      {process.env.NODE_ENV === "development" && (
        <div className="performance-info">
          <h4>パフォーマンス情報</h4>
          <ul>
            <li>最適化状態: {performanceStatus.isOptimized ? "最適化済み" : "未最適化"}</li>
            <li>メモリ使用量: {performanceStatus.memoryUsage}MB</li>
            <li>メモリ削減: {performanceStatus.memoryReduction.toFixed(1)}%</li>
            <li>初回読み込み時間: {performanceStatus.initialLoadTime.toFixed(2)}ms</li>
            <li>チャート描画時間: {performanceStatus.chartRenderTime.toFixed(2)}ms</li>
            <li>スコア: {performanceStatus.score.toFixed(1)}%</li>
          </ul>
          
          {performanceStatus.recommendations.length > 0 && (
            <div className="recommendations">
              <h5>推奨事項</h5>
              <ul>
                {performanceStatus.recommendations.map((recommendation, index) => (
                  <li key={index}>{recommendation}</li>
                ))}
              </ul>
            </div>
          )}
          
          <div className="performance-actions">
            <button onClick={optimizePerformance}>
              パフォーマンス最適化
            </button>
            <button onClick={optimizeMemory}>
              メモリ最適化
            </button>
            <button onClick={optimizeCache}>
              キャッシュ最適化
            </button>
            <button onClick={generatePerformanceReport}>
              レポート生成
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// パフォーマンスコンテキスト
interface PerformanceContextType {
  performanceStatus: PerformanceStatus;
  optimizePerformance: () => Promise<void>;
  generatePerformanceReport: () => any;
  optimizeMemory: () => void;
  optimizeCache: () => void;
  performanceSettings: any;
}

const PerformanceContext = React.createContext<PerformanceContextType | null>(null);

// パフォーマンスフック
export function usePerformance() {
  const context = React.useContext(PerformanceContext);
  if (!context) {
    throw new Error("usePerformance must be used within a PerformanceOptimizedApp");
  }
  return context;
}

// パフォーマンス最適化フック
export function usePerformanceOptimization() {
  const { performanceStatus, optimizePerformance, optimizeMemory, optimizeCache } = usePerformance();
  
  const isOptimized = performanceStatus.isOptimized;
  const memoryUsage = performanceStatus.memoryUsage;
  const memoryReduction = performanceStatus.memoryReduction;
  const score = performanceStatus.score;
  const recommendations = performanceStatus.recommendations;
  
  return {
    isOptimized,
    memoryUsage,
    memoryReduction,
    score,
    recommendations,
    optimizePerformance,
    optimizeMemory,
    optimizeCache,
  };
}

// パフォーマンス監視フック
export function usePerformanceMonitoring() {
  const [metrics, setMetrics] = useState({
    memoryUsage: 0,
    renderTime: 0,
    loadTime: 0,
  });

  useEffect(() => {
    const updateMetrics = () => {
      const memoryUsage = frontendMemoryOptimizer.getCurrentMemoryUsage();
      const renderTime = performance.now();
      const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
      
      setMetrics({
        memoryUsage,
        renderTime,
        loadTime,
      });
    };

    const interval = setInterval(updateMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  return metrics;
}

export default PerformanceOptimizedApp;
