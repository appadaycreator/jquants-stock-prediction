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

export class UnifiedApiClient {
  private baseURL: string;
  private defaultConfig: ApiRequestConfig;

  constructor(baseURL: string = "") {
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
    return this.request<T>("GET", url, undefined, config);
  }

  // POST リクエスト
  async post<T = any>(url: string, data?: any, config: ApiRequestConfig = {}): Promise<ApiResponse<T>> {
    return this.request<T>("POST", url, data, config);
  }

  // PUT リクエスト
  async put<T = any>(url: string, data?: any, config: ApiRequestConfig = {}): Promise<ApiResponse<T>> {
    return this.request<T>("PUT", url, data, config);
  }

  // DELETE リクエスト
  async delete<T = any>(url: string, config: ApiRequestConfig = {}): Promise<ApiResponse<T>> {
    return this.request<T>("DELETE", url, undefined, config);
  }

  // 汎用リクエストメソッド
  private async request<T>(
    method: string,
    url: string,
    data?: any,
    config: ApiRequestConfig = {},
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
    
    throw lastError || new Error("Request failed");
  }

  // 実際のHTTPリクエストを実行
  private async executeRequest<T>(
    method: string,
    url: string,
    data: any | undefined,
    config: ApiRequestConfig,
  ): Promise<ApiResponse<T>> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), config.timeout);

    try {
      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
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
    if (url.startsWith("http")) {
      return url;
    }
    return `${this.baseURL}${url.startsWith("/") ? url : `/${url}`}`;
  }

  // ヘッダーを抽出
  private extractHeaders(response: Response): Record<string, string> {
    const headers: Record<string, string> = {};
    if (response.headers && typeof response.headers.forEach === "function") {
      response.headers.forEach((value, key) => {
        headers[key] = value;
      });
    }
    return headers;
  }

  // 遅延処理
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // 接続テスト
  async testConnection(): Promise<{ success: boolean; message: string }> {
    // 静的サイトの場合はモック成功を返す
    if (this.isStaticSite()) {
      return {
        success: true,
        message: '静的サイトモード: モックデータを使用中',
      };
    }

    try {
      // J-Quants APIプロキシの接続テスト
      const response = await fetch("/api/health", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const healthData = await response.json();
      
      return {
        success: true,
        message: `API接続成功: ${healthData.status}`,
      };
    } catch (error) {
      console.error("API接続テストエラー:", error);
      return {
        success: false,
        message: `API接続失敗: ${error instanceof Error ? error.message : "Unknown error"}`,
      };
    }
  }

  // 静的サイトかどうかを判定
  private isStaticSite(): boolean {
    if (typeof window === 'undefined') return true;
    
    // GitHub Pages のドメインパターンをチェック
    const hostname = window.location.hostname;
    return hostname.includes('github.io') || 
           hostname.includes('netlify.app') || 
           hostname.includes('vercel.app') ||
           hostname.includes('appadaycreator.github.io') ||
           hostname.includes('localhost'); // 開発環境でも静的サイトとして扱う
  }

  // 株価データ取得
  async getStockData(symbol: string): Promise<any> {
    if (this.isStaticSite()) {
      // 静的サイトの場合はモックデータを返す
      return {
        symbol,
        price: 2500,
        change: 2.5,
        volume: 1000000,
        lastUpdated: new Date().toISOString()
      };
    }
    const response = await this.get(`/stocks/${symbol}`);
    return response.data;
  }

  // 市場データ取得
  async getMarketData(): Promise<any> {
    if (this.isStaticSite()) {
      // 静的サイトの場合はモックデータを返す
      return {
        marketStatus: 'open',
        topGainers: [],
        topLosers: [],
        lastUpdated: new Date().toISOString()
      };
    }
    const response = await this.get("/market");
    return response.data;
  }

  // 予測データ取得
  async getPredictions(): Promise<any> {
    if (this.isStaticSite()) {
      // 静的サイトの場合はモックデータを返す
      return {
        predictions: [],
        lastUpdated: new Date().toISOString()
      };
    }
    const response = await this.get("/predictions");
    return response.data;
  }

  // 個人投資データ取得
  async getPersonalInvestmentData(): Promise<any> {
    if (this.isStaticSite()) {
      // 静的サイトの場合はモックデータを返す
      return {
        portfolio: { totalValue: 1000000, totalReturn: 5.2 },
        positions: [],
        lastUpdated: new Date().toISOString()
      };
    }
    const response = await this.get("/personal-investment");
    return response.data;
  }
}

// シングルトンインスタンス
export const unifiedApiClient = new UnifiedApiClient();

// 便利な関数としてエクスポート
export const testConnection = () => unifiedApiClient.testConnection();
