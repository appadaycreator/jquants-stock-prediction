/**
 * パフォーマンス監視フック
 * リアルタイムでパフォーマンスを監視・最適化
 */

import { useState, useEffect, useCallback } from "react";
import { performanceOptimizer } from "../lib/performance-optimizer";

interface UsePerformanceOptions {
  enableMonitoring?: boolean;
  reportInterval?: number;
  onPerformanceChange?: (metrics: any) => void;
  onOptimizationNeeded?: (recommendations: string[]) => void;
}

export function usePerformance(options: UsePerformanceOptions = {}) {
  const [metrics, setMetrics] = useState(performanceOptimizer.getMetrics());
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [report, setReport] = useState<any>(null);

  const {
    enableMonitoring = true,
    reportInterval = 30000, // 30秒
    onPerformanceChange,
    onOptimizationNeeded,
  } = options;

  // パフォーマンス監視
  useEffect(() => {
    if (!enableMonitoring) return;

    const interval = setInterval(() => {
      const currentMetrics = performanceOptimizer.getMetrics();
      setMetrics(currentMetrics);
      onPerformanceChange?.(currentMetrics);
    }, 1000); // 1秒ごとに更新

    return () => clearInterval(interval);
  }, [enableMonitoring, onPerformanceChange]);

  // パフォーマンスレポートの生成
  useEffect(() => {
    if (!enableMonitoring) return;

    const interval = setInterval(() => {
      const performanceReport = performanceOptimizer.generateReport();
      setReport(performanceReport);
      
      if (performanceReport.score < 70) {
        onOptimizationNeeded?.(performanceReport.recommendations);
      }
    }, reportInterval);

    return () => clearInterval(interval);
  }, [enableMonitoring, reportInterval, onOptimizationNeeded]);

  // 手動最適化
  const optimize = useCallback(async () => {
    setIsOptimizing(true);
    
    try {
      performanceOptimizer.optimize();
      
      // 最適化後のメトリクス更新
      const updatedMetrics = performanceOptimizer.getMetrics();
      setMetrics(updatedMetrics);
      
      // レポートの再生成
      const updatedReport = performanceOptimizer.generateReport();
      setReport(updatedReport);
      
    } catch (error) {
      console.error("最適化エラー:", error);
    } finally {
      setIsOptimizing(false);
    }
  }, []);

  // パフォーマンススコアの取得
  const getScore = useCallback(() => {
    if (!report) return 0;
    return report.score;
  }, [report]);

  // 推奨事項の取得
  const getRecommendations = useCallback(() => {
    if (!report) return [];
    return report.recommendations;
  }, [report]);

  // パフォーマンス状況の判定
  const getPerformanceStatus = useCallback(() => {
    const score = getScore();
    
    if (score >= 90) return { status: "excellent", color: "green" };
    if (score >= 70) return { status: "good", color: "blue" };
    if (score >= 50) return { status: "fair", color: "yellow" };
    return { status: "poor", color: "red" };
  }, [getScore]);

  return {
    metrics,
    report,
    isOptimizing,
    optimize,
    getScore,
    getRecommendations,
    getPerformanceStatus,
    isHealthy: getScore() >= 70,
    needsOptimization: getScore() < 70,
  };
}
