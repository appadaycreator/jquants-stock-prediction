"use client";

import { useState, useEffect, useCallback, useRef } from "react";

interface PerformanceMetrics {
  renderTime: number;
  memoryUsage: number;
  fps: number;
  isSlowDevice: boolean;
}

interface OptimizationConfig {
  enableVirtualization: boolean;
  enableLazyLoading: boolean;
  enableDebouncing: boolean;
  debounceDelay: number;
  maxConcurrentRequests: number;
}

export function usePerformanceOptimization() {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    renderTime: 0,
    memoryUsage: 0,
    fps: 60,
    isSlowDevice: false,
  });

  const [config, setConfig] = useState<OptimizationConfig>({
    enableVirtualization: true,
    enableLazyLoading: true,
    enableDebouncing: true,
    debounceDelay: 300,
    maxConcurrentRequests: 3,
  });

  const frameCountRef = useRef(0);
  const lastTimeRef = useRef(performance.now());
  const animationFrameRef = useRef<number>();

  // デバイス性能の検出
  useEffect(() => {
    const detectDevicePerformance = () => {
      const isSlowDevice = 
        navigator.hardwareConcurrency <= 2 ||
        (navigator as any).deviceMemory <= 4 ||
        window.innerWidth <= 768;

      setMetrics(prev => ({
        ...prev,
        isSlowDevice,
      }));

      // 設定の調整
      if (isSlowDevice) {
        setConfig(prev => ({
          ...prev,
          enableVirtualization: true,
          enableLazyLoading: true,
          debounceDelay: 500,
          maxConcurrentRequests: 2,
        }));
      }
    };

    detectDevicePerformance();
  }, []);

  // FPS監視
  const measureFPS = useCallback(() => {
    const now = performance.now();
    frameCountRef.current++;

    if (now - lastTimeRef.current >= 1000) {
      const fps = Math.round((frameCountRef.current * 1000) / (now - lastTimeRef.current));
      
      setMetrics(prev => ({
        ...prev,
        fps,
      }));

      frameCountRef.current = 0;
      lastTimeRef.current = now;
    }

    animationFrameRef.current = requestAnimationFrame(measureFPS);
  }, []);

  useEffect(() => {
    animationFrameRef.current = requestAnimationFrame(measureFPS);
    
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [measureFPS]);

  // メモリ使用量の監視
  useEffect(() => {
    const measureMemory = () => {
      if ("memory" in performance) {
        const memory = (performance as any).memory;
        const memoryUsage = memory.usedJSHeapSize / 1024 / 1024; // MB
        
        setMetrics(prev => ({
          ...prev,
          memoryUsage,
        }));
      }
    };

    const interval = setInterval(measureMemory, 5000);
    return () => clearInterval(interval);
  }, []);

  // レンダリング時間の測定
  const measureRenderTime = useCallback((callback: () => void) => {
    const start = performance.now();
    callback();
    const end = performance.now();
    
    setMetrics(prev => ({
      ...prev,
      renderTime: end - start,
    }));
  }, []);

  // デバウンス機能
  const debounce = useCallback(<T extends (...args: any[]) => void>(
    func: T,
    delay: number = config.debounceDelay,
  ): T => {
    let timeoutId: NodeJS.Timeout;
    
    return ((...args: Parameters<T>) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func(...args), delay);
    }) as T;
  }, [config.debounceDelay]);

  // スロットリング機能
  const throttle = useCallback(<T extends (...args: any[]) => void>(
    func: T,
    delay: number = 100,
  ): T => {
    let lastCall = 0;
    
    return ((...args: Parameters<T>) => {
      const now = Date.now();
      if (now - lastCall >= delay) {
        lastCall = now;
        func(...args);
      }
    }) as T;
  }, []);

  // 仮想化のためのアイテム計算
  const calculateVirtualItems = useCallback((
    totalItems: number,
    containerHeight: number,
    itemHeight: number,
    scrollTop: number,
  ) => {
    if (!config.enableVirtualization) {
      return {
        startIndex: 0,
        endIndex: totalItems - 1,
        visibleItems: totalItems,
      };
    }

    const visibleCount = Math.ceil(containerHeight / itemHeight);
    const startIndex = Math.floor(scrollTop / itemHeight);
    const endIndex = Math.min(startIndex + visibleCount, totalItems - 1);
    
    return {
      startIndex,
      endIndex,
      visibleItems: endIndex - startIndex + 1,
    };
  }, [config.enableVirtualization]);

  // 遅延読み込み
  const useLazyLoading = useCallback((
    threshold: number = 0.1,
  ) => {
    const [isVisible, setIsVisible] = useState(false);
    const [hasLoaded, setHasLoaded] = useState(false);
    const elementRef = useRef<HTMLElement>(null);

    useEffect(() => {
      if (!config.enableLazyLoading || hasLoaded) return;

      const observer = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting) {
            setIsVisible(true);
            setHasLoaded(true);
            observer.disconnect();
          }
        },
        { threshold },
      );

      if (elementRef.current) {
        observer.observe(elementRef.current);
      }

      return () => observer.disconnect();
    }, [config.enableLazyLoading, hasLoaded, threshold]);

    return { elementRef, isVisible, hasLoaded };
  }, [config.enableLazyLoading]);

  // 画像の遅延読み込み
  const useLazyImage = useCallback((
    src: string,
    placeholder?: string,
  ) => {
    const [imageSrc, setImageSrc] = useState(placeholder || "");
    const [isLoading, setIsLoading] = useState(true);
    const [hasError, setHasError] = useState(false);

    useEffect(() => {
      if (!config.enableLazyLoading) {
        setImageSrc(src);
        setIsLoading(false);
        return;
      }

      const img = new Image();
      img.onload = () => {
        setImageSrc(src);
        setIsLoading(false);
      };
      img.onerror = () => {
        setHasError(true);
        setIsLoading(false);
      };
      img.src = src;
    }, [src, config.enableLazyLoading]);

    return { imageSrc, isLoading, hasError };
  }, [config.enableLazyLoading]);

  // パフォーマンス警告
  const getPerformanceWarnings = useCallback(() => {
    const warnings: string[] = [];

    if (metrics.fps < 30) {
      warnings.push("低いFPSが検出されました");
    }

    if (metrics.memoryUsage > 100) {
      warnings.push("メモリ使用量が高いです");
    }

    if (metrics.renderTime > 16) {
      warnings.push("レンダリング時間が長いです");
    }

    return warnings;
  }, [metrics]);

  // 最適化の推奨設定
  const getOptimizationRecommendations = useCallback(() => {
    const recommendations: string[] = [];

    if (metrics.isSlowDevice) {
      recommendations.push("デバイス性能が低いため、仮想化を有効にしています");
    }

    if (metrics.fps < 45) {
      recommendations.push("アニメーションを減らすことを推奨します");
    }

    if (metrics.memoryUsage > 80) {
      recommendations.push("メモリ使用量を減らすため、不要なデータをクリアしてください");
    }

    return recommendations;
  }, [metrics]);

  return {
    metrics,
    config,
    setConfig,
    measureRenderTime,
    debounce,
    throttle,
    calculateVirtualItems,
    useLazyLoading,
    useLazyImage,
    getPerformanceWarnings,
    getOptimizationRecommendations,
  };
}
