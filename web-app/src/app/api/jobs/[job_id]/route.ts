import { NextRequest, NextResponse } from 'next/server';
import { getJob } from '../../_jobStore';

export async function GET(
  _request: NextRequest,
  { params }: { params: { job_id: string } }
) {
  const job = getJob(params.job_id);
  if (!job) {
    return NextResponse.json({ error: 'Not Found' }, { status: 404 });
  }
  return NextResponse.json({
    status: job.status,
    progress: job.progress,
    result_url: job.resultUrl,
    error: job.error,
  });
}

export async function POST() {
  return NextResponse.json({ error: 'Method Not Allowed' }, { status: 405 });
}


