/**
 * 統一されたデータフェッチ層
 * エラーハンドリング、リトライ、タイムアウト、AbortController対応
 */

export interface FetchOptions {
  signal?: AbortSignal;
  timeout?: number;
  retries?: number;
  retryDelay?: number;
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
  const {
    signal,
    timeout = 10000,
    retries = 3,
    retryDelay = 1000
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
      const response = await fetch(url, {
        signal: controller.signal,
        cache: "no-cache",
        headers: {
          "Cache-Control": "no-cache",
          "Pragma": "no-cache",
        },
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
