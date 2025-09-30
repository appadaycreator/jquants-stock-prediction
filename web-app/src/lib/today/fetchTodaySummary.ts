import { TodaySummary } from '../../types/today';
import { fetchJsonWithCache } from '@/lib/fetcher';

const DATA_ENDPOINT = '/data/today_summary.json';

export async function fetchTodaySummary(): Promise<TodaySummary> {
  try {
    // ベースパス解決＋キャッシュフォールバック対応の安全フェッチ
    const { data, fromCache } = await fetchJsonWithCache<TodaySummary>(DATA_ENDPOINT, {
      cacheKey: 'today:summary',
      cacheTtlMs: 1000 * 60 * 60, // 1時間
      retries: 2,
      retryDelay: 800,
    });

    // 新規取得の場合はローカルキャッシュも更新
    if (!fromCache) {
      try {
        localStorage.setItem('today_summary', JSON.stringify(data));
        localStorage.setItem('today_summary_timestamp', new Date().toISOString());
      } catch (_) {}
    }

    return data;
  } catch (error) {
    console.error('fetchTodaySummary error:', error);
    // 最後の手段: ローカルキャッシュを返す
    const cachedData = localStorage.getItem('today_summary');
    if (cachedData) {
      try {
        return JSON.parse(cachedData);
      } catch (e) {
        console.warn('Failed to parse cached data:', e);
      }
    }
    throw error;
  }
}

export function saveTodaySummaryToCache(summary: TodaySummary): void {
  try {
    localStorage.setItem('today_summary', JSON.stringify(summary));
    localStorage.setItem('today_summary_timestamp', new Date().toISOString());
  } catch (error) {
    console.warn('Failed to save to cache:', error);
  }
}

export function getCachedTodaySummary(): TodaySummary | null {
  try {
    const cachedData = localStorage.getItem('today_summary');
    if (cachedData) {
      return JSON.parse(cachedData);
    }
  } catch (error) {
    console.warn('Failed to get cached data:', error);
  }
  return null;
}

export function getCacheTimestamp(): string | null {
  return localStorage.getItem('today_summary_timestamp');
}
