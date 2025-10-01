"use client";

import { useEffect, useState, Suspense } from "react";
import { ErrorBoundary } from "react-error-boundary";
import dynamic from "next/dynamic";
import Link from "next/link";
import { SettingsProvider } from "../contexts/SettingsContext";
import { useAnalysisWithSettings } from "../hooks/useAnalysisWithSettings";
import { useFiveMinRoutine } from "@/hooks/useFiveMinRoutine";
import { TrendingUp, TrendingDown, BarChart3, Target, Database, CheckCircle, Play, Settings, RefreshCw, BookOpen, Shield, AlertTriangle, X, DollarSign, User, HelpCircle, Clock, Cpu } from "lucide-react";
import { getCacheMeta } from "@/lib/fetcher";
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
import { DEFAULT_CHECKLIST_ITEMS } from "@/components/guide/Checklist";
import FirstTimeTutorial from "@/components/FirstTimeTutorial";
import { SampleDataProvider, useSampleData } from "@/components/SampleDataProvider";
import EnhancedDataUpdateManager from "@/components/EnhancedDataUpdateManager";
import AnalysisExecutionPanel from "@/components/AnalysisExecutionPanel";
import LoadingOverlay from "@/components/LoadingOverlay";

// 動的インポートでコンポーネントを遅延読み込み
const Navigation = dynamic(() => import("../components/Navigation"), { ssr: false });
const MobileNavigation = dynamic(() => import("../components/MobileNavigation"), { ssr: false });
const BottomNav = dynamic(() => import("../components/mobile/BottomNav"), { ssr: false });
const MobileDashboard = dynamic(() => import("../components/MobileDashboard"), { ssr: false });
const MobileOptimizedDashboard = dynamic(() => import("../components/MobileOptimizedDashboard"), { ssr: false });
const PullToRefresh = dynamic(() => import("../components/PullToRefresh"), { ssr: false });
const SymbolSelector = dynamic(() => import("../components/SymbolSelector"), { ssr: false });
const SymbolAnalysisResults = dynamic(() => import("../components/SymbolAnalysisResults"), { ssr: false });
const OneClickAnalysis = dynamic(() => import("../components/OneClickAnalysis"), { ssr: false });
const StockMonitoringManager = dynamic(() => import("../components/StockMonitoringManager"), { ssr: false });
const RealtimeSignalDisplay = dynamic(() => import("../components/RealtimeSignalDisplay"), { ssr: false });
const NotificationSettings = dynamic(() => import("../components/NotificationSettings"), { ssr: false });
const MobileFirstDashboard = dynamic(() => import("../components/MobileFirstDashboard"), { ssr: false });
const WatchlistManager = dynamic(() => import("../components/WatchlistManager"), { ssr: false });
const JudgmentPanel = dynamic(() => import("../components/JudgmentPanel"), { ssr: false });
const PeriodSelector = dynamic(() => import("../components/PeriodSelector"), { ssr: false });
const ParallelUpdateManager = dynamic(() => import("../components/ParallelUpdateManager"), { ssr: false });
const RoutineDashboard = dynamic(() => import("../components/RoutineDashboard"), { ssr: false });
const SideDetailPanel = dynamic(() => import("@/components/SideDetailPanel"), { ssr: false });
const EnhancedErrorHandler = dynamic(() => import("../components/EnhancedErrorHandler"), { ssr: false });
const ChartErrorBoundary = dynamic(() => import("../components/ChartErrorBoundary"), { ssr: false });
const ButtonTooltip = dynamic(() => import("../components/Tooltip").then(mod => ({ default: mod.ButtonTooltip })), { ssr: false });
const HelpTooltip = dynamic(() => import("../components/Tooltip").then(mod => ({ default: mod.HelpTooltip })), { ssr: false });
const UserGuide = dynamic(() => import("../components/UserGuide"), { ssr: false });
const TourProvider = dynamic(() => import("../components/guide/TourProvider").then(mod => ({ default: mod.TourProvider })), { ssr: false });
const MetricTooltip = dynamic(() => import("../components/guide/Tooltip").then(mod => ({ default: mod.MetricTooltip })), { ssr: false });
const SimpleTooltip = dynamic(() => import("../components/guide/Tooltip").then(mod => ({ default: mod.SimpleTooltip })), { ssr: false });
const Checklist = dynamic(() => import("../components/guide/Checklist"), { ssr: false });
const ChecklistBadge = dynamic(() => import("../components/guide/Checklist").then(mod => ({ default: mod.ChecklistBadge })), { ssr: false });
const GlossaryModal = dynamic(() => import("../components/guide/GlossaryModal"), { ssr: false });
const HelpModal = dynamic(() => import("../components/guide/HelpModal"), { ssr: false });
const JQuantsTokenSetup = dynamic(() => import("@/components/JQuantsTokenSetup"), { ssr: false });
const NextUpdateIndicator = dynamic(() => import("@/components/NextUpdateIndicator"), { ssr: false });

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

interface ChecklistItem {
  id: string
  title: string
  description: string
  completed: boolean
}

interface ChecklistProps {
  items: ChecklistItem[]
  onItemComplete: (id: string) => void
  onItemReset: (id: string) => void
  onComplete: () => void
}

interface FeatureAnalysis {
  feature: string
  importance: number
  percentage: number
}

interface PredictionData {
  index: number
  actual: number
  predicted: number
  error: number
  error_percentage: number
}

interface DashboardSummary {
  total_data_points: number
  prediction_period: string
  best_model: string
  mae: string
  r2: string
  last_updated: string
}

// カラーパレット
const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8", "#82CA9D"];

function DashboardContent() {
  const [activeTab, setActiveTab] = useState("overview");
  const [stockData, setStockData] = useState<StockData[]>([]);
  const [modelComparison, setModelComparison] = useState<ModelComparison[]>([]);
  const [featureAnalysis, setFeatureAnalysis] = useState<FeatureAnalysis[]>([]);
  const [predictions, setPredictions] = useState<PredictionData[]>([]);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [marketInsights, setMarketInsights] = useState<any>(null);
  const [riskAssessment, setRiskAssessment] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showAnalysisModal, setShowAnalysisModal] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [analysisStatus, setAnalysisStatus] = useState("");
  const [selectedSymbols, setSelectedSymbols] = useState<string[]>([]);
  const [showSymbolSelector, setShowSymbolSelector] = useState(false);
  const [showStockMonitoring, setShowStockMonitoring] = useState(false);
  const [monitoredStocks, setMonitoredStocks] = useState<any[]>([]);
  const [monitoringConfig, setMonitoringConfig] = useState<any>(null);
  const [showRealtimeSignals, setShowRealtimeSignals] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  // サイド詳細パネルの状態
  const [sidePanelOpen, setSidePanelOpen] = useState(false);
  const [sidePanelTitle, setSidePanelTitle] = useState<string>("");
  const [sidePanelContent, setSidePanelContent] = useState<React.ReactNode>(null);
  
  // エラーハンドリング状態
  const [error, setError] = useState<Error | null>(null);
  const [isClient, setIsClient] = useState(false);
  
  // パフォーマンス監視
  usePerformanceMonitor("DashboardContent");

  const openSide = (title: string, content: React.ReactNode) => {
    setSidePanelTitle(title);
    setSidePanelContent(content);
    setSidePanelOpen(true);
  };
  const closeSide = () => setSidePanelOpen(false);

  const [showNotificationSettings, setShowNotificationSettings] = useState(false);
  const [showMobileOptimized, setShowMobileOptimized] = useState(false);
  const [showMobileFirst, setShowMobileFirst] = useState(false);
  const [showUserGuide, setShowUserGuide] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedCode, setSelectedCode] = useState<string>("7203.T");
  const [range, setRange] = useState<"5y" | "1y" | "3m" | "1m">("1y");
  const [primaryStock, setPrimaryStock] = useState<any[]>([]);
  const [lastUpdateTime, setLastUpdateTime] = useState<string | null>(null);
  const [modelHealth, setModelHealth] = useState<{ status: "ok" | "warning" | "stop"; reasons?: string[] } | null>(null);
  const [cacheMeta, setCacheMeta] = useState<Record<string, { exists: boolean; timestamp: number | null; ageMs: number | null }>>({});
  const [selectedPeriod, setSelectedPeriod] = useState("1m");
  const [watchlists, setWatchlists] = useState<any[]>([]);
  const [jquantsAdapter, setJquantsAdapter] = useState<JQuantsAdapter | null>(null);
  const [showJQuantsSetup, setShowJQuantsSetup] = useState(false);
  // UI/チャート制御
  const [overviewExpanded, setOverviewExpanded] = useState({ chart: true, models: false, predictions: false });
  const [chartMetric, setChartMetric] = useState<"close" | "sma_5" | "sma_25" | "sma_50" | "volume">("close");
  const [chartRange, setChartRange] = useState<"7" | "30" | "90" | "all">("30");
  // 5分ルーティン
  const routine = useFiveMinRoutine();
  
  // 新機能の状態管理
  const [showFirstTimeTutorial, setShowFirstTimeTutorial] = useState(false);
  const [showAnalysisPanel, setShowAnalysisPanel] = useState(false);
  const [showDataUpdateManager, setShowDataUpdateManager] = useState(false);
  const [loadingOverlay, setLoadingOverlay] = useState<{
    isVisible: boolean;
    title: string;
    message: string;
    progress?: number;
    estimatedTime?: number;
    type?: "loading" | "success" | "error";
    steps?: Array<{ name: string; status: "pending" | "running" | "completed" | "error"; description?: string; }>;
  }>({
    isVisible: false,
    title: "",
    message: "",
  });

  // ガイド機能の状態
  const [showGlossary, setShowGlossary] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  const [checklistItems, setChecklistItems] = useState<ChecklistItem[]>(DEFAULT_CHECKLIST_ITEMS);
  const [showChecklist, setShowChecklist] = useState(false);

  // 設定連携フック
  const { 
    runAnalysisWithSettings, 
    isAnalyzing: settingsAnalyzing, 
    analysisProgress: settingsProgress, 
    analysisStatus: settingsStatus,
    getAnalysisDescription, 
  } = useAnalysisWithSettings();
  const [refreshStatus, setRefreshStatus] = useState<string>("");

  // ガイド機能のハンドラー
  const handleChecklistItemComplete = (itemId: string) => {
    setChecklistItems((prev: ChecklistItem[]) => 
      prev.map((item: ChecklistItem) => 
        item.id === itemId 
          ? { ...item, completed: true }
          : item,
      ),
    );
    guideStore.addChecklistItem(itemId);
  };

  const handleChecklistItemReset = (itemId: string) => {
    setChecklistItems((prev: ChecklistItem[]) => 
      prev.map((item: ChecklistItem) => 
        item.id === itemId 
          ? { ...item, completed: false }
          : item,
      ),
    );
    guideStore.removeChecklistItem(itemId);
  };

  const handleChecklistComplete = () => {
    setShowChecklist(false);
    guideStore.isTourCompleted = true;
  };

  // ショートカット設定
  useGuideShortcuts(
    () => setShowHelp(true),
    () => setShowGlossary(true),
    () => {
      // ツアー開始の処理はTourProvider内で行う
      console.log("ツアー開始");
    },
    () => {
      // 次のステップの処理はTourProvider内で行う
      console.log("次のステップ");
    },
    () => {
      // 前のステップの処理はTourProvider内で行う
      console.log("前のステップ");
    },
    () => {
      // ツアースキップの処理はTourProvider内で行う
      console.log("ツアースキップ");
    },
  );

  // 日時文字列を正規化する関数
  const normalizeDateString = (dateStr: string | undefined): string => {
    try {
      if (!dateStr || dateStr === "undefined" || dateStr === "null") {
        return "2024-01-01"; // デフォルト日付
      }
      
      // 既にYYYY-MM-DD形式の場合はそのまま返す
      if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
        return dateStr;
      }
      
      // YYYYMMDD形式をYYYY-MM-DD形式に変換
      if (/^\d{8}$/.test(dateStr)) {
        return dateStr.replace(/(\d{4})(\d{2})(\d{2})/, "$1-$2-$3");
      }
      
      // その他の形式の場合はDateオブジェクトで解析
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) {
        console.error("Invalid date format:", dateStr);
        return "2024-01-01"; // デフォルト日付
      }
      
      return date.toISOString().split("T")[0];
    } catch (error) {
      console.error("Date normalization error:", error, "Input:", dateStr);
      return "2024-01-01"; // デフォルト日付
    }
  };

  useEffect(() => {
    // クライアントサイドの初期化
    setIsClient(true);
    
    // 強化されたグローバルエラーハンドリングの設定
    setupGlobalErrorHandling();
    
    // パフォーマンス監視の初期化
    console.log("🚀 パフォーマンス監視を開始しました");
    const metrics = performanceMonitor.getMetrics();
    console.log("初期メトリクス:", metrics);
    
    // カスタムエラーハンドリング
    const handleError = (event: ErrorEvent) => {
      console.error("Global error caught:", event.error);
      const errorInfo = getErrorInfo(event.error);
      logError(event.error);
      
      // 詳細なエラーログを記録
      errorLogger.logError(event.error, {
        component: "Dashboard",
        action: "GlobalError",
        state: { isClient, loading, activeTab },
      });
      
      // 重大なエラーの場合は状態を更新
      if (errorInfo.severity === "critical" || errorInfo.severity === "high") {
        setError(event.error);
      }
    };
    
    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      console.error("Unhandled promise rejection:", event.reason);
      const rejectionError = event.reason instanceof Error ? event.reason : new Error(String(event.reason));
      const errorInfo = getErrorInfo(rejectionError);
      logError(rejectionError);
      
      // 詳細なエラーログを記録
      errorLogger.logError(rejectionError, {
        component: "Dashboard",
        action: "UnhandledRejection",
        state: { isClient, loading, activeTab },
      });
      
      if (errorInfo.severity === "critical" || errorInfo.severity === "high") {
        setError(rejectionError);
      }
    };
    
    window.addEventListener("error", handleError);
    window.addEventListener("unhandledrejection", handleUnhandledRejection);
    
    // データ読み込み
    loadData().catch((err) => {
      console.error("Initial data load failed:", err);
      const errorInfo = getErrorInfo(err);
      logError(err);
      
      if (errorInfo.severity === "critical" || errorInfo.severity === "high") {
        setError(err);
      }
    });
    
    // 健全性取得
    fetch("/api/model-health", { cache: "no-cache" })
      .then(r => r.json())
      .then(setModelHealth)
      .catch(() => setModelHealth({ status: "ok" }));
    
    // ガイド再表示ロジック
    try {
      const tourCompleted = localStorage.getItem("guide_tour_completed") === "true";
      const guideDisabled = localStorage.getItem("guide_disabled") === "true";
      const closedThisSession = sessionStorage.getItem("userGuideClosedThisSession") === "true";
      const firstTimeTutorialCompleted = localStorage.getItem("first_time_tutorial_completed") === "true";

      if (!tourCompleted && !guideDisabled && !closedThisSession) {
        setShowUserGuide(true);
      }

      // 初回利用者向けチュートリアルの表示判定
      if (!firstTimeTutorialCompleted && !tourCompleted && !guideDisabled) {
        setShowFirstTimeTutorial(true);
      }
    } catch (e) {
      console.warn("Storage access failed:", e);
      setShowUserGuide(true);
      setShowFirstTimeTutorial(true);
    }
    
    // 初期キャッシュメタ情報の収集
    try {
      setCacheMeta({
        summary: getCacheMeta("dash:summary"),
        stock: getCacheMeta("dash:stock"),
        model: getCacheMeta("dash:model"),
        feature: getCacheMeta("dash:feature"),
        pred: getCacheMeta("dash:pred"),
        marketInsights: getCacheMeta("dash:marketInsights"),
        riskAssessment: getCacheMeta("dash:riskAssessment"),
      });
    } catch (e) {
      console.warn("Cache meta collection failed:", e);
    }
    
    return () => {
      window.removeEventListener("error", handleError);
      window.removeEventListener("unhandledrejection", handleUnhandledRejection);
    };
  }, []);

  // モバイル判定
  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      setShowMobileOptimized(mobile);
      setShowMobileFirst(mobile); // P1のモバイルファースト機能を有効化
    };
    
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  const loadData = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setIsRefreshing(true);
        setRefreshStatus("データを更新しています...");
      } else {
        setLoading(true);
      }
      
      // RSC payloadエラーを防ぐためのリトライ機能付きfetch
      const fetchWithRetry = async (url: string, retries = 3): Promise<Response> => {
        for (let i = 0; i < retries; i++) {
          try {
            const response = await fetch(url, {
              cache: "no-cache",
              headers: {
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
              },
            });
            if (response.ok) {
              return response;
            }
            throw new Error(`HTTP ${response.status}`);
          } catch (error) {
            console.warn(`Fetch attempt ${i + 1} failed for ${url}:`, error);
            if (i === retries - 1) throw error;
            await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
          }
        }
        throw new Error("All retry attempts failed");
      };
      
      // ベースパス解決（fetcher側）が効くように先頭スラッシュで固定
      const dataPath = "/data";
      
      console.log("データパス:", dataPath);
      console.log("環境:", process.env.NODE_ENV);
      
      // キャッシュ対応の安全取得（失敗時はキャッシュから復旧）
      const { fetchManyWithCache } = await import("@/lib/fetcher");
      
      let results, cacheFlags;
      try {
        const fetchResult = await fetchManyWithCache<{
          summary: any;
          stock: any[];
          model: any[];
          feature: any[];
          pred: any[];
          marketInsights: any;
          riskAssessment: any;
        }>({
          summary: { url: `${dataPath}/dashboard_summary.json`, cacheKey: "dash:summary", ttlMs: 1000 * 60 * 30 },
          stock: { url: `${dataPath}/stock_data.json`, cacheKey: "dash:stock", ttlMs: 1000 * 60 * 30 },
          model: { url: `${dataPath}/unified_model_comparison.json`, cacheKey: "dash:model", ttlMs: 1000 * 60 * 30 },
          feature: { url: `${dataPath}/feature_analysis.json`, cacheKey: "dash:feature", ttlMs: 1000 * 60 * 30 },
          pred: { url: `${dataPath}/prediction_results.json`, cacheKey: "dash:pred", ttlMs: 1000 * 60 * 30 },
          marketInsights: { url: `${dataPath}/market_insights.json`, cacheKey: "dash:marketInsights", ttlMs: 1000 * 60 * 30 },
          riskAssessment: { url: `${dataPath}/risk_assessment.json`, cacheKey: "dash:riskAssessment", ttlMs: 1000 * 60 * 30 },
        }, { retries: 2, retryDelay: 800 });
        
        results = fetchResult.results;
        cacheFlags = fetchResult.cacheFlags;
      } catch (fetchError) {
        console.warn("データ取得に失敗、デフォルト値を設定:", fetchError);
        
        // デフォルトデータを設定
        results = {
          summary: {
            total_data_points: 0,
            prediction_period: "-",
            best_model: "-",
            mae: "0",
            r2: "0",
            last_updated: new Date().toISOString(),
          },
          stock: [],
          model: [],
          feature: [],
          pred: [],
          marketInsights: {},
          riskAssessment: {},
        };
        cacheFlags = {
          summary: true,
          stock: true,
          model: true,
          feature: true,
          pred: true,
          marketInsights: true,
          riskAssessment: true,
        };
      }

      const summaryData = results.summary;
      const stockDataRes = results.stock || [];
      const modelDataRes = results.model || [];
      const featureDataRes = results.feature || [];
      const predDataRes = results.pred || [];
      const marketInsightsData = results.marketInsights || {};
      const riskAssessmentData = results.riskAssessment || {};

      // 一部でもキャッシュ復旧が発生した場合は警告を表示
      if (Object.values(cacheFlags).some(Boolean)) {
        console.warn("最新の一部データ取得に失敗したため、キャッシュから復旧しました。");
        // エラー状態は設定しない（ユーザー体験を優先）
      }

      setSummary(summaryData);
      setMarketInsights(marketInsightsData);
      setRiskAssessment(riskAssessmentData);
      
      // 主要チャートデータを公開JSONから取得し、クライアント側で指標を付与
      try {
        const normalizedCode = selectedCode.replace(/\..*$/, "");
        const raw = (stockDataRes || []).filter((r: any) => r && (r.code === selectedCode || r.code === normalizedCode));
        if (raw.length > 0) {
          const enriched = enrichWithIndicators(raw, { todayFinalOnly: true });
          const ranged = sliceByRange(enriched as any, range as any);
          setPrimaryStock(ranged);
        } else {
          setPrimaryStock([]);
        }
      } catch (e) {
        console.warn("client-side indicators failed", e);
        setPrimaryStock([]);
      }
      const now = new Date();
      setLastUpdateTime(now.toLocaleString("ja-JP"));
      try {
        setCacheMeta({
          summary: getCacheMeta("dash:summary"),
          stock: getCacheMeta("dash:stock"),
          model: getCacheMeta("dash:model"),
          feature: getCacheMeta("dash:feature"),
          pred: getCacheMeta("dash:pred"),
          marketInsights: getCacheMeta("dash:marketInsights"),
          riskAssessment: getCacheMeta("dash:riskAssessment"),
        });
      } catch {}
      
      // 日時データを正規化してから設定
      const normalizedStockData = stockDataRes.slice(0, 100).map((item: StockData) => ({
        ...item,
        date: normalizeDateString(item.date || undefined),
      }));
      setStockData(normalizedStockData);
      
      // モデル比較データの構造を変換
      const transformedModelData = modelDataRes.map((model: any) => ({
        name: model.model_name,
        type: model.model_type,
        mae: model.mae,
        mse: model.rmse * model.rmse, // MSEを計算
        rmse: model.rmse,
        r2: model.r2,
        rank: model.rank,
      }));
      setModelComparison(transformedModelData);
      
      // 特徴量分析データが空の場合はサンプルデータを生成
      let featureData = featureDataRes;
      if (!featureData || featureData.length === 0) {
        featureData = [
          { feature: "価格変動率", importance: 0.35, percentage: 35 },
          { feature: "ボリューム", importance: 0.25, percentage: 25 },
          { feature: "RSI", importance: 0.15, percentage: 15 },
          { feature: "移動平均", importance: 0.12, percentage: 12 },
          { feature: "ボリンジャーバンド", importance: 0.08, percentage: 8 },
          { feature: "MACD", importance: 0.05, percentage: 5 },
        ];
      }
      setFeatureAnalysis(featureData);
      setPredictions(predDataRes);
      
    } catch (error) {
      console.error("データの読み込みに失敗:", error);
      
      // エラー時もデフォルトデータを設定してユーザー体験を維持
      setSummary({
        total_data_points: 0,
        prediction_period: "-",
        best_model: "-",
        mae: "0",
        r2: "0",
        last_updated: new Date().toISOString(),
      });
      setStockData([]);
      setModelComparison([]);
      setFeatureAnalysis([]);
      setPredictions([]);
      setMarketInsights({});
      setRiskAssessment({});
      
      // エラーは警告として表示（ページは表示される）
      console.warn("データ読み込みに失敗しましたが、デフォルト表示を継続します。");
      
      // RSC payloadエラーの場合、自動的にリトライ
      if (error instanceof Error && (
        error.message.includes("RSC payload") || 
        error.message.includes("Connection closed") ||
        error.message.includes("Failed to fetch")
      )) {
        console.log("RSC payload error detected, retrying in 3 seconds...");
        setTimeout(() => {
          loadData();
        }, 3000);
      }
    } finally {
      setLoading(false);
      if (isRefresh) {
        setIsRefreshing(false);
        setRefreshStatus("更新完了");
        try {
          const notifier = NotificationService.getInstance();
          await notifier.initializePushNotifications();
          await notifier.notifyAnalysisComplete({
            title: "データ更新完了",
            message: "最新のダッシュボードデータに更新されました",
            timestamp: new Date().toISOString(),
          } as any);
        } catch (e) {
          console.debug("ローカル通知は無効（静的サイト/権限未許可など）");
        }
        // 3秒後にステータスをクリア
        setTimeout(() => {
          setRefreshStatus("");
        }, 3000);
      }
    }
  };

  const runAnalysis = async (symbols?: string[]) => {
    try {
      // 設定連携版の分析実行
      const result = await runAnalysisWithSettings({
        symbols,
        analysisType: "comprehensive",
        useSettings: true,
      });

      if (result.success) {
        // データを再読み込み
        await loadData();
        setShowAnalysisModal(false);
      } else {
        setAnalysisStatus(`分析エラー: ${result.error}`);
      }
      
    } catch (error) {
      console.error("分析実行エラー:", error);
      setAnalysisStatus("分析の実行に失敗しました");
    }
  };

  const handleSymbolAnalysis = async (symbols: string[]) => {
    if (symbols.length === 0) {
      alert("銘柄を選択してください");
      return;
    }
    
    setSelectedSymbols(symbols);
    setShowSymbolSelector(false);
    
    try {
      setIsAnalyzing(true);
      setAnalysisProgress(0);
      setAnalysisStatus("選択された銘柄の分析を開始しています...");
      
      // クライアントサイドでの分析シミュレーション
      // 実際の分析は静的サイトでは実行できないため、シミュレーション
      for (let i = 0; i <= 100; i += 10) {
        setAnalysisProgress(i);
        setAnalysisStatus(`分析進行中... ${i}%`);
        await new Promise(resolve => setTimeout(resolve, 100));
      }
      
      setAnalysisStatus("分析が完了しました。データを更新しています...");
      setAnalysisProgress(100);
      
      // データを再読み込み
      await loadData();
      
      setTimeout(() => {
        setIsAnalyzing(false);
        setAnalysisProgress(0);
        setAnalysisStatus("");
      }, 1000);
      
    } catch (error) {
      console.error("銘柄分析エラー:", error);
      setAnalysisStatus("分析の実行に失敗しました");
      setIsAnalyzing(false);
    }
  };

  const handleMonitoringChange = (stocks: any[]) => {
    setMonitoredStocks(stocks);
  };

  const handleConfigChange = (config: any) => {
    setMonitoringConfig(config);
  };

  // クライアントサイドレンダリング前のフォールバック
  if (!isClient) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">読み込み中...</p>
        </div>
      </div>
    );
  }

  // エラーが発生した場合
  if (error) {
    return (
      <UnifiedErrorHandler
        error={error}
        onRetry={() => {
          setError(null);
          loadData();
        }}
        onDismiss={() => setError(null)}
        showDetails={process.env.NODE_ENV === "development"}
        autoRetry={true}
        maxRetries={3}
      />
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">データを読み込み中...</p>
        </div>
      </div>
    );
  }

  const RangeSelector = () => (
    <div className="flex gap-2 items-center">
      {(["5y","1y","3m","1m"] as const).map(r => (
        <button
          key={r}
          onClick={() => { setRange(r); loadData(true); }}
          className={`px-3 py-1 rounded ${range === r ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-700"}`}
        >
          {r}
        </button>
      ))}
    </div>
  );

  const formatDate = (dateStr: string) => {
    try {
      // Luxonを使用して日付を正規化
      const dt = parseToJst(dateStr);
      
      if (!dt.isValid) {
        console.error("Invalid date format:", dateStr);
        return "2024-01-01"; // デフォルト日付を返す
      }
      
      return dt.toLocaleString({
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
      });
    } catch (error) {
      console.error("Date formatting error:", error, "Input:", dateStr);
      return "2024-01-01"; // デフォルト日付を返す
    }
  };

  const chartData = (primaryStock.length ? primaryStock : stockData).map(item => ({
    date: normalizeDateString(item.date),
    実際価格: item.close,
    SMA_5: item.sma_5 ?? null,
    SMA_25: item.sma_25 ?? null,
    SMA_75: item.sma_75 ?? item.sma_50 ?? null,
    EMA_12: item.ema_12 ?? null,
    EMA_26: item.ema_26 ?? null,
    MACD: item.macd ?? null,
    MACD_Signal: item.macd_signal ?? null,
    MACD_Hist: item.macd_hist ?? null,
    RSI_14: item.rsi_14 ?? null,
    出来高: (item.volume ?? 0) / 1000000,
  }));

  const predictionChartData = predictions.slice(0, 50).map(item => ({
    index: item.index,
    実際値: item.actual,
    予測値: item.predicted,
  }));

  // チャート用データ（N/A防止: データがなければダミー生成）
  const safeStockData = (stockData && stockData.length > 0)
    ? stockData
    : Array.from({ length: 30 }).map((_, i) => ({
        date: normalizeDateString(new Date(Date.now() - (29 - i) * 24 * 3600 * 1000).toISOString()),
        close: 1000 + i * 2,
        sma_5: 1000 + i * 2,
        sma_25: 1000 + i * 2,
        sma_50: 1000 + i * 2,
        volume: 1000000 + i * 5000,
      }));

  const chartFiltered = (() => {
    let data = safeStockData;
    if (chartRange !== "all") {
      const n = parseInt(chartRange, 10);
      data = data.slice(Math.max(0, data.length - n));
    }
    return data;
  })();

  const getMetricValue = (d: any): number | undefined => {
    switch (chartMetric) {
      case "close": return d.close;
      case "sma_5": return d.sma_5;
      case "sma_25": return d.sma_25;
      case "sma_50": return d.sma_50;
      case "volume": return (d.volume ?? 0) / 1000000;
      default: return undefined;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20 lg:pb-0">
      {/* モバイルナビゲーション */}
      <MobileNavigation 
        activeTab={activeTab} 
        onTabChange={setActiveTab}
        onAnalysisClick={() => setShowAnalysisModal(true)}
        onSettingsClick={() => setShowSettingsModal(true)}
        onMonitoringClick={() => setShowStockMonitoring(true)}
      />

      {/* デスクトップナビゲーションはSidebarコンポーネントで処理 */}

      {/* デスクトップヘッダー */}
      <header className="hidden lg:block bg-white shadow-sm border-b">
        <div className="w-full px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div data-guide-target="welcome">
              <h1 className="text-3xl font-bold text-gray-900">J-Quants 株価予測ダッシュボード</h1>
              <p className="text-gray-600">機械学習による株価予測システム</p>
            </div>
            <div className="flex flex-col xl:flex-row items-start xl:items-center space-y-2 xl:space-y-0 xl:space-x-4">
              <div className="flex flex-wrap items-center gap-2">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span className="text-sm text-gray-600">
                    システム: 正常稼働中
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">
                    最終更新: {lastUpdateTime || summary?.last_updated || "-"}
                  </span>
                  {refreshStatus && (
                    <span className="text-sm text-green-600">
                      {refreshStatus}
                    </span>
                  )}
                </div>
              </div>
              <span className="text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-700" title={`summary:${cacheMeta.summary?.timestamp ? new Date(cacheMeta.summary.timestamp).toLocaleString("ja-JP") : "N/A"}\nstock:${cacheMeta.stock?.timestamp ? new Date(cacheMeta.stock.timestamp).toLocaleString("ja-JP") : "N/A"}\nmodel:${cacheMeta.model?.timestamp ? new Date(cacheMeta.model.timestamp).toLocaleString("ja-JP") : "N/A"}\nfeature:${cacheMeta.feature?.timestamp ? new Date(cacheMeta.feature.timestamp).toLocaleString("ja-JP") : "N/A"}\npred:${cacheMeta.pred?.timestamp ? new Date(cacheMeta.pred.timestamp).toLocaleString("ja-JP") : "N/A"}\nmarket:${cacheMeta.marketInsights?.timestamp ? new Date(cacheMeta.marketInsights.timestamp).toLocaleString("ja-JP") : "N/A"}\nrisk:${cacheMeta.riskAssessment?.timestamp ? new Date(cacheMeta.riskAssessment.timestamp).toLocaleString("ja-JP") : "N/A"}`}>
                {Object.values(cacheMeta).some(m => m?.exists) ? "キャッシュ使用中" : "キャッシュなし"}
              </span>
              {/* 本日のモデル健全性バッジ */}
              {modelHealth && (
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                  modelHealth.status === "ok" ? "bg-green-100 text-green-800" :
                  modelHealth.status === "warning" ? "bg-yellow-100 text-yellow-800" :
                  "bg-red-100 text-red-800"
                }`} title={(modelHealth.reasons||[]).join("\n")}>
                  本日のモデル健全性: {modelHealth.status === "ok" ? "OK" : modelHealth.status === "warning" ? "警告" : "停止"}
                </div>
              )}
                <NextUpdateIndicator />
              <div className="flex space-x-2">
                <ButtonTooltip content="特定の銘柄を選択して詳細分析を実行します">
                  <button
                    onClick={() => setShowSymbolSelector(true)}
                    className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Play className="h-4 w-4 mr-2" />
                    銘柄選択・分析
                  </button>
                </ButtonTooltip>
                
                <ButtonTooltip content="全銘柄の包括的な分析を実行します（3-5分程度かかります）">
                  <button
                    onClick={() => setShowAnalysisPanel(true)}
                    disabled={isAnalyzing}
                    className={`flex items-center px-4 py-2 rounded-lg transition-colors ${
                      isAnalyzing 
                        ? "bg-gray-400 cursor-not-allowed" 
                        : "bg-purple-600 hover:bg-purple-700"
                    } text-white`}
                  >
                    <Play className={`h-4 w-4 mr-2 ${isAnalyzing ? "animate-pulse" : ""}`} />
                    {isAnalyzing ? "分析中..." : "全体分析"}
                  </button>
                </ButtonTooltip>
                
                <ButtonTooltip content="分析設定、モデル選択、表示オプションを調整できます">
                  <button
                    onClick={() => setShowSettingsModal(true)}
                    className="flex items-center px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                    data-guide-target="settings-config"
                  >
                    <Settings className="h-4 w-4 mr-2" />
                    設定
                  </button>
                </ButtonTooltip>

                <ButtonTooltip content="J-Quants APIトークンを設定してリアルタイムデータを取得">
                  <button
                    onClick={() => setShowJQuantsSetup(true)}
                    className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                  >
                    <Database className="h-4 w-4 mr-2" />
                    J-Quants設定
                  </button>
                </ButtonTooltip>
                
                <ButtonTooltip content="最新のデータを取得（キャッシュ無視）">
                  <button
                    onClick={() => setShowDataUpdateManager(true)}
                    disabled={isRefreshing}
                    className={`flex items-center px-4 py-2 rounded-lg transition-colors ${
                      isRefreshing 
                        ? "bg-gray-400 cursor-not-allowed" 
                        : "bg-green-600 hover:bg-green-700"
                    } text-white`}
                  >
                    <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? "animate-spin" : ""}`} />
                    {isRefreshing ? "更新中..." : "再取得"}
                  </button>
                </ButtonTooltip>

                <ButtonTooltip content="キャッシュを無視し、分析の再計算を実行します">
                  <button
                    onClick={() => setShowAnalysisModal(true)}
                    className="flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                  >
                    <Cpu className="h-4 w-4 mr-2" />
                    再計算
                  </button>
                </ButtonTooltip>

                {/* ガイド機能ボタン */}
                <div className="flex items-center space-x-2">
                  <ButtonTooltip content="クイックヘルプを表示（F1キー）">
                    <button
                      onClick={() => setShowHelp(true)}
                      className="flex items-center px-3 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
                      data-guide-target="help-support"
                    >
                      <HelpCircle className="h-4 w-4 mr-1" />
                      ヘルプ
                    </button>
                  </ButtonTooltip>

                  <ButtonTooltip content="用語集を表示（Gキー）">
                    <button
                      onClick={() => setShowGlossary(true)}
                      className="flex items-center px-3 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors"
                    >
                      <BookOpen className="h-4 w-4 mr-1" />
                      用語集
                    </button>
                  </ButtonTooltip>
                </div>
                
                <ButtonTooltip content="初回利用者向けの操作ガイドを表示します">
                  <button
                    onClick={() => setShowUserGuide(true)}
                    className="flex items-center px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
                  >
                    <HelpCircle className="h-4 w-4 mr-2" />
                    ガイド
                  </button>
                </ButtonTooltip>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* 1画面主義: タブナビゲーションを撤廃し、ホームで完結 */}

      {/* モバイル最適化ダッシュボード */}
      {showMobileFirst ? (
        <MobileFirstDashboard />
      ) : showMobileOptimized ? (
        <MobileOptimizedDashboard 
          onAnalysisComplete={(result) => {
            console.log("分析完了:", result);
            loadData();
          }}
          onAnalysisStart={() => {
            console.log("分析開始");
          }}
        />
      ) : (
        <div className="lg:hidden p-4">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">J-Quants株価予測システム</h2>
            <p className="text-gray-600 mb-4">モバイル表示を準備中です...</p>
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-semibold text-blue-800">システム情報</h3>
                <p className="text-sm text-blue-700 mt-1">
                  最優秀モデル: {summary?.best_model || "-"}<br/>
                  予測精度: {summary?.r2 || "-"}<br/>
                  データ数: {summary?.total_data_points || "-"}
                </p>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setShowAnalysisModal(true)}
                  className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                >
                  分析実行
                </button>
                <button
                  onClick={() => setShowSettingsModal(true)}
                  className="flex-1 bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700"
                >
                  設定
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* モバイル下部固定ナビ（親指圏の主要操作） */}
      <BottomNav />

      {/* デスクトップメインコンテンツ（4カード＋サイド詳細） */}
      <main className="hidden lg:block w-full px-4 sm:px-6 lg:px-8 py-8" data-guide-target="dashboard-overview">
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 max-w-none">
          {/* 左: 4カード */}
          <div className="xl:col-span-9 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
              {/* 今日のルーティン */}
              <button onClick={() => openSide("今日のルーティン", (
                <div className="space-y-3 text-sm">
                  <div className="text-gray-700">最終更新: {routine.lastUpdated || "N/A"}（{routine.freshnessLabel}）</div>
                  <div className="space-y-2">
                    <div className="font-medium text-gray-900">上位候補</div>
                    <ul className="list-disc pl-4">
                      {(routine.topCandidates || []).slice(0,5).map(c => (
                        <li key={c.symbol}>{c.symbol} {c.recommendation} ({Math.round((c.confidence ?? 0.5)*100)}%)</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))} className="bg-white rounded-lg shadow p-5 text-left w-full">
                <div className="flex items-center">
                  <Clock className="h-6 w-6 text-blue-600" />
                  <div className="ml-3">
                    <p className="text-xs font-medium text-gray-500">今日のルーティン</p>
                    <p className="text-xl font-semibold text-gray-900">{routine.freshnessLabel}</p>
                    <p className="text-xs text-gray-500 mt-1">最終更新: {routine.lastUpdated || "-"}</p>
                  </div>
                </div>
              </button>
              {/* 重要アラート */}
              <button onClick={() => openSide("重要アラート", (
                <div className="space-y-2 text-sm">
                  {(routine.summary?.warnings || []).length > 0 ? (
                    <ul className="list-disc pl-4">
                      {routine.summary?.warnings?.slice(0,10).map((w, i) => (
                        <li key={i}>{w.symbol}: {w.message || "アラート"}</li>
                      ))}
                    </ul>
                  ) : (
                    <div>重要アラートはありません。</div>
                  )}
                </div>
              ))} className="bg-white rounded-lg shadow p-5 text-left w-full">
                <div className="flex items-center">
                  <AlertTriangle className="h-6 w-6 text-yellow-600" />
                  <div className="ml-3">
                    <p className="text-xs font-medium text-gray-500">重要アラート</p>
                    <p className="text-xl font-semibold text-gray-900">{(routine.summary?.warnings || []).length}</p>
                    <p className="text-xs text-gray-500 mt-1">件数</p>
                  </div>
                </div>
              </button>
              {/* リスク状態 */}
              <button onClick={() => openSide("リスク評価", (
                <div className="space-y-3 text-sm">
                  <div>詳細なリスク内訳、スコア根拠、推奨アクションを表示。</div>
                </div>
              ))} className="bg-white rounded-lg shadow p-5 text-left w-full">
                <div className="flex items-center">
                  <Shield className="h-6 w-6 text-red-600" />
                  <div className="ml-3">
                    <p className="text-xs font-medium text-gray-500">リスク状態</p>
                    <p className="text-sm">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                        riskAssessment?.risk_level === "Low" ? "bg-green-100 text-green-800" :
                        riskAssessment?.risk_level === "Medium" ? "bg-yellow-100 text-yellow-800" :
                        "bg-red-100 text-red-800"
                      }`}>{riskAssessment?.risk_level || "-"}</span>
                      <span className="ml-2 text-gray-600">{riskAssessment?.risk_score ? `${(riskAssessment.risk_score * 100).toFixed(0)}%` : "-"}</span>
                    </p>
                  </div>
                </div>
              </button>
              {/* 今日の推奨（STOP時は停止案内に切替） */}
              <button onClick={() => openSide("今日の推奨", (
                <div className="space-y-2 text-sm">
                  {modelHealth?.status === "stop" ? (
                    <div className="space-y-2">
                      <div className="text-red-700 font-semibold">健全性ゲートにより提案を一時停止中</div>
                      <div className="text-gray-700">原因: {(modelHealth?.reasons || []).join("、") || "要確認"}</div>
                      <button
                        onClick={() => loadData(true)}
                        className="mt-2 px-3 py-1.5 bg-blue-600 text-white rounded"
                      >再実行</button>
                    </div>
                  ) : (
                    <>
                      <div className="font-medium text-gray-900">上位候補</div>
                      <ul className="list-disc pl-4">
                        {(routine.topCandidates || []).slice(0,5).map(c => (
                          <li key={c.symbol}>{c.symbol} {c.recommendation} ({Math.round((c.confidence ?? 0.5)*100)}%)</li>
                        ))}
                      </ul>
                    </>
                  )}
                </div>
              ))} className="bg-white rounded-lg shadow p-5 text-left w-full">
                <div className="flex items-center">
                  <Target className="h-6 w-6 text-green-600" />
                  <div className="ml-3">
                    <p className="text-xs font-medium text-gray-500">今日の推奨</p>
                    {modelHealth?.status === "stop" ? (
                      <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">一時停止</span>
                    ) : (
                      <p className="text-sm text-gray-900 truncate max-w-[220px]">
                        {(routine.topCandidates || []).slice(0,3).map(c => c.symbol).join(" / ") || "-"}
                      </p>
                    )}
                  </div>
                </div>
              </button>
            </div>
            {/* 5分ルーティン（ホーム内完結） */}
            <div className="bg-white rounded-lg shadow p-4">
              <h3 className="text-lg font-medium text-gray-900 mb-2">今日のルーティン（5分）</h3>
              <RoutineDashboard
                onAnalysisClick={() => setShowAnalysisModal(true)}
                onReportClick={() => openSide("レポート要約", (<div>今日のダイジェストを表示</div>))}
                onTradeClick={() => openSide("売買案内", (<div>候補別の売買案内を表示</div>))}
              />
            </div>
          </div>

          {/* 右: サイド詳細パネル呼び出し用の固定コンテナ */}
          <div className="xl:col-span-3">
            <SideDetailPanel
              open={sidePanelOpen}
              title={sidePanelTitle}
              onClose={closeSide}
            >
              {sidePanelContent}
            </SideDetailPanel>
          </div>
        </div>

        {/* 以下の詳細セクションはホーム内サイドパネルへ集約するため段階廃止 */}
        {false && activeTab === "predictions" && (
          <div className="space-y-6">
            {/* 予測結果チャート */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">予測 vs 実際値</h3>
              <div className="h-96 bg-gray-50 rounded-lg p-4">
                <div className="h-full flex items-center justify-center">
                  <div className="text-center">
                    <div className="grid grid-cols-3 gap-4 mb-4">
                      {predictionChartData.slice(0, 6).map((item, index) => (
                        <div key={index} className="bg-white rounded p-3 shadow-sm">
                          <div className="text-xs text-gray-500 mb-2">#{item.index}</div>
                          <div className="space-y-1">
                            <div className="text-sm font-semibold text-blue-600">
                              実際: ¥{item.実際値?.toFixed(0) || "N/A"}
                            </div>
                            <div className="text-sm font-semibold text-red-600">
                              予測: ¥{item.予測値?.toFixed(0) || "N/A"}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="text-sm text-gray-500">
                      予測データ数: {predictionChartData.length}件
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* 予測精度分布 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">予測誤差分布</h3>
              <div className="h-72 bg-gray-50 rounded-lg p-4">
                <div className="h-full flex items-center justify-center">
                  <div className="text-center">
                    <div className="grid grid-cols-4 gap-3 mb-4">
                      {predictions.slice(0, 8).map((item, index) => (
                        <div key={index} className="bg-white rounded p-2 shadow-sm">
                          <div className="text-xs text-gray-500 mb-1">#{item.index}</div>
                          <div className="text-sm font-semibold text-purple-600">
                            誤差: {item.error?.toFixed(2) || "N/A"}%
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="text-sm text-gray-500">
                      平均誤差: {predictions.length > 0 ? (predictions.reduce((sum, p) => sum + p.error, 0) / predictions.length).toFixed(2) : "N/A"}%
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {false && activeTab === "models" && (
          <div className="space-y-6" data-guide-target="model-comparison">
            {/* モデル比較表 */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">モデル性能比較</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">順位</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">モデル名</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">MAE</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">RMSE</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">R²</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {modelComparison.map((model, index) => (
                      <tr key={model.name} className={index === 0 ? "bg-green-50" : ""}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {index + 1}
                          {index === 0 && <span className="ml-2 text-green-600">🏆</span>}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{model.name}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{model.mae.toFixed(4)}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{model.rmse.toFixed(4)}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{model.r2.toFixed(4)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* モデル性能比較チャート */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">MAE比較</h3>
              <div className="h-72 bg-gray-50 rounded-lg p-4">
                <div className="h-full flex items-center justify-center">
                  <div className="text-center">
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      {modelComparison.slice(0, 4).map((model, index) => (
                        <div key={index} className="bg-white rounded p-3 shadow-sm">
                          <div className="text-sm font-semibold text-gray-800 mb-1">{model.name}</div>
                          <div className="text-xs text-gray-500 mb-1">MAE: {model.mae?.toFixed(4) || "N/A"}</div>
                          <div className="text-xs text-gray-500 mb-1">RMSE: {model.rmse?.toFixed(4) || "N/A"}</div>
                          <div className="text-xs text-gray-500">R²: {model.r2?.toFixed(4) || "N/A"}</div>
                        </div>
                      ))}
                    </div>
                    <div className="text-sm text-gray-500">
                      最優秀モデル: {modelComparison.length > 0 ? modelComparison[0].name : "N/A"}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* モデルの長所・短所（参考情報） */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-medium text-gray-900">モデルの長所・短所（参考）</h3>
                <span className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded">参考情報</span>
              </div>
              <p className="text-sm text-gray-500 mb-4">各モデルの一般的な特性です。銘柄・期間により当てはまらない場合があります。</p>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {modelComparison.slice(0, 6).map((model) => {
                  const name = model.name?.toLowerCase() || "";
                  const meta = (() => {
                    if (name.includes("random") || name.includes("forest")) {
                      return {
                        display: "Random Forest",
                        pros: ["非線形捕捉に強い", "外れ値に比較的頑健", "特徴量スケールに鈍感"],
                        cons: ["説明性がやや低い", "高次元で計算コスト増", "外挿が苦手"],
                      };
                    }
                    if (name.includes("xgb") || name.includes("xgboost")) {
                      return {
                        display: "XGBoost",
                        pros: ["高精度になりやすい", "欠損や非線形に強い", "特徴量重要度が解釈しやすい"],
                        cons: ["パラメータ調整が複雑", "過学習のリスク", "学習時間が長い場合あり"],
                      };
                    }
                    if (name.includes("linear") || name.includes("ridge") || name.includes("lasso")) {
                      return {
                        display: "線形/正則化モデル",
                        pros: ["解釈容易", "計算が軽い", "外挿に比較的強い"],
                        cons: ["非線形関係を捉えにくい", "特徴量設計に依存", "外れ値影響を受けやすい"],
                      };
                    }
                    return {
                      display: model.name,
                      pros: ["実装が安定", "汎用的"],
                      cons: ["特性はデータ依存"],
                    };
                  })();
                  return (
                    <div key={model.name} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-900">{meta.display}</span>
                        <span className="text-xs text-gray-500">R²: {model.r2?.toFixed(3)}</span>
                      </div>
                      <div className="grid grid-cols-2 gap-3 text-xs">
                        <div>
                          <div className="text-green-700 font-semibold mb-1">長所</div>
                          <ul className="space-y-1">
                            {meta.pros.map((p) => (
                              <li key={p} className="text-green-700">• {p}</li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <div className="text-red-700 font-semibold mb-1">短所</div>
                          <ul className="space-y-1">
                            {meta.cons.map((c) => (
                              <li key={c} className="text-red-700">• {c}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* 特徴量重要度（参考・モデル共通表示） */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-medium text-gray-900">特徴量重要度（参考）</h3>
                <span className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded">参考情報</span>
              </div>
              <p className="text-sm text-gray-500 mb-4">サンプルの特徴量重要度です。実際の学習構成と一致しない場合があります。</p>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {featureAnalysis.slice(0, 9).map((f, idx) => (
                  <div key={`${f.feature}-${idx}`} className="border rounded p-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-900">{f.feature}</span>
                      <span className="text-xs text-gray-600">{(f.importance * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                      <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${Math.min(100, (f.percentage ?? f.importance * 100))}%` }}></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 予測が外れた期間（参考） */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-medium text-gray-900">予測が外れた期間（参考）</h3>
                <span className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded">参考情報</span>
              </div>
              <p className="text-sm text-gray-500 mb-4">誤差が大きいポイント上位をハイライトします（閾値: 誤差{">"}5%）。</p>
              {predictions && predictions.length > 0 ? (
                <div className="space-y-3">
                  {predictions
                    .filter(p => (p.error_percentage ?? p.error ?? 0) > 5)
                    .sort((a, b) => (b.error_percentage ?? b.error ?? 0) - (a.error_percentage ?? a.error ?? 0))
                    .slice(0, 10)
                    .map((p) => (
                      <div key={p.index} className="flex items-center justify-between text-sm border rounded p-2">
                        <div className="text-gray-800"># {p.index}</div>
                        <div className="text-gray-600">実際: {p.actual?.toFixed?.(2) ?? p.actual}</div>
                        <div className="text-gray-600">予測: {p.predicted?.toFixed?.(2) ?? p.predicted}</div>
                        <div className="font-medium text-red-700">誤差: {Number(p.error_percentage ?? p.error ?? 0).toFixed(2)}%</div>
                      </div>
                    ))}
                  <div className="text-xs text-gray-500">注: 外れた期間は銘柄・期間依存であり、モデルの優劣を断定するものではありません。</div>
                </div>
              ) : (
                <div className="text-sm text-gray-500">予測データがありません。</div>
              )}
            </div>
          </div>
        )}

        {false && activeTab === "analysis" && (
          <div className="space-y-6" data-guide-target="analysis-features">
            {/* 選択された銘柄の分析結果 */}
            {selectedSymbols.length > 0 && (
              <SymbolAnalysisResults selectedSymbols={selectedSymbols} />
            )}
            
            {/* 特徴量重要度 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">特徴量重要度</h3>
                <div className="h-72 bg-gray-50 rounded-lg p-4">
                  <div className="h-full flex items-center justify-center">
                    <div className="text-center">
                      <div className="grid grid-cols-2 gap-3 mb-4">
                        {featureAnalysis.slice(0, 6).map((feature, index) => (
                          <div key={index} className="bg-white rounded p-3 shadow-sm">
                            <div className="text-sm font-semibold text-gray-800 mb-1">{feature.feature}</div>
                            <div className="text-xs text-green-600 mb-1">
                              重要度: {(feature.importance * 100)?.toFixed(1) || "N/A"}%
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-green-500 h-2 rounded-full" 
                                style={{ width: `${feature.percentage || 0}%` }}
                              ></div>
                            </div>
                          </div>
                        ))}
                      </div>
                      <div className="text-sm text-gray-500">
                        最重要特徴量: {featureAnalysis.length > 0 ? featureAnalysis[0].feature : "N/A"}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">特徴量重要度分布</h3>
                <div className="h-72 bg-gray-50 rounded-lg p-4">
                  <div className="h-full flex items-center justify-center">
                    <div className="text-center">
                      <div className="space-y-2 mb-4">
                        {featureAnalysis.slice(0, 4).map((feature, index) => (
                          <div key={index} className="bg-white rounded p-2 shadow-sm">
                            <div className="flex justify-between items-center">
                              <span className="text-sm font-medium text-gray-800">{feature.feature}</span>
                              <span className="text-xs text-gray-500">{feature.percentage}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-1 mt-1">
                              <div 
                                className="bg-blue-500 h-1 rounded-full" 
                                style={{ width: `${feature.percentage || 0}%` }}
                              ></div>
                            </div>
                          </div>
                        ))}
                      </div>
                      <div className="text-sm text-gray-500">
                        合計重要度: {featureAnalysis.reduce((sum, f) => sum + (f.percentage || 0), 0).toFixed(1)}%
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* 散布図 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">実際値 vs 予測値散布図</h3>
              <div className="h-96 bg-gray-50 rounded-lg p-4">
                <div className="h-full flex items-center justify-center">
                  <div className="text-center">
                    <div className="grid grid-cols-4 gap-3 mb-4">
                      {predictions.slice(0, 8).map((item, index) => (
                        <div key={index} className="bg-white rounded p-2 shadow-sm">
                          <div className="text-xs text-gray-500 mb-1">#{item.index}</div>
                          <div className="space-y-1">
                            <div className="text-xs text-blue-600">
                              実際: {item.actual?.toFixed(0) || "N/A"}
                            </div>
                            <div className="text-xs text-red-600">
                              予測: {item.predicted?.toFixed(0) || "N/A"}
                            </div>
                            <div className="text-xs text-gray-500">
                              誤差: {item.error?.toFixed(1) || "N/A"}%
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="text-sm text-gray-500">
                      予測精度: {predictions.length > 0 ? (100 - (predictions.reduce((sum, p) => sum + p.error, 0) / predictions.length)).toFixed(1) : "N/A"}%
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {false && activeTab === "signals" && (
          <div className="space-y-6">
            <RealtimeSignalDisplay 
              symbols={selectedSymbols}
              autoRefresh={true}
              refreshInterval={30000}
            />
          </div>
        )}

        {false && activeTab === "personal" && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">💰 個人投資ダッシュボード</h2>
                  <p className="text-gray-600 mt-2">投資判断に直結する情報の優先表示、損益状況の一目瞭然な表示</p>
                </div>
                <Link
                  href="./personal-investment"
                  className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <User className="h-4 w-4 mr-2" />
                  詳細ダッシュボード
                </Link>
              </div>
              
              {/* 個人投資概要カード */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
                <div className="bg-gradient-to-r from-green-50 to-green-100 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-green-800">総投資額</h3>
                      <p className="text-2xl font-bold text-green-600">¥1,000,000</p>
                    </div>
                    <DollarSign className="h-8 w-8 text-green-500" />
                  </div>
                  <p className="text-sm text-green-600 mt-2">現在価値: ¥1,050,000</p>
                </div>
                
                <div className="bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-blue-800">未実現損益</h3>
                      <p className="text-2xl font-bold text-blue-600">+¥50,000</p>
                    </div>
                    <TrendingUp className="h-8 w-8 text-blue-500" />
                  </div>
                  <p className="text-sm text-blue-600 mt-2">+5.0%</p>
                </div>
                
                <div className="bg-gradient-to-r from-purple-50 to-purple-100 border border-purple-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-purple-800">推奨アクション</h3>
                      <p className="text-lg font-bold text-purple-600">BUY</p>
                    </div>
                    <Target className="h-8 w-8 text-purple-500" />
                  </div>
                  <p className="text-sm text-purple-600 mt-2">信頼度: 85%</p>
                </div>
                
                <div className="bg-gradient-to-r from-orange-50 to-orange-100 border border-orange-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-orange-800">リスクレベル</h3>
                      <p className="text-lg font-bold text-orange-600">MEDIUM</p>
                    </div>
                    <Shield className="h-8 w-8 text-orange-500" />
                  </div>
                  <p className="text-sm text-orange-600 mt-2">リスク調整後リターン: 0.75</p>
                </div>
              </div>
              
              {/* ポジション一覧 */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">主要ポジション</h3>
                <div className="grid gap-4">
                  {[
                    { symbol: "7203.T", name: "トヨタ自動車", price: 2500, change: 2.5, action: "BUY", confidence: 85 },
                    { symbol: "6758.T", name: "ソニーグループ", price: 12000, change: -1.2, action: "HOLD", confidence: 70 },
                    { symbol: "6861.T", name: "キーエンス", price: 5000, change: 3.8, action: "STRONG_BUY", confidence: 90 },
                  ].map((stock) => (
                    <div key={stock.symbol} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div>
                          <h4 className="font-semibold text-gray-900">{stock.symbol}</h4>
                          <p className="text-sm text-gray-600">{stock.name}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold">¥{stock.price.toLocaleString()}</p>
                          <p className={`text-sm ${stock.change >= 0 ? "text-green-600" : "text-red-600"}`}>
                            {stock.change >= 0 ? "+" : ""}{stock.change}%
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          stock.action === "STRONG_BUY" ? "bg-green-100 text-green-800" :
                          stock.action === "BUY" ? "bg-blue-100 text-blue-800" :
                          stock.action === "HOLD" ? "bg-gray-100 text-gray-800" :
                          "bg-red-100 text-red-800"
                        }`}>
                          {stock.action}
                        </span>
                        <span className="text-sm text-gray-600">{stock.confidence}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {false && activeTab === "risk" && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">🛡️ リスク管理ダッシュボード</h2>
                  <p className="text-gray-600 mt-2">現在のポジション状況、損切りライン、リスクレベルを可視化</p>
                </div>
                <Link
                  href="./risk"
                  className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Shield className="h-4 w-4 mr-2" />
                  詳細ダッシュボード
                </Link>
              </div>
              
                      {/* リスク管理概要カード */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <div className="bg-gradient-to-r from-red-50 to-red-100 border border-red-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-red-800">リスクレベル</h3>
                      <p className="text-2xl font-bold text-red-600">HIGH</p>
                    </div>
                    <Shield className="h-8 w-8 text-red-500" />
                  </div>
                  <p className="text-sm text-red-600 mt-2">リスクスコア: 0.75</p>
                </div>
                
                <div className="bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-blue-800">ポートフォリオ価値</h3>
                      <p className="text-2xl font-bold text-blue-600">¥1,250,000</p>
                    </div>
                    <TrendingUp className="h-8 w-8 text-blue-500" />
                  </div>
                  <p className="text-sm text-blue-600 mt-2">未実現損益: +¥50,000</p>
                </div>
                
                <div className="bg-gradient-to-r from-yellow-50 to-yellow-100 border border-yellow-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-yellow-800">最大ドローダウン</h3>
                      <p className="text-2xl font-bold text-yellow-600">8.5%</p>
                    </div>
                    <TrendingDown className="h-8 w-8 text-yellow-500" />
                  </div>
                  <p className="text-sm text-yellow-600 mt-2">VaR (95%): ¥125,000</p>
                </div>
              </div>
              
                      {/* 簡易 銘柄別 VaR/MDD テーブル（デモ表示） */}
                      <div className="bg-white rounded-lg border border-gray-200 mb-6">
                        <div className="px-6 py-4 border-b border-gray-200">
                          <h3 className="text-lg font-semibold text-gray-900">銘柄別リスク指標</h3>
                        </div>
                        <div className="overflow-x-auto">
                          <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                              <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">銘柄</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">VaR(95%)</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">最大DD</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">年率ボラ</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">損切り</th>
                              </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200 text-sm">
                              {[ 
                                { symbol: "7203.T", var95: 0.032, mdd: 0.085, vol: 0.24, sl: "¥2,150 / 8%" },
                                { symbol: "6758.T", var95: 0.028, mdd: 0.072, vol: 0.21, sl: "¥11,200 / 7%" },
                                { symbol: "9984.T", var95: 0.045, mdd: 0.125, vol: 0.35, sl: "¥5,200 / 10%" },
                              ].map((row) => (
                                <tr key={row.symbol}>
                                  <td className="px-6 py-3 font-medium text-gray-900">{row.symbol}</td>
                                  <td className="px-6 py-3">{(row.var95 * 100).toFixed(1)}%</td>
                                  <td className="px-6 py-3">{(row.mdd * 100).toFixed(1)}%</td>
                                  <td className="px-6 py-3">{(row.vol * 100).toFixed(1)}%</td>
                                  <td className="px-6 py-3">{row.sl}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>

                      {/* ポジション一覧 */}
              <div className="bg-white border border-gray-200 rounded-lg">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900">現在のポジション</h3>
                </div>
                <div className="divide-y divide-gray-200">
                  {[
                    { symbol: "7203.T", name: "トヨタ自動車", pnl: -10000, pnlPercent: -4.0, risk: "HIGH" },
                    { symbol: "6758.T", name: "ソニーグループ", pnl: 25000, pnlPercent: 4.2, risk: "MEDIUM" },
                    { symbol: "9984.T", name: "ソフトバンクグループ", pnl: -37500, pnlPercent: -6.25, risk: "HIGH" },
                  ].map((position) => (
                    <div key={position.symbol} className="px-6 py-4 flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div>
                          <h4 className="font-semibold text-gray-900">{position.symbol}</h4>
                          <p className="text-sm text-gray-600">{position.name}</p>
                        </div>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          position.risk === "HIGH" ? "bg-red-100 text-red-800" :
                          position.risk === "MEDIUM" ? "bg-yellow-100 text-yellow-800" :
                          "bg-green-100 text-green-800"
                        }`}>
                          {position.risk}
                        </span>
                      </div>
                      <div className="text-right">
                        <div className={`font-semibold ${position.pnl >= 0 ? "text-green-600" : "text-red-600"}`}>
                          {position.pnl >= 0 ? "+" : ""}¥{position.pnl.toLocaleString()}
                        </div>
                        <div className={`text-sm ${position.pnl >= 0 ? "text-green-600" : "text-red-600"}`}>
                          {position.pnl >= 0 ? "+" : ""}{position.pnlPercent}%
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* 推奨事項 */}
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <div className="flex items-start">
                  <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5 mr-3" />
                  <div>
                    <h4 className="font-semibold text-yellow-800">リスク管理推奨事項</h4>
                    <ul className="text-sm text-yellow-700 mt-2 space-y-1">
                      <li>• ポートフォリオリスクが高すぎます。ポジションサイズを縮小してください。</li>
                      <li>• 9984.T（ソフトバンクグループ）の損切りを検討してください。</li>
                      <li>• 損切りラインを現在の80%に設定することを推奨します。</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* 銘柄選択モーダル */}
      {showSymbolSelector && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">銘柄選択・分析</h3>
              <button
                onClick={() => setShowSymbolSelector(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <SymbolSelector
              selectedSymbols={selectedSymbols}
              onSymbolsChange={setSelectedSymbols}
              onAnalysis={handleSymbolAnalysis}
              isAnalyzing={isAnalyzing}
              adapter={jquantsAdapter}
            />
          </div>
        </div>
      )}

      {/* 分析実行モーダル */}
      {showAnalysisModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg mx-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">設定連携分析実行</h3>
              <button
                onClick={() => setShowAnalysisModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            {!settingsAnalyzing ? (
              <div className="space-y-4">
                <p className="text-gray-600">
                  設定に基づいて全銘柄の分析を実行します。この処理には数分かかる場合があります。
                </p>
                
                {/* 設定情報表示 */}
                <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                  <h4 className="font-medium text-gray-900">実行設定</h4>
                  {(() => {
                    const desc = getAnalysisDescription();
                    return (
                      <div className="text-sm text-gray-600 space-y-1">
                        <div>• {desc.prediction}</div>
                        <div>• {desc.model}</div>
                        <div>• {desc.retrain}</div>
                        <div>• {desc.features}</div>
                        <div>• {desc.data}</div>
                      </div>
                    );
                  })()}
                </div>
                
                <div className="flex justify-end space-x-3">
                  <button
                    onClick={() => setShowAnalysisModal(false)}
                    className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    キャンセル
                  </button>
                  <button
                    onClick={() => runAnalysis()}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    設定で実行
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-gray-600">{settingsStatus}</p>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${settingsProgress}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-500 text-center">
                  {Math.round(settingsProgress)}% 完了
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 設定モーダル */}
      {showSettingsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg mx-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">設定</h3>
              <button
                onClick={() => setShowSettingsModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  予測期間（日数）
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500" defaultValue="30">
                  <option value="7">7日</option>
                  <option value="14">14日</option>
                  <option value="30">30日</option>
                  <option value="60">60日</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  使用するモデル
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500" defaultValue="all">
                  <option value="all">すべてのモデル</option>
                  <option value="linear">線形回帰</option>
                  <option value="random_forest">ランダムフォレスト</option>
                  <option value="xgboost">XGBoost</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  特徴量選択
                </label>
                <div className="space-y-2">
                  {["SMA_5", "SMA_10", "SMA_25", "SMA_50", "RSI", "MACD", "ボリンジャーバンド"].map(feature => (
                    <label key={feature} className="flex items-center">
                      <input
                        type="checkbox"
                        defaultChecked
                        className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-700">{feature}</span>
                    </label>
                  ))}
                </div>
              </div>
              
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  onClick={() => setShowSettingsModal(false)}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  キャンセル
                </button>
                <button
                  onClick={() => {
                    // 設定保存のロジック
                    setShowSettingsModal(false);
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  保存
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 銘柄監視管理モーダル */}
      {showStockMonitoring && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">銘柄監視管理</h2>
                <button
                  onClick={() => setShowStockMonitoring(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>
              
              <StockMonitoringManager
                onMonitoringChange={handleMonitoringChange}
                onConfigChange={handleConfigChange}
              />
            </div>
          </div>
        </div>
      )}

      {/* ユーザーガイドモーダル */}
      <UserGuide
        isVisible={showUserGuide}
        onClose={() => {
          try {
            sessionStorage.setItem("userGuideClosedThisSession", "true");
          } catch (_) {}
          setShowUserGuide(false);
        }}
        onStepComplete={(stepId) => {
          console.log("ガイドステップ完了:", stepId);
        }}
        currentTab={activeTab}
      />

      {/* ガイド機能モーダル */}
      <GlossaryModal 
        isOpen={showGlossary} 
        onClose={() => setShowGlossary(false)} 
      />
      
      <HelpModal 
        isOpen={showHelp} 
        onClose={() => setShowHelp(false)} 
        currentPage="/"
      />

      {/* チェックリスト */}
      {showChecklist && (
        <div className="fixed top-4 right-4 z-40">
          <Checklist
            items={checklistItems}
            onItemComplete={handleChecklistItemComplete}
            onItemReset={handleChecklistItemReset}
            onComplete={handleChecklistComplete}
          />
        </div>
      )}

      {/* チェックリスト進捗バッジ */}
      {!showChecklist && !guideStore.checklistProgress.isCompleted && (
        <div className="fixed top-4 right-4 z-40">
          <ChecklistBadge
            completedCount={guideStore.checklistProgress.completedItems.length}
            totalCount={guideStore.checklistProgress.totalItems}
            onClick={() => setShowChecklist(true)}
          />
        </div>
      )}

      {/* J-Quants設定モーダル */}
      {showJQuantsSetup && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">J-Quants API設定</h2>
                <button
                  onClick={() => setShowJQuantsSetup(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>
              
              <JQuantsTokenSetup
                onTokenConfigured={(adapter) => {
                  setJquantsAdapter(adapter);
                  setShowJQuantsSetup(false);
                }}
                onTokenRemoved={() => {
                  setJquantsAdapter(null);
                }}
              />
            </div>
          </div>
        </div>
      )}

      {/* 初回利用者向けチュートリアル */}
      <FirstTimeTutorial
        isVisible={showFirstTimeTutorial}
        onClose={() => setShowFirstTimeTutorial(false)}
        onStartAnalysis={() => {
          setShowFirstTimeTutorial(false);
          setShowAnalysisPanel(true);
        }}
        onStartDataUpdate={() => {
          setShowFirstTimeTutorial(false);
          setShowDataUpdateManager(true);
        }}
      />

      {/* 分析実行パネル */}
      {showAnalysisPanel && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">分析実行</h2>
                <button
                  onClick={() => setShowAnalysisPanel(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>
              
              <AnalysisExecutionPanel
                onAnalysisStart={() => {
                  setLoadingOverlay({
                    isVisible: true,
                    title: "分析実行中",
                    message: "AIによる株価予測分析を実行しています...",
                    progress: 0,
                    type: "loading",
                    steps: [
                      { name: "データ更新", status: "pending", description: "最新の株価データを取得" },
                      { name: "特徴量エンジニアリング", status: "pending", description: "技術指標を計算" },
                      { name: "モデル学習", status: "pending", description: "AIモデルを学習" },
                      { name: "予測実行", status: "pending", description: "株価予測を実行" },
                    ],
                  });
                }}
                onAnalysisComplete={(result) => {
                  setLoadingOverlay({
                    isVisible: true,
                    title: "分析完了",
                    message: "分析が正常に完了しました",
                    type: "success",
                  });
                  setTimeout(() => {
                    setLoadingOverlay({ isVisible: false, title: "", message: "" });
                    setShowAnalysisPanel(false);
                    loadData();
                  }, 2000);
                }}
                onDataUpdateStart={() => {
                  setLoadingOverlay({
                    isVisible: true,
                    title: "データ更新中",
                    message: "最新の株価データを取得しています...",
                    progress: 0,
                    type: "loading",
                  });
                }}
                onDataUpdateComplete={(result) => {
                  setLoadingOverlay({
                    isVisible: true,
                    title: "データ更新完了",
                    message: "データの更新が完了しました",
                    type: "success",
                  });
                  setTimeout(() => {
                    setLoadingOverlay({ isVisible: false, title: "", message: "" });
                    loadData();
                  }, 2000);
                }}
              />
            </div>
          </div>
        </div>
      )}

      {/* データ更新マネージャー */}
      {showDataUpdateManager && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">データ更新</h2>
                <button
                  onClick={() => setShowDataUpdateManager(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>
              
              <EnhancedDataUpdateManager
                symbols={["7203.T", "6758.T", "6861.T", "9984.T", "9432.T"]}
                onUpdateComplete={(results) => {
                  setShowDataUpdateManager(false);
                  loadData();
                }}
                onProgressChange={(progress) => {
                  setLoadingOverlay({
                    isVisible: true,
                    title: "データ更新中",
                    message: progress.current,
                    progress: progress.percentage,
                    estimatedTime: progress.estimatedTimeRemaining,
                    type: "loading",
                  });
                }}
              />
            </div>
          </div>
        </div>
      )}

      {/* ローディングオーバーレイ */}
      <LoadingOverlay
        isVisible={loadingOverlay.isVisible}
        title={loadingOverlay.title}
        message={loadingOverlay.message}
        progress={loadingOverlay.progress}
        estimatedTime={loadingOverlay.estimatedTime}
        type={loadingOverlay.type}
        steps={loadingOverlay.steps}
        onCancel={() => {
          setLoadingOverlay({ isVisible: false, title: "", message: "" });
        }}
      />
    </div>
  );
}

export default function Dashboard() {
  return (
    <ErrorBoundary
      fallbackRender={({ error, resetErrorBoundary }: { error: Error; resetErrorBoundary: () => void }) => (
        <UnifiedErrorHandler
          error={error}
          onRetry={resetErrorBoundary}
          onDismiss={() => window.location.reload()}
          showDetails={process.env.NODE_ENV === "development"}
          autoRetry={true}
          maxRetries={3}
        />
      )}
    >
      <Suspense fallback={
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">コンポーネントを読み込み中...</p>
          </div>
        </div>
      }>
        <SettingsProvider>
          <TourProvider>
            <DashboardContent />
          </TourProvider>
        </SettingsProvider>
      </Suspense>
    </ErrorBoundary>
  );
}