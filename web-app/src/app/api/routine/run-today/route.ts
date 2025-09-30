import { NextRequest, NextResponse } from 'next/server';
import { withIdempotency } from '../../_idempotency';
import { jsonError } from '../../_error';

export const dynamic = 'force-static';

export const POST = withIdempotency(async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}));
    const clientToken = body?.client_token as string | undefined;
    const idemKey = request.headers.get('Idempotency-Key') || undefined;

    // サーバ実行がない環境では、既存の analyze エンドポイントに委譲
    const res = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL || ''}/api/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(idemKey ? { 'Idempotency-Key': idemKey } : {})
      },
      body: JSON.stringify({ client_token: clientToken })
    });
    if (!res.ok) {
      // 下流のエラー(JSON)を透過。JSONでない場合は汎用エラー。
      try {
        const errBody = await res.json();
        return jsonError(errBody, { status: res.status });
      } catch {
        return jsonError({
          error_code: 'ROUTINE_ENQUEUE_FAILED',
          user_message: 'ルーティンの起動に失敗しました',
          retry_hint: '数秒後に再実行してください'
        }, { status: res.status || 500 });
      }
    }
    const data = await res.json();
    return NextResponse.json({ job_id: data.job_id });
  } catch (e) {
    return jsonError({
      error_code: 'INTERNAL_ERROR',
      user_message: '内部エラーが発生しました',
      retry_hint: 'しばらく待ってから再実行してください'
    }, { status: 500 });
  }
});

export async function GET() {
  return NextResponse.json({ error: 'Method Not Allowed' }, { status: 405 });
}


