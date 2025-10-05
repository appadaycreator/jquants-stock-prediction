"use client";

import React, { ReactNode } from "react";

interface TouchTargetProps {
  children: ReactNode;
  size?: "small" | "medium" | "large";
  minSize?: number;
  className?: string;
  onClick?: () => void;
  disabled?: boolean;
  ariaLabel?: string;
}

const SIZE_CLASSES = {
  small: "min-h-[44px] min-w-[44px] p-2",
  medium: "min-h-[48px] min-w-[48px] p-3",
  large: "min-h-[56px] min-w-[56px] p-4",
};

export function TouchTarget({ 
  children, 
  size = "medium",
  minSize = 48,
  className = "",
  onClick,
  disabled = false,
  ariaLabel,
}: TouchTargetProps) {
  const baseClasses = `
    flex items-center justify-center
    transition-all duration-200
    focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
    active:scale-95
    ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer hover:bg-gray-100"}
    ${SIZE_CLASSES[size]}
  `;

  const style = {
    minHeight: `${minSize}px`,
    minWidth: `${minSize}px`,
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${baseClasses} ${className}`}
      style={style}
      aria-label={ariaLabel}
      role="button"
    >
      {children}
    </button>
  );
}

// 特殊化されたタッチターゲットコンポーネント
export function IconButton({ 
  icon, 
  onClick, 
  disabled = false,
  ariaLabel,
  className = "",
}: {
  icon: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  ariaLabel?: string;
  className?: string;
}) {
  return (
    <TouchTarget
      onClick={onClick}
      disabled={disabled}
      ariaLabel={ariaLabel}
      className={`rounded-lg ${className}`}
    >
      {icon}
    </TouchTarget>
  );
}

export function TextButton({ 
  children, 
  onClick, 
  disabled = false,
  variant = "default",
  className = "",
}: {
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  variant?: "default" | "primary" | "secondary";
  className?: string;
}) {
  const variantClasses = {
    default: "bg-white text-gray-900 border border-gray-300 hover:bg-gray-50",
    primary: "bg-blue-600 text-white hover:bg-blue-700",
    secondary: "bg-gray-600 text-white hover:bg-gray-700",
  };

  return (
    <TouchTarget
      onClick={onClick}
      disabled={disabled}
      className={`rounded-lg font-medium ${variantClasses[variant]} ${className}`}
    >
      {children}
    </TouchTarget>
  );
}

export function CardButton({ 
  children, 
  onClick, 
  disabled = false,
  className = "",
}: {
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  className?: string;
}) {
  return (
    <TouchTarget
      onClick={onClick}
      disabled={disabled}
      className={`
        bg-white rounded-lg shadow-sm border border-gray-200
        hover:shadow-md hover:border-gray-300
        active:shadow-sm
        ${className}
      `}
    >
      {children}
    </TouchTarget>
  );
}

// スワイプジェスチャー対応コンポーネント
export function SwipeableCard({ 
  children, 
  onSwipeLeft, 
  onSwipeRight,
  onSwipeUp,
  onSwipeDown,
  className = "",
}: {
  children: ReactNode;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  className?: string;
}) {
  const handleTouchStart = (e: React.TouchEvent) => {
    const startX = e.touches[0].clientX;
    const startY = e.touches[0].clientY;
    
    const handleTouchEnd = (e: TouchEvent) => {
      const endX = e.changedTouches[0].clientX;
      const endY = e.changedTouches[0].clientY;
      const deltaX = endX - startX;
      const deltaY = endY - startY;
      
      const minSwipeDistance = 50;
      
      if (Math.abs(deltaX) > Math.abs(deltaY)) {
        // 水平スワイプ
        if (Math.abs(deltaX) > minSwipeDistance) {
          if (deltaX > 0) {
            onSwipeRight?.();
          } else {
            onSwipeLeft?.();
          }
        }
      } else {
        // 垂直スワイプ
        if (Math.abs(deltaY) > minSwipeDistance) {
          if (deltaY > 0) {
            onSwipeDown?.();
          } else {
            onSwipeUp?.();
          }
        }
      }
      
      document.removeEventListener("touchend", handleTouchEnd);
    };
    
    document.addEventListener("touchend", handleTouchEnd);
  };

  return (
    <div
      onTouchStart={handleTouchStart}
      className={`touch-manipulation ${className}`}
    >
      {children}
    </div>
  );
}

// 長押し対応コンポーネント
export function LongPressButton({ 
  children, 
  onLongPress,
  onPress,
  longPressDelay = 500,
  className = "",
}: {
  children: ReactNode;
  onLongPress?: () => void;
  onPress?: () => void;
  longPressDelay?: number;
  className?: string;
}) {
  const [isLongPressing, setIsLongPressing] = React.useState(false);
  const longPressTimerRef = React.useRef<NodeJS.Timeout>();

  const handleTouchStart = () => {
    longPressTimerRef.current = setTimeout(() => {
      setIsLongPressing(true);
      onLongPress?.();
    }, longPressDelay);
  };

  const handleTouchEnd = () => {
    if (longPressTimerRef.current) {
      clearTimeout(longPressTimerRef.current);
    }
    
    if (!isLongPressing) {
      onPress?.();
    }
    
    setIsLongPressing(false);
  };

  const handleTouchCancel = () => {
    if (longPressTimerRef.current) {
      clearTimeout(longPressTimerRef.current);
    }
    setIsLongPressing(false);
  };

  return (
    <TouchTarget
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
      onTouchCancel={handleTouchCancel}
      className={`${isLongPressing ? "bg-blue-100" : ""} ${className}`}
    >
      {children}
    </TouchTarget>
  );
}
