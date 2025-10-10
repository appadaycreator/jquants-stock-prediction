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
      id: "choose",
      title: "銘柄を選ぶ",
      description: "ウォッチ銘柄から今日の候補を1つ選択",
      estimatedTime: "1分",
      completed: false,
      required: true,
      category: "setup",
      action: () => {
        console.log("銘柄選択");
      },
    },
    {
      id: "analyze",
      title: "AIで分析",
      description: "最新データで予測・リスクを自動分析",
      estimatedTime: "3分",
      completed: false,
      required: true,
      category: "analysis",
      action: onAnalysisClick,
    },
    {
      id: "decide",
      title: "行動を決める",
      description: "買い/保留/売りの判断を1つ選ぶ",
      estimatedTime: "1分",
      completed: false,
      required: true,
      category: "action",
      action: onTradeClick,
    },
  ]);

  const [currentTime, setCurrentTime] = useState(new Date());
  const [startTime, setStartTime] = useState<Date | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);

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
    setActiveIndex(prev => Math.min(prev + 1, steps.length - 1));
  }, [onStepComplete, steps.length]);

  // 全ステップ完了
  const handleCompleteAll = useCallback(() => {
    setSteps(prev => prev.map(step => ({ ...step, completed: true })));
  }, []);

  // ルーティン開始
  const handleStart = useCallback(() => {
    setStartTime(new Date());
    setIsRunning(true);
    setIsPaused(false);
    setActiveIndex(0);
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
    <div className="relative z-30 max-w-4xl mx-auto p-6 pb-24 md:pb-6 space-y-6">
      {/* ヘッダー */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center space-x-2">
          <Clock className="h-8 w-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">5分ルーティン</h1>
        </div>
        <p className="text-gray-700 max-w-2xl mx-auto">
          今日すべきことだけ。<span className="font-semibold">銘柄を選ぶ → AIで分析 → 行動を決める</span>の3ステップ。
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
        
        <div className="flex flex-wrap gap-3 relative z-50">
          {!isRunning ? (
            <button
              onClick={handleStart}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 flex items-center space-x-2 transition-colors"
            >
              <Play className="h-5 w-5" />
              <span>3ステップを開始</span>
            </button>
          ) : (
            <>
              <button
                onClick={() => {
                  const step = steps[activeIndex];
                  if (step?.action) step.action();
                  handleStepComplete(step.id);
                }}
                className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 flex items-center space-x-2 transition-colors"
              >
                <Play className="h-5 w-5" />
                <span>{activeIndex === 0 ? "銘柄を選ぶ" : activeIndex === 1 ? "AIで分析" : "行動を決める"}</span>
              </button>
              <button
                onClick={() => handleStepComplete(steps[activeIndex].id)}
                className="bg-gray-100 text-gray-800 px-4 py-3 rounded-lg hover:bg-gray-200 transition-colors"
              >
                スキップ
              </button>
              {!isPaused ? (
                <button onClick={handlePause} className="bg-yellow-600 text-white px-4 py-3 rounded-lg hover:bg-yellow-700 transition-colors">一時停止</button>
              ) : (
                <button onClick={handleResume} className="bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 transition-colors">再開</button>
              )}
              <button onClick={handleReset} className="bg-gray-600 text-white px-4 py-3 rounded-lg hover:bg-gray-700 transition-colors">リセット</button>
              <button onClick={handleCompleteAll} className="bg-blue-100 text-blue-800 px-4 py-3 rounded-lg hover:bg-blue-200 transition-colors">一括完了</button>
            </>
          )}
        </div>
      </div>

      {/* ステップリスト */}
      <div className="space-y-4">
        {steps.map((step, index) => (
          <div
            key={step.id}
            className={`bg-white rounded-lg border p-6 transition-all duration-300 ${
              step.completed ? "border-green-200 bg-green-50" : 
              index === activeIndex ? "border-blue-200 bg-blue-50" : 
              "border-gray-200"
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                  step.completed ? "bg-green-600 text-white" :
                  index === activeIndex ? "bg-blue-600 text-white" :
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
              
              <div className="flex items-center space-x-2 relative z-50">
                {step.completed ? (
                  <div className="flex items-center space-x-1 text-green-600">
                    <CheckCircle className="h-5 w-5" />
                    <span className="text-sm font-medium">完了</span>
                  </div>
                ) : (
                  <div className="text-sm text-gray-500">上のボタンで進めます</div>
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