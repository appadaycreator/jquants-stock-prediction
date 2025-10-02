/**
 * 修正版J-Quants API アダプタ
 * 404エラー解消とリアルタイムデータ取得の実装
 */

interface JQuantsConfig {
  token: string;
  baseUrl: string;
  timeout: number;
  maxRetries: number;
  retryDelay: number;
  rateLimitDelay: number;
  enableDataValidation: boolean;
  enableQualityMonitoring: boolean;
}

interface StockData {
  date: string;
  code: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  sma_5?: number;
  sma_10?: number;
  sma_25?: number;
  sma_50?: number;
}

interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

class FixedJQuantsAdapter {
  private config: JQuantsConfig;
  private isInitialized: boolean = false;
  private authToken: string | null = null;
  private refreshToken: string | null = null;
  private tokenExpiry: number = 0;

  constructor(config: Partial<JQuantsConfig> = {}) {
    this.config = {
      token: process.env.NEXT_PUBLIC_JQUANTS_TOKEN || '',
      baseUrl: 'https://api.jquants.com/v1',
      timeout: 30000,
      maxRetries: 3,
      retryDelay: 1000,
      rateLimitDelay: 100,
      enableDataValidation: true,
      enableQualityMonitoring: true,
      ...config,
    };
  }

  /**
   * 初期化と認証
   */
  async initialize(): Promise<{ success: boolean; message: string }> {
    try {
      console.info("J-Quants初期化開始");
      
      // 認証トークンの取得
      await this.authenticate();
      
      this.isInitialized = true;
      console.info("J-Quants初期化完了");
      
      return {
        success: true,
        message: "J-Quants API初期化が完了しました"
      };
    } catch (error) {
      console.error("J-Quants初期化エラー:", error);
      return {
        success: false,
        message: `初期化に失敗しました: ${error instanceof Error ? error.message : "不明なエラー"}`
      };
    }
  }

  /**
   * 認証処理
   */
  private async authenticate(): Promise<void> {
    try {
      // 既存のトークンが有効かチェック
      if (this.authToken && Date.now() < this.tokenExpiry) {
        console.info("既存のトークンが有効です");
        return;
      }

      // 新しいトークンを取得
      const response = await fetch(`${this.config.baseUrl}/token/auth_user`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mailaddress: process.env.NEXT_PUBLIC_JQUANTS_EMAIL || '',
          password: process.env.NEXT_PUBLIC_JQUANTS_PASSWORD || '',
        }),
      });

      if (!response.ok) {
        throw new Error(`認証失敗: ${response.status} ${response.statusText}`);
      }

      const authData = await response.json();
      
      if (authData.refreshToken) {
        this.refreshToken = authData.refreshToken;
        
        // アクセストークンを取得
        const tokenResponse = await fetch(`${this.config.baseUrl}/token/auth_refresh`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            refreshtoken: this.refreshToken,
          }),
        });

        if (!tokenResponse.ok) {
          throw new Error(`トークン取得失敗: ${tokenResponse.status} ${tokenResponse.statusText}`);
        }

        const tokenData = await tokenResponse.json();
        this.authToken = tokenData.accessToken;
        this.tokenExpiry = Date.now() + (24 * 60 * 60 * 1000); // 24時間
        
        console.info("認証成功");
      } else {
        throw new Error("リフレッシュトークンが取得できませんでした");
      }
    } catch (error) {
      console.error("認証エラー:", error);
      throw error;
    }
  }

  /**
   * 認証ヘッダーの取得
   */
  private getAuthHeaders(): Record<string, string> {
    if (!this.authToken) {
      throw new Error("認証トークンが設定されていません");
    }

    return {
      'Authorization': `Bearer ${this.authToken}`,
      'Content-Type': 'application/json',
    };
  }

  /**
   * API呼び出し（リトライ機能付き）
   */
  private async makeApiCall<T>(
    apiCall: () => Promise<T>,
    operation: string = "API呼び出し"
  ): Promise<T> {
    let lastError: Error | null = null;
    
    for (let attempt = 1; attempt <= this.config.maxRetries; attempt++) {
      try {
        console.info(`${operation} 開始 (試行 ${attempt}/${this.config.maxRetries})`);
        
        const result = await apiCall();
        
        console.info(`${operation} 成功`);
        return result;
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));
        console.warn(`${operation} 失敗 (試行 ${attempt}/${this.config.maxRetries}):`, lastError.message);
        
        // 認証エラーの場合は再認証を試行
        if (lastError.message.includes('401') || lastError.message.includes('認証')) {
          try {
            await this.authenticate();
            continue;
          } catch (authError) {
            console.error("再認証失敗:", authError);
            throw authError;
          }
        }
        
        // 最後の試行でない場合は待機
        if (attempt < this.config.maxRetries) {
          const delay = this.config.retryDelay * Math.pow(2, attempt - 1);
          console.info(`${delay}ms待機後に再試行`);
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }
    
    throw lastError || new Error(`${operation} が最大試行回数に達しました`);
  }

  /**
   * 接続テスト
   */
  async testConnection(): Promise<{ success: boolean; message: string }> {
    try {
      console.info("J-Quants接続テスト開始");
      
      if (!this.isInitialized) {
        await this.initialize();
      }

      const data = await this.makeApiCall(async () => {
        const response = await fetch(`${this.config.baseUrl}/markets/stock/list`, {
          method: 'GET',
          headers: this.getAuthHeaders(),
        });

        if (!response.ok) {
          throw new Error(`API呼び出し失敗: ${response.status} ${response.statusText}`);
        }

        return await response.json();
      }, "接続テスト");

      console.info("J-Quants接続テスト成功", { 
        dataCount: data?.data?.length || 0,
      });

      return {
        success: true,
        message: `接続成功: ${data?.data?.length || 0}件の銘柄データを取得`,
      };
    } catch (error) {
      console.error("J-Quants接続テスト失敗:", error);
      
      return {
        success: false,
        message: `接続失敗: ${error instanceof Error ? error.message : "不明なエラー"}`,
      };
    }
  }

  /**
   * 株価データの取得
   */
  async getStockData(
    symbol: string, 
    startDate: string, 
    endDate: string,
    useCache: boolean = true,
  ): Promise<StockData[]> {
    try {
      console.info("株価データ取得開始", { symbol, startDate, endDate, useCache });

      if (!this.isInitialized) {
        await this.initialize();
      }

      // キャッシュから取得を試行
      if (useCache) {
        const cachedData = await this.getCachedData(symbol, startDate, endDate);
        if (cachedData.length > 0) {
          console.info("キャッシュからデータ取得", { 
            symbol, 
            count: cachedData.length,
            dateRange: `${startDate} - ${endDate}`,
          });
          return cachedData;
        }
      }

      // APIから取得
      const apiData = await this.makeApiCall(async () => {
        const response = await fetch(
          `${this.config.baseUrl}/markets/daily_quotes?code=${symbol}&from=${startDate}&to=${endDate}`,
          {
            method: 'GET',
            headers: this.getAuthHeaders(),
          }
        );

        if (!response.ok) {
          throw new Error(`API呼び出し失敗: ${response.status} ${response.statusText}`);
        }

        return await response.json();
      }, "株価データ取得");

      // データ変換
      const stockData: StockData[] = apiData.daily_quotes?.map((item: any) => ({
        date: item.Date,
        code: item.Code,
        open: parseFloat(item.Open) || 0,
        high: parseFloat(item.High) || 0,
        low: parseFloat(item.Low) || 0,
        close: parseFloat(item.Close) || 0,
        volume: parseInt(item.Volume) || 0,
      })) || [];

      // 移動平均の計算
      const dataWithMA = this.calculateMovingAverages(stockData);

      // キャッシュに保存
      if (useCache && dataWithMA.length > 0) {
        await this.saveToCache(symbol, dataWithMA, startDate, endDate);
      }

      console.info("APIからデータ取得完了", { 
        symbol, 
        count: dataWithMA.length, 
      });

      return dataWithMA;
    } catch (error) {
      console.error("株価データ取得エラー:", error);
      
      // フォールバック: キャッシュから取得
      if (useCache) {
        const cachedData = await this.getCachedData(symbol, startDate, endDate);
        if (cachedData.length > 0) {
          console.warn("フォールバック: キャッシュからデータ取得", { 
            symbol, 
            count: cachedData.length,
          });
          return cachedData;
        }
      }
      
      throw error;
    }
  }

  /**
   * 移動平均の計算
   */
  private calculateMovingAverages(data: StockData[]): StockData[] {
    const sortedData = data.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
    
    return sortedData.map((item, index) => {
      const result = { ...item };
      
      // SMA5
      if (index >= 4) {
        const sma5Data = sortedData.slice(index - 4, index + 1);
        result.sma_5 = sma5Data.reduce((sum, d) => sum + d.close, 0) / 5;
      }
      
      // SMA10
      if (index >= 9) {
        const sma10Data = sortedData.slice(index - 9, index + 1);
        result.sma_10 = sma10Data.reduce((sum, d) => sum + d.close, 0) / 10;
      }
      
      // SMA25
      if (index >= 24) {
        const sma25Data = sortedData.slice(index - 24, index + 1);
        result.sma_25 = sma25Data.reduce((sum, d) => sum + d.close, 0) / 25;
      }
      
      // SMA50
      if (index >= 49) {
        const sma50Data = sortedData.slice(index - 49, index + 1);
        result.sma_50 = sma50Data.reduce((sum, d) => sum + d.close, 0) / 50;
      }
      
      return result;
    });
  }

  /**
   * キャッシュからデータ取得
   */
  private async getCachedData(symbol: string, startDate: string, endDate: string): Promise<StockData[]> {
    try {
      const cacheKey = `stock_${symbol}_${startDate}_${endDate}`;
      const cached = localStorage.getItem(cacheKey);
      
      if (cached) {
        const { data, timestamp } = JSON.parse(cached);
        const now = Date.now();
        const cacheAge = now - timestamp;
        const maxAge = 60 * 60 * 1000; // 1時間
        
        if (cacheAge < maxAge) {
          return data;
        }
      }
      
      return [];
    } catch (error) {
      console.error("キャッシュ取得エラー:", error);
      return [];
    }
  }

  /**
   * キャッシュにデータ保存
   */
  private async saveToCache(symbol: string, data: StockData[], startDate: string, endDate: string): Promise<void> {
    try {
      const cacheKey = `stock_${symbol}_${startDate}_${endDate}`;
      const cacheData = {
        data,
        timestamp: Date.now(),
        symbol,
        startDate,
        endDate,
      };
      
      localStorage.setItem(cacheKey, JSON.stringify(cacheData));
      console.info("キャッシュに保存完了", { symbol, count: data.length });
    } catch (error) {
      console.error("キャッシュ保存エラー:", error);
    }
  }

  /**
   * システムヘルスチェック
   */
  getSystemHealth(): { status: string; issues: string[]; isInitialized: boolean } {
    const issues: string[] = [];
    
    if (!this.isInitialized) {
      issues.push("システムが初期化されていません");
    }
    
    if (!this.authToken) {
      issues.push("認証トークンが設定されていません");
    }
    
    if (Date.now() >= this.tokenExpiry) {
      issues.push("認証トークンの有効期限が切れています");
    }
    
    const status = issues.length === 0 ? "healthy" : "unhealthy";
    
    return {
      status,
      issues,
      isInitialized: this.isInitialized,
    };
  }
}

export default FixedJQuantsAdapter;
export type { JQuantsConfig, StockData, ApiResponse };
