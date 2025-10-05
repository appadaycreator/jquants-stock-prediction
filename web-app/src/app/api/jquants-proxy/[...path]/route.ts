import { NextRequest, NextResponse } from "next/server";
import { JQuantsAuthManager } from "@/lib/jquants-auth-manager";

// 静的生成用のパラメータ
export async function generateStaticParams() {
  return [
    { path: ["token", "auth_user"] },
    { path: ["token", "auth_refresh"] },
    { path: ["prices", "daily_quotes"] },
    { path: ["prices", "weekly_quotes"] },
    { path: ["prices", "monthly_quotes"] },
  ];
}

const JQUANTS_API_BASE = "https://api.jquants.com/v1";
const ALLOWED_PATHS = ["/token/", "/prices/", "/listed/"];
const RATE_LIMIT_WINDOW = 60 * 1000; // 1分
const RATE_LIMIT_MAX_REQUESTS = 100; // 1分間に100リクエスト

// 最適化されたレート制限（メモリ効率とパフォーマンス向上）
class RateLimiter {
  private static instance: RateLimiter;
  private rateLimitMap = new Map<string, { count: number; resetTime: number }>();
  private cleanupInterval: NodeJS.Timeout;

  private constructor() {
    // 5分ごとに古いエントリをクリーンアップ
    this.cleanupInterval = setInterval(() => {
      const now = Date.now();
      for (const [key, value] of this.rateLimitMap.entries()) {
        if (now > value.resetTime) {
          this.rateLimitMap.delete(key);
        }
      }
    }, 5 * 60 * 1000);
  }

  static getInstance(): RateLimiter {
    if (!RateLimiter.instance) {
      RateLimiter.instance = new RateLimiter();
    }
    return RateLimiter.instance;
  }

  checkRateLimit(clientIp: string): boolean {
    const now = Date.now();
    const clientData = this.rateLimitMap.get(clientIp);

    if (!clientData || now > clientData.resetTime) {
      this.rateLimitMap.set(clientIp, { count: 1, resetTime: now + RATE_LIMIT_WINDOW });
      return true;
    }

    if (clientData.count >= RATE_LIMIT_MAX_REQUESTS) {
      return false;
    }

    clientData.count++;
    return true;
  }

  destroy(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
  }
}

const rateLimiter = RateLimiter.getInstance();

function generateAuthRecommendations(envVars: Record<string, boolean>): string[] {
  const recommendations: string[] = [];

  if (!envVars.hasIdToken && !envVars.hasEmail) {
    recommendations.push("JQUANTS_ID_TOKEN または JQUANTS_EMAIL を設定してください");
  }

  if (envVars.hasEmail && !envVars.hasPassword) {
    recommendations.push("JQUANTS_PASSWORD を設定してください");
  }

  if (envVars.hasPublicIdToken || envVars.hasPublicEmail) {
    recommendations.push("NEXT_PUBLIC_* 環境変数は機密情報を含むため、サーバーサイドでは使用しないでください");
  }

  if (recommendations.length === 0) {
    recommendations.push("認証設定は正常です");
  }

  return recommendations;
}

function isAllowedPath(path: string): boolean {
  return ALLOWED_PATHS.some(allowedPath => path.startsWith(allowedPath));
}

// 削除: 古いcheckRateLimit関数はRateLimiterクラスに統合済み

function getClientIp(request: NextRequest): string {
  const forwarded = request.headers.get("x-forwarded-for");
  const realIp = request.headers.get("x-real-ip");
  const remoteAddr = request.headers.get("x-remote-addr");
  
  return forwarded?.split(",")[0] || realIp || remoteAddr || "unknown";
}

export async function GET(request: NextRequest, { params }: { params: { path: string[] } }) {
  return handleProxyRequest(request, params.path, "GET");
}

export async function POST(request: NextRequest, { params }: { params: { path: string[] } }) {
  return handleProxyRequest(request, params.path, "POST");
}

async function handleProxyRequest(
  request: NextRequest,
  pathSegments: string[],
  method: string,
) {
  try {
    const path = "/" + pathSegments.join("/");
    const clientIp = getClientIp(request);

    // パス許可チェック
    if (!isAllowedPath(path)) {
      return NextResponse.json(
        { error: "Forbidden path" },
        { status: 403 },
      );
    }

    // レート制限チェック
    if (!rateLimiter.checkRateLimit(clientIp)) {
      return NextResponse.json(
        { error: "Rate limit exceeded" },
        { status: 429 },
      );
    }

    // リクエストボディの取得
    let body: string | undefined;
    if (method === "POST") {
      body = await request.text();
    }

    // クエリパラメータの取得
    const searchParams = request.nextUrl.searchParams;
    const queryString = searchParams.toString();
    const fullUrl = `${JQUANTS_API_BASE}${path}${queryString ? "?" + queryString : ""}`;

    // 認証トークンの取得
    const authManager = new JQuantsAuthManager();
    const authToken = await authManager.getValidToken();

    if (!authToken) {
      const envVars = {
        hasIdToken: !!process.env.JQUANTS_ID_TOKEN,
        hasRefreshToken: !!process.env.JQUANTS_REFRESH_TOKEN,
        hasEmail: !!process.env.JQUANTS_EMAIL,
        hasPassword: !!process.env.JQUANTS_PASSWORD,
        hasPublicIdToken: !!process.env.NEXT_PUBLIC_JQUANTS_ID_TOKEN,
        hasPublicRefreshToken: !!process.env.NEXT_PUBLIC_JQUANTS_REFRESH_TOKEN,
        hasPublicEmail: !!process.env.NEXT_PUBLIC_JQUANTS_EMAIL,
        hasPublicPassword: !!process.env.NEXT_PUBLIC_JQUANTS_PASSWORD,
      };
      
      console.error("認証トークンの取得に失敗しました", {
        path,
        method,
        clientIp,
        timestamp: new Date().toISOString(),
        envVars,
        recommendations: generateAuthRecommendations(envVars),
      });
      return NextResponse.json(
        { 
          error: "Authentication failed",
          message: "認証トークンの取得に失敗しました。環境変数を確認してください。",
          retry_hint: "check_credentials",
          debug: {
            envVars,
            recommendations: generateAuthRecommendations(envVars),
          },
        },
        { status: 401 },
      );
    }

    // J-Quants APIへのリクエスト（認証ヘッダー付き）
    console.log(`J-Quants API呼び出し: ${method} ${fullUrl}`);
    const response = await fetch(fullUrl, {
      method,
      headers: {
        "Content-Type": "application/json",
        "User-Agent": "J-Quants-Stock-Prediction/1.0",
        "Authorization": `Bearer ${authToken}`,
      },
      body,
    });

    // レスポンスの処理
    const responseData = await response.text();
    let jsonData;
    
    try {
      jsonData = JSON.parse(responseData);
    } catch (parseError) {
      console.warn("JSON解析エラー:", parseError, "Response:", responseData.substring(0, 200));
      jsonData = { data: responseData };
    }

    // エラーハンドリング
    if (!response.ok) {
      console.error(`J-Quants API Error: ${response.status} ${response.statusText}`, {
        url: fullUrl,
        method,
        path,
        clientIp,
        responseData: responseData.substring(0, 500),
        timestamp: new Date().toISOString(),
      });
      
      // 特定のエラーコードに対する処理
      switch (response.status) {
        case 401:
          return NextResponse.json(
            { 
              error: "Authentication failed",
              message: "認証に失敗しました。トークンを更新してください。",
              retry_hint: "refresh_token",
            },
            { status: 401 },
          );
        case 403:
          return NextResponse.json(
            { 
              error: "Access forbidden",
              message: "アクセスが拒否されました。",
              retry_hint: "check_permissions",
            },
            { status: 403 },
          );
        case 429:
          return NextResponse.json(
            { 
              error: "Rate limit exceeded",
              message: "レート制限に達しました。しばらく待ってから再試行してください。",
              retry_hint: "wait_and_retry",
            },
            { status: 429 },
          );
        case 500:
        case 502:
        case 503:
        case 504:
          return NextResponse.json(
            { 
              error: "Server error",
              message: "サーバーエラーが発生しました。",
              retry_hint: "retry_later",
            },
            { status: response.status },
          );
        default:
          return NextResponse.json(
            { 
              error: "API error",
              message: `API エラー: ${response.status}`,
              retry_hint: "check_status",
            },
            { status: response.status },
          );
      }
    }

    return NextResponse.json(jsonData, {
      status: response.status,
      headers: {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
      },
    });

  } catch (error) {
    console.error("プロキシエラー:", {
      error: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined,
      path,
      method,
      clientIp,
      timestamp: new Date().toISOString(),
    });
    return NextResponse.json(
      { 
        error: "Proxy error",
        message: "プロキシエラーが発生しました",
        retry_hint: "check_connection",
        debug: {
          errorType: error instanceof Error ? error.constructor.name : "Unknown",
          message: error instanceof Error ? error.message : String(error),
        },
      },
      { status: 500 },
    );
  }
}
