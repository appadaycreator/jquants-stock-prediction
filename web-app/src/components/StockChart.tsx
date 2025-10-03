'use client';

import React, { useState, useEffect, useRef } from 'react';
import { X, TrendingUp, Calendar, BarChart3 } from 'lucide-react';

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
  isOpen = true,
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
    if (data.length === 0) return;

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
    setChartData(filteredData);

    // 移動平均線の計算
    const closes = filteredData.map(d => d.close);
    setMovingAverages({
      short: calculateMovingAverage(closes, 5),
      medium: calculateMovingAverage(closes, 25),
      long: calculateMovingAverage(closes, 50)
    });

  }, [data, selectedPeriod]);

  // チャートの描画（簡易版）
  const renderChart = () => {
    if (chartData.length === 0) return null;

    const maxPrice = Math.max(...chartData.map(d => d.high));
    const minPrice = Math.min(...chartData.map(d => d.low));
    const priceRange = maxPrice - minPrice;
    const chartHeight = height;
    const chartWidth = 800;

    return (
      <div className="relative">
        <svg width={chartWidth} height={chartHeight} className="w-full h-full">
          {/* ローソク足の描画 */}
          {chartData.map((candle, index) => {
            const x = (index / (chartData.length - 1)) * chartWidth;
            const bodyTop = ((maxPrice - Math.max(candle.open, candle.close)) / priceRange) * chartHeight;
            const bodyBottom = ((maxPrice - Math.min(candle.open, candle.close)) / priceRange) * chartHeight;
            const wickTop = ((maxPrice - candle.high) / priceRange) * chartHeight;
            const wickBottom = ((maxPrice - candle.low) / priceRange) * chartHeight;
            const isGreen = candle.close > candle.open;

            return (
              <g key={index}>
                {/* ヒゲ */}
                <line
                  x1={x}
                  y1={wickTop}
                  x2={x}
                  y2={wickBottom}
                  stroke={isGreen ? '#10b981' : '#ef4444'}
                  strokeWidth="1"
                />
                {/* 実体 */}
                <rect
                  x={x - 2}
                  y={bodyTop}
                  width="4"
                  height={Math.max(1, bodyBottom - bodyTop)}
                  fill={isGreen ? '#10b981' : '#ef4444'}
                />
              </g>
            );
          })}

          {/* 移動平均線 */}
          {movingAverages.short.map((ma, index) => {
            if (isNaN(ma)) return null;
            const x = (index / (chartData.length - 1)) * chartWidth;
            const y = ((maxPrice - ma) / priceRange) * chartHeight;
            return (
              <circle
                key={`short-${index}`}
                cx={x}
                cy={y}
                r="1"
                fill="#3b82f6"
              />
            );
          })}

          {movingAverages.medium.map((ma, index) => {
            if (isNaN(ma)) return null;
            const x = (index / (chartData.length - 1)) * chartWidth;
            const y = ((maxPrice - ma) / priceRange) * chartHeight;
            return (
              <circle
                key={`medium-${index}`}
                cx={x}
                cy={y}
                r="1"
                fill="#f59e0b"
              />
            );
          })}

          {movingAverages.long.map((ma, index) => {
            if (isNaN(ma)) return null;
            const x = (index / (chartData.length - 1)) * chartWidth;
            const y = ((maxPrice - ma) / priceRange) * chartHeight;
            return (
              <circle
                key={`long-${index}`}
                cx={x}
                cy={y}
                r="1"
                fill="#8b5cf6"
              />
            );
          })}
        </svg>

        {/* ツールチップ */}
        {hoveredData && (
          <div className="absolute top-4 left-4 bg-white border border-gray-200 rounded-lg p-3 shadow-lg">
            <div className="text-sm font-medium text-gray-900">
              {new Date(hoveredData.time).toLocaleDateString('ja-JP')}
            </div>
            <div className="text-xs text-gray-600 space-y-1">
              <div>始値: ¥{hoveredData.open.toLocaleString()}</div>
              <div>高値: ¥{hoveredData.high.toLocaleString()}</div>
              <div>安値: ¥{hoveredData.low.toLocaleString()}</div>
              <div>終値: ¥{hoveredData.close.toLocaleString()}</div>
              <div>出来高: {hoveredData.volume.toLocaleString()}</div>
            </div>
          </div>
        )}
      </div>
    );
  };

  // モーダル形式の場合のみisOpenをチェック
  if (isOpen === false) return null;

  // モーダル形式のレンダリング
  if (isOpen === true) {
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

  // ページ内表示用のレンダリング
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

      {/* チャートエリア */}
      <div className="relative">
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
          <div>
            {renderChart()}
            {hoveredData && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-white rounded-lg p-4 text-center">
                    <div className="text-lg font-bold text-gray-900">
                      ¥{chartData[chartData.length - 1]?.close.toLocaleString() || '--'}
                    </div>
                    <div className="text-sm text-gray-600">現在価格</div>
                  </div>
                  <div className="bg-white rounded-lg p-4 text-center">
                    <div className="text-lg font-bold text-gray-900">
                      {chartData.length}日
                    </div>
                    <div className="text-sm text-gray-600">データ期間</div>
                  </div>
                  <div className="bg-white rounded-lg p-4 text-center">
                    <div className="text-lg font-bold text-gray-900">
                      ¥{Math.max(...chartData.map(d => d.high)).toLocaleString()}
                    </div>
                    <div className="text-sm text-gray-600">期間最高値</div>
                  </div>
                  <div className="bg-white rounded-lg p-4 text-center">
                    <div className="text-lg font-bold text-gray-900">
                      ¥{Math.min(...chartData.map(d => d.low)).toLocaleString()}
                    </div>
                    <div className="text-sm text-gray-600">期間最安値</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default StockChart;
