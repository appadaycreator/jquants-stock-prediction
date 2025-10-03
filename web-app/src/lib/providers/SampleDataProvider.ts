/**
 * サンプルデータプロバイダー
 * フォールバック機能付きのサンプルデータ取得サービス
 */

import { 
  SampleDailyQuotesData, 
  SampleListedData, 
  SampleDataProvider as ISampleDataProvider,
  FallbackConfig,
  SampleDataError 
} from '../types/sample-data';

export class SampleDataProvider implements ISampleDataProvider {
  private config: FallbackConfig;

  constructor(config: Partial<FallbackConfig> = {}) {
    this.config = {
      enabled: true,
      timeout: 5000,
      retryCount: 3,
      retryDelay: 1000,
      ...config
    };
  }

  /**
   * 日足サンプルデータを取得
   */
  async getDailyQuotes(): Promise<SampleDailyQuotesData> {
    try {
      const response = await this.fetchWithTimeout('/data/sample_daily_quotes.json');
      if (response.ok) {
        const data = await response.json();
        return this.validateDailyQuotesData(data);
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      console.warn('サンプル日足データ取得エラー:', error);
      return this.generateFallbackDailyQuotes();
    }
  }

  /**
   * 上場銘柄サンプルデータを取得
   */
  async getListedData(): Promise<SampleListedData> {
    try {
      const response = await this.fetchWithTimeout('/data/sample_listed_data.json');
      if (response.ok) {
        const data = await response.json();
        return this.validateListedData(data);
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      console.warn('サンプル上場銘柄データ取得エラー:', error);
      return this.generateFallbackListedData();
    }
  }

  /**
   * サンプルデータの利用可能性をチェック
   */
  async isAvailable(): Promise<boolean> {
    try {
      const response = await this.fetchWithTimeout('/data/sample_daily_quotes.json', 2000);
      return response.ok;
    } catch {
      return false;
    }
  }

  /**
   * タイムアウト付きフェッチ
   */
  private async fetchWithTimeout(url: string, timeout: number = this.config.timeout): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
        }
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }

  /**
   * 日足データのバリデーション
   */
  private validateDailyQuotesData(data: any): SampleDailyQuotesData {
    if (!data.daily_quotes || !Array.isArray(data.daily_quotes)) {
      throw new Error('Invalid daily quotes data structure');
    }
    return data;
  }

  /**
   * 上場銘柄データのバリデーション
   */
  private validateListedData(data: any): SampleListedData {
    if (!data.listed_data || !Array.isArray(data.listed_data)) {
      throw new Error('Invalid listed data structure');
    }
    return data;
  }

  /**
   * フォールバック用日足データ生成
   */
  private generateFallbackDailyQuotes(): SampleDailyQuotesData {
    const now = new Date();
    const date = now.toISOString().split('T')[0];
    
    return {
      daily_quotes: [
        {
          code: "7203",
          name: "トヨタ自動車",
          sector: "自動車",
          date,
          open: 26787,
          high: 26886,
          low: 26676,
          close: 26755,
          volume: 1213257,
          turnover_value: 32460691035,
          adjustment_factor: 1.0,
          adjustment_open: 26710,
          adjustment_high: 26805,
          adjustment_low: 26603,
          adjustment_close: 26755,
          adjustment_volume: 1213257,
          adjustment_turnover_value: 32460691035,
          change_percent: 0.08,
          timestamp: now.toISOString()
        },
        {
          code: "6758",
          name: "ソニーグループ",
          sector: "電気機器",
          date,
          open: 48407,
          high: 48509,
          low: 48301,
          close: 48478,
          volume: 1224905,
          turnover_value: 59380944590,
          adjustment_factor: 1.0,
          adjustment_open: 48432,
          adjustment_high: 48571,
          adjustment_low: 48333,
          adjustment_close: 48478,
          adjustment_volume: 1224905,
          adjustment_turnover_value: 59380944590,
          change_percent: -0.32,
          timestamp: now.toISOString()
        }
      ],
      metadata: {
        generated_at: now.toISOString(),
        type: "daily_quotes",
        ttl: "24h",
        version: "1.0"
      }
    };
  }

  /**
   * フォールバック用上場銘柄データ生成
   */
  private generateFallbackListedData(): SampleListedData {
    const now = new Date();
    
    return {
      listed_data: [
        {
          code: "7203",
          name: "トヨタ自動車",
          market: "東証プライム",
          sector17_code: "15",
          sector17_name: "自動車",
          sector33_code: "1510",
          sector33_name: "自動車",
          scale_code: "10",
          scale_name: "大型",
          listing_date: "1949-05-16",
          close_date: null
        },
        {
          code: "6758",
          name: "ソニーグループ",
          market: "東証プライム",
          sector17_code: "9",
          sector17_name: "電気機器",
          sector33_code: "9050",
          sector33_name: "電気機器",
          scale_code: "10",
          scale_name: "大型",
          listing_date: "1958-12-23",
          close_date: null
        }
      ],
      metadata: {
        generated_at: now.toISOString(),
        type: "listed_data",
        ttl: "7d",
        version: "1.0"
      }
    };
  }
}

// シングルトンインスタンス
export const sampleDataProvider = new SampleDataProvider();
