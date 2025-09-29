import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

export async function GET() {
  try {
    const filePath = path.join(process.cwd(), 'public', 'data', 'today_summary.json');
    const text = await fs.readFile(filePath, 'utf-8');
    const json = JSON.parse(text);
    return NextResponse.json(json, { status: 200 });
  } catch (e) {
    const message = e instanceof Error ? e.message : 'unknown error';
    return NextResponse.json({ error: 'today_summary not found', message }, { status: 404 });
  }
}


