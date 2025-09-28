"use client";

import { useState, useEffect, useRef } from "react";
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell, ScatterChart, Scatter,
} from "recharts";
import { 
  Maximize2, 
  Minimize2, 
  RotateCcw, 
  ZoomIn, 
  ZoomOut,
  Download,
  Share2,
  BarChart3,
  Target,
  TrendingUp,
} from "lucide-react";

interface MobileChartProps {
  data: any[];
  type: 'line' | 'bar' | 'pie' | 'scatter';
  title: string;
  dataKey: string;
  xAxisKey?: string;
  lines?: Array<{
    dataKey: string;
    stroke: string;
    strokeWidth?: number;
  }>;
  height?: number;
  onFullscreen?: () => void;
  isFullscreen?: boolean;
}

export default function MobileChart({
  data,
  type,
  title,
  dataKey,
  xAxisKey = 'date',
  lines = [],
  height = 300,
  onFullscreen,
  isFullscreen = false,
}: MobileChartProps) {
  const [isFullscreenMode, setIsFullscreenMode] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [panOffset, setPanOffset] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState(0);
  const chartRef = useRef<HTMLDivElement>(null);

  // タッチ操作の処理
  const handleTouchStart = (e: React.TouchEvent) => {
    if (e.touches.length === 1) {
      setIsDragging(true);
      setDragStart(e.touches[0].clientX);
    }
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (isDragging && e.touches.length === 1) {
      const deltaX = e.touches[0].clientX - dragStart;
      setPanOffset(prev => prev + deltaX * 0.1);
      setDragStart(e.touches[0].clientX);
    }
  };

  const handleTouchEnd = () => {
    setIsDragging(false);
  };

  // ピンチズームの処理
  const handleTouchStartMulti = (e: React.TouchEvent) => {
    if (e.touches.length === 2) {
      const touch1 = e.touches[0];
      const touch2 = e.touches[1];
      const distance = Math.sqrt(
        Math.pow(touch2.clientX - touch1.clientX, 2) +
        Math.pow(touch2.clientY - touch1.clientY, 2)
      );
      (e.target as any).initialDistance = distance;
    }
  };

  const handleTouchMoveMulti = (e: React.TouchEvent) => {
    if (e.touches.length === 2) {
      const touch1 = e.touches[0];
      const touch2 = e.touches[1];
      const distance = Math.sqrt(
        Math.pow(touch2.clientX - touch1.clientX, 2) +
        Math.pow(touch2.clientY - touch1.clientY, 2)
      );
      const initialDistance = (e.target as any).initialDistance;
      
      if (initialDistance) {
        const scale = distance / initialDistance;
        setZoomLevel(Math.max(0.5, Math.min(3, zoomLevel * scale)));
        (e.target as any).initialDistance = distance;
      }
    }
  };

  const toggleFullscreen = () => {
    if (isFullscreenMode) {
      document.exitFullscreen?.();
      setIsFullscreenMode(false);
    } else {
      chartRef.current?.requestFullscreen?.();
      setIsFullscreenMode(true);
    }
    onFullscreen?.();
  };

  const resetZoom = () => {
    setZoomLevel(1);
    setPanOffset(0);
  };

  const zoomIn = () => {
    setZoomLevel(prev => Math.min(3, prev * 1.2));
  };

  const zoomOut = () => {
    setZoomLevel(prev => Math.max(0.5, prev / 1.2));
  };

  const downloadChart = () => {
    // チャートの画像ダウンロード機能
    const canvas = chartRef.current?.querySelector('canvas');
    if (canvas) {
      const link = document.createElement('a');
      link.download = `${title}.png`;
      link.href = canvas.toDataURL();
      link.click();
    }
  };

  const shareChart = () => {
    if (navigator.share) {
      navigator.share({
        title: title,
        text: `J-Quants株価予測: ${title}`,
        url: window.location.href,
      });
    } else {
      // フォールバック: URLをクリップボードにコピー
      navigator.clipboard.writeText(window.location.href);
      alert('URLをクリップボードにコピーしました');
    }
  };

  const renderEmptyState = () => {
    const getIcon = () => {
      switch (type) {
        case 'bar':
          return <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-400" />;
        case 'pie':
          return <Target className="h-12 w-12 mx-auto mb-4 text-gray-400" />;
        case 'scatter':
          return <TrendingUp className="h-12 w-12 mx-auto mb-4 text-gray-400" />;
        default:
          return <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-400" />;
      }
    };

    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        <div className="text-center">
          {getIcon()}
          <p className="text-lg font-medium">データがありません</p>
          <p className="text-sm">分析を実行してデータを生成してください</p>
        </div>
      </div>
    );
  };

  const renderChart = () => {
    // データが空の場合は空の状態を表示
    if (!data || data.length === 0) {
      return renderEmptyState();
    }

    const commonProps = {
      data: data,
      margin: { top: 20, right: 30, left: 20, bottom: 5 },
    };

    switch (type) {
      case 'line':
        return (
          <LineChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={xAxisKey} />
            <YAxis />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: '14px',
              }}
            />
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
              />
            ))}
          </LineChart>
        );

      case 'bar':
        return (
          <BarChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={xAxisKey} />
            <YAxis />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: '14px',
              }}
            />
            <Legend />
            <Bar dataKey={dataKey} fill="#8884d8" />
          </BarChart>
        );

      case 'pie':
        const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8", "#82CA9D"];
        return (
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={(props: any) => `${props.name} ${(props.percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey={dataKey}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        );

      case 'scatter':
        return (
          <ScatterChart {...commonProps}>
            <CartesianGrid />
            <XAxis dataKey="actual" name="実際値" />
            <YAxis dataKey="predicted" name="予測値" />
            <Tooltip cursor={{ strokeDasharray: "3 3" }} />
            <Scatter name="予測ポイント" data={data} fill="#8884d8" />
          </ScatterChart>
        );

      default:
        return <div>サポートされていないチャートタイプです</div>;
    }
  };

  return (
    <div 
      ref={chartRef}
      className={`bg-white rounded-lg shadow-sm border ${
        isFullscreenMode ? 'fixed inset-0 z-50 p-4' : ''
      }`}
      style={{
        transform: `scale(${zoomLevel}) translateX(${panOffset}px)`,
        transition: isDragging ? 'none' : 'transform 0.1s ease-out',
      }}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
    >
      {/* チャートヘッダー */}
      <div className="flex items-center justify-between p-4 border-b">
        <h3 className="text-lg font-medium text-gray-900">{title}</h3>
        <div className="flex items-center space-x-2">
          {/* ズームコントロール */}
          <div className="flex items-center space-x-1">
            <button
              onClick={zoomOut}
              className="p-1 rounded hover:bg-gray-100 transition-colors"
              disabled={zoomLevel <= 0.5}
            >
              <ZoomOut className="h-4 w-4 text-gray-600" />
            </button>
            <span className="text-xs text-gray-500 min-w-[3rem] text-center">
              {Math.round(zoomLevel * 100)}%
            </span>
            <button
              onClick={zoomIn}
              className="p-1 rounded hover:bg-gray-100 transition-colors"
              disabled={zoomLevel >= 3}
            >
              <ZoomIn className="h-4 w-4 text-gray-600" />
            </button>
          </div>

          {/* アクションボタン */}
          <div className="flex items-center space-x-1">
            <button
              onClick={resetZoom}
              className="p-1 rounded hover:bg-gray-100 transition-colors"
              title="リセット"
            >
              <RotateCcw className="h-4 w-4 text-gray-600" />
            </button>
            
            <button
              onClick={downloadChart}
              className="p-1 rounded hover:bg-gray-100 transition-colors"
              title="ダウンロード"
            >
              <Download className="h-4 w-4 text-gray-600" />
            </button>
            
            <button
              onClick={shareChart}
              className="p-1 rounded hover:bg-gray-100 transition-colors"
              title="共有"
            >
              <Share2 className="h-4 w-4 text-gray-600" />
            </button>
            
            <button
              onClick={toggleFullscreen}
              className="p-1 rounded hover:bg-gray-100 transition-colors"
              title={isFullscreenMode ? "フルスクリーン終了" : "フルスクリーン"}
            >
              {isFullscreenMode ? (
                <Minimize2 className="h-4 w-4 text-gray-600" />
              ) : (
                <Maximize2 className="h-4 w-4 text-gray-600" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* チャート本体 */}
      <div className="p-4">
        <ResponsiveContainer width="100%" height={height}>
          {renderChart()}
        </ResponsiveContainer>
      </div>

      {/* モバイル操作ガイド */}
      {!isFullscreenMode && (
        <div className="px-4 pb-4">
          <div className="text-xs text-gray-500 bg-gray-50 rounded-lg p-2">
            <div className="flex items-center justify-between">
              <span>📱 モバイル操作:</span>
              <span>スワイプで移動 • ピンチでズーム</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
