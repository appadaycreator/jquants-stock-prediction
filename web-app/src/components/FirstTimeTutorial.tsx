"use client";

import { useState, useEffect } from "react";
import { X, Play, Database, BarChart3, Target, CheckCircle, ArrowRight, RefreshCw } from "lucide-react";

interface FirstTimeTutorialProps {
  isVisible: boolean;
  onClose: () => void;
  onStartAnalysis: () => void;
  onStartDataUpdate: () => void;
}

export default function FirstTimeTutorial({
  isVisible,
  onClose,
  onStartAnalysis,
  onStartDataUpdate,
}: FirstTimeTutorialProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [isCompleted, setIsCompleted] = useState(false);

  const steps = [
    {
      id: "welcome",
      title: "J-Quants株価予測システムへようこそ！",
      description: "AIを活用した株価予測システムで、投資判断をサポートします。",
      icon: <Target className="h-8 w-8 text-blue-600" />,
      action: null,
    },
    {
      id: "data_guide",
      title: "データの準備",
      description: "分析を開始するには、まず最新の株価データを取得する必要があります。",
      icon: <Database className="h-8 w-8 text-green-600" />,
      action: {
        label: "データを更新",
        onClick: onStartDataUpdate,
        icon: <RefreshCw className="h-4 w-4" />,
      },
    },
    {
      id: "analysis_guide",
      title: "分析の実行",
      description: "データが準備できたら、AIによる株価予測分析を実行できます。",
      icon: <BarChart3 className="h-8 w-8 text-purple-600" />,
      action: {
        label: "分析を実行",
        onClick: onStartAnalysis,
        icon: <Play className="h-4 w-4" />,
      },
    },
    {
      id: "completion",
      title: "準備完了！",
      description: "これで分析を開始できます。ダッシュボードで予測結果を確認してください。",
      icon: <CheckCircle className="h-8 w-8 text-green-600" />,
      action: null,
    },
  ];

  const currentStepData = steps[currentStep];

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      setIsCompleted(true);
    }
  };

  const handleSkip = () => {
    setIsCompleted(true);
  };

  const handleComplete = () => {
    // チュートリアル完了をlocalStorageに保存
    try {
      localStorage.setItem("first_time_tutorial_completed", "true");
    } catch (e) {
      console.warn("localStorage access failed:", e);
    }
    onClose();
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        {/* ヘッダー */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-500">
              ステップ {currentStep + 1} / {steps.length}
            </span>
          </div>
          <button
            onClick={handleSkip}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* コンテンツ */}
        <div className="p-6">
          <div className="text-center mb-6">
            <div className="flex justify-center mb-4">
              {currentStepData.icon}
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {currentStepData.title}
            </h3>
            <p className="text-gray-600">
              {currentStepData.description}
            </p>
          </div>

          {/* 進捗バー */}
          <div className="w-full bg-gray-200 rounded-full h-2 mb-6">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
            />
          </div>

          {/* アクションボタン */}
          {currentStepData.action && (
            <div className="mb-6">
              <button
                onClick={currentStepData.action.onClick}
                className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                {currentStepData.action.icon}
                <span>{currentStepData.action.label}</span>
              </button>
            </div>
          )}

          {/* ナビゲーションボタン */}
          <div className="flex space-x-3">
            {currentStep > 0 && (
              <button
                onClick={() => setCurrentStep(currentStep - 1)}
                className="flex-1 px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                前へ
              </button>
            )}
            
            {currentStep < steps.length - 1 ? (
              <button
                onClick={handleNext}
                className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <span>次へ</span>
                <ArrowRight className="h-4 w-4" />
              </button>
            ) : (
              <button
                onClick={handleComplete}
                className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                <CheckCircle className="h-4 w-4" />
                <span>完了</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
