"use client";

import { useState, useRef, useEffect } from "react";
import { HelpCircle } from "lucide-react";

interface TooltipProps {
  content: string;
  children: React.ReactNode;
  position?: "top" | "bottom" | "left" | "right";
  className?: string;
  maxWidth?: string;
}

export default function Tooltip({ 
  content, 
  children, 
  position = "top", 
  className = "",
  maxWidth = "300px"
}: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState({ top: 0, left: 0 });
  const triggerRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  const updatePosition = () => {
    if (!triggerRef.current || !tooltipRef.current) return;

    const triggerRect = triggerRef.current.getBoundingClientRect();
    const tooltipRect = tooltipRef.current.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    let top = 0;
    let left = 0;

    switch (position) {
      case "top":
        top = triggerRect.top - tooltipRect.height - 8;
        left = triggerRect.left + (triggerRect.width - tooltipRect.width) / 2;
        break;
      case "bottom":
        top = triggerRect.bottom + 8;
        left = triggerRect.left + (triggerRect.width - tooltipRect.width) / 2;
        break;
      case "left":
        top = triggerRect.top + (triggerRect.height - tooltipRect.height) / 2;
        left = triggerRect.left - tooltipRect.width - 8;
        break;
      case "right":
        top = triggerRect.top + (triggerRect.height - tooltipRect.height) / 2;
        left = triggerRect.right + 8;
        break;
    }

    // ビューポートからはみ出さないように調整
    if (left < 8) left = 8;
    if (left + tooltipRect.width > viewportWidth - 8) {
      left = viewportWidth - tooltipRect.width - 8;
    }
    if (top < 8) top = 8;
    if (top + tooltipRect.height > viewportHeight - 8) {
      top = viewportHeight - tooltipRect.height - 8;
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

  return (
    <div className={`relative inline-block ${className}`}>
      <div
        ref={triggerRef}
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
        onFocus={() => setIsVisible(true)}
        onBlur={() => setIsVisible(false)}
        className="cursor-help"
      >
        {children}
      </div>
      
      {isVisible && (
        <div
          ref={tooltipRef}
          className="fixed z-50 px-3 py-2 text-sm text-white bg-gray-900 rounded-lg shadow-lg pointer-events-none"
          style={{
            top: tooltipPosition.top,
            left: tooltipPosition.left,
            maxWidth: maxWidth,
          }}
        >
          <div className="whitespace-pre-wrap">{content}</div>
          {/* 矢印 */}
          <div
            className={`absolute w-2 h-2 bg-gray-900 transform rotate-45 ${
              position === "top" ? "top-full left-1/2 -translate-x-1/2 -translate-y-1/2" :
              position === "bottom" ? "bottom-full left-1/2 -translate-x-1/2 translate-y-1/2" :
              position === "left" ? "left-full top-1/2 -translate-y-1/2 -translate-x-1/2" :
              "right-full top-1/2 -translate-y-1/2 translate-x-1/2"
            }`}
          />
        </div>
      )}
    </div>
  );
}

interface HelpTooltipProps {
  content: string;
  className?: string;
}

export function HelpTooltip({ content, className = "" }: HelpTooltipProps) {
  return (
    <Tooltip content={content} className={className}>
      <HelpCircle className="h-4 w-4 text-gray-400 hover:text-gray-600 transition-colors" />
    </Tooltip>
  );
}

interface ValidationTooltipProps {
  isValid: boolean;
  message: string;
  children: React.ReactNode;
  className?: string;
}

export function ValidationTooltip({ 
  isValid, 
  message, 
  children, 
  className = "" 
}: ValidationTooltipProps) {
  const [isVisible, setIsVisible] = useState(false);

  if (isValid) return <>{children}</>;

  return (
    <div className={`relative ${className}`}>
      <div
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
        className="relative"
      >
        {children}
        {/* エラーインジケーター */}
        <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full border-2 border-white" />
      </div>
      
      {isVisible && (
        <div className="absolute z-50 px-3 py-2 text-sm text-white bg-red-600 rounded-lg shadow-lg pointer-events-none top-full left-0 mt-1">
          <div className="whitespace-pre-wrap">{message}</div>
          <div className="absolute -top-1 left-4 w-2 h-2 bg-red-600 transform rotate-45" />
        </div>
      )}
    </div>
  );
}