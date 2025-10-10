"use client";

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  RefreshCw,
  Clock,
  AlertTriangle,
  Info,
  ArrowUp,
  ArrowDown,
  Minus,
} from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useSimpleDashboard } from "@/hooks/useSimpleDashboard";
import { 
  SimpleDashboardCard, 
  RecommendationCard, 
  PortfolioSummaryCard, 
} from "@/components/simple-dashboard/SimpleDashboardCard";

// 動的レンダリングを強制
export const dynamic = "force-dynamic";

export default function SimpleDashboard() {
  const { data: dashboardData, loading, error, refreshData } = useSimpleDashboard();

  const getActionIcon = (action: string) => {
    switch (action) {
      case "BUY":
      case "BUY_MORE":
        return <ArrowUp className="h-4 w-4 text-green-600" />;
      case "SELL":
        return <ArrowDown className="h-4 w-4 text-red-600" />;
      case "HOLD":
        return <Minus className="h-4 w-4 text-gray-600" />;
      default:
        return <Minus className="h-4 w-4 text-gray-600" />;
    }
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case "BUY":
      case "BUY_MORE":
        return "bg-green-100 text-green-800 border-green-200";
      case "SELL":
        return "bg-red-100 text-red-800 border-red-200";
      case "HOLD":
        return "bg-gray-100 text-gray-800 border-gray-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("ja-JP", {
      style: "currency",
      currency: "JPY",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercent = (percent: number) => {
    return `${percent >= 0 ? "+" : ""}${percent.toFixed(1)}%`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-48 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-7xl mx-auto">
          <Alert className="border-red-200 bg-red-50">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-7xl mx-auto">
          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>データがありません</AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* ヘッダー */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">シンプル投資判断</h1>
              <p className="text-gray-600 mt-1">
                最終更新: {new Date(dashboardData.lastUpdate).toLocaleString("ja-JP")}
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Clock className="h-4 w-4 text-gray-500" />
                <span className="text-sm text-gray-600">
                  {dashboardData.marketStatus.isOpen ? "市場開場中" : "市場閉場中"}
                </span>
              </div>
              <Button
                onClick={refreshData}
                variant="outline"
                size="sm"
                disabled={loading}
                aria-label="ダッシュボードを更新"
                data-help="ダッシュボードのデータを最新に更新します。推奨アクション、損益状況、保有銘柄の情報を再取得します。市場の最新動向に基づいて投資判断に必要な情報を最新に保ちます。リアルタイムで投資状況を監視し、重要な投資判断に必要な最新情報を確認できます。市場の開場・閉場状況も同時に更新され、投資タイミングを把握できます。"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
                更新
              </Button>
            </div>
          </div>
        </div>

        {/* 推奨アクション */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">今日の推奨アクション</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {dashboardData.recommendations.map((recommendation) => (
              <RecommendationCard key={recommendation.id} recommendation={recommendation} />
            ))}
          </div>
        </div>

        {/* 損益サマリー */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">損益状況</h2>
          <PortfolioSummaryCard summary={dashboardData.portfolioSummary} />
        </div>

        {/* 保有銘柄一覧 */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">保有銘柄</h2>
          <div className="space-y-4">
            {dashboardData.positions.map((position) => (
              <Card key={position.symbol}>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div>
                        <h3 className="text-lg font-medium">{position.symbolName}</h3>
                        <p className="text-sm text-gray-600">{position.symbol}</p>
                      </div>
                      <Badge className={getActionColor(position.action)}>
                        {getActionIcon(position.action)}
                        <span className="ml-1">{position.action}</span>
                      </Badge>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-600">現在価値</p>
                      <p className="text-lg font-medium">
                        {formatCurrency(position.currentValue)}
                      </p>
                      <p className={`text-sm ${
                        position.unrealizedPnL >= 0 ? "text-green-600" : "text-red-600"
                      }`}>
                        {formatCurrency(position.unrealizedPnL)} ({formatPercent(position.unrealizedPnLPercent)})
                      </p>
                    </div>
                  </div>
                  <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600">数量</p>
                      <p className="font-medium">{position.quantity}株</p>
                    </div>
                    <div>
                      <p className="text-gray-600">平均価格</p>
                      <p className="font-medium">{formatCurrency(position.averagePrice)}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">現在価格</p>
                      <p className="font-medium">{formatCurrency(position.currentPrice)}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">信頼度</p>
                      <p className="font-medium">{position.confidence}%</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
