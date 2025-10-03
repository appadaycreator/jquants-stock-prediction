'use client';

import React, { useRef, useEffect, useState, useCallback } from 'react';

interface ChartData {
  time: number;
  value: number;
  volume?: number;
}

interface LightweightChartProps {
  data: ChartData[];
  type: 'line' | 'candlestick' | 'volume';
  height?: number;
  width?: number;
  color?: string;
  showGrid?: boolean;
  showCrosshair?: boolean;
  onDataPointClick?: (data: ChartData) => void;
  className?: string;
}

export function LightweightChart({
  data,
  type,
  height = 200,
  width,
  color = '#3b82f6',
  showGrid = true,
  showCrosshair = true,
  onDataPointClick,
  className = ''
}: LightweightChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [hoveredPoint, setHoveredPoint] = useState<ChartData | null>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  // データのダウンサンプリング
  const downsampledData = useCallback((data: ChartData[], maxPoints: number = 100) => {
    if (data.length <= maxPoints) return data;
    
    const step = Math.ceil(data.length / maxPoints);
    const result: ChartData[] = [];
    
    for (let i = 0; i < data.length; i += step) {
      result.push(data[i]);
    }
    
    // 最後のデータポイントを必ず含める
    if (result[result.length - 1] !== data[data.length - 1]) {
      result.push(data[data.length - 1]);
    }
    
    return result;
  }, []);

  // キャンバスサイズの更新
  useEffect(() => {
    const updateDimensions = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      
      const rect = canvas.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      
      setDimensions({
        width: width || rect.width,
        height: height
      });
      
      canvas.width = (width || rect.width) * dpr;
      canvas.height = height * dpr;
      
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.scale(dpr, dpr);
      }
    };
    
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    
    return () => window.removeEventListener('resize', updateDimensions);
  }, [width, height]);

  // チャートの描画
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !data.length) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    setIsLoading(true);
    
    // データのダウンサンプリング
    const processedData = downsampledData(data);
    
    const drawChart = () => {
      ctx.clearRect(0, 0, dimensions.width, dimensions.height);
      
      if (processedData.length === 0) return;
      
      const padding = 20;
      const chartWidth = dimensions.width - padding * 2;
      const chartHeight = dimensions.height - padding * 2;
      
      // データの範囲を計算
      const values = processedData.map(d => d.value);
      const minValue = Math.min(...values);
      const maxValue = Math.max(...values);
      const valueRange = maxValue - minValue;
      
      // グリッドの描画
      if (showGrid) {
        ctx.strokeStyle = '#e5e7eb';
        ctx.lineWidth = 1;
        
        // 水平線
        for (let i = 0; i <= 4; i++) {
          const y = padding + (chartHeight / 4) * i;
          ctx.beginPath();
          ctx.moveTo(padding, y);
          ctx.lineTo(padding + chartWidth, y);
          ctx.stroke();
        }
        
        // 垂直線
        for (let i = 0; i <= 4; i++) {
          const x = padding + (chartWidth / 4) * i;
          ctx.beginPath();
          ctx.moveTo(x, padding);
          ctx.lineTo(x, padding + chartHeight);
          ctx.stroke();
        }
      }
      
      // チャートの描画
      if (type === 'line') {
        drawLineChart(ctx, processedData, padding, chartWidth, chartHeight, minValue, valueRange);
      } else if (type === 'candlestick') {
        drawCandlestickChart(ctx, processedData, padding, chartWidth, chartHeight, minValue, valueRange);
      } else if (type === 'volume') {
        drawVolumeChart(ctx, processedData, padding, chartWidth, chartHeight);
      }
      
      // ホバー効果
      if (hoveredPoint) {
        drawHoverEffect(ctx, hoveredPoint, padding, chartWidth, chartHeight, minValue, valueRange);
      }
    };
    
    drawChart();
    setIsLoading(false);
  }, [data, type, dimensions, downsampledData, hoveredPoint, showGrid]);

  const drawLineChart = (
    ctx: CanvasRenderingContext2D,
    data: ChartData[],
    padding: number,
    chartWidth: number,
    chartHeight: number,
    minValue: number,
    valueRange: number
  ) => {
    // グラデーション背景
    const gradient = ctx.createLinearGradient(0, padding, 0, padding + chartHeight);
    gradient.addColorStop(0, `${color}20`);
    gradient.addColorStop(1, `${color}05`);
    
    // エリア塗りつぶし
    ctx.fillStyle = gradient;
    ctx.beginPath();
    data.forEach((point, index) => {
      const x = padding + (chartWidth / (data.length - 1)) * index;
      const y = padding + chartHeight - ((point.value - minValue) / valueRange) * chartHeight;
      
      if (index === 0) {
        ctx.moveTo(x, padding + chartHeight);
        ctx.lineTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.lineTo(padding + chartWidth, padding + chartHeight);
    ctx.closePath();
    ctx.fill();
    
    // ライン描画
    ctx.strokeStyle = color;
    ctx.lineWidth = 3;
    ctx.shadowColor = color;
    ctx.shadowBlur = 10;
    ctx.beginPath();
    
    data.forEach((point, index) => {
      const x = padding + (chartWidth / (data.length - 1)) * index;
      const y = padding + chartHeight - ((point.value - minValue) / valueRange) * chartHeight;
      
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    
    ctx.stroke();
    ctx.shadowBlur = 0;
  };

  const drawCandlestickChart = (
    ctx: CanvasRenderingContext2D,
    data: ChartData[],
    padding: number,
    chartWidth: number,
    chartHeight: number,
    minValue: number,
    valueRange: number
  ) => {
    const barWidth = chartWidth / data.length * 0.6;
    
    data.forEach((point, index) => {
      const x = padding + (chartWidth / data.length) * index + (chartWidth / data.length - barWidth) / 2;
      const y = padding + chartHeight - ((point.value - minValue) / valueRange) * chartHeight;
      
      // 改良されたローソク足の描画
      const isPositive = point.value >= 0;
      const candleColor = isPositive ? '#10b981' : '#ef4444';
      
      // 影効果
      ctx.shadowColor = candleColor;
      ctx.shadowBlur = 5;
      ctx.shadowOffsetX = 2;
      ctx.shadowOffsetY = 2;
      
      // ローソク足本体
      ctx.fillStyle = candleColor;
      ctx.fillRect(x, y - 2, barWidth, 4);
      
      // 境界線
      ctx.strokeStyle = isPositive ? '#059669' : '#dc2626';
      ctx.lineWidth = 1;
      ctx.strokeRect(x, y - 2, barWidth, 4);
      
      ctx.shadowBlur = 0;
      ctx.shadowOffsetX = 0;
      ctx.shadowOffsetY = 0;
    });
  };

  const drawVolumeChart = (
    ctx: CanvasRenderingContext2D,
    data: ChartData[],
    padding: number,
    chartWidth: number,
    chartHeight: number
  ) => {
    const maxVolume = Math.max(...data.map(d => d.volume || 0));
    
    data.forEach((point, index) => {
      const x = padding + (chartWidth / data.length) * index;
      const barWidth = chartWidth / data.length * 0.8;
      const barHeight = ((point.volume || 0) / maxVolume) * chartHeight;
      
      // グラデーション効果
      const gradient = ctx.createLinearGradient(0, padding + chartHeight - barHeight, 0, padding + chartHeight);
      gradient.addColorStop(0, `${color}80`);
      gradient.addColorStop(1, `${color}40`);
      
      ctx.fillStyle = gradient;
      ctx.fillRect(x, padding + chartHeight - barHeight, barWidth, barHeight);
      
      // 境界線
      ctx.strokeStyle = color;
      ctx.lineWidth = 1;
      ctx.strokeRect(x, padding + chartHeight - barHeight, barWidth, barHeight);
    });
  };

  const drawHoverEffect = (
    ctx: CanvasRenderingContext2D,
    point: ChartData,
    padding: number,
    chartWidth: number,
    chartHeight: number,
    minValue: number,
    valueRange: number
  ) => {
    const index = data.findIndex(d => d.time === point.time);
    if (index === -1) return;
    
    const x = padding + (chartWidth / (data.length - 1)) * index;
    const y = padding + chartHeight - ((point.value - minValue) / valueRange) * chartHeight;
    
    // ホバーライン
    ctx.strokeStyle = '#6b7280';
    ctx.lineWidth = 1;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(x, padding);
    ctx.lineTo(x, padding + chartHeight);
    ctx.stroke();
    ctx.setLineDash([]);
    
    // ホバーポイント
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, 2 * Math.PI);
    ctx.fill();
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!showCrosshair) return;
    
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // 最も近いデータポイントを見つける
    const padding = 20;
    const chartWidth = dimensions.width - padding * 2;
    const pointIndex = Math.round(((x - padding) / chartWidth) * (data.length - 1));
    
    if (pointIndex >= 0 && pointIndex < data.length) {
      setHoveredPoint(data[pointIndex]);
    }
  };

  const handleMouseLeave = () => {
    setHoveredPoint(null);
  };

  const handleClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!onDataPointClick || !hoveredPoint) return;
    
    onDataPointClick(hoveredPoint);
  };

  if (isLoading) {
    return (
      <div className={`flex items-center justify-center bg-gray-50 ${className}`} style={{ height, width }}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-300 rounded w-24"></div>
        </div>
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      <canvas
        ref={canvasRef}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        onClick={handleClick}
        className="cursor-crosshair"
        style={{ width: dimensions.width || '100%', height }}
      />
      
      {hoveredPoint && (
        <div className="absolute top-2 left-2 bg-white/95 backdrop-blur-sm rounded-xl shadow-2xl p-3 text-sm border border-gray-200">
          <div className="flex items-center space-x-2 mb-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <div className="font-semibold text-gray-900">¥{hoveredPoint.value.toLocaleString()}</div>
          </div>
          <div className="text-gray-600 text-xs">
            {new Date(hoveredPoint.time).toLocaleDateString('ja-JP', {
              year: 'numeric',
              month: 'short',
              day: 'numeric',
              weekday: 'short'
            })}
          </div>
          {hoveredPoint.volume && (
            <div className="text-gray-500 text-xs mt-1">
              出来高: {hoveredPoint.volume.toLocaleString()}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
