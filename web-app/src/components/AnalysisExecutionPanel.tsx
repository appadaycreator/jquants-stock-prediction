"use client";

import { useState, useEffect } from "react";
import { Play, BarChart3, Target, Clock, CheckCircle, AlertTriangle, RefreshCw, Database } from "lucide-react";

interface AnalysisExecutionPanelProps {
  onAnalysisStart?: () => void;
  onAnalysisComplete?: () => void;
  onDataUpdateStart?: () => void;
  onDataUpdateComplete?: () => void;
  className?: string;
}

interface AnalysisStep {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  estimatedTime: string;
  status: "pending" | "running" | "completed" | "error";
}

export default function AnalysisExecutionPanel({
  onAnalysisStart,
  onAnalysisComplete,
  onDataUpdateStart,
  onDataUpdateComplete,
  className = "",
}: AnalysisExecutionPanelProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [analysisSteps, setAnalysisSteps] = useState<AnalysisStep[]>([
    {
      id: "data_update",
      name: "データ更新",
      description: "最新の株価データを取得します",
      icon: <Database className="h-5 w-5" />,
      estimatedTime: "30秒",
      status: "pending",
    },
    {
      id: "feature_engineering",
      name: "特徴量エンジニアリング",
      description: "技術指標を計算します",
      icon: <BarChart3 className="h-5 w-5" />,
      estimatedTime: "1分",
      status: "pending",
    },
    {
      id: "model_training",
      name: "モデル学習",
      description: "AIモデルを学習させます",
      icon: <Target className="h-5 w-5" />,
      estimatedTime: "2分",
      status: "pending",
    },
    {
      id: "prediction",
      name: "予測実行",
      description: "株価予測を実行します",
      icon: <Play className="h-5 w-5" />,
      estimatedTime: "30秒",
      status: "pending",
    },
  ]);

  const [overallProgress, setOverallProgress] = useState(0);
  const [estimatedTimeRemaining, setEstimatedTimeRemaining] = useState<number | null>(null);

  // 分析実行
  const startAnalysis = async () => {
    if (isAnalyzing) return;

    setIsAnalyzing(true);
    setCurrentStep(0);
    setOverallProgress(0);
    onAnalysisStart?.();

    try {
      // 各ステップを順次実行
      for (let i = 0; i < analysisSteps.length; i++) {
        setCurrentStep(i);
        setAnalysisSteps(prev => prev.map((step, index) => ({
          ...step,
          status: index === i ? "running" : index < i ? "completed" : "pending",
        })));

        // ステップの実行時間をシミュレート
        const stepTime = i === 0 ? 2000 : i === 1 ? 3000 : i === 2 ? 5000 : 2000;
        await new Promise(resolve => setTimeout(resolve, stepTime));

        setOverallProgress(Math.round(((i + 1) / analysisSteps.length) * 100));
      }

      // 完了
      setAnalysisSteps(prev => prev.map(step => ({ ...step, status: "completed" })));
      onAnalysisComplete?.();

    } catch (error) {
      console.error("分析実行エラー:", error);
      setAnalysisSteps(prev => prev.map(step => ({ ...step, status: "error" })));
    } finally {
      setIsAnalyzing(false);
    }
  };

  // データ更新のみ実行
  const startDataUpdate = async () => {
    if (isUpdating) return;

    setIsUpdating(true);
    onDataUpdateStart?.();

    try {
      // データ更新のシミュレーション
      await new Promise(resolve => setTimeout(resolve, 3000));
      onDataUpdateComplete?.();
    } catch (error) {
      console.error("データ更新エラー:", error);
    } finally {
      setIsUpdating(false);
    }
  };

  // 推定残り時間の計算
  useEffect(() => {
    if (!isAnalyzing) {
      setEstimatedTimeRemaining(null);
      return;
    }

    const totalTime = analysisSteps.reduce((sum, step) => {
      const timeMap: Record<string, number> = {
        "data_update": 2,
        "feature_engineering": 3,
        "model_training": 5,
        "prediction": 2,
      };
      return sum + (timeMap[step.id] || 1);
    }, 0);

    const elapsed = currentStep * 2; // 簡易計算
    const remaining = Math.max(0, totalTime - elapsed);
    setEstimatedTimeRemaining(remaining);
  }, [isAnalyzing, currentStep, analysisSteps]);

  const getStepIcon = (step: AnalysisStep) => {
    switch (step.status) {
      case "completed":
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case "running":
        return <RefreshCw className="h-5 w-5 text-blue-500 animate-spin" />;
      case "error":
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      default:
        return step.icon;
    }
  };

  const getStepStatusColor = (step: AnalysisStep) => {
    switch (step.status) {
      case "completed":
        return "text-green-600 bg-green-50 border-green-200";
      case "running":
        return "text-blue-600 bg-blue-50 border-blue-200";
      case "error":
        return "text-red-600 bg-red-50 border-red-200";
      default:
        return "text-gray-600 bg-gray-50 border-gray-200";
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <BarChart3 className="h-6 w-6 text-purple-600" />
          <h3 className="text-lg font-semibold text-gray-900">分析実行</h3>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={startDataUpdate}
            disabled={isUpdating || isAnalyzing}
            className="flex items-center space-x-2 px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Database className="h-4 w-4" />
            <span>データ更新のみ</span>
          </button>
        </div>
      </div>

      {/* 分析ステップ */}
      <div className="space-y-3 mb-6">
        {analysisSteps.map((step, index) => (
          <div
            key={step.id}
            className={`p-4 rounded-lg border-2 transition-all ${getStepStatusColor(step)}`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                {getStepIcon(step)}
                <div>
                  <h4 className="font-medium">{step.name}</h4>
                  <p className="text-sm opacity-75">{step.description}</p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm font-medium">{step.estimatedTime}</div>
                {step.status === "running" && (
                  <div className="text-xs text-blue-600">実行中...</div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 全体進捗 */}
      {isAnalyzing && (
        <div className="mb-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>全体進捗</span>
            <span>{overallProgress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-500"
              style={{ width: `${overallProgress}%` }}
            />
          </div>
          {estimatedTimeRemaining && (
            <div className="flex items-center space-x-2 text-sm text-gray-600 mt-2">
              <Clock className="h-4 w-4" />
              <span>推定残り時間: {estimatedTimeRemaining}分</span>
            </div>
          )}
        </div>
      )}

      {/* 実行ボタン */}
      <div className="flex space-x-3">
        {!isAnalyzing ? (
          <button
            onClick={startAnalysis}
            disabled={isUpdating}
            className="flex-1 flex items-center justify-center space-x-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Play className="h-5 w-5" />
            <span className="font-medium">分析を実行</span>
          </button>
        ) : (
          <button
            disabled
            className="flex-1 flex items-center justify-center space-x-2 px-6 py-3 bg-gray-400 text-white rounded-lg cursor-not-allowed"
          >
            <RefreshCw className="h-5 w-5 animate-spin" />
            <span className="font-medium">実行中...</span>
          </button>
        )}
      </div>

      {/* 実行結果 */}
      {!isAnalyzing && overallProgress === 100 && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center space-x-2">
            <CheckCircle className="h-5 w-5 text-green-600" />
            <span className="text-green-800 font-medium">分析が完了しました</span>
          </div>
          <p className="text-sm text-green-700 mt-1">
            予測結果がダッシュボードに表示されます
          </p>
        </div>
      )}
    </div>
  );
}
