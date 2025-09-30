/**
 * 統一されたデータフェッチ層
 * エラーハンドリング、リトライ、タイムアウト、AbortController対応
 */

export interface FetchOptions {
  signal?: AbortSignal;
  timeout?: number;
  retries?: number;
  retryDelay?: number;
  method?: string;
  headers?: Record<string, string>;
  json?: unknown;
}

export class AppError extends Error {
  constructor(
    message: string,
    public code: string,
    public status?: number
  ) {
    super(message);
    this.name = 'AppError';
  }
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
    json
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

      const response = await fetch(resolveUrl(url), {
        signal: controller.signal,
        cache: "no-cache",
        method: method || (hasJsonBody ? 'POST' : 'GET'),
        headers: { ...baseHeaders, ...(headers || {}) },
        body: hasJsonBody ? JSON.stringify(json) : undefined,
      });

      clearTimeout(timeoutId);

      // ステータス検査
      if (!response.ok) {
        throw new AppError(
          `HTTP ${response.status}: ${response.statusText}`,
          `HTTP_${response.status}`,
          response.status
        );
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

export async function fetchJsonWithCache<T>(
  url: string,
  options: FetchOptions & { cacheKey?: string; cacheTtlMs?: number } = {}
): Promise<{ data: T; fromCache: boolean }>
{
  const { cacheKey, cacheTtlMs } = options;
  try {
    const data = await fetchJson<T>(url, options);
    if (cacheKey) setCache(cacheKey, data);
    return { data, fromCache: false };
  } catch (e) {
    if (cacheKey) {
      const cached = getCache<T>(cacheKey, cacheTtlMs);
      if (cached) {
        return { data: cached, fromCache: true };
      }
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
      // 最後の手段: キャッシュのみ（TTL無視）
      const cached = getCache<any>(cacheKey);
      if (cached) {
        (results as any)[k] = cached;
        cacheFlags[k] = true;
      }
    }
  }));

  return { results, cacheFlags };
}

