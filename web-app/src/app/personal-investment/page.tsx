"use client";

import React, { useState, useEffect } from "react";

// 動的レンダリングを強制
export const dynamic = "force-dynamic";
import { getLatestIndex, resolveBusinessDate, swrJson } from "@/lib/dataClient";
import UserProfileForm from "@/components/personalization/UserProfileForm";
import { useUserProfile } from "@/contexts/UserProfileContext";
import { allocateEqualRiskBudget, AllocationResult, Candidate } from "@/lib/personalization/allocation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  ArrowUp,
  ArrowDown,
  Minus,
  Star,
  Activity,
  Shield,
  RefreshCw,
  Info,
  AlertTriangle,
  Settings,
} from "lucide-react";
import { RiskSettingsPanel } from "@/components/risk-customization/RiskSettingsPanel";
import { PersonalInvestmentLSTM } from "@/components/PersonalInvestmentLSTM";
import RealtimePnLCalculator from "@/components/RealtimePnLCalculator";
import InvestmentRecommendationEngine from "@/components/InvestmentRecommendationEngine";
import { EnhancedProfitLossDisplay } from "@/components/EnhancedProfitLossDisplay";
import { ProfitLossChart } from "@/components/ProfitLossChart";
import { PerformanceComparison } from "@/components/PerformanceComparison";
// import { IndividualStockSettings } from "@/components/risk-customization/IndividualStockSettings";
// import { RecommendationDetails } from "@/components/risk-customization/RecommendationDetails";

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
  yearly_pnl?: number;
  best_performer: string;
  worst_performer: string;
  risk_adjusted_return: number;
  sharpe_ratio?: number;
  max_drawdown?: number;
  volatility?: number;
  win_rate?: number;
  profit_factor?: number;
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
  weight?: number;
  contribution?: number;
  sector?: string;
  market_cap?: number;
  volume?: number;
  volatility?: number;
  beta?: number;
  pe_ratio?: number;
  dividend_yield?: number;
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

interface PerformanceData {
  date: string;
  total_value: number;
  daily_pnl: number;
  cumulative_pnl: number;
  benchmark_return?: number;
  volume?: number;
  volatility?: number;
}

interface DashboardData {
  timestamp: string;
  pnl_summary: PnLSummary;
  positions: PositionSummary[];
  recommendations: InvestmentRecommendation[];
  market_overview: MarketOverview;
  performance_data?: PerformanceData[];
  last_update?: string;
}

export default function PersonalInvestmentDashboard() {
  const { profile } = useUserProfile();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [allocation, setAllocation] = useState<AllocationResult | null>(null);
  
  // カスタマイズ機能の状態
  const [showRiskSettings, setShowRiskSettings] = useState(false);
  const [showIndividualStockSettings, setShowIndividualStockSettings] = useState<string | null>(null);
  const [showRecommendationDetails, setShowRecommendationDetails] = useState<string | null>(null);

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
          { ttlMs: 1000 * 60 * 10, timeoutMs: 6000, retries: 3, retryDelay: 800 },
        );
        data = primary.data;
      } catch (e) {
        const fallback = await swrJson<DashboardData>(
          "personal:dashboard",
          "/data/personal_investment_dashboard.json",
          { ttlMs: 1000 * 60 * 10, timeoutMs: 6000, retries: 2, retryDelay: 800 },
        );
        data = fallback.data;
      }
      if (!data) throw new Error("ダッシュボードデータが空です");
      setDashboardData(data);
      const candidates: Candidate[] = [
        ...data.positions.map((p: any) => ({ symbol: p.symbol, sector: "Unknown", score: Math.max(0.1, p.confidence || 0.5) })),
        ...data.recommendations.map((r: any) => ({ symbol: r.symbol, sector: "Unknown", score: Math.max(0.1, r.confidence || 0.6) })),
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
      console.error("ダッシュボードデータの読み込みエラー:", error);
      // 最後の手段: ローカルキャッシュのキー互換確保
      try {
        const cached = localStorage.getItem("app_cache:personal:dashboard");
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
      case "STRONG_BUY":
        return <ArrowUp className="h-4 w-4 text-green-600" />;
      case "BUY":
        return <ArrowUp className="h-4 w-4 text-green-500" />;
      case "HOLD":
        return <Minus className="h-4 w-4 text-gray-500" />;
      case "SELL":
        return <ArrowDown className="h-4 w-4 text-red-500" />;
      case "STRONG_SELL":
        return <ArrowDown className="h-4 w-4 text-red-600" />;
      default:
        return <Minus className="h-4 w-4 text-gray-500" />;
    }
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case "STRONG_BUY":
        return "bg-green-100 text-green-800 border-green-200";
      case "BUY":
        return "bg-green-50 text-green-700 border-green-100";
      case "HOLD":
        return "bg-gray-100 text-gray-700 border-gray-200";
      case "SELL":
        return "bg-red-50 text-red-700 border-red-100";
      case "STRONG_SELL":
        return "bg-red-100 text-red-800 border-red-200";
      default:
        return "bg-gray-100 text-gray-700 border-gray-200";
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "CRITICAL":
        return "bg-red-100 text-red-800 border-red-200";
      case "HIGH":
        return "bg-orange-100 text-orange-800 border-orange-200";
      case "MEDIUM":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "LOW":
        return "bg-blue-100 text-blue-800 border-blue-200";
      default:
        return "bg-gray-100 text-gray-700 border-gray-200";
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case "HIGH":
        return "text-red-600";
      case "MEDIUM":
        return "text-yellow-600";
      case "LOW":
        return "text-green-600";
      default:
        return "text-gray-600";
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
    <div className="container mx-auto p-4 space-y-4">
      {/* ヘッダー - コンパクト化 */}
      <div className="flex justify-between items-center bg-white rounded-lg shadow-sm p-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">個人投資ダッシュボード</h1>
          <p className="text-sm text-gray-600">投資判断に直結する情報を優先表示</p>
        </div>
        <div className="flex space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowRiskSettings(true)}
            title="リスク管理設定を開く"
            aria-label="リスク管理設定を開く"
            data-help="リスク管理設定パネルを開きます。リスク許容度、投資期間、セクター設定などをカスタマイズできます。個人の投資方針に合わせてシステムの動作を最適化し、より精度の高い投資判断を実現できます。"
          >
            <Settings className="h-4 w-4 mr-1" />
            設定
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={loadDashboardData}
            disabled={loading}
            title="最新のダッシュボードデータを取得します"
            aria-label="ダッシュボードを更新"
            data-help="最新のダッシュボードデータを取得します。損益状況、保有銘柄、投資推奨、市場概況などの情報を再取得します。リアルタイムで投資状況を監視し、重要な投資判断に必要な最新情報を確認できます。"
          >
            <RefreshCw className={`h-4 w-4 mr-1 ${loading ? "animate-spin" : ""}`} />
            更新
          </Button>
          <Button
            variant={autoRefresh ? "default" : "outline"}
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
            title="30秒ごとに自動更新。再クリックで切替"
            aria-label={autoRefresh ? "自動更新を停止" : "自動更新を開始"}
            data-help={autoRefresh ? "30秒ごとの自動更新を停止します。手動更新に切り替わります。バッテリー消費を抑えたい場合や、更新頻度を制御したい場合に使用します。" : "30秒ごとに自動更新を開始します。リアルタイムで投資状況を監視できます。市場の急激な変動や重要な投資判断が必要な状況を継続的に監視できます。"}
          >
            <Activity className="h-4 w-4 mr-1" />
            自動更新
          </Button>
        </div>
      </div>

      {/* 損益サマリー - 一目瞭然な表示 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* 総投資額 */}
        <Card className="bg-blue-50 border-blue-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-blue-800">総投資額</CardTitle>
            <DollarSign className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-900">
              ¥{pnl_summary.total_investment.toLocaleString()}
            </div>
          </CardContent>
        </Card>

        {/* 現在価値 */}
        <Card className="bg-green-50 border-green-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-green-800">現在価値</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-900">
              ¥{pnl_summary.current_value.toLocaleString()}
            </div>
          </CardContent>
        </Card>

        {/* 損益 - 最重要表示 */}
        <Card className={`${pnl_summary.unrealized_pnl >= 0 ? "bg-green-50 border-green-200" : "bg-red-50 border-red-200"}`}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className={`text-sm font-medium ${pnl_summary.unrealized_pnl >= 0 ? "text-green-800" : "text-red-800"}`}>
              損益
            </CardTitle>
            {pnl_summary.unrealized_pnl >= 0 ? (
              <TrendingUp className="h-4 w-4 text-green-600" />
            ) : (
              <TrendingDown className="h-4 w-4 text-red-600" />
            )}
          </CardHeader>
          <CardContent>
            <div className={`text-3xl font-bold ${pnl_summary.unrealized_pnl >= 0 ? "text-green-900" : "text-red-900"}`}>
              {pnl_summary.unrealized_pnl >= 0 ? "+" : ""}¥{pnl_summary.unrealized_pnl.toLocaleString()}
            </div>
            <p className={`text-sm font-medium ${pnl_summary.unrealized_pnl >= 0 ? "text-green-700" : "text-red-700"}`}>
              {pnl_summary.unrealized_pnl >= 0 ? "+" : ""}{pnl_summary.pnl_percentage.toFixed(2)}%
            </p>
          </CardContent>
        </Card>

        {/* リスク調整後リターン */}
        <Card className="bg-purple-50 border-purple-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-purple-800">リスク調整後リターン</CardTitle>
            <Shield className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-900">
              {pnl_summary.risk_adjusted_return.toFixed(3)}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 市場概況アラート */}
      {market_overview.market_alert && (
        <Alert className="border-orange-200 bg-orange-50">
          <AlertTriangle className="h-4 w-4 text-orange-600" />
          <AlertTitle className="text-orange-800">市場アラート</AlertTitle>
          <AlertDescription className="text-orange-700">{market_overview.market_alert}</AlertDescription>
        </Alert>
      )}

      {/* クイックアクション - 投資判断に直結する情報 */}
      <div className="bg-white rounded-lg shadow-sm p-4">
        <h2 className="text-lg font-semibold mb-4 text-gray-900">今日の投資判断</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* 緊急アクション */}
          <Card className="border-red-200 bg-red-50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-red-800 flex items-center">
                <AlertTriangle className="h-4 w-4 mr-2" />
                緊急アクション
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {positions.filter(p => p.priority === "CRITICAL" || p.pnl_percentage < -10).map(position => (
                  <div key={position.symbol} className="text-sm">
                    <div className="font-medium text-red-900">{position.symbol}</div>
                    <div className="text-red-700">{position.next_action}</div>
                  </div>
                ))}
                {positions.filter(p => p.priority === "CRITICAL" || p.pnl_percentage < -10).length === 0 && (
                  <div className="text-sm text-gray-600">緊急アクションはありません</div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* 高優先度アクション */}
          <Card className="border-orange-200 bg-orange-50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-orange-800 flex items-center">
                <Star className="h-4 w-4 mr-2" />
                高優先度
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {positions.filter(p => p.priority === "HIGH").map(position => (
                  <div key={position.symbol} className="text-sm">
                    <div className="font-medium text-orange-900">{position.symbol}</div>
                    <div className="text-orange-700">{position.next_action}</div>
                  </div>
                ))}
                {positions.filter(p => p.priority === "HIGH").length === 0 && (
                  <div className="text-sm text-gray-600">高優先度アクションはありません</div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* 推奨アクション */}
          <Card className="border-green-200 bg-green-50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-green-800 flex items-center">
                <TrendingUp className="h-4 w-4 mr-2" />
                推奨アクション
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {recommendations.filter(r => r.priority === "HIGH").slice(0, 3).map(recommendation => (
                  <div key={recommendation.symbol} className="text-sm">
                    <div className="font-medium text-green-900">{recommendation.symbol}</div>
                    <div className="text-green-700">{recommendation.action}</div>
                  </div>
                ))}
                {recommendations.filter(r => r.priority === "HIGH").length === 0 && (
                  <div className="text-sm text-gray-600">推奨アクションはありません</div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview" title="投資成果を3秒で把握" aria-label="投資成果タブ" data-help="投資成果を3秒で把握できます。総投資額、現在価値、損益、リスク調整後リターンなどの重要指標を一覧表示します。">投資成果</TabsTrigger>
          <TabsTrigger value="positions" title="保有銘柄の損益・推奨アクションを確認" aria-label="ポジション一覧タブ" data-help="保有銘柄の損益・推奨アクションを確認できます。各銘柄の現在価格、損益率、次のアクション、目標価格・損切り価格を表示します。">ポジション一覧</TabsTrigger>
          <TabsTrigger value="performance" title="パフォーマンス比較とランキング" aria-label="パフォーマンスタブ" data-help="パフォーマンス比較とランキングを表示します。銘柄別のパフォーマンス、セクター別分析、リスク指標の比較が可能です。">パフォーマンス</TabsTrigger>
          <TabsTrigger value="charts" title="損益推移グラフとチャート分析" aria-label="チャート分析タブ" data-help="損益推移グラフとチャート分析を表示します。時系列での損益推移、ベンチマーク比較、ボラティリティ分析を確認できます。">チャート分析</TabsTrigger>
          <TabsTrigger value="realtime" title="リアルタイム損益計算と価格更新" aria-label="リアルタイム損益タブ" data-help="リアルタイム損益計算と価格更新を行います。最新の株価データに基づいて損益を自動計算し、価格変動を監視できます。">リアルタイム損益</TabsTrigger>
          <TabsTrigger value="recommendations" title="AI/ルールベースによる投資提案" aria-label="投資推奨タブ" data-help="AI/ルールベースによる投資提案を表示します。機械学習とルールベースの分析に基づく投資判断とアクションプランを確認できます。">投資推奨</TabsTrigger>
          <TabsTrigger value="engine" title="自動投資推奨エンジン" aria-label="推奨エンジンタブ" data-help="自動投資推奨エンジンを表示します。リアルタイムで市場データを分析し、最適な投資判断を自動生成します。">推奨エンジン</TabsTrigger>
          <TabsTrigger value="lstm" title="LSTM深層学習による株価予測" aria-label="LSTM予測タブ" data-help="LSTM深層学習による株価予測を表示します。時系列データを学習した深層学習モデルによる高精度な株価予測を確認できます。">LSTM予測</TabsTrigger>
          <TabsTrigger value="market" title="市場全体のトレンドやボラティリティを確認" aria-label="市場概況タブ" data-help="市場全体のトレンドやボラティリティを確認できます。市場トレンド、セクター別パフォーマンス、重要イベントなどの市場情報を表示します。">市場概況</TabsTrigger>
          <TabsTrigger value="personalize" title="プロフィールに応じた推奨配分を作成" aria-label="パーソナライズタブ" data-help="プロフィールに応じた推奨配分を作成できます。リスク許容度、投資期間、好みのセクターに基づいて最適な投資配分を提案します。">パーソナライズ</TabsTrigger>
        </TabsList>

        {/* 投資成果 - 強化された損益表示 */}
        <TabsContent value="overview" className="space-y-4">
          <EnhancedProfitLossDisplay
            pnlSummary={{
              ...pnl_summary,
              yearly_pnl: pnl_summary.yearly_pnl || 0,
              sharpe_ratio: pnl_summary.sharpe_ratio || 0,
              max_drawdown: pnl_summary.max_drawdown || 0,
              volatility: pnl_summary.volatility || 0,
              win_rate: pnl_summary.win_rate || 0,
              profit_factor: pnl_summary.profit_factor || 0,
              best_performer: typeof pnl_summary.best_performer === "string" ? {
                symbol: pnl_summary.best_performer.split(" ")[0] || "-",
                symbolName: pnl_summary.best_performer.split(" ")[1] || pnl_summary.best_performer,
                return: 0,
                value: 0,
              } : (pnl_summary as any).best_performer,
              worst_performer: typeof pnl_summary.worst_performer === "string" ? {
                symbol: pnl_summary.worst_performer.split(" ")[0] || "-",
                symbolName: pnl_summary.worst_performer.split(" ")[1] || pnl_summary.worst_performer,
                return: 0,
                value: 0,
              } : (pnl_summary as any).worst_performer,
            }}
            performanceData={dashboardData.performance_data || []}
            positions={positions.map(p => ({
              symbol: p.symbol,
              symbolName: p.company_name,
              current_value: p.total_value,
              cost_basis: p.cost_basis,
              unrealized_pnl: p.unrealized_pnl,
              pnl_percentage: p.pnl_percentage,
              weight: p.weight || 0,
              contribution: p.contribution || 0,
              risk_level: p.risk_level,
              sector: p.sector || "その他",
              market_cap: p.market_cap,
              volume: p.volume,
              volatility: p.volatility,
              beta: p.beta,
              pe_ratio: p.pe_ratio,
              dividend_yield: p.dividend_yield,
            }))}
            onRefresh={loadDashboardData}
            isLoading={loading}
            autoRefresh={autoRefresh}
            onAutoRefreshToggle={setAutoRefresh}
          />
        </TabsContent>

        {/* パフォーマンス比較 */}
        <TabsContent value="performance" className="space-y-4">
          <PerformanceComparison
            positions={positions.map(p => ({
              symbol: p.symbol,
              symbolName: p.company_name,
              current_value: p.total_value,
              cost_basis: p.cost_basis,
              unrealized_pnl: p.unrealized_pnl,
              pnl_percentage: p.pnl_percentage,
              weight: p.weight || 0,
              contribution: p.contribution || 0,
              risk_level: p.risk_level,
              sector: p.sector || "その他",
              market_cap: p.market_cap,
              volume: p.volume,
              volatility: p.volatility,
              beta: p.beta,
              pe_ratio: p.pe_ratio,
              dividend_yield: p.dividend_yield,
            }))}
            onPositionClick={(symbol) => {
              console.log("Position clicked:", symbol);
            }}
          />
        </TabsContent>

        {/* チャート分析 */}
        <TabsContent value="charts" className="space-y-4">
          <ProfitLossChart
            data={dashboardData.performance_data || []}
            height={500}
            showBenchmark={true}
            showVolume={true}
            showVolatility={true}
            onDataPointClick={(data) => {
              console.log("Data point clicked:", data);
            }}
          />
        </TabsContent>

        {/* ポジション一覧 - 改善された表示 */}
        <TabsContent value="positions" className="space-y-4">
          <div className="grid gap-3">
            {positions.map((position) => (
              <Card key={position.symbol} className={`hover:shadow-md transition-shadow ${
                position.priority === "CRITICAL" ? "border-red-300 bg-red-50" :
                position.priority === "HIGH" ? "border-orange-300 bg-orange-50" :
                "border-gray-200"
              }`}>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div>
                        <h3 className="font-semibold text-lg">{position.symbol}</h3>
                        <p className="text-sm text-gray-600">{position.company_name}</p>
                      </div>
                      <Badge className={getActionColor(position.action_recommendation)}>
                        {getActionIcon(position.action_recommendation)}
                        <span className="ml-1">{position.action_recommendation}</span>
                      </Badge>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-bold">
                        ¥{position.current_price.toLocaleString()}
                      </div>
                      <div className={`text-lg font-semibold ${position.pnl_percentage >= 0 ? "text-green-600" : "text-red-600"}`}>
                        {position.pnl_percentage >= 0 ? "+" : ""}{position.pnl_percentage.toFixed(2)}%
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
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
                      <p className={`font-medium ${position.unrealized_pnl >= 0 ? "text-green-600" : "text-red-600"}`}>
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
                  
                  {/* 次のアクション - 強調表示 */}
                  <div className={`p-4 rounded-lg ${
                    position.priority === "CRITICAL" ? "bg-red-100 border-red-200" :
                    position.priority === "HIGH" ? "bg-orange-100 border-orange-200" :
                    "bg-blue-100 border-blue-200"
                  }`}>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <p className="text-sm font-semibold">次のアクション</p>
                        <Badge className={getPriorityColor(position.priority)}>
                          {position.priority}
                        </Badge>
                      </div>
                    </div>
                    <p className="text-sm font-medium mb-3">{position.next_action}</p>
                    
                    {(position.target_price || position.stop_loss) && (
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        {position.target_price && (
                          <div className="bg-white p-2 rounded">
                            <p className="text-gray-600">目標価格</p>
                            <p className="font-medium text-green-700">¥{position.target_price.toLocaleString()}</p>
                          </div>
                        )}
                        {position.stop_loss && (
                          <div className="bg-white p-2 rounded">
                            <p className="text-gray-600">損切り価格</p>
                            <p className="font-medium text-red-700">¥{position.stop_loss.toLocaleString()}</p>
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

        {/* リアルタイム損益計算 */}
        <TabsContent value="realtime" className="space-y-4">
          <RealtimePnLCalculator
            positions={positions.map(p => ({
              ...p,
              last_updated: new Date().toISOString(),
            }))}
            onPnLUpdate={(updatedPositions) => {
              console.log("リアルタイム損益更新:", updatedPositions);
            }}
            refreshInterval={30000}
          />
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
                        {recommendation.expected_return ? `${(recommendation.expected_return * 100).toFixed(1)}%` : "N/A"}
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
                  
                  {/* アクションボタン */}
                  <div className="mt-4 flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setShowRecommendationDetails(recommendation.symbol)}
                      className="flex-1"
                      aria-label="詳細理由を表示"
                      data-help="この推奨の詳細理由を表示します。AI分析の根拠、テクニカル指標、ファンダメンタル分析の詳細を確認できます。投資判断の信頼性を高めるため、推奨アクションの根拠となる分析結果を詳細に確認できます。"
                    >
                      <Info className="h-4 w-4 mr-1" />
                      詳細理由
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setShowIndividualStockSettings(recommendation.symbol)}
                      className="flex-1"
                      aria-label="個別設定を開く"
                      data-help="この銘柄の個別設定を開きます。リスク設定、目標価格、損切り価格、投資比率などをカスタマイズできます。個人の投資方針に合わせて銘柄ごとの投資戦略を最適化できます。"
                    >
                      <Settings className="h-4 w-4 mr-1" />
                      個別設定
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* 投資推奨エンジン */}
        <TabsContent value="engine" className="space-y-4">
          <InvestmentRecommendationEngine
            positions={positions}
            marketData={positions.map(p => ({
              symbol: p.symbol,
              price: p.current_price,
              volume: 1000,
              volatility: 0.02,
              rsi: 50,
              macd: 0,
              sma_20: p.current_price * 0.98,
              sma_50: p.current_price * 0.95,
              trend: "up" as const,
              momentum: 0.1,
            }))}
            onRecommendationUpdate={(newRecommendations) => {
              console.log("推奨更新:", newRecommendations);
            }}
            refreshInterval={60000}
          />
        </TabsContent>

        {/* LSTM予測 */}
        <TabsContent value="lstm" className="space-y-4">
          <PersonalInvestmentLSTM
            symbol="7203"
            symbolName="トヨタ自動車"
            currentPrice={pnl_summary.current_value / (positions.length || 1)}
            onPredictionComplete={(prediction) => {
              console.log("LSTM予測完了:", prediction);
            }}
          />
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
                    {market_overview.market_trend === "上昇" ? (
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
                    <span className={`text-sm font-medium ${performance >= 0 ? "text-green-600" : "text-red-600"}`}>
                      {performance >= 0 ? "+" : ""}{(performance * 100).toFixed(2)}%
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

      {/* リスク設定モーダル */}
      {showRiskSettings && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <RiskSettingsPanel onClose={() => setShowRiskSettings(false)} />
            </div>
          </div>
        </div>
      )}

      {/* 個別銘柄設定モーダル - 一時的に無効化 */}
      {false && showIndividualStockSettings && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              {/* <IndividualStockSettings
                symbol={showIndividualStockSettings}
                currentPrice={positions.find(p => p.symbol === showIndividualStockSettings)?.current_price || 0}
                onClose={() => setShowIndividualStockSettings(null)}
              /> */}
              <div>個別銘柄設定（開発中）</div>
            </div>
          </div>
        </div>
      )}

      {/* 推奨詳細モーダル - 一時的に無効化 */}
      {false && showRecommendationDetails && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              {/* <RecommendationDetails
                symbol={showRecommendationDetails}
                action={recommendations.find(r => r.symbol === showRecommendationDetails)?.action || 'HOLD'}
                confidence={recommendations.find(r => r.symbol === showRecommendationDetails)?.confidence || 0}
                currentPrice={positions.find(p => p.symbol === showRecommendationDetails)?.current_price || 0}
                targetPrice={recommendations.find(r => r.symbol === showRecommendationDetails)?.target_price}
                stopLossPrice={recommendations.find(r => r.symbol === showRecommendationDetails)?.stop_loss}
                expectedReturn={recommendations.find(r => r.symbol === showRecommendationDetails)?.expected_return}
                riskScore={recommendations.find(r => r.symbol === showRecommendationDetails)?.risk_score}
                onClose={() => setShowRecommendationDetails(null)}
              /> */}
              <div>推奨詳細（開発中）</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
