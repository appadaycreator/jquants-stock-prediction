"use client";

import React, { useState, useEffect, useRef } from 'react';
import { X, ChevronLeft, ChevronRight, SkipForward } from 'lucide-react';
import { accessibilityUtils } from '../../lib/guide/accessibility';

interface CoachmarkProps {
  step: {
    id: string;
    target: string;
    title?: string;
    body: string;
    placement: "top" | "right" | "bottom" | "left" | "auto";
  };
  onNext: () => void;
  onPrev: () => void;
  onSkip: () => void;
  onComplete: () => void;
  isFirst: boolean;
  isLast: boolean;
  stepNumber?: number;
  totalSteps?: number;
}

export default function Coachmark({ 
  step, 
  onNext, 
  onPrev, 
  onSkip, 
  onComplete, 
  isFirst, 
  isLast,
  stepNumber = 1,
  totalSteps = 10
}: CoachmarkProps) {
  const [targetElement, setTargetElement] = useState<HTMLElement | null>(null);
  const [position, setPosition] = useState({ top: 0, left: 0, width: 0, height: 0 });
  const [tooltipPosition, setTooltipPosition] = useState({ top: 0, left: 0 });
  const tooltipRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const updatePosition = () => {
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
    };

    updatePosition();
    window.addEventListener('resize', updatePosition);
    window.addEventListener('scroll', updatePosition);

    return () => {
      window.removeEventListener('resize', updatePosition);
      window.removeEventListener('scroll', updatePosition);
    };
  }, [step.target]);

  // アクセシビリティ対応
  useEffect(() => {
    if (targetElement) {
      // スクリーンリーダーにステップをアナウンス
      accessibilityUtils.screenReader.announceStep(step.title || '', step.body);
      
      // フォーカストラップを設定
      const cleanup = accessibilityUtils.focusManager.trapFocus(tooltipRef.current!);
      return cleanup;
    }
  }, [targetElement, step.title, step.body]);

  useEffect(() => {
    if (targetElement && tooltipRef.current) {
      const tooltipRect = tooltipRef.current.getBoundingClientRect();
      const { top, left, width, height } = position;
      const tooltipWidth = 320;
      const tooltipHeight = 200;
      const margin = 16;

      let newTop = top;
      let newLeft = left;

      switch (step.placement) {
        case 'top':
          newTop = top - tooltipHeight - margin;
          newLeft = left + width / 2 - tooltipWidth / 2;
          break;
        case 'bottom':
          newTop = top + height + margin;
          newLeft = left + width / 2 - tooltipWidth / 2;
          break;
        case 'left':
          newTop = top + height / 2 - tooltipHeight / 2;
          newLeft = left - tooltipWidth - margin;
          break;
        case 'right':
          newTop = top + height / 2 - tooltipHeight / 2;
          newLeft = left + width + margin;
          break;
        default:
          // auto placement
          const spaceTop = top;
          const spaceBottom = window.innerHeight - (top + height);
          const spaceLeft = left;
          const spaceRight = window.innerWidth - (left + width);

          if (spaceBottom >= tooltipHeight + margin) {
            newTop = top + height + margin;
            newLeft = left + width / 2 - tooltipWidth / 2;
          } else if (spaceTop >= tooltipHeight + margin) {
            newTop = top - tooltipHeight - margin;
            newLeft = left + width / 2 - tooltipWidth / 2;
          } else if (spaceRight >= tooltipWidth + margin) {
            newTop = top + height / 2 - tooltipHeight / 2;
            newLeft = left + width + margin;
          } else {
            newTop = top + height / 2 - tooltipHeight / 2;
            newLeft = left - tooltipWidth - margin;
          }
          break;
      }

      // 画面内に収まるように調整
      const adjustedTop = Math.max(margin, Math.min(newTop, window.innerHeight - tooltipHeight - margin));
      const adjustedLeft = Math.max(margin, Math.min(newLeft, window.innerWidth - tooltipWidth - margin));

      setTooltipPosition({
        top: adjustedTop,
        left: adjustedLeft
      });
    }
  }, [targetElement, position, step.placement]);

  if (!targetElement) {
    // ターゲットが見つからない場合は次のステップへ
    setTimeout(onNext, 100);
    return null;
  }

  return (
    <>
      {/* ハイライトオーバーレイ */}
      <div
        className="absolute border-2 border-blue-500 rounded-lg pointer-events-none animate-pulse"
        style={{
          top: position.top - 4,
          left: position.left - 4,
          width: position.width + 8,
          height: position.height + 8,
          boxShadow: '0 0 0 9999px rgba(0, 0, 0, 0.5)',
          zIndex: 1000
        }}
      />
      
      {/* ツールチップ */}
      <div
        ref={tooltipRef}
        className="absolute bg-white rounded-lg shadow-xl p-6 max-w-sm border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
        style={{
          top: tooltipPosition.top,
          left: tooltipPosition.left,
          zIndex: 1001
        }}
        role="dialog"
        aria-labelledby="coachmark-title"
        aria-describedby="coachmark-description"
        tabIndex={-1}
        {...accessibilityUtils.generateAriaAttributes('tour')}
      >
        {/* ヘッダー */}
        <div className="flex justify-between items-start mb-3">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <span className="text-sm text-gray-500">
              {stepNumber} / {totalSteps}
            </span>
          </div>
          <button
            onClick={onSkip}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="ガイドをスキップ"
          >
            <X size={16} />
          </button>
        </div>

        {/* タイトル */}
        {step.title && (
          <h3 id="coachmark-title" className="text-lg font-semibold text-gray-900 mb-2">
            {step.title}
          </h3>
        )}

        {/* 説明文 */}
        <p id="coachmark-description" className="text-gray-700 mb-4 leading-relaxed">
          {step.body}
        </p>
        
        {/* フッター */}
        <div className="flex justify-between items-center">
          <div className="flex gap-2">
            {!isFirst && (
              <button
                onClick={onPrev}
                className="flex items-center gap-1 px-3 py-1.5 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-md transition-colors"
                aria-label="前のステップに戻る"
              >
                <ChevronLeft size={14} />
                戻る
              </button>
            )}
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={onSkip}
              className="flex items-center gap-1 px-3 py-1.5 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-md transition-colors"
              aria-label="ガイドをスキップ"
            >
              <SkipForward size={14} />
              スキップ
            </button>
            
            {isLast ? (
              <button
                onClick={onComplete}
                className="flex items-center gap-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
                aria-label="ガイドを完了"
              >
                完了
              </button>
            ) : (
              <button
                onClick={onNext}
                className="flex items-center gap-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
                aria-label="次のステップへ"
              >
                次へ
                <ChevronRight size={14} />
              </button>
            )}
          </div>
        </div>

        {/* キーボードショートカットのヒント */}
        <div className="mt-3 pt-3 border-t border-gray-100">
          <p className="text-xs text-gray-500">
            💡 キーボード: ← → で移動、Esc でスキップ、Enter で次へ
          </p>
        </div>
      </div>
    </>
  );
}
