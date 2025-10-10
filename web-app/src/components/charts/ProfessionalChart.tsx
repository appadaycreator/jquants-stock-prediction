"use client";

import React, { useRef, useEffect, useState, useCallback, useMemo } from "react";
import { 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  Settings, 
  Download, 
  Maximize2,
  RotateCcw,
  ZoomIn,
  ZoomOut,
  Move,
  Activity,
  Target,
  AlertCircle,
} from "lucide-react";
import EnhancedTooltip from "../EnhancedTooltip";

interface CandleData {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface TechnicalIndicator {
  name: string;
  type: "sma" | "ema" | "rsi" | "macd" | "bollinger";
  period: number;
  color: string;
  visible: boolean;
}

interface ProfessionalChartProps {
  data: CandleData[];
  symbol: string;
  height?: number;
  width?: number;
  showVolume?: boolean;
  showIndicators?: boolean;
  theme?: "light" | "dark";
  onDataPointClick?: (data: CandleData) => void;
  onIndicatorToggle?: (indicator: TechnicalIndicator) => void;
  className?: string;
}

export const ProfessionalChart: React.FC<ProfessionalChartProps> = ({
  data,
  symbol,
  height = 600,
  width,
  showVolume = true,
  showIndicators = true,
  theme = "light",
  onDataPointClick,
  onIndicatorToggle,
  className = "",
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const [hoveredData, setHoveredData] = useState<CandleData | null>(null);
  const [zoom, setZoom] = useState(1);
  const [panX, setPanX] = useState(0);
  const [panY, setPanY] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [lastMousePos, setLastMousePos] = useState({ x: 0, y: 0 });
  const [showSettings, setShowSettings] = useState(false);
  const [selectedIndicators, setSelectedIndicators] = useState<TechnicalIndicator[]>([
    { name: "SMA 20", type: "sma", period: 20, color: "#3b82f6", visible: true },
    { name: "SMA 50", type: "sma", period: 50, color: "#f59e0b", visible: true },
    { name: "RSI", type: "rsi", period: 14, color: "#8b5cf6", visible: false },
    { name: "MACD", type: "macd", period: 12, color: "#10b981", visible: false },
  ]);

  // レスポンシブサイズ計算
  const calculateDimensions = useCallback(() => {
    if (containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      setDimensions({
        width: width || rect.width,
        height: height,
      });
    }
  }, [width, height]);

  // ウィンドウリサイズ対応
  useEffect(() => {
    calculateDimensions();
    window.addEventListener("resize", calculateDimensions);
    return () => window.removeEventListener("resize", calculateDimensions);
  }, [calculateDimensions]);

  // テクニカル指標の計算
  const calculateSMA = useCallback((data: CandleData[], period: number): number[] => {
    const result: number[] = [];
    for (let i = 0; i < data.length; i++) {
      if (i < period - 1) {
        result.push(NaN);
      } else {
        const sum = data.slice(i - period + 1, i + 1).reduce((acc, candle) => acc + candle.close, 0);
        result.push(sum / period);
      }
    }
    return result;
  }, []);

  const calculateRSI = useCallback((data: CandleData[], period: number): number[] => {
    const result: number[] = [];
    const gains: number[] = [];
    const losses: number[] = [];

    for (let i = 1; i < data.length; i++) {
      const change = data[i].close - data[i - 1].close;
      gains.push(change > 0 ? change : 0);
      losses.push(change < 0 ? Math.abs(change) : 0);
    }

    for (let i = 0; i < data.length; i++) {
      if (i < period) {
        result.push(NaN);
      } else {
        const avgGain = gains.slice(i - period, i).reduce((a, b) => a + b, 0) / period;
        const avgLoss = losses.slice(i - period, i).reduce((a, b) => a + b, 0) / period;
        const rs = avgGain / (avgLoss || 0.0001);
        const rsi = 100 - (100 / (1 + rs));
        result.push(rsi);
      }
    }
    return result;
  }, []);

  // 計算された指標データ
  const calculatedIndicators = useMemo(() => {
    const indicators: { [key: string]: number[] } = {};
    
    selectedIndicators.forEach(indicator => {
      if (indicator.visible) {
        switch (indicator.type) {
          case "sma":
            indicators[indicator.name] = calculateSMA(data, indicator.period);
            break;
          case "rsi":
            indicators[indicator.name] = calculateRSI(data, indicator.period);
            break;
        }
      }
    });
    
    return indicators;
  }, [data, selectedIndicators, calculateSMA, calculateRSI]);

  // プロフェッショナルなチャート描画
  const drawChart = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || !data.length) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const { width: canvasWidth, height: canvasHeight } = dimensions;
    const dpr = window.devicePixelRatio || 1;
    
    canvas.width = canvasWidth * dpr;
    canvas.height = canvasHeight * dpr;
    ctx.scale(dpr, dpr);

    // 背景の描画
    const gradient = ctx.createLinearGradient(0, 0, 0, canvasHeight);
    if (theme === "dark") {
      gradient.addColorStop(0, "#1e293b");
      gradient.addColorStop(1, "#0f172a");
    } else {
      gradient.addColorStop(0, "#f8fafc");
      gradient.addColorStop(1, "#f1f5f9");
    }
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvasWidth, canvasHeight);

    // グリッドの描画
    ctx.strokeStyle = theme === "dark" ? "#334155" : "#e2e8f0";
    ctx.lineWidth = 1;
    ctx.setLineDash([2, 4]);
    
    // 水平グリッド
    for (let i = 0; i <= 10; i++) {
      const y = (canvasHeight / 10) * i;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvasWidth, y);
      ctx.stroke();
    }
    
    // 垂直グリッド
    for (let i = 0; i <= 20; i++) {
      const x = (canvasWidth / 20) * i;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, canvasHeight);
      ctx.stroke();
    }
    
    ctx.setLineDash([]);

    // データの範囲計算
    const visibleData = data.slice(Math.max(0, Math.floor(-panX / 10)), Math.min(data.length, Math.floor((canvasWidth - panX) / 10)));
    if (visibleData.length === 0) return;

    const prices = visibleData.map(d => [d.high, d.low]).flat();
    const maxPrice = Math.max(...prices);
    const minPrice = Math.min(...prices);
    const priceRange = maxPrice - minPrice;
    const padding = 40;

    // ローソク足の描画
    visibleData.forEach((candle, index) => {
      const x = padding + (index * (canvasWidth - padding * 2) / visibleData.length) + panX;
      const isGreen = candle.close > candle.open;
      
      // ヒゲ
      ctx.strokeStyle = isGreen ? "#10b981" : "#ef4444";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(x, padding + ((maxPrice - candle.high) / priceRange) * (canvasHeight - padding * 2));
      ctx.lineTo(x, padding + ((maxPrice - candle.low) / priceRange) * (canvasHeight - padding * 2));
      ctx.stroke();

      // 実体
      const bodyTop = padding + ((maxPrice - Math.max(candle.open, candle.close)) / priceRange) * (canvasHeight - padding * 2);
      const bodyBottom = padding + ((maxPrice - Math.min(candle.open, candle.close)) / priceRange) * (canvasHeight - padding * 2);
      const bodyHeight = Math.max(1, bodyBottom - bodyTop);
      const bodyWidth = Math.max(4, (canvasWidth - padding * 2) / visibleData.length * 0.6);

      // グラデーション効果
      const bodyGradient = ctx.createLinearGradient(0, bodyTop, 0, bodyBottom);
      if (isGreen) {
        bodyGradient.addColorStop(0, "#10b981");
        bodyGradient.addColorStop(1, "#059669");
      } else {
        bodyGradient.addColorStop(0, "#ef4444");
        bodyGradient.addColorStop(1, "#dc2626");
      }

      ctx.fillStyle = bodyGradient;
      ctx.fillRect(x - bodyWidth/2, bodyTop, bodyWidth, bodyHeight);

      // 境界線
      ctx.strokeStyle = isGreen ? "#059669" : "#dc2626";
      ctx.lineWidth = 1;
      ctx.strokeRect(x - bodyWidth/2, bodyTop, bodyWidth, bodyHeight);
    });

    // テクニカル指標の描画
    selectedIndicators.forEach(indicator => {
      if (!indicator.visible || !calculatedIndicators[indicator.name]) return;

      const indicatorData = calculatedIndicators[indicator.name];
      ctx.strokeStyle = indicator.color;
      ctx.lineWidth = 2;
      ctx.setLineDash(indicator.type === "sma" ? [] : [5, 5]);
      ctx.beginPath();

      let firstPoint = true;
      indicatorData.forEach((value, index) => {
        if (isNaN(value)) return;
        
        const x = padding + (index * (canvasWidth - padding * 2) / data.length) + panX;
        const y = padding + ((maxPrice - value) / priceRange) * (canvasHeight - padding * 2);
        
        if (firstPoint) {
          ctx.moveTo(x, y);
          firstPoint = false;
        } else {
          ctx.lineTo(x, y);
        }
      });
      
      ctx.stroke();
    });

    ctx.setLineDash([]);

    // 出来高の描画
    if (showVolume) {
      const maxVolume = Math.max(...visibleData.map(d => d.volume));
      const volumeHeight = canvasHeight * 0.2;
      
      visibleData.forEach((candle, index) => {
        const x = padding + (index * (canvasWidth - padding * 2) / visibleData.length) + panX;
        const barHeight = (candle.volume / maxVolume) * volumeHeight;
        const barWidth = (canvasWidth - padding * 2) / visibleData.length * 0.8;
        
        const volumeGradient = ctx.createLinearGradient(0, canvasHeight - barHeight, 0, canvasHeight);
        volumeGradient.addColorStop(0, "#3b82f6");
        volumeGradient.addColorStop(1, "#1d4ed8");
        
        ctx.fillStyle = volumeGradient;
        ctx.fillRect(x - barWidth/2, canvasHeight - barHeight, barWidth, barHeight);
      });
    }

    // ホバー効果
    if (hoveredData) {
      const index = data.indexOf(hoveredData);
      const x = padding + (index * (canvasWidth - padding * 2) / data.length) + panX;
      
      // クロスヘア
      ctx.strokeStyle = "#6b7280";
      ctx.lineWidth = 1;
      ctx.setLineDash([5, 5]);
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, canvasHeight);
      ctx.stroke();
      ctx.setLineDash([]);
    }

  }, [data, dimensions, theme, panX, panY, zoom, hoveredData, selectedIndicators, calculatedIndicators, showVolume]);

  // マウスイベントハンドラー
  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current) return;

    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (isDragging) {
      const deltaX = x - lastMousePos.x;
      const deltaY = y - lastMousePos.y;
      setPanX(prev => Math.max(-1000, Math.min(1000, prev + deltaX)));
      setPanY(prev => Math.max(-1000, Math.min(1000, prev + deltaY)));
    }

    setLastMousePos({ x, y });

    // ホバーしたデータポイントの検出
    const padding = 40;
    const dataIndex = Math.floor(((x - padding) / (dimensions.width - padding * 2)) * data.length);
    if (dataIndex >= 0 && dataIndex < data.length) {
      setHoveredData(data[dataIndex]);
    }
  }, [isDragging, lastMousePos, dimensions.width, data]);

  const handleMouseDown = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    setIsDragging(true);
    setLastMousePos({ x: e.clientX, y: e.clientY });
  }, []);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleWheel = useCallback((e: React.WheelEvent<HTMLCanvasElement>) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    setZoom(prev => Math.max(0.5, Math.min(3, prev * delta)));
  }, []);

  // チャートの再描画
  useEffect(() => {
    drawChart();
  }, [drawChart]);

  return (
    <div ref={containerRef} className={`professional-chart-container ${className}`}>
      {/* チャートヘッダー */}
      <div className="flex items-center justify-between p-4 bg-white/80 backdrop-blur-sm border-b">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <BarChart3 className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">{symbol}</h3>
          </div>
          <div className="flex items-center space-x-4 text-sm text-gray-600">
            <div className="flex items-center space-x-1">
              <TrendingUp className="w-4 h-4 text-green-500" />
              <span>高値: ¥{Math.max(...data.map(d => d.high)).toLocaleString()}</span>
            </div>
            <div className="flex items-center space-x-1">
              <TrendingDown className="w-4 h-4 text-red-500" />
              <span>安値: ¥{Math.min(...data.map(d => d.low)).toLocaleString()}</span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setZoom(1)}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
            title="リセット"
            aria-label="ズームとパンをリセット"
            data-help="ズーム倍率とスクロール位置を初期状態に戻します。"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
          <button
            onClick={() => setZoom(prev => Math.min(3, prev * 1.2))}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
            title="ズームイン"
            aria-label="ズームイン"
            data-help="チャートを拡大します。ホイールでも操作できます。"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={() => setZoom(prev => Math.max(0.5, prev * 0.8))}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
            title="ズームアウト"
            aria-label="ズームアウト"
            data-help="チャートを縮小します。ホイールでも操作できます。"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
            title="設定"
            aria-label="チャート設定"
            data-help="表示する指標などのチャート設定を変更します。"
          >
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* チャートエリア */}
      <div className="relative">
        <canvas
          ref={canvasRef}
          width={dimensions.width}
          height={dimensions.height}
          onMouseMove={handleMouseMove}
          onMouseDown={handleMouseDown}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          onWheel={handleWheel}
          className="cursor-crosshair"
          style={{ 
            transform: `scale(${zoom})`,
            transformOrigin: "top left",
          }}
        />

        {/* ホバーツールチップ */}
        {hoveredData && (
          <div className="absolute top-4 left-4 bg-white/95 backdrop-blur-sm rounded-xl shadow-2xl p-4 border border-gray-200 max-w-xs">
            <div className="flex items-center space-x-2 mb-3">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <div className="text-sm font-semibold text-gray-900">
                {new Date(hoveredData.time).toLocaleDateString("ja-JP", {
                  year: "numeric",
                  month: "short",
                  day: "numeric",
                  weekday: "short",
                })}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-green-50 rounded-lg p-2">
                <div className="text-xs text-green-600 font-medium">始値</div>
                <EnhancedTooltip
                  content="その日の最初の取引価格です。前日の終値から大きく乖離することがあり、市場の期待やニュースの影響を反映します。例：前日終値3,000円から始値3,100円で始まった場合、+100円の高値スタートとなります。"
                  type="info"
                >
                  <div className="text-sm font-bold text-green-800 cursor-help">¥{hoveredData.open.toLocaleString()}</div>
                </EnhancedTooltip>
              </div>
              <div className="bg-red-50 rounded-lg p-2">
                <div className="text-xs text-red-600 font-medium">終値</div>
                <EnhancedTooltip
                  content="その日の最後の取引価格です。翌日の始値の基準となる重要な価格で、投資家の最終的な評価を反映します。例：終値3,200円の場合、翌日の始値は3,200円前後から始まることが多いです。"
                  type="info"
                >
                  <div className="text-sm font-bold text-red-800 cursor-help">¥{hoveredData.close.toLocaleString()}</div>
                </EnhancedTooltip>
              </div>
              <div className="bg-blue-50 rounded-lg p-2">
                <div className="text-xs text-blue-600 font-medium">高値</div>
                <EnhancedTooltip
                  content="その日の最高取引価格です。上昇の勢いや抵抗線の位置を示し、今後の価格動向の重要な指標となります。例：高値3,500円の場合、3,500円付近が抵抗線として機能することが多いです。"
                  type="success"
                >
                  <div className="text-sm font-bold text-blue-800 cursor-help">¥{hoveredData.high.toLocaleString()}</div>
                </EnhancedTooltip>
              </div>
              <div className="bg-purple-50 rounded-lg p-2">
                <div className="text-xs text-purple-600 font-medium">安値</div>
                <EnhancedTooltip
                  content="その日の最低取引価格です。下落の勢いや支持線の位置を示し、今後の価格動向の重要な指標となります。例：安値2,800円の場合、2,800円付近が支持線として機能することが多いです。"
                  type="warning"
                >
                  <div className="text-sm font-bold text-purple-800 cursor-help">¥{hoveredData.low.toLocaleString()}</div>
                </EnhancedTooltip>
              </div>
            </div>
            <div className="mt-3 pt-3 border-t border-gray-200">
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-600">出来高</span>
                <EnhancedTooltip
                  content="その日の取引された株式の数量です。取引の活発さを示し、流動性の指標となります。例：出来高100万株の場合、その日100万株が取引されたことを示します。"
                  type="info"
                >
                  <span className="text-sm font-semibold text-gray-900 cursor-help">{hoveredData.volume.toLocaleString()}</span>
                </EnhancedTooltip>
              </div>
              <div className="flex justify-between items-center mt-1">
                <span className="text-xs text-gray-600">変動率</span>
                <EnhancedTooltip
                  content="始値から終値への価格変動率です。プラスは上昇、マイナスは下落を示します。例：始値3,000円から終値3,100円の場合、+3.33%の上昇となります。"
                  type={hoveredData.close > hoveredData.open ? "success" : "warning"}
                >
                  <span className={`text-sm font-semibold cursor-help ${hoveredData.close > hoveredData.open ? "text-green-600" : "text-red-600"}`}>
                    {((hoveredData.close - hoveredData.open) / hoveredData.open * 100).toFixed(2)}%
                  </span>
                </EnhancedTooltip>
              </div>
            </div>
          </div>
        )}

        {/* 設定パネル */}
        {showSettings && (
          <div className="absolute top-4 right-4 bg-white/95 backdrop-blur-sm rounded-xl shadow-2xl p-4 border border-gray-200 w-80">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-semibold text-gray-900">テクニカル指標</h4>
              <button
                onClick={() => setShowSettings(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>
            <div className="space-y-3">
              {selectedIndicators.map((indicator, index) => (
                <div key={indicator.name} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: indicator.color }}
                    ></div>
                    <span className="text-sm font-medium text-gray-700">{indicator.name}</span>
                  </div>
                  <button
                    onClick={() => {
                      const newIndicators = [...selectedIndicators];
                      newIndicators[index].visible = !newIndicators[index].visible;
                      setSelectedIndicators(newIndicators);
                    }}
                    className={`px-3 py-1 text-xs rounded-md transition-colors ${
                      indicator.visible 
                        ? "bg-blue-500 text-white" 
                        : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                    }`}
                  >
                    {indicator.visible ? "表示" : "非表示"}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* フッター情報 */}
      <div className="flex items-center justify-between p-4 bg-gray-50 border-t">
        <div className="flex items-center space-x-6 text-sm text-gray-600">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span>SMA 20</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <span>SMA 50</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
            <span>RSI</span>
          </div>
        </div>
        <div className="text-xs text-gray-500">
          ズーム: {Math.round(zoom * 100)}% | データ数: {data.length}
        </div>
      </div>
    </div>
  );
};

export default ProfessionalChart;
