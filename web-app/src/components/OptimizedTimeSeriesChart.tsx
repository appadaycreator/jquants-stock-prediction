/**
 * 最適化された時系列チャートコンポーネント
 * ダウンサンプリング、遅延読み込み、パフォーマンス監視
 */

import React, { useMemo, useState, useEffect, useCallback } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { parseToJst, jstLabel } from "@/lib/datetime";
import { performanceOptimizer } from "@/lib/performance-optimizer";
import { logDateConversionError, logDateConversionSuccess } from "@/lib/observability";

interface OptimizedTimeSeriesChartProps {
  data: Array<{
    date: string;
    [key: string]: any;
  }>;
  lines: Array<{
    dataKey: string;
    stroke: string;
    strokeWidth?: number;
    name: string;
  }>;
  title?: string;
  height?: number;
  maxDataPoints?: number;
  enableDownsampling?: boolean;
  enableLazyLoading?: boolean;
}

export default function OptimizedTimeSeriesChart({
  data,
  lines,
  title,
  height = 300,
  maxDataPoints = 3000,
  enableDownsampling = true,
  enableLazyLoading = true,
}: OptimizedTimeSeriesChartProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [chartData, setChartData] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [performanceMetrics, setPerformanceMetrics] = useState<any>(null);

  // Intersection Observer で遅延読み込み
  const chartRef = useCallback((node: HTMLDivElement | null) => {
    if (!node || !enableLazyLoading) {
      setIsVisible(true);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            setIsVisible(true);
            observer.unobserve(node);
          }
        });
      },
      { threshold: 0.1 },
    );

    observer.observe(node);
  }, [enableLazyLoading]);

  // データの最適化処理
  const optimizedData = useMemo(() => {
    if (!data || data.length === 0) {
      return [];
    }

    const startTime = performance.now();

    try {
      // 日付の正規化
      const normalizedData = data.map((item, index) => {
        try {
          const normalizedDate = parseToJst(item.date);
          
          if (!normalizedDate.isValid) {
            logDateConversionError(item.date, new Error("Invalid date format"), `OptimizedChart item ${index}`);
            return null;
          }

          const jstLabelResult = jstLabel(normalizedDate);
          logDateConversionSuccess(item.date, jstLabelResult, `OptimizedChart item ${index}`);

          return {
            ...item,
            date: jstLabelResult,
            timestamp: normalizedDate.toMillis(),
            originalDate: item.date,
          };
        } catch (error) {
          logDateConversionError(item.date, error as Error, `OptimizedChart item ${index}`);
          return null;
        }
      }).filter(item => item !== null);

      // ダウンサンプリング
      let finalData = normalizedData;
      if (enableDownsampling && normalizedData.length > maxDataPoints) {
        const downsamplingResult = performanceOptimizer.downsampleChartData(normalizedData, maxDataPoints);
        finalData = downsamplingResult.data;
        
        console.info("チャート最適化完了:", {
          original: downsamplingResult.originalCount,
          optimized: downsamplingResult.sampledCount,
          compressionRatio: `${(downsamplingResult.compressionRatio * 100).toFixed(1)}%`,
          performance: "OPTIMIZED",
        });
      }

      const processingTime = performance.now() - startTime;
      console.info("チャートデータ処理時間:", {
        processingTime: `${processingTime.toFixed(2)}ms`,
        dataPoints: finalData.length,
        status: processingTime < 100 ? "FAST" : "NORMAL",
      });

      return finalData;
    } catch (error) {
      console.error("チャートデータ最適化エラー:", error);
      return [];
    }
  }, [data, maxDataPoints, enableDownsampling]);

  // チャートデータの設定
  useEffect(() => {
    if (isVisible) {
      setIsLoading(true);
      
      // 非同期でデータを設定（UIブロックを防ぐ）
      requestAnimationFrame(() => {
        setChartData(optimizedData);
        setIsLoading(false);
      });
    }
  }, [isVisible, optimizedData]);

  // パフォーマンスメトリクスの取得
  useEffect(() => {
    if (isVisible && chartData.length > 0) {
      const metrics = performanceOptimizer.generatePerformanceReport();
      setPerformanceMetrics(metrics);
    }
  }, [isVisible, chartData]);

  // カスタムツールチップ
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium text-gray-900 mb-2">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {typeof entry.value === "number" ? entry.value.toFixed(2) : (entry.value ?? "N/A")}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  // カスタムX軸フォーマッタ
  const formatXAxisLabel = (tickItem: string) => {
    try {
      if (/^\d{4}-\d{2}-\d{2}$/.test(tickItem)) {
        return tickItem;
      }
      
      const dt = parseToJst(tickItem);
      if (dt.isValid) {
        return jstLabel(dt);
      }
      
      return "2024-01-01";
    } catch (error) {
      console.error("X軸ラベルフォーマットエラー:", error);
      return "2024-01-01";
    }
  };

  // ローディング状態
  if (!isVisible) {
    return (
      <div ref={chartRef} className="w-full h-64 bg-gray-50 rounded-lg flex items-center justify-center">
        <div className="text-center">
          <div className="animate-pulse">
            <div className="h-4 bg-gray-300 rounded w-3/4 mx-auto mb-2"></div>
            <div className="h-4 bg-gray-300 rounded w-1/2 mx-auto"></div>
          </div>
          <p className="text-sm text-gray-500 mt-2">チャートを読み込み中...</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="w-full h-64 bg-gray-50 rounded-lg flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
          <p className="text-sm text-gray-500">データを処理中...</p>
        </div>
      </div>
    );
  }

  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg">
        <div className="text-center">
          <svg className="h-12 w-12 text-gray-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <p className="text-gray-500">データがありません</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full">
      {title && (
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">{title}</h3>
          {performanceMetrics && (
            <div className="text-xs text-gray-500">
              {chartData.length}点 | LCP: {performanceMetrics.lcp?.toFixed(0)}ms
            </div>
          )}
        </div>
      )}
      <div className="relative">
        <ResponsiveContainer width="100%" height={height}>
          <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey="date" 
            tickFormatter={formatXAxisLabel}
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={60}
          />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          {lines.map((line, index) => (
            <Line
              key={index}
              type="monotone"
              dataKey={line.dataKey}
              stroke={line.stroke}
              strokeWidth={line.strokeWidth || 2}
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
              name={line.name}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
      </div>
    </div>
  );
}
