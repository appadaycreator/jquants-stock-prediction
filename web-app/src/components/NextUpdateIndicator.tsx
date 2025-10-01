"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Clock, Bell } from "lucide-react";
import { NotificationService, NotificationConfig } from "@/lib/notification/NotificationService";

function parseTimeToToday(timeStr: string): Date {
  const now = new Date();
  const [hh, mm] = timeStr.split(":").map((v) => parseInt(v, 10));
  const d = new Date(now.getFullYear(), now.getMonth(), now.getDate(), hh || 0, mm || 0, 0, 0);
  return d;
}

function getNextScheduledTime(cfg?: NotificationConfig): Date | null {
  if (!cfg?.schedule) return null;
  const now = new Date();
  const candidates: Date[] = [];
  if (cfg.schedule.morning_analysis) {
    const m = parseTimeToToday(cfg.schedule.morning_analysis);
    if (m > now) candidates.push(m); else candidates.push(new Date(m.getTime() + 24 * 3600 * 1000));
  }
  if (cfg.schedule.evening_analysis) {
    const e = parseTimeToToday(cfg.schedule.evening_analysis);
    if (e > now) candidates.push(e); else candidates.push(new Date(e.getTime() + 24 * 3600 * 1000));
  }
  if (candidates.length === 0) return null;
  candidates.sort((a, b) => a.getTime() - b.getTime());
  return candidates[0];
}

function formatRemain(ms: number): string {
  if (ms <= 0) return "まもなく";
  const sec = Math.floor(ms / 1000);
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = sec % 60;
  if (h > 0) return `${h}時間${m}分${s}秒`;
  if (m > 0) return `${m}分${s}秒`;
  return `${s}秒`;
}

export default function NextUpdateIndicator() {
  const [config, setConfig] = useState<NotificationConfig | null>(null);
  const [now, setNow] = useState<Date>(new Date());
  const [pushReady, setPushReady] = useState<boolean>(false);

  useEffect(() => {
    (async () => {
      const svc = NotificationService.getInstance();
      try {
        const cfg = await svc.loadConfig();
        setConfig(cfg);
      } catch (e) {
        console.debug("通知設定が未設定のため、インジケーターはデフォルト表示で継続します。");
        setConfig(null);
      }
      setPushReady(typeof window !== "undefined" && "Notification" in window && Notification.permission === "granted");
    })();
  }, []);

  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  const nextAt = useMemo(() => getNextScheduledTime(config || undefined), [config, now]);
  const remainMs = useMemo(() => (nextAt ? nextAt.getTime() - now.getTime() : 0), [nextAt, now]);

  const requestPush = async () => {
    try {
      const svc = NotificationService.getInstance();
      const ok = await svc.initializePushNotifications();
      if (ok) setPushReady(true);
    } catch (_) {}
  };

  return (
    <div className="flex items-center space-x-3 text-sm text-gray-700">
      <Clock className="h-4 w-4 text-gray-500" />
      <div className="flex items-center space-x-2">
        <span className="text-gray-600">次回更新:</span>
        <span className="font-medium">
          {nextAt ? nextAt.toLocaleString("ja-JP") : "未設定"}
        </span>
        {nextAt && (
          <span className="text-gray-500">(残り {formatRemain(remainMs)})</span>
        )}
      </div>
      <span className="text-gray-400">|</span>
      <Link href="/settings#notifications" className="text-blue-600 hover:underline">
        スケジュール/通知設定
      </Link>
      {!pushReady && (
        <button
          onClick={requestPush}
          className="inline-flex items-center px-2 py-1 bg-blue-50 text-blue-700 rounded hover:bg-blue-100"
          title="ブラウザ通知を有効化"
        >
          <Bell className="h-3.5 w-3.5 mr-1" /> 通知を有効化
        </button>
      )}
    </div>
  );
}


