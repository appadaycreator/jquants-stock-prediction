import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-static';

export async function GET(_req: NextRequest, context: { params: { job_id: string } }) {
  try {
    const jobId = context.params.job_id;
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


