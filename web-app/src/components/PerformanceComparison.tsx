"use client";

import React, { useState, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  TrendingUp, 
  TrendingDown, 
  Award,
  AlertTriangle,
  Target,
  Star,
  Zap,
  Shield,
  Activity,
  BarChart3,
  PieChart as PieChartIcon,
} from "lucide-react";
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from "recharts";

// データ型定義
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
  market_cap?: number;
  volume?: number;
  volatility?: number;
  beta?: number;
  pe_ratio?: number;
  dividend_yield?: number;
}

interface PerformanceComparisonProps {
  positions: PositionPerformance[];
  benchmarkData?: {
    name: string;
    return: number;
    volatility: number;
  };
  onPositionClick?: (symbol: string) => void;
  className?: string;
}

export function PerformanceComparison({
  positions,
  benchmarkData,
  onPositionClick,
  className = "",
}: PerformanceComparisonProps) {
  const [sortBy, setSortBy] = useState<"pnl" | "weight" | "volatility" | "beta">("pnl");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [filterSector, setFilterSector] = useState<string>("all");
  const [viewMode, setViewMode] = useState<"table" | "chart" | "sector">("table");

  // パフォーマンスランキングの計算
  const performanceRanking = useMemo(() => {
    let sorted = [...positions];
    
    // ソート
    sorted.sort((a, b) => {
      let aValue: number, bValue: number;
      
      switch (sortBy) {
        case "pnl":
          aValue = a.pnl_percentage;
          bValue = b.pnl_percentage;
          break;
        case "weight":
          aValue = a.weight;
          bValue = b.weight;
          break;
        case "volatility":
          aValue = a.volatility || 0;
          bValue = b.volatility || 0;
          break;
        case "beta":
          aValue = a.beta || 0;
          bValue = b.beta || 0;
          break;
        default:
          aValue = a.pnl_percentage;
          bValue = b.pnl_percentage;
      }
      
      return sortOrder === "desc" ? bValue - aValue : aValue - bValue;
    });

    // セクターフィルタ
    if (filterSector !== "all") {
      sorted = sorted.filter(pos => pos.sector === filterSector);
    }

    return sorted;
  }, [positions, sortBy, sortOrder, filterSector]);

  // セクター別パフォーマンス
  const sectorPerformance = useMemo(() => {
    const sectorMap = new Map<string, {
      totalValue: number;
      totalPnL: number;
      count: number;
      avgReturn: number;
      totalWeight: number;
    }>();

    positions.forEach(position => {
      const sector = position.sector || "その他";
      const existing = sectorMap.get(sector) || {
        totalValue: 0,
        totalPnL: 0,
        count: 0,
        avgReturn: 0,
        totalWeight: 0,
      };

      sectorMap.set(sector, {
        totalValue: existing.totalValue + position.current_value,
        totalPnL: existing.totalPnL + position.unrealized_pnl,
        count: existing.count + 1,
        avgReturn: existing.avgReturn + position.pnl_percentage,
        totalWeight: existing.totalWeight + position.weight,
      });
    });

    return Array.from(sectorMap.entries()).map(([sector, data]) => ({
      sector,
      value: data.totalValue,
      pnl: data.totalPnL,
      pnlPercentage: data.totalValue > 0 ? (data.totalPnL / data.totalValue) * 100 : 0,
      count: data.count,
      avgReturn: data.avgReturn / data.count,
      weight: data.totalWeight,
    })).sort((a, b) => b.pnlPercentage - a.pnlPercentage);
  }, [positions]);

  // ベスト・ワーストパフォーマー
  const bestWorstPerformers = useMemo(() => {
    const sorted = [...positions].sort((a, b) => b.pnl_percentage - a.pnl_percentage);
    return {
      best: sorted.slice(0, 3),
      worst: sorted.slice(-3).reverse(),
    };
  }, [positions]);

  // リスク分析
  const riskAnalysis = useMemo(() => {
    const highRisk = positions.filter(p => p.risk_level === "HIGH").length;
    const mediumRisk = positions.filter(p => p.risk_level === "MEDIUM").length;
    const lowRisk = positions.filter(p => p.risk_level === "LOW").length;
    
    const totalVolatility = positions.reduce((sum, p) => sum + (p.volatility || 0), 0);
    const avgVolatility = totalVolatility / positions.length;
    
    const highVolatility = positions.filter(p => (p.volatility || 0) > avgVolatility * 1.5).length;

    return {
      riskDistribution: { highRisk, mediumRisk, lowRisk },
      volatilityAnalysis: { avgVolatility, highVolatility },
      totalPositions: positions.length,
    };
  }, [positions]);

  // パフォーマンスバッジの色
  const getPerformanceBadgeColor = (percentage: number) => {
    if (percentage >= 20) return "bg-green-100 text-green-800 border-green-200";
    if (percentage >= 10) return "bg-blue-100 text-blue-800 border-blue-200";
    if (percentage >= 0) return "bg-yellow-100 text-yellow-800 border-yellow-200";
    if (percentage >= -10) return "bg-orange-100 text-orange-800 border-orange-200";
    return "bg-red-100 text-red-800 border-red-200";
  };

  // リスクレベルの色
  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case "HIGH": return "text-red-600 bg-red-100";
      case "MEDIUM": return "text-yellow-600 bg-yellow-100";
      case "LOW": return "text-green-600 bg-green-100";
      default: return "text-gray-600 bg-gray-100";
    }
  };

  // セクターの色
  const getSectorColor = (index: number) => {
    const colors = [
      "#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6",
      "#06b6d4", "#84cc16", "#f97316", "#ec4899", "#6366f1",
    ];
    return colors[index % colors.length];
  };

  return (
    <div className={className}>
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle className="flex items-center">
              <Award className="h-5 w-5 mr-2" />
              パフォーマンス比較
            </CardTitle>
            <div className="flex space-x-2">
              <Button
                variant={viewMode === "table" ? "default" : "outline"}
                size="sm"
                onClick={() => setViewMode("table")}
              >
                <BarChart3 className="h-4 w-4 mr-1" />
                テーブル
              </Button>
              <Button
                variant={viewMode === "chart" ? "default" : "outline"}
                size="sm"
                onClick={() => setViewMode("chart")}
              >
                <Activity className="h-4 w-4 mr-1" />
                チャート
              </Button>
              <Button
                variant={viewMode === "sector" ? "default" : "outline"}
                size="sm"
                onClick={() => setViewMode("sector")}
              >
                <PieChartIcon className="h-4 w-4 mr-1" />
                セクター
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="ranking" className="space-y-4">
            <TabsList>
              <TabsTrigger value="ranking">ランキング</TabsTrigger>
              <TabsTrigger value="best-worst">ベスト・ワースト</TabsTrigger>
              <TabsTrigger value="risk">リスク分析</TabsTrigger>
              <TabsTrigger value="sector">セクター分析</TabsTrigger>
            </TabsList>

            {/* ランキング */}
            <TabsContent value="ranking" className="space-y-4">
              {/* ソート・フィルター */}
              <div className="flex flex-wrap gap-4 items-center">
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium">ソート:</span>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as any)}
                    className="px-3 py-1 border border-gray-300 rounded-md text-sm"
                  >
                    <option value="pnl">損益率</option>
                    <option value="weight">配分</option>
                    <option value="volatility">ボラティリティ</option>
                    <option value="beta">ベータ</option>
                  </select>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSortOrder(sortOrder === "desc" ? "asc" : "desc")}
                  >
                    {sortOrder === "desc" ? <TrendingDown className="h-4 w-4" /> : <TrendingUp className="h-4 w-4" />}
                  </Button>
                </div>
                
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium">セクター:</span>
                  <select
                    value={filterSector}
                    onChange={(e) => setFilterSector(e.target.value)}
                    className="px-3 py-1 border border-gray-300 rounded-md text-sm"
                  >
                    <option value="all">すべて</option>
                    {Array.from(new Set(positions.map(p => p.sector))).map(sector => (
                      <option key={sector} value={sector}>{sector}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* ランキング表示 */}
              <div className="space-y-3">
                {performanceRanking.map((position, index) => (
                  <div 
                    key={position.symbol} 
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                    onClick={() => onPositionClick?.(position.symbol)}
                  >
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center justify-center w-8 h-8 bg-blue-100 text-blue-800 rounded-full font-bold">
                        {index + 1}
                      </div>
                      <div>
                        <div className="font-semibold">{position.symbol}</div>
                        <div className="text-sm text-gray-600">{position.symbolName}</div>
                        <div className="flex items-center space-x-2 mt-1">
                          <Badge className={getRiskColor(position.risk_level)}>
                            {position.risk_level}
                          </Badge>
                          <span className="text-xs text-gray-500">{position.sector}</span>
                        </div>
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
                      <div className="text-xs text-gray-500">
                        配分: {(position.weight * 100).toFixed(1)}%
                      </div>
                    </div>
                    <Badge className={getPerformanceBadgeColor(position.pnl_percentage)}>
                      {position.pnl_percentage >= 0 ? "利益" : "損失"}
                    </Badge>
                  </div>
                ))}
              </div>
            </TabsContent>

            {/* ベスト・ワースト */}
            <TabsContent value="best-worst" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* ベストパフォーマー */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center text-green-600">
                      <Star className="h-5 w-5 mr-2" />
                      ベストパフォーマー
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {bestWorstPerformers.best.map((position, index) => (
                        <div key={position.symbol} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                          <div className="flex items-center space-x-3">
                            <div className="flex items-center justify-center w-6 h-6 bg-green-100 text-green-800 rounded-full font-bold text-sm">
                              {index + 1}
                            </div>
                            <div>
                              <div className="font-semibold">{position.symbol}</div>
                              <div className="text-sm text-gray-600">{position.symbolName}</div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-lg font-bold text-green-600">
                              +{position.pnl_percentage.toFixed(2)}%
                            </div>
                            <div className="text-sm text-gray-600">
                              ¥{position.unrealized_pnl.toLocaleString()}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* ワーストパフォーマー */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center text-red-600">
                      <AlertTriangle className="h-5 w-5 mr-2" />
                      ワーストパフォーマー
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {bestWorstPerformers.worst.map((position, index) => (
                        <div key={position.symbol} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                          <div className="flex items-center space-x-3">
                            <div className="flex items-center justify-center w-6 h-6 bg-red-100 text-red-800 rounded-full font-bold text-sm">
                              {index + 1}
                            </div>
                            <div>
                              <div className="font-semibold">{position.symbol}</div>
                              <div className="text-sm text-gray-600">{position.symbolName}</div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-lg font-bold text-red-600">
                              {position.pnl_percentage.toFixed(2)}%
                            </div>
                            <div className="text-sm text-gray-600">
                              ¥{position.unrealized_pnl.toLocaleString()}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* リスク分析 */}
            <TabsContent value="risk" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Shield className="h-5 w-5 mr-2" />
                      リスク分布
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm">高リスク</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-20 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-red-500 h-2 rounded-full" 
                              style={{ width: `${(riskAnalysis.riskDistribution.highRisk / riskAnalysis.totalPositions) * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium">{riskAnalysis.riskDistribution.highRisk}</span>
                        </div>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">中リスク</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-20 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-yellow-500 h-2 rounded-full" 
                              style={{ width: `${(riskAnalysis.riskDistribution.mediumRisk / riskAnalysis.totalPositions) * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium">{riskAnalysis.riskDistribution.mediumRisk}</span>
                        </div>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">低リスク</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-20 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-green-500 h-2 rounded-full" 
                              style={{ width: `${(riskAnalysis.riskDistribution.lowRisk / riskAnalysis.totalPositions) * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium">{riskAnalysis.riskDistribution.lowRisk}</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Zap className="h-5 w-5 mr-2" />
                      ボラティリティ分析
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-gray-700">
                          {riskAnalysis.volatilityAnalysis.avgVolatility.toFixed(2)}%
                        </div>
                        <div className="text-sm text-gray-600">平均ボラティリティ</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-orange-600">
                          {riskAnalysis.volatilityAnalysis.highVolatility}
                        </div>
                        <div className="text-sm text-gray-600">高ボラティリティ銘柄</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* セクター分析 */}
            <TabsContent value="sector" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>セクター別パフォーマンス</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {sectorPerformance.map((sector, index) => (
                        <div key={sector.sector} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div className="flex items-center space-x-3">
                            <div 
                              className="w-4 h-4 rounded-full" 
                              style={{ backgroundColor: getSectorColor(index) }}
                            ></div>
                            <div>
                              <div className="font-semibold">{sector.sector}</div>
                              <div className="text-sm text-gray-600">{sector.count}銘柄</div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className={`text-lg font-bold ${
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
                            dataKey="weight"
                            nameKey="sector"
                            cx="50%"
                            cy="50%"
                            outerRadius={80}
                            label={({ sector, percent }) => `${sector} ${(percent * 100).toFixed(1)}%`}
                          >
                            {sectorPerformance.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={getSectorColor(index)} />
                            ))}
                          </Pie>
                          <Tooltip formatter={(value: number) => [`${(value * 100).toFixed(1)}%`, "配分"]} />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}

export default PerformanceComparison;
