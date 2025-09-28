"use client";

import React, { useState, useRef, useEffect } from 'react';
import { HelpCircle, Info } from 'lucide-react';

interface TooltipProps {
  content: string;
  detail?: string;
  children: React.ReactNode;
  placement?: 'top' | 'bottom' | 'left' | 'right' | 'auto';
  trigger?: 'hover' | 'click' | 'focus';
  maxWidth?: number;
  className?: string;
}

export default function Tooltip({ 
  content, 
  detail,
  children, 
  placement = 'auto',
  trigger = 'hover',
  maxWidth = 300,
  className = ''
}: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const tooltipRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLDivElement>(null);

  const updatePosition = () => {
    if (!triggerRef.current || !tooltipRef.current) return;

    const triggerRect = triggerRef.current.getBoundingClientRect();
    const tooltipRect = tooltipRef.current.getBoundingClientRect();
    const margin = 8;

    let newTop = triggerRect.top;
    let newLeft = triggerRect.left;

    switch (placement) {
      case 'top':
        newTop = triggerRect.top - tooltipRect.height - margin;
        newLeft = triggerRect.left + triggerRect.width / 2 - tooltipRect.width / 2;
        break;
      case 'bottom':
        newTop = triggerRect.bottom + margin;
        newLeft = triggerRect.left + triggerRect.width / 2 - tooltipRect.width / 2;
        break;
      case 'left':
        newTop = triggerRect.top + triggerRect.height / 2 - tooltipRect.height / 2;
        newLeft = triggerRect.left - tooltipRect.width - margin;
        break;
      case 'right':
        newTop = triggerRect.top + triggerRect.height / 2 - tooltipRect.height / 2;
        newLeft = triggerRect.right + margin;
        break;
      default:
        // auto placement
        const spaceTop = triggerRect.top;
        const spaceBottom = window.innerHeight - triggerRect.bottom;
        const spaceLeft = triggerRect.left;
        const spaceRight = window.innerWidth - triggerRect.right;

        if (spaceBottom >= tooltipRect.height + margin) {
          newTop = triggerRect.bottom + margin;
          newLeft = triggerRect.left + triggerRect.width / 2 - tooltipRect.width / 2;
        } else if (spaceTop >= tooltipRect.height + margin) {
          newTop = triggerRect.top - tooltipRect.height - margin;
          newLeft = triggerRect.left + triggerRect.width / 2 - tooltipRect.width / 2;
        } else if (spaceRight >= tooltipRect.width + margin) {
          newTop = triggerRect.top + triggerRect.height / 2 - tooltipRect.height / 2;
          newLeft = triggerRect.right + margin;
        } else {
          newTop = triggerRect.top + triggerRect.height / 2 - tooltipRect.height / 2;
          newLeft = triggerRect.left - tooltipRect.width - margin;
        }
        break;
    }

    // 画面内に収まるように調整
    const adjustedTop = Math.max(margin, Math.min(newTop, window.innerHeight - tooltipRect.height - margin));
    const adjustedLeft = Math.max(margin, Math.min(newLeft, window.innerWidth - tooltipRect.width - margin));

    setPosition({
      top: adjustedTop + window.scrollY,
      left: adjustedLeft + window.scrollX
    });
  };

  useEffect(() => {
    if (isVisible) {
      updatePosition();
      window.addEventListener('resize', updatePosition);
      window.addEventListener('scroll', updatePosition);
    }

    return () => {
      window.removeEventListener('resize', updatePosition);
      window.removeEventListener('scroll', updatePosition);
    };
  }, [isVisible, placement]);

  const handleMouseEnter = () => {
    if (trigger === 'hover') {
      setIsVisible(true);
    }
  };

  const handleMouseLeave = () => {
    if (trigger === 'hover') {
      setIsVisible(false);
    }
  };

  const handleClick = () => {
    if (trigger === 'click') {
      setIsVisible(!isVisible);
    }
  };

  const handleFocus = () => {
    if (trigger === 'focus') {
      setIsVisible(true);
    }
  };

  const handleBlur = () => {
    if (trigger === 'focus') {
      setIsVisible(false);
    }
  };

  return (
    <div 
      ref={triggerRef}
      className={`relative inline-block ${className}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={handleClick}
      onFocus={handleFocus}
      onBlur={handleBlur}
    >
      {children}
      
      {isVisible && (
        <div
          ref={tooltipRef}
          className="absolute z-50 bg-gray-900 text-white text-sm rounded-lg shadow-lg p-3 pointer-events-none"
          style={{
            top: position.top,
            left: position.left,
            maxWidth: maxWidth
          }}
          role="tooltip"
        >
          <div className="flex items-start gap-2">
            <Info size={14} className="text-blue-300 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium">{content}</p>
              {detail && (
                <p className="text-gray-300 text-xs mt-1">{detail}</p>
              )}
            </div>
          </div>
          
          {/* 矢印 */}
          <div 
            className="absolute w-2 h-2 bg-gray-900 transform rotate-45"
            style={{
              [placement === 'top' ? 'bottom' : placement === 'bottom' ? 'top' : 
               placement === 'left' ? 'right' : 'left']: '-4px',
              [placement === 'top' || placement === 'bottom' ? 'left' : 'top']: '50%',
              transform: placement === 'top' || placement === 'bottom' ? 
                'translateX(-50%) rotate(45deg)' : 'translateY(-50%) rotate(45deg)'
            }}
          />
        </div>
      )}
    </div>
  );
}

// 簡易ツールチップ（ホバー専用）
export function SimpleTooltip({ content, children, className = '' }: { 
  content: string; 
  children: React.ReactNode; 
  className?: string;
}) {
  return (
    <Tooltip content={content} trigger="hover" className={className}>
      {children}
    </Tooltip>
  );
}

// 指標用ツールチップ
export function MetricTooltip({ 
  metric, 
  value, 
  description, 
  children, 
  className = '' 
}: { 
  metric: string; 
  value: string; 
  description: string; 
  children: React.ReactNode; 
  className?: string;
}) {
  return (
    <Tooltip 
      content={`${metric}: ${value}`}
      detail={description}
      trigger="hover"
      className={className}
    >
      {children}
    </Tooltip>
  );
}

// ヘルプアイコン付きツールチップ
export function HelpTooltip({ content, detail, className = '' }: { 
  content: string; 
  detail?: string; 
  className?: string;
}) {
  return (
    <Tooltip content={content} detail={detail} trigger="hover" className={className}>
      <HelpCircle size={16} className="text-gray-400 hover:text-gray-600 cursor-help" />
    </Tooltip>
  );
}
