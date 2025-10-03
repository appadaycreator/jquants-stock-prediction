'use client';

import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Star, AlertTriangle, RefreshCw } from 'lucide-react';
import { LightweightChart } from '../charts/LightweightChart';

interface KPIData {
  label: string;
  value: number;
  change: number;
  changePercent: number;
  trend: 'up' | 'down' | 'neutral';
}

interface CandidateStock {
  code: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  score: number;
  reason: string;
}

interface FirstViewProps {
  kpis: KPIData[];
  candidates: CandidateStock[];
  isLoading?: boolean;
  onRefresh?: () => void;
  onStockClick?: (stock: CandidateStock) => void;
}

export function FirstView({ 
  kpis, 
  candidates, 
  isLoading = false, 
  onRefresh,
  onStockClick 
}: FirstViewProps) {
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    if (onRefresh) {
      setIsRefreshing(true);
      try {
        await onRefresh();
      } finally {
        setIsRefreshing(false);
      }
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    } else if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toLocaleString();
  };

  const formatPercent = (percent: number) => {
    const sign = percent >= 0 ? '+' : '';
    return `${sign}${percent.toFixed(2)}%`;
  };

  const getTrendIcon = (trend: 'up' | 'down' | 'neutral') => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-green-600" />;
      case 'down':
        return <TrendingDown className="w-4 h-4 text-red-600" />;
      default:
        return <div className="w-4 h-4" />;
    }
  };

  const getTrendColor = (trend: 'up' | 'down' | 'neutral') => {
    switch (trend) {
      case 'up':
        return 'text-green-600';
      case 'down':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  if (isLoading) {
    return (
      <div className="p-4 space-y-4">
        {/* KPI スケルトン */}
        <div className="grid grid-cols-2 gap-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white rounded-lg p-3 shadow-sm">
              <div className="animate-pulse">
                <div className="h-3 bg-gray-300 rounded w-16 mb-2"></div>
                <div className="h-6 bg-gray-300 rounded w-20 mb-1"></div>
                <div className="h-3 bg-gray-300 rounded w-12"></div>
              </div>
            </div>
          ))}
        </div>

        {/* 候補銘柄スケルトン */}
        <div className="bg-white rounded-lg p-4 shadow-sm">
          <div className="animate-pulse">
            <div className="h-4 bg-gray-300 rounded w-24 mb-3"></div>
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="flex items-center justify-between py-2">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-gray-300 rounded"></div>
                  <div className="space-y-1">
                    <div className="h-3 bg-gray-300 rounded w-16"></div>
                    <div className="h-3 bg-gray-300 rounded w-20"></div>
                  </div>
                </div>
                <div className="text-right space-y-1">
                  <div className="h-3 bg-gray-300 rounded w-12"></div>
                  <div className="h-3 bg-gray-300 rounded w-16"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">今日の概要</h2>
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors disabled:opacity-50"
          aria-label="更新"
        >
          <RefreshCw className={`w-5 h-5 text-gray-600 ${isRefreshing ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* KPI カード */}
      <div className="grid grid-cols-2 gap-3">
        {kpis.map((kpi, index) => (
          <div key={index} className="bg-white rounded-lg p-3 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">{kpi.label}</span>
              {getTrendIcon(kpi.trend)}
            </div>
            <div className="text-xl font-bold text-gray-900">
              {formatNumber(kpi.value)}
            </div>
            <div className={`text-sm ${getTrendColor(kpi.trend)}`}>
              {formatPercent(kpi.changePercent)}
            </div>
          </div>
        ))}
      </div>

      {/* 候補銘柄 */}
      <div className="bg-white rounded-lg shadow-sm">
        <div className="p-4 border-b">
          <h3 className="text-lg font-semibold text-gray-900">本日の候補銘柄</h3>
          <p className="text-sm text-gray-600">AI分析による推奨銘柄</p>
        </div>
        
        <div className="divide-y">
          {candidates.slice(0, 5).map((stock, index) => (
            <button
              key={stock.code}
              onClick={() => onStockClick?.(stock)}
              className="w-full p-4 text-left hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-sm font-bold text-blue-600">
                      {index + 1}
                    </span>
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{stock.name}</div>
                    <div className="text-sm text-gray-600">{stock.code}</div>
                  </div>
                </div>
                
                <div className="text-right">
                  <div className="font-bold text-gray-900">
                    ¥{stock.price.toLocaleString()}
                  </div>
                  <div className={`text-sm ${
                    stock.change >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {formatPercent(stock.changePercent)}
                  </div>
                  <div className="text-xs text-gray-500">
                    スコア: {stock.score.toFixed(1)}
                  </div>
                </div>
              </div>
              
              <div className="mt-2 text-sm text-gray-600">
                {stock.reason}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* クイックアクション */}
      <div className="grid grid-cols-2 gap-3">
        <button className="bg-blue-600 text-white rounded-lg p-4 text-center hover:bg-blue-700 transition-colors">
          <TrendingUp className="w-6 h-6 mx-auto mb-2" />
          <div className="font-medium">5分ルーティン</div>
          <div className="text-sm opacity-90">今すぐ開始</div>
        </button>
        
        <button className="bg-green-600 text-white rounded-lg p-4 text-center hover:bg-green-700 transition-colors">
          <Star className="w-6 h-6 mx-auto mb-2" />
          <div className="font-medium">ウォッチリスト</div>
          <div className="text-sm opacity-90">銘柄を追加</div>
        </button>
      </div>
    </div>
  );
}
