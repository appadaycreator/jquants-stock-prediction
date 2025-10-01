"use client";

import React, { useState, useRef, useEffect } from "react";
import { HelpCircle, X } from "lucide-react";

interface TooltipProps {
  content: string | React.ReactNode;
  children: React.ReactNode;
  position?: "top" | "bottom" | "left" | "right";
  delay?: number;
  className?: string;
  maxWidth?: string;
}

export default function Tooltip({
  content,
  children,
  position = "top",
  delay = 300,
  className = "",
  maxWidth = "300px",
}: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState({ top: 0, left: 0 });
  const triggerRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const timeoutRef = useRef<NodeJS.Timeout>();

  const showTooltip = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true);
      updatePosition();
    }, delay);
  };

  const hideTooltip = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsVisible(false);
  };

  const updatePosition = () => {
    if (!triggerRef.current || !tooltipRef.current) return;

    const triggerRect = triggerRef.current.getBoundingClientRect();
    const tooltipRect = tooltipRef.current.getBoundingClientRect();
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;

    let top = 0;
    let left = 0;

    switch (position) {
      case "top":
        top = triggerRect.top + scrollTop - tooltipRect.height - 8;
        left = triggerRect.left + scrollLeft + (triggerRect.width - tooltipRect.width) / 2;
        break;
      case "bottom":
        top = triggerRect.bottom + scrollTop + 8;
        left = triggerRect.left + scrollLeft + (triggerRect.width - tooltipRect.width) / 2;
        break;
      case "left":
        top = triggerRect.top + scrollTop + (triggerRect.height - tooltipRect.height) / 2;
        left = triggerRect.left + scrollLeft - tooltipRect.width - 8;
        break;
      case "right":
        top = triggerRect.top + scrollTop + (triggerRect.height - tooltipRect.height) / 2;
        left = triggerRect.right + scrollLeft + 8;
        break;
    }

    // 画面外に出ないように調整
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    if (left < 8) left = 8;
    if (left + tooltipRect.width > viewportWidth - 8) {
      left = viewportWidth - tooltipRect.width - 8;
    }
    if (top < 8) top = 8;
    if (top + tooltipRect.height > viewportHeight + scrollTop - 8) {
      top = viewportHeight + scrollTop - tooltipRect.height - 8;
    }

    setTooltipPosition({ top, left });
  };

  useEffect(() => {
    if (isVisible) {
      updatePosition();
      const handleResize = () => updatePosition();
      const handleScroll = () => updatePosition();
      
      window.addEventListener("resize", handleResize);
      window.addEventListener("scroll", handleScroll);
      
      return () => {
        window.removeEventListener("resize", handleResize);
        window.removeEventListener("scroll", handleScroll);
      };
    }
  }, [isVisible, position]);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return (
    <div
      ref={triggerRef}
      onMouseEnter={showTooltip}
      onMouseLeave={hideTooltip}
      onFocus={showTooltip}
      onBlur={hideTooltip}
      className={`inline-block ${className}`}
    >
      {children}
      
      {isVisible && (
        <div
          ref={tooltipRef}
          className={`fixed z-50 px-3 py-2 text-sm text-white bg-gray-900 rounded-lg shadow-lg pointer-events-none transition-opacity duration-200 ${
            position === "top" ? "mb-2" : ""
          }`}
          style={{
            top: `${tooltipPosition.top}px`,
            left: `${tooltipPosition.left}px`,
            maxWidth: maxWidth,
          }}
        >
          <div className="relative">
            {content}
            
            {/* 矢印 */}
            <div
              className={`absolute w-2 h-2 bg-gray-900 transform rotate-45 ${
                position === "top" ? "top-full left-1/2 -translate-x-1/2 -mt-1" :
                position === "bottom" ? "bottom-full left-1/2 -translate-x-1/2 -mb-1" :
                position === "left" ? "left-full top-1/2 -translate-y-1/2 -ml-1" :
                "right-full top-1/2 -translate-y-1/2 -mr-1"
              }`}
            />
          </div>
        </div>
      )}
    </div>
  );
}

// ヘルプアイコン付きツールチップ
interface HelpTooltipProps {
  content: string | React.ReactNode;
  className?: string;
}

export function HelpTooltip({ content, className = "" }: HelpTooltipProps) {
  return (
    <Tooltip content={content} position="top" delay={200}>
      <HelpCircle className={`w-4 h-4 text-gray-400 hover:text-gray-600 cursor-help ${className}`} />
    </Tooltip>
  );
}

// ボタン用ツールチップ
interface ButtonTooltipProps {
  content: string | React.ReactNode;
  children: React.ReactNode;
  disabled?: boolean;
  className?: string;
}

export function ButtonTooltip({ content, children, disabled = false, className = "" }: ButtonTooltipProps) {
  if (disabled) {
    return <>{children}</>;
  }

  return (
    <Tooltip content={content} position="top" delay={300}>
      <div className={className}>
        {children}
      </div>
    </Tooltip>
  );
}
