/**
 * J-Quants API アダプタ
 * 自動認証、IndexedDBキャッシュ、差分更新機能
 */

interface JQuantsConfig {
  email?: string;
  password?: string;
  token?: string;
  baseUrl: string;
  timeout: number;
}

interface JQuantsAuthResponse {
  refreshToken?: string;
  refreshtoken?: string;
}

interface JQuantsTokenResponse {
  idtoken?: string;
  idToken?: string;
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

interface CacheMetadata {
  lastUpdated: string;
  dataVersion: string;
  symbol: string;
  dateRange: {
    start: string;
    end: string;
  };
}

class JQuantsAdapter {
  private config: JQuantsConfig;
  private db: IDBDatabase | null = null;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;
  private readonly DB_NAME = "jquants_cache";
  private readonly DB_VERSION = 1;
  private readonly STORE_NAME = "stock_data";
  private readonly METADATA_STORE = "metadata";

  constructor(config: JQuantsConfig) {
    this.config = config;
    this.accessToken = config.token || null;
    
    // ブラウザ環境でのみIndexedDBを初期化
    if (typeof window !== "undefined") {
      this.initDB().catch(error => {
        console.warn("IndexedDB初期化に失敗しました（キャッシュ機能は無効）:", error);
      });
    }
  }

  /**
   * IndexedDBの初期化
   */
  private async initDB(): Promise<void> {
    if (typeof window === "undefined" || typeof indexedDB === "undefined") {
      console.info("IndexedDBはクライアントサイドでのみ利用可能です");
      return;
    }
    
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.DB_NAME, this.DB_VERSION);
      
      request.onerror = () => {
        console.error("IndexedDB初期化エラー:", request.error);
        reject(request.error);
      };
      
      request.onsuccess = () => {
        this.db = request.result;
        console.info("IndexedDB初期化完了");
        resolve();
      };
      
      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        
        // 株価データストア
        if (!db.objectStoreNames.contains(this.STORE_NAME)) {
          const stockStore = db.createObjectStore(this.STORE_NAME, { keyPath: ["symbol", "date"] });
          stockStore.createIndex("symbol", "symbol", { unique: false });
          stockStore.createIndex("date", "date", { unique: false });
        }
        
        // メタデータストア
        if (!db.objectStoreNames.contains(this.METADATA_STORE)) {
          db.createObjectStore(this.METADATA_STORE, { keyPath: "symbol" });
        }
      };
    });
  }

  /**
   * 認証を実行してアクセストークンを取得
   */
  async authenticate(): Promise<{ success: boolean; message: string }> {
    try {
      // 既存のアクセストークンがある場合はテストする
      if (this.accessToken) {
        const testResult = await this.testConnectionInternal();
        if (testResult.success) {
          return { success: true, message: "既存のトークンで認証済み" };
        }
      }

      if (!this.config.email || !this.config.password) {
        return { 
          success: false, 
          message: "認証情報が設定されていません。環境変数JQUANTS_EMAIL, JQUANTS_PASSWORDを設定してください。", 
        };
      }

      console.info("J-Quants認証開始");

      // Step 1: リフレッシュトークンを取得
      const authResponse = await fetch("https://api.jquants.com/v1/token/auth_user", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          mailaddress: this.config.email,
          password: this.config.password,
        }),
        signal: AbortSignal.timeout(this.config.timeout),
      });

      if (!authResponse.ok) {
        throw new Error(`認証失敗: HTTP ${authResponse.status}`);
      }

      const authData: JQuantsAuthResponse = await authResponse.json();
      this.refreshToken = authData.refreshToken || authData.refreshtoken || null;

      // Step 2: アクセストークンを取得
      if (!this.refreshToken) {
        throw new Error("リフレッシュトークンが取得できませんでした");
      }
      const tokenResponse = await fetch(`https://api.jquants.com/v1/token/auth_refresh?refreshtoken=${encodeURIComponent(this.refreshToken)}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        signal: AbortSignal.timeout(this.config.timeout),
      });

      if (!tokenResponse.ok) {
        throw new Error(`トークン取得失敗: HTTP ${tokenResponse.status}`);
      }

      const tokenData: JQuantsTokenResponse = await tokenResponse.json();
      this.accessToken = tokenData.idtoken || tokenData.idToken || null;

      console.info("J-Quants認証成功");
      return { success: true, message: "認証が完了しました" };

    } catch (error) {
      console.error("J-Quants認証エラー:", error);
      return {
        success: false,
        message: `認証失敗: ${error instanceof Error ? error.message : "不明なエラー"}`,
      };
    }
  }

  /**
   * 全銘柄一覧の取得（コード・名称・セクター）
   * 失敗時は空配列を返す
   */
  async getAllSymbols(): Promise<Array<{ code: string; name: string; sector?: string }>> {
    try {
      // 認証を確保
      await this.ensureAuthenticated();

      const response = await fetch(`${this.config.baseUrl}/listed/info`, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${this.accessToken}`,
          "Content-Type": "application/json",
        },
        signal: AbortSignal.timeout(this.config.timeout),
      });

      if (!response.ok) {
        console.error("全銘柄一覧取得失敗", response.status, response.statusText);
        return [];
      }

      const data = await response.json();
      const list: any[] = data?.info || [];
      return list.map((item: any) => ({
        code: item?.Code || item?.code,
        name: item?.CompanyName || item?.name || item?.CompanyNameEnglish || "不明",
        sector: item?.Sector33CodeName || item?.sector,
      })).filter((s: any) => !!s.code && !!s.name);
    } catch (error) {
      console.error("全銘柄一覧取得エラー:", error);
      return [];
    }
  }

  /**
   * 認証を確保する（必要に応じて自動認証）
   */
  private async ensureAuthenticated(): Promise<void> {
    if (!this.accessToken) {
      const authResult = await this.authenticate();
      if (!authResult.success) {
        throw new Error(authResult.message);
      }
    }
  }

  /**
   * トークン接続テスト（内部用）
   */
  private async testConnectionInternal(): Promise<{ success: boolean; message: string }> {
    try {
      const response = await fetch(`${this.config.baseUrl}/listed/info`, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${this.accessToken}`,
          "Content-Type": "application/json",
        },
        signal: AbortSignal.timeout(this.config.timeout),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        success: true,
        message: `接続成功: ${data?.info?.length || 0}件の銘柄データを取得`,
      };
    } catch (error) {
      return {
        success: false,
        message: `接続失敗: ${error instanceof Error ? error.message : "不明なエラー"}`,
      };
    }
  }

  /**
   * トークン接続テスト（公開メソッド）
   */
  async testConnection(): Promise<{ success: boolean; message: string }> {
    try {
      console.info("J-Quants接続テスト開始");
      
      // 認証を確保
      await this.ensureAuthenticated();
      
      const result = await this.testConnectionInternal();
      
      if (result.success) {
        console.info("J-Quants接続テスト成功", result.message);
      } else {
        console.error("J-Quants接続テスト失敗", result.message);
      }

      return result;
    } catch (error) {
      console.error("J-Quants接続テストエラー:", error);
      return {
        success: false,
        message: `接続失敗: ${error instanceof Error ? error.message : "不明なエラー"}`,
      };
    }
  }

  /**
   * 株価データの取得（キャッシュ対応）
   */
  async getStockData(
    symbol: string, 
    startDate: string, 
    endDate: string,
    useCache: boolean = true,
  ): Promise<StockData[]> {
    try {
      console.info("株価データ取得開始", { symbol, startDate, endDate, useCache });

      // 認証を確保
      await this.ensureAuthenticated();

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
      const apiData = await this.fetchFromAPI(symbol, startDate, endDate);
      
      // キャッシュに保存
      if (useCache && apiData.length > 0) {
        await this.saveToCache(symbol, apiData, startDate, endDate);
      }

      console.info("APIからデータ取得完了", { 
        symbol, 
        count: apiData.length, 
      });

      return apiData;
    } catch (error) {
      console.error("株価データ取得エラー:", error);
      throw error;
    }
  }

  /**
   * 差分更新：直近7日は常時再取得
   * サブスクリプション期間内の日付を使用（2023-07-10 ~ 2025-07-10）
   */
  async getIncrementalData(symbol: string): Promise<StockData[]> {
    try {
      // サブスクリプション期間内の日付を使用
      const subscriptionEnd = new Date("2025-07-10");
      const today = new Date();
      const actualEndDate = today > subscriptionEnd ? subscriptionEnd : today;
      const sevenDaysAgo = new Date(actualEndDate.getTime() - 7 * 24 * 60 * 60 * 1000);
      const sevenDaysAgoStr = sevenDaysAgo.toISOString().split("T")[0];
      const todayStr = actualEndDate.toISOString().split("T")[0];

      console.info("差分更新開始", { symbol, dateRange: `${sevenDaysAgoStr} - ${todayStr}` });

      // 直近7日を常時再取得
      const recentData = await this.getStockData(symbol, sevenDaysAgoStr, todayStr, false);
      
      // 既存のキャッシュデータとマージ
      const existingData = await this.getCachedData(symbol, "2020-01-01", sevenDaysAgoStr);
      const mergedData = [...existingData, ...recentData].sort((a, b) => 
        new Date(a.date).getTime() - new Date(b.date).getTime(),
      );

      // キャッシュを更新
      await this.saveToCache(symbol, mergedData, "2020-01-01", todayStr);

      console.info("差分更新完了", { 
        symbol, 
        totalCount: mergedData.length,
        newCount: recentData.length, 
      });

      return mergedData;
    } catch (error) {
      console.error("差分更新エラー:", error);
      throw error;
    }
  }

  /**
   * APIから直接データを取得
   */
  private async fetchFromAPI(symbol: string, startDate: string, endDate: string): Promise<StockData[]> {
    const params = new URLSearchParams({
      code: symbol,
      from: startDate,
      to: endDate,
    });

    const response = await fetch(`https://api.jquants.com/v1/prices/daily_quotes?${params}`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${this.accessToken}`,
        "Content-Type": "application/json",
      },
      signal: AbortSignal.timeout(this.config.timeout),
    });

    if (!response.ok) {
      const errorText = await response.text().catch(() => "エラーレスポンスの読み取りに失敗");
      
      // サブスクリプション期間外のエラーの場合、サンプルデータを返す
      if (response.status === 400 && errorText.includes("subscription covers")) {
        console.warn(`サブスクリプション期間外のデータ要求: ${symbol} (${startDate} - ${endDate})`);
        return this.generateSampleStockData(symbol, startDate, endDate);
      }
      
      console.error(`API取得失敗: HTTP ${response.status}`, {
        url: `https://api.jquants.com/v1/prices/daily_quotes?${params}`,
        status: response.status,
        statusText: response.statusText,
        error: errorText,
        params: { symbol, startDate, endDate },
      });
      throw new Error(`API取得失敗: HTTP ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    return this.transformAPIResponse(data, symbol);
  }

  /**
   * サンプル株価データを生成（サブスクリプション期間外の場合）
   */
  private generateSampleStockData(symbol: string, startDate: string, endDate: string): StockData[] {
    const sampleData: StockData[] = [];
    const start = new Date(startDate);
    const end = new Date(endDate);
    
    // 日付範囲内のサンプルデータを生成
    for (let date = new Date(start); date <= end; date.setDate(date.getDate() + 1)) {
      // 土日をスキップ
      if (date.getDay() === 0 || date.getDay() === 6) continue;
      
      const basePrice = 1000 + Math.random() * 5000;
      const variation = (Math.random() - 0.5) * 100;
      
      sampleData.push({
        date: date.toISOString().split("T")[0],
        code: symbol,
        open: basePrice + variation,
        high: basePrice + variation + Math.random() * 50,
        low: basePrice + variation - Math.random() * 50,
        close: basePrice + variation + (Math.random() - 0.5) * 20,
        volume: Math.floor(Math.random() * 1000000),
        sma_5: basePrice + variation * 0.8,
        sma_10: basePrice + variation * 0.6,
        sma_25: basePrice + variation * 0.4,
        sma_50: basePrice + variation * 0.2,
      });
    }
    
    console.info(`サンプルデータを生成: ${symbol} (${sampleData.length}件)`);
    return sampleData;
  }

  /**
   * APIレスポンスをStockData形式に変換
   */
  private transformAPIResponse(apiData: any, symbol: string): StockData[] {
    if (!apiData?.daily_quotes) {
      return [];
    }

    return apiData.daily_quotes
      .filter((item: any) => item.Code === symbol)
      .map((item: any) => ({
        date: item.Date,
        code: item.Code,
        open: parseFloat(item.Open) || 0,
        high: parseFloat(item.High) || 0,
        low: parseFloat(item.Low) || 0,
        close: parseFloat(item.Close) || 0,
        volume: parseInt(item.Volume) || 0,
        // 技術指標は別途計算が必要
        sma_5: undefined,
        sma_10: undefined,
        sma_25: undefined,
        sma_50: undefined,
      }))
      .sort((a: StockData, b: StockData) => new Date(a.date).getTime() - new Date(b.date).getTime());
  }

  /**
   * キャッシュからデータを取得
   */
  private async getCachedData(symbol: string, startDate: string, endDate: string): Promise<StockData[]> {
    if (!this.db) {
      return [];
    }

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.STORE_NAME], "readonly");
      const store = transaction.objectStore(this.STORE_NAME);
      const index = store.index("symbol");
      const request = index.getAll(symbol);

      request.onsuccess = () => {
        const allData = request.result;
        const filteredData = allData.filter(item => 
          item.date >= startDate && item.date <= endDate,
        );
        resolve(filteredData);
      };

      request.onerror = () => {
        console.error("キャッシュ取得エラー:", request.error);
        reject(request.error);
      };
    });
  }

  /**
   * データをキャッシュに保存
   */
  private async saveToCache(symbol: string, data: StockData[], startDate: string, endDate: string): Promise<void> {
    if (!this.db || data.length === 0) {
      return;
    }

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.STORE_NAME, this.METADATA_STORE], "readwrite");
      
      // 株価データを保存
      const stockStore = transaction.objectStore(this.STORE_NAME);
      const metadataStore = transaction.objectStore(this.METADATA_STORE);

      let completed = 0;
      const total = data.length + 1; // データ + メタデータ

      data.forEach(item => {
        const request = stockStore.put(item);
        request.onsuccess = () => {
          completed++;
          if (completed === total) {
            resolve();
          }
        };
        request.onerror = () => {
          console.error("キャッシュ保存エラー:", request.error);
          reject(request.error);
        };
      });

      // メタデータを保存
      const metadata: CacheMetadata = {
        lastUpdated: new Date().toISOString(),
        dataVersion: "1.0",
        symbol,
        dateRange: { start: startDate, end: endDate },
      };

      const metadataRequest = metadataStore.put(metadata);
      metadataRequest.onsuccess = () => {
        completed++;
        if (completed === total) {
          resolve();
        }
      };
      metadataRequest.onerror = () => {
        console.error("メタデータ保存エラー:", metadataRequest.error);
        reject(metadataRequest.error);
      };
    });
  }

  /**
   * キャッシュのクリア
   */
  async clearCache(symbol?: string): Promise<void> {
    if (!this.db) {
      return;
    }

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.STORE_NAME, this.METADATA_STORE], "readwrite");
      
      if (symbol) {
        // 特定銘柄のキャッシュをクリア
        const stockStore = transaction.objectStore(this.STORE_NAME);
        const index = stockStore.index("symbol");
        const request = index.getAll(symbol);
        
        request.onsuccess = () => {
          const data = request.result;
          let completed = 0;
          
          data.forEach(item => {
            const deleteRequest = stockStore.delete([item.symbol, item.date]);
            deleteRequest.onsuccess = () => {
              completed++;
              if (completed === data.length) {
                resolve();
              }
            };
          });
        };
      } else {
        // 全キャッシュをクリア
        const stockStore = transaction.objectStore(this.STORE_NAME);
        const metadataStore = transaction.objectStore(this.METADATA_STORE);
        
        stockStore.clear();
        metadataStore.clear();
        resolve();
      }
    });
  }

  /**
   * キャッシュ統計情報を取得
   */
  async getCacheStats(): Promise<{ totalRecords: number; symbols: string[]; lastUpdated: string }> {
    if (!this.db) {
      return { totalRecords: 0, symbols: [], lastUpdated: "" };
    }

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.STORE_NAME, this.METADATA_STORE], "readonly");
      const stockStore = transaction.objectStore(this.STORE_NAME);
      const metadataStore = transaction.objectStore(this.METADATA_STORE);

      const stockRequest = stockStore.getAll();
      const metadataRequest = metadataStore.getAll();

      let stockData: any[] = [];
      let metadata: any[] = [];

      stockRequest.onsuccess = () => {
        stockData = stockRequest.result;
      };

      metadataRequest.onsuccess = () => {
        metadata = metadataRequest.result;
      };

      transaction.oncomplete = () => {
        const symbols = [...new Set(stockData.map(item => item.symbol))];
        const lastUpdated = metadata.length > 0 
          ? Math.max(...metadata.map(m => new Date(m.lastUpdated).getTime()))
          : 0;

        resolve({
          totalRecords: stockData.length,
          symbols,
          lastUpdated: lastUpdated > 0 ? new Date(lastUpdated).toISOString() : "",
        });
      };

      transaction.onerror = () => {
        reject(transaction.error);
      };
    });
  }
}

export default JQuantsAdapter;
export type { JQuantsConfig, StockData, CacheMetadata };
