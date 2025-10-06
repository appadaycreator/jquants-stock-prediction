import { NextRequest, NextResponse } from "next/server";
import { AutomatedScheduler } from "../../../../../../automated_scheduler";

// スケジューラーインスタンス（シングルトン）
let scheduler: AutomatedScheduler | null = null;

function getScheduler() {
  if (!scheduler) {
    scheduler = new AutomatedScheduler();
  }
  return scheduler;
}

export async function GET(request: NextRequest) {
  try {
    const scheduler = getScheduler();
    const status = scheduler.get_status();
    
    return NextResponse.json(status);
  } catch (error) {
    console.error("スケジューラーステータス取得エラー:", error);
    return NextResponse.json(
      { error: "ステータス取得に失敗しました" },
      { status: 500 },
    );
  }
}
