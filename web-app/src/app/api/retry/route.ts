import { NextRequest, NextResponse } from "next/server";
import { createJob, getJobIdByClientToken, updateJob } from "../_jobStore";
import { jsonError } from "../_error";

export const dynamic = "force-static";

// 簡易的な冪等性対応と再実行フック
export async function POST(request: NextRequest) {
  try {
    const idempotencyKey = request.headers.get("Idempotency-Key") || undefined;
    if (!idempotencyKey) {
      return jsonError({
        error_code: "IDEMPOTENCY_KEY_REQUIRED",
        user_message: "再実行にはIdempotency-Keyが必要です",
        retry_hint: "ユニークなIdempotency-Keyを付与して再実行してください",
      }, { status: 400 });
    }

    const existingId = getJobIdByClientToken(idempotencyKey);
    if (existingId) {
      return NextResponse.json({ jobId: existingId, status: "accepted" }, { status: 202 });
    }

    const job = createJob({ clientToken: idempotencyKey });
    // ここで本来はサーバ側の安全な再実行処理を起動する
    updateJob(job.id, { status: "queued", progress: 0 });
    return NextResponse.json({ jobId: job.id, status: "queued" }, { status: 202 });
  } catch (e) {
    return jsonError({
      error_code: "RETRY_API_FAILED",
      user_message: "再実行要求の受理に失敗しました",
      retry_hint: "数秒後に再実行してください",
    }, { status: 500 });
  }
}


