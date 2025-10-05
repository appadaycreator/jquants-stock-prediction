import { NextRequest, NextResponse } from "next/server";
import { JQuantsAuthManager } from "@/lib/jquants-auth-manager";

export async function POST(request: NextRequest) {
  try {
    const authManager = new JQuantsAuthManager();
    
    // 環境変数の確認
    const envStatus = {
      hasIdToken: !!process.env.JQUANTS_ID_TOKEN,
      hasRefreshToken: !!process.env.JQUANTS_REFRESH_TOKEN,
      hasEmail: !!process.env.JQUANTS_EMAIL,
      hasPassword: !!process.env.JQUANTS_PASSWORD,
    };

    // 認証方法の選択
    let newToken: string | null = null;
    let authMethod = "";

    // 1. リフレッシュトークンで更新を試行
    if (envStatus.hasRefreshToken) {
      console.log("リフレッシュトークンで更新を試行...");
      newToken = await authManager.refreshIdToken(process.env.JQUANTS_REFRESH_TOKEN!);
      if (newToken) {
        authMethod = "refresh_token";
      }
    }

    // 2. メール/パスワードで新規取得
    if (!newToken && envStatus.hasEmail && envStatus.hasPassword) {
      console.log("メール/パスワードで新規認証を試行...");
      const newTokens = await authManager.getNewTokens(
        process.env.JQUANTS_EMAIL!,
        process.env.JQUANTS_PASSWORD!,
      );
      if (newTokens) {
        newToken = newTokens.idToken;
        authMethod = "email_password";
      }
    }

    if (!newToken) {
      return NextResponse.json(
        {
          status: "error",
          message: "認証トークンの取得に失敗しました",
          timestamp: new Date().toISOString(),
          envStatus,
          recommendations: generateRefreshRecommendations(envStatus),
        },
        { status: 401 },
      );
    }

    // 新しいトークンの有効性をテスト
    const isTokenValid = await authManager.testTokenWithAPI(newToken);
    
    return NextResponse.json({
      status: "success",
      message: "認証トークンの更新に成功しました",
      timestamp: new Date().toISOString(),
      authMethod,
      tokenLength: newToken.length,
      isTokenValid,
      recommendations: [
        "新しいトークンが正常に取得されました",
        "環境変数 JQUANTS_ID_TOKEN を更新してください",
        "サーバーを再起動して新しいトークンを使用してください",
      ],
    });

  } catch (error) {
    console.error("認証トークン更新エラー:", error);
    return NextResponse.json(
      {
        status: "error",
        message: "認証トークンの更新中にエラーが発生しました",
        error: error instanceof Error ? error.message : "Unknown error",
        timestamp: new Date().toISOString(),
      },
      { status: 500 },
    );
  }
}

function generateRefreshRecommendations(envStatus: Record<string, boolean>): string[] {
  const recommendations: string[] = [];

  if (!envStatus.hasRefreshToken && !envStatus.hasEmail) {
    recommendations.push("JQUANTS_REFRESH_TOKEN または JQUANTS_EMAIL を設定してください");
  }

  if (envStatus.hasEmail && !envStatus.hasPassword) {
    recommendations.push("JQUANTS_PASSWORD を設定してください");
  }

  if (!envStatus.hasIdToken) {
    recommendations.push("JQUANTS_ID_TOKEN を設定してください");
  }

  if (recommendations.length === 0) {
    recommendations.push("認証設定は正常です。トークンの有効期限を確認してください");
  }

  return recommendations;
}
