"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { ChevronLeft, ChevronRight, Circle } from "lucide-react";

interface SwipeNavigationProps {
  children: React.ReactNode[];
  onPageChange?: (pageIndex: number) => void;
  enableSwipe?: boolean;
  enableDots?: boolean;
  enableArrows?: boolean;
  autoPlay?: boolean;
  autoPlayInterval?: number;
  className?: string;
}

export default function SwipeNavigation({
  children,
  onPageChange,
  enableSwipe = true,
  enableDots = true,
  enableArrows = true,
  autoPlay = false,
  autoPlayInterval = 5000,
  className = "",
}: SwipeNavigationProps) {
  const [currentPage, setCurrentPage] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);
  const [currentX, setCurrentX] = useState(0);
  const [translateX, setTranslateX] = useState(0);
  const [isTransitioning, setIsTransitioning] = useState(false);
  
  const containerRef = useRef<HTMLDivElement>(null);
  const autoPlayRef = useRef<NodeJS.Timeout | null>(null);

  // ページ変更の処理
  const changePage = useCallback((pageIndex: number) => {
    if (pageIndex < 0 || pageIndex >= children.length) return;
    
    setCurrentPage(pageIndex);
    setIsTransitioning(true);
    
    if (onPageChange) {
      onPageChange(pageIndex);
    }
    
    // トランジション完了後に状態をリセット
    setTimeout(() => {
      setIsTransitioning(false);
    }, 300);
  }, [children.length, onPageChange]);

  // 次のページへ
  const nextPage = useCallback(() => {
    const nextIndex = (currentPage + 1) % children.length;
    changePage(nextIndex);
  }, [currentPage, children.length, changePage]);

  // 前のページへ
  const prevPage = useCallback(() => {
    const prevIndex = currentPage === 0 ? children.length - 1 : currentPage - 1;
    changePage(prevIndex);
  }, [currentPage, children.length, changePage]);

  // 自動再生の制御
  useEffect(() => {
    if (autoPlay && children.length > 1) {
      autoPlayRef.current = setInterval(nextPage, autoPlayInterval);
    }
    
    return () => {
      if (autoPlayRef.current) {
        clearInterval(autoPlayRef.current);
      }
    };
  }, [autoPlay, autoPlayInterval, nextPage, children.length]);

  // ドラッグ開始
  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    if (!enableSwipe) return;
    
    setIsDragging(true);
    setStartX(e.touches[0].clientX);
    setCurrentX(e.touches[0].clientX);
    setTranslateX(0);
    
    // 自動再生を一時停止
    if (autoPlayRef.current) {
      clearInterval(autoPlayRef.current);
    }
  }, [enableSwipe]);

  // ドラッグ中
  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    if (!isDragging || !enableSwipe) return;
    
    e.preventDefault();
    
    const touchX = e.touches[0].clientX;
    const deltaX = touchX - startX;
    
    setCurrentX(touchX);
    setTranslateX(deltaX);
  }, [isDragging, enableSwipe, startX]);

  // ドラッグ終了
  const handleTouchEnd = useCallback(() => {
    if (!isDragging || !enableSwipe) return;
    
    setIsDragging(false);
    
    const deltaX = currentX - startX;
    const threshold = 50; // スワイプの閾値
    
    if (Math.abs(deltaX) > threshold) {
      if (deltaX > 0) {
        // 右にスワイプ：前のページ
        prevPage();
      } else {
        // 左にスワイプ：次のページ
        nextPage();
      }
    }
    
    setTranslateX(0);
    setStartX(0);
    setCurrentX(0);
    
    // 自動再生を再開
    if (autoPlay && children.length > 1) {
      autoPlayRef.current = setInterval(nextPage, autoPlayInterval);
    }
  }, [isDragging, enableSwipe, currentX, startX, prevPage, nextPage, autoPlay, autoPlayInterval, children.length]);

  // マウスイベントの処理（デスクトップ対応）
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (!enableSwipe) return;
    
    setIsDragging(true);
    setStartX(e.clientX);
    setCurrentX(e.clientX);
    setTranslateX(0);
    
    // 自動再生を一時停止
    if (autoPlayRef.current) {
      clearInterval(autoPlayRef.current);
    }
  }, [enableSwipe]);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isDragging || !enableSwipe) return;
    
    const mouseX = e.clientX;
    const deltaX = mouseX - startX;
    
    setCurrentX(mouseX);
    setTranslateX(deltaX);
  }, [isDragging, enableSwipe, startX]);

  const handleMouseUp = useCallback(() => {
    if (!isDragging || !enableSwipe) return;
    
    setIsDragging(false);
    
    const deltaX = currentX - startX;
    const threshold = 50;
    
    if (Math.abs(deltaX) > threshold) {
      if (deltaX > 0) {
        prevPage();
      } else {
        nextPage();
      }
    }
    
    setTranslateX(0);
    setStartX(0);
    setCurrentX(0);
    
    // 自動再生を再開
    if (autoPlay && children.length > 1) {
      autoPlayRef.current = setInterval(nextPage, autoPlayInterval);
    }
  }, [isDragging, enableSwipe, currentX, startX, prevPage, nextPage, autoPlay, autoPlayInterval, children.length]);

  // マウスイベントのリスナー登録
  useEffect(() => {
    if (isDragging) {
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("mouseup", handleMouseUp);
    }
    
    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isDragging, handleMouseMove, handleMouseUp]);

  return (
    <div className={`swipe-navigation ${className}`}>
      {/* メインコンテンツ */}
      <div 
        ref={containerRef}
        className="relative overflow-hidden"
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        onMouseDown={handleMouseDown}
      >
        <div 
          className="flex transition-transform duration-300 ease-out"
          style={{
            transform: `translateX(${-currentPage * 100 + (isDragging ? translateX : 0)}%)`,
            width: `${children.length * 100}%`
          }}
        >
          {children.map((child, index) => (
            <div
              key={index}
              className="w-full flex-shrink-0"
              style={{ width: `${100 / children.length}%` }}
            >
              {child}
            </div>
          ))}
        </div>
        
        {/* スワイプインジケーター */}
        {isDragging && (
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-10">
            <div className="bg-black/50 text-white px-3 py-1 rounded-full text-sm">
              {translateX > 0 ? "← 前へ" : "次へ →"}
            </div>
          </div>
        )}
      </div>

      {/* ナビゲーションコントロール */}
      <div className="flex items-center justify-between mt-4">
        {/* 前へボタン */}
        {enableArrows && (
          <button
            onClick={prevPage}
            className="mobile-touch-target p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
            disabled={children.length <= 1}
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
        )}

        {/* ドットインジケーター */}
        {enableDots && (
          <div className="flex items-center space-x-2">
            {children.map((_, index) => (
              <button
                key={index}
                onClick={() => changePage(index)}
                className={`mobile-touch-target p-1 rounded-full transition-colors ${
                  index === currentPage
                    ? "bg-blue-600 text-white"
                    : "bg-gray-300 hover:bg-gray-400"
                }`}
              >
                <Circle className="h-2 w-2" />
              </button>
            ))}
          </div>
        )}

        {/* 次へボタン */}
        {enableArrows && (
          <button
            onClick={nextPage}
            className="mobile-touch-target p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
            disabled={children.length <= 1}
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        )}
      </div>

      {/* ページ情報 */}
      <div className="text-center mt-2 text-sm text-gray-600">
        {currentPage + 1} / {children.length}
      </div>
    </div>
  );
}
