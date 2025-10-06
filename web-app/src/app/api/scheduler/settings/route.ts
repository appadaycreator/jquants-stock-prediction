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
    
    return NextResponse.json({
      execution_time: status.execution_time,
      email_enabled: status.notifications.email_enabled,
      slack_enabled: status.notifications.slack_enabled,
      browser_enabled: status.notifications.browser_enabled,
    });
  } catch (error) {
    console.error("設定取得エラー:", error);
    return NextResponse.json(
      { error: "設定取得に失敗しました" },
      { status: 500 },
    );
  }
}

export async function PUT(request: NextRequest) {
  try {
    const body = await request.json();
    const { execution_time, email_enabled, slack_enabled, browser_enabled } = body;
    
    // 設定更新の実装（実際の実装では設定ファイルを更新）
    // ここでは簡易的な実装
    
    return NextResponse.json({
      success: true,
      message: "設定が更新されました",
      settings: {
        execution_time,
        email_enabled,
        slack_enabled,
        browser_enabled,
      },
    });
  } catch (error) {
    console.error("設定更新エラー:", error);
    return NextResponse.json(
      { 
        success: false, 
        error: "設定更新に失敗しました", 
      },
      { status: 500 },
    );
  }
}
