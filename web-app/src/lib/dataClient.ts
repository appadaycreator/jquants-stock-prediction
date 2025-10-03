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
    fetchJsonWithCache<LatestIndex>("/data/latest/index.json", {
      cacheKey,
      cacheTtlMs: 1000 * 60 * 10,
      timeout: SIX_SECONDS,
      retries: 2,
      retryDelay: 800,
    }).then(({ data, fromCache }) => {
      if (!fromCache) setLocal(cacheKey, data);
    }).catch(() => {});
    return cached;
  }

  const { data, fromCache } = await fetchJsonWithCache<LatestIndex>("/data/latest/index.json", {
    cacheKey,
    cacheTtlMs: 1000 * 60 * 10,
    timeout: SIX_SECONDS,
    retries: 2,
    retryDelay: 800,
  });
  if (!fromCache) setLocal(cacheKey, data);
  return data;
}

export function resolveBusinessDate(target: string | null, index: LatestIndex): string {
  if (target && index.dates.includes(target)) return target;
  // 市場休場日の場合は直近過去にフォールバック
  const candidate = target ? index.dates.find(d => d <= target) : index.latest;
  return candidate || index.latest;
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


