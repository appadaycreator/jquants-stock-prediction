"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { 
  ZoomIn, 
  ZoomOut, 
  RotateCcw, 
  Download, 
  Share2, 
  Maximize2,
  Minimize2,
  Move,
  BarChart3
} from "lucide-react";

interface MobileChartProps {
  data: any[];
  title?: string;
  height?: number;
  onFullscreen?: () => void;
  onDownload?: () => void;
  onShare?: () => void;
  className?: string;
}

export default function MobileChart({
  data,
  title = "チャート",
  height = 300,
  onFullscreen,
  onDownload,
  onShare,
  className = "",
}: MobileChartProps) {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [zoom, setZoom] = useState(1);
  const [panX, setPanX] = useState(0);
  const [panY, setPanY] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [lastTouch, setLastTouch] = useState<{ x: number; y: number } | null>(null);
  const [touchStartDistance, setTouchStartDistance] = useState(0);
  const [isPinching, setIsPinching] = useState(false);
  
  const chartRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // タッチ操作のハンドリング
  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    e.preventDefault();
    
    if (e.touches.length === 1) {
      // 単一タッチ：パン操作
      const touch = e.touches[0];
      setLastTouch({ x: touch.clientX, y: touch.clientY });
      setIsDragging(true);
    } else if (e.touches.length === 2) {
      // 二点タッチ：ピンチズーム
      const touch1 = e.touches[0];
      const touch2 = e.touches[1];
      const distance = Math.sqrt(
        Math.pow(touch2.clientX - touch1.clientX, 2) +
        Math.pow(touch2.clientY - touch1.clientY, 2)
      );
      setTouchStartDistance(distance);
      setIsPinching(true);
    }
  }, []);

  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    e.preventDefault();
    
    if (isDragging && e.touches.length === 1 && lastTouch) {
      // パン操作
      const touch = e.touches[0];
      const deltaX = touch.clientX - lastTouch.x;
      const deltaY = touch.clientY - lastTouch.y;
      
      setPanX(prev => Math.max(-200, Math.min(200, prev + deltaX)));
      setPanY(prev => Math.max(-200, Math.min(200, prev + deltaY)));
      setLastTouch({ x: touch.clientX, y: touch.clientY });
    } else if (isPinching && e.touches.length === 2) {
      // ピンチズーム
      const touch1 = e.touches[0];
      const touch2 = e.touches[1];
      const distance = Math.sqrt(
        Math.pow(touch2.clientX - touch1.clientX, 2) +
        Math.pow(touch2.clientY - touch1.clientY, 2)
      );
      
      if (touchStartDistance > 0) {
        const scale = distance / touchStartDistance;
        setZoom(prev => Math.max(0.5, Math.min(3, prev * scale)));
        setTouchStartDistance(distance);
      }
    }
  }, [isDragging, isPinching, lastTouch, touchStartDistance]);

  const handleTouchEnd = useCallback((e: React.TouchEvent) => {
    setIsDragging(false);
    setIsPinching(false);
    setLastTouch(null);
    setTouchStartDistance(0);
  }, []);

  // ズーム操作
  const handleZoomIn = useCallback(() => {
    setZoom(prev => Math.min(3, prev + 0.2));
  }, []);

  const handleZoomOut = useCallback(() => {
    setZoom(prev => Math.max(0.5, prev - 0.2));
  }, []);

  const handleReset = useCallback(() => {
    setZoom(1);
    setPanX(0);
    setPanY(0);
  }, []);

  // フルスクリーン切り替え
  const handleFullscreen = useCallback(() => {
    setIsFullscreen(!isFullscreen);
    if (onFullscreen) {
      onFullscreen();
    }
  }, [isFullscreen, onFullscreen]);

  // チャート描画
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !data.length) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // キャンバスサイズの設定
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * window.devicePixelRatio;
    canvas.height = rect.height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

    // 背景のクリア
    ctx.clearRect(0, 0, rect.width, rect.height);

    // データの準備
    const values = data.map(item => item.close || item.value || 0);
    const maxValue = Math.max(...values);
    const minValue = Math.min(...values);
    const valueRange = maxValue - minValue;

    if (valueRange === 0) return;

    // チャートの描画領域
    const padding = 40;
    const chartWidth = rect.width - padding * 2;
    const chartHeight = rect.height - padding * 2;

    // ズームとパンの適用
    ctx.save();
    ctx.translate(panX, panY);
    ctx.scale(zoom, zoom);

    // グリッド線の描画
    ctx.strokeStyle = "#e5e7eb";
    ctx.lineWidth = 1;
    for (let i = 0; i <= 5; i++) {
      const y = padding + (chartHeight / 5) * i;
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(padding + chartWidth, y);
      ctx.stroke();
    }

    // 価格ラインの描画
    ctx.strokeStyle = "#2563eb";
    ctx.lineWidth = 2;
    ctx.beginPath();

    values.forEach((value, index) => {
      const x = padding + (chartWidth / (values.length - 1)) * index;
      const y = padding + chartHeight - ((value - minValue) / valueRange) * chartHeight;
      
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });

    ctx.stroke();

    // データポイントの描画
    ctx.fillStyle = "#2563eb";
    values.forEach((value, index) => {
      const x = padding + (chartWidth / (values.length - 1)) * index;
      const y = padding + chartHeight - ((value - minValue) / valueRange) * chartHeight;
      
      ctx.beginPath();
      ctx.arc(x, y, 3, 0, 2 * Math.PI);
      ctx.fill();
    });

    ctx.restore();

    // Y軸ラベルの描画
    ctx.fillStyle = "#6b7280";
    ctx.font = "12px sans-serif";
    ctx.textAlign = "right";
    for (let i = 0; i <= 5; i++) {
      const value = minValue + (valueRange / 5) * (5 - i);
      const y = padding + (chartHeight / 5) * i;
      ctx.fillText(value.toFixed(0), padding - 10, y + 4);
    }

  }, [data, zoom, panX, panY]);

  return (
    <div className={`mobile-chart ${className}`}>
      {/* チャートヘッダー */}
      <div className="mobile-chart-header">
        <div className="flex items-center space-x-2">
          <BarChart3 className="h-5 w-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        </div>
        
        <div className="flex items-center space-x-2">
          {/* ズームコントロール */}
          <button
            onClick={handleZoomOut}
            className="mobile-touch-target p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
            disabled={zoom <= 0.5}
          >
            <ZoomOut className="h-4 w-4" />
          </button>
          
          <span className="text-sm text-gray-600 min-w-[3rem] text-center">
            {Math.round(zoom * 100)}%
          </span>
          
          <button
            onClick={handleZoomIn}
            className="mobile-touch-target p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
            disabled={zoom >= 3}
          >
            <ZoomIn className="h-4 w-4" />
          </button>
          
          <button
            onClick={handleReset}
            className="mobile-touch-target p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
          >
            <RotateCcw className="h-4 w-4" />
          </button>
          
          <button
            onClick={handleFullscreen}
            className="mobile-touch-target p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
          >
            {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
          </button>
          
          {onDownload && (
            <button
              onClick={onDownload}
              className="mobile-touch-target p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
            >
              <Download className="h-4 w-4" />
            </button>
          )}
          
          {onShare && (
            <button
              onClick={onShare}
              className="mobile-touch-target p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
            >
              <Share2 className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>

      {/* チャートコンテンツ */}
      <div 
        ref={chartRef}
        className="mobile-chart-content relative overflow-hidden"
        style={{ height: `${height}px` }}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        <canvas
          ref={canvasRef}
          className="w-full h-full touch-none"
          style={{ 
            transform: `scale(${zoom}) translate(${panX / zoom}px, ${panY / zoom}px)`,
            transformOrigin: "center center"
          }}
        />
        
        {/* タッチ操作のヒント */}
        <div className="absolute bottom-2 right-2 text-xs text-gray-500 bg-white/80 px-2 py-1 rounded">
          <div className="flex items-center space-x-1">
            <Move className="h-3 w-3" />
            <span>ドラッグで移動</span>
          </div>
        </div>
      </div>

      {/* フルスクリーンモード */}
      {isFullscreen && (
        <div className="fixed inset-0 z-50 bg-white">
          <div className="h-full flex flex-col">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-semibold">{title}</h3>
              <button
                onClick={handleFullscreen}
                className="mobile-touch-target p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
              >
                <Minimize2 className="h-5 w-5" />
              </button>
            </div>
            
            <div className="flex-1 relative">
              <canvas
                ref={canvasRef}
                className="w-full h-full touch-none"
                style={{ 
                  transform: `scale(${zoom}) translate(${panX / zoom}px, ${panY / zoom}px)`,
                  transformOrigin: "center center"
                }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
