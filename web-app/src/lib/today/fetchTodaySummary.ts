import { TodaySummary } from "../../types/today";
import { getLatestIndex, resolveBusinessDate, swrJson } from "@/lib/dataClient";

export async function fetchTodaySummary(targetYmd?: string): Promise<TodaySummary> {
  try {
    // latest/index.json を参照して対象営業日を決定
    const latestIndex = await getLatestIndex();
    const date = resolveBusinessDate(targetYmd || null, latestIndex);

    // SWR: まず直近成功データを即時、同日のCDN JSONを6s/指数バックオフで裏更新
    const { data, fromCache } = await swrJson<TodaySummary | null>(
      "today:summary",
      `/data/${date}/summary.json`,
      { ttlMs: 1000 * 60 * 60, timeoutMs: 6000, retries: 3, retryDelay: 800 },
    );

    if (!fromCache) {
      try {
        localStorage.setItem("today_summary", JSON.stringify(data));
        localStorage.setItem("today_summary_timestamp", new Date().toISOString());
      } catch (_) {}
    }
    if (!data) throw new Error("today_summary_missing");
    return data as TodaySummary;
  } catch (error) {
    console.error("fetchTodaySummary error:", error);
    const cachedData = localStorage.getItem("today_summary");
    if (cachedData) {
      try {
        return JSON.parse(cachedData);
      } catch (e) {
        console.warn("Failed to parse cached data:", e);
      }
    }
    throw error;
  }
}

export function saveTodaySummaryToCache(summary: TodaySummary): void {
  try {
    localStorage.setItem("today_summary", JSON.stringify(summary));
    localStorage.setItem("today_summary_timestamp", new Date().toISOString());
  } catch (error) {
    console.warn("Failed to save to cache:", error);
  }
}

export function getCachedTodaySummary(): TodaySummary | null {
  try {
    const cachedData = localStorage.getItem("today_summary");
    if (cachedData) {
      return JSON.parse(cachedData);
    }
  } catch (error) {
    console.warn("Failed to get cached data:", error);
  }
  return null;
}

export function getCacheTimestamp(): string | null {
  return localStorage.getItem("today_summary_timestamp");
}
