import { NextRequest, NextResponse } from "next/server";

type StoredEntry = {
  status: number;
  headers: Record<string, string>;
  body: any;
  createdAt: number;
};

// 開発用のインメモリストア（プロセス再起動で消える）
const store = new Map<string, StoredEntry>();
const DEFAULT_TTL_MS = 10 * 60 * 1000; // 10分

function isExpired(entry: StoredEntry, ttlMs: number) {
  return Date.now() - entry.createdAt > ttlMs;
}

export interface IdempotencyOptions {
  headerName?: string; // 例: 'Idempotency-Key'
  ttlMs?: number;
}

/**
 * 冪等化ミドルウェア: 同一キーのPOST/PUT/PATCH/DELETEは前回レスポンスを返す
 * - ヘッダに Idempotency-Key を要求
 * - 保存期間はデフォルト10分
 */
export function withIdempotency<T extends (req: NextRequest) => Promise<Response>>(
  handler: T,
  options: IdempotencyOptions = {},
): T {
  const headerName = options.headerName || "Idempotency-Key";
  const ttlMs = options.ttlMs ?? DEFAULT_TTL_MS;

  return (async (req: NextRequest): Promise<Response> => {
    const method = req.method.toUpperCase();
    const requiresKey = method === "POST" || method === "PUT" || method === "PATCH" || method === "DELETE";

    if (!requiresKey) {
      return handler(req);
    }

    const key = req.headers.get(headerName) || "";
    if (!key) {
      return NextResponse.json(
        {
          error_code: "IDEMPOTENCY_KEY_REQUIRED",
          user_message: `${headerName} ヘッダが必要です`,
          retry_hint: "クライアントで一意キーを生成し、同一操作で同一キーを送信してください",
        },
        { status: 400 },
      );
    }

    const hit = store.get(key);
    if (hit && !isExpired(hit, ttlMs)) {
      // 前回レスポンスをそのまま返す
      return new NextResponse(JSON.stringify(hit.body), {
        status: hit.status,
        headers: {
          "Content-Type": "application/json",
          "Idempotency-Reused": "true",
          ...hit.headers,
        },
      });
    }

    // 実行して結果を保存
    const res = await handler(req);
    try {
      // JSONレスポンス前提
      const clone = res.clone();
      const body = await clone.json().catch(() => null);
      const headers: Record<string, string> = {};
      res.headers.forEach((v, k) => {
        // センシティブ/不要なヘッダは保存しない
        if (!["set-cookie"].includes(k.toLowerCase())) headers[k] = v;
      });
      if (body !== null) {
        store.set(key, {
          status: res.status,
          headers,
          body,
          createdAt: Date.now(),
        });
      }
    } catch {}

    return res;
  }) as T;
}


