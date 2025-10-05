"use client";

interface ApiResponse<T> {
  data: T;
  success: boolean;
  error?: string;
  timestamp: string;
  source: "api" | "cache" | "fallback";
}

interface RetryConfig {
  maxRetries: number;
  baseDelay: number;
  maxDelay: number;
  backoffFactor: number;
}

interface ApiClientConfig {
  baseUrl: string;
  timeout: number;
  retryConfig: RetryConfig;
  enableFallback: boolean;
  fallbackDataPath: string;
}

export class ApiClient {
  private config: ApiClientConfig;
  private isOnline: boolean = true;
  private retryCount: number = 0;
  private lastSuccessfulRequest: number = 0;

  constructor(config: Partial<ApiClientConfig> = {}) {
    this.config = {
      baseUrl: config.baseUrl || "/api",
      timeout: config.timeout || 10000,
      retryConfig: {
        maxRetries: 3,
        baseDelay: 1000,
        maxDelay: 10000,
        backoffFactor: 2,
        ...config.retryConfig,
      },
      enableFallback: config.enableFallback ?? true,
      fallbackDataPath: config.fallbackDataPath || "/docs/data",
      ...config,
    };

    this.setupNetworkMonitoring();
  }

  private setupNetworkMonitoring(): void {
    if (typeof window !== "undefined") {
      window.addEventListener("online", () => {
        this.isOnline = true;
        this.retryCount = 0;
        console.log("🌐 オンライン復帰: API接続を再開します");
      });

      window.addEventListener("offline", () => {
        this.isOnline = false;
        console.log("📱 オフライン状態: キャッシュデータを使用します");
      });
    }
  }

  private async sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private calculateDelay(attempt: number): number {
    const { baseDelay, maxDelay, backoffFactor } = this.config.retryConfig;
    const delay = baseDelay * Math.pow(backoffFactor, attempt);
    return Math.min(delay, maxDelay);
  }

  private async fetchWithRetry<T>(
    url: string,
    options: RequestInit = {},
    attempt: number = 0,
  ): Promise<ApiResponse<T>> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.abortSignal,
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      this.retryCount = 0;
      this.lastSuccessfulRequest = Date.now();

      return {
        data,
        success: true,
        timestamp: new Date().toISOString(),
        source: "api",
      };

    } catch (error) {
      clearTimeout(timeoutId);

      if (attempt < this.config.retryConfig.maxRetries) {
        const delay = this.calculateDelay(attempt);
        console.warn(`API呼び出し失敗 (試行 ${attempt + 1}/${this.config.retryConfig.maxRetries}): ${error}`);
        console.log(`${delay}ms後に再試行します...`);
        
        await this.sleep(delay);
        return this.fetchWithRetry(url, options, attempt + 1);
      }

      throw error;
    }
  }

  private async getFallbackData<T>(endpoint: string): Promise<ApiResponse<T>> {
    try {
      const fallbackUrl = `${this.config.fallbackDataPath}/sample_${endpoint}.json`;
      const response = await fetch(fallbackUrl);
      
      if (!response.ok) {
        throw new Error(`フォールバックデータが見つかりません: ${fallbackUrl}`);
      }

      const data = await response.json();
      
      return {
        data,
        success: true,
        timestamp: new Date().toISOString(),
        source: "fallback",
      };

    } catch (error) {
      console.error("フォールバックデータの取得に失敗:", error);
      throw new Error("API接続とフォールバックデータの両方に失敗しました");
    }
  }

  async get<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    const url = `${this.config.baseUrl}/${endpoint}`;
    
    try {
      // オフライン時は即座にフォールバック
      if (!this.isOnline) {
        console.log("📱 オフライン状態: フォールバックデータを使用します");
        return this.getFallbackData<T>(endpoint);
      }

      // API呼び出しを試行
      return await this.fetchWithRetry<T>(url, { ...options, method: "GET" });

    } catch (error) {
      console.error(`API呼び出し失敗 (${endpoint}):`, error);

      // フォールバックが有効な場合は試行
      if (this.config.enableFallback) {
        try {
          console.log("🔄 フォールバックデータに切り替えます");
          return await this.getFallbackData<T>(endpoint);
        } catch (fallbackError) {
          console.error("フォールバックも失敗:", fallbackError);
        }
      }

      // 最終的にエラーを投げる
      throw new Error(`データの取得に失敗しました: ${error}`);
    }
  }

  async post<T>(endpoint: string, data: any, options: RequestInit = {}): Promise<ApiResponse<T>> {
    const url = `${this.config.baseUrl}/${endpoint}`;
    
    try {
      return await this.fetchWithRetry<T>(url, {
        ...options,
        method: "POST",
        body: JSON.stringify(data),
      });

    } catch (error) {
      console.error(`POST API呼び出し失敗 (${endpoint}):`, error);
      throw new Error(`データの送信に失敗しました: ${error}`);
    }
  }

  async put<T>(endpoint: string, data: any, options: RequestInit = {}): Promise<ApiResponse<T>> {
    const url = `${this.config.baseUrl}/${endpoint}`;
    
    try {
      return await this.fetchWithRetry<T>(url, {
        ...options,
        method: "PUT",
        body: JSON.stringify(data),
      });

    } catch (error) {
      console.error(`PUT API呼び出し失敗 (${endpoint}):`, error);
      throw new Error(`データの更新に失敗しました: ${error}`);
    }
  }

  async delete<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    const url = `${this.config.baseUrl}/${endpoint}`;
    
    try {
      return await this.fetchWithRetry<T>(url, {
        ...options,
        method: "DELETE",
      });

    } catch (error) {
      console.error(`DELETE API呼び出し失敗 (${endpoint}):`, error);
      throw new Error(`データの削除に失敗しました: ${error}`);
    }
  }

  // 接続状態の確認
  getConnectionStatus(): {
    isOnline: boolean;
    retryCount: number;
    lastSuccessfulRequest: number;
    timeSinceLastSuccess: number;
  } {
    return {
      isOnline: this.isOnline,
      retryCount: this.retryCount,
      lastSuccessfulRequest: this.lastSuccessfulRequest,
      timeSinceLastSuccess: Date.now() - this.lastSuccessfulRequest,
    };
  }

  // 設定の更新
  updateConfig(newConfig: Partial<ApiClientConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  // リトライ設定の更新
  updateRetryConfig(retryConfig: Partial<RetryConfig>): void {
    this.config.retryConfig = { ...this.config.retryConfig, ...retryConfig };
  }
}

// シングルトンインスタンス
export const apiClient = new ApiClient({
  baseUrl: "/api",
  timeout: 10000,
  retryConfig: {
    maxRetries: 3,
    baseDelay: 1000,
    maxDelay: 10000,
    backoffFactor: 2,
  },
  enableFallback: true,
  fallbackDataPath: "/docs/data",
});

export default ApiClient;
