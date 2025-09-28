/**
 * 散布図チャートコンポーネント
 * 実測値 vs 予測値の散布図
 */

import React, { useMemo } from 'react';
import {
  ScatterChart as RechartsScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { chartLogger } from '@/lib/logger';

interface ScatterChartProps {
  data: Array<{
    x: number;
    y: number;
    [key: string]: any;
  }>;
  xLabel: string;
  yLabel: string;
  title?: string;
  height?: number;
}

export default function ScatterChart({
  data,
  xLabel,
  yLabel,
  title,
  height = 300
}: ScatterChartProps) {
  
  // 散布図用データの生成
  const chartData = useMemo(() => {
    if (!data || data.length === 0) {
      chartLogger.warn('散布図データが空です');
      return [];
    }

    try {
      const normalizedData = data.map(item => ({
        ...item,
        x: Number(item.x),
        y: Number(item.y)
      })).filter(item => 
        !isNaN(item.x) && !isNaN(item.y) && 
        isFinite(item.x) && isFinite(item.y)
      );

      chartLogger.info('散布図データの正規化完了', {
        originalCount: data.length,
        normalizedCount: normalizedData.length,
        invalidPoints: data.length - normalizedData.length
      });

      return normalizedData;
    } catch (error) {
      chartLogger.error('散布図データの正規化に失敗:', error);
      return [];
    }
  }, [data]);

  // カスタムツールチップ
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium text-gray-900 mb-2">
            データポイント
          </p>
          <p className="text-sm text-blue-600">
            {xLabel}: {data.x.toFixed(2)}
          </p>
          <p className="text-sm text-green-600">
            {yLabel}: {data.y.toFixed(2)}
          </p>
          {data.error && (
            <p className="text-sm text-red-600">
              誤差: {data.error.toFixed(2)}
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  // 理想線（y=x）のデータを生成
  const idealLineData = useMemo(() => {
    if (chartData.length === 0) return [];
    
    const min = Math.min(...chartData.map(d => Math.min(d.x, d.y)));
    const max = Math.max(...chartData.map(d => Math.max(d.x, d.y)));
    
    return [
      { x: min, y: min },
      { x: max, y: max }
    ];
  }, [chartData]);

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
        <h3 className="text-lg font-medium text-gray-900 mb-4">{title}</h3>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <RechartsScatterChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            type="number" 
            dataKey="x" 
            name={xLabel}
            tick={{ fontSize: 12 }}
            label={{ value: xLabel, position: 'insideBottom', offset: -5 }}
          />
          <YAxis 
            type="number" 
            dataKey="y" 
            name={yLabel}
            tick={{ fontSize: 12 }}
            label={{ value: yLabel, angle: -90, position: 'insideLeft' }}
          />
          <Tooltip content={<CustomTooltip />} />
          
          {/* 理想線（y=x） */}
          <Scatter
            data={idealLineData}
            fill="#ff6b6b"
            line={{ stroke: '#ff6b6b', strokeWidth: 2, strokeDasharray: '5 5' }}
            name="理想線 (y=x)"
          />
          
          {/* 実際のデータポイント */}
          <Scatter
            data={chartData}
            fill="#3b82f6"
            name="予測 vs 実際"
          />
        </RechartsScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
