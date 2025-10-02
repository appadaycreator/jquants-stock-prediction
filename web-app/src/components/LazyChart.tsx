"use client";

import { useEffect, useState, useCallback, useRef, useMemo } from "react";
import { frontendMemoryOptimizer } from "@/lib/frontend-memory-optimizer";

interface LazyChartProps {
  data: any[];
  type: "line" | "candlestick" | "volume" | "technical";
  height?: number;
  width?: number;
  enableLazyLoading?: boolean;
  enableDataCompression?: boolean;
  maxDataPoints?: number;
  onLoadStart?: () => void;
  onLoadComplete?: () => void;
  onError?: (error: Error) => void;
}

interface ChartState {
  isLoading: boolean;
  isVisible: boolean;
  isLoaded: boolean;
  error: Error | null;
  renderTime: number;
  memoryUsage: number;
}

export default function LazyChart({
  data,
  type,
  height = 400,
  width = 800,
  enableLazyLoading = true,
  enableDataCompression = true,
  maxDataPoints = 3000,
  onLoadStart,
  onLoadComplete,
  onError,
}: LazyChartProps) {
  const [chartState, setChartState] = useState<ChartState>({
    isLoading: false,
    isVisible: false,
    isLoaded: false,
    error: null,
    renderTime: 0,
    memoryUsage: 0,
  });

  const chartRef = useRef<HTMLDivElement>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const chartInstanceRef = useRef<any>(null);
  const renderStartTime = useRef<number>(0);

  // データの最適化
  const optimizedData = useMemo(() => {
    if (!enableDataCompression || data.length <= maxDataPoints) {
      return data;
    }

    const startTime = performance.now();
    const optimized = frontendMemoryOptimizer.downsampleChartData(data, maxDataPoints);
    const endTime = performance.now();

    console.info("チャートデータ最適化:", {
      original: data.length,
      optimized: optimized.length,
      compressionRatio: `${((optimized.length / data.length) * 100).toFixed(1)}%`,
      processingTime: `${(endTime - startTime).toFixed(2)}ms`,
    });

    return optimized;
  }, [data, maxDataPoints, enableDataCompression]);

  // 可視性の監視
  useEffect(() => {
    if (!enableLazyLoading) {
      setChartState(prev => ({ ...prev, isVisible: true }));
      return;
    }

    if (!chartRef.current) return;

    observerRef.current = new IntersectionObserver(
      ([entry]) => {
        setChartState(prev => ({ ...prev, isVisible: entry.isIntersecting }));
      },
      {
        rootMargin: "100px", // 100px手前で読み込み開始
        threshold: 0.1,
      },
    );

    observerRef.current.observe(chartRef.current);

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [enableLazyLoading]);

  // チャートの遅延読み込み
  useEffect(() => {
    if (!chartState.isVisible || chartState.isLoaded || chartState.isLoading) {
      return;
    }

    const loadChart = async () => {
      try {
        setChartState(prev => ({ ...prev, isLoading: true, error: null }));
        onLoadStart?.();

        renderStartTime.current = performance.now();

        // チャートライブラリの動的読み込み
        const chartModule = await importChartLibrary(type);
        
        // メモリ使用量の記録
        const memoryBefore = frontendMemoryOptimizer.getCurrentMemoryUsage();

        // チャートの初期化
        if (chartRef.current) {
          // chart.js または lightweight-charts の適切なコンストラクタを使用
          const ChartConstructor = (chartModule as any).default || chartModule;
          chartInstanceRef.current = new ChartConstructor(chartRef.current, {
            data: optimizedData,
            height,
            width,
            type,
          });

          // チャートの描画完了を待つ
          await new Promise(resolve => {
            if (chartInstanceRef.current) {
              chartInstanceRef.current.on("ready", resolve);
            } else {
              resolve(void 0);
            }
          });

          const renderTime = performance.now() - renderStartTime.current;
          const memoryAfter = frontendMemoryOptimizer.getCurrentMemoryUsage();
          const memoryUsed = memoryAfter - memoryBefore;

          setChartState(prev => ({
            ...prev,
            isLoading: false,
            isLoaded: true,
            renderTime,
            memoryUsage: memoryUsed,
          }));

          onLoadComplete?.();

          console.info("チャート読み込み完了:", {
            type,
            renderTime: `${renderTime.toFixed(2)}ms`,
            memoryUsed: `${memoryUsed}MB`,
            dataPoints: optimizedData.length,
            status: renderTime < 1000 ? "FAST" : "SLOW",
          });
        }
      } catch (error) {
        console.error("チャート読み込みエラー:", error);
        setChartState(prev => ({
          ...prev,
          isLoading: false,
          error: error as Error,
        }));
        onError?.(error as Error);
      }
    };

    loadChart();
  }, [chartState.isVisible, chartState.isLoaded, chartState.isLoading, optimizedData, type, height, width, onLoadStart, onLoadComplete, onError]);

  // チャートライブラリの動的読み込み
  const importChartLibrary = useCallback(async (chartType: string) => {
    const startTime = performance.now();

    let chartModule;
    switch (chartType) {
      case "line":
        chartModule = await import("chart.js");
        break;
      case "candlestick":
        chartModule = await import("lightweight-charts");
        break;
      case "volume":
        chartModule = await import("chart.js");
        break;
      case "technical":
        chartModule = await import("chart.js");
        break;
      default:
        chartModule = await import("chart.js");
    }

    const loadTime = performance.now() - startTime;
    console.info("チャートライブラリ読み込み:", {
      type: chartType,
      loadTime: `${loadTime.toFixed(2)}ms`,
      status: loadTime < 500 ? "FAST" : "NORMAL",
    });

    return chartModule;
  }, []);

  // チャートの再描画
  const redrawChart = useCallback(() => {
    if (!chartInstanceRef.current || !chartState.isLoaded) return;

    const startTime = performance.now();
    chartInstanceRef.current.updateData(optimizedData);
    const renderTime = performance.now() - startTime;

    console.info("チャート再描画:", {
      renderTime: `${renderTime.toFixed(2)}ms`,
      dataPoints: optimizedData.length,
    });
  }, [optimizedData, chartState.isLoaded]);

  // データの更新
  useEffect(() => {
    if (chartState.isLoaded) {
      redrawChart();
    }
  }, [optimizedData, redrawChart, chartState.isLoaded]);

  // メモリ最適化
  const optimizeMemory = useCallback(() => {
    if (chartInstanceRef.current) {
      chartInstanceRef.current.destroy();
      chartInstanceRef.current = null;
    }

    frontendMemoryOptimizer.optimizeMemory();
    
    setChartState(prev => ({
      ...prev,
      isLoaded: false,
      memoryUsage: 0,
    }));
  }, []);

  // パフォーマンス監視
  useEffect(() => {
    if (!chartState.isLoaded) return;

    const monitor = setInterval(() => {
      const memoryUsage = frontendMemoryOptimizer.getCurrentMemoryUsage();
      
      if (memoryUsage > 100) { // 100MB超過
        console.warn("チャートメモリ使用量が高い:", `${memoryUsage}MB`);
        optimizeMemory();
      }
    }, 10000);

    return () => clearInterval(monitor);
  }, [chartState.isLoaded, optimizeMemory]);

  // クリーンアップ
  useEffect(() => {
    return () => {
      if (chartInstanceRef.current) {
        chartInstanceRef.current.destroy();
      }
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, []);

  // ローディング状態の表示
  if (chartState.isLoading) {
    return (
      <div 
        ref={chartRef}
        className="lazy-chart-container"
        style={{ height, width }}
      >
        <div className="chart-loading">
          <div className="loading-spinner" />
          <p>チャートを読み込み中...</p>
        </div>
      </div>
    );
  }

  // エラー状態の表示
  if (chartState.error) {
    return (
      <div 
        ref={chartRef}
        className="lazy-chart-container"
        style={{ height, width }}
      >
        <div className="chart-error">
          <p>チャートの読み込みに失敗しました</p>
          <button onClick={() => setChartState(prev => ({ ...prev, error: null, isLoaded: false }))}>
            再試行
          </button>
        </div>
      </div>
    );
  }

  // 遅延読み込み待機状態
  if (!chartState.isVisible) {
    return (
      <div 
        ref={chartRef}
        className="lazy-chart-container"
        style={{ height, width }}
      >
        <div className="chart-placeholder">
          <p>チャートを表示する準備中...</p>
        </div>
      </div>
    );
  }

  // チャートの表示
  return (
    <div className="lazy-chart-wrapper">
      <div 
        ref={chartRef}
        className="lazy-chart-container"
        style={{ height, width }}
        data-chart-type={type}
        data-render-time={chartState.renderTime}
        data-memory-usage={chartState.memoryUsage}
      />
      
      {/* パフォーマンス情報 */}
      {process.env.NODE_ENV === "development" && (
        <div className="chart-performance-info">
          <small>
            描画時間: {chartState.renderTime.toFixed(2)}ms | 
            メモリ使用量: {chartState.memoryUsage}MB | 
            データポイント: {optimizedData.length}
          </small>
        </div>
      )}
    </div>
  );
}

// チャートの遅延読み込みフック
export function useLazyChart() {
  const [charts, setCharts] = useState<Map<string, any>>(new Map());

  const loadChart = useCallback(async (
    id: string,
    type: string,
    data: any[],
    options: any = {},
  ) => {
    if (charts.has(id)) {
      return charts.get(id);
    }

    try {
      const chartModule = await importChartLibrary(type);
      const ChartConstructor = (chartModule as any).default || chartModule;
      const chart = new ChartConstructor(data, options);
      
      setCharts(prev => new Map(prev).set(id, chart));
      return chart;
    } catch (error) {
      console.error("チャート読み込みエラー:", error);
      throw error;
    }
  }, [charts]);

  const unloadChart = useCallback((id: string) => {
    const chart = charts.get(id);
    if (chart) {
      chart.destroy();
      setCharts(prev => {
        const newCharts = new Map(prev);
        newCharts.delete(id);
        return newCharts;
      });
    }
  }, [charts]);

  const optimizeAllCharts = useCallback(() => {
    charts.forEach((chart, id) => {
      chart.optimize();
    });
  }, [charts]);

  return {
    loadChart,
    unloadChart,
    optimizeAllCharts,
    charts: Array.from(charts.keys()),
  };
}

// チャートライブラリの動的読み込み
async function importChartLibrary(type: string) {
  const startTime = performance.now();

  let chartModule;
  switch (type) {
    case "line":
      chartModule = await import("chart.js");
      break;
    case "candlestick":
      chartModule = await import("lightweight-charts");
      break;
    case "volume":
      chartModule = await import("chart.js");
      break;
    case "technical":
      chartModule = await import("chart.js");
      break;
    default:
      chartModule = await import("chart.js");
  }

  const loadTime = performance.now() - startTime;
  console.info("チャートライブラリ読み込み:", {
    type,
    loadTime: `${loadTime.toFixed(2)}ms`,
    status: loadTime < 500 ? "FAST" : "NORMAL",
  });

  return chartModule;
}
