/**
 * 統一されたAPIクライアント
 * アプリケーション全体で使用されるAPI通信機能を提供
 */

export interface ApiResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
  headers: Record<string, string>;
}

export interface ApiRequestConfig {
  timeout?: number;
  retries?: number;
  retryDelay?: number;
  headers?: Record<string, string>;
  cache?: boolean;
  cacheTTL?: number;
}

class UnifiedApiClient {
  private baseURL: string;
  private defaultConfig: ApiRequestConfig;

  constructor(baseURL: string = '/api') {
    this.baseURL = baseURL;
    this.defaultConfig = {
      timeout: 10000,
      retries: 3,
      retryDelay: 1000,
      cache: true,
      cacheTTL: 300000, // 5分
    };
  }

  // GET リクエスト
  async get<T = any>(url: string, config: ApiRequestConfig = {}): Promise<ApiResponse<T>> {
    return this.request<T>('GET', url, undefined, config);
  }

  // POST リクエスト
  async post<T = any>(url: string, data?: any, config: ApiRequestConfig = {}): Promise<ApiResponse<T>> {
    return this.request<T>('POST', url, data, config);
  }

  // PUT リクエスト
  async put<T = any>(url: string, data?: any, config: ApiRequestConfig = {}): Promise<ApiResponse<T>> {
    return this.request<T>('PUT', url, data, config);
  }

  // DELETE リクエスト
  async delete<T = any>(url: string, config: ApiRequestConfig = {}): Promise<ApiResponse<T>> {
    return this.request<T>('DELETE', url, undefined, config);
  }

  // 汎用リクエストメソッド
  private async request<T>(
    method: string,
    url: string,
    data?: any,
    config: ApiRequestConfig = {}
  ): Promise<ApiResponse<T>> {
    const mergedConfig = { ...this.defaultConfig, ...config };
    const fullUrl = this.buildUrl(url);
    
    let lastError: Error | null = null;
    
    for (let attempt = 0; attempt <= mergedConfig.retries!; attempt++) {
      try {
        const response = await this.executeRequest<T>(method, fullUrl, data, mergedConfig);
        return response;
      } catch (error) {
        lastError = error as Error;
        
        if (attempt < mergedConfig.retries!) {
          await this.delay(mergedConfig.retryDelay! * Math.pow(2, attempt));
          continue;
        }
      }
    }
    
    throw lastError || new Error('Request failed');
  }

  // 実際のHTTPリクエストを実行
  private async executeRequest<T>(
    method: string,
    url: string,
    data?: any,
    config: ApiRequestConfig
  ): Promise<ApiResponse<T>> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), config.timeout);

    try {
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          ...config.headers,
        },
        body: data ? JSON.stringify(data) : undefined,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const responseData = await response.json();
      
      return {
        data: responseData,
        status: response.status,
        statusText: response.statusText,
        headers: this.extractHeaders(response),
      };
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }

  // URLを構築
  private buildUrl(url: string): string {
    if (url.startsWith('http')) {
      return url;
    }
    return `${this.baseURL}${url.startsWith('/') ? url : `/${url}`}`;
  }

  // ヘッダーを抽出
  private extractHeaders(response: Response): Record<string, string> {
    const headers: Record<string, string> = {};
    response.headers.forEach((value, key) => {
      headers[key] = value;
    });
    return headers;
  }

  // 遅延処理
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // 接続テスト
  async testConnection(): Promise<{ success: boolean; message: string }> {
    try {
      const response = await this.get('/health', { timeout: 5000, retries: 1 });
      return {
        success: true,
        message: 'Connection successful',
      };
    } catch (error) {
      return {
        success: false,
        message: `Connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
      };
    }
  }
}

// シングルトンインスタンス
export const unifiedApiClient = new UnifiedApiClient();
