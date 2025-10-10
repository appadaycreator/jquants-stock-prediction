"use client";

import { useState, useEffect, useCallback } from "react";
import { 
  Clock, 
  Target, 
  TrendingUp, 
  RefreshCw, 
  CheckCircle, 
  AlertTriangle,
  Eye,
  BarChart3,
  Play,
  Pause,
  RotateCcw,
  Smartphone,
  Zap,
} from "lucide-react";

interface RoutineStep {
  id: string;
  title: string;
  description: string;
  estimatedTime: string;
  completed: boolean;
  required: boolean;
  category: "setup" | "analysis" | "review" | "action";
  action?: () => void;
}

interface EnhancedFiveMinRoutineProps {
  onAnalysisClick?: () => void;
  onSettingsClick?: () => void;
  onReportClick?: () => void;
  onTradeClick?: () => void;
  currentStep?: number;
  onStepComplete?: (stepId: string) => void;
}

export default function EnhancedFiveMinRoutine({
  onAnalysisClick,
  onSettingsClick,
  onReportClick,
  onTradeClick,
  currentStep = 0,
  onStepComplete,
}: EnhancedFiveMinRoutineProps) {
  const [steps, setSteps] = useState<RoutineStep[]>([
    {
      id: "symbol_selection",
      title: "銘柄選択",
      description: "分析したい銘柄を選択します",
      estimatedTime: "1分",
      completed: false,
      required: true,
      category: "setup",
      action: () => {
        console.log("銘柄選択を開始");
      },
    },
    {
      id: "data_validation",
      title: "データ確認",
      description: "選択した銘柄のデータが最新か確認します",
      estimatedTime: "30秒",
      completed: false,
      required: true,
      category: "setup",
      action: () => {
        console.log("データ確認を開始");
      },
    },
    {
      id: "analysis_execution",
      title: "分析実行",
      description: "AI予測分析を実行します",
      estimatedTime: "2分",
      completed: false,
      required: true,
      category: "analysis",
      action: onAnalysisClick,
    },
    {
      id: "prediction_review",
      title: "予測結果確認",
      description: "分析結果と予測値を確認します",
      estimatedTime: "1分",
      completed: false,
      required: true,
      category: "review",
      action: onReportClick,
    },
    {
      id: "risk_assessment",
      title: "リスク評価",
      description: "投資リスクと推奨アクションを確認します",
      estimatedTime: "30秒",
      completed: false,
      required: true,
      category: "review",
      action: () => {
        console.log("リスク評価を開始");
      },
    },
    {
      id: "investment_decision",
      title: "投資判断",
      description: "個人投資ダッシュボードで最終判断を行います",
      estimatedTime: "1分",
      completed: false,
      required: false,
      category: "action",
      action: onTradeClick,
    },
  ]);

  const [currentTime, setCurrentTime] = useState(new Date());
  const [startTime, setStartTime] = useState<Date | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  // モバイル判定
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  // タイマー更新
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // ステップ完了処理
  const handleStepComplete = useCallback((stepId: string) => {
    setSteps(prev => prev.map(step => 
      step.id === stepId ? { ...step, completed: true } : step,
    ));
    
    if (onStepComplete) {
      onStepComplete(stepId);
    }
  }, [onStepComplete]);

  // 全ステップ完了
  const handleCompleteAll = useCallback(() => {
    setSteps(prev => prev.map(step => ({ ...step, completed: true })));
  }, []);

  // ルーティン開始
  const handleStart = useCallback(() => {
    setStartTime(new Date());
    setIsRunning(true);
    setIsPaused(false);
  }, []);

  // ルーティン一時停止
  const handlePause = useCallback(() => {
    setIsPaused(true);
    setIsRunning(false);
  }, []);

  // ルーティン再開
  const handleResume = useCallback(() => {
    setIsPaused(false);
    setIsRunning(true);
  }, []);

  // ルーティンリセット
  const handleReset = useCallback(() => {
    setStartTime(null);
    setIsRunning(false);
    setIsPaused(false);
    setSteps(prev => prev.map(step => ({ ...step, completed: false })));
  }, []);

  // 経過時間計算
  const getElapsedTime = useCallback(() => {
    if (!startTime) return "00:00";
    const elapsed = Math.floor((currentTime.getTime() - startTime.getTime()) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    return `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
  }, [startTime, currentTime]);

  // 推定総時間計算
  const getEstimatedTotalTime = useCallback(() => {
    const totalMinutes = steps.reduce((total, step) => {
      const minutes = parseInt(step.estimatedTime.replace(/[^\d]/g, ""));
      return total + minutes;
    }, 0);
    return `${totalMinutes}分`;
  }, [steps]);

  // 完了率計算
  const getCompletionRate = useCallback(() => {
    const completedSteps = steps.filter(step => step.completed).length;
    return Math.round((completedSteps / steps.length) * 100);
  }, [steps]);

  return (
    <div className="max-w-4xl mx-auto p-6 pb-24 md:pb-6 space-y-6">
      {/* ヘッダー */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center space-x-2">
          <Clock className="h-8 w-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">5分ルーティン</h1>
        </div>
        <p className="text-gray-600 max-w-2xl mx-auto">
          毎日の投資分析を効率的に行うための5分間のルーティンです。
          各ステップを順番に実行して、確実に分析結果を取得しましょう。
        </p>
      </div>

      {/* 進捗サマリー */}
      <div className="bg-white rounded-lg border p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-4">
            <div className="bg-blue-100 p-3 rounded-lg">
              <Target className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">進捗状況</h2>
              <p className="text-sm text-gray-600">
                {steps.filter(s => s.completed).length} / {steps.length} ステップ完了
              </p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-blue-600">{getCompletionRate()}%</div>
            <div className="text-sm text-gray-500">完了率</div>
          </div>
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
          <div 
            className="bg-blue-600 h-3 rounded-full transition-all duration-500"
            style={{ width: `${getCompletionRate()}%` }}
          />
        </div>

        <div className="flex items-center justify-between text-sm text-gray-600">
          <div className="flex items-center space-x-2">
            <Clock className="h-4 w-4" />
            <span>経過時間: {getElapsedTime()}</span>
          </div>
          <div className="flex items-center space-x-2">
            <Target className="h-4 w-4" />
            <span>推定時間: {getEstimatedTotalTime()}</span>
          </div>
        </div>
      </div>

      {/* コントロールパネル */}
      <div className="bg-white rounded-lg border p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">ルーティン制御</h3>
          <div className="flex items-center space-x-2">
            {isMobile && (
              <div className="flex items-center space-x-1 text-sm text-gray-500">
                <Smartphone className="h-4 w-4" />
                <span>モバイル最適化</span>
              </div>
            )}
          </div>
        </div>
        
        <div className="flex flex-wrap gap-3">
          {!isRunning && !isPaused && (
            <button
              onClick={handleStart}
              className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 flex items-center space-x-2 transition-colors"
            >
              <Play className="h-5 w-5" />
              <span>開始</span>
            </button>
          )}
          
          {isRunning && !isPaused && (
            <button
              onClick={handlePause}
              className="bg-yellow-600 text-white px-6 py-3 rounded-lg hover:bg-yellow-700 flex items-center space-x-2 transition-colors"
            >
              <Pause className="h-5 w-5" />
              <span>一時停止</span>
            </button>
          )}
          
          {isPaused && (
            <button
              onClick={handleResume}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 flex items-center space-x-2 transition-colors"
            >
              <Play className="h-5 w-5" />
              <span>再開</span>
            </button>
          )}
          
          <button
            onClick={handleReset}
            className="bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 flex items-center space-x-2 transition-colors"
          >
            <RotateCcw className="h-5 w-5" />
            <span>リセット</span>
          </button>
          
          <button
            onClick={handleCompleteAll}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 flex items-center space-x-2 transition-colors"
          >
            <Zap className="h-5 w-5" />
            <span>全完了</span>
          </button>
        </div>
      </div>

      {/* ステップリスト */}
      <div className="space-y-4">
        {steps.map((step, index) => (
          <div
            key={step.id}
            className={`bg-white rounded-lg border p-6 transition-all duration-300 ${
              step.completed ? "border-green-200 bg-green-50" : 
              index === currentStep ? "border-blue-200 bg-blue-50" : 
              "border-gray-200"
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                  step.completed ? "bg-green-600 text-white" :
                  index === currentStep ? "bg-blue-600 text-white" :
                  "bg-gray-200 text-gray-600"
                }`}>
                  {step.completed ? <CheckCircle className="h-5 w-5" /> : index + 1}
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{step.title}</h3>
                  <p className="text-sm text-gray-600">{step.description}</p>
                  <div className="flex items-center space-x-4 mt-2">
                    <span className="text-xs text-gray-500">
                      推定時間: {step.estimatedTime}
                    </span>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      step.category === "setup" ? "bg-blue-100 text-blue-800" :
                      step.category === "analysis" ? "bg-green-100 text-green-800" :
                      step.category === "review" ? "bg-yellow-100 text-yellow-800" :
                      "bg-purple-100 text-purple-800"
                    }`}>
                      {step.category === "setup" ? "セットアップ" :
                       step.category === "analysis" ? "分析" :
                       step.category === "review" ? "レビュー" : "アクション"}
                    </span>
                    {step.required && (
                      <span className="text-xs text-red-600 font-medium">必須</span>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                {step.completed ? (
                  <div className="flex items-center space-x-1 text-green-600">
                    <CheckCircle className="h-5 w-5" />
                    <span className="text-sm font-medium">完了</span>
                  </div>
                ) : (
                  <button
                    onClick={() => {
                      if (step.action) step.action();
                      handleStepComplete(step.id);
                    }}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2 transition-colors"
                  >
                    <span>実行</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* モバイル最適化ヒント */}
      {isMobile && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Smartphone className="h-5 w-5 text-blue-600" />
            <h3 className="font-semibold text-blue-900">モバイル最適化</h3>
          </div>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• 縦スクロールのみで操作完了</li>
            <li>• 大きなボタンでタッチ操作を最適化</li>
            <li>• 5分以内に全ステップ完了</li>
            <li>• オフライン時もフォールバック機能</li>
          </ul>
        </div>
      )}

      {/* 完了メッセージ */}
      {getCompletionRate() === 100 && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
          <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-green-900 mb-2">
            お疲れ様でした！
          </h3>
          <p className="text-green-800">
            5分ルーティンが完了しました。今日の投資判断が完了しています。
          </p>
        </div>
      )}
    </div>
  );
}