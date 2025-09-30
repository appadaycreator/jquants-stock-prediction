import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export const dynamic = 'force-static';

// なるべく軽量に: 既定では最新100件のみ返却
// クエリ: level, source, request_id, limit

type LogItem = {
  ts: string;
  level: string;
  source: string;
  message: string;
  request_id?: string;
  file: string;
};

const LOG_DIR = path.join(process.cwd(), '..', 'logs');

function listLogFiles(): string[] {
  try {
    if (!fs.existsSync(LOG_DIR)) return [];
    const files = fs.readdirSync(LOG_DIR)
      .filter((f) => f.endsWith('.log'))
      .map((f) => path.join(LOG_DIR, f))
      .sort((a, b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs);
    return files;
  } catch {
    return [];
  }
}

// 既定フォーマット: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
// 例: 2025-09-30 12:34:56,789 - system - ERROR - failed to ... [request_id=abc]
const LINE_RE = /^(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}[.,]\d{3})\s+-\s+([^\s]+)\s+-\s+([A-Z]+)\s+-\s+(.+)$/;

function parseLine(line: string, file: string): LogItem | null {
  const m = line.match(LINE_RE);
  if (!m) return null;
  const [, ts, source, level, rest] = m;
  let message = rest.trim();
  let request_id: string | undefined;
  const rid = message.match(/request_id=([\w-]+)/);
  if (rid) request_id = rid[1];
  return { ts, level, source, message, request_id, file: path.basename(file) };
}

function collectLogs(params: {
  level?: string;
  source?: string;
  request_id?: string;
  limit: number;
}): { items: LogItem[]; files: string[] } {
  const files = listLogFiles();
  const items: LogItem[] = [];
  if (!files.length) return { items, files: [] };

  outer: for (const file of files) {
    try {
      // 大きすぎるファイル対策: 最大3MBだけ読む（末尾優先）
      const stat = fs.statSync(file);
      const maxBytes = 3 * 1024 * 1024;
      let content: string;
      if (stat.size > maxBytes) {
        const fd = fs.openSync(file, 'r');
        const buf = new Uint8Array(maxBytes);
        const bytesRead = fs.readSync(fd, buf, 0, maxBytes, stat.size - maxBytes);
        fs.closeSync(fd);
        content = Buffer.from(buf.subarray(0, bytesRead)).toString('utf-8');
      } else {
        content = fs.readFileSync(file, 'utf-8');
      }
      const lines = content.split(/\r?\n/);
      // 末尾からさかのぼる（新しい順）
      for (let i = lines.length - 1; i >= 0; i--) {
        const item = parseLine(lines[i], file);
        if (!item) continue;
        // フィルタ
        if (params.level && item.level !== params.level.toUpperCase()) continue;
        if (params.source && !item.source.toLowerCase().includes(params.source.toLowerCase())) continue;
        if (params.request_id && item.request_id !== params.request_id) continue;
        items.push(item);
        if (items.length >= params.limit) break outer;
      }
    } catch {
      // 読めないファイルはスキップ
    }
  }
  return { items, files: files.map((f) => path.basename(f)) };
}

export async function GET(req: NextRequest) {
  // 静的互換は不要（動的ログ読み込みのため）
  try {
    const { searchParams } = new URL(req.url);
    const level = searchParams.get('level') || undefined; // DEBUG/INFO/WARN/ERROR/CRITICAL
    const source = searchParams.get('source') || undefined; // logger name substring
    const request_id = searchParams.get('request_id') || undefined;
    const limit = Math.min(Math.max(parseInt(searchParams.get('limit') || '100', 10) || 100, 1), 1000);

    const { items, files } = collectLogs({ level, source, request_id, limit });
    return NextResponse.json({ items, meta: { total: items.length, limit }, files });
  } catch (e) {
    return NextResponse.json({ items: [], meta: { total: 0, limit: 0 }, files: [] }, { status: 500 });
  }
}


