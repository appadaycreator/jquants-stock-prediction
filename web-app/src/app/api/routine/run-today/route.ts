import { NextRequest, NextResponse } from 'next/server';
import { withIdempotency } from '../../_idempotency';

export const dynamic = 'force-static';

export const POST = withIdempotency(async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}));
    const clientToken = body?.client_token as string | undefined;

    // サーバ実行がない環境では、既存の analyze エンドポイントに委譲
    const res = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL || ''}/api/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ client_token: clientToken })
    });
    if (!res.ok) {
      return NextResponse.json({ error: 'Failed to enqueue routine' }, { status: 500 });
    }
    const data = await res.json();
    return NextResponse.json({ job_id: data.job_id });
  } catch (e) {
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
});

export async function GET() {
  return NextResponse.json({ error: 'Method Not Allowed' }, { status: 405 });
}


