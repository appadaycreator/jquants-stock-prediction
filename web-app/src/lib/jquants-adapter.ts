/**
 * J-Quants API アダプタ
 * BYOトークン対応、IndexedDBキャッシュ、差分更新機能
 */

interface JQuantsConfig {
  token: string;
  baseUrl: string;
  timeout: number;
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
  private readonly DB_NAME = "jquants_cache";
  private readonly DB_VERSION = 1;
  private readonly STORE_NAME = "stock_data";
  private readonly METADATA_STORE = "metadata";

  constructor(config: JQuantsConfig) {
    this.config = config;
    this.initDB();
  }

  /**
   * IndexedDBの初期化
   */
  private async initDB(): Promise<void> {
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
   * 全銘柄一覧の取得（コード・名称・セクター）
   * 失敗時は空配列を返す
   */
  async getAllSymbols(): Promise<Array<{ code: string; name: string; sector?: string }>> {
    try {
      const response = await fetch(`${this.config.baseUrl}/markets/stock/list`, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${this.config.token}`,
          "Content-Type": "application/json",
        },
        signal: AbortSignal.timeout(this.config.timeout),
      });

      if (!response.ok) {
        console.error("全銘柄一覧取得失敗", response.status, response.statusText);
        return [];
      }

      const data = await response.json();
      const list: any[] = data?.data || [];
      return list.map((item: any) => ({
        code: item?.Code || item?.code,
        name: item?.CompanyName || item?.name || item?.CompanyNameJa || item?.CompanyNameJp || item?.CompanyNameJPN,
        sector: item?.Sector33 || item?.SectorName || item?.sector,
      })).filter((s: any) => !!s.code && !!s.name);
    } catch (error) {
      console.error("全銘柄一覧取得エラー:", error);
      return [];
    }
  }

  /**
   * トークン接続テスト
   */
  async testConnection(): Promise<{ success: boolean; message: string }> {
    try {
      console.info("J-Quants接続テスト開始");
      
      const response = await fetch(`${this.config.baseUrl}/markets/stock/list`, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${this.config.token}`,
          "Content-Type": "application/json",
        },
        signal: AbortSignal.timeout(this.config.timeout),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.info("J-Quants接続テスト成功", { 
        status: response.status,
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
   */
  async getIncrementalData(symbol: string): Promise<StockData[]> {
    try {
      const today = new Date();
      const sevenDaysAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
      const sevenDaysAgoStr = sevenDaysAgo.toISOString().split("T")[0];
      const todayStr = today.toISOString().split("T")[0];

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
    const response = await fetch(`${this.config.baseUrl}/markets/daily_quotes`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${this.config.token}`,
        "Content-Type": "application/json",
      },
      signal: AbortSignal.timeout(this.config.timeout),
    });

    if (!response.ok) {
      throw new Error(`API取得失敗: HTTP ${response.status}`);
    }

    const data = await response.json();
    return this.transformAPIResponse(data, symbol);
  }

  /**
   * APIレスポンスをStockData形式に変換
   */
  private transformAPIResponse(apiData: any, symbol: string): StockData[] {
    if (!apiData?.data) {
      return [];
    }

    return apiData.data
      .filter((item: any) => item.code === symbol)
      .map((item: any) => ({
        date: item.date,
        code: item.code,
        open: parseFloat(item.open) || 0,
        high: parseFloat(item.high) || 0,
        low: parseFloat(item.low) || 0,
        close: parseFloat(item.close) || 0,
        volume: parseInt(item.volume) || 0,
        // 技術指標は別途計算が必要
        sma_5: undefined,
        sma_10: undefined,
        sma_25: undefined,
        sma_50: undefined,
      }));
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
