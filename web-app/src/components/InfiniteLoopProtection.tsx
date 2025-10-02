"use client";

import React, { useEffect, useRef, useState } from "react";
import { infiniteLoopDetector } from "@/lib/infiniteLoopDetector";

interface InfiniteLoopProtectionProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  componentId?: string;
}

export default function InfiniteLoopProtection({ 
  children, 
  fallback,
  componentId = "default",
}: InfiniteLoopProtectionProps) {
  const [isBlocked, setIsBlocked] = useState(false);
  const renderCount = useRef(0);
  const lastRenderTime = useRef(Date.now());
  const blockTimeout = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    renderCount.current += 1;
    const now = Date.now();
    const timeSinceLastRender = now - lastRenderTime.current;
    
    // より厳しい条件で無限ループを検出
    if (timeSinceLastRender < 50 && renderCount.current > 15) {
      console.warn("InfiniteLoopProtection: Infinite loop detected, blocking");
      setIsBlocked(true);
      
      // 5秒後にブロックを解除
      if (blockTimeout.current) {
        clearTimeout(blockTimeout.current);
      }
      blockTimeout.current = setTimeout(() => {
        setIsBlocked(false);
        renderCount.current = 0;
        console.log("Infinite loop protection reset");
      }, 5000);
    }
    
    lastRenderTime.current = now;
    
    // レンダリングカウントをリセット（正常な間隔の場合）
    if (timeSinceLastRender > 1000) {
      renderCount.current = 0;
    }
  });

  useEffect(() => {
    return () => {
      if (blockTimeout.current) {
        clearTimeout(blockTimeout.current);
      }
    };
  }, []);

  // ブロック状態をチェック
  useEffect(() => {
    if (infiniteLoopDetector.isBlocked(componentId)) {
      setIsBlocked(true);
    }
  }, [componentId]);

  if (isBlocked) {
    if (fallback) {
      return <>{fallback}</>;
    }
    
    return (
      <div className="flex flex-col items-center justify-center p-4 bg-red-50 border border-red-200 rounded-lg">
        <div className="text-red-800 text-center">
          <h3 className="text-lg font-semibold mb-2">コンポーネントが一時的にブロックされました</h3>
          <p className="text-sm mb-4">
            無限ループが検出されたため、このコンポーネントを一時的にブロックしています。
            数秒後に自動的に復旧します。
          </p>
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-red-600 mx-auto"></div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
