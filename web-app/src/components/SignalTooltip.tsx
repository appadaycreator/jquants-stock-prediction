"use client";

import { useState, useRef, useEffect } from "react";
import { HelpCircle, TrendingUp, TrendingDown, AlertTriangle, Info } from "lucide-react";

interface SignalTooltipProps {
  content: React.ReactNode;
  children: React.ReactNode;
  position?: "top" | "bottom" | "left" | "right";
  maxWidth?: number;
}

export default function SignalTooltip({ 
  content, 
  children, 
  position = "top",
  maxWidth = 300 
}: SignalTooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });
  const triggerRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isVisible && triggerRef.current && tooltipRef.current) {
      const triggerRect = triggerRef.current.getBoundingClientRect();
      const tooltipRect = tooltipRef.current.getBoundingClientRect();
      const scrollX = window.pageXOffset || document.documentElement.scrollLeft;
      const scrollY = window.pageYOffset || document.documentElement.scrollTop;

      let x = 0;
      let y = 0;

      switch (position) {
        case "top":
          x = triggerRect.left + triggerRect.width / 2 - tooltipRect.width / 2 + scrollX;
          y = triggerRect.top - tooltipRect.height - 8 + scrollY;
          break;
        case "bottom":
          x = triggerRect.left + triggerRect.width / 2 - tooltipRect.width / 2 + scrollX;
          y = triggerRect.bottom + 8 + scrollY;
          break;
        case "left":
          x = triggerRect.left - tooltipRect.width - 8 + scrollX;
          y = triggerRect.top + triggerRect.height / 2 - tooltipRect.height / 2 + scrollY;
          break;
        case "right":
          x = triggerRect.right + 8 + scrollX;
          y = triggerRect.top + triggerRect.height / 2 - tooltipRect.height / 2 + scrollY;
          break;
      }

      // 画面外に出ないように調整
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;

      if (x < 0) x = 8;
      if (x + tooltipRect.width > viewportWidth) x = viewportWidth - tooltipRect.width - 8;
      if (y < 0) y = 8;
      if (y + tooltipRect.height > viewportHeight) y = viewportHeight - tooltipRect.height - 8;

      setTooltipPosition({ x, y });
    }
  }, [isVisible, position]);

  const showTooltip = () => setIsVisible(true);
  const hideTooltip = () => setIsVisible(false);

  return (
    <div className="relative inline-block">
      <div
        ref={triggerRef}
        onMouseEnter={showTooltip}
        onMouseLeave={hideTooltip}
        onFocus={showTooltip}
        onBlur={hideTooltip}
        className="inline-block"
      >
        {children}
      </div>

      {isVisible && (
        <div
          ref={tooltipRef}
          className="absolute z-50 bg-gray-900 text-white text-sm rounded-lg shadow-lg p-3 pointer-events-none"
          style={{
            left: tooltipPosition.x,
            top: tooltipPosition.y,
            maxWidth: maxWidth,
          }}
        >
          <div className="relative">
            {content}
            {/* 矢印 */}
            <div
              className={`absolute w-2 h-2 bg-gray-900 transform rotate-45 ${
                position === "top" ? "bottom-[-4px] left-1/2 -translate-x-1/2" :
                position === "bottom" ? "top-[-4px] left-1/2 -translate-x-1/2" :
                position === "left" ? "right-[-4px] top-1/2 -translate-y-1/2" :
                "left-[-4px] top-1/2 -translate-y-1/2"
              }`}
            />
          </div>
        </div>
      )}
    </div>
  );
}

interface SignalCategoryTooltipProps {
  category: string;
  children: React.ReactNode;
}

export function SignalCategoryTooltip({ category, children }: SignalCategoryTooltipProps) {
  const getCategoryInfo = (category: string) => {
    const categoryInfo: { [key: string]: { title: string; description: string; icon: React.ReactNode; color: string } } = {
      "上昇トレンド発生": {
        title: "上昇トレンド発生",
        description: "移動平均線の上昇トレンド形成により、価格の継続的な上昇が期待されるシグナルです。",
        icon: <TrendingUp className="h-4 w-4" />,
        color: "text-green-600"
      },
      "下落トレンド注意": {
        title: "下落トレンド注意",
        description: "下落トレンドの兆候を検出したシグナルです。リスク管理を強化する必要があります。",
        icon: <AlertTriangle className="h-4 w-4" />,
        color: "text-red-600"
      },
      "出来高急増": {
        title: "出来高急増",
        description: "出来高が平均の2倍以上に急増したシグナルです。市場の関心が高まっている可能性があります。",
        icon: <TrendingUp className="h-4 w-4" />,
        color: "text-blue-600"
      },
      "リスクリターン改善": {
        title: "リスクリターン改善",
        description: "シャープレシオの改善により、リスクに対するリターンが向上したシグナルです。",
        icon: <TrendingUp className="h-4 w-4" />,
        color: "text-purple-600"
      },
      "テクニカルブレイクアウト": {
        title: "テクニカルブレイクアウト",
        description: "ボリンジャーバンドの上限を突破したテクニカルブレイクアウトシグナルです。",
        icon: <TrendingUp className="h-4 w-4" />,
        color: "text-orange-600"
      }
    };

    return categoryInfo[category] || {
      title: category,
      description: "シグナルの詳細情報",
      icon: <Info className="h-4 w-4" />,
      color: "text-gray-600"
    };
  };

  const info = getCategoryInfo(category);

  return (
    <SignalTooltip
      content={
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <span className={info.color}>{info.icon}</span>
            <span className="font-semibold">{info.title}</span>
          </div>
          <p className="text-gray-300 text-xs leading-relaxed">{info.description}</p>
        </div>
      }
    >
      {children}
    </SignalTooltip>
  );
}

interface ConfidenceTooltipProps {
  confidence: number;
  children: React.ReactNode;
}

export function ConfidenceTooltip({ confidence, children }: ConfidenceTooltipProps) {
  const getConfidenceLevel = (conf: number) => {
    if (conf >= 0.8) return { level: "高", color: "text-green-400", description: "非常に信頼性の高いシグナル" };
    if (conf >= 0.6) return { level: "中", color: "text-yellow-400", description: "信頼性の高いシグナル" };
    return { level: "低", color: "text-red-400", description: "信頼性の低いシグナル" };
  };

  const { level, color, description } = getConfidenceLevel(confidence);

  return (
    <SignalTooltip
      content={
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <span className={color}>信頼度: {level}</span>
          </div>
          <p className="text-gray-300 text-xs">{description}</p>
          <p className="text-gray-400 text-xs">数値: {(confidence * 100).toFixed(0)}%</p>
        </div>
      }
    >
      {children}
    </SignalTooltip>
  );
}
