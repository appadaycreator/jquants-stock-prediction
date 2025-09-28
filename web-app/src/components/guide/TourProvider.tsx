"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { accessibilityUtils } from '../../lib/guide/accessibility';

// 型定義
export interface GuideStep {
  id: string;
  target: string;        // CSS セレクタ
  title?: string;        // 見出し（任意）
  body: string;          // 60字以内
  placement: "top" | "right" | "bottom" | "left" | "auto";
  page: "/" | "/predictions" | "/models" | "/analysis" | "/reports" | "/settings";
  next?: string;         // 次ステップ id
  prev?: string;
  action?: { type: "nav"; to: string } | { type: "click"; target: string };
}

export interface GuideState {
  isActive: boolean;
  currentStep: string | null;
  completedSteps: string[];
  isFirstVisit: boolean;
  isTourCompleted: boolean;
  isGuideDisabled: boolean;
}

export interface GuideContextType {
  state: GuideState;
  startTour: () => void;
  nextStep: () => void;
  prevStep: () => void;
  skipTour: () => void;
  completeTour: () => void;
  toggleGuide: () => void;
  resetGuide: () => void;
  getCurrentStepData: () => GuideStep | null;
  isStepCompleted: (stepId: string) => boolean;
}

const GuideContext = createContext<GuideContextType | null>(null);

// ローカルストレージキー
const STORAGE_KEYS = {
  FIRST_VISIT: 'guide_first_visit',
  COMPLETED_STEPS: 'guide_completed_steps',
  TOUR_COMPLETED: 'guide_tour_completed',
  GUIDE_DISABLED: 'guide_disabled',
  CURRENT_STEP: 'guide_current_step'
};

// デフォルトステップ定義
const DEFAULT_STEPS: GuideStep[] = [
  {
    id: 'welcome',
    target: '[data-guide-target="welcome"]',
    title: 'ようこそ！',
    body: 'J-Quants株価予測システムへようこそ。3分で主要機能を案内します。',
    placement: 'auto',
    page: '/',
    next: 'navigation'
  },
  {
    id: 'navigation',
    target: '[data-guide-target="navigation"]',
    title: 'ナビゲーション',
    body: '各ページへの移動はここから。予測・モデル・分析・設定を切り替えできます。',
    placement: 'bottom',
    page: '/',
    next: 'dashboard-overview'
  },
  {
    id: 'dashboard-overview',
    target: '[data-guide-target="dashboard-overview"]',
    title: 'ダッシュボード概要',
    body: '今日の投資指示と主要KPIが表示されます。まずはここを確認しましょう。',
    placement: 'auto',
    page: '/',
    next: 'kpi-metrics'
  },
  {
    id: 'kpi-metrics',
    target: '[data-guide-target="kpi-metrics"]',
    title: '主要指標の見方',
    body: 'MAE（平均絶対誤差）・R²（決定係数）・予測精度を確認。低いMAEと高いR²が理想的。',
    placement: 'auto',
    page: '/',
    next: 'candidate-cards'
  },
  {
    id: 'candidate-cards',
    target: '[data-guide-target="candidate-cards"]',
    title: '候補銘柄カード',
    body: '推奨銘柄とリスク情報を表示。カードをクリックして詳細分析に進めます。',
    placement: 'auto',
    page: '/',
    next: 'model-comparison'
  },
  {
    id: 'model-comparison',
    target: '[data-guide-target="model-comparison"]',
    title: 'モデル比較',
    body: '複数モデルの性能を比較。総合評価→詳細指標の順で確認しましょう。',
    placement: 'auto',
    page: '/',
    next: 'analysis-features'
  },
  {
    id: 'analysis-features',
    target: '[data-guide-target="analysis-features"]',
    title: '分析機能',
    body: '特徴量重要度・残差分析・相関分析でモデルの信頼性を確認できます。',
    placement: 'auto',
    page: '/',
    next: 'settings-config'
  },
  {
    id: 'settings-config',
    target: '[data-guide-target="settings-config"]',
    title: '設定',
    body: '実行時刻・通知先・しきい値を設定。定期的な分析実行に必要です。',
    placement: 'auto',
    page: '/',
    next: 'help-support'
  },
  {
    id: 'help-support',
    target: '[data-guide-target="help-support"]',
    title: 'ヘルプ・サポート',
    body: '困った時はF1キーまたは「？」ボタンでクイックヘルプを表示できます。',
    placement: 'auto',
    page: '/',
    next: 'completion'
  },
  {
    id: 'completion',
    target: '[data-guide-target="completion"]',
    title: '完了！',
    body: 'お疲れ様でした！これで主要機能を理解できました。明日からは自動案内しません。',
    placement: 'auto',
    page: '/'
  }
];

export function TourProvider({ children, steps = DEFAULT_STEPS }: { 
  children: React.ReactNode; 
  steps?: GuideStep[];
}) {
  const [state, setState] = useState<GuideState>({
    isActive: false,
    currentStep: null,
    completedSteps: [],
    isFirstVisit: true,
    isTourCompleted: false,
    isGuideDisabled: false
  });

  // ローカルストレージから状態を復元
  useEffect(() => {
    const isFirstVisit = localStorage.getItem(STORAGE_KEYS.FIRST_VISIT) !== 'false';
    const completedSteps = JSON.parse(localStorage.getItem(STORAGE_KEYS.COMPLETED_STEPS) || '[]');
    const isTourCompleted = localStorage.getItem(STORAGE_KEYS.TOUR_COMPLETED) === 'true';
    const isGuideDisabled = localStorage.getItem(STORAGE_KEYS.GUIDE_DISABLED) === 'true';
    const currentStep = localStorage.getItem(STORAGE_KEYS.CURRENT_STEP);

    setState(prev => ({
      ...prev,
      isFirstVisit,
      completedSteps,
      isTourCompleted,
      isGuideDisabled,
      currentStep: currentStep || null
    }));

    // 初回訪問でガイドが無効化されていない場合は自動開始
    if (isFirstVisit && !isGuideDisabled && !isTourCompleted) {
      setTimeout(() => {
        startTour();
      }, 1000);
    }
  }, []);

  // 状態をローカルストレージに保存
  const saveState = useCallback((newState: Partial<GuideState>) => {
    setState(prev => {
      const updated = { ...prev, ...newState };
      
      // ローカルストレージに保存
      if (newState.isFirstVisit !== undefined) {
        localStorage.setItem(STORAGE_KEYS.FIRST_VISIT, newState.isFirstVisit.toString());
      }
      if (newState.completedSteps !== undefined) {
        localStorage.setItem(STORAGE_KEYS.COMPLETED_STEPS, JSON.stringify(newState.completedSteps));
      }
      if (newState.isTourCompleted !== undefined) {
        localStorage.setItem(STORAGE_KEYS.TOUR_COMPLETED, newState.isTourCompleted.toString());
      }
      if (newState.isGuideDisabled !== undefined) {
        localStorage.setItem(STORAGE_KEYS.GUIDE_DISABLED, newState.isGuideDisabled.toString());
      }
      if (newState.currentStep !== undefined) {
        if (newState.currentStep) {
          localStorage.setItem(STORAGE_KEYS.CURRENT_STEP, newState.currentStep);
        } else {
          localStorage.removeItem(STORAGE_KEYS.CURRENT_STEP);
        }
      }
      
      return updated;
    });
  }, []);

  const startTour = useCallback(() => {
    const firstStep = steps[0];
    if (firstStep) {
      // フォーカスを保存
      accessibilityUtils.focusManager.saveFocus();
      
      // スクリーンリーダーにアナウンス
      accessibilityUtils.screenReader.announce('ガイドツアーを開始しました');
      
      saveState({
        isActive: true,
        currentStep: firstStep.id,
        isFirstVisit: false
      });
    }
  }, [steps, saveState]);

  const nextStep = useCallback(() => {
    // 状態更新を次のレンダリングサイクルに遅延
    setTimeout(() => {
      setState(prev => {
        if (!prev.currentStep) return prev;

        const currentStepData = steps.find(step => step.id === prev.currentStep);
        if (!currentStepData?.next) {
          // 最後のステップ
          return {
            ...prev,
            isActive: false,
            currentStep: null,
            isTourCompleted: true,
            completedSteps: [...prev.completedSteps, prev.currentStep]
          };
        }

        const nextStepData = steps.find(step => step.id === currentStepData.next);
        if (!nextStepData) return prev;

        // アクション実行
        if (nextStepData.action) {
          if (nextStepData.action.type === 'nav') {
            // ページ遷移は親コンポーネントで処理
            window.location.href = nextStepData.action.to;
          } else if (nextStepData.action.type === 'click') {
            const element = document.querySelector(nextStepData.action.target);
            if (element) {
              (element as HTMLElement).click();
            }
          }
        }

        return {
          ...prev,
          currentStep: nextStepData.id,
          completedSteps: [...prev.completedSteps, prev.currentStep]
        };
      });
    }, 0);
  }, [steps]);

  const prevStep = useCallback(() => {
    setState(prev => {
      if (!prev.currentStep) return prev;

      const currentStepData = steps.find(step => step.id === prev.currentStep);
      if (!currentStepData?.prev) return prev;

      const prevStepData = steps.find(step => step.id === currentStepData.prev);
      if (!prevStepData) return prev;

      return {
        ...prev,
        currentStep: prevStepData.id
      };
    });
  }, [steps]);

  const skipTour = useCallback(() => {
    saveState({
      isActive: false,
      currentStep: null,
      isTourCompleted: true
    });
  }, [saveState]);

  const completeTour = useCallback(() => {
    // スクリーンリーダーにアナウンス
    accessibilityUtils.screenReader.announce('ガイドツアーが完了しました');
    
    // フォーカスを復元
    accessibilityUtils.focusManager.restoreFocus();
    
    saveState({
      isActive: false,
      currentStep: null,
      isTourCompleted: true,
      completedSteps: [...state.completedSteps, state.currentStep || '']
    });
  }, [saveState, state.completedSteps, state.currentStep]);

  const toggleGuide = useCallback(() => {
    saveState({
      isGuideDisabled: !state.isGuideDisabled
    });
  }, [saveState, state.isGuideDisabled]);

  const resetGuide = useCallback(() => {
    localStorage.removeItem(STORAGE_KEYS.FIRST_VISIT);
    localStorage.removeItem(STORAGE_KEYS.COMPLETED_STEPS);
    localStorage.removeItem(STORAGE_KEYS.TOUR_COMPLETED);
    localStorage.removeItem(STORAGE_KEYS.GUIDE_DISABLED);
    localStorage.removeItem(STORAGE_KEYS.CURRENT_STEP);
    
    setState({
      isActive: false,
      currentStep: null,
      completedSteps: [],
      isFirstVisit: true,
      isTourCompleted: false,
      isGuideDisabled: false
    });
  }, []);

  const getCurrentStepData = useCallback((): GuideStep | null => {
    if (!state.currentStep) return null;
    return steps.find(step => step.id === state.currentStep) || null;
  }, [state.currentStep, steps]);

  const isStepCompleted = useCallback((stepId: string): boolean => {
    return state.completedSteps.includes(stepId);
  }, [state.completedSteps]);

  const contextValue: GuideContextType = {
    state,
    startTour,
    nextStep,
    prevStep,
    skipTour,
    completeTour,
    toggleGuide,
    resetGuide,
    getCurrentStepData,
    isStepCompleted
  };

  return (
    <GuideContext.Provider value={contextValue}>
      {children}
      {state.isActive && typeof window !== 'undefined' && (
        <TourOverlay />
      )}
    </GuideContext.Provider>
  );
}

// ツアーオーバーレイコンポーネント
function TourOverlay() {
  const { state, getCurrentStepData, nextStep, prevStep, skipTour, completeTour } = useGuide();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  const currentStepData = getCurrentStepData();
  if (!currentStepData) return null;

  return createPortal(
    <div className="fixed inset-0 z-50">
      <div className="absolute inset-0 bg-black/50" />
      <Coachmark 
        step={currentStepData}
        onNext={nextStep}
        onPrev={prevStep}
        onSkip={skipTour}
        onComplete={completeTour}
        isFirst={!currentStepData.prev}
        isLast={!currentStepData.next}
      />
    </div>,
    document.body
  );
}

// フック
export function useGuide(): GuideContextType {
  const context = useContext(GuideContext);
  if (!context) {
    throw new Error('useGuide must be used within a TourProvider');
  }
  return context;
}

// コーチマークコンポーネント
interface CoachmarkProps {
  step: GuideStep;
  onNext: () => void;
  onPrev: () => void;
  onSkip: () => void;
  onComplete: () => void;
  isFirst: boolean;
  isLast: boolean;
}

function Coachmark({ step, onNext, onPrev, onSkip, onComplete, isFirst, isLast }: CoachmarkProps) {
  const [targetElement, setTargetElement] = useState<HTMLElement | null>(null);
  const [position, setPosition] = useState({ top: 0, left: 0, width: 0, height: 0 });

  useEffect(() => {
    const element = document.querySelector(step.target) as HTMLElement;
    if (element) {
      setTargetElement(element);
      const rect = element.getBoundingClientRect();
      setPosition({
        top: rect.top + window.scrollY,
        left: rect.left + window.scrollX,
        width: rect.width,
        height: rect.height
      });
    }
  }, [step.target]);

  useEffect(() => {
    if (!targetElement) {
      // ターゲットが見つからない場合は次のステップへ
      const timer = setTimeout(() => {
        onNext();
      }, 0);
      return () => clearTimeout(timer);
    }
  }, [targetElement, onNext]);

  if (!targetElement) {
    return null;
  }

  const getTooltipPosition = () => {
    const { top, left, width, height } = position;
    const tooltipWidth = 320;
    const tooltipHeight = 200;
    const margin = 16;

    switch (step.placement) {
      case 'top':
        return {
          top: top - tooltipHeight - margin,
          left: left + width / 2 - tooltipWidth / 2
        };
      case 'bottom':
        return {
          top: top + height + margin,
          left: left + width / 2 - tooltipWidth / 2
        };
      case 'left':
        return {
          top: top + height / 2 - tooltipHeight / 2,
          left: left - tooltipWidth - margin
        };
      case 'right':
        return {
          top: top + height / 2 - tooltipHeight / 2,
          left: left + width + margin
        };
      default:
        // auto
        const spaceTop = top;
        const spaceBottom = window.innerHeight - (top + height);
        const spaceLeft = left;
        const spaceRight = window.innerWidth - (left + width);

        if (spaceBottom >= tooltipHeight + margin) {
          return {
            top: top + height + margin,
            left: left + width / 2 - tooltipWidth / 2
          };
        } else if (spaceTop >= tooltipHeight + margin) {
          return {
            top: top - tooltipHeight - margin,
            left: left + width / 2 - tooltipWidth / 2
          };
        } else if (spaceRight >= tooltipWidth + margin) {
          return {
            top: top + height / 2 - tooltipHeight / 2,
            left: left + width + margin
          };
        } else {
          return {
            top: top + height / 2 - tooltipHeight / 2,
            left: left - tooltipWidth - margin
          };
        }
    }
  };

  const tooltipPosition = getTooltipPosition();

  return (
    <>
      {/* ハイライト */}
      <div
        className="absolute border-2 border-blue-500 rounded-lg pointer-events-none"
        style={{
          top: position.top - 4,
          left: position.left - 4,
          width: position.width + 8,
          height: position.height + 8,
          boxShadow: '0 0 0 9999px rgba(0, 0, 0, 0.5)'
        }}
      />
      
      {/* ツールチップ */}
      <div
        className="absolute bg-white rounded-lg shadow-xl p-6 max-w-sm"
        style={{
          top: tooltipPosition.top,
          left: tooltipPosition.left,
          zIndex: 1000
        }}
      >
        {step.title && (
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {step.title}
          </h3>
        )}
        <p className="text-gray-700 mb-4">
          {step.body}
        </p>
        
        <div className="flex justify-between items-center">
          <div className="flex gap-2">
            {!isFirst && (
              <button
                onClick={onPrev}
                className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
              >
                戻る
              </button>
            )}
            <button
              onClick={onSkip}
              className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
            >
              スキップ
            </button>
          </div>
          
          <div className="flex gap-2">
            {isLast ? (
              <button
                onClick={onComplete}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                完了
              </button>
            ) : (
              <button
                onClick={onNext}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                次へ
              </button>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
