"use client";

import { useState, useEffect, useCallback } from "react";
import { fetchJson, createIdempotencyKey } from "../lib/fetcher";
import { 
  Clock, 
  TrendingUp, 
  FileText, 
  ShoppingCart, 
  RefreshCw, 
  AlertCircle,
  CheckCircle,
  ArrowUp,
  ArrowDown,
  Minus,
  Timer,
  Target,
  BarChart3,
  Eye,
  Settings,
  Loader2,
  Play,
} from "lucide-react";

interface YesterdaySummary {
  date: string;
  totalReturn: number;
  topPerformers: Array<{
    symbol: string;
    name: string;
    return: number;
    action: "buy" | "sell" | "hold";
  }>;
  alerts: Array<{
    type: "warning" | "info" | "success";
    message: string;
  }>;
  analysisStatus: "completed" | "partial" | "failed";
}

interface TodayActions {
  analysisRequired: boolean;
  watchlistUpdates: Array<{
    symbol: string;
    action: "add" | "remove" | "modify";
    reason: string;
  }>;
  nextUpdateTime: string;
  priorityActions: Array<{
    id: string;
    title: string;
    description: string;
    action: "analyze" | "report" | "trade";
    priority: "high" | "medium" | "low";
  }>;
}

interface RoutineDashboardProps {
  onAnalysisClick?: () => void;
  onReportClick?: () => void;
  onTradeClick?: () => void;
}

export default function RoutineDashboard({ 
  onAnalysisClick, 
  onReportClick, 
  onTradeClick, 
}: RoutineDashboardProps) {
  const [yesterdaySummary, setYesterdaySummary] = useState<YesterdaySummary | null>(null);
  const [todayActions, setTodayActions] = useState<TodayActions | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeUntilUpdate, setTimeUntilUpdate] = useState<string>("");
  const [isExecutingAction, setIsExecutingAction] = useState<string | null>(null);
  const [routineJobId, setRoutineJobId] = useState<string | null>(null);
  const [routineProgress, setRoutineProgress] = useState<number>(0);
  const [routineStatus, setRoutineStatus] = useState<"idle" | "running" | "succeeded" | "failed">("idle");
  const [routineError, setRoutineError] = useState<string | null>(null);

  // 前日の分析結果を取得
  const loadYesterdaySummary = useCallback(async () => {
    try {
      // 実際のAPIから前日の結果を取得
      const response = await fetch("/api/yesterday-summary", {
        method: "GET",
        headers: { "Content-Type": "application/json" },
        cache: "no-store",
      });
      
      if (response.ok) {
        const data = await response.json();
        setYesterdaySummary(data);
      } else {
        // フォールバック: ローカルストレージから取得
        const cached = localStorage.getItem("yesterday_summary");
        if (cached) {
          setYesterdaySummary(JSON.parse(cached));
        }
      }
    } catch (err) {
      console.error("前日結果の取得に失敗:", err);
      // デモデータを表示
      setYesterdaySummary({
        date: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString().split("T")[0],
        totalReturn: 2.3,
        topPerformers: [
          { symbol: "7203.T", name: "トヨタ自動車", return: 3.2, action: "buy" },
          { symbol: "6758.T", name: "ソニーグループ", return: -1.1, action: "sell" },
          { symbol: "6861.T", name: "キーエンス", return: 1.8, action: "hold" },
        ],
        alerts: [
          { type: "success", message: "分析完了: 3銘柄の予測精度向上" },
          { type: "warning", message: "市場ボラティリティ上昇に注意" },
        ],
        analysisStatus: "completed",
      });
    }
  }, []);

  // 今日のアクションを取得
  const loadTodayActions = useCallback(async () => {
    try {
      const response = await fetch("/api/today-actions", {
        method: "GET",
        headers: { "Content-Type": "application/json" },
        cache: "no-store",
      });
      
      if (response.ok) {
        const data = await response.json();
        setTodayActions(data);
      } else {
        // デモデータを表示
        setTodayActions({
          analysisRequired: true,
          watchlistUpdates: [
            { symbol: "7203.T", action: "modify", reason: "予測精度向上のため設定調整" },
            { symbol: "6758.T", action: "remove", reason: "パフォーマンス低下" },
          ],
          nextUpdateTime: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(),
          priorityActions: [
            {
              id: "analysis",
              title: "分析実行",
              description: "最新データで予測分析を実行",
              action: "analyze",
              priority: "high",
            },
            {
              id: "report",
              title: "レポート確認",
              description: "昨日の分析結果を確認",
              action: "report",
              priority: "medium",
            },
            {
              id: "trade",
              title: "売買指示",
              description: "推奨アクションに基づく取引指示",
              action: "trade",
              priority: "high",
            },
          ],
        });
      }
    } catch (err) {
      console.error("今日のアクション取得に失敗:", err);
    }
  }, []);

  // タイマー更新
  useEffect(() => {
    const updateTimer = () => {
      if (todayActions?.nextUpdateTime) {
        const now = new Date();
        const nextUpdate = new Date(todayActions.nextUpdateTime);
        const diff = nextUpdate.getTime() - now.getTime();
        
        if (diff > 0) {
          const hours = Math.floor(diff / (1000 * 60 * 60));
          const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
          setTimeUntilUpdate(`${hours}時間${minutes}分`);
        } else {
          setTimeUntilUpdate("更新準備中");
        }
      }
    };

    updateTimer();
    const interval = setInterval(updateTimer, 60000); // 1分ごと
    return () => clearInterval(interval);
  }, [todayActions]);

  // データ読み込み
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        await Promise.all([
          loadYesterdaySummary(),
          loadTodayActions(),
        ]);
      } catch (err) {
        setError("データの読み込みに失敗しました");
        console.error("データ読み込みエラー:", err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [loadYesterdaySummary, loadTodayActions]);

  // アクション実行
  const handleActionClick = async (action: "analyze" | "report" | "trade") => {
    setIsExecutingAction(action);
    
    try {
      switch (action) {
        case "analyze":
          const result = await fetchJson<any>("/api/execute-analysis", {
            json: {
              type: "full_analysis",
              symbols: ["7203.T", "6758.T", "6861.T"],
              timeframe: "1d",
            },
            idempotencyKey: true,
          });
            console.log("分析完了:", result);
            onAnalysisClick?.();
            showNotification("分析が完了しました", "success");
          
          break;
          
        case "report":
          const report = await fetchJson<any>("/api/generate-report", {
            json: {
              type: "daily_summary",
              includeCharts: true,
              includeRecommendations: true,
            },
            idempotencyKey: true,
          });
            console.log("レポート生成完了:", report);
            onReportClick?.();
            showNotification("レポートが生成されました", "success");
          
          break;
          
        case "trade":
          const trade = await fetchJson<any>("/api/execute-trade", {
            json: {
              type: "recommended_actions",
              confirmBeforeExecute: true,
            },
            idempotencyKey: true,
          });
            console.log("売買指示完了:", trade);
            onTradeClick?.();
            showNotification("売買指示が実行されました", "success");
          
          break;
      }
    } catch (error) {
      console.error(`${action}実行エラー:`, error);
      showNotification(`${action}実行に失敗しました`, "error");
    } finally {
      setIsExecutingAction(null);
    }
  };

  // 今日のルーティン実行（1→Nステップ進捗UI）
  const runTodayRoutine = async () => {
    try {
      setRoutineStatus("running");
      setRoutineError(null);
      setRoutineProgress(0);

      const clientTokenKey = "routine:client_token";
      let clientToken = localStorage.getItem(clientTokenKey);
      if (!clientToken) {
        clientToken = `client_${crypto.randomUUID?.() || Math.random().toString(36).slice(2)}`;
        localStorage.setItem(clientTokenKey, clientToken);
      }

      const data = await fetchJson<any>("/api/routine/run-today", {
        json: { client_token: clientToken },
        idempotencyKey: true,
      });
      const jobId = data.job_id as string;
      setRoutineJobId(jobId);

      // 再開対応: jobId を保存
      sessionStorage.setItem("routine:job_id", jobId);

      // ポーリング開始
      pollRoutine(jobId);
    } catch (e: any) {
      setRoutineStatus("failed");
      setRoutineError(e?.message || "不明なエラー");
    }
  };

  const pollRoutine = async (jobId: string) => {
    const start = Date.now();
    const poll = async (): Promise<void> => {
      try {
        const res = await fetch(`/api/routine/jobs/${jobId}`, { cache: "no-store" });
        if (!res.ok) throw new Error("ジョブ取得に失敗");
        const data = await res.json();
        setRoutineProgress(Math.min(99, Math.floor(data.progress ?? 0)));
        if (data.status === "succeeded") {
          setRoutineProgress(100);
          setRoutineStatus("succeeded");
          showNotification("今日のルーティンが完了しました", "success");
          return;
        }
        if (data.status === "failed") {
          setRoutineStatus("failed");
          setRoutineError(data.error || "サーバーエラー");
          showNotification("ルーティンが失敗しました", "error");
          return;
        }

        if (Date.now() - start > 3 * 60 * 1000) {
          throw new Error("タイムアウト（3分）");
        }
        setTimeout(poll, 1500);
      } catch (e: any) {
        setRoutineStatus("failed");
        setRoutineError(e?.message || "不明なエラー");
      }
    };
    setTimeout(poll, 1500);
  };

  // 中断→再開対応（同UIで再アタッチ）
  useEffect(() => {
    const existingJobId = sessionStorage.getItem("routine:job_id");
    if (existingJobId && routineStatus !== "succeeded") {
      setRoutineJobId(existingJobId);
      setRoutineStatus("running");
      pollRoutine(existingJobId);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 通知表示
  const showNotification = (message: string, type: "success" | "error" | "info") => {
    const notification = document.createElement("div");
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
      type === "success" ? "bg-green-100 text-green-800 border border-green-200" :
      type === "error" ? "bg-red-100 text-red-800 border border-red-200" :
      "bg-blue-100 text-blue-800 border border-blue-200"
    }`;
    notification.innerHTML = `
      <div class="flex items-center space-x-2">
        ${type === "success" ? "<div class=\"w-4 h-4 bg-green-500 rounded-full\"></div>" :
          type === "error" ? "<div class=\"w-4 h-4 bg-red-500 rounded-full\"></div>" :
          "<div class=\"w-4 h-4 bg-blue-500 rounded-full\"></div>"}
        <span>${message}</span>
      </div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.remove();
    }, 3000);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">5分ルーティンデータを読み込み中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-8 w-8 text-red-600 mx-auto mb-4" />
          <p className="text-red-600 mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            再読み込み
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ヘッダー */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">5分ルーティン</h1>
              <p className="text-gray-600">毎日の投資判断を効率化</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <Timer className="h-4 w-4" />
                <span>次回更新まで: {timeUntilUpdate}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* 今日のルーティン カード（最上段） */}
        <div className="mb-6 bg-white rounded-lg shadow border p-6">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Play className="h-5 w-5 text-blue-600" />
              <h2 className="text-lg font-semibold text-gray-900">今日のルーティン</h2>
            </div>
            <button
              onClick={runTodayRoutine}
              disabled={routineStatus === "running"}
              className={`px-4 py-2 rounded-lg text-white font-medium ${
                routineStatus === "running" ? "bg-gray-400 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"
              }`}
            >
              {routineStatus === "running" ? "実行中..." : "1クリックで実行"}
            </button>
          </div>
          {/* 進捗UI */}
          <div className="space-y-2">
            <div className="w-full bg-gray-100 rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all duration-500 ${
                  routineStatus === "failed" ? "bg-red-500" : "bg-blue-600"
                }`}
                style={{ width: `${routineProgress}%` }}
              />
            </div>
            <div className="text-sm text-gray-600 flex items-center gap-3">
              <span>進捗: {routineProgress}%</span>
              {routineJobId && (
                <span className="text-xs text-gray-500">Job: {routineJobId}</span>
              )}
              {routineStatus === "succeeded" && (
                <span className="text-green-700 flex items-center gap-1"><CheckCircle className="h-4 w-4"/> 完了</span>
              )}
              {routineStatus === "failed" && (
                <span className="text-red-700 flex items-center gap-1"><AlertCircle className="h-4 w-4"/> 失敗</span>
              )}
            </div>
            {/* 再開ボタン（中断→復帰）*/}
            {routineStatus !== "running" && sessionStorage.getItem("routine:job_id") && (
              <button
                onClick={() => {
                  const jid = sessionStorage.getItem("routine:job_id");
                  if (jid) {
                    setRoutineJobId(jid);
                    setRoutineStatus("running");
                    pollRoutine(jid);
                  }
                }}
                className="text-blue-600 text-sm underline"
              >
                途中から再開
              </button>
            )}
            {routineError && (
              <div className="text-sm text-red-700">{routineError}</div>
            )}
          </div>
          {/* ステップ表示（1→N）*/}
          <div className="mt-4 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2 text-xs">
            {["データ取得","前処理","予測","シグナル","推奨","実行記録"].map((label, idx) => {
              const thresholds = [10,30,55,70,85,95,100];
              const done = routineProgress >= thresholds[idx];
              return (
                <div key={label} className={`p-2 rounded border ${done ? "bg-green-50 border-green-200 text-green-800" : "bg-gray-50 border-gray-200 text-gray-700"}`}>
                  <div className="flex items-center gap-1">
                    {done ? <CheckCircle className="h-3 w-3"/> : <Loader2 className="h-3 w-3"/>}
                    <span>{label}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 前日の分析結果要約 */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow border p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">前日の分析結果</h2>
                <div className="flex items-center space-x-2">
                  {yesterdaySummary?.analysisStatus === "completed" ? (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  ) : (
                    <AlertCircle className="h-5 w-5 text-yellow-600" />
                  )}
                  <span className="text-sm text-gray-600">
                    {yesterdaySummary?.date}
                  </span>
                </div>
              </div>

              {/* パフォーマンスサマリー */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">総リターン</span>
                    <span className={`text-lg font-semibold ${
                      (yesterdaySummary?.totalReturn || 0) >= 0 ? "text-green-600" : "text-red-600"
                    }`}>
                      {yesterdaySummary?.totalReturn ? 
                        `${yesterdaySummary.totalReturn > 0 ? "+" : ""}${yesterdaySummary.totalReturn}%` : 
                        "N/A"
                      }
                    </span>
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">分析銘柄数</span>
                    <span className="text-lg font-semibold text-gray-900">
                      {yesterdaySummary?.topPerformers.length || 0}
                    </span>
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">アラート数</span>
                    <span className="text-lg font-semibold text-gray-900">
                      {yesterdaySummary?.alerts.length || 0}
                    </span>
                  </div>
                </div>
              </div>

              {/* トップパフォーマー */}
              <div className="mb-6">
                <h3 className="text-md font-medium text-gray-900 mb-3">主要銘柄パフォーマンス</h3>
                <div className="space-y-2">
                  {yesterdaySummary?.topPerformers.map((stock, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="flex items-center space-x-1">
                          {stock.action === "buy" && <ArrowUp className="h-4 w-4 text-green-600" />}
                          {stock.action === "sell" && <ArrowDown className="h-4 w-4 text-red-600" />}
                          {stock.action === "hold" && <Minus className="h-4 w-4 text-gray-600" />}
                        </div>
                        <div>
                          <span className="font-medium text-gray-900">{stock.symbol}</span>
                          <span className="text-sm text-gray-600 ml-2">{stock.name}</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className={`font-semibold ${
                          stock.return >= 0 ? "text-green-600" : "text-red-600"
                        }`}>
                          {stock.return > 0 ? "+" : ""}{stock.return}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* アラート */}
              {yesterdaySummary?.alerts && yesterdaySummary.alerts.length > 0 && (
                <div>
                  <h3 className="text-md font-medium text-gray-900 mb-3">重要なアラート</h3>
                  <div className="space-y-2">
                    {yesterdaySummary.alerts.map((alert, index) => (
                      <div key={index} className={`p-3 rounded-lg flex items-center space-x-2 ${
                        alert.type === "success" ? "bg-green-50 text-green-800" :
                        alert.type === "warning" ? "bg-yellow-50 text-yellow-800" :
                        "bg-blue-50 text-blue-800"
                      }`}>
                        <AlertCircle className="h-4 w-4" />
                        <span className="text-sm">{alert.message}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* 今日のアクション */}
          <div className="space-y-6">
            {/* 1クリックアクション */}
            <div className="bg-white rounded-lg shadow border p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">今日のアクション</h2>
              
              <div className="space-y-3">
                {todayActions?.priorityActions.map((action) => {
                  const isExecuting = isExecutingAction === action.action;
                  return (
                    <button
                      key={action.id}
                      onClick={() => handleActionClick(action.action)}
                      disabled={isExecuting}
                      className={`w-full p-4 rounded-lg border-2 transition-all duration-200 ${
                        isExecuting 
                          ? "border-gray-300 bg-gray-100 cursor-not-allowed opacity-75"
                          : action.priority === "high" 
                          ? "border-red-200 bg-red-50 hover:bg-red-100" 
                          : action.priority === "medium"
                          ? "border-yellow-200 bg-yellow-50 hover:bg-yellow-100"
                          : "border-gray-200 bg-gray-50 hover:bg-gray-100"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          {isExecuting ? (
                            <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
                          ) : (
                            <>
                              {action.action === "analyze" && <BarChart3 className="h-5 w-5 text-blue-600" />}
                              {action.action === "report" && <FileText className="h-5 w-5 text-green-600" />}
                              {action.action === "trade" && <ShoppingCart className="h-5 w-5 text-purple-600" />}
                            </>
                          )}
                          <div className="text-left">
                            <div className="font-medium text-gray-900">
                              {isExecuting ? `${action.title}中...` : action.title}
                            </div>
                            <div className="text-sm text-gray-600">{action.description}</div>
                          </div>
                        </div>
                        <div className={`px-2 py-1 rounded text-xs font-medium ${
                          action.priority === "high" ? "bg-red-100 text-red-800" :
                          action.priority === "medium" ? "bg-yellow-100 text-yellow-800" :
                          "bg-gray-100 text-gray-800"
                        }`}>
                          {action.priority === "high" ? "高" : action.priority === "medium" ? "中" : "低"}
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* ウォッチリスト更新 */}
            {todayActions?.watchlistUpdates && todayActions.watchlistUpdates.length > 0 && (
              <div className="bg-white rounded-lg shadow border p-6">
                <h3 className="text-md font-semibold text-gray-900 mb-4">ウォッチリスト更新</h3>
                <div className="space-y-2">
                  {todayActions.watchlistUpdates.map((update, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <span className="font-medium text-gray-900">{update.symbol}</span>
                        <span className="text-sm text-gray-600 ml-2">
                          {update.action === "add" ? "追加" : 
                           update.action === "remove" ? "削除" : "変更"}
                        </span>
                      </div>
                      <div className="text-sm text-gray-600 text-right">
                        {update.reason}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 次回更新タイマー */}
            <div className="bg-blue-50 rounded-lg border border-blue-200 p-6">
              <div className="flex items-center space-x-3 mb-3">
                <Clock className="h-5 w-5 text-blue-600" />
                <h3 className="text-md font-semibold text-blue-900">次回更新</h3>
              </div>
              <div className="text-2xl font-bold text-blue-900 mb-2">
                {timeUntilUpdate}
              </div>
              <p className="text-sm text-blue-700">
                次回の自動分析まで
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
