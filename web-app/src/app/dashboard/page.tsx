"use client";

import { useEffect, useState, Suspense } from "react";

// 動的レンダリングを強制
export const dynamic = "force-dynamic";
import { ErrorBoundary } from "react-error-boundary";
import dynamicImport from "next/dynamic";
import { SettingsProvider } from "../../contexts/SettingsContext";
import { useAnalysisWithSettings } from "../../hooks/useAnalysisWithSettings";
import { useFiveMinRoutine } from "@/hooks/useFiveMinRoutine";
import { useRealDashboardData } from "@/hooks/useRealDashboardData";
import { TrendingUp, TrendingDown, BarChart3, Target, Database, CheckCircle, Play, Settings, RefreshCw, BookOpen, Shield, AlertTriangle, X, DollarSign, User, HelpCircle, Clock, Cpu, Info } from "lucide-react";
import { MODEL_DEFINITIONS } from "@/data/modelDefinitions";
import { getCacheMeta } from "@/lib/fetcher";
import { freshnessManager, DataFreshnessInfo } from "@/lib/data-freshness-manager";
import DataFreshnessBadge, { DataFreshnessSummary } from "@/components/DataFreshnessBadge";
import DataTimestampDisplay, { DataTimestampSummary } from "@/components/DataTimestampDisplay";
import CacheVisualization, { CacheVisualizationCompact } from "@/components/CacheVisualization";
import EnhancedRefreshButton, { RefreshButtonGroup } from "@/components/EnhancedRefreshButton";
import { NotificationService } from "@/lib/notification/NotificationService";
import UnifiedErrorHandler from "@/components/UnifiedErrorHandler";
import { getErrorInfo, logError } from "@/lib/error-handler";
import { errorLogger, setupGlobalErrorHandling } from "@/lib/error-logger";
import { performanceMonitor, usePerformanceMonitor } from "@/lib/performance-monitor";
import { useGuideShortcuts } from "@/lib/guide/shortcut";
import { enrichWithIndicators, sliceByRange } from "@/lib/indicators";
import { guideStore } from "@/lib/guide/guideStore";
import { parseToJst } from "@/lib/datetime";
import JQuantsAdapter from "@/lib/jquants-adapter";
import { DEFAULT_CHECKLIST_ITEMS, type ChecklistItem } from "@/components/guide/Checklist";
import FirstTimeTutorial from "@/components/FirstTimeTutorial";
import { SampleDataProvider, useSampleData } from "@/components/SampleDataProvider";
import EnhancedDataUpdateManager from "@/components/EnhancedDataUpdateManager";
import AnalysisExecutionPanel from "@/components/AnalysisExecutionPanel";
import LoadingOverlay from "@/components/LoadingOverlay";
import AnalysisGuide from "@/components/AnalysisGuide";
import ModelDetailModal from "@/components/ModelDetailModal";
import ChartDataErrorBoundary from "@/components/ChartDataErrorBoundary";
import InfiniteLoopProtection from "@/components/InfiniteLoopProtection";
import { ChartDataProviderOverride } from "@/components/ChartDataProviderOverride";
import { ChartDataProviderKiller } from "@/components/ChartDataProviderKiller";
import FeatureAnalysisPanel from "@/components/FeatureAnalysisPanel";
import { DataPlaceholder, MetricPlaceholder, ChartPlaceholder } from "@/components/PlaceholderComponents";
import TutorialSystem from "@/components/TutorialSystem";

// 動的インポートでコンポーネントを遅延読み込み
const Navigation = dynamicImport(() => import("../../components/Navigation"), { ssr: false });
const MobileNavigation = dynamicImport(() => import("../../components/MobileNavigation"), { ssr: false });
const BottomNav = dynamicImport(() => import("../../components/mobile/BottomNav"), { ssr: false });
const MobileDashboard = dynamicImport(() => import("../../components/MobileDashboard"), { ssr: false });
const MobileOptimizedDashboard = dynamicImport(() => import("../../components/MobileOptimizedDashboard"), { ssr: false });
const PullToRefresh = dynamicImport(() => import("../../components/PullToRefresh"), { ssr: false });
const SymbolSelector = dynamicImport(() => import("../../components/SymbolSelector"), { ssr: false });
const SymbolAnalysisResults = dynamicImport(() => import("../../components/SymbolAnalysisResults"), { ssr: false });
const OneClickAnalysis = dynamicImport(() => import("../../components/OneClickAnalysis"), { ssr: false });
const StockMonitoringManager = dynamicImport(() => import("../../components/StockMonitoringManager"), { ssr: false });
const RealtimeSignalDisplay = dynamicImport(() => import("../../components/RealtimeSignalDisplay"), { ssr: false });
const NotificationSettings = dynamicImport(() => import("../../components/NotificationSettings"), { ssr: false });
const MobileFirstDashboard = dynamicImport(() => import("../../components/MobileFirstDashboard"), { ssr: false });
const WatchlistManager = dynamicImport(() => import("../../components/WatchlistManager"), { ssr: false });
const JudgmentPanel = dynamicImport(() => import("../../components/JudgmentPanel"), { ssr: false });
const PeriodSelector = dynamicImport(() => import("../../components/PeriodSelector"), { ssr: false });
const ParallelUpdateManager = dynamicImport(() => import("../../components/ParallelUpdateManager"), { ssr: false });
const RoutineDashboard = dynamicImport(() => import("../../components/RoutineDashboard"), { ssr: false });
const SideDetailPanel = dynamicImport(() => import("@/components/SideDetailPanel"), { ssr: false });
const EnhancedErrorHandler = dynamicImport(() => import("../../components/EnhancedErrorHandler"), { ssr: false });
const ChartErrorBoundary = dynamicImport(() => import("../../components/ChartErrorBoundary"), { ssr: false });
const Tooltip = dynamicImport(() => import("../../components/Tooltip").then(mod => ({ default: mod.default })), { ssr: false });
const UserGuide = dynamicImport(() => import("../../components/UserGuide"), { ssr: false });
const TourProvider = dynamicImport(() => import("../../components/guide/TourProvider").then(mod => ({ default: mod.TourProvider })), { ssr: false });
const MetricTooltip = dynamicImport(() => import("../../components/guide/Tooltip").then(mod => ({ default: mod.MetricTooltip })), { ssr: false });
const SimpleTooltip = dynamicImport(() => import("../../components/guide/Tooltip").then(mod => ({ default: mod.SimpleTooltip })), { ssr: false });
const Checklist = dynamicImport(() => import("../../components/guide/Checklist"), { ssr: false });
const ChecklistBadge = dynamicImport(() => import("../../components/guide/Checklist").then(mod => ({ default: mod.ChecklistBadge })), { ssr: false });
const GlossaryModal = dynamicImport(() => import("../../components/guide/GlossaryModal"), { ssr: false });
const HelpModal = dynamicImport(() => import("../../components/guide/HelpModal"), { ssr: false });
const NextUpdateIndicator = dynamicImport(() => import("@/components/NextUpdateIndicator"), { ssr: false });

// 型定義
interface StockData {
  date: string
  code?: string
  open?: number
  high?: number
  low?: number
  close?: number
  volume?: number
  sma_5?: number
  sma_10?: number
  sma_25?: number
  sma_50?: number
}

interface ModelComparison {
  name: string
  type: string
  mae: number
  mse: number
  rmse: number
  r2: number
  rank: number
}

// ChecklistItem型は@/components/guide/Checklistからインポート

interface CacheMeta {
  summary?: { exists: boolean; timestamp?: number }
  stock?: { exists: boolean; timestamp?: number }
  model?: { exists: boolean; timestamp?: number }
  feature?: { exists: boolean; timestamp?: number }
  pred?: { exists: boolean; timestamp?: number }
  marketInsights?: { exists: boolean; timestamp?: number }
  riskAssessment?: { exists: boolean; timestamp?: number }
}

function DashboardContent() {
  const [activeTab, setActiveTab] = useState("overview");
  const [stockData, setStockData] = useState<StockData[]>([]);
  const [modelComparison, setModelComparison] = useState<ModelComparison[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [performanceMetrics, setPerformanceMetrics] = useState<any>(null);
  const [marketInsights, setMarketInsights] = useState<any>(null);
  const [riskAssessment, setRiskAssessment] = useState<any>(null);
  const [featureAnalysis, setFeatureAnalysis] = useState<any>(null);
  const [lastUpdateTime, setLastUpdateTime] = useState<string>("");
  const [refreshStatus, setRefreshStatus] = useState<string>("");
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [showAnalysisModal, setShowAnalysisModal] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [showStockMonitoring, setShowStockMonitoring] = useState(false);
  const [showModelDetail, setShowModelDetail] = useState(false);
  const [selectedModel, setSelectedModel] = useState<ModelComparison | null>(null);
  const [checklistItems, setChecklistItems] = useState<ChecklistItem[]>(DEFAULT_CHECKLIST_ITEMS);
  const [cacheMeta, setCacheMeta] = useState<CacheMeta>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [freshnessInfos, setFreshnessInfos] = useState<DataFreshnessInfo[]>([]);
  
  // ガイド関連の状態
  // 簡素化のため不要な状態変数を削除

  // パフォーマンス監視
  usePerformanceMonitor("dashboard");

  // ガイドショートカット（簡素化）
  // useGuideShortcuts();

  // 分析フック
  const analysis = useAnalysisWithSettings();

  // 5分ルーティンフック
  const routine = useFiveMinRoutine();

  // 実際のダッシュボードデータフック
  const realDashboard = useRealDashboardData();

  // サンプルデータフック
  const sampleData = useSampleData();

  // 実データ使用フラグ
  const [useRealData, setUseRealData] = useState(true);

  useEffect(() => {
    const initializeDashboard = async () => {
      try {
        setIsLoading(true);
        
        // キャッシュメタデータの取得
        const meta = {
          summary: {
            exists: getCacheMeta("dash:summary").exists,
            timestamp: getCacheMeta("dash:summary").timestamp || undefined,
          },
          stock: {
            exists: getCacheMeta("dash:stock").exists,
            timestamp: getCacheMeta("dash:stock").timestamp || undefined,
          },
          model: {
            exists: getCacheMeta("dash:model").exists,
            timestamp: getCacheMeta("dash:model").timestamp || undefined,
          },
          feature: {
            exists: getCacheMeta("dash:feature").exists,
            timestamp: getCacheMeta("dash:feature").timestamp || undefined,
          },
          pred: {
            exists: getCacheMeta("dash:pred").exists,
            timestamp: getCacheMeta("dash:pred").timestamp || undefined,
          },
          marketInsights: {
            exists: getCacheMeta("dash:marketInsights").exists,
            timestamp: getCacheMeta("dash:marketInsights").timestamp || undefined,
          },
          riskAssessment: {
            exists: getCacheMeta("dash:riskAssessment").exists,
            timestamp: getCacheMeta("dash:riskAssessment").timestamp || undefined,
          },
        };
        setCacheMeta(meta);

        // データの読み込み
        await loadDashboardData();
        
        // 通知サービスの初期化
        const notificationService = NotificationService.getInstance();
        await notificationService.initialize();
        
        // エラーハンドリングの設定（簡素化）
        // setupGlobalErrorHandling();
        
        setIsLoading(false);
      } catch (err) {
        console.error("ダッシュボード初期化エラー:", err);
        setError("ダッシュボードの初期化に失敗しました");
        setIsLoading(false);
      }
    };

    initializeDashboard();
  }, []);

  const loadDashboardData = async () => {
    try {
      // ここで実際のデータ読み込み処理を実装
      // 簡素化のため基本的なデータのみ設定
      setLastUpdateTime(new Date().toLocaleString("ja-JP"));
      
      // 鮮度情報の更新
      updateFreshnessInfos();
    } catch (err) {
      console.error("データ読み込みエラー:", err);
      setError("データの読み込みに失敗しました");
    }
  };

  const updateFreshnessInfos = () => {
    const now = new Date();
    const infos: DataFreshnessInfo[] = [];

    // 各データソースの鮮度情報を生成
    if (cacheMeta.summary?.exists && cacheMeta.summary.timestamp) {
      infos.push(freshnessManager.getFreshnessInfo(
        cacheMeta.summary.timestamp,
        "cache",
        60, // 1時間TTL
      ));
    }

    if (cacheMeta.stock?.exists && cacheMeta.stock.timestamp) {
      infos.push(freshnessManager.getFreshnessInfo(
        cacheMeta.stock.timestamp,
        "cache",
        30, // 30分TTL
      ));
    }

    if (cacheMeta.model?.exists && cacheMeta.model.timestamp) {
      infos.push(freshnessManager.getFreshnessInfo(
        cacheMeta.model.timestamp,
        "cache",
        120, // 2時間TTL
      ));
    }

    if (cacheMeta.feature?.exists && cacheMeta.feature.timestamp) {
      infos.push(freshnessManager.getFreshnessInfo(
        cacheMeta.feature.timestamp,
        "cache",
        60, // 1時間TTL
      ));
    }

    if (cacheMeta.pred?.exists && cacheMeta.pred.timestamp) {
      infos.push(freshnessManager.getFreshnessInfo(
        cacheMeta.pred.timestamp,
        "cache",
        15, // 15分TTL
      ));
    }

    if (cacheMeta.marketInsights?.exists && cacheMeta.marketInsights.timestamp) {
      infos.push(freshnessManager.getFreshnessInfo(
        cacheMeta.marketInsights.timestamp,
        "cache",
        30, // 30分TTL
      ));
    }

    if (cacheMeta.riskAssessment?.exists && cacheMeta.riskAssessment.timestamp) {
      infos.push(freshnessManager.getFreshnessInfo(
        cacheMeta.riskAssessment.timestamp,
        "cache",
        60, // 1時間TTL
      ));
    }

    setFreshnessInfos(infos);
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    setRefreshStatus("更新中...");
    
    try {
      await loadDashboardData();
      setRefreshStatus("更新完了");
      setTimeout(() => setRefreshStatus(""), 2000);
    } catch (err) {
      console.error("更新エラー:", err);
      setRefreshStatus("更新失敗");
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleForceRefresh = async () => {
    setIsRefreshing(true);
    setRefreshStatus("強制更新中...");
    
    try {
      // キャッシュをクリアして強制更新
      await loadDashboardData();
      setRefreshStatus("強制更新完了");
      setTimeout(() => setRefreshStatus(""), 2000);
    } catch (err) {
      console.error("強制更新エラー:", err);
      setRefreshStatus("強制更新失敗");
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleRecompute = async () => {
    setIsRefreshing(true);
    setRefreshStatus("再計算中...");
    
    try {
      // 分析の再実行
      await loadDashboardData();
      setRefreshStatus("再計算完了");
      setTimeout(() => setRefreshStatus(""), 2000);
    } catch (err) {
      console.error("再計算エラー:", err);
      setRefreshStatus("再計算失敗");
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleModelClick = (model: ModelComparison) => {
    setSelectedModel(model);
    setShowModelDetail(true);
  };

  const handleChecklistToggle = (itemId: string) => {
    setChecklistItems(prev => 
      prev.map(item => 
        item.id === itemId 
          ? { ...item, completed: !item.completed }
          : item,
      ),
    );
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">ダッシュボードを読み込み中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">エラーが発生しました</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            再読み込み
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      <ChartDataProviderKiller />
      <ChartDataProviderOverride>
        <InfiniteLoopProtection componentId="dashboard-main">
          <div className="min-h-screen bg-gray-50 pb-20 lg:pb-0">
            {/* モバイルナビゲーション */}
            <MobileNavigation 
              activeTab={activeTab} 
              onTabChange={setActiveTab}
              onAnalysisClick={() => setShowAnalysisModal(true)}
              onSettingsClick={() => setShowSettingsModal(true)}
              onMonitoringClick={() => setShowStockMonitoring(true)}
            />

            {/* デスクトップヘッダー */}
            <header className="hidden lg:block bg-white shadow-sm border-b">
              <div className="w-full px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center py-6">
                  <div data-guide-target="welcome">
                    <h1 className="text-3xl font-bold text-gray-900">J-Quants 株価予測ダッシュボード</h1>
                    <p className="text-gray-600">機械学習による株価予測システム</p>
                  </div>
                  <div className="flex flex-col xl:flex-row items-start xl:items-center space-y-2 xl:space-y-0 xl:space-x-4">
                    {/* システム状況と鮮度表示 */}
                    <div className="flex flex-wrap items-center gap-3">
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="h-5 w-5 text-green-500" />
                        <span className="text-sm text-gray-600">
                          システム: 正常稼働中
                        </span>
                      </div>
                      
                      {/* データ鮮度サマリー */}
                      {freshnessInfos.length > 0 && (
                        <DataFreshnessSummary
                          freshnessInfos={freshnessInfos}
                          onRefreshAll={handleRefresh}
                        />
                      )}
                      
                      {/* キャッシュ状態の可視化 */}
                      {freshnessInfos.length > 0 && (
                        <CacheVisualization
                          freshnessInfos={freshnessInfos}
                          showDetails={false}
                          onRefreshAll={handleRefresh}
                          className="hidden xl:block"
                        />
                      )}
                    </div>
                    
                    {/* 更新ボタン群 */}
                    <div className="flex items-center gap-2">
                      <EnhancedRefreshButton
                        onRefresh={useRealData ? realDashboard.actions.refresh : handleRefresh}
                        onForceRefresh={useRealData ? realDashboard.actions.refresh : handleForceRefresh}
                        onRecompute={useRealData ? realDashboard.actions.refresh : handleRecompute}
                        isLoading={useRealData ? realDashboard.isLoading : isRefreshing}
                        lastRefresh={useRealData 
                          ? (realDashboard.lastUpdated ? new Date(realDashboard.lastUpdated) : undefined)
                          : (lastUpdateTime ? new Date(lastUpdateTime) : undefined)
                        }
                        refreshInterval={5} // 5分間隔で自動更新
                        variant="default"
                        size="md"
                        showProgress={true}
                        showLastRefresh={true}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </header>

            {/* メインコンテンツ */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
              {/* タブナビゲーション */}
              <div className="mb-8">
                <nav className="flex space-x-8" aria-label="Tabs">
                  {[
                    { id: "overview", name: "概要", icon: BarChart3 },
                    { id: "analysis", name: "分析", icon: Target },
                    { id: "models", name: "モデル", icon: Cpu },
                    { id: "predictions", name: "予測", icon: TrendingUp },
                  ].map((tab) => {
                    const Icon = tab.icon;
                    return (
                      <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                          activeTab === tab.id
                            ? "border-blue-500 text-blue-600"
                            : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                        }`}
                      >
                        <Icon className="h-4 w-4" />
                        <span>{tab.name}</span>
                      </button>
                    );
                  })}
                </nav>
              </div>

              {/* データソース切り替えボタン */}
              <div className="mb-6 flex justify-center">
                <div className="bg-white rounded-lg p-2 shadow-sm border flex">
                  <button
                    onClick={() => setUseRealData(true)}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                      useRealData 
                        ? "bg-blue-600 text-white" 
                        : "text-gray-600 hover:text-gray-900"
                    }`}
                  >
                    実データ (JQuants)
                  </button>
                  <button
                    onClick={() => setUseRealData(false)}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                      !useRealData 
                        ? "bg-blue-600 text-white" 
                        : "text-gray-600 hover:text-gray-900"
                    }`}
                  >
                    サンプルデータ
                  </button>
                </div>
              </div>

              {/* タブコンテンツ */}
              {activeTab === "overview" && (
                <div className="space-y-6" data-guide-target="overview">
                  {/* システム状況 */}
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h2 className="text-lg font-semibold text-gray-900">システム状況</h2>
                      {/* 接続ステータス表示（実データモード時） */}
                      {useRealData && realDashboard.connectionStatus && (
                        <div className={`flex items-center px-3 py-1 rounded-lg text-sm ${
                          realDashboard.connectionStatus.success 
                            ? "bg-green-50 text-green-800" 
                            : "bg-red-50 text-red-800"
                        }`}>
                          {realDashboard.connectionStatus.success ? (
                            <CheckCircle className="w-4 h-4 mr-2" />
                          ) : (
                            <AlertTriangle className="w-4 h-4 mr-2" />
                          )}
                          JQuants API: {realDashboard.connectionStatus.success ? "接続中" : "エラー"}
                        </div>
                      )}
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="flex items-center space-x-3">
                        <div className="flex-shrink-0">
                          <CheckCircle className="h-8 w-8 text-green-500" />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900">システム状態</p>
                          <p className="text-sm text-green-600">
                            {useRealData && realDashboard.connectionStatus?.success ? "JQuants接続中" : "正常稼働中"}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <div className="flex-shrink-0">
                          <Database className="h-8 w-8 text-blue-500" />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900">データ更新</p>
                          <p className="text-sm text-gray-600">
                            {useRealData 
                              ? (realDashboard.lastUpdated ? new Date(realDashboard.lastUpdated).toLocaleString("ja-JP") : "未更新")
                              : (lastUpdateTime || "未更新")
                            }
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <div className="flex-shrink-0">
                          <Cpu className="h-8 w-8 text-purple-500" />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900">分析銘柄数</p>
                          <p className="text-sm text-gray-600">
                            {useRealData && realDashboard.marketSummary 
                              ? `${realDashboard.marketSummary.analyzedSymbols}/${realDashboard.marketSummary.totalSymbols}件`
                              : "学習済み"
                            }
                          </p>
                        </div>
                      </div>
                    </div>
                    
                    {/* 実データの場合は市場サマリーを表示 */}
                    {useRealData && realDashboard.marketSummary && (
                      <div className="mt-6 grid grid-cols-2 md:grid-cols-5 gap-4">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-green-600">
                            {realDashboard.marketSummary.recommendations.STRONG_BUY + realDashboard.marketSummary.recommendations.BUY}
                          </div>
                          <div className="text-sm text-gray-600">買い推奨</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-blue-600">
                            {realDashboard.marketSummary.recommendations.HOLD}
                          </div>
                          <div className="text-sm text-gray-600">ホールド</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-red-600">
                            {realDashboard.marketSummary.recommendations.SELL + realDashboard.marketSummary.recommendations.STRONG_SELL}
                          </div>
                          <div className="text-sm text-gray-600">売り推奨</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-green-600">
                            {realDashboard.marketSummary.topGainers.length}
                          </div>
                          <div className="text-sm text-gray-600">上昇銘柄</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-red-600">
                            {realDashboard.marketSummary.topLosers.length}
                          </div>
                          <div className="text-sm text-gray-600">下落銘柄</div>
                        </div>
                      </div>
                    )}
                    
                    {/* 詳細なキャッシュ状態（サンプルデータ時のみ） */}
                    {!useRealData && freshnessInfos.length > 0 && (
                      <div className="mt-6">
                        <CacheVisualization
                          freshnessInfos={freshnessInfos}
                          showDetails={true}
                          onRefreshAll={handleRefresh}
                        />
                      </div>
                    )}
                  </div>

                  {/* パフォーマンス指標 */}
                  {performanceMetrics && (
                    <div className="bg-white rounded-lg shadow p-6">
                      <h2 className="text-lg font-semibold text-gray-900 mb-4">パフォーマンス指標</h2>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <div className="text-center">
                          <p className="text-2xl font-bold text-blue-600">{performanceMetrics.accuracy || "N/A"}%</p>
                          <p className="text-sm text-gray-600">精度</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-green-600">{performanceMetrics.mae || "N/A"}</p>
                          <p className="text-sm text-gray-600">MAE</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-purple-600">{performanceMetrics.rmse || "N/A"}</p>
                          <p className="text-sm text-gray-600">RMSE</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-orange-600">{performanceMetrics.r2 || "N/A"}</p>
                          <p className="text-sm text-gray-600">R²</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* 市場インサイト */}
                  {marketInsights && (
                    <div className="bg-white rounded-lg shadow p-6">
                      <h2 className="text-lg font-semibold text-gray-900 mb-4">市場インサイト</h2>
                      <div className="space-y-3">
                        {marketInsights.trends?.map((trend: any, index: number) => (
                          <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <span className="text-sm text-gray-700">{trend.description}</span>
                            <span className={`text-sm font-medium ${
                              trend.sentiment === "positive" ? "text-green-600" : 
                              trend.sentiment === "negative" ? "text-red-600" : "text-gray-600"
                            }`}>
                              {trend.sentiment === "positive" ? "上昇" : 
                               trend.sentiment === "negative" ? "下降" : "中立"}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {activeTab === "analysis" && (
                <div className="space-y-6" data-guide-target="analysis-features">
                  <div className="bg-white rounded-lg shadow p-6">
                    <h2 className="text-lg font-semibold text-gray-900 mb-4">分析機能</h2>
                    <div className="text-center py-8">
                      <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">分析機能は準備中です</p>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "models" && (
                <div className="space-y-6" data-guide-target="model-comparison">
                  <div className="bg-white rounded-lg shadow p-6">
                    <h2 className="text-lg font-semibold text-gray-900 mb-4">モデル比較</h2>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">モデル名</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">タイプ</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">MAE</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">RMSE</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">R²</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ランク</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {modelComparison.map((model, index) => (
                            <tr key={index} className="hover:bg-gray-50 cursor-pointer" onClick={() => handleModelClick(model)}>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{model.name}</td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{model.type}</td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{model.mae.toFixed(4)}</td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{model.rmse.toFixed(4)}</td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{model.r2.toFixed(4)}</td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                  model.rank === 1 ? "bg-green-100 text-green-800" :
                                  model.rank <= 3 ? "bg-yellow-100 text-yellow-800" :
                                  "bg-gray-100 text-gray-800"
                                }`}>
                                  #{model.rank}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "predictions" && (
                <div className="space-y-6">
                  <div className="bg-white rounded-lg shadow p-6">
                    <h2 className="text-lg font-semibold text-gray-900 mb-4">予測結果</h2>
                    <div className="text-center py-8">
                      <TrendingUp className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">予測機能は準備中です</p>
                    </div>
                  </div>
                </div>
              )}
            </main>

            {/* モーダル */}
            {showAnalysisModal && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
                  <div className="flex justify-between items-center mb-4">
                    <h2 className="text-lg font-semibold">分析実行</h2>
                    <button
                      onClick={() => setShowAnalysisModal(false)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      <X className="h-6 w-6" />
                    </button>
                  </div>
                  <AnalysisExecutionPanel />
                </div>
              </div>
            )}

            {/* モデル詳細モーダル（簡素化のため削除） */}

            {/* 簡素化のため不要なコンポーネントを削除 */}
          </div>
        </InfiniteLoopProtection>
      </ChartDataProviderOverride>
    </>
  );
}

export default function Dashboard() {
  return (
    <ErrorBoundary
      fallbackRender={({ error, resetErrorBoundary }: { error: Error; resetErrorBoundary: () => void }) => (
        <UnifiedErrorHandler
          error={error}
        />
      )}
    >
      <SettingsProvider>
        <SampleDataProvider>
          <TourProvider>
            <Suspense fallback={
              <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-gray-600">読み込み中...</p>
                </div>
              </div>
            }>
              <DashboardContent />
            </Suspense>
          </TourProvider>
        </SampleDataProvider>
      </SettingsProvider>
    </ErrorBoundary>
  );
}
