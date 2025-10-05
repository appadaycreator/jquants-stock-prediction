import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const { webhook_url, channel, username, icon_emoji, title, message, priority } = await request.json();

    if (!webhook_url || !title || !message) {
      return NextResponse.json(
        { error: "必須フィールドが不足しています" },
        { status: 400 },
      );
    }

    // 優先度に応じた色を設定
    const getColor = (priority: string) => {
      switch (priority) {
        case "critical":
          return "#ff0000";
        case "high":
          return "#ff6600";
        case "medium":
          return "#ffcc00";
        case "low":
          return "#00cc00";
        default:
          return "#36a64f";
      }
    };

    // Slackメッセージの構築
    const slackMessage = {
      channel: channel || "#stock-analysis",
      username: username || "株価分析Bot",
      icon_emoji: icon_emoji || ":chart_with_upwards_trend:",
      text: title,
      attachments: [
        {
          color: getColor(priority),
          text: message,
          footer: "5分ルーティン自動化システム",
          ts: Math.floor(Date.now() / 1000),
        },
      ],
    };

    // Slack Webhook送信
    const response = await fetch(webhook_url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(slackMessage),
    });

    if (!response.ok) {
      throw new Error(`Slack送信失敗: ${response.status}`);
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Slack送信エラー:", error);
    return NextResponse.json(
      { error: "Slack通知送信に失敗しました" },
      { status: 500 },
    );
  }
}
