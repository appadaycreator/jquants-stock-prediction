"use client";

import { useState, useEffect, useRef } from "react";
import { RefreshCw } from "lucide-react";

interface PullToRefreshProps {
  onRefresh: () => Promise<void>;
  children: React.ReactNode;
  threshold?: number;
  resistance?: number;
}

export default function PullToRefresh({
  onRefresh,
  children,
  threshold = 80,
  resistance = 0.5,
}: PullToRefreshProps) {
  const [isPulling, setIsPulling] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [pullDistance, setPullDistance] = useState(0);
  const [startY, setStartY] = useState(0);
  const [currentY, setCurrentY] = useState(0);
  const [isAtTop, setIsAtTop] = useState(false);
  
  const containerRef = useRef<HTMLDivElement>(null);
  const pullIndicatorRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleTouchStart = (e: TouchEvent) => {
      const scrollTop = container.scrollTop;
      if (scrollTop === 0) {
        setIsAtTop(true);
        setStartY(e.touches[0].clientY);
        setCurrentY(e.touches[0].clientY);
      }
    };

    const handleTouchMove = (e: TouchEvent) => {
      if (!isAtTop) return;

      const touchY = e.touches[0].clientY;
      const deltaY = touchY - startY;
      
      if (deltaY > 0) {
        e.preventDefault();
        const distance = Math.min(deltaY * resistance, threshold * 1.5);
        setPullDistance(distance);
        setCurrentY(touchY);
        
        if (distance > 0) {
          setIsPulling(true);
        }
      }
    };

    const handleTouchEnd = async () => {
      if (!isAtTop || !isPulling) {
        resetPull();
        return;
      }

      if (pullDistance >= threshold) {
        setIsRefreshing(true);
        try {
          await onRefresh();
        } catch (error) {
          console.error('Refresh failed:', error);
        } finally {
          setIsRefreshing(false);
        }
      }
      
      resetPull();
    };

    const resetPull = () => {
      setIsPulling(false);
      setPullDistance(0);
      setStartY(0);
      setCurrentY(0);
      setIsAtTop(false);
    };

    container.addEventListener('touchstart', handleTouchStart, { passive: false });
    container.addEventListener('touchmove', handleTouchMove, { passive: false });
    container.addEventListener('touchend', handleTouchEnd, { passive: false });

    return () => {
      container.removeEventListener('touchstart', handleTouchStart);
      container.removeEventListener('touchmove', handleTouchMove);
      container.removeEventListener('touchend', handleTouchEnd);
    };
  }, [isAtTop, isPulling, pullDistance, startY, threshold, resistance, onRefresh]);

  const pullProgress = Math.min(pullDistance / threshold, 1);
  const shouldTrigger = pullDistance >= threshold;

  return (
    <div ref={containerRef} className="relative overflow-auto">
      {/* プルトゥリフレッシュインジケーター */}
      <div
        ref={pullIndicatorRef}
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-200 ${
          isPulling || isRefreshing ? 'translate-y-0' : '-translate-y-full'
        }`}
        style={{
          transform: `translateY(${Math.max(0, pullDistance - 60)}px)`,
        }}
      >
        <div className="bg-white shadow-lg border-b">
          <div className="flex items-center justify-center py-4">
            <div className="flex items-center space-x-3">
              <div
                className={`transition-all duration-200 ${
                  isRefreshing ? 'animate-spin' : ''
                }`}
                style={{
                  transform: `rotate(${pullProgress * 180}deg)`,
                }}
              >
                <RefreshCw className="h-5 w-5 text-blue-600" />
              </div>
              
              <div className="text-sm font-medium text-gray-700">
                {isRefreshing ? (
                  '更新中...'
                ) : shouldTrigger ? (
                  '離すと更新されます'
                ) : (
                  '引っ張って更新'
                )}
              </div>
            </div>
          </div>
          
          {/* プログレスバー */}
          <div className="h-1 bg-gray-200">
            <div
              className="h-full bg-blue-600 transition-all duration-200"
              style={{ width: `${pullProgress * 100}%` }}
            />
          </div>
        </div>
      </div>

      {/* メインコンテンツ */}
      <div
        className="transition-transform duration-200"
        style={{
          transform: `translateY(${isPulling ? Math.min(pullDistance * 0.3, 20) : 0}px)`,
        }}
      >
        {children}
      </div>

      {/* プルトゥリフレッシュの視覚的フィードバック */}
      {isPulling && (
        <div
          className="fixed inset-0 pointer-events-none z-40"
          style={{
            background: `linear-gradient(to bottom, 
              rgba(59, 130, 246, ${pullProgress * 0.1}) 0%, 
              rgba(59, 130, 246, 0) 100%)`,
          }}
        />
      )}
    </div>
  );
}
