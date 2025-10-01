"use client";

class InfiniteLoopDetector {
  private renderCounts = new Map<string, number>();
  private lastRenderTimes = new Map<string, number>();
  private blockedComponents = new Set<string>();
  private readonly MAX_RENDERS = 10;
  private readonly TIME_THRESHOLD = 100; // ms
  private readonly BLOCK_DURATION = 5000; // ms

  detectInfiniteLoop(componentId: string): boolean {
    const now = Date.now();
    const lastTime = this.lastRenderTimes.get(componentId) || 0;
    const timeSinceLastRender = now - lastTime;
    
    // 短時間で大量のレンダリングが発生した場合
    if (timeSinceLastRender < this.TIME_THRESHOLD) {
      const currentCount = this.renderCounts.get(componentId) || 0;
      const newCount = currentCount + 1;
      this.renderCounts.set(componentId, newCount);
      
      if (newCount > this.MAX_RENDERS) {
        console.warn(`Infinite loop detected in component: ${componentId}`);
        this.blockComponent(componentId);
        return true;
      }
    } else {
      // 正常な間隔の場合はカウントをリセット
      this.renderCounts.set(componentId, 1);
    }
    
    this.lastRenderTimes.set(componentId, now);
    return false;
  }

  private blockComponent(componentId: string) {
    this.blockedComponents.add(componentId);
    
    // 一定時間後にブロックを解除
    setTimeout(() => {
      this.blockedComponents.delete(componentId);
      this.renderCounts.delete(componentId);
      console.log(`Infinite loop protection reset for component: ${componentId}`);
    }, this.BLOCK_DURATION);
  }

  isBlocked(componentId: string): boolean {
    return this.blockedComponents.has(componentId);
  }

  reset() {
    this.renderCounts.clear();
    this.lastRenderTimes.clear();
    this.blockedComponents.clear();
  }
}

export const infiniteLoopDetector = new InfiniteLoopDetector();

// グローバルな無限ループ検出
if (typeof window !== 'undefined') {
  let globalRenderCount = 0;
  let lastGlobalRenderTime = Date.now();
  let isReloading = false;
  
  const originalConsoleError = console.error;
  console.error = (...args) => {
    const message = args.join(' ');
    if (message.includes('Maximum update depth exceeded') && !isReloading) {
      console.warn('Global infinite loop detected, forcing page reload');
      isReloading = true;
      // 即座にリロード
      window.location.reload();
    }
    originalConsoleError.apply(console, args);
  };
  
  // レンダリング頻度を監視
  const observer = new MutationObserver(() => {
    const now = Date.now();
    const timeSinceLastRender = now - lastGlobalRenderTime;
    
    if (timeSinceLastRender < 30) { // 30ms以内の連続レンダリング
      globalRenderCount++;
      if (globalRenderCount > 25 && !isReloading) {
        console.warn('Global infinite loop detected, forcing page reload');
        isReloading = true;
        window.location.reload();
      }
    } else {
      globalRenderCount = 0;
    }
    
    lastGlobalRenderTime = now;
  });
  
  // DOMが準備できたら監視開始
  if (document.body) {
    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true
    });
  } else {
    document.addEventListener('DOMContentLoaded', () => {
      observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true
      });
    });
  }
}
