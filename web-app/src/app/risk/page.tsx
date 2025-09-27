"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
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
  PieChart,
  Pie,
  Cell,
  Area,
  AreaChart
} from 'recharts';
import { 
  Shield, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  DollarSign, 
  Target,
  Activity,
  AlertCircle,
  CheckCircle,
  XCircle
} from 'lucide-react';

// データ型定義
interface PortfolioOverview {
  timestamp: string;
  account_value: number;
  portfolio_value: number;
  total_exposure: number;
  total_unrealized_pnl: number;
  risk_level: string;
  risk_color: string;
  risk_score: number;
  max_drawdown: number;
  var_95: number;
  sharpe_ratio: number;
  should_reduce_risk: boolean;
}

interface Position {
  symbol: string;
  company_name: string;
  position_type: string;
  entry_price: number;
  current_price: number;
  quantity: number;
  entry_time: string;
  unrealized_pnl: number;
  unrealized_pnl_percent: number;
  pnl_color: string;
  stop_loss_price: number;
  take_profit_price: number;
  stop_distance: number;
  profit_distance: number;
  risk_score: number;
  risk_level: string;
  risk_color: string;
  status: string;
  market_value: number;
  weight: number;
}

interface RiskMetricsChart {
  dates: string[];
  risk_scores: number[];
  portfolio_values: number[];
  drawdowns: number[];
  current_risk_score: number;
  current_portfolio_value: number;
  current_drawdown: number;
}

interface PositionPerformanceChart {
  positions: Array<{
    symbol: string;
    company_name: string;
    dates: string[];
    prices: number[];
    stop_loss_line: number[];
    take_profit_line: number[];
    entry_price: number;
    current_price: number;
    unrealized_pnl: number;
    unrealized_pnl_percent: number;
    risk_score: number;
  }>;
  total_positions: number;
}

interface RiskAlert {
  id: string;
  type: string;
  title: string;
  message: string;
  timestamp: string;
  priority: string;
  color: string;
}

interface Recommendation {
  id: string;
  type: string;
  title: string;
  description: string;
  priority: string;
  action: string;
}

export default function RiskDashboard() {
  const [portfolioOverview, setPortfolioOverview] = useState<PortfolioOverview | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const [riskMetricsChart, setRiskMetricsChart] = useState<RiskMetricsChart | null>(null);
  const [positionPerformanceChart, setPositionPerformanceChart] = useState<PositionPerformanceChart | null>(null);
  const [riskAlerts, setRiskAlerts] = useState<RiskAlert[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPosition, setSelectedPosition] = useState<string | null>(null);

  useEffect(() => {
    loadRiskData();
  }, []);

  const loadRiskData = async () => {
    try {
      setLoading(true);
      
      const [
        overviewRes,
        positionsRes,
        metricsRes,
        performanceRes,
        alertsRes,
        recommendationsRes
      ] = await Promise.all([
        fetch('/data/risk_portfolio_overview.json'),
        fetch('/data/risk_positions.json'),
        fetch('/data/risk_metrics_chart.json'),
        fetch('/data/risk_position_performance.json'),
        fetch('/data/risk_alerts.json'),
        fetch('/data/risk_recommendations.json')
      ]);

      const overviewData = await overviewRes.json();
      const positionsData = await positionsRes.json();
      const metricsData = await metricsRes.json();
      const performanceData = await performanceRes.json();
      const alertsData = await alertsRes.json();
      const recommendationsData = await recommendationsRes.json();

      setPortfolioOverview(overviewData);
      setPositions(positionsData);
      setRiskMetricsChart(metricsData);
      setPositionPerformanceChart(performanceData);
      setRiskAlerts(alertsData);
      setRecommendations(recommendationsData);
      
    } catch (error) {
      console.error('リスクデータの読み込みエラー:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('ja-JP', {
      style: 'currency',
      currency: 'JPY',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPercent = (value: number) => {
    return `${value.toFixed(2)}%`;
  };

  const getRiskLevelIcon = (riskLevel: string) => {
    switch (riskLevel) {
      case 'LOW':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'MEDIUM':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      case 'HIGH':
        return <AlertTriangle className="h-4 w-4 text-orange-500" />;
      case 'CRITICAL':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'HIGH':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'LOW':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* ヘッダー */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">🛡️ リスク管理ダッシュボード</h1>
          <p className="text-gray-600">現在のポジション状況、損切りライン、リスクレベルを可視化</p>
        </div>

        {/* ポートフォリオ概要 */}
        {portfolioOverview && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">ポートフォリオ価値</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatCurrency(portfolioOverview.portfolio_value)}</div>
                <p className="text-xs text-muted-foreground">
                  未実現損益: {formatCurrency(portfolioOverview.total_unrealized_pnl)}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">リスクレベル</CardTitle>
                <Shield className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="flex items-center space-x-2">
                  {getRiskLevelIcon(portfolioOverview.risk_level)}
                  <span className="text-2xl font-bold" style={{ color: portfolioOverview.risk_color }}>
                    {portfolioOverview.risk_level}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground">
                  リスクスコア: {portfolioOverview.risk_score.toFixed(2)}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">最大ドローダウン</CardTitle>
                <TrendingDown className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">
                  {formatPercent(portfolioOverview.max_drawdown * 100)}
                </div>
                <p className="text-xs text-muted-foreground">
                  VaR (95%): {formatCurrency(portfolioOverview.var_95)}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">シャープレシオ</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{portfolioOverview.sharpe_ratio.toFixed(2)}</div>
                <p className="text-xs text-muted-foreground">
                  リスク調整後リターン
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* アラート */}
        {riskAlerts.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4">⚠️ リスクアラート</h2>
            <div className="space-y-3">
              {riskAlerts.map((alert) => (
                <Alert key={alert.id} style={{ borderColor: alert.color }}>
                  <AlertTriangle className="h-4 w-4" style={{ color: alert.color }} />
                  <AlertTitle>{alert.title}</AlertTitle>
                  <AlertDescription>{alert.message}</AlertDescription>
                </Alert>
              ))}
            </div>
          </div>
        )}

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">概要</TabsTrigger>
            <TabsTrigger value="positions">ポジション</TabsTrigger>
            <TabsTrigger value="risk-metrics">リスク指標</TabsTrigger>
            <TabsTrigger value="recommendations">推奨事項</TabsTrigger>
          </TabsList>

          {/* 概要タブ */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* リスク指標チャート */}
              {riskMetricsChart && (
                <Card>
                  <CardHeader>
                    <CardTitle>リスク指標推移</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <AreaChart data={riskMetricsChart.dates.map((date, index) => ({
                        date,
                        risk_score: riskMetricsChart.risk_scores[index],
                        portfolio_value: riskMetricsChart.portfolio_values[index]
                      }))}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis yAxisId="left" />
                        <YAxis yAxisId="right" orientation="right" />
                        <Tooltip />
                        <Area
                          yAxisId="left"
                          type="monotone"
                          dataKey="risk_score"
                          stroke="#ef4444"
                          fill="#ef4444"
                          fillOpacity={0.3}
                          name="リスクスコア"
                        />
                        <Line
                          yAxisId="right"
                          type="monotone"
                          dataKey="portfolio_value"
                          stroke="#10b981"
                          name="ポートフォリオ価値"
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              )}

              {/* ポジション分布 */}
              <Card>
                <CardHeader>
                  <CardTitle>ポジション分布</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={positions.map(pos => ({
                          name: pos.symbol,
                          value: pos.weight,
                          color: pos.pnl_color
                        }))}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {positions.map((pos, index) => (
                          <Cell key={`cell-${index}`} fill={pos.pnl_color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* ポジションタブ */}
          <TabsContent value="positions" className="space-y-6">
            <div className="grid grid-cols-1 gap-6">
              {/* ポジション一覧 */}
              <Card>
                <CardHeader>
                  <CardTitle>現在のポジション</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {positions.map((position) => (
                      <div
                        key={position.symbol}
                        className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
                        onClick={() => setSelectedPosition(selectedPosition === position.symbol ? null : position.symbol)}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <div>
                              <h3 className="font-semibold">{position.symbol}</h3>
                              <p className="text-sm text-gray-600">{position.company_name}</p>
                            </div>
                            <Badge variant="outline" style={{ borderColor: position.risk_color, color: position.risk_color }}>
                              {position.risk_level}
                            </Badge>
                          </div>
                          <div className="text-right">
                            <div className="font-semibold" style={{ color: position.pnl_color }}>
                              {formatCurrency(position.unrealized_pnl)}
                            </div>
                            <div className="text-sm text-gray-600">
                              {formatPercent(position.unrealized_pnl_percent)}
                            </div>
                          </div>
                        </div>
                        
                        {selectedPosition === position.symbol && (
                          <div className="mt-4 pt-4 border-t grid grid-cols-2 gap-4">
                            <div>
                              <p className="text-sm text-gray-600">エントリー価格</p>
                              <p className="font-semibold">{formatCurrency(position.entry_price)}</p>
                            </div>
                            <div>
                              <p className="text-sm text-gray-600">現在価格</p>
                              <p className="font-semibold">{formatCurrency(position.current_price)}</p>
                            </div>
                            <div>
                              <p className="text-sm text-gray-600">損切り価格</p>
                              <p className="font-semibold text-red-600">{formatCurrency(position.stop_loss_price)}</p>
                            </div>
                            <div>
                              <p className="text-sm text-gray-600">利確価格</p>
                              <p className="font-semibold text-green-600">{formatCurrency(position.take_profit_price)}</p>
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* ポジションパフォーマンスチャート */}
              {positionPerformanceChart && selectedPosition && (
                <Card>
                  <CardHeader>
                    <CardTitle>{selectedPosition} パフォーマンス</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {(() => {
                      const selectedPosData = positionPerformanceChart.positions.find(
                        pos => pos.symbol === selectedPosition
                      );
                      if (!selectedPosData) return null;

                      return (
                        <ResponsiveContainer width="100%" height={400}>
                          <LineChart data={selectedPosData.dates.map((date, index) => ({
                            date,
                            price: selectedPosData.prices[index],
                            stop_loss: selectedPosData.stop_loss_line[index],
                            take_profit: selectedPosData.take_profit_line[index]
                          }))}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" />
                            <YAxis />
                            <Tooltip />
                            <Line
                              type="monotone"
                              dataKey="price"
                              stroke="#3b82f6"
                              strokeWidth={2}
                              name="価格"
                            />
                            <Line
                              type="monotone"
                              dataKey="stop_loss"
                              stroke="#ef4444"
                              strokeDasharray="5 5"
                              name="損切りライン"
                            />
                            <Line
                              type="monotone"
                              dataKey="take_profit"
                              stroke="#10b981"
                              strokeDasharray="5 5"
                              name="利確ライン"
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      );
                    })()}
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* リスク指標タブ */}
          <TabsContent value="risk-metrics" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* ドローダウン分析 */}
              {riskMetricsChart && (
                <Card>
                  <CardHeader>
                    <CardTitle>ドローダウン分析</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <AreaChart data={riskMetricsChart.dates.map((date, index) => ({
                        date,
                        drawdown: riskMetricsChart.drawdowns[index] * 100
                      }))}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip formatter={(value) => [`${value}%`, 'ドローダウン']} />
                        <Area
                          type="monotone"
                          dataKey="drawdown"
                          stroke="#ef4444"
                          fill="#ef4444"
                          fillOpacity={0.3}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              )}

              {/* リスクスコア分布 */}
              <Card>
                <CardHeader>
                  <CardTitle>ポジション別リスクスコア</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={positions.map(pos => ({
                      symbol: pos.symbol,
                      risk_score: pos.risk_score,
                      color: pos.risk_color
                    }))}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="symbol" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="risk_score" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* 推奨事項タブ */}
          <TabsContent value="recommendations" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>リスク管理推奨事項</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recommendations.map((rec) => (
                    <div key={rec.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-semibold text-lg">{rec.title}</h3>
                          <p className="text-gray-600 mt-1">{rec.description}</p>
                          <p className="text-sm text-blue-600 mt-2 font-medium">{rec.action}</p>
                        </div>
                        <Badge className={getPriorityColor(rec.priority)}>
                          {rec.priority}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
