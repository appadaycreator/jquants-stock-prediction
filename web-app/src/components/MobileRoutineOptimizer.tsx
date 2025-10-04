"use client";

import React, { useState, useEffect, useCallback } from "react";
import { 
  Play, 
  Pause, 
  CheckCircle, 
  Clock, 
  Smartphone, 
  Wifi, 
  Battery,
  Settings,
  Bell,
  TrendingUp,
  Target,
  BarChart3
} from "lucide-react";

interface MobileRoutineOptimizerProps {
  onRoutineStart?: () => void;
  onRoutineComplete?: (result: any) => void;
  onRoutineError?: (error: string) => void;
  className?: string;
}

interface RoutineStep {
  id: string;
  title: string;
  description: string;
  estimatedTime: number; // 秒
  completed: boolean;
  required: boolean;
  category: "setup" | "analysis" | "review" | "action";
}

interface MobileOptimization {
  touchOptimized: boolean;
  gestureEnabled: boolean;
  hapticFeedback: boolean;
  voiceGuidance: boolean;
  autoScroll: boolean;
  quickActions: boolean;
}

export default function MobileRoutineOptimizer({
  onRoutineStart,
  onRoutineComplete,
  onRoutineError,
  className = "",
}: MobileRoutineOptimizerProps) {
  const [isMobile, setIsMobile] = useState(false);
  const [isRoutineRunning, setIsRoutineRunning] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [routineProgress, setRoutineProgress] = useState(0);
  const [optimization, setOptimization] = useState<MobileOptimization>({
    touchOptimized: true,
    gestureEnabled: true,
    hapticFeedback: true,
    voiceGuidance: false,
    autoScroll: true,
    quickActions: true,
  });

  const [steps, setSteps] = useState<RoutineStep[]>([
    {
      id: "symbol_selection",
      title: "銘柄選択",
      description: "分析したい銘柄を選択します",
      estimatedTime: 30,
      completed: false,
      required: true,
      category: "setup",
    },
    {
      id: "data_validation",
      title: "データ確認",
      description: "選択した銘柄のデータが最新か確認します",
      estimatedTime: 15,
      completed: false,
      required: true,
      category: "setup",
    },
    {
      id: "analysis_execution",
      title: "分析実行",
      description: "AI予測分析を実行します",
      estimatedTime: 120,
      completed: false,
      required: true,
      category: "analysis",
    },
    {
      id: "prediction_review",
      title: "予測結果確認",
      description: "分析結果と予測値を確認します",
      estimatedTime: 30,
      completed: false,
      required: true,
      category: "review",
    },
    {
      id: "risk_assessment",
      title: "リスク評価",
      description: "投資リスクと推奨アクションを確認します",
      estimatedTime: 15,
      completed: false,
      required: true,
      category: "review",
    },
    {
      id: "investment_decision",
      title: "投資判断",
      description: "個人投資ダッシュボードで最終判断を行います",
      estimatedTime: 30,
      completed: false,
      required: false,
      category: "action",
    },
  ]);

  // モバイルデバイス検出
  useEffect(() => {
    const checkMobile = () => {
      const userAgent = navigator.userAgent;
      const isMobileDevice = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
      const isSmallScreen = window.innerWidth <= 768;
      setIsMobile(isMobileDevice || isSmallScreen);
    };

    checkMobile();
    window.addEventListener("resize", checkMobile);
    
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  // ハプティックフィードバック
  const triggerHapticFeedback = useCallback(() => {
    if (optimization.hapticFeedback && 'vibrate' in navigator) {
      navigator.vibrate(50);
    }
  }, [optimization.hapticFeedback]);

  // 音声ガイダンス
  const speakText = useCallback((text: string) => {
    if (optimization.voiceGuidance && 'speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'ja-JP';
      utterance.rate = 0.9;
      speechSynthesis.speak(utterance);
    }
  }, [optimization.voiceGuidance]);

  // ルーティン開始
  const startRoutine = useCallback(async () => {
    if (isRoutineRunning) return;

    setIsRoutineRunning(true);
    setCurrentStep(0);
    setRoutineProgress(0);
    
    triggerHapticFeedback();
    speakText("5分ルーティンを開始します");
    
    onRoutineStart?.();

    try {
      // 各ステップを順次実行
      for (let i = 0; i < steps.length; i++) {
        setCurrentStep(i);
        const step = steps[i];
        
        // ステップ開始通知
        speakText(`${step.title}を開始します`);
        
        // ステップ実行（実際のAPI呼び出し）
        await executeStep(step);
        
        // ステップ完了
        setSteps(prev => prev.map((s, index) => 
          index === i ? { ...s, completed: true } : s
        ));
        
        // 進捗更新
        const progress = Math.round(((i + 1) / steps.length) * 100);
        setRoutineProgress(progress);
        
        triggerHapticFeedback();
        speakText(`${step.title}が完了しました`);
        
        // 自動スクロール
        if (optimization.autoScroll) {
          setTimeout(() => {
            const stepElement = document.getElementById(`step-${i}`);
            stepElement?.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }, 100);
        }
      }

      // ルーティン完了
      setIsRoutineRunning(false);
      setRoutineProgress(100);
      
      triggerHapticFeedback();
      speakText("5分ルーティンが完了しました");
      
      const result = {
        completed_at: new Date().toISOString(),
        total_steps: steps.length,
        completed_steps: steps.length,
        execution_time: "約5分",
      };
      
      onRoutineComplete?.(result);
      
    } catch (error) {
      setIsRoutineRunning(false);
      const errorMessage = error instanceof Error ? error.message : "不明なエラーが発生しました";
      
      triggerHapticFeedback();
      speakText(`エラーが発生しました: ${errorMessage}`);
      
      onRoutineError?.(errorMessage);
    }
  }, [isRoutineRunning, steps, optimization, onRoutineStart, onRoutineComplete, onRoutineError, triggerHapticFeedback, speakText]);

  // ステップ実行
  const executeStep = async (step: RoutineStep): Promise<void> => {
    // 実際のAPI呼び出しをシミュレート
    await new Promise(resolve => setTimeout(resolve, step.estimatedTime * 10));
  };

  // クイックアクション
  const quickActions = [
    {
      id: "start_routine",
      title: "ルーティン開始",
      icon: <Play className="h-5 w-5" />,
      action: startRoutine,
      color: "bg-green-600 hover:bg-green-700",
    },
    {
      id: "pause_routine",
      title: "一時停止",
      icon: <Pause className="h-5 w-5" />,
      action: () => setIsRoutineRunning(false),
      color: "bg-yellow-600 hover:bg-yellow-700",
    },
    {
      id: "settings",
      title: "設定",
      icon: <Settings className="h-5 w-5" />,
      action: () => console.log("設定を開く"),
      color: "bg-gray-600 hover:bg-gray-700",
    },
  ];

  // デスクトップ表示
  if (!isMobile) {
    return (
      <div className={`desktop-layout ${className}`}>
        <div className="text-center py-8">
          <Smartphone className="h-12 w-12 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-semibold text-gray-700 mb-2">
            モバイル最適化表示
          </h3>
          <p className="text-gray-500">
            このコンポーネントはモバイルデバイスで最適化されています
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`mobile-routine-optimizer ${className}`}>
      {/* ヘッダー */}
      <div className="mobile-header sticky top-0 z-40 bg-white border-b border-gray-200 px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Smartphone className="h-5 w-5 text-blue-600" />
            <h1 className="text-lg font-semibold text-gray-900">5分ルーティン</h1>
          </div>
          <div className="flex items-center gap-2">
            <Wifi className="h-4 w-4 text-green-500" />
            <Battery className="h-4 w-4 text-green-500" />
          </div>
        </div>
      </div>

      {/* 進捗表示 */}
      <div className="px-4 py-4 bg-gray-50">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">進捗</span>
          <span className="text-sm text-gray-500">{routineProgress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${routineProgress}%` }}
          />
        </div>
        {isRoutineRunning && (
          <p className="text-xs text-gray-500 mt-1">
            実行中... {steps[currentStep]?.title}
          </p>
        )}
      </div>

      {/* クイックアクション */}
      {optimization.quickActions && (
        <div className="px-4 py-3 bg-white border-b border-gray-200">
          <div className="flex gap-2">
            {quickActions.map((action) => (
              <button
                key={action.id}
                onClick={action.action}
                className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-white text-sm font-medium transition-colors ${action.color}`}
              >
                {action.icon}
                <span className="hidden sm:inline">{action.title}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* ステップ一覧 */}
      <div className="px-4 py-4 space-y-3">
        {steps.map((step, index) => (
          <div
            key={step.id}
            id={`step-${index}`}
            className={`p-4 rounded-lg border-2 transition-all duration-200 ${
              step.completed
                ? 'border-green-200 bg-green-50'
                : index === currentStep && isRoutineRunning
                ? 'border-blue-200 bg-blue-50'
                : 'border-gray-200 bg-white'
            }`}
          >
            <div className="flex items-start gap-3">
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                step.completed
                  ? 'bg-green-100 text-green-600'
                  : index === currentStep && isRoutineRunning
                  ? 'bg-blue-100 text-blue-600'
                  : 'bg-gray-100 text-gray-600'
              }`}>
                {step.completed ? (
                  <CheckCircle className="h-4 w-4" />
                ) : (
                  <span>{index + 1}</span>
                )}
              </div>
              
              <div className="flex-1 min-w-0">
                <h3 className="font-medium text-gray-900 mb-1">
                  {step.title}
                </h3>
                <p className="text-sm text-gray-600 mb-2">
                  {step.description}
                </p>
                
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <Clock className="h-3 w-3" />
                  <span>約{step.estimatedTime}秒</span>
                  {step.required && (
                    <span className="px-2 py-0.5 bg-red-100 text-red-600 rounded">
                      必須
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 最適化設定 */}
      <div className="px-4 py-4 bg-gray-50 border-t border-gray-200">
        <h3 className="font-medium text-gray-900 mb-3">モバイル最適化設定</h3>
        
        <div className="space-y-3">
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={optimization.touchOptimized}
              onChange={(e) => setOptimization(prev => ({ ...prev, touchOptimized: e.target.checked }))}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">タッチ操作最適化</span>
          </label>
          
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={optimization.gestureEnabled}
              onChange={(e) => setOptimization(prev => ({ ...prev, gestureEnabled: e.target.checked }))}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">ジェスチャー操作</span>
          </label>
          
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={optimization.hapticFeedback}
              onChange={(e) => setOptimization(prev => ({ ...prev, hapticFeedback: e.target.checked }))}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">振動フィードバック</span>
          </label>
          
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={optimization.voiceGuidance}
              onChange={(e) => setOptimization(prev => ({ ...prev, voiceGuidance: e.target.checked }))}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">音声ガイダンス</span>
          </label>
          
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={optimization.autoScroll}
              onChange={(e) => setOptimization(prev => ({ ...prev, autoScroll: e.target.checked }))}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">自動スクロール</span>
          </label>
        </div>
      </div>
    </div>
  );
}
