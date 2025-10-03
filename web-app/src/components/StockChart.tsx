'use client';

import React, { useState, useEffect, useRef } from 'react';
import { X, TrendingUp, Calendar, BarChart3 } from 'lucide-react';
import UltimateChart from './charts/UltimateChart';

interface CandleData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface StockChartProps {
  symbol: string;
  data: CandleData[];
  isOpen?: boolean;
  onClose?: () => void;
  isLoading?: boolean;
  error?: Error | null;
  timeframe?: string;
  height?: number;
}

export const StockChart: React.FC<StockChartProps> = ({
  symbol,
  data,
  isOpen,
  onClose,
  isLoading = false,
  error,
  timeframe,
  height = 400
}) => {
  const [selectedPeriod, setSelectedPeriod] = useState('1M');
  const [chartData, setChartData] = useState<CandleData[]>([]);
  const [movingAverages, setMovingAverages] = useState<{
    short: number[];
    medium: number[];
    long: number[];
  }>({ short: [], medium: [], long: [] });
  const [hoveredData, setHoveredData] = useState<CandleData | null>(null);
  const [zoom, setZoom] = useState(1);
  const [panX, setPanX] = useState(0);
  const [showVolume, setShowVolume] = useState(false);
  const [chartType, setChartType] = useState<'candlestick' | 'line'>('candlestick');
  const chartRef = useRef<HTMLDivElement>(null);

  const periods = [
    { value: '1M', label: '1ヶ月' },
    { value: '3M', label: '3ヶ月' },
    { value: '6M', label: '6ヶ月' },
    { value: '1Y', label: '1年' }
  ];

  // 移動平均線の計算
  const calculateMovingAverage = (prices: number[], period: number): number[] => {
    const result: number[] = [];
    for (let i = 0; i < prices.length; i++) {
      if (i < period - 1) {
        result.push(NaN);
      } else {
        const sum = prices.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
        result.push(sum / period);
      }
    }
    return result;
  };

  // データの処理
  useEffect(() => {
    console.log('StockChart useEffect - data length:', data.length);
    console.log('StockChart useEffect - selectedPeriod:', selectedPeriod);
    
    if (data.length === 0) {
      console.log('No data available');
      return;
    }

    // 期間に応じたデータのフィルタリング
    const now = new Date();
    const periodDays = {
      '1M': 30,
      '3M': 90,
      '6M': 180,
      '1Y': 365
    };

    const days = periodDays[selectedPeriod as keyof typeof periodDays] || 30;
    const cutoffDate = new Date(now.getTime() - days * 24 * 60 * 60 * 1000);
    
    const filteredData = data.filter(d => new Date(d.time) >= cutoffDate);
    console.log('Filtered data length:', filteredData.length);
    setChartData(filteredData);

    // 移動平均線の計算
    const closes = filteredData.map(d => d.close);
    setMovingAverages({
      short: calculateMovingAverage(closes, 5),
      medium: calculateMovingAverage(closes, 25),
      long: calculateMovingAverage(closes, 50)
    });

  }, [data, selectedPeriod]);

  // チャートの描画（改良版）
  const renderChart = () => {
    console.log('renderChart called - chartData length:', chartData.length);
    
    if (chartData.length === 0) {
      console.log('No chart data to render');
      return null;
    }

    const maxPrice = Math.max(...chartData.map(d => d.high));
    const minPrice = Math.min(...chartData.map(d => d.low));
    const priceRange = maxPrice - minPrice;
    const chartHeight = height;
    const chartWidth = Math.max(800, window.innerWidth * 0.9); // レスポンシブ幅
    
    console.log('Chart dimensions:', { chartHeight, chartWidth, maxPrice, minPrice, priceRange });

    return (
      <div className="relative bg-gradient-to-br from-slate-50 to-slate-100 rounded-lg p-4 shadow-lg overflow-hidden">
        {/* チャートコントロール */}
        <div className="absolute top-2 right-2 z-10 flex space-x-2">
          <button
            onClick={() => setChartType(chartType === 'candlestick' ? 'line' : 'candlestick')}
            className="px-3 py-1 text-xs bg-white/80 backdrop-blur-sm rounded-md shadow-sm hover:bg-white transition-colors"
          >
            {chartType === 'candlestick' ? '線グラフ' : 'ローソク足'}
          </button>
          <button
            onClick={() => setShowVolume(!showVolume)}
            className={`px-3 py-1 text-xs rounded-md shadow-sm transition-colors ${
              showVolume ? 'bg-blue-500 text-white' : 'bg-white/80 backdrop-blur-sm hover:bg-white'
            }`}
          >
            出来高
          </button>
          <button
            onClick={() => setZoom(1)}
            className="px-3 py-1 text-xs bg-white/80 backdrop-blur-sm rounded-md hover:bg-white transition-colors"
          >
            リセット
          </button>
        </div>
        
        <svg 
          width={chartWidth} 
          height={chartHeight} 
          className="w-full h-full" 
          viewBox={`0 0 ${chartWidth} ${chartHeight}`}
          style={{ transform: `scale(${zoom}) translateX(${panX}px)` }}
        >
          {/* 背景グリッド */}
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#e2e8f0" strokeWidth="0.5" opacity="0.3"/>
            </pattern>
            <linearGradient id="bullGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#10b981" stopOpacity="0.8"/>
              <stop offset="100%" stopColor="#059669" stopOpacity="0.6"/>
            </linearGradient>
            <linearGradient id="bearGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#ef4444" stopOpacity="0.8"/>
              <stop offset="100%" stopColor="#dc2626" stopOpacity="0.6"/>
            </linearGradient>
            <filter id="glow">
              <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
              <feMerge> 
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          
          {/* 背景グリッド */}
          <rect width="100%" height="100%" fill="url(#grid)"/>
          
          {/* 価格帯の背景色 */}
          <rect x="0" y="0" width={chartWidth} height={chartHeight} fill="rgba(255,255,255,0.8)"/>
          
          {/* ローソク足の描画（改良版） */}
          {chartData.map((candle, index) => {
            const x = (index / (chartData.length - 1)) * chartWidth;
            const bodyTop = ((maxPrice - Math.max(candle.open, candle.close)) / priceRange) * chartHeight;
            const bodyBottom = ((maxPrice - Math.min(candle.open, candle.close)) / priceRange) * chartHeight;
            const wickTop = ((maxPrice - candle.high) / priceRange) * chartHeight;
            const wickBottom = ((maxPrice - candle.low) / priceRange) * chartHeight;
            const isGreen = candle.close > candle.open;
            const bodyHeight = Math.max(2, bodyBottom - bodyTop);
            const candleWidth = Math.max(3, chartWidth / chartData.length * 0.6);

            return (
              <g key={index} className="candle-group">
                {/* ヒゲ（改良版） */}
                <line
                  x1={x}
                  y1={wickTop}
                  x2={x}
                  y2={wickBottom}
                  stroke={isGreen ? '#10b981' : '#ef4444'}
                  strokeWidth="2"
                  strokeLinecap="round"
                  filter="url(#glow)"
                />
                {/* 実体（改良版） */}
                <rect
                  x={x - candleWidth/2}
                  y={bodyTop}
                  width={candleWidth}
                  height={bodyHeight}
                  fill={isGreen ? 'url(#bullGradient)' : 'url(#bearGradient)'}
                  stroke={isGreen ? '#059669' : '#dc2626'}
                  strokeWidth="1"
                  rx="1"
                  ry="1"
                  filter="url(#glow)"
                />
                {/* ホバー効果用の透明な領域 */}
                <rect
                  x={x - candleWidth/2 - 5}
                  y={wickTop - 5}
                  width={candleWidth + 10}
                  height={wickBottom - wickTop + 10}
                  fill="transparent"
                  onMouseEnter={() => setHoveredData(candle)}
                  onMouseLeave={() => setHoveredData(null)}
                  style={{ cursor: 'pointer' }}
                />
              </g>
            );
          })}

          {/* 移動平均線（線として描画） */}
          {movingAverages.short.map((ma, index) => {
            if (isNaN(ma) || index === 0) return null;
            const x1 = ((index - 1) / (chartData.length - 1)) * chartWidth;
            const x2 = (index / (chartData.length - 1)) * chartWidth;
            const y1 = ((maxPrice - movingAverages.short[index - 1]) / priceRange) * chartHeight;
            const y2 = ((maxPrice - ma) / priceRange) * chartHeight;
            return (
              <line
                key={`short-line-${index}`}
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
                stroke="#3b82f6"
                strokeWidth="2"
                strokeDasharray="5,5"
                opacity="0.8"
                filter="url(#glow)"
              />
            );
          })}

          {movingAverages.medium.map((ma, index) => {
            if (isNaN(ma) || index === 0) return null;
            const x1 = ((index - 1) / (chartData.length - 1)) * chartWidth;
            const x2 = (index / (chartData.length - 1)) * chartWidth;
            const y1 = ((maxPrice - movingAverages.medium[index - 1]) / priceRange) * chartHeight;
            const y2 = ((maxPrice - ma) / priceRange) * chartHeight;
            return (
              <line
                key={`medium-line-${index}`}
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
                stroke="#f59e0b"
                strokeWidth="2"
                strokeDasharray="8,4"
                opacity="0.8"
                filter="url(#glow)"
              />
            );
          })}

          {movingAverages.long.map((ma, index) => {
            if (isNaN(ma) || index === 0) return null;
            const x1 = ((index - 1) / (chartData.length - 1)) * chartWidth;
            const x2 = (index / (chartData.length - 1)) * chartWidth;
            const y1 = ((maxPrice - movingAverages.long[index - 1]) / priceRange) * chartHeight;
            const y2 = ((maxPrice - ma) / priceRange) * chartHeight;
            return (
              <line
                key={`long-line-${index}`}
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
                stroke="#8b5cf6"
                strokeWidth="2"
                strokeDasharray="12,6"
                opacity="0.8"
                filter="url(#glow)"
              />
            );
          })}
        </svg>

        {/* 改良されたツールチップ */}
        {hoveredData && (
          <div className="absolute top-4 left-4 bg-white/95 backdrop-blur-sm border border-gray-200 rounded-xl p-4 shadow-2xl max-w-xs">
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
              <div className="bg-green-50 rounded-lg p-2">
                <div className="text-xs text-green-600 font-medium">始値</div>
                <div className="text-sm font-bold text-green-800">¥{hoveredData.open.toLocaleString()}</div>
              </div>
              <div className="bg-red-50 rounded-lg p-2">
                <div className="text-xs text-red-600 font-medium">終値</div>
                <div className="text-sm font-bold text-red-800">¥{hoveredData.close.toLocaleString()}</div>
              </div>
              <div className="bg-blue-50 rounded-lg p-2">
                <div className="text-xs text-blue-600 font-medium">高値</div>
                <div className="text-sm font-bold text-blue-800">¥{hoveredData.high.toLocaleString()}</div>
              </div>
              <div className="bg-purple-50 rounded-lg p-2">
                <div className="text-xs text-purple-600 font-medium">安値</div>
                <div className="text-sm font-bold text-purple-800">¥{hoveredData.low.toLocaleString()}</div>
              </div>
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
          </div>
        )}
      </div>
    );
  };

  // デバッグログ
  console.log('StockChart render - isOpen:', isOpen, 'typeof isOpen:', typeof isOpen);

  // モーダル形式の場合のみisOpenをチェック
  if (isOpen === false) {
    console.log('isOpen is false, returning null');
    return null;
  }

  // モーダル形式のレンダリング（isOpenが明示的にtrueの場合のみ）
  if (isOpen === true) {
    console.log('isOpen is true, rendering modal');
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full mx-4 max-h-[90vh] overflow-hidden">
          {/* ヘッダー */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <BarChart3 className="w-6 h-6 text-blue-600" />
              <h2 className="text-xl font-semibold text-gray-900">
                {symbol} チャート
              </h2>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* 期間選択 */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center space-x-4">
              <Calendar className="w-5 h-5 text-gray-500" />
              <div className="flex space-x-2">
                {periods.map((period) => (
                  <button
                    key={period.value}
                    onClick={() => setSelectedPeriod(period.value)}
                    className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                      selectedPeriod === period.value
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {period.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

        {/* チャートエリア */}
        <div className="p-6">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">チャートデータの読み込みに失敗しました</p>
                <p className="text-sm text-gray-500 mt-2">{error.message}</p>
              </div>
            </div>
          ) : chartData.length === 0 ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">チャートデータがありません</p>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {/* チャート */}
              <div className="border border-gray-200 rounded-lg p-4">
                {renderChart()}
              </div>

              {/* 凡例 */}
              <div className="flex items-center justify-center space-x-6 text-sm">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                  <span>短期移動平均 (5日)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                  <span>中期移動平均 (25日)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                  <span>長期移動平均 (50日)</span>
                </div>
              </div>

              {/* 統計情報 */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <div className="text-lg font-bold text-gray-900">
                    ¥{chartData[chartData.length - 1]?.close.toLocaleString() || '--'}
                  </div>
                  <div className="text-sm text-gray-600">現在価格</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <div className="text-lg font-bold text-gray-900">
                    {chartData.length}日
                  </div>
                  <div className="text-sm text-gray-600">データ期間</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <div className="text-lg font-bold text-gray-900">
                    ¥{Math.max(...chartData.map(d => d.high)).toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-600">期間最高値</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <div className="text-lg font-bold text-gray-900">
                    ¥{Math.min(...chartData.map(d => d.low)).toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-600">期間最安値</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
    );
  }

  // ページ内表示用のレンダリング（UltimateChartを使用）
  console.log('Rendering inline chart with UltimateChart');
  return (
    <div className="w-full">
      {/* 期間選択 */}
      <div className="mb-4">
        <div className="flex items-center space-x-4">
          <Calendar className="w-5 h-5 text-gray-500" />
          <div className="flex space-x-2">
            {periods.map((period) => (
              <button
                key={period.value}
                onClick={() => setSelectedPeriod(period.value)}
                className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                  selectedPeriod === period.value
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {period.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* UltimateChartを使用 */}
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-2 text-gray-600">読み込み中...</span>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-64 text-red-600">
            <div className="text-center">
              <div className="text-lg font-semibold mb-2">エラーが発生しました</div>
              <div className="text-sm">{error.message}</div>
            </div>
          </div>
        ) : chartData.length === 0 ? (
          <div className="flex items-center justify-center h-64 text-gray-500">
            <div className="text-center">
              <div className="text-lg font-semibold mb-2">データがありません</div>
              <div className="text-sm">チャートデータを取得できませんでした</div>
            </div>
          </div>
        ) : (
        <UltimateChart
          data={chartData.map(d => ({
            time: new Date(d.time).getTime(),
            open: d.open,
            high: d.high,
            low: d.low,
            close: d.close,
            volume: d.volume
          }))}
          symbol={symbol}
          height={height}
          enableAllModes={true}
          onDataPointClick={(data) => {
            console.log('Data point clicked:', data);
          }}
          onExport={(format) => {
            console.log('Exporting chart as:', format);
          }}
          onShare={() => {
            console.log('Sharing chart');
          }}
        />
      )}
    </div>
  );
};

export default StockChart;
