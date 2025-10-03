// 予測結果キャッシュの最小実装（メモリ内）
type CacheValue = { data: any; metadata: any };

const memoryStore: Record<string, CacheValue> = {};

function sizeOfStore(): number {
  try {
    return new TextEncoder().encode(JSON.stringify(memoryStore)).length;
  } catch {
    return 0;
  }
}

let hits = 0;
let misses = 0;

export async function initialize(): Promise<void> {
  // 永続化層なしのため初期化することは特になし
}

export function getCacheStats() {
  const total = hits + misses || 1;
  return {
    hits,
    misses,
    hitRate: Math.round((hits / total) * 100) / 100,
    totalSize: sizeOfStore(),
    entryCount: Object.keys(memoryStore).length,
  };
}

export function generateCacheKey(...parts: any[]): string {
  return parts.map(p => (typeof p === "string" ? p : JSON.stringify(p))).join(":");
}

export async function getCachedPrediction(key: string): Promise<any | null> {
  const v = memoryStore[key];
  if (v) {
    hits++;
    return v.data;
  }
  misses++;
  return null;
}

export async function getCachedModelComparison(key: string): Promise<any | null> {
  const v = memoryStore[key];
  if (v) {
    hits++;
    return v.data;
  }
  misses++;
  return null;
}

export async function cachePrediction(key: string, data: any, metadata: any): Promise<void> {
  memoryStore[key] = { data, metadata };
}

export async function cacheModelComparison(key: string, data: any, metadata: any): Promise<void> {
  memoryStore[key] = { data, metadata };
}

export async function searchCache(_type: string, _tags: string[]): Promise<Array<{ key: string; data: any; metadata: any }>> {
  return Object.entries(memoryStore).map(([key, value]) => ({ key, data: value.data, metadata: value.metadata }));
}

export async function clearCache(_type?: "prediction" | "comparison"): Promise<void> {
  for (const k of Object.keys(memoryStore)) delete memoryStore[k];
  hits = 0; misses = 0;
}

export default {
  initialize,
  getCacheStats,
  generateCacheKey,
  getCachedPrediction,
  getCachedModelComparison,
  cachePrediction,
  cacheModelComparison,
  searchCache,
  clearCache,
};


