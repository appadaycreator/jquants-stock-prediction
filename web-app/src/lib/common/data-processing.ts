/**
 * 共通のデータ処理ユーティリティ
 * データの変換、検証、正規化を統一
 */

export interface DataProcessingConfig {
  enableValidation: boolean;
  enableNormalization: boolean;
  enableCaching: boolean;
  cacheTimeout: number;
}

export interface ProcessingResult<T> {
  data: T;
  isValid: boolean;
  errors: string[];
  warnings: string[];
  metadata: {
    processedAt: string;
    processingTime: number;
    cacheHit?: boolean;
  };
}

export class DataProcessor<T> {
  private config: DataProcessingConfig;
  private cache = new Map<string, { data: T; timestamp: number }>();
  private validators: Array<(data: any) => string[]> = [];
  private normalizers: Array<(data: any) => any> = [];

  constructor(config: Partial<DataProcessingConfig> = {}) {
    this.config = {
      enableValidation: true,
      enableNormalization: true,
      enableCaching: true,
      cacheTimeout: 300000, // 5分
      ...config,
    };
  }

  addValidator(validator: (data: any) => string[]): this {
    this.validators.push(validator);
    return this;
  }

  addNormalizer(normalizer: (data: any) => any): this {
    this.normalizers.push(normalizer);
    return this;
  }

  async process(data: any, cacheKey?: string): Promise<ProcessingResult<T>> {
    const startTime = Date.now();
    const processedAt = new Date().toISOString();
    
    // キャッシュチェック
    if (this.config.enableCaching && cacheKey) {
      const cached = this.cache.get(cacheKey);
      if (cached && Date.now() - cached.timestamp < this.config.cacheTimeout) {
        return {
          data: cached.data,
          isValid: true,
          errors: [],
          warnings: [],
          metadata: {
            processedAt,
            processingTime: Date.now() - startTime,
            cacheHit: true,
          },
        };
      }
    }

    let processedData = data;
    const errors: string[] = [];
    const warnings: string[] = [];

    // 正規化
    if (this.config.enableNormalization) {
      for (const normalizer of this.normalizers) {
        try {
          processedData = normalizer(processedData);
        } catch (error) {
          warnings.push(`Normalization warning: ${error instanceof Error ? error.message : "Unknown error"}`);
        }
      }
    }

    // 検証
    if (this.config.enableValidation) {
      for (const validator of this.validators) {
        try {
          const validationErrors = validator(processedData);
          errors.push(...validationErrors);
        } catch (error) {
          errors.push(`Validation error: ${error instanceof Error ? error.message : "Unknown error"}`);
        }
      }
    }

    const result: ProcessingResult<T> = {
      data: processedData as T,
      isValid: errors.length === 0,
      errors,
      warnings,
      metadata: {
        processedAt,
        processingTime: Date.now() - startTime,
      },
    };

    // キャッシュ保存
    if (this.config.enableCaching && cacheKey && result.isValid) {
      this.cache.set(cacheKey, {
        data: result.data,
        timestamp: Date.now(),
      });
    }

    return result;
  }

  clearCache(): void {
    this.cache.clear();
  }

  getCacheStats(): { size: number; keys: string[] } {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys()),
    };
  }
}

// 共通のバリデーター
export const commonValidators = {
  required: (field: string) => (data: any) => {
    if (data[field] === null || data[field] === undefined || data[field] === "") {
      return [`${field} is required`];
    }
    return [];
  },

  number: (field: string, min?: number, max?: number) => (data: any) => {
    const value = data[field];
    if (value === null || value === undefined) return [];
    
    const num = Number(value);
    if (isNaN(num)) {
      return [`${field} must be a number`];
    }
    
    const errors: string[] = [];
    if (min !== undefined && num < min) {
      errors.push(`${field} must be at least ${min}`);
    }
    if (max !== undefined && num > max) {
      errors.push(`${field} must be at most ${max}`);
    }
    return errors;
  },

  string: (field: string, minLength?: number, maxLength?: number) => (data: any) => {
    const value = data[field];
    if (value === null || value === undefined) return [];
    
    if (typeof value !== "string") {
      return [`${field} must be a string`];
    }
    
    const errors: string[] = [];
    if (minLength !== undefined && value.length < minLength) {
      errors.push(`${field} must be at least ${minLength} characters`);
    }
    if (maxLength !== undefined && value.length > maxLength) {
      errors.push(`${field} must be at most ${maxLength} characters`);
    }
    return errors;
  },

  array: (field: string, minItems?: number, maxItems?: number) => (data: any) => {
    const value = data[field];
    if (value === null || value === undefined) return [];
    
    if (!Array.isArray(value)) {
      return [`${field} must be an array`];
    }
    
    const errors: string[] = [];
    if (minItems !== undefined && value.length < minItems) {
      errors.push(`${field} must have at least ${minItems} items`);
    }
    if (maxItems !== undefined && value.length > maxItems) {
      errors.push(`${field} must have at most ${maxItems} items`);
    }
    return errors;
  },
};

// 共通のノーマライザー
export const commonNormalizers = {
  trimStrings: (data: any) => {
    if (typeof data === "object" && data !== null) {
      const normalized = { ...data };
      for (const key in normalized) {
        if (typeof normalized[key] === "string") {
          normalized[key] = normalized[key].trim();
        }
      }
      return normalized;
    }
    return data;
  },

  convertNumbers: (data: any) => {
    if (typeof data === "object" && data !== null) {
      const normalized = { ...data };
      for (const key in normalized) {
        if (typeof normalized[key] === "string" && !isNaN(Number(normalized[key]))) {
          normalized[key] = Number(normalized[key]);
        }
      }
      return normalized;
    }
    return data;
  },

  removeNulls: (data: any) => {
    if (typeof data === "object" && data !== null) {
      const normalized: any = {};
      for (const key in data) {
        if (data[key] !== null && data[key] !== undefined) {
          normalized[key] = data[key];
        }
      }
      return normalized;
    }
    return data;
  },
};

// 株価データ専用のプロセッサー
export class StockDataProcessor extends DataProcessor<any> {
  constructor() {
    super({
      enableValidation: true,
      enableNormalization: true,
      enableCaching: true,
      cacheTimeout: 600000, // 10分
    });

    // 株価データ用のバリデーター
    this.addValidator(commonValidators.required("symbol"))
      .addValidator(commonValidators.required("price"))
      .addValidator(commonValidators.number("price", 0))
      .addValidator(commonValidators.string("symbol", 1, 10));

    // 株価データ用のノーマライザー
    this.addNormalizer(commonNormalizers.trimStrings)
      .addNormalizer(commonNormalizers.convertNumbers)
      .addNormalizer(commonNormalizers.removeNulls);
  }
}

// 予測データ専用のプロセッサー
export class PredictionDataProcessor extends DataProcessor<any> {
  constructor() {
    super({
      enableValidation: true,
      enableNormalization: true,
      enableCaching: true,
      cacheTimeout: 300000, // 5分
    });

    // 予測データ用のバリデーター
    this.addValidator(commonValidators.required("date"))
      .addValidator(commonValidators.required("symbol"))
      .addValidator(commonValidators.required("y_true"))
      .addValidator(commonValidators.required("y_pred"))
      .addValidator(commonValidators.number("y_true", 0))
      .addValidator(commonValidators.number("y_pred", 0));

    // 予測データ用のノーマライザー
    this.addNormalizer(commonNormalizers.trimStrings)
      .addNormalizer(commonNormalizers.convertNumbers)
      .addNormalizer(commonNormalizers.removeNulls);
  }
}

export const stockDataProcessor = new StockDataProcessor();
export const predictionDataProcessor = new PredictionDataProcessor();
