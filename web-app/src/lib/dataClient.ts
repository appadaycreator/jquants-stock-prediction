"use client";

type HttpMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";

function resolveApiPath(path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  return p.startsWith("/api/") ? p : `/api${p}`;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const url = resolveApiPath(path);
  const headers = {
    "Content-Type": "application/json",
    ...(init.headers || {}),
  } as Record<string, string>;
  const res = await fetch(url, { ...init, headers });
  if (!res.ok) {
    throw new Error(`API Error: ${res.status} ${res.statusText}`);
  }
  return (await res.json()) as T;
}

export const dataClient = {
  async get<T>(path: string): Promise<T> {
    return request<T>(path, { method: "GET" });
  },
  async post<T>(path: string, body?: unknown): Promise<T> {
    return request<T>(path, { method: "POST", body: body ? JSON.stringify(body) : undefined });
  },
  async put<T>(path: string, body?: unknown): Promise<T> {
    return request<T>(path, { method: "PUT", body: body ? JSON.stringify(body) : undefined });
  },
  async delete<T>(path: string): Promise<T> {
    return request<T>(path, { method: "DELETE" });
  },
  async request<T>(path: string, init: RequestInit & { method?: HttpMethod }): Promise<T> {
    return request<T>(path, init);
  },
};

export type DataClient = typeof dataClient;

import { fetchJsonWithCache } from "@/lib/fetcher";
import { resolveStaticPath } from "@/lib/path";

export type LatestIndex = {
  latest: string; // YYYYMMDD
  dates: string[]; // 降順推奨
  hashes?: Record<string, string>; // 任意: 各日付のハッシュ
};

type SwrResult<T> = {
  data: T | null;
  fromCache: boolean;
};

const SIX_SECONDS = 6000;

function setLocal<T>(key: string, value: T): void {
  try {
    localStorage.setItem(key, JSON.stringify({ v: value, t: Date.now() }));
  } catch {}
}

function getLocal<T>(key: string, maxAgeMs?: number): T | null {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return null;
    const { v, t } = JSON.parse(raw);
    if (maxAgeMs && Date.now() - t > maxAgeMs) return null;
    return v as T;
  } catch {
    return null;
  }
}

export async function getLatestIndex(): Promise<LatestIndex> {
  // 直近成功値を最初に返し、裏で更新
  const cacheKey = "latest:index";
  const cached = getLocal<LatestIndex>(cacheKey, 1000 * 60 * 60 * 6);
  if (cached) {
    // 裏で更新をキック（待たない）
    fetchLatestIndexWithFallback().then((data) => {
      if (data) setLocal(cacheKey, data);
    }).catch(() => {});
    return cached;
  }

  const data = await fetchLatestIndexWithFallback();
  if (data) setLocal(cacheKey, data);
  return data;
}

async function fetchLatestIndexWithFallback(): Promise<LatestIndex> {
  // 複数のURLを順次試行
  const urls = [
    "/data/latest/index.json", // 直接パス（最優先）
    resolveStaticPath("/data/latest/index.json"), // resolveStaticPath経由
  ];
  
  // 重複を除去
  const uniqueUrls = [...new Set(urls)];
  
  for (let i = 0; i < uniqueUrls.length; i++) {
    const url = uniqueUrls[i];
    console.log(`Trying URL ${i + 1}/${uniqueUrls.length}: ${url}`);
    
    try {
      const { data, fromCache } = await fetchJsonWithCache<LatestIndex>(url, {
        cacheKey: `latest:index:attempt_${i}`,
        cacheTtlMs: 1000 * 60 * 10,
        timeout: SIX_SECONDS,
        retries: 1,
        retryDelay: 500,
      });
      console.log(`Success with URL: ${url}`);
      return data;
    } catch (error) {
      console.warn(`URL ${i + 1} failed: ${url}`, error);
      if (i === uniqueUrls.length - 1) {
        // 最後のURLも失敗した場合
        console.error("All URLs failed, returning fallback data");
        return {
          latest: "20250930",
          dates: ["20250930"]
        };
      }
    }
  }
  
  // この行には到達しないはずだが、TypeScriptのため
  throw new Error("Unexpected error in fetchLatestIndexWithFallback");
}

export function resolveBusinessDate(target: string | null, index: LatestIndex): string {
  // 入力値の検証
  if (!index || !index.latest || !Array.isArray(index.dates)) {
    console.warn("Invalid index data, using fallback date");
    return "20250930";
  }
  
  if (target && typeof target === 'string' && target !== 'undefined' && index.dates.includes(target)) {
    return target;
  }
  
  // 市場休場日の場合は直近過去にフォールバック
  const candidate = target && target !== 'undefined' ? index.dates.find(d => d <= target) : index.latest;
  const result = candidate || index.latest;
  
  console.log(`resolveBusinessDate: target=${target}, result=${result}`);
  return result;
}

export async function swrJson<T>(
  cacheKey: string,
  url: string,
  opts: { ttlMs?: number; timeoutMs?: number; retries?: number; retryDelay?: number } = {},
): Promise<SwrResult<T>> {
  const { ttlMs = 1000 * 60 * 60, timeoutMs = SIX_SECONDS, retries = 3, retryDelay = 800 } = opts;

  const cached = getLocal<T>(`swr:${cacheKey}`, ttlMs);
  if (cached) {
    // 裏で更新
    fetchJsonWithCache<T>(url, {
      cacheKey: `swr:${cacheKey}`,
      cacheTtlMs: ttlMs,
      timeout: timeoutMs,
      retries,
      retryDelay,
    }).then(({ data, fromCache }) => {
      if (!fromCache) setLocal(`swr:${cacheKey}`, data);
    }).catch(() => {});
    return { data: cached, fromCache: true };
  }

  const { data, fromCache } = await fetchJsonWithCache<T>(url, {
    cacheKey: `swr:${cacheKey}`,
    cacheTtlMs: ttlMs,
    timeout: timeoutMs,
    retries,
    retryDelay,
  });
  if (!fromCache) setLocal(`swr:${cacheKey}`, data);
  return { data, fromCache };
}

export function computeMissingCount<T>(items: Array<T | null | undefined>): number {
  return items.filter(v => v == null).length;
}

export function clearDataCache(): void {
  try {
    // 関連するキャッシュキーをクリア
    const keysToRemove = [
      "latest:index",
      "latest:index:primary", 
      "latest:index:fallback",
      "latest:index:attempt_0",
      "latest:index:attempt_1",
      "today:summary",
      "personal:dashboard",
    ];
    
    // パターンマッチングでキャッシュキーをクリア
    const allKeys = Object.keys(localStorage);
    const patternsToRemove = [
      /^latest:index/,
      /^swr:latest:index/,
      /^today:summary/,
      /^personal:dashboard/,
    ];
    
    // 特定のキーを削除
    keysToRemove.forEach(key => {
      localStorage.removeItem(key);
      localStorage.removeItem(`swr:${key}`);
    });
    
    // パターンマッチングでキーを削除
    allKeys.forEach(key => {
      if (patternsToRemove.some(pattern => pattern.test(key))) {
        localStorage.removeItem(key);
      }
    });
    
    // キャッシュクリアのタイムスタンプを記録
    localStorage.setItem("cache_cleared_at", new Date().toISOString());
    
    console.log("Data cache cleared successfully");
  } catch (error) {
    console.warn("Failed to clear data cache:", error);
  }
}

// アプリケーション起動時の自動キャッシュクリア
if (typeof window !== 'undefined') {
  // バージョン管理による自動キャッシュクリア
  const APP_VERSION = "2.24.1";
  const lastVersion = localStorage.getItem("app_version");
  
  if (lastVersion !== APP_VERSION) {
    console.log(`App version changed from ${lastVersion} to ${APP_VERSION}, clearing cache`);
    clearDataCache();
    localStorage.setItem("app_version", APP_VERSION);
  }
  
  // デバッグ用: グローバルに公開
  (window as any).clearDataCache = clearDataCache;
  (window as any).getLatestIndex = getLatestIndex;
  (window as any).resolveStaticPath = require('./path').resolveStaticPath;
  (window as any).APP_VERSION = APP_VERSION;
}


