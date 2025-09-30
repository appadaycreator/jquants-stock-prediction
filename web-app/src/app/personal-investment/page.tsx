"use client";

import React, { useState, useEffect } from 'react';
import { getLatestIndex, resolveBusinessDate, swrJson } from '@/lib/dataClient';
import UserProfileForm from '@/components/personalization/UserProfileForm';
import { useUserProfile } from '@/contexts/UserProfileContext';
import { allocateEqualRiskBudget, AllocationResult, Candidate } from '@/lib/personalization/allocation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
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
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Target,
  AlertTriangle,
  CheckCircle,
  XCircle,
  ArrowUp,
  ArrowDown,
  Minus,
  Star,
  Activity,
  Shield,
  Eye,
  RefreshCw
} from 'lucide-react';

// データ型定義
interface PnLSummary {
  total_investment: number;
  current_value: number;
  unrealized_pnl: number;
  realized_pnl: number;
  total_pnl: number;
  pnl_percentage: number;
  daily_pnl: number;
  weekly_pnl: number;
  monthly_pnl: number;
  best_performer: string;
  worst_performer: string;
  risk_adjusted_return: number;
}

interface PositionSummary {
  symbol: string;
  company_name: string;
  current_price: number;
  quantity: number;
  total_value: number;
  cost_basis: number;
  unrealized_pnl: number;
  pnl_percentage: number;
  action_recommendation: string;
  confidence: number;
  priority: string;
  risk_level: string;
  next_action: string;
  target_price?: number;
  stop_loss?: number;
}

interface InvestmentRecommendation {
  symbol: string;
  action: string;
  confidence: number;
  priority: string;
  reason: string;
  target_price?: number;
  stop_loss?: number;
  position_size?: number;
  expected_return?: number;
  risk_level: string;
  timeframe: string;
}

interface MarketOverview {
  market_trend: string;
  volatility_level: string;
  sentiment_score: number;
  key_events: string[];
  sector_performance: Record<string, number>;
  market_alert?: string;
}

interface DashboardData {
  timestamp: string;
  pnl_summary: PnLSummary;
  positions: PositionSummary[];
  recommendations: InvestmentRecommendation[];
  market_overview: MarketOverview;
  last_update?: string;
}

export default function PersonalInvestmentDashboard() {
  const { profile } = useUserProfile();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPosition, setSelectedPosition] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [allocation, setAllocation] = useState<AllocationResult | null>(null);

  useEffect(() => {
    loadDashboardData();
    
    // 自動更新の設定
    if (autoRefresh) {
      const interval = setInterval(loadDashboardData, 30000); // 30秒ごと
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const latestIndex = await getLatestIndex();
      const ymd = resolveBusinessDate(null, latestIndex);
      // まずは日付付きパスを取得し、404等で失敗した場合は無日付パスにフォールバック
      let data: DashboardData | null = null;
      try {
        const primary = await swrJson<DashboardData>(
          `personal:dashboard:${ymd}`,
          `/data/${ymd}/personal_investment_dashboard.json`,
          { ttlMs: 1000 * 60 * 10, timeoutMs: 6000, retries: 3, retryDelay: 800 }
        );
        data = primary.data;
      } catch (e) {
        const fallback = await swrJson<DashboardData>(
          'personal:dashboard',
          `/data/personal_investment_dashboard.json`,
          { ttlMs: 1000 * 60 * 10, timeoutMs: 6000, retries: 2, retryDelay: 800 }
        );
        data = fallback.data;
      }
      if (!data) throw new Error('ダッシュボードデータが空です');
      setDashboardData(data);
      const candidates: Candidate[] = [
        ...data.positions.map((p: any) => ({ symbol: p.symbol, sector: 'Unknown', score: Math.max(0.1, p.confidence || 0.5) })),
        ...data.recommendations.map((r: any) => ({ symbol: r.symbol, sector: 'Unknown', score: Math.max(0.1, r.confidence || 0.6) }))
      ].filter((v, i, arr) => arr.findIndex(x => x.symbol === v.symbol) === i);

      const alloc = allocateEqualRiskBudget({
        capitalAmount: profile.capitalAmount,
        riskTolerance: profile.riskTolerance,
        preferredSectors: profile.preferredSectors,
        esgPreference: profile.esgPreference,
        maxPositions: profile.maxPositions || 8,
        excludeSymbols: (profile.excludeSymbols || []),
        candidates,
      });
      setAllocation(alloc);
    } catch (error) {
      console.error('ダッシュボードデータの読み込みエラー:', error);
      // 最後の手段: ローカルキャッシュのキー互換確保
      try {
        const cached = localStorage.getItem('app_cache:personal:dashboard');
        if (cached) {
          const parsed = JSON.parse(cached);
          if (parsed && parsed.v) setDashboardData(parsed.v as DashboardData);
        }
      } catch (_) {}
    } finally {
      setLoading(false);
    }
  };

  const getActionIcon = (action: string) => {
    switch (action) {
      case 'STRONG_BUY':
        return <ArrowUp className="h-4 w-4 text-green-600" />;
      case 'BUY':
        return <ArrowUp className="h-4 w-4 text-green-500" />;
      case 'HOLD':
        return <Minus className="h-4 w-4 text-gray-500" />;
      case 'SELL':
        return <ArrowDown className="h-4 w-4 text-red-500" />;
      case 'STRONG_SELL':
        return <ArrowDown className="h-4 w-4 text-red-600" />;
      default:
        return <Minus className="h-4 w-4 text-gray-500" />;
    }
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case 'STRONG_BUY':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'BUY':
        return 'bg-green-50 text-green-700 border-green-100';
      case 'HOLD':
        return 'bg-gray-100 text-gray-700 border-gray-200';
      case 'SELL':
        return 'bg-red-50 text-red-700 border-red-100';
      case 'STRONG_SELL':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'CRITICAL':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'HIGH':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'LOW':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'HIGH':
        return 'text-red-600';
      case 'MEDIUM':
        return 'text-yellow-600';
      case 'LOW':
        return 'text-green-600';
      default:
        return 'text-gray-600';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>ダッシュボードを読み込み中...</p>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertTriangle className="h-8 w-8 text-red-500 mx-auto mb-4" />
          <p>データの読み込みに失敗しました</p>
          <Button onClick={loadDashboardData} className="mt-4">
            再読み込み
          </Button>
        </div>
      </div>
    );
  }

  const { pnl_summary, positions, recommendations, market_overview } = dashboardData;

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* ヘッダー */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">個人投資ダッシュボード</h1>
          <p className="text-gray-600">投資判断に直結する情報を優先表示</p>
        </div>
        <div className="flex space-x-2">
          <Button
            variant="outline"
            onClick={loadDashboardData}
            disabled={loading}
            title="最新のダッシュボードデータを取得します"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            更新
          </Button>
          <Button
            variant={autoRefresh ? "default" : "outline"}
            onClick={() => setAutoRefresh(!autoRefresh)}
            title="30秒ごとに自動更新。再クリックで切替"
          >
            <Activity className="h-4 w-4 mr-2" />
            自動更新
          </Button>
        </div>
      </div>

      {/* 損益サマリー */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">総投資額</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ¥{pnl_summary.total_investment.toLocaleString()}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">現在価値</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ¥{pnl_summary.current_value.toLocaleString()}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">未実現損益</CardTitle>
            {pnl_summary.unrealized_pnl >= 0 ? (
              <TrendingUp className="h-4 w-4 text-green-600" />
            ) : (
              <TrendingDown className="h-4 w-4 text-red-600" />
            )}
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${pnl_summary.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              ¥{pnl_summary.unrealized_pnl.toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">
              {pnl_summary.pnl_percentage.toFixed(2)}%
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">リスク調整後リターン</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {pnl_summary.risk_adjusted_return.toFixed(3)}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 市場概況アラート */}
      {market_overview.market_alert && (
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>市場アラート</AlertTitle>
          <AlertDescription>{market_overview.market_alert}</AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="positions" className="space-y-4">
        <TabsList>
          <TabsTrigger value="positions" title="保有銘柄の損益・推奨アクションを確認">ポジション一覧</TabsTrigger>
          <TabsTrigger value="recommendations" title="AI/ルールベースによる投資提案">投資推奨</TabsTrigger>
          <TabsTrigger value="market" title="市場全体のトレンドやボラティリティを確認">市場概況</TabsTrigger>
          <TabsTrigger value="personalize" title="プロフィールに応じた推奨配分を作成">パーソナライズ</TabsTrigger>
        </TabsList>

        {/* ポジション一覧 */}
        <TabsContent value="positions" className="space-y-4">
          <div className="grid gap-4">
            {positions.map((position) => (
              <Card key={position.symbol} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div>
                        <h3 className="font-semibold">{position.symbol}</h3>
                        <p className="text-sm text-gray-600">{position.company_name}</p>
                      </div>
                      <Badge className={getActionColor(position.action_recommendation)}>
                        {getActionIcon(position.action_recommendation)}
                        <span className="ml-1">{position.action_recommendation}</span>
                      </Badge>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-semibold">
                        ¥{position.current_price.toLocaleString()}
                      </div>
                      <div className={`text-sm ${position.pnl_percentage >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {position.pnl_percentage >= 0 ? '+' : ''}{position.pnl_percentage.toFixed(2)}%
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600">数量</p>
                      <p className="font-medium">{position.quantity.toLocaleString()}株</p>
                    </div>
                    <div>
                      <p className="text-gray-600">評価額</p>
                      <p className="font-medium">¥{position.total_value.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">損益</p>
                      <p className={`font-medium ${position.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        ¥{position.unrealized_pnl.toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-600">リスク</p>
                      <p className={`font-medium ${getRiskColor(position.risk_level)}`}>
                        {position.risk_level}
                      </p>
                    </div>
                  </div>
                  
                  <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium">次のアクション</p>
                        <p className="text-sm text-gray-600">{position.next_action}</p>
                      </div>
                      <Badge className={getPriorityColor(position.priority)}>
                        {position.priority}
                      </Badge>
                    </div>
                    
                    {(position.target_price || position.stop_loss) && (
                      <div className="mt-2 grid grid-cols-2 gap-4 text-sm">
                        {position.target_price && (
                          <div>
                            <p className="text-gray-600">目標価格</p>
                            <p className="font-medium">¥{position.target_price.toLocaleString()}</p>
                          </div>
                        )}
                        {position.stop_loss && (
                          <div>
                            <p className="text-gray-600">損切り価格</p>
                            <p className="font-medium">¥{position.stop_loss.toLocaleString()}</p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* 投資推奨 */}
        <TabsContent value="recommendations" className="space-y-4">
          <div className="grid gap-4">
            {recommendations.map((recommendation, index) => (
              <Card key={index} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div>
                        <h3 className="font-semibold">{recommendation.symbol}</h3>
                        <p className="text-sm text-gray-600">{recommendation.reason}</p>
                      </div>
                      <Badge className={getActionColor(recommendation.action)}>
                        {getActionIcon(recommendation.action)}
                        <span className="ml-1">{recommendation.action}</span>
                      </Badge>
                    </div>
                    <Badge className={getPriorityColor(recommendation.priority)}>
                      {recommendation.priority}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600">信頼度</p>
                      <p className="font-medium">{(recommendation.confidence * 100).toFixed(1)}%</p>
                    </div>
                    <div>
                      <p className="text-gray-600">リスクレベル</p>
                      <p className={`font-medium ${getRiskColor(recommendation.risk_level)}`}>
                        {recommendation.risk_level}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-600">期間</p>
                      <p className="font-medium">{recommendation.timeframe}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">期待リターン</p>
                      <p className="font-medium">
                        {recommendation.expected_return ? `${(recommendation.expected_return * 100).toFixed(1)}%` : 'N/A'}
                      </p>
                    </div>
                  </div>
                  
                  {(recommendation.target_price || recommendation.stop_loss) && (
                    <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        {recommendation.target_price && (
                          <div>
                            <p className="text-gray-600">目標価格</p>
                            <p className="font-medium">¥{recommendation.target_price.toLocaleString()}</p>
                          </div>
                        )}
                        {recommendation.stop_loss && (
                          <div>
                            <p className="text-gray-600">損切り価格</p>
                            <p className="font-medium">¥{recommendation.stop_loss.toLocaleString()}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* 市場概況 */}
        <TabsContent value="market" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>市場トレンド</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center">
                  <div className="text-3xl font-bold mb-2">
                    {market_overview.market_trend === '上昇' ? (
                      <TrendingUp className="h-8 w-8 text-green-600 mx-auto" />
                    ) : (
                      <TrendingDown className="h-8 w-8 text-red-600 mx-auto" />
                    )}
                  </div>
                  <p className="text-lg font-medium">{market_overview.market_trend}</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>ボラティリティ</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center">
                  <div className={`text-3xl font-bold mb-2 ${getRiskColor(market_overview.volatility_level)}`}>
                    {market_overview.volatility_level}
                  </div>
                  <p className="text-sm text-gray-600">市場の変動性</p>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>セクター別パフォーマンス</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {Object.entries(market_overview.sector_performance).map(([sector, performance]) => (
                  <div key={sector} className="flex justify-between items-center">
                    <span className="text-sm font-medium">{sector}</span>
                    <span className={`text-sm font-medium ${performance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {performance >= 0 ? '+' : ''}{(performance * 100).toFixed(2)}%
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {market_overview.key_events.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>重要イベント</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {market_overview.key_events.map((event, index) => (
                    <li key={index} className="flex items-center space-x-2">
                      <Star className="h-4 w-4 text-yellow-500" />
                      <span className="text-sm">{event}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* パーソナライズ */}
        <TabsContent value="personalize" className="space-y-4">
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">ユーザープロファイル</h3>
              <UserProfileForm />
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">推奨配分</h3>
              {!allocation || allocation.items.length === 0 ? (
                <p className="text-sm text-gray-600">条件に合致する候補がありません</p>
              ) : (
                <div className="space-y-3">
                  <div className="text-sm text-gray-600">配分合計: ¥{allocation.totalAllocated.toLocaleString()}</div>
                  <div className="space-y-2">
                    {allocation.items.map(item => (
                      <div key={item.symbol} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <div className="font-medium">{item.symbol}</div>
                        <div className="text-sm text-gray-700">{(item.weight * 100).toFixed(1)}%</div>
                        <div className="text-sm font-semibold">¥{item.amount.toLocaleString()}</div>
                      </div>
                    ))}
                  </div>
                  {allocation.guidance.length > 0 && (
                    <div className="pt-2 border-t">
                      <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                        {allocation.guidance.map((g, idx) => <li key={idx}>{g}</li>)}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
