/**
 * 日付処理ユーティリティ
 * JST正規化とタイムゾーン対応
 */

import { DateTime } from 'luxon';

/**
 * 様々な日付形式をJSTに正規化
 */
export function parseToJst(v: string | number): DateTime {
  let dt: DateTime;

  if (typeof v === 'number') {
    // 秒/ミリ秒自動判定
    if (v > 1e12) {
      // ミリ秒
      dt = DateTime.fromMillis(v).toUTC();
    } else {
      // 秒
      dt = DateTime.fromSeconds(v).toUTC();
    }
  } else {
    // ISO文字列を優先
    dt = DateTime.fromISO(v, { setZone: true });
    
    if (!dt.isValid) {
      // YYYY-MM-DD形式
      dt = DateTime.fromFormat(v, 'yyyy-MM-dd', { zone: 'utc' });
    }
    
    if (!dt.isValid) {
      // YYYY-MM-DD HH:mm:ss形式
      dt = DateTime.fromFormat(v, 'yyyy-MM-dd HH:mm:ss', { zone: 'utc' });
    }
    
    if (!dt.isValid) {
      // YYYYMMDD形式
      dt = DateTime.fromFormat(v, 'yyyyMMdd', { zone: 'utc' });
    }
    
    if (!dt.isValid) {
      // YYYY/MM/DD形式
      dt = DateTime.fromFormat(v, 'yyyy/MM/dd', { zone: 'utc' });
    }
  }

  if (!dt.isValid) {
    console.error('Invalid date format:', v);
    // デフォルト日付を返す
    return DateTime.fromISO('2024-01-01', { zone: 'Asia/Tokyo' });
  }

  // すべてJSTに正規化
  return dt.setZone('Asia/Tokyo');
}

/**
 * JSTラベルを生成
 */
export function jstLabel(dt: DateTime): string {
  return dt.toFormat('yyyy-LL-dd');
}

/**
 * 日付文字列を正規化（既存コードとの互換性）
 */
export function normalizeDateString(dateStr: string): string {
  try {
    // 既にYYYY-MM-DD形式の場合はそのまま返す
    if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
      return dateStr;
    }
    
    // YYYYMMDD形式をYYYY-MM-DD形式に変換
    if (/^\d{8}$/.test(dateStr)) {
      return dateStr.replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3');
    }
    
    // Luxonで解析
    const dt = parseToJst(dateStr);
    return dt.toFormat('yyyy-MM-dd');
    
  } catch (error) {
    console.error('Date normalization error:', error, 'Input:', dateStr);
    return '2024-01-01'; // デフォルト日付
  }
}

/**
 * 日付をフォーマット（既存コードとの互換性）
 */
export function formatDate(dateStr: string): string {
  try {
    const dt = parseToJst(dateStr);
    
    if (!dt.isValid) {
      console.error('Invalid date format:', dateStr);
      return 'Invalid Date';
    }
    
    return dt.toLocaleString({
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
    
  } catch (error) {
    console.error('Date formatting error:', error, 'Input:', dateStr);
    return 'Invalid Date';
  }
}

/**
 * チャート用の日付配列を生成
 */
export function createChartDateArray(dates: string[]): { date: string; timestamp: number }[] {
  return dates.map(dateStr => {
    const dt = parseToJst(dateStr);
    return {
      date: jstLabel(dt),
      timestamp: dt.toMillis()
    };
  });
}

/**
 * 日付範囲の検証
 */
export function validateDateRange(startDate: string, endDate: string): boolean {
  try {
    const start = parseToJst(startDate);
    const end = parseToJst(endDate);
    
    if (!start.isValid || !end.isValid) {
      return false;
    }
    
    return start <= end;
  } catch (error) {
    console.error('Date range validation error:', error);
    return false;
  }
}
