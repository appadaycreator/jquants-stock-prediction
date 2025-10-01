import { NextRequest, NextResponse } from "next/server";
import { withIdempotency } from "../../_idempotency";
import { jsonError } from "../../_error";
import { createJob, getJobIdByClientToken, simulateProgress, updateJob } from "../../_jobStore";

export const dynamic = "force-static";

export const POST = withIdempotency(async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}));
    const clientToken = body?.client_token as string | undefined;
    
    // まずは同一クライアントトークンでの既存ジョブを再利用
    if (clientToken) {
      const existing = getJobIdByClientToken(clientToken);
      if (existing) {
        return NextResponse.json({ job_id: existing });
      }
    }

    // 直接ジョブを作成し、進捗シミュレーションを開始
    const job = createJob({ clientToken });
    const cancel = simulateProgress(job.id, () => {});

    (async () => {
      try {
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
  } catch (e) {
    return jsonError({
      error_code: "INTERNAL_ERROR",
      user_message: "内部エラーが発生しました",
      retry_hint: "しばらく待ってから再実行してください",
    }, { status: 500 });
  }
});

export async function GET() {
  return NextResponse.json({ error: "Method Not Allowed" }, { status: 405 });
}


