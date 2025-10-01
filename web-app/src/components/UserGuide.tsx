"use client";

import React, { useState, useEffect } from "react";
import { 
  Play, 
  RefreshCw, 
  Settings, 
  BarChart3, 
  TrendingUp, 
  Target, 
  Database, 
  Shield, 
  User,
  X,
  ChevronRight,
  CheckCircle,
  ArrowRight,
  BookOpen,
} from "lucide-react";

interface GuideStep {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  action?: string;
  target?: string;
}

const guideSteps: GuideStep[] = [
  {
    id: "overview",
    title: "ダッシュボードの概要",
    description: "株価予測システムの主要機能と指標を確認できます。システムの稼働状況、最新の更新日時、主要な指標（最優秀モデル、予測精度、MAE、データ数）を確認できます。",
    icon: <BarChart3 className="w-6 h-6" />,
    action: "概要タブをクリックして、システムの現在の状況を確認してください",
    target: "overview",
  },
  {
    id: "analysis",
    title: "分析の実行",
    description: "ワンクリックで株価分析を実行し、予測結果を取得できます。ボタンを押すとローディング状態が表示され、処理の進捗が確認できます。",
    icon: <Play className="w-6 h-6" />,
    action: "「分析実行」ボタンをクリックして、ローディング状態と進捗表示を確認してください",
    target: "analysis",
  },
  {
    id: "refresh",
    title: "データの更新",
    description: "最新のデータを取得してダッシュボードを更新します。更新ボタンを押すとローディング状態が表示され、完了後に更新日時が表示されます。",
    icon: <RefreshCw className="w-6 h-6" />,
    action: "「更新」ボタンをクリックして、ローディング状態と完了通知を確認してください",
    target: "refresh",
  },
  {
    id: "predictions",
    title: "予測結果の確認",
    description: "実際の株価と予測値の比較、精度の評価を行います。予測vs実際値のチャートと誤差分布を確認できます。",
    icon: <TrendingUp className="w-6 h-6" />,
    action: "予測結果タブをクリックして、予測精度を確認してください",
    target: "predictions",
  },
  {
    id: "models",
    title: "モデル比較",
    description: "複数の機械学習モデルの性能を比較し、最適なモデルを選択できます。MAE、RMSE、R²の比較表とチャートを確認できます。",
    icon: <Target className="w-6 h-6" />,
    action: "モデル比較タブをクリックして、各モデルの性能を比較してください",
    target: "models",
  },
  {
    id: "settings",
    title: "設定の調整",
    description: "分析期間、モデル選択、表示オプションなどをカスタマイズできます。設定ボタンをクリックして詳細なオプションを調整できます。",
    icon: <Settings className="w-6 h-6" />,
    action: "設定ボタンをクリックして、分析設定をカスタマイズしてください",
    target: "settings",
  },
];

interface UserGuideProps {
  isVisible: boolean;
  onClose: () => void;
  onStepComplete?: (stepId: string) => void;
  currentTab?: string;
}

export default function UserGuide({ 
  isVisible, 
  onClose, 
  onStepComplete,
  currentTab = "overview",
}: UserGuideProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<string[]>([]);
  const [showQuickStart, setShowQuickStart] = useState(false);

  // ローカルストレージから完了済みステップを読み込み
  useEffect(() => {
    const saved = localStorage.getItem("userGuideCompleted");
    if (saved) {
      try {
        setCompletedSteps(JSON.parse(saved));
      } catch (error) {
        console.error("ガイド進捗の読み込みエラー:", error);
      }
    }
  }, []);

  // 完了済みステップを保存
  const saveCompletedSteps = (steps: string[]) => {
    setCompletedSteps(steps);
    localStorage.setItem("userGuideCompleted", JSON.stringify(steps));
  };

  // ステップ完了
  const completeStep = (stepId: string) => {
    if (!completedSteps.includes(stepId)) {
      const newCompleted = [...completedSteps, stepId];
      saveCompletedSteps(newCompleted);
      onStepComplete?.(stepId);
    }
  };

  // 次のステップへ
  const nextStep = () => {
    if (currentStep < guideSteps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      // 全ステップ完了
      completeStep("all");
      onClose();
    }
  };

  // 前のステップへ
  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  // ステップをスキップ
  const skipStep = () => {
    completeStep(guideSteps[currentStep].id);
    nextStep();
  };

  // クイックスタート
  const startQuickStart = () => {
    setShowQuickStart(true);
    setCurrentStep(0);
  };

  if (!isVisible) return null;

  if (showQuickStart) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                <BookOpen className="w-6 h-6 text-blue-600" />
                クイックスタートガイド
              </h2>
              <button
                onClick={() => setShowQuickStart(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-semibold text-blue-800 mb-2">🚀 5分で始める株価予測</h3>
                <p className="text-blue-700 text-sm">
                  以下の手順に従って、システムの基本操作を学習できます。
                </p>
              </div>

              <div className="space-y-4">
                {guideSteps.map((step, index) => (
                  <div
                    key={step.id}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      completedSteps.includes(step.id)
                        ? "border-green-200 bg-green-50"
                        : "border-gray-200 bg-white"
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`p-2 rounded-lg ${
                        completedSteps.includes(step.id)
                          ? "bg-green-100 text-green-600"
                          : "bg-blue-100 text-blue-600"
                      }`}>
                        {completedSteps.includes(step.id) ? (
                          <CheckCircle className="w-5 h-5" />
                        ) : (
                          step.icon
                        )}
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900 mb-1">
                          {index + 1}. {step.title}
                        </h4>
                        <p className="text-gray-600 text-sm mb-2">
                          {step.description}
                        </p>
                        {step.action && (
                          <p className="text-blue-600 text-sm font-medium">
                            💡 {step.action}
                          </p>
                        )}
                      </div>
                      {!completedSteps.includes(step.id) && (
                        <button
                          onClick={() => completeStep(step.id)}
                          className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
                        >
                          完了
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex justify-between pt-4 border-t border-gray-200">
                <button
                  onClick={() => setShowQuickStart(false)}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  閉じる
                </button>
                <button
                  onClick={() => {
                    saveCompletedSteps(guideSteps.map(s => s.id));
                    setShowQuickStart(false);
                  }}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  すべて完了としてマーク
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <BookOpen className="w-6 h-6 text-blue-600" />
              ユーザーガイド
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          <div className="space-y-6">
            {/* 進捗バー */}
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${((currentStep + 1) / guideSteps.length) * 100}%` }}
              />
            </div>

            {/* 現在のステップ */}
            <div className="text-center">
              <div className="text-sm text-gray-500 mb-2">
                ステップ {currentStep + 1} / {guideSteps.length}
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {guideSteps[currentStep].title}
              </h3>
              <p className="text-gray-600 text-sm">
                {guideSteps[currentStep].description}
              </p>
            </div>

            {/* アクションガイド */}
            {guideSteps[currentStep].action && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center gap-2 text-blue-800">
                  <ArrowRight className="w-4 h-4" />
                  <span className="font-medium">
                    {guideSteps[currentStep].action}
                  </span>
                </div>
              </div>
            )}

            {/* ナビゲーションボタン */}
            <div className="flex justify-between">
              <div className="flex gap-2">
                <button
                  onClick={prevStep}
                  disabled={currentStep === 0}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  前へ
                </button>
                <button
                  onClick={skipStep}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  スキップ
                </button>
              </div>
              
              <div className="flex gap-2">
                <button
                  onClick={startQuickStart}
                  className="px-4 py-2 text-blue-600 border border-blue-300 rounded-lg hover:bg-blue-50 transition-colors"
                >
                  クイックスタート
                </button>
                <button
                  onClick={nextStep}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  {currentStep === guideSteps.length - 1 ? "完了" : "次へ"}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
