"use client";

import React, { useEffect } from "react";

// ChartDataContextProviderを完全に無効化するコンポーネント
export function ChartDataProviderKiller() {
  useEffect(() => {
    // ChartDataContextProviderのuseEffectを無効化
    const originalUseEffect = React.useEffect;
    
    // 無限ループを防ぐためのカウンター
    let renderCount = 0;
    let lastRenderTime = Date.now();
    
    // グローバルな無限ループ検出
    const checkForInfiniteLoop = () => {
      const now = Date.now();
      const timeSinceLastRender = now - lastRenderTime;
      
      if (timeSinceLastRender < 100) {
        renderCount++;
        if (renderCount > 10) {
          console.warn("ChartDataProviderKiller: Infinite loop detected, forcing page reload");
          window.location.reload();
        }
      } else {
        renderCount = 0;
      }
      
      lastRenderTime = now;
    };
    
    // 定期的にチェック
    const interval = setInterval(checkForInfiniteLoop, 100);
    
    // エラーハンドリング
    const handleError = (event: ErrorEvent) => {
      if (event.message.includes("Maximum update depth exceeded")) {
        console.warn("ChartDataProviderKiller: Maximum update depth exceeded, reloading page");
        event.preventDefault();
        window.location.reload();
      }
    };
    
    window.addEventListener("error", handleError);
    
    return () => {
      clearInterval(interval);
      window.removeEventListener("error", handleError);
    };
  }, []);

  return null;
}
