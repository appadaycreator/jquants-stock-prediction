"use client";

import { useEffect, useState, useCallback, useMemo } from "react";

interface MobilePerformanceOptimizerProps {
  children: React.ReactNode;
  enableVirtualization?: boolean;
  enableLazyLoading?: boolean;
  enableImageOptimization?: boolean;
  enableDataThrottling?: boolean;
}

export default function MobilePerformanceOptimizer({
  children,
  enableVirtualization = true,
  enableLazyLoading = true,
  enableImageOptimization = true,
  enableDataThrottling = true,
}: MobilePerformanceOptimizerProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [isLowEndDevice, setIsLowEndDevice] = useState(false);
  const [connectionType, setConnectionType] = useState<'slow' | 'fast' | 'unknown'>('unknown');

  // デバイス性能の判定
  useEffect(() => {
    const checkDevicePerformance = () => {
      // メモリ情報の取得
      const memory = (navigator as any).deviceMemory;
      const cores = navigator.hardwareConcurrency;
      
      // 低性能デバイスの判定
      const isLowEnd = 
        memory && memory <= 2 || // 2GB以下
        cores && cores <= 2 ||   // 2コア以下
        /Android.*Chrome\/[0-5]/.test(navigator.userAgent) || // 古いAndroid
        /iPhone.*OS [0-9]/.test(navigator.userAgent); // 古いiOS

      setIsLowEndDevice(isLowEnd);
    };

    checkDevicePerformance();
  }, []);

  // ネットワーク接続の判定
  useEffect(() => {
    const checkConnection = () => {
      if ('connection' in navigator) {
        const connection = (navigator as any).connection;
        const effectiveType = connection.effectiveType;
        
        if (effectiveType === 'slow-2g' || effectiveType === '2g') {
          setConnectionType('slow');
        } else if (effectiveType === '4g') {
          setConnectionType('fast');
        } else {
          setConnectionType('unknown');
        }
      }
    };

    checkConnection();
    
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      connection.addEventListener('change', checkConnection);
      return () => connection.removeEventListener('change', checkConnection);
    }
  }, []);

  // 可視性の監視
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsVisible(entry.isIntersecting);
      },
      { threshold: 0.1 }
    );

    const element = document.getElementById('mobile-performance-container');
    if (element) {
      observer.observe(element);
    }

    return () => {
      if (element) {
        observer.unobserve(element);
      }
    };
  }, []);

  // データスロットリング
  const throttledDataUpdate = useCallback((data: any[], delay: number = 100) => {
    if (!enableDataThrottling || connectionType === 'fast') {
      return data;
    }

    // 低速接続ではデータを制限
    const maxItems = connectionType === 'slow' ? 50 : 100;
    return data.slice(0, maxItems);
  }, [enableDataThrottling, connectionType]);

  // 画像最適化
  const optimizeImage = useCallback((src: string, width?: number, height?: number) => {
    if (!enableImageOptimization) return src;

    // WebP対応の確認
    const supportsWebP = document.createElement('canvas')
      .toDataURL('image/webp')
      .indexOf('data:image/webp') === 0;

    if (supportsWebP && src.includes('.')) {
      const baseSrc = src.replace(/\.[^/.]+$/, '');
      return `${baseSrc}.webp`;
    }

    // サイズ最適化
    if (width && height) {
      const params = new URLSearchParams();
      params.set('w', width.toString());
      params.set('h', height.toString());
      params.set('q', isLowEndDevice ? '60' : '80');
      
      return `${src}?${params.toString()}`;
    }

    return src;
  }, [enableImageOptimization, isLowEndDevice]);

  // 仮想化の実装
  const virtualizeList = useCallback((items: any[], itemHeight: number = 50) => {
    if (!enableVirtualization || !isLowEndDevice) {
      return items;
    }

    // 簡易的な仮想化（実際の実装ではreact-window等を使用）
    const containerHeight = window.innerHeight;
    const visibleItems = Math.ceil(containerHeight / itemHeight) + 2;
    
    return items.slice(0, visibleItems);
  }, [enableVirtualization, isLowEndDevice]);

  // レイジーローディング
  const lazyLoadComponent = useCallback((Component: React.ComponentType<any>, props: any) => {
    if (!enableLazyLoading || !isVisible) {
      return null;
    }

    return <Component {...props} />;
  }, [enableLazyLoading, isVisible]);

  // パフォーマンス設定の最適化
  const performanceSettings = useMemo(() => ({
    // アニメーションの制限
    reducedMotion: isLowEndDevice || connectionType === 'slow',
    
    // データ更新頻度の制限
    updateInterval: connectionType === 'slow' ? 5000 : 1000,
    
    // チャートの詳細度制限
    chartDetail: isLowEndDevice ? 'low' : 'high',
    
    // キャッシュ戦略
    cacheStrategy: connectionType === 'slow' ? 'aggressive' : 'normal',
    
    // プリロードの制限
    preloadLimit: connectionType === 'slow' ? 2 : 5,
  }), [isLowEndDevice, connectionType]);

  // メモリ使用量の監視
  useEffect(() => {
    if (!isLowEndDevice) return;

    const monitorMemory = () => {
      if ('memory' in performance) {
        const memory = (performance as any).memory;
        const usedMB = memory.usedJSHeapSize / 1024 / 1024;
        const limitMB = memory.jsHeapSizeLimit / 1024 / 1024;
        
        // メモリ使用率が80%を超えた場合の警告
        if (usedMB / limitMB > 0.8) {
          console.warn('High memory usage detected:', {
            used: `${usedMB.toFixed(2)}MB`,
            limit: `${limitMB.toFixed(2)}MB`,
            percentage: `${((usedMB / limitMB) * 100).toFixed(1)}%`
          });
        }
      }
    };

    const interval = setInterval(monitorMemory, 10000);
    return () => clearInterval(interval);
  }, [isLowEndDevice]);

  // ネットワーク状態の監視
  useEffect(() => {
    const handleOnline = () => {
      console.log('Network: Online');
    };

    const handleOffline = () => {
      console.log('Network: Offline');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return (
    <div 
      id="mobile-performance-container"
      className="mobile-performance-optimized"
      data-performance-settings={JSON.stringify(performanceSettings)}
    >
      {children}
    </div>
  );
}

// パフォーマンス最適化フック
export function useMobilePerformance() {
  const [isLowEndDevice, setIsLowEndDevice] = useState(false);
  const [connectionType, setConnectionType] = useState<'slow' | 'fast' | 'unknown'>('unknown');

  useEffect(() => {
    // デバイス性能の判定
    const memory = (navigator as any).deviceMemory;
    const cores = navigator.hardwareConcurrency;
    
    const isLowEnd = 
      memory && memory <= 2 ||
      cores && cores <= 2 ||
      /Android.*Chrome\/[0-5]/.test(navigator.userAgent);

    setIsLowEndDevice(isLowEnd);

    // ネットワーク接続の判定
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      const effectiveType = connection.effectiveType;
      
      if (effectiveType === 'slow-2g' || effectiveType === '2g') {
        setConnectionType('slow');
      } else if (effectiveType === '4g') {
        setConnectionType('fast');
      }
    }
  }, []);

  return {
    isLowEndDevice,
    connectionType,
    shouldReduceAnimations: isLowEndDevice || connectionType === 'slow',
    shouldLimitData: connectionType === 'slow',
    updateInterval: connectionType === 'slow' ? 5000 : 1000,
  };
}
