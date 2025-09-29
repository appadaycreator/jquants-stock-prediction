import { TodaySummary } from '../../types/today';

const DATA_ENDPOINT = '/data/today_summary.json';

export async function fetchTodaySummary(): Promise<TodaySummary> {
  try {
    // 静的ファイルから直接データを取得
    const response = await fetch(DATA_ENDPOINT, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
    });

    if (response.ok) {
      const data = await response.json();
      return data;
    }

    // 両方失敗した場合はローカルストレージから前回のデータを取得
    const cachedData = localStorage.getItem('today_summary');
    if (cachedData) {
      try {
        return JSON.parse(cachedData);
      } catch (error) {
        console.warn('Failed to parse cached data:', error);
      }
    }

    throw new Error('データの取得に失敗しました。静的データファイルが利用できません。');
  } catch (error) {
    console.error('fetchTodaySummary error:', error);
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
