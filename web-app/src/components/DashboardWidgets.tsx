"use client";

import React, { useState, useEffect } from "react";
import { 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  AlertTriangle, 
  CheckCircle, 
  RefreshCw,
  Activity,
  Target,
  Shield,
  Brain
} from "lucide-react";

interface PerformanceMetrics {
  accuracy: number;
  mae: number;
  rmse: number;
  r2: number;
}

interface MarketInsights {
  trends: Array<{
    description: string;
    sentiment: "positive" | "negative" | "neutral";
  }>;
}

interface ModelComparison {
  name: string;
  type: string;
  mae: number;
  mse: number;
  rmse: number;
  r2: number;
  rank: number;
}

interface DashboardWidgetsProps {
  performanceMetrics: PerformanceMetrics;
  marketInsights: MarketInsights;
  modelComparison: ModelComparison[];
  isLoading?: boolean;
  error?: string | null;
  onRetry?: () => void;
  isSampleData?: boolean;
}

export default function DashboardWidgets({
  performanceMetrics,
  marketInsights,
  modelComparison,
  isLoading = false,
  error = null,
  onRetry,
  isSampleData = false
}: DashboardWidgetsProps) {
  const [retryCount, setRetryCount] = useState(0);
  const maxRetries = 3;

  const handleRetry = () => {
    if (retryCount < maxRetries) {
      setRetryCount(prev => prev + 1);
      onRetry?.();
    }
  };

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-full"></div>
          </div>
        ))}
      </div>
    );
  }

  if (error && retryCount >= maxRetries) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-red-800 mb-2">データの読み込みに失敗しました</h3>
        <p className="text-red-600 mb-4">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors"
        >
          ページを再読み込み
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* サンプルデータ警告 */}
      {isSampleData && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 text-yellow-600 mr-2" />
            <span className="text-yellow-800">
              サンプルデータを表示しています。実際のデータを取得するには認証設定を確認してください。
            </span>
          </div>
        </div>
      )}

      {/* エラー表示とリトライ */}
      {error && retryCount < maxRetries && (
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <AlertTriangle className="h-5 w-5 text-orange-600 mr-2" />
              <span className="text-orange-800">
                データ取得エラー: {error} ({retryCount}/{maxRetries}回試行中)
              </span>
            </div>
            <button
              onClick={handleRetry}
              className="bg-orange-600 text-white px-3 py-1 rounded text-sm hover:bg-orange-700 transition-colors flex items-center"
            >
              <RefreshCw className="h-4 w-4 mr-1" />
              再試行
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* パフォーマンスサマリー */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">パフォーマンスサマリー</h3>
            <Activity className="h-5 w-5 text-blue-600" />
          </div>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">精度</span>
              <span className="font-semibold text-green-600">{performanceMetrics.accuracy}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">MAE</span>
              <span className="font-semibold">{performanceMetrics.mae}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">RMSE</span>
              <span className="font-semibold">{performanceMetrics.rmse}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">R²</span>
              <span className="font-semibold">{performanceMetrics.r2}</span>
            </div>
          </div>
        </div>

        {/* 市場サマリー */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">市場サマリー</h3>
            <BarChart3 className="h-5 w-5 text-green-600" />
          </div>
          <div className="space-y-2">
            {marketInsights.trends.map((trend, index) => (
              <div key={index} className="flex items-center">
                {trend.sentiment === "positive" && <TrendingUp className="h-4 w-4 text-green-500 mr-2" />}
                {trend.sentiment === "negative" && <TrendingDown className="h-4 w-4 text-red-500 mr-2" />}
                {trend.sentiment === "neutral" && <Activity className="h-4 w-4 text-gray-500 mr-2" />}
                <span className="text-sm text-gray-700">{trend.description}</span>
              </div>
            ))}
          </div>
        </div>

        {/* 機械学習モデル比較 */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">モデル比較</h3>
            <Brain className="h-5 w-5 text-purple-600" />
          </div>
          <div className="space-y-3">
            {modelComparison.slice(0, 3).map((model, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className={`w-3 h-3 rounded-full mr-2 ${
                    model.rank === 1 ? 'bg-green-500' : 
                    model.rank === 2 ? 'bg-yellow-500' : 'bg-gray-400'
                  }`} />
                  <span className="text-sm font-medium">{model.name}</span>
                </div>
                <span className="text-sm text-gray-600">{model.r2.toFixed(3)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* アラート */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">アラート</h3>
            <Shield className="h-5 w-5 text-red-600" />
          </div>
          <div className="space-y-2">
            <div className="flex items-center text-sm">
              <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
              <span className="text-gray-700">システム正常稼働中</span>
            </div>
            <div className="flex items-center text-sm">
              <AlertTriangle className="h-4 w-4 text-yellow-500 mr-2" />
              <span className="text-gray-700">高ボラティリティ銘柄を監視中</span>
            </div>
          </div>
        </div>

        {/* 推奨アクション */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">推奨アクション</h3>
            <Target className="h-5 w-5 text-blue-600" />
          </div>
          <div className="space-y-2">
            <div className="text-sm text-gray-700">
              • ポートフォリオの再バランスを検討
            </div>
            <div className="text-sm text-gray-700">
              • リスク管理指標の確認
            </div>
            <div className="text-sm text-gray-700">
              • 新規投資機会の分析
            </div>
          </div>
        </div>

        {/* システム状態 */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">システム状態</h3>
            <CheckCircle className="h-5 w-5 text-green-600" />
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">API接続</span>
              <span className="text-green-600 font-medium">正常</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">データ更新</span>
              <span className="text-green-600 font-medium">最新</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">予測精度</span>
              <span className="text-green-600 font-medium">高</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
