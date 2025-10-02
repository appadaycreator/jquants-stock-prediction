"use client";

import { useState, useEffect, useRef } from "react";
import { ChevronUp, ChevronDown } from "lucide-react";

interface MobileVerticalLayoutProps {
  children: React.ReactNode;
  enableScrollToTop?: boolean;
  enableScrollIndicator?: boolean;
  className?: string;
}

export default function MobileVerticalLayout({
  children,
  enableScrollToTop = true,
  enableScrollIndicator = true,
  className = "",
}: MobileVerticalLayoutProps) {
  const [showScrollToTop, setShowScrollToTop] = useState(false);
  const [scrollProgress, setScrollProgress] = useState(0);
  const [isScrolling, setIsScrolling] = useState(false);
  
  const containerRef = useRef<HTMLDivElement>(null);
  const scrollTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // スクロール位置の監視
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleScroll = () => {
      const scrollTop = container.scrollTop;
      const scrollHeight = container.scrollHeight;
      const clientHeight = container.clientHeight;
      
      // スクロール進捗の計算
      const progress = scrollTop / (scrollHeight - clientHeight);
      setScrollProgress(Math.min(progress, 1));
      
      // スクロールトップボタンの表示制御
      setShowScrollToTop(scrollTop > 200);
      
      // スクロール中の状態管理
      setIsScrolling(true);
      
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
      
      scrollTimeoutRef.current = setTimeout(() => {
        setIsScrolling(false);
      }, 150);
    };

    container.addEventListener("scroll", handleScroll, { passive: true });
    
    return () => {
      container.removeEventListener("scroll", handleScroll);
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
    };
  }, []);

  // スクロールトップ機能
  const scrollToTop = () => {
    if (containerRef.current) {
      containerRef.current.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    }
  };

  // スクロールインジケーターのクリック処理
  const handleScrollIndicatorClick = () => {
    if (containerRef.current) {
      const container = containerRef.current;
      const scrollHeight = container.scrollHeight;
      const clientHeight = container.clientHeight;
      const currentScroll = container.scrollTop;
      
      // 次のセクションへスクロール
      const nextScroll = currentScroll + clientHeight * 0.8;
      const maxScroll = scrollHeight - clientHeight;
      
      container.scrollTo({
        top: Math.min(nextScroll, maxScroll),
        behavior: "smooth",
      });
    }
  };

  return (
    <div className={`mobile-vertical-layout ${className}`}>
      {/* メインコンテンツ */}
      <div 
        ref={containerRef}
        className="mobile-content mobile-scroll-y mobile-scroll-smooth"
        style={{
          height: "100vh",
          overflowY: "auto",
          WebkitOverflowScrolling: "touch",
        }}
      >
        {children}
      </div>

      {/* スクロール進捗インジケーター */}
      {enableScrollIndicator && (
        <div className="fixed right-4 top-1/2 transform -translate-y-1/2 z-30">
          <div className="flex flex-col items-center space-y-2">
            {/* スクロール進捗バー */}
            <div className="w-1 h-32 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className="w-full bg-blue-600 transition-all duration-200"
                style={{ 
                  height: `${scrollProgress * 100}%`,
                  transform: "translateY(0)",
                }}
              />
            </div>
            
            {/* スクロールインジケーター */}
            <button
              onClick={handleScrollIndicatorClick}
              className="mobile-touch-target p-2 rounded-full bg-white shadow-lg border border-gray-200 hover:bg-gray-50 transition-colors"
              disabled={scrollProgress >= 0.95}
            >
              <ChevronDown className="h-4 w-4 text-gray-600" />
            </button>
          </div>
        </div>
      )}

      {/* スクロールトップボタン */}
      {enableScrollToTop && showScrollToTop && (
        <button
          onClick={scrollToTop}
          className="fixed bottom-20 right-4 mobile-touch-target p-3 rounded-full bg-blue-600 text-white shadow-lg hover:bg-blue-700 transition-all duration-200 z-30"
        >
          <ChevronUp className="h-5 w-5" />
        </button>
      )}

      {/* スクロール状態インジケーター */}
      {isScrolling && (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-40">
          <div className="bg-black/50 text-white px-3 py-1 rounded-full text-sm">
            スクロール中...
          </div>
        </div>
      )}
    </div>
  );
}
