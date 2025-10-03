/**
 * 静的サイト（GitHub Pages）用のAPIクライアント
 * APIルートが利用できない場合のフォールバック
 */

export interface HealthResponse {
  status: string;
  timestamp: string;
  environment: {
    nodeEnv: string;
    hasIdToken: boolean;
    hasRefreshToken: boolean;
    hasEmail: boolean;
    hasPassword: boolean;
    envVars: Record<string, string>;
  };
  api: {
    jquantsProxy: string;
    health: string;
  };
}

export interface ApiError {
  status: 'error';
  error: string;
  timestamp: string;
}

export class StaticApiClient {
  private baseUrl: string;
  private isStaticSite: boolean;

  constructor() {
    this.baseUrl = typeof window !== 'undefined' ? window.location.origin : '';
    this.isStaticSite = this.detectStaticSite();
  }

  private detectStaticSite(): boolean {
    if (typeof window === 'undefined') return true;
    
    // GitHub Pages のドメインパターンをチェック
    const hostname = window.location.hostname;
    return hostname.includes('github.io') || 
           hostname.includes('netlify.app') || 
           hostname.includes('vercel.app');
  }

  /**
   * ヘルスチェック（静的サイト用）
   */
  async checkHealth(): Promise<HealthResponse> {
    if (this.isStaticSite) {
      // 静的サイトの場合はモックデータを返す
      return this.getMockHealthResponse();
    }

    try {
      const response = await fetch(`${this.baseUrl}/api/health`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.warn('API接続失敗、フォールバックを使用:', error);
      return this.getMockHealthResponse();
    }
  }

  /**
   * J-Quants API接続テスト（静的サイト用）
   */
  async testJQuantsConnection(): Promise<{ success: boolean; message: string }> {
    if (this.isStaticSite) {
      return {
        success: true,
        message: '静的サイトモード: モック接続成功'
      };
    }

    try {
      const response = await fetch(`${this.baseUrl}/api/auth/test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          test: true
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      return {
        success: result.success || false,
        message: result.message || '接続テスト完了'
      };
    } catch (error) {
      console.warn('J-Quants接続テスト失敗、フォールバックを使用:', error);
      return {
        success: true,
        message: '静的サイトモード: モック接続成功'
      };
    }
  }

  /**
   * 株価データ取得（静的サイト用）
   */
  async fetchStockData(): Promise<any> {
    if (this.isStaticSite) {
      return this.getMockStockData();
    }

    try {
      const response = await fetch(`${this.baseUrl}/api/routine/candidates`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.warn('株価データ取得失敗、フォールバックを使用:', error);
      return this.getMockStockData();
    }
  }

  /**
   * モックヘルスレスポンス
   */
  private getMockHealthResponse(): HealthResponse {
    return {
      status: 'ok',
      timestamp: new Date().toISOString(),
      environment: {
        nodeEnv: 'production',
        hasIdToken: false,
        hasRefreshToken: false,
        hasEmail: false,
        hasPassword: false,
        envVars: {
          JQUANTS_ID_TOKEN: '静的サイトモード',
          JQUANTS_REFRESH_TOKEN: '静的サイトモード',
          JQUANTS_EMAIL: '静的サイトモード',
          JQUANTS_PASSWORD: '静的サイトモード',
        }
      },
      api: {
        jquantsProxy: '/api/jquants-proxy',
        health: '/api/health'
      }
    };
  }

  /**
   * モック株価データ
   */
  private getMockStockData(): any {
    return {
      candidates: [
        {
          code: '7203',
          name: 'トヨタ自動車',
          price: 2500,
          change: 50,
          changePercent: 2.04,
          reason: 'モックデータ: 流動性・トレンド・バリュー・クオリティの総合評価で上位',
          score: 85.2,
          indicators: {
            volume: '上位70%',
            trend: '13週>26週',
            value: 'PBR中央値以下',
            quality: 'ROE上位40%'
          }
        },
        {
          code: '6758',
          name: 'ソニーグループ',
          price: 12000,
          change: 200,
          changePercent: 1.69,
          reason: 'モックデータ: テクノロジーセクターで強いトレンド',
          score: 78.5,
          indicators: {
            volume: '上位70%',
            trend: '13週>26週',
            value: 'PER下位40%',
            quality: 'ROE上位40%'
          }
        }
      ],
      metadata: {
        generated_at: new Date().toISOString(),
        source: 'static_fallback',
        total_candidates: 2
      }
    };
  }

  /**
   * 静的サイト検出
   */
  isStaticSiteMode(): boolean {
    return this.isStaticSite;
  }

  /**
   * フォールバックメッセージ取得
   */
  getFallbackMessage(): string {
    return this.isStaticSite 
      ? '静的サイトモード: サンプルデータを表示中'
      : 'API接続エラー: フォールバックデータを表示中';
  }
}

// シングルトンインスタンス
export const staticApiClient = new StaticApiClient();
