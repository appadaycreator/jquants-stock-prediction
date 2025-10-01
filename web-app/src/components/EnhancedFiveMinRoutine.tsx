"use client";

import { useState, useEffect } from "react";
import FiveMinRoutineSteps from "./FiveMinRoutineSteps";
import EnhancedJudgmentPanel from "./EnhancedJudgmentPanel";
import EnhancedWatchlistModal from "./EnhancedWatchlistModal";
import BatchUpdateController from "./BatchUpdateController";
import TimeManagementHelper from "./TimeManagementHelper";
import { 
  Eye, 
  BarChart3, 
  TrendingUp, 
  Target,
  Clock,
  Settings,
  Play,
  Pause,
  RotateCcw
} from "lucide-react";

interface WatchlistItem {
  symbol: string;
  name: string;
  currentPrice: number;
  change: number;
  changePercent: number;
  addedDate: string;
  notes?: string;
  priority: "high" | "medium" | "low";
  alerts: {
    priceTarget?: number;
    stopLoss?: number;
    volumeAlert?: boolean;
  };
}

interface PredictionData {
  symbol: string;
  name: string;
  currentPrice: number;
  predictedPrice: number;
  confidence: number;
  recommendation: "STRONG_BUY" | "BUY" | "HOLD" | "SELL" | "STRONG_SELL";
  reasons: string[];
  riskLevel: "LOW" | "MEDIUM" | "HIGH";
  timeframe: string;
  technicalSignals: {
    trend: "bullish" | "bearish" | "neutral";
    momentum: "strong" | "weak" | "neutral";
    volatility: "low" | "medium" | "high";
  };
  fundamentalFactors: {
    earnings: "positive" | "negative" | "neutral";
    growth: "high" | "medium" | "low";
    valuation: "undervalued" | "fair" | "overvalued";
  };
}

export default function EnhancedFiveMinRoutine() {
  const [currentStep, setCurrentStep] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [totalProgress, setTotalProgress] = useState(0);
  const [showWatchlistModal, setShowWatchlistModal] = useState(false);
  const [showBatchUpdate, setShowBatchUpdate] = useState(false);
  const [showTimeHelper, setShowTimeHelper] = useState(false);
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [predictions, setPredictions] = useState<PredictionData[]>([]);
  const [stepTimes, setStepTimes] = useState<Record<string, number>>({});

  const steps = [
    { id: "watchlist", title: "ウォッチリスト更新", icon: <Eye className="h-5 w-5" /> },
    { id: "prediction", title: "予測実行", icon: <BarChart3 className="h-5 w-5" /> },
    { id: "signals", title: "シグナル確認", icon: <TrendingUp className="h-5 w-5" /> },
    { id: "judgment", title: "売買判断", icon: <Target className="h-5 w-5" /> }
  ];

  // ステップ完了時の処理
  const handleStepComplete = (stepId: string) => {
    const stepIndex = steps.findIndex(step => step.id === stepId);
    if (stepIndex < steps.length - 1) {
      setCurrentStep(stepIndex + 1);
    } else {
      setIsRunning(false);
      setTotalProgress(100);
    }
  };

  // ステップ開始時の処理
  const handleStepStart = (stepId: string) => {
    const stepIndex = steps.findIndex(step => step.id === stepId);
    setCurrentStep(stepIndex);
    setIsRunning(true);
    setIsPaused(false);
  };

  // ルーティン開始
  const handleRoutineStart = () => {
    setCurrentStep(0);
    setIsRunning(true);
    setIsPaused(false);
    setTotalProgress(0);
  };

  // ルーティン一時停止
  const handleRoutinePause = () => {
    setIsPaused(true);
    setIsRunning(false);
  };

  // ルーティン再開
  const handleRoutineResume = () => {
    setIsPaused(false);
    setIsRunning(true);
  };

  // ルーティンリセット
  const handleRoutineReset = () => {
    setCurrentStep(0);
    setIsRunning(false);
    setIsPaused(false);
    setTotalProgress(0);
    setStepTimes({});
  };

  // 時間更新
  const handleTimeUpdate = (step: string, actualTime: number) => {
    setStepTimes(prev => ({ ...prev, [step]: actualTime }));
  };

  // ヒントクリック
  const handleTipClick = (tip: string) => {
    console.log("Tip clicked:", tip);
    // ヒントの詳細表示やアクション実行
  };

  // 判断パネルのアクション
  const handleActionClick = (symbol: string, action: string) => {
    console.log("Action clicked:", symbol, action);
    // アクション実行処理
  };

  const handleDetailClick = (symbol: string) => {
    console.log("Detail clicked:", symbol);
    // 詳細分析ページへの遷移
  };

  // ウォッチリスト更新
  const handleWatchlistUpdate = (updatedWatchlist: WatchlistItem[]) => {
    setWatchlist(updatedWatchlist);
  };

  // インポート処理
  const handleImport = (file: File) => {
    console.log("Import file:", file);
    // CSVファイルの解析とウォッチリスト更新
  };

  // エクスポート処理
  const handleExport = () => {
    console.log("Export watchlist");
    // ウォッチリストのCSVエクスポート
  };

  // 一括更新完了
  const handleUpdateComplete = (results: any[]) => {
    console.log("Batch update complete:", results);
    setShowBatchUpdate(false);
  };

  // 進捗更新
  const handleProgressChange = (progress: any) => {
    console.log("Progress update:", progress);
  };

  // 進捗計算
  useEffect(() => {
    const progress = (currentStep / steps.length) * 100;
    setTotalProgress(progress);
  }, [currentStep, steps.length]);

  return (
    <div className="space-y-6">
      {/* メインルーティンステップ */}
      <FiveMinRoutineSteps
        currentStep={currentStep}
        onStepComplete={handleStepComplete}
        onStepStart={handleStepStart}
        onRoutineStart={handleRoutineStart}
        onRoutinePause={handleRoutinePause}
        onRoutineResume={handleRoutineResume}
        onRoutineReset={handleRoutineReset}
        isRunning={isRunning}
        isPaused={isPaused}
        totalProgress={totalProgress}
      />

      {/* 時間管理ヘルパー */}
      {isRunning && (
        <TimeManagementHelper
          currentStep={steps[currentStep]?.id || ""}
          onTimeUpdate={handleTimeUpdate}
          onTipClick={handleTipClick}
        />
      )}

      {/* 判断パネル */}
      {currentStep >= 2 && predictions.length > 0 && (
        <EnhancedJudgmentPanel
          predictions={predictions}
          onActionClick={handleActionClick}
          onDetailClick={handleDetailClick}
        />
      )}

      {/* コントロールパネル */}
      <div className="bg-white rounded-lg shadow-lg border p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">5分ルーチンコントロール</h3>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowTimeHelper(!showTimeHelper)}
              className="flex items-center px-3 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
            >
              <Clock className="h-4 w-4 mr-2" />
              時間管理
            </button>
            <button
              onClick={() => setShowWatchlistModal(true)}
              className="flex items-center px-3 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors"
            >
              <Eye className="h-4 w-4 mr-2" />
              ウォッチリスト
            </button>
            <button
              onClick={() => setShowBatchUpdate(true)}
              className="flex items-center px-3 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors"
            >
              <Settings className="h-4 w-4 mr-2" />
              一括更新
            </button>
          </div>
        </div>

        {/* ステップ状況 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {steps.map((step, index) => (
            <div
              key={step.id}
              className={`p-3 rounded-lg border-2 ${
                index < currentStep
                  ? "bg-green-100 border-green-300 text-green-800"
                  : index === currentStep
                  ? "bg-blue-100 border-blue-300 text-blue-800"
                  : "bg-gray-100 border-gray-300 text-gray-600"
              }`}
            >
              <div className="flex items-center space-x-2 mb-1">
                {step.icon}
                <span className="font-medium text-sm">{step.title}</span>
              </div>
              <div className="text-xs">
                {index < currentStep ? "完了" : index === currentStep ? "実行中" : "待機中"}
              </div>
              {stepTimes[step.id] && (
                <div className="text-xs opacity-75">
                  {Math.floor(stepTimes[step.id] / 60)}分{stepTimes[step.id] % 60}秒
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* モーダル */}
      {showWatchlistModal && (
        <EnhancedWatchlistModal
          isOpen={showWatchlistModal}
          onClose={() => setShowWatchlistModal(false)}
          watchlist={watchlist}
          onWatchlistUpdate={handleWatchlistUpdate}
          onImport={handleImport}
          onExport={handleExport}
        />
      )}

      {showBatchUpdate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">一括更新</h2>
                <button
                  onClick={() => setShowBatchUpdate(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              <BatchUpdateController
                symbols={watchlist.map(item => item.symbol)}
                onUpdateComplete={handleUpdateComplete}
                onProgressChange={handleProgressChange}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
