"use client";

import React, { useState } from "react";
import { Play, CheckCircle, AlertCircle, RefreshCw, Settings, BarChart3, TrendingUp, Brain, Zap, History, Clock } from "lucide-react";
import { useAnalysisWithSettings } from "@/hooks/useAnalysisWithSettings";
import { fetchJson } from "@/lib/fetcher";

interface AnalysisConfig {
  type: "ultra_fast" | "comprehensive" | "symbols" | "trading" | "sentiment";
  name: string;
  description: string;
  icon: React.ReactNode;
  estimatedTime: string;
}

const analysisConfigs: AnalysisConfig[] = [
  {
    type: "ultra_fast",
    name: "超高速分析",
    description: "1日5分で完結する最適化された分析",
    icon: <Zap className="w-5 h-5" />,
    estimatedTime: "1-2分",
  },
  {
    type: "comprehensive",
    name: "包括的分析",
    description: "データ取得から予測まで全工程を自動実行",
    icon: <BarChart3 className="w-5 h-5" />,
    estimatedTime: "3-5分",
  },
  {
    type: "symbols",
    name: "銘柄分析",
    description: "指定銘柄の詳細分析を実行",
    icon: <TrendingUp className="w-5 h-5" />,
    estimatedTime: "2-3分",
  },
  {
    type: "trading",
    name: "トレーディング分析",
    description: "統合トレーディングシステムによる分析",
    icon: <Zap className="w-5 h-5" />,
    estimatedTime: "4-6分",
  },
  {
    type: "sentiment",
    name: "感情分析",
    description: "ニュース感情分析による予測",
    icon: <Brain className="w-5 h-5" />,
    estimatedTime: "3-4分",
  },
];

interface AnalysisHistory {
  id: string;
  type: string;
  timestamp: string;
  duration: string;
  status: "success" | "error";
  result?: any;
  error?: string;
}

interface OneClickAnalysisProps {
  onAnalysisComplete?: (result: any) => void;
  onAnalysisStart?: () => void;
}

export default function OneClickAnalysis({ onAnalysisComplete, onAnalysisStart }: OneClickAnalysisProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedType, setSelectedType] = useState<AnalysisConfig["type"]>("ultra_fast");
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState("");
  const [showConfig, setShowConfig] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [elapsedTime, setElapsedTime] = useState<string>("00:00");
  const [analysisHistory, setAnalysisHistory] = useState<AnalysisHistory[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [previousResult, setPreviousResult] = useState<any>(null);

  // 設定連携フック
  const { 
    runAnalysisWithSettings, 
    isAnalyzing: settingsAnalyzing, 
    analysisProgress: settingsProgress, 
    analysisStatus: settingsStatus,
    getAnalysisDescription, 
  } = useAnalysisWithSettings();

  const selectedConfig = analysisConfigs.find(config => config.type === selectedType);

  // 履歴の保存
  const saveAnalysisHistory = (history: AnalysisHistory) => {
    const newHistory = [history, ...analysisHistory.slice(0, 9)]; // 最新10件を保持
    setAnalysisHistory(newHistory);
    localStorage.setItem("analysisHistory", JSON.stringify(newHistory));
  };

  // 履歴の読み込み
  const loadAnalysisHistory = () => {
    const saved = localStorage.getItem("analysisHistory");
    if (saved) {
      try {
        const history = JSON.parse(saved);
        setAnalysisHistory(history);
        if (history.length > 0) {
          setPreviousResult(history[0].result);
        }
      } catch (error) {
        console.error("履歴読み込みエラー:", error);
      }
    }
  };

  // コンポーネントマウント時に履歴を読み込み
  React.useEffect(() => {
    loadAnalysisHistory();
  }, []);

  const startAnalysis = async () => {
    try {
      setIsAnalyzing(true);
      setProgress(0);
      setStatus("ジョブを作成しています...");
      setError(null);
      setAnalysisResult(null);
      setElapsedTime("00:00");

      onAnalysisStart?.();

      // 冪等化用トークン（セッションに一意）
      const clientTokenKey = "analysis:client_token";
      let clientToken = localStorage.getItem(clientTokenKey);
      if (!clientToken) {
        clientToken = `client_${crypto.randomUUID?.() || Math.random().toString(36).slice(2)}`;
        localStorage.setItem(clientTokenKey, clientToken);
      }

      // GitHub Pages静的サイト環境では直接ローカル分析を実行
      const isStaticSite = process.env.NODE_ENV === "production" && typeof window !== "undefined";
      
      if (isStaticSite) {
        // 静的サイト環境: 直接ローカル分析を実行
        setStatus("ローカル分析を実行中...");
        try {
          const sim = await runAnalysisWithSettings({ analysisType: selectedType, useSettings: true });
          if (!sim.success) {
            throw new Error(sim.error || "分析実行に失敗しました");
          }
          setStatus("分析が完了しました！");
          setProgress(100);
          setAnalysisResult(sim.result);
          onAnalysisComplete?.(sim.result);
          const localId = `local_${Date.now()}`;
          setAnalysisId(localId);
          saveAnalysisHistory({ id: localId, type: selectedType, timestamp: new Date().toISOString(), duration: elapsedTime, status: "success", result: sim.result });
          setIsAnalyzing(false);
          return;
        } catch (error) {
          setStatus(`分析エラー: ${error instanceof Error ? error.message : "不明なエラー"}`);
          setError(`分析の実行に失敗しました。詳細: ${error instanceof Error ? error.message : "不明なエラー"}`);
          setIsAnalyzing(false);
          throw error;
        }
      }

      // 開発環境: APIエンドポイントを試行
      let job_id: string | undefined;
      try {
        const response = await fetchJson<{ job_id: string }>(
          "/api/analyze",
          { timeout: 10000, json: { client_token: clientToken } },
        );
        job_id = response.job_id;
        if (!job_id) return;
        setAnalysisId(job_id);
        setStatus("キューに投入しました。進捗を監視します...");
      } catch (e) {
        // APIエンドポイントが利用できない場合のフォールバック
        setStatus("APIが利用できないためローカル分析に切り替えます...");
        const sim = await runAnalysisWithSettings({ analysisType: selectedType, useSettings: true });
        if (!sim.success) {
          throw new Error(sim.error || "分析実行に失敗しました");
        }
        setStatus("分析が完了しました！（ローカル）");
        setProgress(100);
        setAnalysisResult(sim.result);
        onAnalysisComplete?.(sim.result);
        const localId = `local_${Date.now()}`;
        setAnalysisId(localId);
        saveAnalysisHistory({ id: localId, type: selectedType, timestamp: new Date().toISOString(), duration: elapsedTime, status: "success", result: sim.result });
        setIsAnalyzing(false);
        return;
      }

      // 2) ポーリング: 1.5s間隔 最大3分
      const startedAt = Date.now();
      const pollInterval = 1500;
      const timeoutMs = 3 * 60 * 1000;

      const poll = async (): Promise<void> => {
        try {
          const res = await fetchJson<{ status: string; progress?: number; result_url?: string; error?: string }>(
            `/api/jobs/${job_id}`,
            { timeout: 8000 },
          );
          const prog = Math.min(99, Math.max(0, Math.floor(res.progress ?? 0)));
          setProgress(prog);
          setStatus(res.status === "running" ? "分析を実行中..." : res.status === "queued" ? "待機中..." : status);

          if (res.status === "succeeded") {
            setProgress(100);
            setStatus("分析が完了しました！");
            const resultPayload = { message: "分析が完了しました", resultUrl: res.result_url, webDataGenerated: true };
            setAnalysisResult(resultPayload);
            onAnalysisComplete?.(resultPayload);
            saveAnalysisHistory({ id: job_id, type: selectedType, timestamp: new Date().toISOString(), duration: elapsedTime, status: "success", result: resultPayload });
            setIsAnalyzing(false);
            return;
          }
          if (res.status === "failed") {
            const errMsg = res.error || "サーバー側でエラーが発生しました";
            throw new Error(errMsg);
          }

          if (Date.now() - startedAt > timeoutMs) {
            throw new Error("タイムアウトしました（3分）");
          }

          setTimeout(poll, pollInterval);
        } catch (err) {
          // フェールオーバー: 前回結果
          const last = analysisHistory[0]?.result;
          setError(err instanceof Error ? err.message : "不明なエラー");
          setStatus("失敗しました。前回結果にフォールバックできます");
          if (last) {
            setAnalysisResult(last);
          }
          // 履歴保存
          saveAnalysisHistory({ id: job_id, type: selectedType, timestamp: new Date().toISOString(), duration: elapsedTime, status: "error", error: err instanceof Error ? err.message : "Unknown" });
          setIsAnalyzing(false);
        }
      };

      setTimeout(poll, pollInterval);
    } catch (err) {
      setError(err instanceof Error ? err.message : "不明なエラーが発生しました");
      setStatus("分析に失敗しました");
      setIsAnalyzing(false);
    }
  };

  const resetAnalysis = () => {
    setIsAnalyzing(false);
    setProgress(0);
    setStatus("");
    setError(null);
    setAnalysisResult(null);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <Play className="w-6 h-6 text-blue-600" />
          ワンクリック分析実行
        </h2>
        <div className="flex gap-2">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
            title="分析履歴"
          >
            <History className="w-5 h-5" />
          </button>
          <button
            onClick={() => setShowConfig(!showConfig)}
            className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
            title="設定"
          >
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </div>

      {showConfig && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-semibold text-gray-800 mb-3">分析タイプを選択</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {analysisConfigs.map((config) => (
              <button
                key={config.type}
                onClick={() => setSelectedType(config.type)}
                className={`p-3 rounded-lg border-2 transition-all ${
                  selectedType === config.type
                    ? "border-blue-500 bg-blue-50"
                    : "border-gray-200 hover:border-gray-300"
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  {config.icon}
                  <span className="font-medium">{config.name}</span>
                </div>
                <p className="text-sm text-gray-600">{config.description}</p>
                <p className="text-xs text-gray-500 mt-1">予想時間: {config.estimatedTime}</p>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 履歴表示パネル */}
      {showHistory && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
            <History className="w-5 h-5" />
            分析履歴
          </h3>
          {analysisHistory.length === 0 ? (
            <p className="text-gray-500 text-sm">分析履歴がありません</p>
          ) : (
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {analysisHistory.map((history, index) => (
                <div
                  key={history.id}
                  className={`p-3 rounded-lg border ${
                    history.status === "success"
                      ? "border-green-200 bg-green-50"
                      : "border-red-200 bg-red-50"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {history.status === "success" ? (
                        <CheckCircle className="w-4 h-4 text-green-600" />
                      ) : (
                        <AlertCircle className="w-4 h-4 text-red-600" />
                      )}
                      <span className="font-medium text-sm">
                        {analysisConfigs.find(c => c.type === history.type)?.name || history.type}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <Clock className="w-3 h-3" />
                      {new Date(history.timestamp).toLocaleString("ja-JP")}
                    </div>
                  </div>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-xs text-gray-600">
                      実行時間: {history.duration}
                    </span>
                    {index === 0 && history.status === "success" && (
                      <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        最新結果
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 前回結果との比較表示 */}
      {previousResult && analysisResult && (
        <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h3 className="font-semibold text-blue-800 mb-3 flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            前回結果との比較
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium text-blue-700 mb-2">前回の結果</h4>
              <div className="text-sm text-blue-600">
                <p>実行日時: {new Date(analysisHistory[0]?.timestamp).toLocaleString("ja-JP")}</p>
                <p>実行時間: {analysisHistory[0]?.duration}</p>
                <p>分析タイプ: {analysisConfigs.find(c => c.type === analysisHistory[0]?.type)?.name}</p>
              </div>
            </div>
            <div>
              <h4 className="font-medium text-green-700 mb-2">今回の結果</h4>
              <div className="text-sm text-green-600">
                <p>実行日時: {new Date().toLocaleString("ja-JP")}</p>
                <p>実行時間: {elapsedTime}</p>
                <p>分析タイプ: {selectedConfig?.name}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="space-y-4">
        {/* 設定情報表示 */}
        <div className="bg-gray-50 rounded-lg p-4 mb-4">
          <div className="flex items-center mb-2">
            <Settings className="w-4 h-4 text-gray-600 mr-2" />
            <h4 className="font-medium text-gray-800">実行設定</h4>
          </div>
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

        {/* 分析実行ボタン */}
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-gray-800">
              {selectedConfig?.name}を実行
            </h3>
            <p className="text-sm text-gray-600">
              {selectedConfig?.description}
            </p>
            <p className="text-xs text-gray-500">
              予想時間: {selectedConfig?.estimatedTime}
            </p>
          </div>
          <button
            onClick={startAnalysis}
            disabled={isAnalyzing}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              isAnalyzing
                ? "bg-gray-400 cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-700 text-white"
            }`}
          >
            {isAnalyzing ? (
              <div className="flex items-center gap-2">
                <RefreshCw className="w-4 h-4 animate-spin" />
                実行中...
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Play className="w-4 h-4" />
                分析実行
              </div>
            )}
          </button>
        </div>

        {/* 進捗表示 */}
        {isAnalyzing && (
          <div className="space-y-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-blue-800">分析実行中</span>
              <div className="flex items-center gap-2">
                <span className="text-sm text-blue-600">経過時間: {elapsedTime}</span>
                <span className="text-sm font-medium text-blue-800">{progress}%</span>
              </div>
            </div>
            
            <div className="w-full bg-blue-100 rounded-full h-3">
              <div
                className="bg-blue-600 h-3 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${progress}%` }}
              />
            </div>
            
            <div className="flex items-center gap-2">
              <RefreshCw className="w-4 h-4 animate-spin text-blue-600" />
              <p className="text-sm text-blue-700">{status}</p>
            </div>
            
            {analysisId && (
              <p className="text-xs text-blue-500">
                分析ID: {analysisId}
              </p>
            )}
          </div>
        )}

        {/* エラー表示 */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center gap-2 text-red-800">
              <AlertCircle className="w-5 h-5" />
              <span className="font-medium">エラーが発生しました</span>
            </div>
            <p className="text-red-700 text-sm mt-1">{error}</p>
            <button
              onClick={resetAnalysis}
              className="mt-2 text-red-600 hover:text-red-800 text-sm underline"
            >
              再試行
            </button>
          </div>
        )}

        {/* 成功結果表示 */}
        {analysisResult && (
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center gap-2 text-green-800">
              <CheckCircle className="w-5 h-5" />
              <span className="font-medium">分析完了</span>
            </div>
            <p className="text-green-700 text-sm mt-1">
              {analysisResult.message}
            </p>
            {analysisResult.webDataGenerated && (
              <p className="text-green-600 text-xs mt-1">
                ✅ Webデータも更新されました
              </p>
            )}
            <button
              onClick={resetAnalysis}
              className="mt-2 text-green-600 hover:text-green-800 text-sm underline"
            >
              新しい分析を実行
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
