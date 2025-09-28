/**
 * 時系列チャートコンポーネント
 * Invalid Date問題の修正とJST正規化
 */

import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { parseToJst, jstLabel, createChartDateArray } from '../lib/datetime.ts';
import { chartLogger } from '../lib/logger.ts';

interface TimeSeriesChartProps {
  data: Array<{
    date: string;
    [key: string]: any;
  }>;
  lines: Array<{
    dataKey: string;
    stroke: string;
    strokeWidth?: number;
    name: string;
  }>;
  title?: string;
  height?: number;
}

export default function TimeSeriesChart({
  data,
  lines,
  title,
  height = 300
}: TimeSeriesChartProps) {
  
  // データの正規化とチャート用データの生成
  const chartData = useMemo(() => {
    if (!data || data.length === 0) {
      chartLogger.warn('チャートデータが空です');
      return [];
    }

    try {
      // 日付を正規化してチャート用データを生成
      const normalizedData = data.map(item => {
        const normalizedDate = parseToJst(item.date);
        
        if (!normalizedDate.isValid) {
          chartLogger.error('無効な日付を検出:', item.date);
          return null;
        }

        return {
          ...item,
          date: jstLabel(normalizedDate),
          timestamp: normalizedDate.toMillis(),
          // 元の日付文字列も保持（デバッグ用）
          originalDate: item.date
        };
      }).filter(item => item !== null);

      chartLogger.info('チャートデータの正規化完了', {
        originalCount: data.length,
        normalizedCount: normalizedData.length,
        invalidDates: data.length - normalizedData.length
      });

      return normalizedData;
    } catch (error) {
      chartLogger.error('チャートデータの正規化に失敗:', error);
      return [];
    }
  }, [data]);

  // カスタムツールチップ
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium text-gray-900 mb-2">
            {label}
          </p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {typeof entry.value === 'number' ? entry.value.toFixed(2) : entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  // カスタムX軸フォーマッタ
  const formatXAxisLabel = (tickItem: string) => {
    try {
      // 既にJST形式の場合はそのまま返す
      if (/^\d{4}-\d{2}-\d{2}$/.test(tickItem)) {
        return tickItem;
      }
      
      // 日付文字列をJSTに正規化
      const dt = parseToJst(tickItem);
      if (dt.isValid) {
        return jstLabel(dt);
      }
      
      chartLogger.warn('X軸ラベルの日付が無効です:', tickItem);
      // Invalid Dateの代わりにデフォルト日付を返す
      return '2024-01-01';
    } catch (error) {
      chartLogger.error('X軸ラベルのフォーマットに失敗:', error, 'Input:', tickItem);
      // Invalid Dateの代わりにデフォルト日付を返す
      return '2024-01-01';
    }
  };

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
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey="date" 
            tickFormatter={formatXAxisLabel}
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={60}
          />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip content={<CustomTooltip />} />
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
              name={line.name}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
