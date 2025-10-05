"use client";

import React, { useState, useMemo, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  Area,
  AreaChart,
  ReferenceLine,
  Legend
} from "recharts";
import { 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  Activity,
  Calendar,
  Target,
  Zap
} from "lucide-react";

// データ型定義
interface ProfitLossData {
  date: string;
  total_value: number;
  daily_pnl: number;
  cumulative_pnl: number;
  benchmark_return?: number;
  volume?: number;
  volatility?: number;
}

interface ProfitLossChartProps {
  data: ProfitLossData[];
  height?: number;
  showBenchmark?: boolean;
  showVolume?: boolean;
  showVolatility?: boolean;
  onDataPointClick?: (data: ProfitLossData) => void;
  className?: string;
}

export function ProfitLossChart({
  data,
  height = 400,
  showBenchmark = false,
  showVolume = false,
  showVolatility = false,
  onDataPointClick,
  className = ""
}: ProfitLossChartProps) {
  const [chartType, setChartType] = useState<'line' | 'area' | 'bar'>('line');
  const [timeframe, setTimeframe] = useState<'1d' | '1w' | '1m' | '3m' | '1y' | 'all'>('1m');
  const [showGrid, setShowGrid] = useState(true);

  // データの処理とフィルタリング
  const processedData = useMemo(() => {
    if (!data || data.length === 0) return [];

    // 期間フィルタリング
    const now = new Date();
    const filteredData = data.filter(item => {
      const itemDate = new Date(item.date);
      const daysDiff = (now.getTime() - itemDate.getTime()) / (1000 * 60 * 60 * 24);
      
      switch (timeframe) {
        case '1d': return daysDiff <= 1;
        case '1w': return daysDiff <= 7;
        case '1m': return daysDiff <= 30;
        case '3m': return daysDiff <= 90;
        case '1y': return daysDiff <= 365;
        default: return true;
      }
    });

    // データポイントの最適化（表示用）
    const maxPoints = 100;
    if (filteredData.length > maxPoints) {
      const step = Math.ceil(filteredData.length / maxPoints);
      return filteredData.filter((_, index) => index % step === 0);
    }

    return filteredData.map((item, index) => ({
      ...item,
      date: new Date(item.date).toLocaleDateString('ja-JP', { 
        month: 'short', 
        day: 'numeric' 
      }),
      index: index + 1,
      formattedDate: new Date(item.date).toLocaleDateString('ja-JP')
    }));
  }, [data, timeframe]);

  // パフォーマンス統計の計算
  const performanceStats = useMemo(() => {
    if (processedData.length === 0) return null;

    const firstValue = processedData[0].total_value;
    const lastValue = processedData[processedData.length - 1].total_value;
    const totalReturn = ((lastValue - firstValue) / firstValue) * 100;
    
    const dailyReturns = processedData.slice(1).map((item, index) => {
      const prevValue = processedData[index].total_value;
      return ((item.total_value - prevValue) / prevValue) * 100;
    });

    const avgDailyReturn = dailyReturns.reduce((sum, ret) => sum + ret, 0) / dailyReturns.length;
    const volatility = Math.sqrt(
      dailyReturns.reduce((sum, ret) => sum + Math.pow(ret - avgDailyReturn, 2), 0) / dailyReturns.length
    );

    const maxValue = Math.max(...processedData.map(d => d.total_value));
    const maxDrawdown = Math.min(...processedData.map(d => d.total_value - maxValue));

    return {
      totalReturn,
      avgDailyReturn,
      volatility,
      maxDrawdown,
      sharpeRatio: volatility > 0 ? avgDailyReturn / volatility : 0
    };
  }, [processedData]);

  // カスタムツールチップ
  const CustomTooltip = useCallback(({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-gray-900">{data.formattedDate}</p>
          <div className="space-y-1 mt-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">総資産価値:</span>
              <span className="font-medium">¥{data.total_value.toLocaleString()}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">日次損益:</span>
              <span className={`font-medium ${data.daily_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {data.daily_pnl >= 0 ? '+' : ''}¥{data.daily_pnl.toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">累積損益:</span>
              <span className={`font-medium ${data.cumulative_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {data.cumulative_pnl >= 0 ? '+' : ''}¥{data.cumulative_pnl.toLocaleString()}
              </span>
            </div>
            {showBenchmark && data.benchmark_return !== undefined && (
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">ベンチマーク:</span>
                <span className="font-medium">
                  {data.benchmark_return >= 0 ? '+' : ''}{data.benchmark_return.toFixed(2)}%
                </span>
              </div>
            )}
          </div>
        </div>
      );
    }
    return null;
  }, [showBenchmark]);

  // チャートの描画
  const renderChart = () => {
    const commonProps = {
      data: processedData,
      margin: { top: 20, right: 30, left: 20, bottom: 5 }
    };

    switch (chartType) {
      case 'area':
        return (
          <AreaChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" opacity={showGrid ? 0.3 : 0} />
            <XAxis 
              dataKey="date" 
              tick={{ fontSize: 12 }}
              tickLine={{ stroke: '#e5e7eb' }}
            />
            <YAxis 
              tick={{ fontSize: 12 }}
              tickLine={{ stroke: '#e5e7eb' }}
              tickFormatter={(value) => `¥${(value / 1000000).toFixed(1)}M`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="total_value"
              stroke="#3b82f6"
              fill="url(#colorGradient)"
              strokeWidth={2}
            />
            <defs>
              <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
              </linearGradient>
            </defs>
          </AreaChart>
        );

      case 'bar':
        return (
          <BarChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" opacity={showGrid ? 0.3 : 0} />
            <XAxis 
              dataKey="date" 
              tick={{ fontSize: 12 }}
              tickLine={{ stroke: '#e5e7eb' }}
            />
            <YAxis 
              tick={{ fontSize: 12 }}
              tickLine={{ stroke: '#e5e7eb' }}
              tickFormatter={(value) => `¥${(value / 1000000).toFixed(1)}M`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar 
              dataKey="daily_pnl" 
              fill="#10b981"
              radius={[2, 2, 0, 0]}
            />
            <ReferenceLine y={0} stroke="#6b7280" strokeDasharray="2 2" />
          </BarChart>
        );

      default:
        return (
          <LineChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" opacity={showGrid ? 0.3 : 0} />
            <XAxis 
              dataKey="date" 
              tick={{ fontSize: 12 }}
              tickLine={{ stroke: '#e5e7eb' }}
            />
            <YAxis 
              tick={{ fontSize: 12 }}
              tickLine={{ stroke: '#e5e7eb' }}
              tickFormatter={(value) => `¥${(value / 1000000).toFixed(1)}M`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Line 
              type="monotone" 
              dataKey="total_value" 
              stroke="#3b82f6" 
              strokeWidth={3}
              dot={false}
              activeDot={{ r: 6, stroke: '#3b82f6', strokeWidth: 2 }}
            />
            <Line 
              type="monotone" 
              dataKey="cumulative_pnl" 
              stroke="#10b981" 
              strokeWidth={2}
              dot={false}
              strokeDasharray="5 5"
            />
            {showBenchmark && (
              <Line 
                type="monotone" 
                dataKey="benchmark_return" 
                stroke="#f59e0b" 
                strokeWidth={2}
                dot={false}
                strokeDasharray="3 3"
              />
            )}
            <ReferenceLine y={0} stroke="#6b7280" strokeDasharray="2 2" />
          </LineChart>
        );
    }
  };

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle className="flex items-center">
            <Activity className="h-5 w-5 mr-2" />
            損益推移グラフ
          </CardTitle>
          <div className="flex space-x-2">
            <Button
              variant={chartType === 'line' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setChartType('line')}
            >
              <TrendingUp className="h-4 w-4 mr-1" />
              ライン
            </Button>
            <Button
              variant={chartType === 'area' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setChartType('area')}
            >
              <Target className="h-4 w-4 mr-1" />
              エリア
            </Button>
            <Button
              variant={chartType === 'bar' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setChartType('bar')}
            >
              <BarChart3 className="h-4 w-4 mr-1" />
              バー
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* 期間選択 */}
        <div className="flex justify-between items-center mb-4">
          <div className="flex space-x-2">
            {(['1d', '1w', '1m', '3m', '1y', 'all'] as const).map((period) => (
              <Button
                key={period}
                variant={timeframe === period ? 'default' : 'outline'}
                size="sm"
                onClick={() => setTimeframe(period)}
              >
                {period === '1d' ? '1日' :
                 period === '1w' ? '1週' :
                 period === '1m' ? '1月' :
                 period === '3m' ? '3月' :
                 period === '1y' ? '1年' : '全期間'}
              </Button>
            ))}
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant={showGrid ? 'default' : 'outline'}
              size="sm"
              onClick={() => setShowGrid(!showGrid)}
            >
              <Calendar className="h-4 w-4 mr-1" />
              グリッド
            </Button>
          </div>
        </div>

        {/* パフォーマンス統計 */}
        {performanceStats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 p-4 bg-gray-50 rounded-lg">
            <div className="text-center">
              <div className="text-sm text-gray-600">総リターン</div>
              <div className={`text-lg font-bold ${
                performanceStats.totalReturn >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {performanceStats.totalReturn >= 0 ? '+' : ''}{performanceStats.totalReturn.toFixed(2)}%
              </div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-600">平均日次リターン</div>
              <div className={`text-lg font-bold ${
                performanceStats.avgDailyReturn >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {performanceStats.avgDailyReturn >= 0 ? '+' : ''}{performanceStats.avgDailyReturn.toFixed(3)}%
              </div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-600">ボラティリティ</div>
              <div className="text-lg font-bold text-gray-700">
                {performanceStats.volatility.toFixed(2)}%
              </div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-600">シャープレシオ</div>
              <div className="text-lg font-bold text-gray-700">
                {performanceStats.sharpeRatio.toFixed(2)}
              </div>
            </div>
          </div>
        )}

        {/* チャート */}
        <div style={{ height: `${height}px` }}>
          <ResponsiveContainer width="100%" height="100%">
            {renderChart()}
          </ResponsiveContainer>
        </div>

        {/* 凡例 */}
        <div className="flex justify-center space-x-6 mt-4 text-sm text-gray-600">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
            総資産価値
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
            累積損益
          </div>
          {showBenchmark && (
            <div className="flex items-center">
              <div className="w-3 h-3 bg-yellow-500 rounded-full mr-2"></div>
              ベンチマーク
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default ProfitLossChart;
