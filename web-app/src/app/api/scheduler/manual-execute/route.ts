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

export async function POST(request: NextRequest) {
  try {
    const scheduler = getScheduler();
    const success = scheduler.manual_execute();
    
    if (success) {
      return NextResponse.json({
        success: true,
        message: "5分ルーティンが手動実行されました",
        timestamp: new Date().toISOString(),
      });
    } else {
      return NextResponse.json(
        { 
          success: false, 
          error: "手動実行に失敗しました", 
        },
        { status: 500 },
      );
    }
  } catch (error) {
    console.error("手動実行エラー:", error);
    return NextResponse.json(
      { 
        success: false, 
        error: "手動実行中にエラーが発生しました", 
      },
      { status: 500 },
    );
  }
}
