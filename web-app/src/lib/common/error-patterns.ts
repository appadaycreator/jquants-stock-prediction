/**
 * 共通のエラーハンドリングパターン
 * アプリケーション全体で一貫したエラー処理を提供
 */

export interface ErrorPattern {
  category: 'network' | 'api' | 'data' | 'validation' | 'permission' | 'unknown';
  severity: 'low' | 'medium' | 'high' | 'critical';
  autoRetry: boolean;
  retryDelay: number;
  fallbackAction: 'none' | 'refresh' | 'clear-cache' | 'redirect' | 'reload';
  userMessage: string;
}

export class ErrorPatternMatcher {
  private static patterns: Map<string, ErrorPattern> = new Map([
    // ネットワークエラー
    ['network', {
      category: 'network',
      severity: 'medium',
      autoRetry: true,
      retryDelay: 3000,
      fallbackAction: 'refresh',
      userMessage: 'ネットワーク接続に問題があります。しばらく待ってから再試行してください。'
    }],
    ['fetch', {
      category: 'network',
      severity: 'medium',
      autoRetry: true,
      retryDelay: 3000,
      fallbackAction: 'refresh',
      userMessage: 'データの取得に失敗しました。接続を確認してください。'
    }],
    ['timeout', {
      category: 'network',
      severity: 'medium',
      autoRetry: true,
      retryDelay: 5000,
      fallbackAction: 'refresh',
      userMessage: 'タイムアウトが発生しました。しばらく待ってから再試行してください。'
    }],
    ['connection', {
      category: 'network',
      severity: 'high',
      autoRetry: true,
      retryDelay: 5000,
      fallbackAction: 'refresh',
      userMessage: 'サーバーとの接続に問題があります。'
    }],

    // APIエラー
    ['api', {
      category: 'api',
      severity: 'high',
      autoRetry: false,
      retryDelay: 0,
      fallbackAction: 'none',
      userMessage: 'API接続に問題があります。管理者にお問い合わせください。'
    }],
    ['http', {
      category: 'api',
      severity: 'high',
      autoRetry: false,
      retryDelay: 0,
      fallbackAction: 'none',
      userMessage: 'HTTPエラーが発生しました。'
    }],
    ['status', {
      category: 'api',
      severity: 'high',
      autoRetry: false,
      retryDelay: 0,
      fallbackAction: 'none',
      userMessage: 'サーバーエラーが発生しました。'
    }],

    // データエラー
    ['data', {
      category: 'data',
      severity: 'medium',
      autoRetry: true,
      retryDelay: 1000,
      fallbackAction: 'clear-cache',
      userMessage: 'データの処理中にエラーが発生しました。'
    }],
    ['parse', {
      category: 'data',
      severity: 'medium',
      autoRetry: true,
      retryDelay: 1000,
      fallbackAction: 'clear-cache',
      userMessage: 'データの解析に失敗しました。'
    }],
    ['json', {
      category: 'data',
      severity: 'medium',
      autoRetry: true,
      retryDelay: 1000,
      fallbackAction: 'clear-cache',
      userMessage: 'JSONデータの処理に失敗しました。'
    }],

    // バリデーションエラー
    ['validation', {
      category: 'validation',
      severity: 'low',
      autoRetry: false,
      retryDelay: 0,
      fallbackAction: 'none',
      userMessage: '入力データに問題があります。値を確認してください。'
    }],
    ['required', {
      category: 'validation',
      severity: 'low',
      autoRetry: false,
      retryDelay: 0,
      fallbackAction: 'none',
      userMessage: '必須項目が入力されていません。'
    }],
    ['format', {
      category: 'validation',
      severity: 'low',
      autoRetry: false,
      retryDelay: 0,
      fallbackAction: 'none',
      userMessage: '入力形式が正しくありません。'
    }],

    // 権限エラー
    ['permission', {
      category: 'permission',
      severity: 'high',
      autoRetry: false,
      retryDelay: 0,
      fallbackAction: 'redirect',
      userMessage: 'アクセス権限がありません。'
    }],
    ['unauthorized', {
      category: 'permission',
      severity: 'high',
      autoRetry: false,
      retryDelay: 0,
      fallbackAction: 'redirect',
      userMessage: '認証が必要です。ログインしてください。'
    }],
    ['forbidden', {
      category: 'permission',
      severity: 'high',
      autoRetry: false,
      retryDelay: 0,
      fallbackAction: 'redirect',
      userMessage: 'この操作は許可されていません。'
    }]
  ]);

  static matchError(error: Error): ErrorPattern {
    const message = error.message.toLowerCase();
    
    for (const [keyword, pattern] of this.patterns) {
      if (message.includes(keyword)) {
        return pattern;
      }
    }

    // デフォルトパターン
    return {
      category: 'unknown',
      severity: 'medium',
      autoRetry: false,
      retryDelay: 0,
      fallbackAction: 'none',
      userMessage: '予期しないエラーが発生しました。'
    };
  }

  static getPatternByCategory(category: string): ErrorPattern | undefined {
    return this.patterns.get(category);
  }
}

export interface ErrorHandlerConfig {
  maxRetries: number;
  retryDelay: number;
  enableAutoRetry: boolean;
  enableFallback: boolean;
  logErrors: boolean;
}

export class StandardErrorHandler {
  private config: ErrorHandlerConfig;
  private retryCounts = new Map<string, number>();
  private lastRetryTimes = new Map<string, number>();

  constructor(config: Partial<ErrorHandlerConfig> = {}) {
    this.config = {
      maxRetries: 3,
      retryDelay: 1000,
      enableAutoRetry: true,
      enableFallback: true,
      logErrors: true,
      ...config
    };
  }

  async handleError(error: Error, context?: { operation?: string; component?: string }): Promise<boolean> {
    const pattern = ErrorPatternMatcher.matchError(error);
    const errorKey = context ? `${context.operation}_${context.component}_${error.message}` : error.message;
    
    if (this.config.logErrors) {
      console.error('Error handled:', {
        error: error.message,
        pattern,
        context,
        timestamp: new Date().toISOString()
      });
    }

    // 自動リトライ
    if (this.config.enableAutoRetry && pattern.autoRetry) {
      return await this.handleRetry(error, errorKey, pattern);
    }

    // フォールバックアクション
    if (this.config.enableFallback) {
      return await this.executeFallback(pattern);
    }

    return false;
  }

  private async handleRetry(error: Error, errorKey: string, pattern: ErrorPattern): Promise<boolean> {
    const retryCount = this.retryCounts.get(errorKey) || 0;
    const lastRetryTime = this.lastRetryTimes.get(errorKey) || 0;
    const now = Date.now();

    // 最大リトライ回数チェック
    if (retryCount >= this.config.maxRetries) {
      return false;
    }

    // リトライ間隔チェック
    if (now - lastRetryTime < pattern.retryDelay) {
      return false;
    }

    // リトライ実行
    this.retryCounts.set(errorKey, retryCount + 1);
    this.lastRetryTimes.set(errorKey, now);

    try {
      await new Promise(resolve => setTimeout(resolve, pattern.retryDelay));
      return true;
    } catch (retryError) {
      console.error('Retry failed:', retryError);
      return false;
    }
  }

  private async executeFallback(pattern: ErrorPattern): Promise<boolean> {
    try {
      switch (pattern.fallbackAction) {
        case 'refresh':
          if (typeof window !== 'undefined') {
            window.location.reload();
          }
          break;
        case 'clear-cache':
          if (typeof window !== 'undefined' && 'caches' in window) {
            const cacheNames = await caches.keys();
            await Promise.all(cacheNames.map(name => caches.delete(name)));
          }
          break;
        case 'redirect':
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
          break;
        case 'reload':
          if (typeof window !== 'undefined') {
            window.location.reload();
          }
          break;
        default:
          return false;
      }
      return true;
    } catch (fallbackError) {
      console.error('Fallback action failed:', fallbackError);
      return false;
    }
  }

  reset(): void {
    this.retryCounts.clear();
    this.lastRetryTimes.clear();
  }
}

export const standardErrorHandler = new StandardErrorHandler();
