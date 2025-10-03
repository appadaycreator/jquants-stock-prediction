'use client';

import React, { useRef, useEffect, useState, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  Zap, 
  Target,
  Activity,
  TrendingUp,
  TrendingDown
} from 'lucide-react';

interface ChartData {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface AnimatedChartProps {
  data: ChartData[];
  symbol: string;
  height?: number;
  width?: number;
  enableAnimation?: boolean;
  animationSpeed?: number;
  showVolume?: boolean;
  showTrendLines?: boolean;
  onDataPointClick?: (data: ChartData) => void;
  className?: string;
}

export const AnimatedChart: React.FC<AnimatedChartProps> = ({
  data,
  symbol,
  height = 600,
  width,
  enableAnimation = true,
  animationSpeed = 1000,
  showVolume = true,
  showTrendLines = true,
  onDataPointClick,
  className = ''
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const animationRef = useRef<number>();
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const [isAnimating, setIsAnimating] = useState(false);
  const [animationProgress, setAnimationProgress] = useState(0);
  const [hoveredData, setHoveredData] = useState<ChartData | null>(null);
  const [trendLines, setTrendLines] = useState<Array<{start: number, end: number, color: string}>>([]);
  const [showTrendAnalysis, setShowTrendAnalysis] = useState(false);

  // レスポンシブサイズ計算
  const calculateDimensions = useCallback(() => {
    if (containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      setDimensions({
        width: width || rect.width,
        height: height
      });
    }
  }, [width, height]);

  useEffect(() => {
    calculateDimensions();
    window.addEventListener('resize', calculateDimensions);
    return () => window.removeEventListener('resize', calculateDimensions);
  }, [calculateDimensions]);

  // トレンドラインの自動検出
  const detectTrendLines = useCallback((data: ChartData[]) => {
    const lines: Array<{start: number, end: number, color: string}> = [];
    
    // サポートライン（安値の連続）
    let supportStart = 0;
    let supportEnd = 0;
    let minPrice = data[0].low;
    
    for (let i = 1; i < data.length; i++) {
      if (data[i].low < minPrice) {
        if (supportEnd - supportStart > 5) {
          lines.push({
            start: supportStart,
            end: supportEnd,
            color: '#10b981'
          });
        }
        supportStart = i;
        supportEnd = i;
        minPrice = data[i].low;
      } else {
        supportEnd = i;
      }
    }
    
    // レジスタンスライン（高値の連続）
    let resistanceStart = 0;
    let resistanceEnd = 0;
    let maxPrice = data[0].high;
    
    for (let i = 1; i < data.length; i++) {
      if (data[i].high > maxPrice) {
        if (resistanceEnd - resistanceStart > 5) {
          lines.push({
            start: resistanceStart,
            end: resistanceEnd,
            color: '#ef4444'
          });
        }
        resistanceStart = i;
        resistanceEnd = i;
        maxPrice = data[i].high;
      } else {
        resistanceEnd = i;
      }
    }
    
    setTrendLines(lines);
  }, []);

  // アニメーション付きチャート描画
  const drawAnimatedChart = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || !data.length) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const { width: canvasWidth, height: canvasHeight } = dimensions;
    const dpr = window.devicePixelRatio || 1;
    
    canvas.width = canvasWidth * dpr;
    canvas.height = canvasHeight * dpr;
    ctx.scale(dpr, dpr);

    // 背景の描画（グラデーション）
    const gradient = ctx.createLinearGradient(0, 0, 0, canvasHeight);
    gradient.addColorStop(0, '#f8fafc');
    gradient.addColorStop(0.5, '#f1f5f9');
    gradient.addColorStop(1, '#e2e8f0');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvasWidth, canvasHeight);

    // アニメーション進捗に基づく表示データ
    const visibleDataCount = Math.floor(data.length * animationProgress);
    const visibleData = data.slice(0, visibleDataCount);

    if (visibleData.length === 0) return;

    // データの範囲計算
    const prices = visibleData.map(d => [d.high, d.low]).flat();
    const maxPrice = Math.max(...prices);
    const minPrice = Math.min(...prices);
    const priceRange = maxPrice - minPrice;
    const padding = 60;

    // グリッドの描画（アニメーション付き）
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 1;
    ctx.setLineDash([2, 4]);
    
    const gridOpacity = animationProgress;
    ctx.globalAlpha = gridOpacity;
    
    for (let i = 0; i <= 10; i++) {
      const y = padding + (canvasHeight - padding * 2) / 10 * i;
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(canvasWidth - padding, y);
      ctx.stroke();
    }
    
    ctx.setLineDash([]);
    ctx.globalAlpha = 1;

    // ローソク足の描画（アニメーション付き）
    visibleData.forEach((candle, index) => {
      const x = padding + (index * (canvasWidth - padding * 2) / visibleData.length);
      const isGreen = candle.close > candle.open;
      
      // アニメーション効果
      const candleOpacity = Math.min(1, (index / visibleData.length) * 2);
      ctx.globalAlpha = candleOpacity;
      
      // ヒゲ
      ctx.strokeStyle = isGreen ? '#10b981' : '#ef4444';
      ctx.lineWidth = 2;
      ctx.shadowColor = isGreen ? '#10b981' : '#ef4444';
      ctx.shadowBlur = 4;
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
        bodyGradient.addColorStop(0, '#10b981');
        bodyGradient.addColorStop(1, '#059669');
      } else {
        bodyGradient.addColorStop(0, '#ef4444');
        bodyGradient.addColorStop(1, '#dc2626');
      }

      ctx.fillStyle = bodyGradient;
      ctx.fillRect(x - bodyWidth/2, bodyTop, bodyWidth, bodyHeight);

      // 境界線
      ctx.strokeStyle = isGreen ? '#059669' : '#dc2626';
      ctx.lineWidth = 1;
      ctx.strokeRect(x - bodyWidth/2, bodyTop, bodyWidth, bodyHeight);
    });

    ctx.shadowBlur = 0;
    ctx.globalAlpha = 1;

    // トレンドラインの描画
    if (showTrendLines && trendLines.length > 0) {
      trendLines.forEach(line => {
        const startX = padding + (line.start * (canvasWidth - padding * 2) / data.length);
        const endX = padding + (line.end * (canvasWidth - padding * 2) / data.length);
        const startY = padding + ((maxPrice - data[line.start].low) / priceRange) * (canvasHeight - padding * 2);
        const endY = padding + ((maxPrice - data[line.end].low) / priceRange) * (canvasHeight - padding * 2);
        
        ctx.strokeStyle = line.color;
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        ctx.moveTo(startX, startY);
        ctx.lineTo(endX, endY);
        ctx.stroke();
      });
      ctx.setLineDash([]);
    }

    // 出来高の描画（アニメーション付き）
    if (showVolume) {
      const maxVolume = Math.max(...visibleData.map(d => d.volume));
      const volumeHeight = canvasHeight * 0.2;
      
      visibleData.forEach((candle, index) => {
        const x = padding + (index * (canvasWidth - padding * 2) / visibleData.length);
        const barHeight = (candle.volume / maxVolume) * volumeHeight;
        const barWidth = (canvasWidth - padding * 2) / visibleData.length * 0.8;
        
        const volumeOpacity = Math.min(1, (index / visibleData.length) * 2);
        ctx.globalAlpha = volumeOpacity * 0.7;
        
        const volumeGradient = ctx.createLinearGradient(0, canvasHeight - barHeight, 0, canvasHeight);
        volumeGradient.addColorStop(0, '#3b82f6');
        volumeGradient.addColorStop(1, '#1d4ed8');
        
        ctx.fillStyle = volumeGradient;
        ctx.fillRect(x - barWidth/2, canvasHeight - barHeight, barWidth, barHeight);
      });
      
      ctx.globalAlpha = 1;
    }

    // ホバー効果
    if (hoveredData) {
      const index = visibleData.indexOf(hoveredData);
      if (index !== -1) {
        const x = padding + (index * (canvasWidth - padding * 2) / visibleData.length);
        
        // クロスヘア
        ctx.strokeStyle = '#6b7280';
        ctx.lineWidth = 1;
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvasHeight);
        ctx.stroke();
        ctx.setLineDash([]);
      }
    }

  }, [data, dimensions, animationProgress, trendLines, showTrendLines, showVolume, hoveredData]);

  // アニメーション制御
  const startAnimation = useCallback(() => {
    if (isAnimating) return;
    
    setIsAnimating(true);
    setAnimationProgress(0);
    
    const animate = () => {
      setAnimationProgress(prev => {
        const newProgress = prev + 0.02;
        if (newProgress >= 1) {
          setIsAnimating(false);
          return 1;
        }
        animationRef.current = requestAnimationFrame(animate);
        return newProgress;
      });
    };
    
    animationRef.current = requestAnimationFrame(animate);
  }, [isAnimating]);

  const stopAnimation = useCallback(() => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
    setIsAnimating(false);
  }, []);

  const resetAnimation = useCallback(() => {
    stopAnimation();
    setAnimationProgress(0);
  }, [stopAnimation]);

  // トレンドラインの検出
  useEffect(() => {
    if (data.length > 0) {
      detectTrendLines(data);
    }
  }, [data, detectTrendLines]);

  // チャートの再描画
  useEffect(() => {
    drawAnimatedChart();
  }, [drawAnimatedChart]);

  // クリーンアップ
  useEffect(() => {
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  return (
    <div ref={containerRef} className={`animated-chart-container ${className}`}>
      {/* ヘッダー */}
      <div className="flex items-center justify-between p-4 bg-white/80 backdrop-blur-sm border-b">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <Activity className="w-5 h-5 text-blue-600" />
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
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={isAnimating ? stopAnimation : startAnimation}
            className={`p-2 rounded-md transition-colors ${
              isAnimating 
                ? 'bg-red-500 text-white hover:bg-red-600' 
                : 'bg-green-500 text-white hover:bg-green-600'
            }`}
          >
            {isAnimating ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={resetAnimation}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setShowTrendAnalysis(!showTrendAnalysis)}
            className={`p-2 rounded-md transition-colors ${
              showTrendAnalysis 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            <Target className="w-4 h-4" />
          </motion.button>
        </div>
      </div>

      {/* チャートエリア */}
      <div className="relative">
        <canvas
          ref={canvasRef}
          width={dimensions.width}
          height={dimensions.height}
          className="cursor-crosshair"
        />

        {/* アニメーション進捗バー */}
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-gray-200">
          <motion.div
            className="h-full bg-blue-500"
            initial={{ width: 0 }}
            animate={{ width: `${animationProgress * 100}%` }}
            transition={{ duration: 0.1 }}
          />
        </div>

        {/* ホバーツールチップ */}
        <AnimatePresence>
          {hoveredData && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.8, y: 10 }}
              transition={{ duration: 0.2 }}
              className="absolute top-4 left-4 bg-white/95 backdrop-blur-sm rounded-xl shadow-2xl p-4 border border-gray-200 max-w-xs"
            >
              <div className="flex items-center space-x-2 mb-3">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <div className="text-sm font-semibold text-gray-900">
                  {new Date(hoveredData.time).toLocaleDateString('ja-JP', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                    weekday: 'short'
                  })}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <motion.div 
                  className="bg-green-50 rounded-lg p-2"
                  whileHover={{ scale: 1.02 }}
                >
                  <div className="text-xs text-green-600 font-medium">始値</div>
                  <div className="text-sm font-bold text-green-800">¥{hoveredData.open.toLocaleString()}</div>
                </motion.div>
                <motion.div 
                  className="bg-red-50 rounded-lg p-2"
                  whileHover={{ scale: 1.02 }}
                >
                  <div className="text-xs text-red-600 font-medium">終値</div>
                  <div className="text-sm font-bold text-red-800">¥{hoveredData.close.toLocaleString()}</div>
                </motion.div>
                <motion.div 
                  className="bg-blue-50 rounded-lg p-2"
                  whileHover={{ scale: 1.02 }}
                >
                  <div className="text-xs text-blue-600 font-medium">高値</div>
                  <div className="text-sm font-bold text-blue-800">¥{hoveredData.high.toLocaleString()}</div>
                </motion.div>
                <motion.div 
                  className="bg-purple-50 rounded-lg p-2"
                  whileHover={{ scale: 1.02 }}
                >
                  <div className="text-xs text-purple-600 font-medium">安値</div>
                  <div className="text-sm font-bold text-purple-800">¥{hoveredData.low.toLocaleString()}</div>
                </motion.div>
              </div>
              <div className="mt-3 pt-3 border-t border-gray-200">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-600">出来高</span>
                  <span className="text-sm font-semibold text-gray-900">{hoveredData.volume.toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center mt-1">
                  <span className="text-xs text-gray-600">変動率</span>
                  <span className={`text-sm font-semibold ${hoveredData.close > hoveredData.open ? 'text-green-600' : 'text-red-600'}`}>
                    {((hoveredData.close - hoveredData.open) / hoveredData.open * 100).toFixed(2)}%
                  </span>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* トレンド分析パネル */}
        <AnimatePresence>
          {showTrendAnalysis && (
            <motion.div
              initial={{ opacity: 0, x: 300 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 300 }}
              transition={{ duration: 0.3 }}
              className="absolute top-4 right-4 bg-white/95 backdrop-blur-sm rounded-xl shadow-2xl p-4 border border-gray-200 w-80"
            >
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-lg font-semibold text-gray-900">トレンド分析</h4>
                <button
                  onClick={() => setShowTrendAnalysis(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">サポートライン</span>
                  <span className="text-sm font-semibold text-green-600">
                    {trendLines.filter(line => line.color === '#10b981').length}本
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">レジスタンスライン</span>
                  <span className="text-sm font-semibold text-red-600">
                    {trendLines.filter(line => line.color === '#ef4444').length}本
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">現在価格</span>
                  <span className="text-sm font-semibold text-gray-900">
                    ¥{data[data.length - 1]?.close.toLocaleString()}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">価格変動</span>
                  <span className={`text-sm font-semibold ${
                    data[data.length - 1]?.close > data[data.length - 2]?.close ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {data[data.length - 1]?.close > data[data.length - 2]?.close ? '上昇' : '下降'}
                  </span>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* フッター情報 */}
      <div className="flex items-center justify-between p-4 bg-gray-50 border-t">
        <div className="flex items-center space-x-6 text-sm text-gray-600">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span>サポートライン</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <span>レジスタンスライン</span>
          </div>
        </div>
        <div className="text-xs text-gray-500">
          アニメーション進捗: {Math.round(animationProgress * 100)}% | データ数: {data.length}
        </div>
      </div>
    </div>
  );
};

export default AnimatedChart;
