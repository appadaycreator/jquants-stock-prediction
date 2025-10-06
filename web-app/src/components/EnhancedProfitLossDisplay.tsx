"use client";

import React, { useState, useEffect, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Target,
  Award,
  AlertTriangle,
  BarChart3,
  Calendar,
  RefreshCw,
  Eye,
  EyeOff,
  ArrowUp,
  ArrowDown,
  Minus,
  Star,
  Activity,
  Shield,
  Zap,
} from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from "recharts";

// データ型定義
interface EnhancedPnLSummary {
  total_investment: number;
  current_value: number;
  unrealized_pnl: number;
  realized_pnl: number;
  total_pnl: number;
  pnl_percentage: number;
  daily_pnl: number;
  weekly_pnl: number;
  monthly_pnl: number;
  yearly_pnl: number;
  best_performer: {
    symbol: string;
    symbolName: string;
    return: number;
    value: number;
  };
  worst_performer: {
    symbol: string;
    symbolName: string;
    return: number;
    value: number;
  };
  risk_adjusted_return: number;
  sharpe_ratio: number;
  max_drawdown: number;
  volatility: number;
  win_rate: number;
  profit_factor: number;
}

interface PerformanceData {
  date: string;
  total_value: number;
  daily_pnl: number;
  cumulative_pnl: number;
  benchmark_return?: number;
}

interface PositionPerformance {
  symbol: string;
  symbolName: string;
  current_value: number;
  cost_basis: number;
  unrealized_pnl: number;
  pnl_percentage: number;
  weight: number;
  contribution: number;
  risk_level: string;
  sector: string;
}

interface EnhancedProfitLossDisplayProps {
  pnlSummary: EnhancedPnLSummary;
  performanceData: PerformanceData[];
  positions: PositionPerformance[];
  onRefresh?: () => void;
  isLoading?: boolean;
  autoRefresh?: boolean;
  onAutoRefreshToggle?: (enabled: boolean) => void;
}

export function EnhancedProfitLossDisplay({
  pnlSummary,
  performanceData,
  positions,
  onRefresh,
  isLoading = false,
  autoRefresh = false,
  onAutoRefreshToggle,
}: EnhancedProfitLossDisplayProps) {
  const [selectedPeriod, setSelectedPeriod] = useState<"daily" | "weekly" | "monthly" | "yearly">("daily");
  const [showDetails, setShowDetails] = useState(true);
  const [chartType, setChartType] = useState<"line" | "bar">("line");

  // パフォーマンスデータの処理
  const processedPerformanceData = useMemo(() => {
    if (!performanceData || performanceData.length === 0) return [];
    
    return performanceData.map((data, index) => ({
      ...data,
      date: new Date(data.date).toLocaleDateString("ja-JP", { 
        month: "short", 
        day: "numeric", 
      }),
      index: index + 1,
    }));
  }, [performanceData]);

  // 期間別損益の計算
  const periodPnL = useMemo(() => {
    const current = pnlSummary.current_value;
    const investment = pnlSummary.total_investment;
    
    return {
      daily: pnlSummary.daily_pnl,
      weekly: pnlSummary.weekly_pnl,
      monthly: pnlSummary.monthly_pnl,
      yearly: pnlSummary.yearly_pnl,
      total: pnlSummary.unrealized_pnl,
    };
  }, [pnlSummary]);

  // パフォーマンスランキング
  const performanceRanking = useMemo(() => {
    return positions
      .sort((a, b) => b.pnl_percentage - a.pnl_percentage)
      .slice(0, 10);
  }, [positions]);

  // セクター別パフォーマンス
  const sectorPerformance = useMemo(() => {
    const sectorMap = new Map<string, { totalValue: number; totalPnL: number; count: number }>();
    
    positions.forEach(position => {
      const sector = position.sector || "その他";
      const existing = sectorMap.get(sector) || { totalValue: 0, totalPnL: 0, count: 0 };
      
      sectorMap.set(sector, {
        totalValue: existing.totalValue + position.current_value,
        totalPnL: existing.totalPnL + position.unrealized_pnl,
        count: existing.count + 1,
      });
    });

    return Array.from(sectorMap.entries()).map(([sector, data]) => ({
      sector,
      value: data.totalValue,
      pnl: data.totalPnL,
      pnlPercentage: data.totalValue > 0 ? (data.totalPnL / data.totalValue) * 100 : 0,
      count: data.count,
    })).sort((a, b) => b.pnlPercentage - a.pnlPercentage);
  }, [positions]);

  // リスク指標の色分け
  const getRiskColor = (value: number, type: "positive" | "negative" = "positive") => {
    if (type === "positive") {
      return value >= 0 ? "text-green-600" : "text-red-600";
    } else {
      return value <= 0.1 ? "text-green-600" : value <= 0.3 ? "text-yellow-600" : "text-red-600";
    }
  };

  // パフォーマンスバッジの色
  const getPerformanceBadgeColor = (percentage: number) => {
    if (percentage >= 20) return "bg-green-100 text-green-800 border-green-200";
    if (percentage >= 10) return "bg-blue-100 text-blue-800 border-blue-200";
    if (percentage >= 0) return "bg-yellow-100 text-yellow-800 border-yellow-200";
    if (percentage >= -10) return "bg-orange-100 text-orange-800 border-orange-200";
    return "bg-red-100 text-red-800 border-red-200";
  };

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">投資成果ダッシュボード</h2>
          <p className="text-sm text-gray-600">投資成果を3秒で把握</p>
        </div>
        <div className="flex space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowDetails(!showDetails)}
            title={showDetails ? "詳細を非表示" : "詳細を表示"}
          >
            {showDetails ? <EyeOff className="h-4 w-4 mr-1" /> : <Eye className="h-4 w-4 mr-1" />}
            {showDetails ? "簡易表示" : "詳細表示"}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={onRefresh}
            disabled={isLoading}
            title="最新データを取得"
          >
            <RefreshCw className={`h-4 w-4 mr-1 ${isLoading ? "animate-spin" : ""}`} />
            更新
          </Button>
          <Button
            variant={autoRefresh ? "default" : "outline"}
            size="sm"
            onClick={() => onAutoRefreshToggle?.(!autoRefresh)}
            title="30秒ごとに自動更新"
          >
            <Activity className="h-4 w-4 mr-1" />
            自動更新
          </Button>
        </div>
      </div>

      {/* 主要指標 - 大きく表示 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* 総投資額 */}
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-blue-800">総投資額</CardTitle>
            <DollarSign className="h-5 w-5 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-900">
              ¥{pnlSummary.total_investment.toLocaleString()}
            </div>
            <p className="text-xs text-blue-700 mt-1">累計投資金額</p>
          </CardContent>
        </Card>

        {/* 現在価値 */}
        <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-green-800">現在価値</CardTitle>
            <TrendingUp className="h-5 w-5 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-900">
              ¥{pnlSummary.current_value.toLocaleString()}
            </div>
            <p className="text-xs text-green-700 mt-1">現在の評価額</p>
          </CardContent>
        </Card>

        {/* 損益 - 最重要表示 */}
        <Card className={`${
          pnlSummary.unrealized_pnl >= 0 
            ? "bg-gradient-to-br from-green-50 to-green-100 border-green-200" 
            : "bg-gradient-to-br from-red-50 to-red-100 border-red-200"
        }`}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className={`text-sm font-medium ${
              pnlSummary.unrealized_pnl >= 0 ? "text-green-800" : "text-red-800"
            }`}>
              損益
            </CardTitle>
            {pnlSummary.unrealized_pnl >= 0 ? (
              <TrendingUp className="h-5 w-5 text-green-600" />
            ) : (
              <TrendingDown className="h-5 w-5 text-red-600" />
            )}
          </CardHeader>
          <CardContent>
            <div className={`text-4xl font-bold ${
              pnlSummary.unrealized_pnl >= 0 ? "text-green-900" : "text-red-900"
            }`}>
              {pnlSummary.unrealized_pnl >= 0 ? "+" : ""}¥{pnlSummary.unrealized_pnl.toLocaleString()}
            </div>
            <p className={`text-lg font-semibold ${
              pnlSummary.unrealized_pnl >= 0 ? "text-green-700" : "text-red-700"
            }`}>
              {pnlSummary.unrealized_pnl >= 0 ? "+" : ""}{pnlSummary.pnl_percentage.toFixed(2)}%
            </p>
          </CardContent>
        </Card>

        {/* リスク調整後リターン */}
        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-purple-800">シャープレシオ</CardTitle>
            <Shield className="h-5 w-5 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-purple-900">
              {pnlSummary.sharpe_ratio.toFixed(2)}
            </div>
            <p className="text-xs text-purple-700 mt-1">リスク調整後リターン</p>
          </CardContent>
        </Card>
      </div>

      {/* 期間別損益 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Calendar className="h-5 w-5 mr-2" />
            期間別損益
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {Object.entries(periodPnL).map(([period, value]) => (
              <div key={period} className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-sm font-medium text-gray-600 capitalize mb-1">
                  {period === "daily" ? "日次" : 
                   period === "weekly" ? "週次" : 
                   period === "monthly" ? "月次" : 
                   period === "yearly" ? "年次" : "総合"}
                </div>
                <div className={`text-2xl font-bold ${
                  value >= 0 ? "text-green-600" : "text-red-600"
                }`}>
                  {value >= 0 ? "+" : ""}¥{value.toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 詳細表示 */}
      {showDetails && (
        <Tabs defaultValue="performance" className="space-y-4">
          <TabsList>
            <TabsTrigger value="performance">パフォーマンス推移</TabsTrigger>
            <TabsTrigger value="ranking">銘柄ランキング</TabsTrigger>
            <TabsTrigger value="sector">セクター分析</TabsTrigger>
            <TabsTrigger value="risk">リスク指標</TabsTrigger>
          </TabsList>

          {/* パフォーマンス推移 */}
          <TabsContent value="performance" className="space-y-4">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>損益推移グラフ</CardTitle>
                  <div className="flex space-x-2">
                    <Button
                      variant={chartType === "line" ? "default" : "outline"}
                      size="sm"
                      onClick={() => setChartType("line")}
                    >
                      <BarChart3 className="h-4 w-4 mr-1" />
                      ライン
                    </Button>
                    <Button
                      variant={chartType === "bar" ? "default" : "outline"}
                      size="sm"
                      onClick={() => setChartType("bar")}
                    >
                      <BarChart3 className="h-4 w-4 mr-1" />
                      バー
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="h-96">
                  <ResponsiveContainer width="100%" height="100%">
                    {chartType === "line" ? (
                      <LineChart data={processedPerformanceData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip 
                          formatter={(value: number, name: string) => [
                            `¥${value.toLocaleString()}`, 
                            name === "total_value" ? "総資産価値" : 
                            name === "daily_pnl" ? "日次損益" : 
                            name === "cumulative_pnl" ? "累積損益" : name,
                          ]}
                        />
                        <Line 
                          type="monotone" 
                          dataKey="total_value" 
                          stroke="#3b82f6" 
                          strokeWidth={3}
                          name="総資産価値"
                        />
                        <Line 
                          type="monotone" 
                          dataKey="cumulative_pnl" 
                          stroke="#10b981" 
                          strokeWidth={2}
                          name="累積損益"
                        />
                      </LineChart>
                    ) : (
                      <BarChart data={processedPerformanceData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip 
                          formatter={(value: number, name: string) => [
                            `¥${value.toLocaleString()}`, 
                            name === "daily_pnl" ? "日次損益" : "累積損益",
                          ]}
                        />
                        <Bar dataKey="daily_pnl" fill="#10b981" name="日次損益" />
                      </BarChart>
                    )}
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* 銘柄ランキング */}
          <TabsContent value="ranking" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Award className="h-5 w-5 mr-2" />
                  銘柄パフォーマンスランキング
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {performanceRanking.map((position, index) => (
                    <div key={position.symbol} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center justify-center w-8 h-8 bg-blue-100 text-blue-800 rounded-full font-bold">
                          {index + 1}
                        </div>
                        <div>
                          <div className="font-semibold">{position.symbol}</div>
                          <div className="text-sm text-gray-600">{position.symbolName}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`text-lg font-bold ${
                          position.pnl_percentage >= 0 ? "text-green-600" : "text-red-600"
                        }`}>
                          {position.pnl_percentage >= 0 ? "+" : ""}{position.pnl_percentage.toFixed(2)}%
                        </div>
                        <div className="text-sm text-gray-600">
                          ¥{position.unrealized_pnl.toLocaleString()}
                        </div>
                      </div>
                      <Badge className={getPerformanceBadgeColor(position.pnl_percentage)}>
                        {position.pnl_percentage >= 0 ? "利益" : "損失"}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* セクター分析 */}
          <TabsContent value="sector" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle>セクター別パフォーマンス</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {sectorPerformance.map((sector, index) => (
                      <div key={sector.sector} className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                          <span className="font-medium">{sector.sector}</span>
                          <span className="text-sm text-gray-500">({sector.count}銘柄)</span>
                        </div>
                        <div className="text-right">
                          <div className={`font-bold ${
                            sector.pnlPercentage >= 0 ? "text-green-600" : "text-red-600"
                          }`}>
                            {sector.pnlPercentage >= 0 ? "+" : ""}{sector.pnlPercentage.toFixed(2)}%
                          </div>
                          <div className="text-sm text-gray-600">
                            ¥{sector.pnl.toLocaleString()}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>セクター別配分</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={sectorPerformance}
                          dataKey="value"
                          nameKey="sector"
                          cx="50%"
                          cy="50%"
                          outerRadius={80}
                          label={({ sector, percent }) => `${sector} ${(percent * 100).toFixed(1)}%`}
                        >
                          {sectorPerformance.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={`hsl(${index * 60}, 70%, 50%)`} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value: number) => [`¥${value.toLocaleString()}`, "価値"]} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* リスク指標 */}
          <TabsContent value="risk" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">最大ドローダウン</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className={`text-2xl font-bold ${getRiskColor(pnlSummary.max_drawdown, "negative")}`}>
                    {pnlSummary.max_drawdown.toFixed(2)}%
                  </div>
                  <p className="text-xs text-gray-600 mt-1">最大損失幅</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">ボラティリティ</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className={`text-2xl font-bold ${getRiskColor(pnlSummary.volatility, "negative")}`}>
                    {pnlSummary.volatility.toFixed(2)}%
                  </div>
                  <p className="text-xs text-gray-600 mt-1">価格変動率</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">勝率</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className={`text-2xl font-bold ${getRiskColor(pnlSummary.win_rate, "positive")}`}>
                    {pnlSummary.win_rate.toFixed(1)}%
                  </div>
                  <p className="text-xs text-gray-600 mt-1">利益確定率</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">プロフィットファクター</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className={`text-2xl font-bold ${getRiskColor(pnlSummary.profit_factor, "positive")}`}>
                    {pnlSummary.profit_factor.toFixed(2)}
                  </div>
                  <p className="text-xs text-gray-600 mt-1">利益/損失比率</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
}

export default EnhancedProfitLossDisplay;
