/**
 * 強化されたAPIクライアント
 * リトライ機能、エラーハンドリング、キャッシュ機能を統合
 */

interface ApiClientConfig {
  baseUrl: string;
  timeout: number;
  maxRetries: number;
  retryDelay: number;
  enableCache: boolean;
  cacheTtl: number;
}

interface RetryOptions {
  maxRetries: number;
  retryDelay: number;
  backoffMultiplier: number;
  retryCondition: (error: any) => boolean;
}

interface CacheOptions {
  ttl: number;
  key: string;
  tags?: string[];
}

interface ApiResponse<T> {
  data: T;
  fromCache: boolean;
  retryCount: number;
  responseTime: number;
  error?: string;
}

class EnhancedApiClient {
  private config: ApiClientConfig;
  private cache: Map<string, { data: any; timestamp: number; ttl: number }> = new Map();
  private requestQueue: Map<string, Promise<any>> = new Map();

  constructor(config: Partial<ApiClientConfig> = {}) {
    this.config = {
      baseUrl: config.baseUrl || '/api/proxy',
      timeout: config.timeout || 30000,
      maxRetries: config.maxRetries || 3,
      retryDelay: config.retryDelay || 1000,
      enableCache: config.enableCache !== false,
      cacheTtl: config.cacheTtl || 300000, // 5分
    };
  }

  /**
   * GETリクエストの実行
   */
  async get<T>(
    endpoint: string,
    params?: Record<string, any>,
    options: {
      retry?: RetryOptions;
      cache?: CacheOptions;
      timeout?: number;
    } = {}
  ): Promise<ApiResponse<T>> {
    return this.request<T>('GET', endpoint, undefined, params, options);
  }

  /**
   * POSTリクエストの実行
   */
  async post<T>(
    endpoint: string,
    data?: any,
    options: {
      retry?: RetryOptions;
      cache?: CacheOptions;
      timeout?: number;
    } = {}
  ): Promise<ApiResponse<T>> {
    return this.request<T>('POST', endpoint, data, undefined, options);
  }

  /**
   * 統合リクエスト処理
   */
  private async request<T>(
    method: string,
    endpoint: string,
    data?: any,
    params?: Record<string, any>,
    options: {
      retry?: RetryOptions;
      cache?: CacheOptions;
      timeout?: number;
    } = {}
  ): Promise<ApiResponse<T>> {
    const startTime = performance.now();
    const cacheKey = this.generateCacheKey(method, endpoint, data, params);
    
    // キャッシュチェック
    if (options.cache && this.config.enableCache) {
      const cached = this.getFromCache(cacheKey);
      if (cached) {
        return {
          data: cached,
          fromCache: true,
          retryCount: 0,
          responseTime: performance.now() - startTime,
        };
      }
    }

    // 重複リクエストの防止
    if (this.requestQueue.has(cacheKey)) {
      const result = await this.requestQueue.get(cacheKey);
      return {
        data: result,
        fromCache: false,
        retryCount: 0,
        responseTime: performance.now() - startTime,
      };
    }

    // リトライ設定
    const retryOptions: RetryOptions = {
      maxRetries: options.retry?.maxRetries || this.config.maxRetries,
      retryDelay: options.retry?.retryDelay || this.config.retryDelay,
      backoffMultiplier: options.retry?.backoffMultiplier || 2,
      retryCondition: options.retry?.retryCondition || this.defaultRetryCondition,
    };

    // リクエスト実行
    const requestPromise = this.executeWithRetry<T>(
      method,
      endpoint,
      retryOptions,
      options.timeout || this.config.timeout,
      data,
      params
    );

    this.requestQueue.set(cacheKey, requestPromise);

    try {
      const result = await requestPromise;
      const responseTime = performance.now() - startTime;

      // キャッシュに保存
      if (options.cache && this.config.enableCache) {
        this.setCache(cacheKey, result, options.cache.ttl || this.config.cacheTtl);
      }

      return {
        data: result,
        fromCache: false,
        retryCount: 0,
        responseTime,
      };
    } catch (error) {
      throw error;
    } finally {
      this.requestQueue.delete(cacheKey);
    }
  }

  /**
   * リトライ機能付きリクエスト実行
   */
  private async executeWithRetry<T>(
    method: string,
    endpoint: string,
    retryOptions: RetryOptions,
    timeout: number,
    data?: any,
    params?: Record<string, any>
  ): Promise<T> {
    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= retryOptions.maxRetries; attempt++) {
      try {
        const response = await this.executeRequest(method, endpoint, timeout, data, params);
        return response;
      } catch (error) {
        lastError = error as Error;
        
        // リトライ条件チェック
        if (attempt < retryOptions.maxRetries && retryOptions.retryCondition(error)) {
          const delay = retryOptions.retryDelay * Math.pow(retryOptions.backoffMultiplier, attempt);
          console.warn(`リクエスト失敗 (試行 ${attempt + 1}/${retryOptions.maxRetries + 1}):`, error);
          console.log(`${delay}ms後にリトライ...`);
          await this.sleep(delay);
        } else {
          break;
        }
      }
    }

    throw new Error(`リクエストが${retryOptions.maxRetries + 1}回の試行後に失敗: ${lastError?.message}`);
  }

  /**
   * 実際のリクエスト実行
   */
  private async executeRequest(
    method: string,
    endpoint: string,
    timeout: number,
    data?: any,
    params?: Record<string, any>
  ): Promise<any> {
    const url = new URL(`${this.config.baseUrl}?endpoint=${endpoint}`);
    
    // パラメータの追加
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, String(value));
      });
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url.toString(), {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: data ? JSON.stringify(data) : undefined,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(`HTTP ${response.status}: ${response.statusText} - ${errorData}`);
      }

      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }

  /**
   * デフォルトリトライ条件
   */
  private defaultRetryCondition(error: any): boolean {
    // ネットワークエラー、タイムアウト、5xxエラーの場合はリトライ
    if (error.name === 'AbortError') return true; // タイムアウト
    if (error.message?.includes('HTTP 5')) return true; // 5xxエラー
    if (error.message?.includes('fetch')) return true; // ネットワークエラー
    return false;
  }

  /**
   * キャッシュキーの生成
   */
  private generateCacheKey(method: string, endpoint: string, data?: any, params?: Record<string, any>): string {
    const keyData = {
      method,
      endpoint,
      data,
      params,
    };
    return btoa(JSON.stringify(keyData));
  }

  /**
   * キャッシュからの取得
   */
  private getFromCache(key: string): any | null {
    const cached = this.cache.get(key);
    if (!cached) return null;

    const now = Date.now();
    if (now - cached.timestamp > cached.ttl) {
      this.cache.delete(key);
      return null;
    }

    return cached.data;
  }

  /**
   * キャッシュへの保存
   */
  private setCache(key: string, data: any, ttl: number): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    });
  }

  /**
   * キャッシュのクリア
   */
  clearCache(pattern?: string): void {
    if (pattern) {
      for (const key of this.cache.keys()) {
        if (key.includes(pattern)) {
          this.cache.delete(key);
        }
      }
    } else {
      this.cache.clear();
    }
  }

  /**
   * キャッシュ統計の取得
   */
  getCacheStats(): { size: number; keys: string[] } {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys()),
    };
  }

  /**
   * スリープ関数
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// シングルトンインスタンス
const apiClient = new EnhancedApiClient({
  baseUrl: '/api/proxy',
  timeout: 30000,
  maxRetries: 3,
  retryDelay: 1000,
  enableCache: true,
  cacheTtl: 300000, // 5分
});

export default apiClient;
export type { ApiClientConfig, RetryOptions, CacheOptions, ApiResponse };
