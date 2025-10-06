import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  BarChart3,
  PieChart,
  Shield,
} from "lucide-react";

interface SimplifiedRiskMetrics {
  risk_level: "low" | "medium" | "high";
  risk_score: number;
  max_loss_amount: number;
  volatility_level: "low" | "medium" | "high";
  color_code: string;
  recommendation: string;
  confidence: number;
  display_text: string;
}

interface PortfolioRiskBalance {
  total_risk_score: number;
  risk_distribution: {
    low: number;
    medium: number;
    high: number;
  };
  color_balance: {
    green: number;
    orange: number;
    red: number;
  };
  overall_recommendation: string;
  risk_counts: {
    low: number;
    medium: number;
    high: number;
  };
  risk_summary: string;
}

interface RiskAlert {
  type: string;
  symbol: string;
  message: string;
  severity: "HIGH" | "MEDIUM" | "LOW";
  risk_score?: number;
  max_loss_amount?: number;
  color_code: string;
}

interface SimplifiedRiskDashboardProps {
  portfolioData?: any;
  accountBalance?: number;
}

export default function SimplifiedRiskDashboard({ 
  portfolioData = {}, 
  accountBalance = 1000000, 
}: SimplifiedRiskDashboardProps) {
  const [riskData, setRiskData] = useState<{
    portfolio_balance: PortfolioRiskBalance;
    stock_risk_data: any[];
    risk_alerts: RiskAlert[];
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRiskData();
  }, [portfolioData, accountBalance]);

  const fetchRiskData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch("/api/risk/simplified", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          portfolio_data: portfolioData,
          account_balance: accountBalance,
        }),
      });

      if (!response.ok) {
        throw new Error("リスクデータの取得に失敗しました");
      }

      const data = await response.json();
      setRiskData(data.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "不明なエラーが発生しました");
    } finally {
      setLoading(false);
    }
  };

  const getRiskLevelIcon = (level: string) => {
    switch (level) {
      case "low":
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case "medium":
        return <AlertTriangle className="h-5 w-5 text-orange-500" />;
      case "high":
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Shield className="h-5 w-5 text-gray-500" />;
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case "low":
        return "bg-green-100 text-green-800 border-green-200";
      case "medium":
        return "bg-orange-100 text-orange-800 border-orange-200";
      case "high":
        return "bg-red-100 text-red-800 border-red-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "HIGH":
        return "bg-red-100 text-red-800 border-red-200";
      case "MEDIUM":
        return "bg-orange-100 text-orange-800 border-orange-200";
      case "LOW":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
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

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert className="border-red-200 bg-red-50">
        <AlertTriangle className="h-4 w-4 text-red-600" />
        <AlertDescription className="text-red-800">
          {error}
        </AlertDescription>
      </Alert>
    );
  }

  if (!riskData) {
    return (
      <Alert>
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          リスクデータが取得できませんでした。
        </AlertDescription>
      </Alert>
    );
  }

  const { portfolio_balance, stock_risk_data, risk_alerts } = riskData;

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">簡素化リスク管理</h2>
          <p className="text-gray-600">個人投資家向けの直感的なリスク表示</p>
        </div>
        <Button onClick={fetchRiskData} variant="outline" size="sm">
          更新
        </Button>
      </div>

      {/* ポートフォリオ全体リスクサマリー */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            ポートフォリオ全体リスク
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* リスクスコア */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">総合リスクスコア</span>
              <span className="text-lg font-bold">{portfolio_balance.total_risk_score.toFixed(1)}</span>
            </div>
            <Progress 
              value={portfolio_balance.total_risk_score} 
              className="h-2"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>低リスク</span>
              <span>中リスク</span>
              <span>高リスク</span>
            </div>
          </div>

          {/* リスク分布 */}
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 mb-1">
                <CheckCircle className="h-4 w-4 text-green-500" />
                <span className="text-sm font-medium">低リスク</span>
              </div>
              <div className="text-2xl font-bold text-green-600">
                {portfolio_balance.risk_counts.low}
              </div>
              <div className="text-xs text-gray-500">
                {((portfolio_balance.risk_distribution.low || 0) * 100).toFixed(1)}%
              </div>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 mb-1">
                <AlertTriangle className="h-4 w-4 text-orange-500" />
                <span className="text-sm font-medium">中リスク</span>
              </div>
              <div className="text-2xl font-bold text-orange-600">
                {portfolio_balance.risk_counts.medium}
              </div>
              <div className="text-xs text-gray-500">
                {((portfolio_balance.risk_distribution.medium || 0) * 100).toFixed(1)}%
              </div>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 mb-1">
                <XCircle className="h-4 w-4 text-red-500" />
                <span className="text-sm font-medium">高リスク</span>
              </div>
              <div className="text-2xl font-bold text-red-600">
                {portfolio_balance.risk_counts.high}
              </div>
              <div className="text-xs text-gray-500">
                {((portfolio_balance.risk_distribution.high || 0) * 100).toFixed(1)}%
              </div>
            </div>
          </div>

          {/* 全体推奨事項 */}
          <Alert className="border-blue-200 bg-blue-50">
            <Shield className="h-4 w-4 text-blue-600" />
            <AlertDescription className="text-blue-800">
              <strong>推奨事項:</strong> {portfolio_balance.overall_recommendation}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>

      {/* リスクアラート */}
      {risk_alerts && risk_alerts.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              リスクアラート
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {risk_alerts.map((alert, index) => (
                <Alert key={index} className="border-l-4" style={{ borderLeftColor: alert.color_code }}>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge className={getSeverityColor(alert.severity)}>
                          {alert.severity}
                        </Badge>
                        <span className="font-medium">{alert.symbol}</span>
                      </div>
                      <AlertDescription>{alert.message}</AlertDescription>
                      {alert.max_loss_amount && (
                        <div className="text-sm text-gray-600 mt-1">
                          最大損失予想額: {formatCurrency(alert.max_loss_amount)}
                        </div>
                      )}
                    </div>
                  </div>
                </Alert>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 銘柄別リスク詳細 */}
      {stock_risk_data && stock_risk_data.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChart className="h-5 w-5" />
              銘柄別リスク詳細
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stock_risk_data.map((stock, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-lg">{stock.symbol}</span>
                      {getRiskLevelIcon(stock.risk_level)}
                    </div>
                    <Badge className={getRiskLevelColor(stock.risk_level)}>
                      {stock.risk_level === "low" ? "低リスク" : 
                       stock.risk_level === "medium" ? "中リスク" : "高リスク"}
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 mb-3">
                    <div>
                      <div className="text-sm text-gray-600">リスクスコア</div>
                      <div className="text-lg font-semibold">{stock.risk_score.toFixed(1)}</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">最大損失予想額</div>
                      <div className="text-lg font-semibold text-red-600">
                        {formatCurrency(stock.max_loss_amount)}
                      </div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 mb-3">
                    <div>
                      <div className="text-sm text-gray-600">ボラティリティ</div>
                      <div className="text-sm font-medium">
                        {stock.volatility_level === "low" ? "低" : 
                         stock.volatility_level === "medium" ? "中" : "高"}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">信頼度</div>
                      <div className="text-sm font-medium">
                        {(stock.confidence * 100).toFixed(1)}%
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-gray-50 rounded p-3">
                    <div className="text-sm text-gray-600 mb-1">推奨アクション</div>
                    <div className="text-sm font-medium">{stock.recommendation}</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 色分け表示の説明 */}
      <Card>
        <CardHeader>
          <CardTitle>リスクレベル色分け説明</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="w-8 h-8 bg-green-500 rounded mx-auto mb-2"></div>
              <div className="text-sm font-medium text-green-600">低リスク</div>
              <div className="text-xs text-gray-500">投資推奨</div>
            </div>
            <div className="text-center">
              <div className="w-8 h-8 bg-orange-500 rounded mx-auto mb-2"></div>
              <div className="text-sm font-medium text-orange-600">中リスク</div>
              <div className="text-xs text-gray-500">注意深く投資</div>
            </div>
            <div className="text-center">
              <div className="w-8 h-8 bg-red-500 rounded mx-auto mb-2"></div>
              <div className="text-sm font-medium text-red-600">高リスク</div>
              <div className="text-xs text-gray-500">投資見送り推奨</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
