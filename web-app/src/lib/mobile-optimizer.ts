/**
 * モバイル最適化システム
 * スマートフォンでの使いやすさを向上
 */

interface MobileConfig {
  enableTouchGestures: boolean;
  enableSwipeNavigation: boolean;
  enableHapticFeedback: boolean;
  enableOfflineMode: boolean;
  enablePWA: boolean;
  touchSensitivity: 'low' | 'medium' | 'high';
}

interface TouchGesture {
  type: 'swipe' | 'pinch' | 'tap' | 'longpress';
  direction?: 'left' | 'right' | 'up' | 'down';
  threshold: number;
  callback: () => void;
}

class MobileOptimizer {
  private config: MobileConfig;
  private gestures: TouchGesture[] = [];
  private touchStart: { x: number; y: number; time: number } | null = null;
  private isEnabled = false;

  constructor(config: Partial<MobileConfig> = {}) {
    this.config = {
      enableTouchGestures: true,
      enableSwipeNavigation: true,
      enableHapticFeedback: true,
      enableOfflineMode: true,
      enablePWA: true,
      touchSensitivity: 'medium',
      ...config
    };

    this.initializeTouchHandlers();
    this.initializePWA();
  }

  /**
   * タッチハンドラーの初期化
   */
  private initializeTouchHandlers(): void {
    if (typeof window === 'undefined') return;

    // タッチ開始
    document.addEventListener('touchstart', (e) => {
      const touch = e.touches[0];
      this.touchStart = {
        x: touch.clientX,
        y: touch.clientY,
        time: Date.now()
      };
    }, { passive: true });

    // タッチ終了
    document.addEventListener('touchend', (e) => {
      if (!this.touchStart) return;

      const touch = e.changedTouches[0];
      const deltaX = touch.clientX - this.touchStart.x;
      const deltaY = touch.clientY - this.touchStart.y;
      const deltaTime = Date.now() - this.touchStart.time;

      // ジェスチャーの判定
      this.detectGesture(deltaX, deltaY, deltaTime);
      
      this.touchStart = null;
    }, { passive: true });

    // ピンチズーム
    document.addEventListener('touchmove', (e) => {
      if (e.touches.length === 2) {
        e.preventDefault();
        this.handlePinch(e);
      }
    }, { passive: false });
  }

  /**
   * ジェスチャーの検出
   */
  private detectGesture(deltaX: number, deltaY: number, deltaTime: number): void {
    const threshold = this.getTouchThreshold();
    const isSwipe = Math.abs(deltaX) > threshold || Math.abs(deltaY) > threshold;
    const isQuick = deltaTime < 300;

    if (isSwipe && isQuick) {
      const direction = this.getSwipeDirection(deltaX, deltaY);
      this.executeGesture('swipe', direction);
    } else if (!isSwipe && isQuick) {
      this.executeGesture('tap');
    } else if (!isSwipe && !isQuick) {
      this.executeGesture('longpress');
    }
  }

  /**
   * スワイプ方向の判定
   */
  private getSwipeDirection(deltaX: number, deltaY: number): 'left' | 'right' | 'up' | 'down' {
    if (Math.abs(deltaX) > Math.abs(deltaY)) {
      return deltaX > 0 ? 'right' : 'left';
    } else {
      return deltaY > 0 ? 'down' : 'up';
    }
  }

  /**
   * ジェスチャーの実行
   */
  private executeGesture(type: string, direction?: string): void {
    const gesture = this.gestures.find(g => 
      g.type === type && 
      (direction ? g.direction === direction : !g.direction)
    );

    if (gesture) {
      gesture.callback();
      this.triggerHapticFeedback();
    }
  }

  /**
   * ピンチズームの処理
   */
  private handlePinch(e: TouchEvent): void {
    if (e.touches.length !== 2) return;

    const touch1 = e.touches[0];
    const touch2 = e.touches[1];
    const distance = Math.sqrt(
      Math.pow(touch2.clientX - touch1.clientX, 2) + 
      Math.pow(touch2.clientY - touch1.clientY, 2)
    );

    // ズームレベルの計算
    const zoomLevel = distance / 100; // 基準距離を100pxとする
    
    // ズームイベントの発生
    const zoomEvent = new CustomEvent('mobile-zoom', {
      detail: { zoomLevel, distance }
    });
    document.dispatchEvent(zoomEvent);
  }

  /**
   * タッチ感度の取得
   */
  private getTouchThreshold(): number {
    switch (this.config.touchSensitivity) {
      case 'low': return 100;
      case 'medium': return 50;
      case 'high': return 25;
      default: return 50;
    }
  }

  /**
   * ハプティックフィードバックの実行
   */
  private triggerHapticFeedback(): void {
    if (!this.config.enableHapticFeedback) return;

    // バイブレーションAPIの使用
    if ('vibrate' in navigator) {
      navigator.vibrate(50); // 50ms振動
    }
  }

  /**
   * ジェスチャーの登録
   */
  registerGesture(gesture: TouchGesture): void {
    this.gestures.push(gesture);
  }

  /**
   * ジェスチャーの削除
   */
  removeGesture(type: string, direction?: string): void {
    this.gestures = this.gestures.filter(g => 
      !(g.type === type && (direction ? g.direction === direction : !g.direction))
    );
  }

  /**
   * PWAの初期化
   */
  private initializePWA(): void {
    if (!this.config.enablePWA || typeof window === 'undefined') return;

    // Service Worker の登録
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js').then((registration) => {
        console.log('Service Worker 登録成功:', registration);
      }).catch((error) => {
        console.error('Service Worker 登録エラー:', error);
      });
    }

    // インストールプロンプトの処理
    let deferredPrompt: any;
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      deferredPrompt = e;
      
      // インストールボタンの表示
      this.showInstallPrompt();
    });

    // アプリのインストール完了
    window.addEventListener('appinstalled', () => {
      console.log('PWA インストール完了');
      this.hideInstallPrompt();
    });
  }

  /**
   * インストールプロンプトの表示
   */
  private showInstallPrompt(): void {
    const prompt = document.createElement('div');
    prompt.id = 'install-prompt';
    prompt.className = 'fixed bottom-4 left-4 right-4 bg-blue-600 text-white p-4 rounded-lg shadow-lg z-50';
    prompt.innerHTML = `
      <div class="flex items-center justify-between">
        <div>
          <h3 class="font-semibold">アプリをインストール</h3>
          <p class="text-sm">ホーム画面に追加してより快適にご利用ください</p>
        </div>
        <button id="install-button" class="bg-white text-blue-600 px-4 py-2 rounded-lg font-semibold">
          インストール
        </button>
      </div>
    `;

    document.body.appendChild(prompt);

    // インストールボタンのクリック処理
    const installButton = document.getElementById('install-button');
    if (installButton) {
      installButton.addEventListener('click', () => {
        this.triggerInstall();
      });
    }
  }

  /**
   * インストールの実行
   */
  private triggerInstall(): void {
    if (typeof window !== 'undefined' && (window as any).deferredPrompt) {
      (window as any).deferredPrompt.prompt();
      (window as any).deferredPrompt.userChoice.then((choiceResult: any) => {
        if (choiceResult.outcome === 'accepted') {
          console.log('ユーザーがインストールを承認');
        } else {
          console.log('ユーザーがインストールを拒否');
        }
        (window as any).deferredPrompt = null;
      });
    }
  }

  /**
   * インストールプロンプトの非表示
   */
  private hideInstallPrompt(): void {
    const prompt = document.getElementById('install-prompt');
    if (prompt) {
      prompt.remove();
    }
  }

  /**
   * オフラインモードの初期化
   */
  initializeOfflineMode(): void {
    if (!this.config.enableOfflineMode || typeof window === 'undefined') return;

    // オフライン状態の監視
    window.addEventListener('online', () => {
      console.log('オンライン状態に復帰');
      this.showOnlineStatus();
    });

    window.addEventListener('offline', () => {
      console.log('オフライン状態');
      this.showOfflineStatus();
    });
  }

  /**
   * オンライン状態の表示
   */
  private showOnlineStatus(): void {
    const status = document.createElement('div');
    status.id = 'online-status';
    status.className = 'fixed top-4 right-4 bg-green-600 text-white px-4 py-2 rounded-lg shadow-lg z-50';
    status.textContent = 'オンラインに復帰しました';
    document.body.appendChild(status);

    setTimeout(() => {
      status.remove();
    }, 3000);
  }

  /**
   * オフライン状態の表示
   */
  private showOfflineStatus(): void {
    const status = document.createElement('div');
    status.id = 'offline-status';
    status.className = 'fixed top-4 right-4 bg-red-600 text-white px-4 py-2 rounded-lg shadow-lg z-50';
    status.textContent = 'オフライン状態です';
    document.body.appendChild(status);
  }

  /**
   * モバイル最適化の有効化
   */
  enable(): void {
    this.isEnabled = true;
    this.initializeOfflineMode();
  }

  /**
   * モバイル最適化の無効化
   */
  disable(): void {
    this.isEnabled = false;
    this.gestures = [];
  }

  /**
   * 設定の更新
   */
  updateConfig(newConfig: Partial<MobileConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  /**
   * 現在の設定の取得
   */
  getConfig(): MobileConfig {
    return { ...this.config };
  }
}

// シングルトンインスタンス
export const mobileOptimizer = new MobileOptimizer();

// 自動有効化
if (typeof window !== 'undefined') {
  mobileOptimizer.enable();
}

export default MobileOptimizer;
