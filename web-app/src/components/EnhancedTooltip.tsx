"use client";

import React, { useState, useRef, useEffect } from 'react';
import { HelpCircle, Info, AlertTriangle, CheckCircle, X } from 'lucide-react';

export type TooltipType = 'info' | 'warning' | 'success' | 'error' | 'help';

interface EnhancedTooltipProps {
  content: React.ReactNode;
  children: React.ReactNode;
  type?: TooltipType;
  position?: 'top' | 'bottom' | 'left' | 'right';
  delay?: number;
  maxWidth?: number;
  className?: string;
  disabled?: boolean;
  persistent?: boolean;
  title?: string;
}

const EnhancedTooltip: React.FC<EnhancedTooltipProps> = ({
  content,
  children,
  type = 'info',
  position = 'top',
  delay = 300,
  maxWidth = 300,
  className = '',
  disabled = false,
  persistent = false,
  title,
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isPersistent, setIsPersistent] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout>();
  const tooltipRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLDivElement>(null);

  const getIcon = () => {
    switch (type) {
      case 'warning':
        return <AlertTriangle className="h-4 w-4" />;
      case 'success':
        return <CheckCircle className="h-4 w-4" />;
      case 'error':
        return <X className="h-4 w-4" />;
      case 'help':
        return <HelpCircle className="h-4 w-4" />;
      default:
        return <Info className="h-4 w-4" />;
    }
  };

  const getTypeStyles = () => {
    switch (type) {
      case 'warning':
        return 'bg-themed-warning-light border-themed-warning text-themed-warning';
      case 'success':
        return 'bg-themed-success-light border-themed-success text-themed-success';
      case 'error':
        return 'bg-themed-error-light border-themed-error text-themed-error';
      case 'help':
        return 'bg-themed-info-light border-themed-info text-themed-info';
      default:
        return 'bg-themed-background-secondary border-themed-border text-themed-text-primary';
    }
  };

  const getPositionStyles = () => {
    switch (position) {
      case 'top':
        return 'bottom-full left-1/2 transform -translate-x-1/2 mb-2';
      case 'bottom':
        return 'top-full left-1/2 transform -translate-x-1/2 mt-2';
      case 'left':
        return 'right-full top-1/2 transform -translate-y-1/2 mr-2';
      case 'right':
        return 'left-full top-1/2 transform -translate-y-1/2 ml-2';
      default:
        return 'bottom-full left-1/2 transform -translate-x-1/2 mb-2';
    }
  };

  const getArrowStyles = () => {
    switch (position) {
      case 'top':
        return 'top-full left-1/2 transform -translate-x-1/2 border-l-transparent border-r-transparent border-b-transparent border-t-themed-border';
      case 'bottom':
        return 'bottom-full left-1/2 transform -translate-x-1/2 border-l-transparent border-r-transparent border-t-transparent border-b-themed-border';
      case 'left':
        return 'left-full top-1/2 transform -translate-y-1/2 border-t-transparent border-b-transparent border-r-transparent border-l-themed-border';
      case 'right':
        return 'right-full top-1/2 transform -translate-y-1/2 border-t-transparent border-b-transparent border-l-transparent border-r-themed-border';
      default:
        return 'top-full left-1/2 transform -translate-x-1/2 border-l-transparent border-r-transparent border-b-transparent border-t-themed-border';
    }
  };

  const showTooltip = () => {
    if (disabled) return;
    
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true);
    }, delay);
  };

  const hideTooltip = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    
    if (!persistent || !isPersistent) {
      setIsVisible(false);
    }
  };

  const togglePersistent = () => {
    if (persistent) {
      setIsPersistent(!isPersistent);
      if (!isPersistent) {
        setIsVisible(true);
      }
    }
  };

  const handleClick = () => {
    if (persistent) {
      togglePersistent();
    }
  };

  // クリック外部でツールチップを閉じる
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        tooltipRef.current &&
        !tooltipRef.current.contains(event.target as Node) &&
        triggerRef.current &&
        !triggerRef.current.contains(event.target as Node)
      ) {
        setIsVisible(false);
        setIsPersistent(false);
      }
    };

    if (isVisible || isPersistent) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isVisible, isPersistent]);

  // キーボードナビゲーション対応
  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      if (persistent) {
        togglePersistent();
      } else {
        setIsVisible(!isVisible);
      }
    } else if (event.key === 'Escape') {
      setIsVisible(false);
      setIsPersistent(false);
    }
  };

  return (
    <div className={`relative inline-block ${className}`}>
      <div
        ref={triggerRef}
        onMouseEnter={showTooltip}
        onMouseLeave={hideTooltip}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        tabIndex={0}
        role="button"
        aria-describedby={isVisible ? 'tooltip' : undefined}
        title={title}
        className="cursor-pointer focus:outline-none focus:ring-2 focus:ring-themed-border-focus focus:ring-offset-2 rounded"
      >
        {children}
      </div>

      {(isVisible || isPersistent) && (
        <div
          ref={tooltipRef}
          id="tooltip"
          role="tooltip"
          className={`
            absolute z-50 px-3 py-2 rounded-lg border shadow-lg
            ${getTypeStyles()}
            ${getPositionStyles()}
            ${persistent ? 'pointer-events-auto' : 'pointer-events-none'}
          `}
          style={{ maxWidth: `${maxWidth}px` }}
        >
          <div className="flex items-start space-x-2">
            <div className="flex-shrink-0 mt-0.5">
              {getIcon()}
            </div>
            <div className="flex-1 text-sm">
              {content}
            </div>
            {persistent && (
              <button
                onClick={() => {
                  setIsVisible(false);
                  setIsPersistent(false);
                }}
                className="flex-shrink-0 ml-2 text-themed-text-tertiary hover:text-themed-text-secondary"
                aria-label="ツールチップを閉じる"
              >
                <X className="h-3 w-3" />
              </button>
            )}
          </div>
          
          {/* 矢印 */}
          <div
            className={`
              absolute w-0 h-0 border-4
              ${getArrowStyles()}
            `}
          />
        </div>
      )}
    </div>
  );
};

export default EnhancedTooltip;
