/**
 * サンプルデータ用の統一型定義
 */

// 日足データの型定義
export interface DailyQuote {
  code: string;
  name: string;
  sector: string;
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  turnover_value: number;
  adjustment_factor: number;
  adjustment_open: number;
  adjustment_high: number;
  adjustment_low: number;
  adjustment_close: number;
  adjustment_volume: number;
  adjustment_turnover_value: number;
  change_percent: number;
  timestamp: string;
}

// 上場銘柄データの型定義
export interface ListedStock {
  code: string;
  name: string;
  market: string;
  sector17_code: string;
  sector17_name: string;
  sector33_code: string;
  sector33_name: string;
  scale_code: string;
  scale_name: string;
  listing_date: string;
  close_date: string | null;
}

// サンプルデータのメタデータ
export interface SampleDataMetadata {
  generated_at: string;
  type: string;
  ttl: string;
  version: string;
}

// 日足サンプルデータの型定義
export interface SampleDailyQuotesData {
  daily_quotes: DailyQuote[];
  metadata: SampleDataMetadata;
}

// 上場銘柄サンプルデータの型定義
export interface SampleListedData {
  listed_data: ListedStock[];
  metadata: SampleDataMetadata;
}

// フォールバック機能の型定義
export interface FallbackConfig {
  enabled: boolean;
  timeout: number;
  retryCount: number;
  retryDelay: number;
}

// サンプルデータプロバイダーの型定義
export interface SampleDataProvider {
  getDailyQuotes(): Promise<SampleDailyQuotesData>;
  getListedData(): Promise<SampleListedData>;
  isAvailable(): Promise<boolean>;
}

// エラーハンドリングの型定義
export interface SampleDataError {
  type: 'network' | 'parse' | 'not_found' | 'timeout';
  message: string;
  timestamp: string;
  fallbackUsed: boolean;
}
