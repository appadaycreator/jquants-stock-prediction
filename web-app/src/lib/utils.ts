/**
 * ユーティリティ関数
 */

import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * 数値を通貨形式でフォーマットする
 * @param value フォーマットする数値
 * @returns フォーマットされた通貨文字列
 */
export function formatCurrency(value: number): string {
  return new Intl.NumberFormat("ja-JP", {
    style: "currency",
    currency: "JPY",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

/**
 * 数値をパーセンテージ形式でフォーマットする
 * @param value フォーマットする数値（0-1の範囲）
 * @param decimals 小数点以下の桁数
 * @returns フォーマットされたパーセンテージ文字列
 */
export function formatPercentage(value: number, decimals: number = 1): string {
  return new Intl.NumberFormat("ja-JP", {
    style: "percent",
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

/**
 * Dateオブジェクトを日付文字列にフォーマットする
 * @param date フォーマットする日付
 * @param format フォーマット文字列
 * @returns フォーマットされた日付文字列
 */
export function formatDate(date: Date, format: string = "YYYY-MM-DD"): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");

  return format
    .replace("YYYY", String(year))
    .replace("MM", month)
    .replace("DD", day);
}

/**
 * 関数の実行を遅延させるデバウンス関数
 * @param func 実行する関数
 * @param delay 遅延時間（ミリ秒）
 * @returns デバウンスされた関数
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number,
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout;

  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
}

/**
 * 配列をシャッフルする
 * @param array シャッフルする配列
 * @returns シャッフルされた配列
 */
export function shuffleArray<T>(array: T[]): T[] {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

/**
 * オブジェクトをディープクローンする
 * @param obj クローンするオブジェクト
 * @returns クローンされたオブジェクト
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== "object") {
    return obj;
  }

  if (obj instanceof Date) {
    return new Date(obj.getTime()) as T;
  }

  if (obj instanceof Array) {
    return obj.map(item => deepClone(item)) as T;
  }

  if (typeof obj === "object") {
    const cloned = {} as T;
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        cloned[key] = deepClone(obj[key]);
      }
    }
    return cloned;
  }

  return obj;
}

/**
 * 文字列をキャメルケースに変換する
 * @param str 変換する文字列
 * @returns キャメルケースの文字列
 */
export function toCamelCase(str: string): string {
  return str
    .replace(/(?:^\w|[A-Z]|\b\w)/g, (word, index) => {
      return index === 0 ? word.toLowerCase() : word.toUpperCase();
    })
    .replace(/\s+/g, "");
}

/**
 * 文字列をスネークケースに変換する
 * @param str 変換する文字列
 * @returns スネークケースの文字列
 */
export function toSnakeCase(str: string): string {
  return str
    .replace(/\W+/g, " ")
    .split(/ |\B(?=[A-Z])/)
    .map(word => word.toLowerCase())
    .join("_");
}

/**
 * 配列から重複を削除する
 * @param array 重複を削除する配列
 * @returns 重複が削除された配列
 */
export function uniqueArray<T>(array: T[]): T[] {
  return [...new Set(array)];
}

/**
 * 配列を指定したサイズのチャンクに分割する
 * @param array 分割する配列
 * @param size チャンクのサイズ
 * @returns 分割された配列の配列
 */
export function chunkArray<T>(array: T[], size: number): T[][] {
  const chunks: T[][] = [];
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size));
  }
  return chunks;
}

/**
 * 2つの配列の差分を取得する
 * @param array1 比較する配列1
 * @param array2 比較する配列2
 * @returns 差分の配列
 */
export function arrayDiff<T>(array1: T[], array2: T[]): T[] {
  return array1.filter(item => !array2.includes(item));
}

/**
 * 配列の要素をランダムに選択する
 * @param array 選択する配列
 * @param count 選択する要素数
 * @returns 選択された要素の配列
 */
export function randomSelect<T>(array: T[], count: number = 1): T[] {
  const shuffled = shuffleArray(array);
  return shuffled.slice(0, count);
}