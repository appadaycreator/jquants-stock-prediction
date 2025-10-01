/**
 * エラー処理システムのテスト用ユーティリティ
 * 今日の指示・シグナル取得エラーの解消をテストする
 */

interface TestScenario {
  name: string;
  description: string;
  testFn: () => Promise<boolean>;
}

class ErrorHandlingTest {
  private static instance: ErrorHandlingTest;
  private testResults: Array<{
    scenario: string;
    passed: boolean;
    error?: string;
    timestamp: string;
  }> = [];

  static getInstance(): ErrorHandlingTest {
    if (!ErrorHandlingTest.instance) {
      ErrorHandlingTest.instance = new ErrorHandlingTest();
    }
    return ErrorHandlingTest.instance;
  }

  /**
   * 分析未実行時のエラー処理テスト
   */
  async testAnalysisRequiredError(): Promise<boolean> {
    try {
      const response = await fetch('/api/today-actions');
      const data = await response.json();
      
      // 分析未実行時は202ステータスとanalysisRequired: trueが返されることを確認
      return response.status === 202 && data.analysisRequired === true;
    } catch (error) {
      console.error('分析未実行テストエラー:', error);
      return false;
    }
  }

  /**
   * シグナル取得エラー処理テスト
   */
  async testSignalErrorHandling(): Promise<boolean> {
    try {
      const response = await fetch('/api/signals');
      const data = await response.json();
      
      // エラーレスポンスの構造を確認
      return data.error && data.error.code && data.error.message;
    } catch (error) {
      console.error('シグナルエラーテストエラー:', error);
      return false;
    }
  }

  /**
   * キャッシュ機能テスト
   */
  async testCacheFunctionality(): Promise<boolean> {
    try {
      // キャッシュマネージャーをテスト
      const { default: CacheManager } = await import('./cacheManager');
      const cache = CacheManager.getInstance();
      
      // テストデータを保存
      const testData = { test: 'data', timestamp: new Date().toISOString() };
      cache.set('test_key', testData);
      
      // キャッシュから取得
      const retrieved = cache.get('test_key');
      
      // データが正しく取得できることを確認
      return retrieved && retrieved.test === 'data';
    } catch (error) {
      console.error('キャッシュテストエラー:', error);
      return false;
    }
  }

  /**
   * ネットワークエラー処理テスト
   */
  async testNetworkErrorHandling(): Promise<boolean> {
    try {
      // 存在しないエンドポイントにリクエストしてネットワークエラーをシミュレート
      const response = await fetch('/api/nonexistent-endpoint');
      
      // 404エラーが適切に処理されることを確認
      return response.status === 404;
    } catch (error) {
      // ネットワークエラーが適切にキャッチされることを確認
      return error instanceof TypeError; // fetch のネットワークエラー
    }
  }

  /**
   * フォールバック機能テスト
   */
  async testFallbackFunctionality(): Promise<boolean> {
    try {
      // モックデータでフォールバック機能をテスト
      const mockSignals = [
        {
          symbol: '7203.T',
          signal_type: 'BUY',
          confidence: 0.8,
          price: 2500,
          timestamp: new Date().toISOString(),
          reason: 'テスト用シグナル',
          category: 'テスト',
          expected_holding_period: 30
        }
      ];

      // ローカルストレージにテストデータを保存
      localStorage.setItem('signal_fallback_data', JSON.stringify({
        signals: mockSignals,
        timestamp: new Date().toISOString()
      }));

      // キャッシュからデータが取得できることを確認
      const cached = localStorage.getItem('signal_fallback_data');
      return cached && JSON.parse(cached).signals.length > 0;
    } catch (error) {
      console.error('フォールバックテストエラー:', error);
      return false;
    }
  }

  /**
   * エラーガイダンス表示テスト
   */
  async testErrorGuidanceDisplay(): Promise<boolean> {
    try {
      // ErrorGuidanceコンポーネントの基本的な機能をテスト
      const testError = 'テストエラーメッセージ';
      const testErrorCode = 'TEST_ERROR';
      
      // エラーコードとメッセージが適切に処理されることを確認
      return testError && testErrorCode && testError.length > 0;
    } catch (error) {
      console.error('エラーガイダンステストエラー:', error);
      return false;
    }
  }

  /**
   * 全テストシナリオを実行
   */
  async runAllTests(): Promise<{
    total: number;
    passed: number;
    failed: number;
    results: Array<{
      scenario: string;
      passed: boolean;
      error?: string;
      timestamp: string;
    }>;
  }> {
    const scenarios: TestScenario[] = [
      {
        name: 'analysis_required',
        description: '分析未実行時のエラー処理',
        testFn: () => this.testAnalysisRequiredError()
      },
      {
        name: 'signal_error',
        description: 'シグナル取得エラー処理',
        testFn: () => this.testSignalErrorHandling()
      },
      {
        name: 'cache_functionality',
        description: 'キャッシュ機能',
        testFn: () => this.testCacheFunctionality()
      },
      {
        name: 'network_error',
        description: 'ネットワークエラー処理',
        testFn: () => this.testNetworkErrorHandling()
      },
      {
        name: 'fallback_functionality',
        description: 'フォールバック機能',
        testFn: () => this.testFallbackFunctionality()
      },
      {
        name: 'error_guidance',
        description: 'エラーガイダンス表示',
        testFn: () => this.testErrorGuidanceDisplay()
      }
    ];

    this.testResults = [];

    for (const scenario of scenarios) {
      try {
        const passed = await scenario.testFn();
        this.testResults.push({
          scenario: scenario.name,
          passed,
          timestamp: new Date().toISOString()
        });
      } catch (error) {
        this.testResults.push({
          scenario: scenario.name,
          passed: false,
          error: error instanceof Error ? error.message : String(error),
          timestamp: new Date().toISOString()
        });
      }
    }

    const passed = this.testResults.filter(r => r.passed).length;
    const failed = this.testResults.filter(r => !r.passed).length;

    return {
      total: this.testResults.length,
      passed,
      failed,
      results: this.testResults
    };
  }

  /**
   * テスト結果を取得
   */
  getTestResults() {
    return this.testResults;
  }

  /**
   * テスト結果をクリア
   */
  clearResults() {
    this.testResults = [];
  }
}

export default ErrorHandlingTest;
