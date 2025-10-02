/**
 * クイックルーティンガイド
 * 1日5分で完結する投資判断のためのガイドコンポーネント
 */

import React, { useState, useEffect } from 'react';
import { CheckCircle, Clock, Target, TrendingUp, ArrowRight, X } from 'lucide-react';

interface RoutineStep {
  id: string;
  title: string;
  description: string;
  estimatedTime: number; // 秒
  completed: boolean;
  action?: () => void;
  href?: string;
}

interface QuickRoutineGuideProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete?: () => void;
  onSkip?: () => void;
}

export default function QuickRoutineGuide({
  isOpen,
  onClose,
  onComplete,
  onSkip,
}: QuickRoutineGuideProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [steps, setSteps] = useState<RoutineStep[]>([
    {
      id: 'analysis',
      title: '分析実行',
      description: '最新の市場データを分析して投資候補を特定します',
      estimatedTime: 60,
      completed: false,
      action: () => {
        // 分析実行のアクション
        console.log('分析実行');
      },
    },
    {
      id: 'review',
      title: '結果確認',
      description: '分析結果を確認し、投資候補の詳細を確認します',
      estimatedTime: 120,
      completed: false,
      href: '/today',
    },
    {
      id: 'decision',
      title: '投資判断',
      description: '今日の投資指示に基づいて投資判断を行います',
      estimatedTime: 120,
      completed: false,
      href: '/personal-investment',
    },
  ]);
  const [startTime, setStartTime] = useState<number | null>(null);
  const [elapsedTime, setElapsedTime] = useState(0);

  useEffect(() => {
    if (isOpen && !startTime) {
      setStartTime(Date.now());
    }
  }, [isOpen, startTime]);

  useEffect(() => {
    if (startTime) {
      const interval = setInterval(() => {
        setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [startTime]);

  const handleStepComplete = (stepId: string) => {
    setSteps(prev => prev.map(step => 
      step.id === stepId ? { ...step, completed: true } : step
    ));
    
    // 次のステップに進む
    if (currentStep < steps.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      // 全て完了
      onComplete?.();
    }
  };

  const handleSkip = () => {
    onSkip?.();
    onClose();
  };

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      onComplete?.();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const totalEstimatedTime = steps.reduce((sum, step) => sum + step.estimatedTime, 0);
  const completedSteps = steps.filter(step => step.completed).length;
  const progress = (completedSteps / steps.length) * 100;

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        {/* ヘッダー */}
        <div className="bg-blue-600 text-white p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold">5分投資ルーティン</h2>
              <p className="text-blue-100 mt-1">
                効率的な投資判断のためのステップバイステップガイド
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-blue-200 hover:text-white transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* プログレスバー */}
        <div className="px-6 py-4 bg-gray-50">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              進捗: {completedSteps}/{steps.length} ステップ
            </span>
            <span className="text-sm text-gray-500">
              {Math.floor(elapsedTime / 60)}:{(elapsedTime % 60).toString().padStart(2, '0')}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="flex justify-between mt-2">
            <span className="text-xs text-gray-500">
              推定時間: {Math.floor(totalEstimatedTime / 60)}分
            </span>
            <span className="text-xs text-gray-500">
              残り時間: {Math.max(0, Math.floor((totalEstimatedTime - elapsedTime) / 60))}分
            </span>
          </div>
        </div>

        {/* ステップ表示 */}
        <div className="p-6">
          <div className="space-y-4">
            {steps.map((step, index) => (
              <div
                key={step.id}
                className={`p-4 rounded-lg border-2 transition-all ${
                  index === currentStep
                    ? 'border-blue-500 bg-blue-50'
                    : step.completed
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 bg-gray-50'
                }`}
              >
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    {step.completed ? (
                      <CheckCircle className="w-6 h-6 text-green-600" />
                    ) : index === currentStep ? (
                      <Target className="w-6 h-6 text-blue-600" />
                    ) : (
                      <Clock className="w-6 h-6 text-gray-400" />
                    )}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">{step.title}</h3>
                    <p className="text-sm text-gray-600 mt-1">{step.description}</p>
                    <div className="flex items-center justify-between mt-3">
                      <span className="text-xs text-gray-500">
                        推定時間: {step.estimatedTime}秒
                      </span>
                      {index === currentStep && (
                        <div className="flex space-x-2">
                          {step.action && (
                            <button
                              onClick={() => {
                                step.action?.();
                                handleStepComplete(step.id);
                              }}
                              className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 transition-colors"
                            >
                              実行
                            </button>
                          )}
                          {step.href && (
                            <a
                              href={step.href}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 transition-colors"
                            >
                              ページを開く
                            </a>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* フッター */}
        <div className="bg-gray-50 px-6 py-4 flex items-center justify-between">
          <div className="flex space-x-2">
            {currentStep > 0 && (
              <button
                onClick={handlePrevious}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                前へ
              </button>
            )}
          </div>
          
          <div className="flex space-x-2">
            <button
              onClick={handleSkip}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              スキップ
            </button>
            {currentStep < steps.length - 1 ? (
              <button
                onClick={handleNext}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors flex items-center"
              >
                次へ
                <ArrowRight className="w-4 h-4 ml-1" />
              </button>
            ) : (
              <button
                onClick={() => {
                  onComplete?.();
                  onClose();
                }}
                className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors flex items-center"
              >
                完了
                <CheckCircle className="w-4 h-4 ml-1" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * クイックルーティンガイドのフック
 */
export function useQuickRoutineGuide() {
  const [isOpen, setIsOpen] = useState(false);
  const [hasCompleted, setHasCompleted] = useState(false);

  useEffect(() => {
    // 初回訪問チェック
    const hasSeenGuide = localStorage.getItem('quick_routine_guide_seen');
    if (!hasSeenGuide) {
      setIsOpen(true);
    }
  }, []);

  const openGuide = () => setIsOpen(true);
  const closeGuide = () => {
    setIsOpen(false);
    localStorage.setItem('quick_routine_guide_seen', 'true');
  };

  const completeGuide = () => {
    setHasCompleted(true);
    localStorage.setItem('quick_routine_guide_completed', 'true');
  };

  const skipGuide = () => {
    localStorage.setItem('quick_routine_guide_seen', 'true');
  };

  return {
    isOpen,
    hasCompleted,
    openGuide,
    closeGuide,
    completeGuide,
    skipGuide,
  };
}
