"use client";

import React, { useState, useEffect } from "react";
import { 
  X, 
  ArrowRight, 
  ArrowLeft, 
  CheckCircle, 
  Play, 
  Users, 
  Target, 
  BarChart3, 
  Shield,
  Settings,
  HelpCircle,
  Star,
} from "lucide-react";
import { TutorialPlaceholder } from "./PlaceholderComponents";

interface TutorialStep {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  action?: () => void;
}

interface TutorialSystemProps {
  onComplete?: () => void;
  onSkip?: () => void;
  onStartAnalysis?: () => void;
  onOpenSettings?: () => void;
  onOpenRoutine?: () => void;
}

export default function TutorialSystem({
  onComplete,
  onSkip,
  onStartAnalysis,
  onOpenSettings,
  onOpenRoutine,
}: TutorialSystemProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [steps, setSteps] = useState<TutorialStep[]>([
    {
      id: "welcome",
      title: "JQuants投資分析システムへようこそ",
      description: "AIを活用した株式投資分析システムです。5分で簡単に分析を実行できます。",
      completed: false,
    },
    {
      id: "symbol_selection",
      title: "銘柄選択",
      description: "分析したい銘柄を選択します。人気銘柄やお気に入りから選べます。",
      completed: false,
      action: () => {
        // 銘柄選択ページに遷移
        console.log("銘柄選択ページに遷移");
      },
    },
    {
      id: "analysis_execution",
      title: "分析実行",
      description: "AI予測分析を実行します。技術指標、センチメント分析、リスク評価を行います。",
      completed: false,
      action: onStartAnalysis,
    },
    {
      id: "results_review",
      title: "結果確認",
      description: "分析結果と予測値を確認します。チャートや指標で視覚的に確認できます。",
      completed: false,
    },
    {
      id: "risk_management",
      title: "リスク管理",
      description: "投資リスクと推奨アクションを確認します。個人のリスク許容度に応じて調整できます。",
      completed: false,
    },
    {
      id: "routine_setup",
      title: "5分ルーティン設定",
      description: "毎日の分析ルーティンを設定します。効率的な投資判断のための手順を自動化できます。",
      completed: false,
      action: onOpenRoutine,
    },
  ]);

  useEffect(() => {
    // 初回利用者判定
    const hasSeenTutorial = localStorage.getItem("jquants-tutorial-completed");
    const isFirstVisit = !hasSeenTutorial;
    
    if (isFirstVisit) {
      setIsVisible(true);
    }
  }, []);

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    localStorage.setItem("jquants-tutorial-completed", "true");
    setIsVisible(false);
    onComplete?.();
  };

  const handleSkip = () => {
    localStorage.setItem("jquants-tutorial-completed", "true");
    setIsVisible(false);
    onSkip?.();
  };

  const handleStepAction = (step: TutorialStep) => {
    if (step.action) {
      step.action();
    }
    // ステップを完了としてマーク
    setSteps(prev => prev.map(s => 
      s.id === step.id ? { ...s, completed: true } : s,
    ));
  };

  if (!isVisible) {
    return null;
  }

  const currentStepData = steps[currentStep];
  const progress = ((currentStep + 1) / steps.length) * 100;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* ヘッダー */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-full">
              <Users className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">チュートリアル</h2>
              <p className="text-sm text-gray-600">ステップ {currentStep + 1} / {steps.length}</p>
            </div>
          </div>
          <button
            onClick={handleSkip}
            className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* 進捗バー */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>進捗</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* メインコンテンツ */}
        <div className="p-6">
          <div className="text-center space-y-6">
            {/* ステップアイコン */}
            <div className="flex justify-center">
              <div className="p-4 bg-blue-100 rounded-full">
                {currentStepData.id === "welcome" && <Users className="h-8 w-8 text-blue-600" />}
                {currentStepData.id === "symbol_selection" && <Target className="h-8 w-8 text-blue-600" />}
                {currentStepData.id === "analysis_execution" && <BarChart3 className="h-8 w-8 text-blue-600" />}
                {currentStepData.id === "results_review" && <CheckCircle className="h-8 w-8 text-blue-600" />}
                {currentStepData.id === "risk_management" && <Shield className="h-8 w-8 text-blue-600" />}
                {currentStepData.id === "routine_setup" && <Settings className="h-8 w-8 text-blue-600" />}
              </div>
            </div>

            {/* ステップタイトルと説明 */}
            <div className="space-y-3">
              <h3 className="text-2xl font-bold text-gray-900">
                {currentStepData.title}
              </h3>
              <p className="text-gray-600 max-w-md mx-auto">
                {currentStepData.description}
              </p>
            </div>

            {/* アクションボタン */}
            {currentStepData.action && (
              <div className="pt-4">
                <button
                  onClick={() => handleStepAction(currentStepData)}
                  className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Play className="h-5 w-5 mr-2" />
                  今すぐ試す
                </button>
              </div>
            )}

            {/* ステップ一覧 */}
            <div className="pt-6">
              <h4 className="text-lg font-semibold text-gray-900 mb-4">チュートリアルステップ</h4>
              <div className="space-y-2">
                {steps.map((step, index) => (
                  <div
                    key={step.id}
                    className={`flex items-center space-x-3 p-3 rounded-lg transition-colors ${
                      index === currentStep
                        ? "bg-blue-50 border border-blue-200"
                        : step.completed
                        ? "bg-green-50 border border-green-200"
                        : "bg-gray-50 border border-gray-200"
                    }`}
                  >
                    <div className={`p-1 rounded-full ${
                      index === currentStep
                        ? "bg-blue-500"
                        : step.completed
                        ? "bg-green-500"
                        : "bg-gray-300"
                    }`}>
                      <CheckCircle className={`h-4 w-4 ${
                        index === currentStep || step.completed
                          ? "text-white"
                          : "text-gray-500"
                      }`} />
                    </div>
                    <div className="flex-1">
                      <div className={`text-sm font-medium ${
                        index === currentStep
                          ? "text-blue-800"
                          : step.completed
                          ? "text-green-800"
                          : "text-gray-700"
                      }`}>
                        {step.title}
                      </div>
                    </div>
                    {index === currentStep && (
                      <div className="text-xs text-blue-600 font-medium">
                        現在
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* フッター */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200">
          <button
            onClick={handleSkip}
            className="px-4 py-2 text-gray-600 text-sm font-medium rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors"
          >
            スキップ
          </button>
          
          <div className="flex items-center space-x-3">
            {currentStep > 0 && (
              <button
                onClick={handlePrevious}
                className="flex items-center px-4 py-2 text-gray-600 text-sm font-medium rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                前へ
              </button>
            )}
            
            <button
              onClick={handleNext}
              className="flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              {currentStep === steps.length - 1 ? "完了" : "次へ"}
              {currentStep < steps.length - 1 && <ArrowRight className="h-4 w-4 ml-2" />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// チュートリアル再表示用のフック
export function useTutorial() {
  const [showTutorial, setShowTutorial] = useState(false);

  const showTutorialAgain = () => {
    localStorage.removeItem("jquants-tutorial-completed");
    setShowTutorial(true);
  };

  const hideTutorial = () => {
    setShowTutorial(false);
  };

  return {
    showTutorial,
    showTutorialAgain,
    hideTutorial,
  };
}
