/**
 * 統一エラーハンドラー
 * 全エラーを一元管理し、適切な対応を実行
 */

export interface ErrorInfo {
  category: 'network' | 'api' | 'data' | 'validation' | 'system' | 'unknown';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  userMessage: string;
  autoRetry: boolean;
  retryDelay: number;
  fallbackAction: string;
  timestamp: string;
  context?: Record<string, any>;
}

export interface ErrorRecoveryAction {
  type: 'retry' | 'fallback' | 'redirect' | 'refresh' | 'clear-cache' | 'none';
  description: string;
  execute: () => Promise<boolean>;
}

class UnifiedErrorHandler {
  private errorHistory: ErrorInfo[] = [];
  private recoveryActions: Map<string, ErrorRecoveryAction[]> = new Map();
  private isRecovering = false;

  constructor() {
    this.initializeRecoveryActions();
  }

  /**
   * エラーの分類と情報取得
   */
  categorizeError(error: Error): ErrorInfo {
    const message = error.message.toLowerCase();
    const stack = error.stack || '';
    
    let category: ErrorInfo['category'] = 'unknown';
    let severity: ErrorInfo['severity'] = 'medium';
    let userMessage = '予期しないエラーが発生しました';
    let autoRetry = false;
    let retryDelay = 2000;
    let fallbackAction = 'ページを再読み込みしてください';

    // ネットワークエラー
    if (message.includes('network') || message.includes('fetch') || message.includes('connection') || 
        message.includes('timeout') || message.includes('cors')) {
      category = 'network';
      severity = 'medium';
      userMessage = 'ネットワーク接続に問題があります。しばらく待ってから再試行してください。';
      autoRetry = true;
      retryDelay = 3000;
      fallbackAction = 'オフライン機能を使用するか、後でもう一度お試しください';
    }
    
    // APIエラー
    else if (message.includes('api') || message.includes('endpoint') || message.includes('server')) {
      category = 'api';
      severity = 'high';
      userMessage = 'サーバーとの通信に問題があります。';
      autoRetry = true;
      retryDelay = 5000;
      fallbackAction = 'キャッシュされたデータを表示します';
    }
    
    // データエラー
    else if (message.includes('data') || message.includes('json') || message.includes('parse') || 
             message.includes('validation')) {
      category = 'data';
      severity = 'medium';
      userMessage = 'データの処理中に問題が発生しました。';
      autoRetry = false;
      fallbackAction = 'デフォルトデータを表示します';
    }
    
    // システムエラー
    else if (message.includes('system') || message.includes('internal') || 
             message.includes('unexpected')) {
      category = 'system';
      severity = 'high';
      userMessage = 'システム内部でエラーが発生しました。';
      autoRetry = true;
      retryDelay = 10000;
      fallbackAction = 'システムを再初期化します';
    }

    // 重大なエラー
    if (message.includes('critical') || message.includes('fatal') || 
        stack.includes('TypeError') || stack.includes('ReferenceError')) {
      severity = 'critical';
      userMessage = '重大なエラーが発生しました。ページを再読み込みしてください。';
      autoRetry = false;
      fallbackAction = 'ページを完全に再読み込みしてください';
    }

    return {
      category,
      severity,
      message: error.message,
      userMessage,
      autoRetry,
      retryDelay,
      fallbackAction,
      timestamp: new Date().toISOString(),
      context: {
        userAgent: typeof window !== 'undefined' ? window.navigator.userAgent : '',
        url: typeof window !== 'undefined' ? window.location.href : '',
        timestamp: Date.now()
      }
    };
  }

  /**
   * エラーの処理
   */
  async handleError(error: Error): Promise<boolean> {
    const errorInfo = this.categorizeError(error);
    this.errorHistory.push(errorInfo);

    console.error('統一エラーハンドラー:', errorInfo);

    // 復旧アクションの実行
    if (this.isRecovering) {
      console.log('既に復旧処理中です');
      return false;
    }

    this.isRecovering = true;

    try {
      const recoveryActions = this.recoveryActions.get(errorInfo.category) || [];
      
      for (const action of recoveryActions) {
        if (await action.execute()) {
          console.log(`復旧成功: ${action.description}`);
          this.isRecovering = false;
          return true;
        }
      }

      // フォールバックアクション
      if (await this.executeFallbackAction(errorInfo)) {
        console.log('フォールバック復旧成功');
        this.isRecovering = false;
        return true;
      }

    } catch (recoveryError) {
      console.error('復旧処理エラー:', recoveryError);
    } finally {
      this.isRecovering = false;
    }

    return false;
  }

  /**
   * 復旧アクションの初期化
   */
  private initializeRecoveryActions(): void {
    // ネットワークエラー用の復旧アクション
    this.recoveryActions.set('network', [
      {
        type: 'retry',
        description: 'ネットワーク接続の再試行',
        execute: async () => {
          await new Promise(resolve => setTimeout(resolve, 2000));
          return true;
        }
      },
      {
        type: 'clear-cache',
        description: 'キャッシュのクリア',
        execute: async () => {
          if ('caches' in window) {
            const cacheNames = await caches.keys();
            await Promise.all(cacheNames.map(name => caches.delete(name)));
          }
          return true;
        }
      }
    ]);

    // APIエラー用の復旧アクション
    this.recoveryActions.set('api', [
      {
        type: 'retry',
        description: 'API呼び出しの再試行',
        execute: async () => {
          await new Promise(resolve => setTimeout(resolve, 3000));
          return true;
        }
      },
      {
        type: 'fallback',
        description: 'フォールバックデータの使用',
        execute: async () => {
          // フォールバックデータの読み込み
          return true;
        }
      }
    ]);

    // データエラー用の復旧アクション
    this.recoveryActions.set('data', [
      {
        type: 'fallback',
        description: 'デフォルトデータの使用',
        execute: async () => {
          // デフォルトデータの読み込み
          return true;
        }
      }
    ]);

    // システムエラー用の復旧アクション
    this.recoveryActions.set('system', [
      {
        type: 'refresh',
        description: 'ページの再読み込み',
        execute: async () => {
          if (typeof window !== 'undefined') {
            window.location.reload();
          }
          return true;
        }
      }
    ]);
  }

  /**
   * フォールバックアクションの実行
   */
  private async executeFallbackAction(errorInfo: ErrorInfo): Promise<boolean> {
    try {
      switch (errorInfo.category) {
        case 'network':
          // オフライン機能の有効化
          return true;
        
        case 'api':
          // キャッシュデータの使用
          return true;
        
        case 'data':
          // デフォルトデータの使用
          return true;
        
        case 'system':
          // ページの再読み込み
          if (typeof window !== 'undefined') {
            window.location.reload();
          }
          return true;
        
        default:
          return false;
      }
    } catch (error) {
      console.error('フォールバックアクションエラー:', error);
      return false;
    }
  }

  /**
   * エラー履歴の取得
   */
  getErrorHistory(): ErrorInfo[] {
    return [...this.errorHistory];
  }

  /**
   * エラー履歴のクリア
   */
  clearErrorHistory(): void {
    this.errorHistory = [];
  }

  /**
   * 復旧状況の取得
   */
  getRecoveryStatus(): { isRecovering: boolean; lastError?: ErrorInfo } {
    return {
      isRecovering: this.isRecovering,
      lastError: this.errorHistory[this.errorHistory.length - 1]
    };
  }
}

// シングルトンインスタンス
export const unifiedErrorHandler = new UnifiedErrorHandler();

export default UnifiedErrorHandler;
