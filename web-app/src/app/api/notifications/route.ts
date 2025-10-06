import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET(request: NextRequest) {
  try {
    // 通知ファイルのパス
    const notificationFile = path.join(process.cwd(), "data", "notifications.json");
    
    // 通知ファイルが存在するかチェック
    if (!fs.existsSync(notificationFile)) {
      return NextResponse.json({
        notifications: [],
      });
    }
    
    // 通知ファイルを読み込み
    const notificationData = JSON.parse(fs.readFileSync(notificationFile, "utf-8"));
    
    // 最近の通知を取得（最新10件）
    const recentNotifications = Array.isArray(notificationData) 
      ? notificationData.slice(-10).reverse()
      : [notificationData].filter(Boolean);
    
    return NextResponse.json({
      notifications: recentNotifications,
    });
  } catch (error) {
    console.error("通知取得エラー:", error);
    return NextResponse.json(
      { 
        notifications: [],
        error: "通知取得に失敗しました", 
      },
      { status: 500 },
    );
  }
}
