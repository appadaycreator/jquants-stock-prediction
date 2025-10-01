"use client";

import { useState, useEffect } from "react";
import { 
  CheckCircle, 
  Clock, 
  AlertCircle, 
  RefreshCw, 
  Target, 
  TrendingUp, 
  BarChart3, 
  ShoppingCart,
  Eye,
  Settings,
  Play,
  Pause,
  RotateCcw
} from "lucide-react";

interface Step {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  estimatedTime: string;
  status: "pending" | "running" | "completed" | "error";
  progress: number;
  advice?: string;
}

interface FiveMinRoutineStepsProps {
  currentStep: number;
  onStepComplete: (stepId: string) => void;
  onStepStart: (stepId: string) => void;
  onRoutineStart: () => void;
  onRoutinePause: () => void;
  onRoutineResume: () => void;
  onRoutineReset: () => void;
  isRunning: boolean;
  isPaused: boolean;
  totalProgress: number;
}

export default function FiveMinRoutineSteps({
  currentStep,
  onStepComplete,
  onStepStart,
  onRoutineStart,
  onRoutinePause,
  onRoutineResume,
  onRoutineReset,
  isRunning,
  isPaused,
  totalProgress,
}: FiveMinRoutineStepsProps) {
  const [steps, setSteps] = useState<Step[]>([
    {
      id: "watchlist",
      title: "ウォッチリスト更新",
      description: "監視銘柄の追加・削除・設定調整",
      icon: <Eye className="h-5 w-5" />,
      estimatedTime: "1分",
      status: "pending",
      progress: 0,
      advice: "新規銘柄は3-5銘柄までに絞り、既存銘柄の設定を優先的に確認しましょう"
    },
    {
      id: "prediction",
      title: "予測実行",
      description: "AI予測モデルによる価格予測分析",
      icon: <BarChart3 className="h-5 w-5" />,
      estimatedTime: "2分",
      status: "pending",
      progress: 0,
      advice: "予測精度が80%以上の銘柄を優先的に確認し、信頼度の低い銘柄は除外を検討"
    },
    {
      id: "signals",
      title: "シグナル確認",
      description: "売買シグナルとアラートの確認",
      icon: <TrendingUp className="h-5 w-5" />,
      estimatedTime: "1分",
      status: "pending",
      progress: 0,
      advice: "複数のシグナルが一致する銘柄を優先し、矛盾するシグナルは慎重に判断"
    },
    {
      id: "judgment",
      title: "売買判断",
      description: "最終的な投資判断とアクションプラン",
      icon: <Target className="h-5 w-5" />,
      estimatedTime: "1分",
      status: "pending",
      progress: 0,
      advice: "リスク許容度に応じてポジションサイズを調整し、損切りラインを明確に設定"
    }
  ]);

  // ステップの状態を更新
  useEffect(() => {
    setSteps(prevSteps => 
      prevSteps.map((step, index) => {
        if (index < currentStep) {
          return { ...step, status: "completed", progress: 100 };
        } else if (index === currentStep) {
          return { ...step, status: isRunning ? "running" : "pending", progress: step.progress };
        } else {
          return { ...step, status: "pending", progress: 0 };
        }
      })
    );
  }, [currentStep, isRunning]);

  const handleStepClick = (stepId: string, stepIndex: number) => {
    if (stepIndex <= currentStep) {
      onStepStart(stepId);
    }
  };

  const getStepStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-100 border-green-300 text-green-800";
      case "running":
        return "bg-blue-100 border-blue-300 text-blue-800";
      case "error":
        return "bg-red-100 border-red-300 text-red-800";
      default:
        return "bg-gray-100 border-gray-300 text-gray-600";
    }
  };

  const getStepStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case "running":
        return <RefreshCw className="h-5 w-5 text-blue-600 animate-spin" />;
      case "error":
        return <AlertCircle className="h-5 w-5 text-red-600" />;
      default:
        return <Clock className="h-5 w-5 text-gray-500" />;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg border p-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">5分ルーチン</h2>
          <p className="text-sm text-gray-600">効率的な投資判断のための4ステップ</p>
        </div>
        <div className="flex items-center space-x-2">
          {!isRunning && !isPaused && (
            <button
              onClick={onRoutineStart}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Play className="h-4 w-4 mr-2" />
              開始
            </button>
          )}
          {isRunning && !isPaused && (
            <button
              onClick={onRoutinePause}
              className="flex items-center px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
            >
              <Pause className="h-4 w-4 mr-2" />
              一時停止
            </button>
          )}
          {isPaused && (
            <button
              onClick={onRoutineResume}
              className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              <Play className="h-4 w-4 mr-2" />
              再開
            </button>
          )}
          <button
            onClick={onRoutineReset}
            className="flex items-center px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            リセット
          </button>
        </div>
      </div>

      {/* 全体進捗バー */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">全体進捗</span>
          <span className="text-sm text-gray-600">{totalProgress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className="bg-blue-600 h-3 rounded-full transition-all duration-500"
            style={{ width: `${totalProgress}%` }}
          />
        </div>
      </div>

      {/* ステップ一覧 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {steps.map((step, index) => (
          <div
            key={step.id}
            onClick={() => handleStepClick(step.id, index)}
            className={`p-4 rounded-lg border-2 cursor-pointer transition-all duration-200 hover:shadow-md ${
              getStepStatusColor(step.status)
            } ${index <= currentStep ? "cursor-pointer" : "cursor-not-allowed opacity-50"}`}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                {getStepStatusIcon(step.status)}
                <span className="font-medium">{step.title}</span>
              </div>
              <span className="text-xs bg-white bg-opacity-50 px-2 py-1 rounded">
                {step.estimatedTime}
              </span>
            </div>
            
            <p className="text-sm mb-3 opacity-90">{step.description}</p>
            
            {/* 進捗バー */}
            <div className="w-full bg-white bg-opacity-50 rounded-full h-2 mb-3">
              <div
                className="bg-current h-2 rounded-full transition-all duration-300"
                style={{ width: `${step.progress}%` }}
              />
            </div>
            
            {/* アドバイス */}
            {step.advice && (
              <div className="text-xs opacity-75 bg-white bg-opacity-30 p-2 rounded">
                💡 {step.advice}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* 現在のステップ詳細 */}
      {currentStep < steps.length && (
        <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex items-center space-x-2 mb-2">
            <Settings className="h-5 w-5 text-blue-600" />
            <span className="font-medium text-blue-900">現在のステップ</span>
          </div>
          <p className="text-blue-800">
            {steps[currentStep]?.title}: {steps[currentStep]?.description}
          </p>
          {steps[currentStep]?.advice && (
            <p className="text-sm text-blue-700 mt-2">
              💡 {steps[currentStep].advice}
            </p>
          )}
        </div>
      )}

      {/* 完了時のメッセージ */}
      {currentStep >= steps.length && (
        <div className="mt-6 p-4 bg-green-50 rounded-lg border border-green-200">
          <div className="flex items-center space-x-2 mb-2">
            <CheckCircle className="h-5 w-5 text-green-600" />
            <span className="font-medium text-green-900">5分ルーチン完了！</span>
          </div>
          <p className="text-green-800">
            お疲れ様でした！今日の投資判断が完了しました。結果を確認して、必要に応じてアクションを実行してください。
          </p>
        </div>
      )}
    </div>
  );
}
