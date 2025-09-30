import { NextResponse } from 'next/server';

export const dynamic = 'force-static';

export async function generateStaticParams() {
  // 静的エクスポート用のダミーパラメータを生成
  return [
    { job_id: 'dummy' }
  ];
}

export async function GET(req: Request) {
  try {
    const url = new URL(req.url);
    const match = url.pathname.match(/\/api\/routine\/jobs\/([^/]+)/);
    const jobId = match?.[1] || url.searchParams.get('job_id') || '';
    if (!jobId) {
      return NextResponse.json({ error: 'Bad Request' }, { status: 400 });
    }
    // 既存のジョブAPIに委譲
    const res = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL || ''}/api/jobs/${jobId}`, { cache: 'no-store' });
    if (!res.ok) {
      return NextResponse.json({ error: 'Not Found' }, { status: 404 });
    }
    const data = await res.json();
    return NextResponse.json({ status: data.status, progress: data.progress, result_url: data.resultUrl, error: data.error });
  } catch (e) {
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}


