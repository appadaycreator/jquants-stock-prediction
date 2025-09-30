/**
 * 統一されたデータフェッチ層
 * エラーハンドリング、リトライ、タイムアウト、AbortController対応
 */

import { useState, useEffect } from 'react';

export interface FetchOptions {
  signal?: AbortSignal;
  timeout?: number;
  retries?: number;
  retryDelay?: number;
  method?: string;
  headers?: Record<string, string>;
  json?: unknown;
  idempotencyKey?: string | true;
}

export class AppError extends Error {
  constructor(
    message: string,
    public code: string,
    public status?: number,
    public retryHint?: string
  ) {
    super(message);
    this.name = 'AppError';
  }
}

export function createIdempotencyKey(): string {
  try {
    // @ts-ignore
    const uuid = (globalThis.crypto && (globalThis.crypto as any).randomUUID?.()) || undefined;
    if (uuid) return `idem_${uuid}`;
  } catch {}
  const rand = Math.random().toString(36).slice(2);
  return `idem_${Date.now()}_${rand}`;
}

/**
 * 指数バックオフでリトライするfetchJson関数
 */
export async function fetchJson<T>(
  url: string,
  options: FetchOptions = {}
): Promise<T> {
  const resolveUrl = (input: string) => {
    try {
      // 絶対URLまたはhttp(s)はそのまま
      if (/^https?:\/\//i.test(input)) return input;
      const basePath = process.env.NODE_ENV === 'production' ? '/jquants-stock-prediction' : '';
      // 先頭が/の場合はベースパス連結
      if (input.startsWith('/')) return `${basePath}${input}`;
      return input;
    } catch {
      return input;
    }
  };

  const {
    signal,
    timeout = 10000,
    retries = 3,
    retryDelay = 1000,
    method,
    headers,
    json,
    idempotencyKey
  } = options;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  // 外部のAbortSignalと統合
  if (signal) {
    signal.addEventListener('abort', () => controller.abort());
  }

  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const baseHeaders: Record<string, string> = {
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
      };

      const hasJsonBody = typeof json !== 'undefined';
      if (hasJsonBody) {
        baseHeaders['Content-Type'] = 'application/json';
      }

      // 冪等キーを必要に応じて付与
      const finalMethod = method || (hasJsonBody ? 'POST' : 'GET');
      const shouldAttachIdem = /^(POST|PUT|PATCH|DELETE)$/i.test(finalMethod);
      const keyValue = idempotencyKey === true ? createIdempotencyKey() : (typeof idempotencyKey === 'string' ? idempotencyKey : undefined);
      if (shouldAttachIdem && keyValue) {
        baseHeaders['Idempotency-Key'] = keyValue;
      }

      const response = await fetch(resolveUrl(url), {
        signal: controller.signal,
        cache: "no-cache",
        method: finalMethod,
        headers: { ...baseHeaders, ...(headers || {}) },
        body: hasJsonBody ? JSON.stringify(json) : undefined,
      });

      clearTimeout(timeoutId);

      // ステータス検査
      if (!response.ok) {
        // 共通エラースキーマを優先して解釈
        try {
          const text = await response.text();
          const json = JSON.parse(text);
          if (json && typeof json === 'object' && json.error_code && json.user_message) {
            throw new AppError(
              json.user_message,
              String(json.error_code),
              response.status,
              json.retry_hint
            );
          }
          // JSONでない/スキーマ外の場合は従来のHTTPエラー
          throw new AppError(
            `HTTP ${response.status}: ${response.statusText}`,
            `HTTP_${response.status}`,
            response.status
          );
        } catch (parseErr) {
          if (parseErr instanceof AppError) throw parseErr;
          throw new AppError(
            `HTTP ${response.status}: ${response.statusText}`,
            `HTTP_${response.status}`,
            response.status
          );
        }
      }

      // コンテンツタイプ検査
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        throw new AppError(
          'レスポンスがJSON形式ではありません',
          'INVALID_CONTENT_TYPE'
        );
      }

      const data = await response.json();
      return data;

    } catch (error) {
      lastError = error as Error;
      
      // AbortErrorの場合は即座に終了
      if (error instanceof Error && error.name === 'AbortError') {
        throw new AppError('リクエストが中断されました', 'ABORTED');
      }

      // 最後の試行でない場合は待機
      if (attempt < retries) {
        const delay = retryDelay * Math.pow(2, attempt); // 指数バックオフ
        console.warn(`Fetch attempt ${attempt + 1} failed for ${url}:`, error);
        console.log(`Retrying in ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  // すべてのリトライが失敗した場合
  if (lastError instanceof AppError) {
    throw lastError;
  }

  throw new AppError(
    `すべてのリトライ試行が失敗しました: ${lastError?.message || 'Unknown error'}`,
    'ALL_RETRIES_FAILED'
  );
}

/**
 * 複数のデータを並列取得
 */
export async function fetchMultiple<T extends Record<string, any>>(
  requests: Record<keyof T, string>,
  options: FetchOptions = {}
): Promise<T> {
  const results = {} as T;
  const errors: string[] = [];

  const promises = Object.entries(requests).map(async ([key, url]) => {
    try {
      const data = await fetchJson<any>(url, options);
      return { key, data };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      errors.push(`${key}: ${errorMessage}`);
      return { key, data: null };
    }
  });

  const responses = await Promise.all(promises);
  
  responses.forEach(({ key, data }) => {
    if (data !== null) {
      results[key as keyof T] = data;
    }
  });

  // エラーがあった場合は警告を出力
  if (errors.length > 0) {
    console.warn('一部のデータ取得に失敗しました:', errors);
  }

  return results;
}

/**
 * データの整合性をチェック
 */
export function validateDataStructure<T>(
  data: any,
  validator: (data: any) => data is T
): T {
  if (!validator(data)) {
    throw new AppError(
      'データ構造が不正です',
      'INVALID_DATA_STRUCTURE'
    );
  }
  return data;
}

// =========================
// 追加: キャッシュ対応ユーティリティ
// =========================

const CACHE_PREFIX = 'app_cache:';

export function getCacheTimestamp(key: string): number | null {
  try {
    const raw = localStorage.getItem(CACHE_PREFIX + key);
    if (!raw) return null;
    const payload = JSON.parse(raw) as { v: unknown; t: number };
    return typeof payload.t === 'number' ? payload.t : null;
  } catch {
    return null;
  }
}

export function getCacheMeta(key: string): { exists: boolean; timestamp: number | null; ageMs: number | null } {
  try {
    const ts = getCacheTimestamp(key);
    if (!ts) return { exists: false, timestamp: null, ageMs: null };
    return { exists: true, timestamp: ts, ageMs: Date.now() - ts };
  } catch {
    return { exists: false, timestamp: null, ageMs: null };
  }
}

function setCache(key: string, value: unknown): void {
  try {
    const payload = { v: value, t: Date.now() };
    localStorage.setItem(CACHE_PREFIX + key, JSON.stringify(payload));
  } catch {}
}

export function getCache<T>(key: string, maxAgeMs?: number): T | null {
  try {
    const raw = localStorage.getItem(CACHE_PREFIX + key);
    if (!raw) return null;
    const payload = JSON.parse(raw) as { v: T; t: number };
    if (maxAgeMs && Date.now() - payload.t > maxAgeMs) return null;
    return payload.v;
  } catch {
    return null;
  }
}

// デフォルトデータの取得
function getDefaultData<T>(url: string): T | null {
  try {
    // URLパターンに基づいてデフォルトデータを提供
    if (url.includes('/api/today')) {
      return {
        date: new Date().toISOString().split('T')[0],
        summary: 'データ取得中...',
        status: 'loading'
      } as T;
    }
    
    if (url.includes('/api/predictions')) {
      return {
        predictions: [],
        status: 'loading',
        message: '予測データを取得中...'
      } as T;
    }
    
    if (url.includes('/api/risk')) {
      return {
        risk_level: 'medium',
        status: 'loading',
        message: 'リスク分析中...'
      } as T;
    }
    
    if (url.includes('/api/dashboard')) {
      return {
        summary: {},
        status: 'loading',
        message: 'ダッシュボードデータを読み込み中...'
      } as T;
    }
    
    // 汎用デフォルト
    return {
      status: 'loading',
      message: 'データを読み込み中...',
      timestamp: Date.now()
    } as T;
  } catch {
    return null;
  }
}

export async function fetchJsonWithCache<T>(
  url: string,
  options: FetchOptions & { cacheKey?: string; cacheTtlMs?: number } = {}
): Promise<{ data: T; fromCache: boolean }>
{
  const { cacheKey, cacheTtlMs } = options;
  
  // まずキャッシュをチェック
  if (cacheKey) {
    const cached = getCache<T>(cacheKey, cacheTtlMs);
    if (cached) {
      console.log(`Using cached data for ${cacheKey}`);
      return { data: cached, fromCache: true };
    }
  }
  
  try {
    const data = await fetchJson<T>(url, options);
    if (cacheKey) {
      setCache(cacheKey, data);
      console.log(`Cached fresh data for ${cacheKey}`);
    }
    return { data, fromCache: false };
  } catch (e) {
    console.warn(`Fetch failed for ${url}, attempting cache fallback:`, e);
    
    // キャッシュフォールバック（TTL無視）
    if (cacheKey) {
      const cached = getCache<T>(cacheKey);
      if (cached) {
        console.log(`Using stale cache for ${cacheKey} due to fetch failure`);
        return { data: cached, fromCache: true };
      }
    }
    
    // 最後の手段: デフォルトデータ
    const defaultData = getDefaultData<T>(url);
    if (defaultData) {
      console.log(`Using default data for ${url}`);
      return { data: defaultData, fromCache: true };
    }
    
    throw e;
  }
}

export async function fetchManyWithCache<T extends Record<string, any>>(
  map: Record<keyof T, { url: string; cacheKey: string; ttlMs?: number }>,
  options: FetchOptions = {}
): Promise<{ results: Partial<T>; cacheFlags: Record<string, boolean> }>
{
  const entries = Object.entries(map) as [string, { url: string; cacheKey: string; ttlMs?: number }][];
  const results: Partial<T> = {};
  const cacheFlags: Record<string, boolean> = {};

  await Promise.all(entries.map(async ([k, { url, cacheKey, ttlMs }]) => {
    try {
      const { data, fromCache } = await fetchJsonWithCache<any>(url, { ...options, cacheKey, cacheTtlMs: ttlMs });
      (results as any)[k] = data;
      cacheFlags[k] = fromCache;
    } catch (err) {
      console.warn(`Failed to fetch ${k}:`, err);
      
      // 最後の手段: キャッシュのみ（TTL無視）
      const cached = getCache<any>(cacheKey);
      if (cached) {
        (results as any)[k] = cached;
        cacheFlags[k] = true;
        console.log(`Using stale cache for ${k}`);
      } else {
        // デフォルトデータを使用
        const defaultData = getDefaultData<any>(url);
        if (defaultData) {
          (results as any)[k] = defaultData;
          cacheFlags[k] = true;
          console.log(`Using default data for ${k}`);
        }
      }
    }
  }));

  return { results, cacheFlags };
}

// オフライン対応の強化
export function isOnline(): boolean {
  return typeof navigator !== 'undefined' ? navigator.onLine : true;
}

export function waitForOnline(): Promise<void> {
  return new Promise((resolve) => {
    if (isOnline()) {
      resolve();
      return;
    }
    
    const handleOnline = () => {
      window.removeEventListener('online', handleOnline);
      resolve();
    };
    
    window.addEventListener('online', handleOnline);
  });
}

// ネットワーク状態の監視
export function createNetworkStatusHook() {
  const [isOnline, setIsOnline] = useState(navigator?.onLine ?? true);
  
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);
  
  return isOnline;
}

