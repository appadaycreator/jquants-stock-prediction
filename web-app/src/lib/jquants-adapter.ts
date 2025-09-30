/**
 * J-Quants API アダプタ
 * BYOトークン対応、IndexedDBキャッシュ、差分更新機能
 */

interface JQuantsConfig {
  token: string;
  baseUrl: string;
  timeout: number;
  maxRetries?: number;
  retryDelay?: number;
  rateLimitDelay?: number;
}

interface RetryConfig {
  maxRetries: number;
  baseDelay: number;
  maxDelay: number;
  backoffMultiplier: number;
}

interface RateLimitInfo {
  remaining: number;
  resetTime: number;
  retryAfter?: number;
}

interface DataValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  qualityScore: number;
}

interface DataQualityReport {
  totalRecords: number;
  validRecords: number;
  invalidRecords: number;
  qualityScore: number;
  errors: Array<{
    type: string;
    count: number;
    examples: string[];
  }>;
  timestamp: string;
}

interface CacheStrategy {
  ttl: number; // Time to live in milliseconds
  maxSize: number; // Maximum cache size in MB
  compressionEnabled: boolean;
  autoInvalidation: boolean;
}

interface CacheMetrics {
  hitRate: number;
  missRate: number;
  totalRequests: number;
  cacheSize: number;
  lastCleanup: string;
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
  private readonly DB_NAME = 'jquants_cache';
  private readonly DB_VERSION = 1;
  private readonly STORE_NAME = 'stock_data';
  private readonly METADATA_STORE = 'metadata';
  private rateLimitInfo: RateLimitInfo | null = null;
  private requestQueue: Array<() => Promise<any>> = [];
  private isProcessingQueue = false;
  private cacheStrategy: CacheStrategy;
  private cacheMetrics: CacheMetrics;

  constructor(config: JQuantsConfig) {
    this.config = {
      maxRetries: 3,
      retryDelay: 1000,
      rateLimitDelay: 100,
      ...config
    };
    
    // キャッシュ戦略の初期化
    this.cacheStrategy = {
      ttl: 24 * 60 * 60 * 1000, // 24時間
      maxSize: 100, // 100MB
      compressionEnabled: true,
      autoInvalidation: true
    };
    
    // キャッシュメトリクスの初期化
    this.cacheMetrics = {
      hitRate: 0,
      missRate: 0,
      totalRequests: 0,
      cacheSize: 0,
      lastCleanup: new Date().toISOString()
    };
    
    this.initDB();
  }

  /**
   * IndexedDBの初期化
   */
  private async initDB(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.DB_NAME, this.DB_VERSION);
      
      request.onerror = () => {
        console.error('IndexedDB初期化エラー:', request.error);
        reject(request.error);
      };
      
      request.onsuccess = () => {
        this.db = request.result;
        console.info('IndexedDB初期化完了');
        resolve();
      };
      
      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        
        // 株価データストア
        if (!db.objectStoreNames.contains(this.STORE_NAME)) {
          const stockStore = db.createObjectStore(this.STORE_NAME, { keyPath: ['symbol', 'date'] });
          stockStore.createIndex('symbol', 'symbol', { unique: false });
          stockStore.createIndex('date', 'date', { unique: false });
        }
        
        // メタデータストア
        if (!db.objectStoreNames.contains(this.METADATA_STORE)) {
          db.createObjectStore(this.METADATA_STORE, { keyPath: 'symbol' });
        }
      };
    });
  }

  /**
   * 強化されたAPIリクエスト（リトライ、レート制限対応）
   */
  private async makeRequest<T>(
    url: string, 
    options: RequestInit = {},
    retryConfig?: RetryConfig
  ): Promise<T> {
    const config = retryConfig || {
      maxRetries: this.config.maxRetries || 3,
      baseDelay: this.config.retryDelay || 1000,
      maxDelay: 30000,
      backoffMultiplier: 2
    };

    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= config.maxRetries; attempt++) {
      try {
        // レート制限チェック
        await this.checkRateLimit();

        const response = await fetch(url, {
          ...options,
          headers: {
            'Authorization': `Bearer ${this.config.token}`,
            'Content-Type': 'application/json',
            ...options.headers,
          },
          signal: AbortSignal.timeout(this.config.timeout),
        });

        // レート制限情報を更新
        this.updateRateLimitInfo(response);

        if (response.ok) {
          return await response.json();
        }

        // レート制限エラーの場合
        if (response.status === 429) {
          const retryAfter = response.headers.get('Retry-After');
          if (retryAfter) {
            await this.delay(parseInt(retryAfter) * 1000);
            continue;
          }
        }

        // サーバーエラーの場合
        if (response.status >= 500 && attempt < config.maxRetries) {
          const delay = Math.min(
            config.baseDelay * Math.pow(config.backoffMultiplier, attempt),
            config.maxDelay
          );
          await this.delay(delay);
          continue;
        }

        throw new Error(`HTTP ${response.status}: ${response.statusText}`);

      } catch (error) {
        lastError = error instanceof Error ? error : new Error('Unknown error');
        
        if (attempt < config.maxRetries) {
          const delay = Math.min(
            config.baseDelay * Math.pow(config.backoffMultiplier, attempt),
            config.maxDelay
          );
          console.warn(`APIリクエスト失敗 (試行 ${attempt + 1}/${config.maxRetries + 1}):`, lastError.message);
          await this.delay(delay);
        }
      }
    }

    throw lastError || new Error('Max retries exceeded');
  }

  /**
   * レート制限チェック
   */
  private async checkRateLimit(): Promise<void> {
    if (!this.rateLimitInfo) return;

    const now = Date.now();
    if (this.rateLimitInfo.remaining <= 0 && now < this.rateLimitInfo.resetTime) {
      const waitTime = this.rateLimitInfo.resetTime - now;
      console.warn(`レート制限により待機: ${waitTime}ms`);
      await this.delay(waitTime);
    }
  }

  /**
   * レート制限情報の更新
   */
  private updateRateLimitInfo(response: Response): void {
    const remaining = response.headers.get('X-RateLimit-Remaining');
    const reset = response.headers.get('X-RateLimit-Reset');
    
    if (remaining && reset) {
      this.rateLimitInfo = {
        remaining: parseInt(remaining),
        resetTime: parseInt(reset) * 1000
      };
    }
  }

  /**
   * 遅延実行
   */
  private async delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * 全銘柄一覧の取得（コード・名称・セクター）
   * 失敗時は空配列を返す
   */
  async getAllSymbols(): Promise<Array<{ code: string; name: string; sector?: string }>> {
    try {
      const data = await this.makeRequest<any>(`${this.config.baseUrl}/markets/stock/list`);
      const list: any[] = data?.data || [];
      return list.map((item: any) => ({
        code: item?.Code || item?.code,
        name: item?.CompanyName || item?.name || item?.CompanyNameJa || item?.CompanyNameJp || item?.CompanyNameJPN,
        sector: item?.Sector33 || item?.SectorName || item?.sector,
      })).filter((s: any) => !!s.code && !!s.name);
    } catch (error) {
      console.error('全銘柄一覧取得エラー:', error);
      return [];
    }
  }

  /**
   * トークン接続テスト
   */
  async testConnection(): Promise<{ success: boolean; message: string }> {
    try {
      console.info('J-Quants接続テスト開始');
      
      const data = await this.makeRequest<any>(`${this.config.baseUrl}/markets/stock/list`);
      console.info('J-Quants接続テスト成功', { 
        dataCount: data?.data?.length || 0 
      });

      return {
        success: true,
        message: `接続成功: ${data?.data?.length || 0}件の銘柄データを取得`
      };
    } catch (error) {
      console.error('J-Quants接続テスト失敗:', error);
      return {
        success: false,
        message: `接続失敗: ${error instanceof Error ? error.message : '不明なエラー'}`
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
    useCache: boolean = true
  ): Promise<StockData[]> {
    try {
      console.info('株価データ取得開始', { symbol, startDate, endDate, useCache });

      // キャッシュから取得を試行
      if (useCache) {
        const cachedData = await this.getCachedData(symbol, startDate, endDate);
        if (cachedData.length > 0) {
          console.info('キャッシュからデータ取得', { 
            symbol, 
            count: cachedData.length,
            dateRange: `${startDate} - ${endDate}`
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

      console.info('APIからデータ取得完了', { 
        symbol, 
        count: apiData.length 
      });

      return apiData;
    } catch (error) {
      console.error('株価データ取得エラー:', error);
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
      const sevenDaysAgoStr = sevenDaysAgo.toISOString().split('T')[0];
      const todayStr = today.toISOString().split('T')[0];

      console.info('差分更新開始', { symbol, dateRange: `${sevenDaysAgoStr} - ${todayStr}` });

      // 直近7日を常時再取得
      const recentData = await this.getStockData(symbol, sevenDaysAgoStr, todayStr, false);
      
      // 既存のキャッシュデータとマージ
      const existingData = await this.getCachedData(symbol, '2020-01-01', sevenDaysAgoStr);
      const mergedData = [...existingData, ...recentData].sort((a, b) => 
        new Date(a.date).getTime() - new Date(b.date).getTime()
      );

      // キャッシュを更新
      await this.saveToCache(symbol, mergedData, '2020-01-01', todayStr);

      console.info('差分更新完了', { 
        symbol, 
        totalCount: mergedData.length,
        newCount: recentData.length 
      });

      return mergedData;
    } catch (error) {
      console.error('差分更新エラー:', error);
      throw error;
    }
  }

  /**
   * APIから直接データを取得
   */
  private async fetchFromAPI(symbol: string, startDate: string, endDate: string): Promise<StockData[]> {
    const data = await this.makeRequest<any>(`${this.config.baseUrl}/markets/daily_quotes`);
    return this.transformAPIResponse(data, symbol);
  }

  /**
   * データ検証システム
   */
  private validateStockData(data: StockData[]): DataValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    let qualityScore = 100;

    for (let i = 0; i < data.length; i++) {
      const item = data[i];
      const recordIndex = i + 1;

      // 必須フィールドの検証
      if (!item.date || !item.code) {
        errors.push(`レコード${recordIndex}: 必須フィールド（date, code）が不足`);
        qualityScore -= 20;
        continue;
      }

      // 日付形式の検証
      if (!/^\d{4}-\d{2}-\d{2}$/.test(item.date)) {
        errors.push(`レコード${recordIndex}: 日付形式が無効 (${item.date})`);
        qualityScore -= 15;
      }

      // 数値フィールドの検証
      const numericFields = ['open', 'high', 'low', 'close', 'volume'];
      for (const field of numericFields) {
        const value = item[field as keyof StockData];
        if (typeof value !== 'number' || isNaN(value)) {
          errors.push(`レコード${recordIndex}: ${field}が無効な数値 (${value})`);
          qualityScore -= 10;
        }
      }

      // 価格データの論理検証
      if (item.high < item.low) {
        errors.push(`レコード${recordIndex}: 高値が安値を下回っています`);
        qualityScore -= 15;
      }

      if (item.high < item.open || item.high < item.close) {
        warnings.push(`レコード${recordIndex}: 高値が始値・終値を下回っています`);
        qualityScore -= 5;
      }

      if (item.low > item.open || item.low > item.close) {
        warnings.push(`レコード${recordIndex}: 安値が始値・終値を上回っています`);
        qualityScore -= 5;
      }

      // 異常値の検出
      if (item.volume < 0) {
        errors.push(`レコード${recordIndex}: 出来高が負の値です`);
        qualityScore -= 20;
      }

      // 極端な価格変動の検出
      if (i > 0) {
        const prevItem = data[i - 1];
        const priceChange = Math.abs(item.close - prevItem.close) / prevItem.close;
        if (priceChange > 0.3) { // 30%以上の変動
          warnings.push(`レコード${recordIndex}: 極端な価格変動を検出 (${(priceChange * 100).toFixed(1)}%)`);
          qualityScore -= 5;
        }
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      qualityScore: Math.max(0, qualityScore)
    };
  }

  /**
   * データ品質レポートの生成
   */
  private generateQualityReport(data: StockData[], validationResult: DataValidationResult): DataQualityReport {
    const errorTypes = new Map<string, { count: number; examples: string[] }>();
    
    validationResult.errors.forEach(error => {
      const type = error.split(':')[0];
      if (!errorTypes.has(type)) {
        errorTypes.set(type, { count: 0, examples: [] });
      }
      const entry = errorTypes.get(type)!;
      entry.count++;
      if (entry.examples.length < 3) {
        entry.examples.push(error);
      }
    });

    return {
      totalRecords: data.length,
      validRecords: data.length - validationResult.errors.length,
      invalidRecords: validationResult.errors.length,
      qualityScore: validationResult.qualityScore,
      errors: Array.from(errorTypes.entries()).map(([type, info]) => ({
        type,
        count: info.count,
        examples: info.examples
      })),
      timestamp: new Date().toISOString()
    };
  }

  /**
   * APIレスポンスをStockData形式に変換（検証付き）
   */
  private transformAPIResponse(apiData: any, symbol: string): StockData[] {
    if (!apiData?.data) {
      return [];
    }

    const rawData = apiData.data
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

    // データ検証を実行
    const validationResult = this.validateStockData(rawData);
    
    if (!validationResult.isValid) {
      console.warn('データ品質の問題を検出:', {
        errors: validationResult.errors,
        warnings: validationResult.warnings,
        qualityScore: validationResult.qualityScore
      });
    }

    // 品質レポートを生成（開発環境でのみ）
    if (process.env.NODE_ENV === 'development') {
      const qualityReport = this.generateQualityReport(rawData, validationResult);
      console.info('データ品質レポート:', qualityReport);
    }

    return rawData;
  }

  /**
   * 強化されたキャッシュ取得（TTL、圧縮対応）
   */
  private async getCachedData(symbol: string, startDate: string, endDate: string): Promise<StockData[]> {
    if (!this.db) {
      this.cacheMetrics.missRate++;
      return [];
    }

    this.cacheMetrics.totalRequests++;

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.STORE_NAME, this.METADATA_STORE], 'readonly');
      const store = transaction.objectStore(this.STORE_NAME);
      const metadataStore = transaction.objectStore(this.METADATA_STORE);
      const index = store.index('symbol');
      const request = index.getAll(symbol);
      const metadataRequest = metadataStore.get(symbol);

      let allData: StockData[] = [];
      let metadata: CacheMetadata | null = null;

      request.onsuccess = () => {
        allData = request.result;
      };

      metadataRequest.onsuccess = () => {
        metadata = metadataRequest.result;
      };

      transaction.oncomplete = () => {
        // TTLチェック
        if (metadata && this.isCacheExpired(metadata)) {
          console.info('キャッシュが期限切れのため無効化', { symbol, lastUpdated: metadata.lastUpdated });
          this.cacheMetrics.missRate++;
          resolve([]);
          return;
        }

        // データフィルタリング
        const filteredData = allData.filter(item => 
          item.date >= startDate && item.date <= endDate
        );

        if (filteredData.length > 0) {
          this.cacheMetrics.hitRate++;
          console.info('キャッシュヒット', { 
            symbol, 
            count: filteredData.length,
            dateRange: `${startDate} - ${endDate}`
          });
        } else {
          this.cacheMetrics.missRate++;
        }

        resolve(filteredData);
      };

      transaction.onerror = () => {
        console.error('キャッシュ取得エラー:', transaction.error);
        this.cacheMetrics.missRate++;
        reject(transaction.error);
      };
    });
  }

  /**
   * キャッシュの有効期限チェック
   */
  private isCacheExpired(metadata: CacheMetadata): boolean {
    const now = new Date().getTime();
    const lastUpdated = new Date(metadata.lastUpdated).getTime();
    return (now - lastUpdated) > this.cacheStrategy.ttl;
  }

  /**
   * キャッシュサイズの計算
   */
  private calculateCacheSize(data: StockData[]): number {
    const jsonString = JSON.stringify(data);
    return new Blob([jsonString]).size / (1024 * 1024); // MB単位
  }

  /**
   * 自動キャッシュクリーンアップ
   */
  private async performCacheCleanup(): Promise<void> {
    if (!this.db) return;

    try {
      const transaction = this.db.transaction([this.STORE_NAME, this.METADATA_STORE], 'readwrite');
      const store = transaction.objectStore(this.STORE_NAME);
      const metadataStore = transaction.objectStore(this.METADATA_STORE);
      
      // 期限切れデータの削除
      const metadataRequest = metadataStore.getAll();
      
      metadataRequest.onsuccess = () => {
        const allMetadata = metadataRequest.result;
        const expiredSymbols = allMetadata
          .filter(meta => this.isCacheExpired(meta))
          .map(meta => meta.symbol);

        if (expiredSymbols.length > 0) {
          console.info('期限切れキャッシュの削除', { count: expiredSymbols.length });
          
          expiredSymbols.forEach(symbol => {
            const index = store.index('symbol');
            const deleteRequest = index.getAll(symbol);
            
            deleteRequest.onsuccess = () => {
              const dataToDelete = deleteRequest.result;
              dataToDelete.forEach(item => {
                store.delete([item.symbol, item.date]);
              });
            };
          });
        }
      };

      this.cacheMetrics.lastCleanup = new Date().toISOString();
    } catch (error) {
      console.error('キャッシュクリーンアップエラー:', error);
    }
  }

  /**
   * 強化されたキャッシュ保存（サイズ制限、圧縮対応）
   */
  private async saveToCache(symbol: string, data: StockData[], startDate: string, endDate: string): Promise<void> {
    if (!this.db || data.length === 0) {
      return;
    }

    // キャッシュサイズチェック
    const dataSize = this.calculateCacheSize(data);
    if (dataSize > this.cacheStrategy.maxSize) {
      console.warn('キャッシュサイズが上限を超過', { 
        size: dataSize, 
        maxSize: this.cacheStrategy.maxSize 
      });
      await this.performCacheCleanup();
    }

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.STORE_NAME, this.METADATA_STORE], 'readwrite');
      
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
            // キャッシュメトリクス更新
            this.cacheMetrics.cacheSize += dataSize;
            resolve();
          }
        };
        request.onerror = () => {
          console.error('キャッシュ保存エラー:', request.error);
          reject(request.error);
        };
      });

      // メタデータを保存
      const metadata: CacheMetadata = {
        lastUpdated: new Date().toISOString(),
        dataVersion: '1.0',
        symbol,
        dateRange: { start: startDate, end: endDate }
      };

      const metadataRequest = metadataStore.put(metadata);
      metadataRequest.onsuccess = () => {
        completed++;
        if (completed === total) {
          resolve();
        }
      };
      metadataRequest.onerror = () => {
        console.error('メタデータ保存エラー:', metadataRequest.error);
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
      const transaction = this.db!.transaction([this.STORE_NAME, this.METADATA_STORE], 'readwrite');
      
      if (symbol) {
        // 特定銘柄のキャッシュをクリア
        const stockStore = transaction.objectStore(this.STORE_NAME);
        const index = stockStore.index('symbol');
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
   * 強化されたキャッシュ統計情報を取得
   */
  async getCacheStats(): Promise<{ 
    totalRecords: number; 
    symbols: string[]; 
    lastUpdated: string;
    metrics: CacheMetrics;
    strategy: CacheStrategy;
  }> {
    if (!this.db) {
      return { 
        totalRecords: 0, 
        symbols: [], 
        lastUpdated: '',
        metrics: this.cacheMetrics,
        strategy: this.cacheStrategy
      };
    }

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.STORE_NAME, this.METADATA_STORE], 'readonly');
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

        // メトリクス計算
        const totalRequests = this.cacheMetrics.totalRequests;
        const hitRate = totalRequests > 0 ? (this.cacheMetrics.hitRate / totalRequests) * 100 : 0;
        const missRate = totalRequests > 0 ? (this.cacheMetrics.missRate / totalRequests) * 100 : 0;

        const updatedMetrics: CacheMetrics = {
          ...this.cacheMetrics,
          hitRate,
          missRate
        };

        resolve({
          totalRecords: stockData.length,
          symbols,
          lastUpdated: lastUpdated > 0 ? new Date(lastUpdated).toISOString() : '',
          metrics: updatedMetrics,
          strategy: this.cacheStrategy
        });
      };

      transaction.onerror = () => {
        reject(transaction.error);
      };
    });
  }

  /**
   * キャッシュ戦略の更新
   */
  updateCacheStrategy(newStrategy: Partial<CacheStrategy>): void {
    this.cacheStrategy = { ...this.cacheStrategy, ...newStrategy };
    console.info('キャッシュ戦略を更新', this.cacheStrategy);
  }

  /**
   * 自動キャッシュクリーンアップの実行
   */
  async runCacheCleanup(): Promise<void> {
    console.info('手動キャッシュクリーンアップを実行');
    await this.performCacheCleanup();
  }
}

export default JQuantsAdapter;
export type { 
  JQuantsConfig, 
  StockData, 
  CacheMetadata, 
  DataValidationResult, 
  DataQualityReport,
  CacheStrategy,
  CacheMetrics,
  RetryConfig,
  RateLimitInfo
};
