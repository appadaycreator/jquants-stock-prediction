/**
 * モバイル最適化フック
 * モバイル環境での最適化機能を提供
 */

import { useState, useEffect, useCallback } from "react";
import { mobileOptimizer } from "../lib/mobile-optimizer";

interface UseMobileOptions {
  enableGestures?: boolean;
  enablePWA?: boolean;
  enableOffline?: boolean;
  onGesture?: (type: string, direction?: string) => void;
  onInstall?: () => void;
  onOffline?: () => void;
  onOnline?: () => void;
}

export function useMobile(options: UseMobileOptions = {}) {
  const [isMobile, setIsMobile] = useState(false);
  const [isOnline, setIsOnline] = useState(true);
  const [isInstalled, setIsInstalled] = useState(false);
  const [gestures, setGestures] = useState<string[]>([]);

  const {
    enableGestures = true,
    enablePWA = true,
    enableOffline = true,
    onGesture,
    onInstall,
    onOffline,
    onOnline,
  } = options;

  // モバイル環境の検出
  useEffect(() => {
    const checkMobile = () => {
      const userAgent = navigator.userAgent;
      const isMobileDevice = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
      const isTouchDevice = "ontouchstart" in window;
      const isSmallScreen = window.innerWidth < 768;
      
      setIsMobile(isMobileDevice || (isTouchDevice && isSmallScreen));
    };

    checkMobile();
    window.addEventListener("resize", checkMobile);
    
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  // オンライン状態の監視
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      onOnline?.();
    };

    const handleOffline = () => {
      setIsOnline(false);
      onOffline?.();
    };

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, [onOnline, onOffline]);

  // PWAインストール状態の監視
  useEffect(() => {
    const checkInstallation = () => {
      const isStandalone = window.matchMedia("(display-mode: standalone)").matches;
      const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
      const isInStandaloneMode = ("standalone" in window.navigator) && (window.navigator as any).standalone;
      
      setIsInstalled(isStandalone || (isIOS && isInStandaloneMode));
    };

    checkInstallation();
    
    // インストール完了の監視
    window.addEventListener("appinstalled", () => {
      setIsInstalled(true);
      onInstall?.();
    });
  }, [onInstall]);

  // ジェスチャーの登録
  useEffect(() => {
    if (!enableGestures || !isMobile) return;

    const gestureTypes = ["swipe", "tap", "longpress", "pinch"];
    setGestures(gestureTypes);

    // ジェスチャーの登録
    gestureTypes.forEach(type => {
      if (type === "swipe") {
        ["left", "right", "up", "down"].forEach(direction => {
          mobileOptimizer.registerGesture({
            type: "swipe",
            direction: direction as any,
            threshold: 50,
            callback: () => onGesture?.(type, direction),
          });
        });
      } else {
        mobileOptimizer.registerGesture({
          type: type as any,
          threshold: 50,
          callback: () => onGesture?.(type),
        });
      }
    });

    return () => {
      // ジェスチャーの削除
      gestureTypes.forEach(type => {
        if (type === "swipe") {
          ["left", "right", "up", "down"].forEach(direction => {
            mobileOptimizer.removeGesture(type, direction);
          });
        } else {
          mobileOptimizer.removeGesture(type);
        }
      });
    };
  }, [enableGestures, isMobile, onGesture]);

  // スワイプナビゲーション
  const enableSwipeNavigation = useCallback(() => {
    if (!isMobile) return;

    // 左スワイプで前のページ
    mobileOptimizer.registerGesture({
      type: "swipe",
      direction: "left",
      threshold: 50,
      callback: () => {
        if (window.history.length > 1) {
          window.history.back();
        }
      },
    });

    // 右スワイプで次のページ
    mobileOptimizer.registerGesture({
      type: "swipe",
      direction: "right",
      threshold: 50,
      callback: () => {
        if (window.history.length > 1) {
          window.history.forward();
        }
      },
    });
  }, [isMobile]);

  // ピンチズーム
  const enablePinchZoom = useCallback(() => {
    if (!isMobile) return;

    document.addEventListener("mobile-zoom", (e: any) => {
      const { zoomLevel } = e.detail;
      
      // ズームレベルの調整
      if (zoomLevel > 1.5) {
        document.body.style.transform = `scale(${Math.min(zoomLevel, 2)})`;
      } else {
        document.body.style.transform = "scale(1)";
      }
    });
  }, [isMobile]);

  // タッチフィードバック
  const enableTouchFeedback = useCallback(() => {
    if (!isMobile) return;

    // タッチ時の視覚的フィードバック
    document.addEventListener("touchstart", (e) => {
      const target = e.target as HTMLElement;
      if (target.tagName === "BUTTON" || target.tagName === "A") {
        target.style.transform = "scale(0.95)";
        target.style.transition = "transform 0.1s";
      }
    });

    document.addEventListener("touchend", (e) => {
      const target = e.target as HTMLElement;
      if (target.tagName === "BUTTON" || target.tagName === "A") {
        target.style.transform = "scale(1)";
      }
    });
  }, [isMobile]);

  // モバイル最適化の有効化
  const enableMobileOptimization = useCallback(() => {
    if (!isMobile) return;

    enableSwipeNavigation();
    enablePinchZoom();
    enableTouchFeedback();
  }, [isMobile, enableSwipeNavigation, enablePinchZoom, enableTouchFeedback]);

  // 自動最適化の実行
  useEffect(() => {
    if (isMobile) {
      enableMobileOptimization();
    }
  }, [isMobile, enableMobileOptimization]);

  return {
    isMobile,
    isOnline,
    isInstalled,
    gestures,
    enableMobileOptimization,
    enableSwipeNavigation,
    enablePinchZoom,
    enableTouchFeedback,
  };
}
