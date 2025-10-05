"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  CheckCircle, 
  DollarSign,
  PieChart,
  BarChart3,
  Calendar,
  Target,
  Shield,
} from "lucide-react";

interface NisaQuotaStatus {
  growth_investment: {
    annual_limit: number;
    tax_free_limit: number;
    used_amount: number;
    available_amount: number;
    utilization_rate: number;
  };
  accumulation_investment: {
    annual_limit: number;
    tax_free_limit: number;
    used_amount: number;
    available_amount: number;
    utilization_rate: number;
  };
  quota_reuse: {
    growth_available: number;
    accumulation_available: number;
    next_year_available: number;
  };
}

interface NisaPosition {
  symbol: string;
  symbol_name: string;
  quantity: number;
  average_price: number;
  current_price: number;
  cost: number;
  current_value: number;
  unrealized_profit_loss: number;
  quota_type: string;
  purchase_date: string;
}

interface NisaPortfolio {
  positions: NisaPosition[];
  total_value: number;
  total_cost: number;
  unrealized_profit_loss: number;
  realized_profit_loss: number;
  tax_free_profit_loss: number;
}

interface NisaAlert {
  type: string;
  message: string;
  quota_type: string;
  current_usage: number;
  threshold: number;
  recommended_action: string;
  priority: string;
}

interface NisaDashboard {
  quota_status: NisaQuotaStatus;
  portfolio: NisaPortfolio;
  alerts: NisaAlert[];
  last_updated: string;
}

export default function NisaDashboard() {
  const [dashboard, setDashboard] = useState<NisaDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadNisaData();
  }, []);

  const loadNisaData = async () => {
    try {
      setLoading(true);
      // 実際の実装では、APIからデータを取得
      const mockData: NisaDashboard = {
        quota_status: {
          growth_investment: {
            annual_limit: 2400000,
            tax_free_limit: 12000000,
            used_amount: 1200000,
            available_amount: 1200000,
            utilization_rate: 50.0,
          },
          accumulation_investment: {
            annual_limit: 400000,
            tax_free_limit: 2000000,
            used_amount: 200000,
            available_amount: 200000,
            utilization_rate: 50.0,
          },
          quota_reuse: {
            growth_available: 100000,
            accumulation_available: 50000,
            next_year_available: 150000,
          },
        },
        portfolio: {
          positions: [
            {
              symbol: "7203",
              symbol_name: "トヨタ自動車",
              quantity: 100,
              average_price: 2500,
              current_price: 2600,
              cost: 250000,
              current_value: 260000,
              unrealized_profit_loss: 10000,
              quota_type: "GROWTH",
              purchase_date: "2024-01-15",
            },
            {
              symbol: "6758",
              symbol_name: "ソニーグループ",
              quantity: 10,
              average_price: 12000,
              current_price: 12500,
              cost: 120000,
              current_value: 125000,
              unrealized_profit_loss: 5000,
              quota_type: "ACCUMULATION",
              purchase_date: "2024-02-01",
            },
          ],
          total_value: 385000,
          total_cost: 370000,
          unrealized_profit_loss: 15000,
          realized_profit_loss: 0,
          tax_free_profit_loss: 15000,
        },
        alerts: [
          {
            type: "INFO",
            message: "成長投資枠の使用率が50%に達しています",
            quota_type: "GROWTH",
            current_usage: 50.0,
            threshold: 80.0,
            recommended_action: "残りの枠を有効活用することを検討してください",
            priority: "MEDIUM",
          },
        ],
        last_updated: new Date().toISOString(),
      };
      
      setDashboard(mockData);
    } catch (err) {
      setError("データの読み込みに失敗しました");
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("ja-JP", {
      style: "currency",
      currency: "JPY",
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  const getQuotaStatusColor = (utilizationRate: number) => {
    if (utilizationRate >= 95) return "text-red-600";
    if (utilizationRate >= 80) return "text-yellow-600";
    return "text-green-600";
  };

  const getQuotaStatusBadge = (utilizationRate: number) => {
    if (utilizationRate >= 95) return <Badge variant="destructive">クリティカル</Badge>;
    if (utilizationRate >= 80) return <Badge variant="secondary">警告</Badge>;
    return <Badge variant="default">正常</Badge>;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">NISAデータを読み込み中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Alert className="max-w-md">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  if (!dashboard) return null;

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">新NISA管理ダッシュボード</h1>
          <p className="text-gray-600 mt-2">2024年1月開始の新NISA制度に対応した投資枠管理</p>
        </div>
        <div className="text-sm text-gray-500">
          最終更新: {new Date(dashboard.last_updated).toLocaleString("ja-JP")}
        </div>
      </div>

      {/* アラート表示 */}
      {dashboard.alerts.length > 0 && (
        <div className="space-y-2">
          {dashboard.alerts.map((alert, index) => (
            <Alert key={index} className={alert.type === "CRITICAL" ? "border-red-200 bg-red-50" : "border-yellow-200 bg-yellow-50"}>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                <div className="flex items-center justify-between">
                  <span>{alert.message}</span>
                  <Badge variant={alert.priority === "HIGH" ? "destructive" : "secondary"}>
                    {alert.priority}
                  </Badge>
                </div>
              </AlertDescription>
            </Alert>
          ))}
        </div>
      )}

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">概要</TabsTrigger>
          <TabsTrigger value="quotas">枠管理</TabsTrigger>
          <TabsTrigger value="portfolio">ポートフォリオ</TabsTrigger>
          <TabsTrigger value="tax">税務計算</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* 枠利用状況サマリー */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">成長投資枠</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-2xl font-bold">
                      {formatCurrency(dashboard.quota_status.growth_investment.used_amount)}
                    </span>
                    {getQuotaStatusBadge(dashboard.quota_status.growth_investment.utilization_rate)}
                  </div>
                  <div className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span>使用率</span>
                      <span className={getQuotaStatusColor(dashboard.quota_status.growth_investment.utilization_rate)}>
                        {formatPercentage(dashboard.quota_status.growth_investment.utilization_rate)}
                      </span>
                    </div>
                    <Progress 
                      value={dashboard.quota_status.growth_investment.utilization_rate} 
                      className="h-2"
                    />
                    <div className="flex justify-between text-sm text-gray-600">
                      <span>利用可能: {formatCurrency(dashboard.quota_status.growth_investment.available_amount)}</span>
                      <span>年間枠: {formatCurrency(dashboard.quota_status.growth_investment.annual_limit)}</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">つみたて投資枠</CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-2xl font-bold">
                      {formatCurrency(dashboard.quota_status.accumulation_investment.used_amount)}
                    </span>
                    {getQuotaStatusBadge(dashboard.quota_status.accumulation_investment.utilization_rate)}
                  </div>
                  <div className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span>使用率</span>
                      <span className={getQuotaStatusColor(dashboard.quota_status.accumulation_investment.utilization_rate)}>
                        {formatPercentage(dashboard.quota_status.accumulation_investment.utilization_rate)}
                      </span>
                    </div>
                    <Progress 
                      value={dashboard.quota_status.accumulation_investment.utilization_rate} 
                      className="h-2"
                    />
                    <div className="flex justify-between text-sm text-gray-600">
                      <span>利用可能: {formatCurrency(dashboard.quota_status.accumulation_investment.available_amount)}</span>
                      <span>年間枠: {formatCurrency(dashboard.quota_status.accumulation_investment.annual_limit)}</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* ポートフォリオサマリー */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <PieChart className="h-5 w-5" />
                ポートフォリオサマリー
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {formatCurrency(dashboard.portfolio.total_value)}
                  </div>
                  <div className="text-sm text-gray-600">現在価値</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {formatCurrency(dashboard.portfolio.total_cost)}
                  </div>
                  <div className="text-sm text-gray-600">投資額</div>
                </div>
                <div className="text-center">
                  <div className={`text-2xl font-bold ${dashboard.portfolio.unrealized_profit_loss >= 0 ? "text-green-600" : "text-red-600"}`}>
                    {formatCurrency(dashboard.portfolio.unrealized_profit_loss)}
                  </div>
                  <div className="text-sm text-gray-600">未実現損益</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="quotas" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>枠利用状況詳細</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* 成長投資枠詳細 */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">成長投資枠</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {formatCurrency(dashboard.quota_status.growth_investment.used_amount)}
                    </div>
                    <div className="text-sm text-gray-600">使用済み</div>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {formatCurrency(dashboard.quota_status.growth_investment.available_amount)}
                    </div>
                    <div className="text-sm text-gray-600">利用可能</div>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">
                      {formatCurrency(dashboard.quota_status.growth_investment.annual_limit)}
                    </div>
                    <div className="text-sm text-gray-600">年間枠</div>
                  </div>
                  <div className="text-center p-4 bg-orange-50 rounded-lg">
                    <div className="text-2xl font-bold text-orange-600">
                      {formatCurrency(dashboard.quota_status.growth_investment.tax_free_limit)}
                    </div>
                    <div className="text-sm text-gray-600">非課税保有限度額</div>
                  </div>
                </div>
              </div>

              {/* つみたて投資枠詳細 */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">つみたて投資枠</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {formatCurrency(dashboard.quota_status.accumulation_investment.used_amount)}
                    </div>
                    <div className="text-sm text-gray-600">使用済み</div>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {formatCurrency(dashboard.quota_status.accumulation_investment.available_amount)}
                    </div>
                    <div className="text-sm text-gray-600">利用可能</div>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">
                      {formatCurrency(dashboard.quota_status.accumulation_investment.annual_limit)}
                    </div>
                    <div className="text-sm text-gray-600">年間枠</div>
                  </div>
                  <div className="text-center p-4 bg-orange-50 rounded-lg">
                    <div className="text-2xl font-bold text-orange-600">
                      {formatCurrency(dashboard.quota_status.accumulation_investment.tax_free_limit)}
                    </div>
                    <div className="text-sm text-gray-600">非課税保有限度額</div>
                  </div>
                </div>
              </div>

              {/* 枠再利用状況 */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">枠再利用状況</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-yellow-50 rounded-lg">
                    <div className="text-2xl font-bold text-yellow-600">
                      {formatCurrency(dashboard.quota_status.quota_reuse.growth_available)}
                    </div>
                    <div className="text-sm text-gray-600">成長枠再利用可能</div>
                  </div>
                  <div className="text-center p-4 bg-yellow-50 rounded-lg">
                    <div className="text-2xl font-bold text-yellow-600">
                      {formatCurrency(dashboard.quota_status.quota_reuse.accumulation_available)}
                    </div>
                    <div className="text-sm text-gray-600">つみたて枠再利用可能</div>
                  </div>
                  <div className="text-center p-4 bg-yellow-50 rounded-lg">
                    <div className="text-2xl font-bold text-yellow-600">
                      {formatCurrency(dashboard.quota_status.quota_reuse.next_year_available)}
                    </div>
                    <div className="text-sm text-gray-600">翌年利用可能</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="portfolio" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>保有ポジション</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {dashboard.portfolio.positions.map((position, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <h4 className="font-semibold">{position.symbol_name}</h4>
                        <p className="text-sm text-gray-600">{position.symbol}</p>
                      </div>
                      <Badge variant={position.quota_type === "GROWTH" ? "default" : "secondary"}>
                        {position.quota_type === "GROWTH" ? "成長投資枠" : "つみたて投資枠"}
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <div className="text-gray-600">数量</div>
                        <div className="font-semibold">{position.quantity}株</div>
                      </div>
                      <div>
                        <div className="text-gray-600">平均取得価格</div>
                        <div className="font-semibold">{formatCurrency(position.average_price)}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">現在価格</div>
                        <div className="font-semibold">{formatCurrency(position.current_price)}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">損益</div>
                        <div className={`font-semibold ${position.unrealized_profit_loss >= 0 ? "text-green-600" : "text-red-600"}`}>
                          {formatCurrency(position.unrealized_profit_loss)}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tax" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                税務計算・最適化
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="text-center p-6 bg-green-50 rounded-lg">
                  <div className="text-3xl font-bold text-green-600 mb-2">
                    {formatCurrency(dashboard.portfolio.tax_free_profit_loss)}
                  </div>
                  <div className="text-lg text-gray-600">非課税枠内の損益</div>
                  <div className="text-sm text-gray-500 mt-2">
                    税務メリット: 約{formatCurrency(dashboard.portfolio.tax_free_profit_loss * 0.3)}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 border rounded-lg">
                    <h4 className="font-semibold mb-2">成長投資枠の税務効果</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>投資額</span>
                        <span>{formatCurrency(dashboard.quota_status.growth_investment.used_amount)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>推定税務節約</span>
                        <span className="text-green-600">
                          {formatCurrency(dashboard.quota_status.growth_investment.used_amount * 0.3)}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="p-4 border rounded-lg">
                    <h4 className="font-semibold mb-2">つみたて投資枠の税務効果</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>投資額</span>
                        <span>{formatCurrency(dashboard.quota_status.accumulation_investment.used_amount)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>推定税務節約</span>
                        <span className="text-green-600">
                          {formatCurrency(dashboard.quota_status.accumulation_investment.used_amount * 0.3)}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}