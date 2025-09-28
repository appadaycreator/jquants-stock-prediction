import { TodaySummary } from '../../types/today';

const API_ENDPOINT = '/api/today';
const FALLBACK_ENDPOINT = '/data/today_summary.json';

export async function fetchTodaySummary(): Promise<TodaySummary> {
  try {
    // まずAPIエンドポイントを試行
    const response = await fetch(API_ENDPOINT, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store', // 常に最新データを取得
    });

    if (response.ok) {
      const data = await response.json();
      return data;
    }

    // APIが失敗した場合は静的ファイルを試行
    const fallbackResponse = await fetch(FALLBACK_ENDPOINT, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
    });

    if (fallbackResponse.ok) {
      const data = await fallbackResponse.json();
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

    throw new Error('データの取得に失敗しました。APIとフォールバックファイルの両方が利用できません。');
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
