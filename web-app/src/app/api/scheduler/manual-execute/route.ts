import { NextRequest, NextResponse } from "next/server";

// NOTE: 静的ホスティング環境ではサーバーサイド実行不可のためNO-OP応答
export async function POST(_request: NextRequest) {
  return NextResponse.json(
    {
      status: "unsupported",
      message: "Static hosting environment does not support scheduler execution.",
    },
    { status: 400 },
  );
}

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
