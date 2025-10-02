"use client";

import { useState, useEffect } from "react";
import MobileVerticalLayout from "./MobileVerticalLayout";
import SwipeNavigation from "./SwipeNavigation";
import PullToRefresh from "./PullToRefresh";
import MobileChart from "./MobileChart";

interface MobileOptimizedPageProps {
  children: React.ReactNode;
  enablePullToRefresh?: boolean;
  enableSwipeNavigation?: boolean;
  enableVerticalLayout?: boolean;
  onRefresh?: () => Promise<void>;
  swipePages?: React.ReactNode[];
  chartData?: any[];
  className?: string;
}

export default function MobileOptimizedPage({
  children,
  enablePullToRefresh = true,
  enableSwipeNavigation = false,
  enableVerticalLayout = true,
  onRefresh,
  swipePages = [],
  chartData = [],
  className = "",
}: MobileOptimizedPageProps) {
  const [isMobile, setIsMobile] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // モバイルデバイスの検出
  useEffect(() => {
    const checkMobile = () => {
      const userAgent = navigator.userAgent;
      const isMobileDevice = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
      const isSmallScreen = window.innerWidth <= 768;
      setIsMobile(isMobileDevice || isSmallScreen);
    };

    checkMobile();
    window.addEventListener("resize", checkMobile);
    
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  // リフレッシュ処理
  const handleRefresh = async () => {
    if (!onRefresh) return;
    
    setIsLoading(true);
    try {
      await onRefresh();
    } catch (error) {
      console.error("Refresh failed:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // デスクトップ表示
  if (!isMobile) {
    return (
      <div className={`desktop-layout ${className}`}>
        {children}
      </div>
    );
  }

  // モバイル表示
  const renderContent = () => {
    if (enableSwipeNavigation && swipePages.length > 0) {
      return (
        <SwipeNavigation
          enableSwipe={true}
          enableDots={true}
          enableArrows={true}
          autoPlay={false}
        >
          {swipePages}
        </SwipeNavigation>
      );
    }

    if (enableVerticalLayout) {
      return (
        <MobileVerticalLayout
          enableScrollToTop={true}
          enableScrollIndicator={true}
        >
          {children}
        </MobileVerticalLayout>
      );
    }

    return children;
  };

  return (
    <div className={`mobile-optimized-page ${className}`}>
      {enablePullToRefresh && onRefresh ? (
        <PullToRefresh
          onRefresh={handleRefresh}
          threshold={80}
          resistance={0.5}
        >
          {renderContent()}
        </PullToRefresh>
      ) : (
        renderContent()
      )}

      {/* ローディングインジケーター */}
      {isLoading && (
        <div className="fixed inset-0 bg-black/20 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-4 shadow-lg">
            <div className="flex items-center space-x-3">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <span className="text-gray-700">更新中...</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
