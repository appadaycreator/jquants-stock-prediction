"use client";

import React, { useState, useEffect } from "react";
import { 
  CheckCircle, 
  Clock, 
  Play, 
  ArrowRight, 
  Target, 
  BarChart3, 
  Shield, 
  DollarSign,
  TrendingUp,
  AlertCircle,
  CheckCircle2,
  Timer,
  Users,
  Settings,
} from "lucide-react";
import { ChecklistPlaceholder } from "./PlaceholderComponents";

interface RoutineStep {
  id: string;
  title: string;
  description: string;
  estimatedTime: string;
  completed: boolean;
  action?: () => void;
  required: boolean;
  category: "setup" | "analysis" | "review" | "action";
}

interface FiveMinRoutineProps {
  onAnalysisClick?: () => void;
  onSettingsClick?: () => void;
  onReportClick?: () => void;
  onTradeClick?: () => void;
  currentStep?: string;
  onStepComplete?: (stepId: string) => void;
}

export default function FiveMinRoutine({
  onAnalysisClick,
  onSettingsClick,
  onReportClick,
  onTradeClick,
  currentStep,
  onStepComplete,
}: FiveMinRoutineProps) {
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
        // 銘柄選択ページに遷移
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
        // データ確認処理
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
        // リスク評価ページに遷移
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
  const [isRunning, setIsRunning] = useState(false);
  const [startTime, setStartTime] = useState<Date | null>(null);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const completedSteps = steps.filter(step => step.completed).length;
  const totalSteps = steps.length;
  const progress = totalSteps > 0 ? (completedSteps / totalSteps) * 100 : 0;

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "setup": return Settings;
      case "analysis": return BarChart3;
      case "review": return Target;
      case "action": return DollarSign;
      default: return CheckCircle;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case "setup": return "text-blue-600 bg-blue-50 border-blue-200";
      case "analysis": return "text-purple-600 bg-purple-50 border-purple-200";
      case "review": return "text-green-600 bg-green-50 border-green-200";
      case "action": return "text-orange-600 bg-orange-50 border-orange-200";
      default: return "text-gray-600 bg-gray-50 border-gray-200";
    }
  };

  const handleStepComplete = (stepId: string) => {
    setSteps(prev => prev.map(step => 
      step.id === stepId 
        ? { ...step, completed: !step.completed }
        : step,
    ));
    onStepComplete?.(stepId);
  };

  const handleStartRoutine = () => {
    setIsRunning(true);
    setStartTime(new Date());
  };

  const handleCompleteAll = () => {
    setSteps(prev => prev.map(step => ({ ...step, completed: true })));
  };

  const getElapsedTime = () => {
    if (!startTime) return "00:00";
    const elapsed = Math.floor((currentTime.getTime() - startTime.getTime()) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    return `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
  };

  const getEstimatedTotalTime = () => {
    const totalMinutes = steps.reduce((total, step) => {
      const minutes = parseInt(step.estimatedTime.replace(/[^\d]/g, ""));
      return total + minutes;
    }, 0);
    return `${totalMinutes}分`;
  };

  return (
    <div className="max-w-4xl mx-auto p-6 pb-24 md:pb-6 space-y-6">
      {/* ヘッダー */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center space-x-2">
          <Timer className="h-8 w-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">5分ルーティン</h1>
        </div>
        <p className="text-gray-600 max-w-2xl mx-auto">
          毎日の投資分析を効率的に行うための5分間のルーティンです。
          各ステップを順番に実行して、確実に分析結果を取得しましょう。
        </p>
      </div>

      {/* 進捗サマリー */}
      <div className="bg-white rounded-lg border p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{completedSteps}</div>
            <div className="text-sm text-gray-600">完了ステップ</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{totalSteps}</div>
            <div className="text-sm text-gray-600">総ステップ数</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{Math.round(progress)}%</div>
            <div className="text-sm text-gray-600">進捗率</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {isRunning ? getElapsedTime() : getEstimatedTotalTime()}
            </div>
            <div className="text-sm text-gray-600">
              {isRunning ? "経過時間" : "予想時間"}
            </div>
          </div>
        </div>

        {/* 進捗バー */}
        <div className="mt-4">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>全体の進捗</span>
            <span>{completedSteps}/{totalSteps}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className="bg-blue-500 h-3 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>

      {/* ルーティン開始ボタン */}
      {!isRunning && (
        <div className="text-center">
          <button
            onClick={handleStartRoutine}
            className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Play className="h-5 w-5 mr-2" />
            5分ルーティンを開始
          </button>
        </div>
      )}

      {/* ステップリスト */}
      <div className="space-y-4">
        {steps.map((step, index) => {
          const CategoryIcon = getCategoryIcon(step.category);
          const isCurrentStep = currentStep === step.id;
          
          return (
            <div
              key={step.id}
              className={`bg-white rounded-lg border-2 p-6 transition-all ${
                step.completed 
                  ? "border-green-200 bg-green-50" 
                  : isCurrentStep
                  ? "border-blue-300 bg-blue-50"
                  : "border-gray-200"
              }`}
            >
              <div className="flex items-start space-x-4">
                {/* ステップ番号 */}
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                  step.completed 
                    ? "bg-green-500 text-white" 
                    : isCurrentStep
                    ? "bg-blue-500 text-white"
                    : "bg-gray-300 text-gray-600"
                }`}>
                  {step.completed ? <CheckCircle2 className="h-4 w-4" /> : index + 1}
                </div>

                {/* ステップ内容 */}
                <div className="flex-1 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <CategoryIcon className={`h-5 w-5 ${
                        step.completed ? "text-green-600" : "text-gray-400"
                      }`} />
                      <h3 className={`text-lg font-semibold ${
                        step.completed ? "text-green-800" : "text-gray-900"
                      }`}>
                        {step.title}
                      </h3>
                      {step.required && (
                        <span className="text-xs bg-red-100 text-red-600 px-2 py-1 rounded-full">
                          必須
                        </span>
                      )}
                    </div>
                    <div className="flex items-center space-x-2">
                      <Clock className="h-4 w-4 text-gray-400" />
                      <span className="text-sm text-gray-500">{step.estimatedTime}</span>
                    </div>
                  </div>

                  <p className={`text-sm ${
                    step.completed ? "text-green-700" : "text-gray-600"
                  }`}>
                    {step.description}
                  </p>

                  {/* アクションボタン */}
                  <div className="flex items-center space-x-3">
                    {step.action && (
                      <button
                        onClick={step.action}
                        disabled={step.completed}
                        className={`inline-flex items-center px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                          step.completed
                            ? "bg-green-100 text-green-700 cursor-not-allowed"
                            : "bg-blue-600 text-white hover:bg-blue-700"
                        }`}
                      >
                        <Play className="h-4 w-4 mr-2" />
                        {step.completed ? "完了" : "実行"}
                      </button>
                    )}

                    <button
                      onClick={() => handleStepComplete(step.id)}
                      className={`inline-flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                        step.completed
                          ? "bg-green-100 text-green-700 hover:bg-green-200"
                          : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                      }`}
                    >
                      <CheckCircle className="h-4 w-4 mr-2" />
                      {step.completed ? "完了済み" : "完了にする"}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* クイックアクション */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">クイックアクション</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={handleCompleteAll}
            className="flex items-center justify-center px-4 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors"
          >
            <CheckCircle className="h-5 w-5 mr-2" />
            すべてのステップを完了にする
          </button>
          <button
            onClick={() => window.location.reload()}
            className="flex items-center justify-center px-4 py-3 bg-gray-600 text-white font-medium rounded-lg hover:bg-gray-700 transition-colors"
          >
            <ArrowRight className="h-5 w-5 mr-2" />
            ルーティンをリセット
          </button>
        </div>
      </div>

      {/* 完了メッセージ */}
      {completedSteps === totalSteps && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
          <div className="flex items-center justify-center space-x-2 mb-2">
            <CheckCircle className="h-6 w-6 text-green-600" />
            <h3 className="text-lg font-semibold text-green-800">おめでとうございます！</h3>
          </div>
          <p className="text-green-700">
            5分ルーティンが完了しました。分析結果を確認して、投資判断を行ってください。
          </p>
        </div>
      )}
    </div>
  );
}
