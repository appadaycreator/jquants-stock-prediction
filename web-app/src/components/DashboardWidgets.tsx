'use client';

import React, { useState, useEffect } from 'react';
import { TrendingUp, BarChart3, Target, AlertTriangle, CheckCircle, Clock } from 'lucide-react';

interface PerformanceSummary {
  modelAccuracy: number;
  averageReturn: number;
  successRate: number;
  totalTrades: number;
}

interface MarketSummary {
  nikkeiChange: number;
  topixChange: number;
  sectorPerformance: Record<string, number>;
}

interface ModelComparison {
  name: string;
  algorithm: string;
  accuracy: number;
  trend: 'up' | 'down' | 'stable';
  lastUpdated: string;
}

interface Alert {
  id: string;
  type: 'volatility' | 'economic' | 'technical';
  message: string;
  severity: 'low' | 'medium' | 'high';
  timestamp: string;
}

interface DashboardWidgetsProps {
  performanceData?: PerformanceSummary;
  marketData?: MarketSummary;
  modelData?: ModelComparison[];
  alerts?: Alert[];
  isLoading?: boolean;
  error?: Error | null;
}

export const DashboardWidgets: React.FC<DashboardWidgetsProps> = ({
  performanceData,
  marketData,
  modelData = [],
  alerts = [],
  isLoading = false,
  error
}) => {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow-md p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-full"></div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center space-x-2 text-red-800">
          <AlertTriangle className="w-5 h-5" />
          <span className="font-medium">データの読み込みに失敗しました</span>
        </div>
        <p className="text-red-600 mt-2">{error.message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* パフォーマンスサマリー */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">モデル精度</p>
              <p className="text-2xl font-bold text-green-600">
                {performanceData?.modelAccuracy?.toFixed(1) || '--'}%
              </p>
            </div>
            <Target className="w-8 h-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">平均利回り</p>
              <p className="text-2xl font-bold text-blue-600">
                {performanceData?.averageReturn?.toFixed(2) || '--'}%
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">成功率</p>
              <p className="text-2xl font-bold text-purple-600">
                {performanceData?.successRate?.toFixed(1) || '--'}%
              </p>
            </div>
            <CheckCircle className="w-8 h-8 text-purple-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">総取引数</p>
              <p className="text-2xl font-bold text-orange-600">
                {performanceData?.totalTrades || '--'}
              </p>
            </div>
            <BarChart3 className="w-8 h-8 text-orange-500" />
          </div>
        </div>
      </div>

      {/* 市場サマリー */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">市場サマリー</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-600">日経平均</span>
              <span className={`text-lg font-bold ${
                (marketData?.nikkeiChange || 0) >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {(marketData?.nikkeiChange || 0) >= 0 ? '+' : ''}{marketData?.nikkeiChange?.toFixed(2) || '--'}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-600">TOPIX</span>
              <span className={`text-lg font-bold ${
                (marketData?.topixChange || 0) >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {(marketData?.topixChange || 0) >= 0 ? '+' : ''}{marketData?.topixChange?.toFixed(2) || '--'}%
              </span>
            </div>
          </div>
          
          <div>
            <h4 className="text-sm font-medium text-gray-600 mb-2">セクター別パフォーマンス</h4>
            <div className="space-y-1">
              {Object.entries(marketData?.sectorPerformance || {}).slice(0, 3).map(([sector, performance]) => (
                <div key={sector} className="flex justify-between items-center">
                  <span className="text-xs text-gray-600">{sector}</span>
                  <span className={`text-xs font-medium ${
                    performance >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {performance >= 0 ? '+' : ''}{performance.toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 機械学習モデル比較 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">機械学習モデル比較</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2 px-4 font-medium text-gray-600">モデル名</th>
                <th className="text-left py-2 px-4 font-medium text-gray-600">アルゴリズム</th>
                <th className="text-left py-2 px-4 font-medium text-gray-600">精度</th>
                <th className="text-left py-2 px-4 font-medium text-gray-600">トレンド</th>
                <th className="text-left py-2 px-4 font-medium text-gray-600">最終更新</th>
              </tr>
            </thead>
            <tbody>
              {modelData.map((model, index) => (
                <tr key={index} className="border-b">
                  <td className="py-2 px-4 font-medium">{model.name}</td>
                  <td className="py-2 px-4 text-gray-600">{model.algorithm}</td>
                  <td className="py-2 px-4">
                    <span className="font-bold text-green-600">
                      {model.accuracy.toFixed(1)}%
                    </span>
                  </td>
                  <td className="py-2 px-4">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      model.trend === 'up' ? 'bg-green-100 text-green-800' :
                      model.trend === 'down' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {model.trend === 'up' ? '↗' : model.trend === 'down' ? '↘' : '→'}
                    </span>
                  </td>
                  <td className="py-2 px-4 text-gray-600 text-sm">
                    {new Date(model.lastUpdated).toLocaleString('ja-JP')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* アラート */}
      {alerts.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">アラート</h3>
          <div className="space-y-3">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className={`p-3 rounded-md border-l-4 ${
                  alert.severity === 'high' ? 'border-red-500 bg-red-50' :
                  alert.severity === 'medium' ? 'border-yellow-500 bg-yellow-50' :
                  'border-blue-500 bg-blue-50'
                }`}
              >
                <div className="flex items-start space-x-3">
                  <AlertTriangle className={`w-5 h-5 mt-0.5 ${
                    alert.severity === 'high' ? 'text-red-500' :
                    alert.severity === 'medium' ? 'text-yellow-500' :
                    'text-blue-500'
                  }`} />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{alert.message}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(alert.timestamp).toLocaleString('ja-JP')}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 現在時刻 */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex items-center space-x-2 text-gray-600">
          <Clock className="w-4 h-4" />
          <span className="text-sm">
            最終更新: {currentTime.toLocaleString('ja-JP')}
          </span>
        </div>
      </div>
    </div>
  );
};

export default DashboardWidgets;