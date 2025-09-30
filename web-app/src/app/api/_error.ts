import { NextResponse } from 'next/server';

export type ApiErrorBody = {
  error_code: string;
  user_message: string;
  retry_hint?: string;
  details?: Record<string, unknown>;
};

export function jsonError(
  body: ApiErrorBody,
  init?: { status?: number; headers?: Record<string, string> }
) {
  const status = init?.status ?? 500;
  const headers = {
    'Content-Type': 'application/json',
    ...init?.headers,
  };
  return new NextResponse(JSON.stringify(body), { status, headers });
}

export function wrapHandler<T extends (...args: any[]) => Promise<Response>>(
  handler: T,
  options?: { defaultErrorCode?: string; retryHint?: string }
) {
  const defaultErrorCode = options?.defaultErrorCode ?? 'INTERNAL_ERROR';
  const defaultRetryHint = options?.retryHint ?? 'しばらく待ってから再実行してください';

  return (async (...args: Parameters<T>): Promise<Response> => {
    try {
      return await handler(...args);
    } catch (e: any) {
      const error_code = e?.code || e?.error_code || defaultErrorCode;
      const user_message = e?.user_message || '処理中にエラーが発生しました';
      const retry_hint = e?.retry_hint || defaultRetryHint;
      const status = typeof e?.status === 'number' ? e.status : 500;
      return jsonError({ error_code, user_message, retry_hint }, { status });
    }
  }) as T;
}


