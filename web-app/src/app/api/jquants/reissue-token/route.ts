import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

/**
 * jQuants IDトークン再発行API
 * サーバーサイドでトークンを再発行し、環境変数に保存
 */
export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json();

    if (!email || !password) {
      return NextResponse.json(
        { error: "メールアドレスとパスワードが必要です" },
        { status: 400 },
      );
    }

    console.log("🔄 jQuants IDトークン再発行を開始...");

    // Step 1: リフレッシュトークンを取得
    const authResponse = await fetch("https://api.jquants.com/v1/token/auth_user", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        mailaddress: email,
        password: password,
      }),
    });

    if (!authResponse.ok) {
      const errorData = await authResponse.json().catch(() => ({}));
      console.error("認証エラー:", errorData);
      return NextResponse.json(
        { 
          error: "jQuants認証に失敗しました", 
          details: errorData, 
        },
        { status: 401 },
      );
    }

    const authData = await authResponse.json();
    console.log("🔍 認証レスポンス:", authData);
    
    // jQuants APIの実際のレスポンス形式を確認
    const refreshToken = authData.refreshToken || authData.refreshtoken;

    if (!refreshToken) {
      console.error("❌ リフレッシュトークンが見つかりません:", authData);
      return NextResponse.json(
        { 
          error: "リフレッシュトークンの取得に失敗しました",
          details: authData,
        },
        { status: 401 },
      );
    }

    console.log("✅ リフレッシュトークンを取得しました");

    // Step 2: IDトークンを取得
    console.log("🔄 IDトークン取得リクエスト:", { refreshtoken: refreshToken });
    
    // jQuants APIのauth_refreshエンドポイントはクエリパラメータを使用
    const tokenUrl = `https://api.jquants.com/v1/token/auth_refresh?refreshtoken=${encodeURIComponent(refreshToken)}`;
    
    const tokenResponse = await fetch(tokenUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!tokenResponse.ok) {
      const errorData = await tokenResponse.json().catch(() => ({}));
      console.error("トークン取得エラー:", errorData);
      return NextResponse.json(
        { 
          error: "IDトークンの取得に失敗しました", 
          details: errorData, 
        },
        { status: 401 },
      );
    }

    const tokenData = await tokenResponse.json();
    console.log("🔍 トークンレスポンス:", tokenData);
    
    // jQuants APIのレスポンス形式: idtoken (小文字) または idToken (大文字)
    const idToken = tokenData.idtoken || tokenData.idToken;

    if (!idToken) {
      console.error("❌ IDトークンが見つかりません:", tokenData);
      return NextResponse.json(
        { 
          error: "IDトークンの取得に失敗しました",
          details: tokenData,
        },
        { status: 401 },
      );
    }

    console.log("✅ IDトークンを取得しました");

    // Step 3: トークンをテスト
    const testResponse = await fetch("https://api.jquants.com/v1/listed/info", {
      headers: {
        "Authorization": `Bearer ${idToken}`,
      },
    });

    if (!testResponse.ok) {
      console.error("トークンテストエラー:", testResponse.status);
      return NextResponse.json(
        { error: "トークンテストに失敗しました" },
        { status: 401 },
      );
    }

    console.log("✅ トークンテスト成功");

    // Step 4: 環境変数ファイルに保存（開発環境のみ）
    if (process.env.NODE_ENV === "development") {
      try {
        const envPath = path.join(process.cwd(), ".env");
        
        // 既存の.envファイルを読み込み（存在する場合）
        let existingContent = "";
        if (fs.existsSync(envPath)) {
          existingContent = fs.readFileSync(envPath, "utf8");
        }
        
        // 新しいトークン情報を追加/更新
        const newEnvContent = `# jQuants API設定
JQUANTS_EMAIL=${email}
JQUANTS_PASSWORD=${password}
JQUANTS_ID_TOKEN=${idToken}

# その他の設定
NODE_ENV=development
`;

        fs.writeFileSync(envPath, newEnvContent);
        console.log("✅ 環境変数ファイルに保存しました");
      } catch (error) {
        console.warn("⚠️ 環境変数ファイルの保存に失敗:", error);
        // ファイル保存の失敗は致命的ではないので、処理を続行
      }
    }

    return NextResponse.json({
      success: true,
      message: "IDトークンの再発行が完了しました",
      token: {
        idToken: idToken,
        refreshToken: refreshToken,
        expiresIn: 86400, // 24時間
        issuedAt: new Date().toISOString(),
      },
    });

  } catch (error) {
    console.error("トークン再発行エラー:", error);
    return NextResponse.json(
      { 
        error: "トークン再発行処理中にエラーが発生しました",
        details: error instanceof Error ? error.message : "不明なエラー",
      },
      { status: 500 },
    );
  }
}
