/**
 * サンプルデータバリデーター
 * データ構造の検証とエラーハンドリング
 */

import { 
  SampleDailyQuotesData, 
  SampleListedData, 
  DailyQuote, 
  ListedStock,
  SampleDataError, 
} from "../types/sample-data";

export class SampleDataValidator {
  /**
   * 日足データのバリデーション
   */
  static validateDailyQuotes(data: any): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!data) {
      errors.push("データがnullまたはundefinedです");
      return { isValid: false, errors };
    }

    if (!data.daily_quotes) {
      errors.push("daily_quotesフィールドが存在しません");
    } else if (!Array.isArray(data.daily_quotes)) {
      errors.push("daily_quotesは配列である必要があります");
    } else {
      // 各日足データのバリデーション
      data.daily_quotes.forEach((quote: any, index: number) => {
        const quoteErrors = this.validateDailyQuote(quote);
        if (quoteErrors.length > 0) {
          errors.push(`日足データ[${index}]: ${quoteErrors.join(", ")}`);
        }
      });
    }

    if (!data.metadata) {
      errors.push("metadataフィールドが存在しません");
    } else {
      const metadataErrors = this.validateMetadata(data.metadata);
      if (metadataErrors.length > 0) {
        errors.push(`メタデータ: ${metadataErrors.join(", ")}`);
      }
    }

    return { isValid: errors.length === 0, errors };
  }

  /**
   * 上場銘柄データのバリデーション
   */
  static validateListedData(data: any): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!data) {
      errors.push("データがnullまたはundefinedです");
      return { isValid: false, errors };
    }

    if (!data.listed_data) {
      errors.push("listed_dataフィールドが存在しません");
    } else if (!Array.isArray(data.listed_data)) {
      errors.push("listed_dataは配列である必要があります");
    } else {
      // 各上場銘柄データのバリデーション
      data.listed_data.forEach((stock: any, index: number) => {
        const stockErrors = this.validateListedStock(stock);
        if (stockErrors.length > 0) {
          errors.push(`上場銘柄データ[${index}]: ${stockErrors.join(", ")}`);
        }
      });
    }

    if (!data.metadata) {
      errors.push("metadataフィールドが存在しません");
    } else {
      const metadataErrors = this.validateMetadata(data.metadata);
      if (metadataErrors.length > 0) {
        errors.push(`メタデータ: ${metadataErrors.join(", ")}`);
      }
    }

    return { isValid: errors.length === 0, errors };
  }

  /**
   * 個別日足データのバリデーション
   */
  private static validateDailyQuote(quote: any): string[] {
    const errors: string[] = [];
    const requiredFields = [
      "code", "name", "sector", "date", "open", "high", "low", "close", 
      "volume", "turnover_value", "change_percent", "timestamp",
    ];

    requiredFields.forEach(field => {
      if (quote[field] === undefined || quote[field] === null) {
        errors.push(`${field}フィールドが必須です`);
      }
    });

    // 数値フィールドの検証
    const numericFields = ["open", "high", "low", "close", "volume", "turnover_value", "change_percent"];
    numericFields.forEach(field => {
      if (quote[field] !== undefined && typeof quote[field] !== "number") {
        errors.push(`${field}は数値である必要があります`);
      }
    });

    // 文字列フィールドの検証
    const stringFields = ["code", "name", "sector", "date", "timestamp"];
    stringFields.forEach(field => {
      if (quote[field] !== undefined && typeof quote[field] !== "string") {
        errors.push(`${field}は文字列である必要があります`);
      }
    });

    // 日付形式の検証
    if (quote.date && !this.isValidDate(quote.date)) {
      errors.push("dateは有効な日付形式である必要があります");
    }

    if (quote.timestamp && !this.isValidTimestamp(quote.timestamp)) {
      errors.push("timestampは有効なISO形式である必要があります");
    }

    return errors;
  }

  /**
   * 個別上場銘柄データのバリデーション
   */
  private static validateListedStock(stock: any): string[] {
    const errors: string[] = [];
    const requiredFields = [
      "code", "name", "market", "sector17_code", "sector17_name",
      "sector33_code", "sector33_name", "scale_code", "scale_name",
      "listing_date",
    ];

    requiredFields.forEach(field => {
      if (stock[field] === undefined || stock[field] === null) {
        errors.push(`${field}フィールドが必須です`);
      }
    });

    // 文字列フィールドの検証
    const stringFields = [
      "code", "name", "market", "sector17_code", "sector17_name",
      "sector33_code", "sector33_name", "scale_code", "scale_name",
      "listing_date",
    ];
    stringFields.forEach(field => {
      if (stock[field] !== undefined && typeof stock[field] !== "string") {
        errors.push(`${field}は文字列である必要があります`);
      }
    });

    // 日付形式の検証
    if (stock.listing_date && !this.isValidDate(stock.listing_date)) {
      errors.push("listing_dateは有効な日付形式である必要があります");
    }

    if (stock.close_date && stock.close_date !== null && !this.isValidDate(stock.close_date)) {
      errors.push("close_dateは有効な日付形式またはnullである必要があります");
    }

    return errors;
  }

  /**
   * メタデータのバリデーション
   */
  private static validateMetadata(metadata: any): string[] {
    const errors: string[] = [];
    const requiredFields = ["generated_at", "type", "ttl", "version"];

    requiredFields.forEach(field => {
      if (metadata[field] === undefined || metadata[field] === null) {
        errors.push(`メタデータの${field}フィールドが必須です`);
      }
    });

    if (metadata.generated_at && !this.isValidTimestamp(metadata.generated_at)) {
      errors.push("generated_atは有効なISO形式である必要があります");
    }

    return errors;
  }

  /**
   * 日付形式の検証
   */
  private static isValidDate(dateString: string): boolean {
    const date = new Date(dateString);
    return !isNaN(date.getTime()) && dateString.match(/^\d{4}-\d{2}-\d{2}$/);
  }

  /**
   * タイムスタンプ形式の検証
   */
  private static isValidTimestamp(timestamp: string): boolean {
    const date = new Date(timestamp);
    return !isNaN(date.getTime()) && timestamp.includes("T");
  }

  /**
   * エラーレポートの生成
   */
  static generateErrorReport(errors: string[]): SampleDataError {
    return {
      type: "parse",
      message: `データバリデーションエラー: ${errors.join("; ")}`,
      timestamp: new Date().toISOString(),
      fallbackUsed: true,
    };
  }
}
