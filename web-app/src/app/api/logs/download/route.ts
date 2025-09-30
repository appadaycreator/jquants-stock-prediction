import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

const LOG_DIR = path.join(process.cwd(), '..', 'logs');

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const file = searchParams.get('file');
    if (!file || file.includes('..') || file.includes('/') || !file.endsWith('.log')) {
      return NextResponse.json({ error: 'Invalid file' }, { status: 400 });
    }
    const full = path.join(LOG_DIR, file);
    if (!fs.existsSync(full)) {
      return NextResponse.json({ error: 'Not found' }, { status: 404 });
    }
    const stat = fs.statSync(full);
    const stream = fs.createReadStream(full);
    return new NextResponse(stream as any, {
      status: 200,
      headers: new Headers({
        'content-type': 'text/plain; charset=utf-8',
        'content-length': String(stat.size),
        'content-disposition': `attachment; filename="${file}"`,
        'cache-control': 'no-store',
      }),
    });
  } catch (e) {
    return NextResponse.json({ error: 'Internal Error' }, { status: 500 });
  }
}


