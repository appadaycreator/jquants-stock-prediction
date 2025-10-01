export const dynamic = "force-static";
import { NextRequest, NextResponse } from "next/server";
import { createJob, getJobIdByClientToken, simulateProgress, updateJob } from "../_jobStore";
import { withIdempotency } from "../_idempotency";

export async function GET() {
  return NextResponse.json({ error: "Method Not Allowed" }, { status: 405 });
}

export const POST = withIdempotency(async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}));
    const clientToken = body?.client_token as string | undefined;

    // 冪等化: 同一クライアントトークンなら同一job_idを返却
    if (clientToken) {
      const existing = getJobIdByClientToken(clientToken);
      if (existing) {
        return NextResponse.json({ job_id: existing });
      }
    }

    const job = createJob({ clientToken });

    // 非同期シミュレーション: 5〜20秒で完了し、結果URLを付与
    const cancel = simulateProgress(job.id, () => {});

    (async () => {
      try {
        // 実処理のシミュレーション
        const execMs = 5000 + Math.floor(Math.random() * 15000);
        await new Promise((r) => setTimeout(r, execMs));
        const dateStr = new Date().toISOString().split("T")[0];
        updateJob(job.id, {
          status: "succeeded",
          progress: 100,
          resultUrl: `https://cdn.example.com/results/${dateStr}.json`,
        });
        cancel();
      } catch (e: any) {
        updateJob(job.id, { status: "failed", error: e?.message || "Unknown error" });
        cancel();
      }
    })();

    return NextResponse.json({ job_id: job.id });
  } catch (error) {
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
});


