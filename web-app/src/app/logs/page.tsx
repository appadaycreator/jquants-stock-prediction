"use client";
import { useEffect, useMemo, useRef, useState } from "react";

type LogItem = {
  ts: string;
  level: string;
  source: string;
  message: string;
  request_id?: string;
  file: string;
};

const LEVELS = ["ALL", "ERROR", "WARN", "INFO", "DEBUG"];

export default function LogsPage() {
  const [level, setLevel] = useState<string>("ALL");
  const [source, setSource] = useState<string>("");
  const [requestId, setRequestId] = useState<string>("");
  const [limit, setLimit] = useState<number>(100);
  const [onlyCritical, setOnlyCritical] = useState<boolean>(false);
  const [items, setItems] = useState<LogItem[]>([]);
  const [files, setFiles] = useState<string[]>([]);
  const [q, setQ] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [autoRefresh, setAutoRefresh] = useState<boolean>(true);
  const timerRef = useRef<any>(null);

  const fetchLogs = async () => {
    setLoading(true);
    const params = new URLSearchParams();
    if (level !== "ALL") params.set("level", level);
    if (source) params.set("source", source);
    if (requestId) params.set("request_id", requestId);
    params.set("limit", String(limit));
    const res = await fetch(`/api/logs?${params.toString()}`, { cache: "no-store" });
    const json = await res.json();
    setItems(json.items || []);
    setFiles(json.files || []);
    setLoading(false);
  };

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs, level, source, requestId, limit]);

  useEffect(() => {
    if (autoRefresh) {
      timerRef.current = setInterval(fetchLogs, 5000);
    }
    return () => timerRef.current && clearInterval(timerRef.current);
  }, [autoRefresh, fetchLogs, level, source, requestId, limit]);

  const filtered = useMemo(() => {
    const kw = q.trim().toLowerCase();
    const list = onlyCritical
      ? items.filter((x) => x.level === "ERROR" || x.level === "CRITICAL")
      : items;
    if (!kw) return list;
    return list.filter(
      (x) =>
        x.ts.toLowerCase().includes(kw) ||
        x.level.toLowerCase().includes(kw) ||
        x.source.toLowerCase().includes(kw) ||
        (x.request_id || "").toLowerCase().includes(kw) ||
        x.message.toLowerCase().includes(kw),
    );
  }, [items, q, onlyCritical]);

  const copyToClipboard = async () => {
    const text = filtered
      .map((x) => `${x.ts} ${x.level} [${x.source}] ${x.message}`)
      .join("\n");
    await navigator.clipboard.writeText(text);
  };

  return (
    <div style={{ padding: 16, display: "grid", gap: 12 }}>
      <h2>ログビューア</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, alignItems: "center" }}>
        <label>
          レベル:
          <select value={level} onChange={(e) => setLevel(e.target.value)}>
            {LEVELS.map((lv) => (
              <option key={lv} value={lv}>
                {lv}
              </option>
            ))}
          </select>
        </label>
        <label>
          処理（source）:
          <input value={source} onChange={(e) => setSource(e.target.value)} placeholder="system/model/api..." />
        </label>
        <label>
          request_id:
          <input value={requestId} onChange={(e) => setRequestId(e.target.value)} placeholder="xxxx-xxxx" />
        </label>
        <label>
          件数:
          <input type="number" min={1} max={1000} value={limit} onChange={(e) => setLimit(parseInt(e.target.value || "100", 10))} />
        </label>
        <label title="ERROR/CRITICAL のみ">
          <input type="checkbox" checked={onlyCritical} onChange={(e) => setOnlyCritical(e.target.checked)} /> 重大のみ
        </label>
        <label>
          検索:
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="キーワード" />
        </label>
        <button onClick={fetchLogs} disabled={loading}>更新</button>
        <button onClick={() => setAutoRefresh((v) => !v)}>{autoRefresh ? "自動更新停止" : "自動更新"}</button>
        <button onClick={copyToClipboard}>表示内容をコピー</button>
      </div>

      <div style={{ fontSize: 12, opacity: 0.8 }}>ログファイル（ダウンロード可）:</div>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        {files.map((f) => (
          <a key={f} href={`/api/logs/download?file=${encodeURIComponent(f)}`}>
            {f}
          </a>
        ))}
      </div>

      <div style={{ border: "1px solid #ddd", borderRadius: 8, overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead style={{ background: "#fafafa" }}>
            <tr>
              <th style={{ textAlign: "left", padding: 8 }}>時間</th>
              <th style={{ textAlign: "left", padding: 8 }}>レベル</th>
              <th style={{ textAlign: "left", padding: 8 }}>処理</th>
              <th style={{ textAlign: "left", padding: 8 }}>request_id</th>
              <th style={{ textAlign: "left", padding: 8 }}>メッセージ</th>
              <th style={{ textAlign: "left", padding: 8 }}>ファイル</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((x, i) => (
              <tr key={i} style={{ borderTop: "1px solid #eee", background: x.level === "ERROR" || x.level === "CRITICAL" ? "#fff4f4" : "white" }}>
                <td style={{ padding: 8, whiteSpace: "nowrap" }}>{x.ts}</td>
                <td style={{ padding: 8 }}>{x.level}</td>
                <td style={{ padding: 8 }}>{x.source}</td>
                <td style={{ padding: 8 }}>{x.request_id || ""}</td>
                <td style={{ padding: 8 }}>{x.message}</td>
                <td style={{ padding: 8 }}>{x.file}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {loading && <div>読み込み中...</div>}
    </div>
  );
}


