/**
 * 自動復旧システム
 * アプリケーションの自動復旧、ヘルスチェック、状態復元
 */

import { getErrorInfo, logError, type ErrorCategory } from './error-handler';

export interface RecoveryStrategy {
  name: string;
  condition: (error: Error) => boolean;
  action: () => Promise<boolean>;
  priority: number;
  maxAttempts: number;
}

export interface RecoveryState {
  isRecovering: boolean;
  lastRecoveryAttempt: number;
  recoveryCount: number;
  successfulRecoveries: number;
  failedRecoveries: number;
}

class AutoRecoverySystem {
  private strategies: RecoveryStrategy[] = [];
  private state: RecoveryState = {
    isRecovering: false,
    lastRecoveryAttempt: 0,
    recoveryCount: 0,
    successfulRecoveries: 0,
    failedRecoveries: 0
  };

  constructor() {
    this.initializeDefaultStrategies();
    this.setupGlobalErrorHandling();
  }

  private initializeDefaultStrategies() {
    // RSC Payload エラーの復旧戦略
    this.addStrategy({
      name: 'rsc-payload-recovery',
      condition: (error) => {
        const message = error.message.toLowerCase();
        return message.includes('rsc payload') || 
               message.includes('server component') ||
               message.includes('connection closed');
      },
      action: async () => {
        console.log('Executing RSC payload recovery...');
        
        // キャッシュクリア
        await this.clearCaches();
        
        // ページリロード
        window.location.reload();
        return true;
      },
      priority: 1,
      maxAttempts: 3
    });

    // ネットワークエラーの復旧戦略
    this.addStrategy({
      name: 'network-recovery',
      condition: (error) => {
        const message = error.message.toLowerCase();
        return message.includes('network') || 
               message.includes('fetch') || 
               message.includes('connection') ||
               message.includes('timeout');
      },
      action: async () => {
        console.log('Executing network recovery...');
        
        // ネットワーク接続の確認
        if (!navigator.onLine) {
          await this.waitForOnline();
        }
        
        // キャッシュクリア
        await this.clearCaches();
        
        return true;
      },
      priority: 2,
      maxAttempts: 5
    });

    // データエラーの復旧戦略
    this.addStrategy({
      name: 'data-recovery',
      condition: (error) => {
        const message = error.message.toLowerCase();
        return message.includes('data') || 
               message.includes('json') || 
               message.includes('parse');
      },
      action: async () => {
        console.log('Executing data recovery...');
        
        // ローカルストレージのクリア
        await this.clearLocalStorage();
        
        // デフォルトデータの復元
        await this.restoreDefaultData();
        
        return true;
      },
      priority: 3,
      maxAttempts: 2
    });

    // コンポーネントエラーの復旧戦略
    this.addStrategy({
      name: 'component-recovery',
      condition: (error) => {
        const stack = error.stack?.toLowerCase() || '';
        return stack.includes('react') || 
               stack.includes('component') ||
               error.message.includes('render');
      },
      action: async () => {
        console.log('Executing component recovery...');
        
        // コンポーネント状態のリセット
        await this.resetComponentState();
        
        // ページリロード
        window.location.reload();
        return true;
      },
      priority: 4,
      maxAttempts: 2
    });
  }

  private setupGlobalErrorHandling() {
    // 未処理のエラーをキャッチ
    window.addEventListener('error', (event) => {
      this.handleError(event.error);
    });

    // 未処理のPromise拒否をキャッチ
    window.addEventListener('unhandledrejection', (event) => {
      this.handleError(event.reason);
    });
  }

  public addStrategy(strategy: RecoveryStrategy) {
    this.strategies.push(strategy);
    this.strategies.sort((a, b) => a.priority - b.priority);
  }

  public async handleError(error: Error): Promise<boolean> {
    if (this.state.isRecovering) {
      console.log('Recovery already in progress, skipping...');
      return false;
    }

    const errorInfo = getErrorInfo(error);
    console.log('Handling error:', errorInfo);

    // エラーログを記録
    logError(error);

    // 復旧戦略を実行
    for (const strategy of this.strategies) {
      if (strategy.condition(error)) {
        const success = await this.executeStrategy(strategy, error);
        if (success) {
          this.state.successfulRecoveries++;
          return true;
        }
      }
    }

    this.state.failedRecoveries++;
    return false;
  }

  private async executeStrategy(strategy: RecoveryStrategy, error: Error): Promise<boolean> {
    this.state.isRecovering = true;
    this.state.lastRecoveryAttempt = Date.now();
    this.state.recoveryCount++;

    try {
      console.log(`Executing recovery strategy: ${strategy.name}`);
      const success = await strategy.action();
      
      if (success) {
        console.log(`Recovery strategy ${strategy.name} succeeded`);
        this.state.successfulRecoveries++;
      } else {
        console.log(`Recovery strategy ${strategy.name} failed`);
        this.state.failedRecoveries++;
      }
      
      return success;
    } catch (recoveryError) {
      console.error(`Recovery strategy ${strategy.name} threw error:`, recoveryError);
      this.state.failedRecoveries++;
      return false;
    } finally {
      this.state.isRecovering = false;
    }
  }

  private async clearCaches(): Promise<void> {
    if ('caches' in window) {
      const cacheNames = await caches.keys();
      await Promise.all(
        cacheNames.map(name => caches.delete(name))
      );
    }
  }

  private async clearLocalStorage(): Promise<void> {
    try {
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.startsWith('app_cache:') || 
            key.startsWith('next:') || 
            key.startsWith('error_')) {
          localStorage.removeItem(key);
        }
      });
    } catch (e) {
      console.warn('Failed to clear localStorage:', e);
    }
  }

  private async restoreDefaultData(): Promise<void> {
    try {
      // デフォルトの設定を復元
      const defaultSettings = {
        theme: 'light',
        language: 'ja',
        notifications: true,
        autoRefresh: true
      };
      
      localStorage.setItem('app_settings', JSON.stringify(defaultSettings));
    } catch (e) {
      console.warn('Failed to restore default data:', e);
    }
  }

  private async resetComponentState(): Promise<void> {
    try {
      // コンポーネント状態をリセット
      const stateKeys = Object.keys(localStorage).filter(key => 
        key.startsWith('component_') || key.startsWith('react_')
      );
      
      stateKeys.forEach(key => {
        localStorage.removeItem(key);
      });
    } catch (e) {
      console.warn('Failed to reset component state:', e);
    }
  }

  private async waitForOnline(): Promise<void> {
    return new Promise((resolve) => {
      if (navigator.onLine) {
        resolve();
        return;
      }
      
      const handleOnline = () => {
        window.removeEventListener('online', handleOnline);
        resolve();
      };
      
      window.addEventListener('online', handleOnline);
    });
  }

  public getState(): RecoveryState {
    return { ...this.state };
  }

  public getRecoveryStats() {
    return {
      totalRecoveries: this.state.recoveryCount,
      successfulRecoveries: this.state.successfulRecoveries,
      failedRecoveries: this.state.failedRecoveries,
      successRate: this.state.recoveryCount > 0 
        ? (this.state.successfulRecoveries / this.state.recoveryCount) * 100 
        : 0,
      lastRecoveryAttempt: this.state.lastRecoveryAttempt,
      isRecovering: this.state.isRecovering
    };
  }

  public resetStats() {
    this.state = {
      isRecovering: false,
      lastRecoveryAttempt: 0,
      recoveryCount: 0,
      successfulRecoveries: 0,
      failedRecoveries: 0
    };
  }
}

// シングルトンインスタンス
export const autoRecoverySystem = new AutoRecoverySystem();

// ヘルスチェック機能
export async function performHealthCheck(): Promise<{
  isHealthy: boolean;
  issues: string[];
  recommendations: string[];
}> {
  const issues: string[] = [];
  const recommendations: string[] = [];

  // ネットワーク接続の確認
  if (!navigator.onLine) {
    issues.push('ネットワーク接続がありません');
    recommendations.push('ネットワーク接続を確認してください');
  }

  // ローカルストレージの確認
  try {
    localStorage.setItem('health_check', 'test');
    localStorage.removeItem('health_check');
  } catch (e) {
    issues.push('ローカルストレージが利用できません');
    recommendations.push('ブラウザの設定を確認してください');
  }

  // キャッシュの確認
  if ('caches' in window) {
    try {
      const cacheNames = await caches.keys();
      if (cacheNames.length > 10) {
        issues.push('キャッシュが多すぎます');
        recommendations.push('キャッシュをクリアしてください');
      }
    } catch (e) {
      issues.push('キャッシュAPIが利用できません');
    }
  }

  // メモリ使用量の確認
  if ('memory' in performance) {
    const memory = (performance as any).memory;
    const usedMB = memory.usedJSHeapSize / 1024 / 1024;
    if (usedMB > 100) {
      issues.push('メモリ使用量が高いです');
      recommendations.push('ページを再読み込みしてください');
    }
  }

  return {
    isHealthy: issues.length === 0,
    issues,
    recommendations
  };
}

// 自動復旧の開始
export function startAutoRecovery() {
  console.log('Auto-recovery system started');
  return autoRecoverySystem;
}

// 自動復旧の停止
export function stopAutoRecovery() {
  console.log('Auto-recovery system stopped');
  // 必要に応じてクリーンアップ処理を追加
}
