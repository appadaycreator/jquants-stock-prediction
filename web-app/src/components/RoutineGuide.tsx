'use client';

import React, { useState, useEffect } from 'react';
import { Play, Pause, RotateCcw, CheckCircle, Clock, Target, TrendingUp, AlertTriangle } from 'lucide-react';

interface RoutineStep {
  id: string;
  title: string;
  description: string;
  estimatedTime: number; // 秒
  completed: boolean;
  action?: () => void;
}

interface RoutineGuideProps {
  isOpen: boolean;
  onClose: () => void;
  onStepComplete?: (stepId: string) => void;
  onRoutineComplete?: () => void;
}

export const RoutineGuide: React.FC<RoutineGuideProps> = ({
  isOpen,
  onClose,
  onStepComplete,
  onRoutineComplete
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(300); // 5分 = 300秒
  const [steps, setSteps] = useState<RoutineStep[]>([
    {
      id: 'data-update',
      title: '最新データの取得',
      description: 'J-Quants APIから最新の株価データを取得します',
      estimatedTime: 30,
      completed: false
    },
    {
      id: 'candidates-review',
      title: '買い候補の確認',
      description: '今日の投資候補銘柄を確認し、理由を検討します',
      estimatedTime: 60,
      completed: false
    },
    {
      id: 'holdings-check',
      title: '保有銘柄の評価',
      description: '現在保有している銘柄の利益・損失を確認します',
      estimatedTime: 45,
      completed: false
    },
    {
      id: 'risk-assessment',
      title: 'リスク管理の確認',
      description: 'ポートフォリオ全体のリスク状況を確認します',
      estimatedTime: 30,
      completed: false
    },
    {
      id: 'action-memo',
      title: 'アクションメモの作成',
      description: '今日の投資判断と今後の計画をメモします',
      estimatedTime: 45,
      completed: false
    }
  ]);

  const totalSteps = steps.length;
  const completedSteps = steps.filter(step => step.completed).length;
  const progress = (completedSteps / totalSteps) * 100;

  // タイマーの管理
  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (isRunning && timeRemaining > 0) {
      interval = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            setIsRunning(false);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isRunning, timeRemaining]);

  // 進捗の保存
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('routine-progress', JSON.stringify({
        currentStep,
        steps,
        timeRemaining
      }));
    }
  }, [currentStep, steps, timeRemaining]);

  // 進捗の復元
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('routine-progress');
      if (saved) {
        try {
          const data = JSON.parse(saved);
          setCurrentStep(data.currentStep || 0);
          setSteps(data.steps || steps);
          setTimeRemaining(data.timeRemaining || 300);
        } catch (error) {
          console.error('進捗の復元に失敗:', error);
        }
      }
    }
  }, []);

  const startRoutine = () => {
    setIsRunning(true);
  };

  const pauseRoutine = () => {
    setIsRunning(false);
  };

  const resetRoutine = () => {
    setIsRunning(false);
    setCurrentStep(0);
    setTimeRemaining(300);
    setSteps(prev => prev.map(step => ({ ...step, completed: false })));
  };

  const completeStep = (stepId: string) => {
    setSteps(prev => prev.map(step => 
      step.id === stepId ? { ...step, completed: true } : step
    ));
    
    onStepComplete?.(stepId);

    // 次のステップへ
    if (currentStep < totalSteps - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      // 全ステップ完了
      setIsRunning(false);
      onRoutineComplete?.();
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getStepIcon = (step: RoutineStep, index: number) => {
    if (step.completed) {
      return <CheckCircle className="w-6 h-6 text-green-500" />;
    }
    if (index === currentStep) {
      return <Target className="w-6 h-6 text-blue-500" />;
    }
    return <Clock className="w-6 h-6 text-gray-400" />;
  };

  const getStepStatus = (step: RoutineStep, index: number) => {
    if (step.completed) return 'completed';
    if (index === currentStep) return 'current';
    if (index < currentStep) return 'pending';
    return 'upcoming';
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden">
        {/* ヘッダー */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <Target className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-semibold text-gray-900">
              今日の5分ルーティン
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            ×
          </button>
        </div>

        {/* 進捗バー */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-4">
              <div className="text-2xl font-bold text-blue-600">
                {formatTime(timeRemaining)}
              </div>
              <div className="text-sm text-gray-600">
                残り時間
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={isRunning ? pauseRoutine : startRoutine}
                className={`px-4 py-2 rounded-md font-medium transition-colors ${
                  isRunning
                    ? 'bg-yellow-600 text-white hover:bg-yellow-700'
                    : 'bg-green-600 text-white hover:bg-green-700'
                }`}
              >
                {isRunning ? (
                  <div className="flex items-center space-x-2">
                    <Pause className="w-4 h-4" />
                    <span>一時停止</span>
                  </div>
                ) : (
                  <div className="flex items-center space-x-2">
                    <Play className="w-4 h-4" />
                    <span>開始</span>
                  </div>
                )}
              </button>
              <button
                onClick={resetRoutine}
                className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
              >
                <div className="flex items-center space-x-2">
                  <RotateCcw className="w-4 h-4" />
                  <span>リセット</span>
                </div>
              </button>
            </div>
          </div>

          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <div className="flex justify-between text-sm text-gray-600 mt-2">
            <span>{completedSteps}/{totalSteps} ステップ完了</span>
            <span>{Math.round(progress)}% 完了</span>
          </div>
        </div>

        {/* ステップ一覧 */}
        <div className="p-6 max-h-96 overflow-y-auto">
          <div className="space-y-4">
            {steps.map((step, index) => {
              const status = getStepStatus(step, index);
              const isCurrent = index === currentStep;
              
              return (
                <div
                  key={step.id}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    isCurrent
                      ? 'border-blue-500 bg-blue-50'
                      : step.completed
                      ? 'border-green-500 bg-green-50'
                      : 'border-gray-200 bg-white'
                  }`}
                >
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0">
                      {getStepIcon(step, index)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h3 className={`text-lg font-medium ${
                          isCurrent ? 'text-blue-900' : 'text-gray-900'
                        }`}>
                          {step.title}
                        </h3>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">
                            {step.estimatedTime}秒
                          </span>
                          {isCurrent && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              実行中
                            </span>
                          )}
                        </div>
                      </div>
                      <p className={`text-sm mt-1 ${
                        isCurrent ? 'text-blue-700' : 'text-gray-600'
                      }`}>
                        {step.description}
                      </p>
                      
                      {isCurrent && (
                        <div className="mt-4">
                          <button
                            onClick={() => completeStep(step.id)}
                            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                          >
                            <div className="flex items-center space-x-2">
                              <CheckCircle className="w-4 h-4" />
                              <span>完了</span>
                            </div>
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* フッター */}
        <div className="p-6 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              💡 ヒント: 各ステップを順番に実行することで、効率的に投資判断を行えます
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <Clock className="w-4 h-4" />
              <span>推奨時間: 5分</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RoutineGuide;
