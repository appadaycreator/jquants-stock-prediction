/**
 * J-Quants API アダプタ（テスト用）
 * 実際のAPI呼び出しをモック化し、テスト環境で使用
 */

export interface ConnectionResult {
  success: boolean;
  message: string;
  metrics?: any;
}

/**
 * 接続テスト関数
 * テスト環境では静的データを使用して接続をシミュレート
 */
export async function testConnection(): Promise<ConnectionResult> {
  try {
    // 静的データファイルから接続テスト用のデータを取得
    const { resolveStaticPath } = await import("@/lib/path");
    const response = await fetch(resolveStaticPath("/data/listed_index.json"), {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    
    return {
      success: true,
      message: `接続成功: ${data?.stocks?.length || 0}件の銘柄データを取得`,
      metrics: {
        totalRequests: 1,
        successfulRequests: 1,
        failedRequests: 0,
        averageResponseTime: 100,
      },
    };
  } catch (error) {
    return {
      success: false,
      message: `接続失敗: ${error instanceof Error ? error.message : "不明なエラー"}`,
      metrics: {
        totalRequests: 1,
        successfulRequests: 0,
        failedRequests: 1,
        averageResponseTime: 0,
      },
    };
  }
}

/**
 * 株価データ取得関数（テスト用）
 */
export async function getStockData(symbol: string, startDate: string, endDate: string): Promise<any[]> {
  try {
    // 静的データファイルから株価データを取得（basePath対応）
    const { resolveStaticPath } = await import("@/lib/path");
    const response = await fetch(resolveStaticPath(`/data/stock_${symbol}.json`), {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    return data?.data || [];
  } catch (error) {
    console.error("株価データ取得エラー:", error);
    return [];
  }
}

/**
 * 全銘柄一覧取得関数（テスト用）
 */
export async function getAllSymbols(): Promise<Array<{ code: string; name: string; sector?: string }>> {
  try {
    const { resolveStaticPath } = await import("@/lib/path");
    const response = await fetch(resolveStaticPath("/data/listed_index.json"), {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const responseText = await response.text();
    let data;
    
    try {
      data = JSON.parse(responseText);
    } catch (parseError) {
      console.error("JSON解析エラー:", {
        error: parseError,
        position: (parseError as any)?.pos || 'unknown',
        responseLength: responseText.length,
        responsePreview: responseText.substring(0, 500),
        timestamp: new Date().toISOString(),
      });
      throw new Error(`JSON解析エラー: ${parseError.message}`);
    }
    
    const list: any[] = data?.stocks || data?.data || [];
    
    return list.map((item: any) => ({
      code: item?.code || item?.Code,
      name: item?.name || item?.CompanyName || item?.CompanyNameJa || item?.CompanyNameJp || item?.CompanyNameJPN,
      sector: item?.sector || item?.Sector33 || item?.SectorName,
    })).filter((s: any) => !!s.code && !!s.name);
  } catch (error) {
    console.error("全銘柄一覧取得エラー:", {
      error: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString(),
    });
    return [];
  }
}
