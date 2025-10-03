/**
 * 銘柄ランキングサービス
 * 本日の買い候補を生成するサービス
 */

export interface StockIndicator {
  name: string;
  value: number;
  threshold: number;
  weight: number;
  status: 'good' | 'warning' | 'bad';
}

export interface CandidateStock {
  code: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  reason: string;
  indicators: StockIndicator[];
  score: number;
  rank: number;
}

export interface RankingConfig {
  maxCandidates: number;
  minScore: number;
  indicators: {
    name: string;
    weight: number;
    threshold: number;
  }[];
}

export class RankerService {
  private static readonly DEFAULT_CONFIG: RankingConfig = {
    maxCandidates: 5,
    minScore: 0.6,
    indicators: [
      { name: 'RSI', weight: 0.2, threshold: 30 },
      { name: 'MACD', weight: 0.2, threshold: 0 },
      { name: 'Volume', weight: 0.15, threshold: 1.5 },
      { name: 'Price_Momentum', weight: 0.15, threshold: 0.05 },
      { name: 'PE_Ratio', weight: 0.1, threshold: 15 },
      { name: 'PB_Ratio', weight: 0.1, threshold: 1.2 },
      { name: 'ROE', weight: 0.1, threshold: 0.1 }
    ]
  };

  /**
   * 本日の買い候補を生成
   */
  static async generateCandidates(config?: Partial<RankingConfig>): Promise<CandidateStock[]> {
    try {
      const finalConfig = { ...RankerService.DEFAULT_CONFIG, ...config };
      
      // 株価データを取得
      const stockData = await RankerService.fetchStockData();
      
      // 各銘柄をスコアリング
      const scoredStocks = stockData.map(stock => 
        RankerService.calculateStockScore(stock, finalConfig)
      );

      // スコア順にソート
      const sortedStocks = scoredStocks
        .filter(stock => stock.score >= finalConfig.minScore)
        .sort((a, b) => b.score - a.score)
        .slice(0, finalConfig.maxCandidates);

      // ランキングを設定
      return sortedStocks.map((stock, index) => ({
        ...stock,
        rank: index + 1
      }));

    } catch (error) {
      console.error('候補生成エラー:', error);
      throw new Error('候補生成に失敗しました');
    }
  }

  /**
   * 株価データの取得
   */
  private static async fetchStockData(): Promise<any[]> {
    try {
      const response = await fetch('/api/stocks/data', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!response.ok) {
        throw new Error('株価データの取得に失敗しました');
      }

      const data = await response.json();
      return data.stocks || [];
    } catch (error) {
      console.error('株価データ取得エラー:', error);
      // モックデータを返す
      return RankerService.getMockStockData();
    }
  }

  /**
   * 銘柄のスコア計算
   */
  private static calculateStockScore(stock: any, config: RankingConfig): CandidateStock {
    const indicators: StockIndicator[] = [];
    let totalScore = 0;

    // 各指標を計算
    config.indicators.forEach(indicatorConfig => {
      const indicator = RankerService.calculateIndicator(stock, indicatorConfig);
      indicators.push(indicator);
      totalScore += indicator.value * indicator.weight;
    });

    // 理由を生成
    const reason = RankerService.generateReason(indicators);

    return {
      code: stock.code,
      name: stock.name,
      price: stock.price,
      change: stock.change,
      changePercent: stock.changePercent,
      reason,
      indicators,
      score: totalScore,
      rank: 0 // 後で設定
    };
  }

  /**
   * 個別指標の計算
   */
  private static calculateIndicator(stock: any, config: { name: string; weight: number; threshold: number }): StockIndicator {
    let value = 0;
    let status: 'good' | 'warning' | 'bad' = 'bad';

    switch (config.name) {
      case 'RSI':
        value = stock.rsi || 0;
        status = value <= config.threshold ? 'good' : value <= 70 ? 'warning' : 'bad';
        break;
      
      case 'MACD':
        value = stock.macd || 0;
        status = value >= config.threshold ? 'good' : value >= -0.1 ? 'warning' : 'bad';
        break;
      
      case 'Volume':
        value = stock.volumeRatio || 1;
        status = value >= config.threshold ? 'good' : value >= 1.2 ? 'warning' : 'bad';
        break;
      
      case 'Price_Momentum':
        value = stock.priceMomentum || 0;
        status = value >= config.threshold ? 'good' : value >= 0.02 ? 'warning' : 'bad';
        break;
      
      case 'PE_Ratio':
        value = stock.peRatio || 0;
        status = value <= config.threshold ? 'good' : value <= 20 ? 'warning' : 'bad';
        break;
      
      case 'PB_Ratio':
        value = stock.pbRatio || 0;
        status = value <= config.threshold ? 'good' : value <= 1.5 ? 'warning' : 'bad';
        break;
      
      case 'ROE':
        value = stock.roe || 0;
        status = value >= config.threshold ? 'good' : value >= 0.05 ? 'warning' : 'bad';
        break;
    }

    return {
      name: config.name,
      value,
      threshold: config.threshold,
      weight: config.weight,
      status
    };
  }

  /**
   * 理由の生成
   */
  private static generateReason(indicators: StockIndicator[]): string {
    const goodIndicators = indicators.filter(ind => ind.status === 'good');
    const warningIndicators = indicators.filter(ind => ind.status === 'warning');
    
    if (goodIndicators.length >= 3) {
      return `${goodIndicators.length}個の指標が良好です`;
    } else if (goodIndicators.length >= 2) {
      return `${goodIndicators.length}個の指標が良好、${warningIndicators.length}個が要注意です`;
    } else if (warningIndicators.length >= 3) {
      return `${warningIndicators.length}個の指標が要注意です`;
    } else {
      return '指標に注意が必要です';
    }
  }

  /**
   * モック株価データ
   */
  private static getMockStockData(): any[] {
    return [
      {
        code: '7203',
        name: 'トヨタ自動車',
        price: 2500,
        change: 50,
        changePercent: 2.04,
        rsi: 25,
        macd: 0.5,
        volumeRatio: 2.1,
        priceMomentum: 0.08,
        peRatio: 12,
        pbRatio: 1.1,
        roe: 0.15
      },
      {
        code: '6758',
        name: 'ソニーグループ',
        price: 12000,
        change: -200,
        changePercent: -1.64,
        rsi: 35,
        macd: -0.2,
        volumeRatio: 1.8,
        priceMomentum: -0.02,
        peRatio: 18,
        pbRatio: 1.3,
        roe: 0.12
      },
      {
        code: '9984',
        name: 'ソフトバンクグループ',
        price: 8000,
        change: 150,
        changePercent: 1.91,
        rsi: 28,
        macd: 0.3,
        volumeRatio: 2.5,
        priceMomentum: 0.06,
        peRatio: 14,
        pbRatio: 1.0,
        roe: 0.18
      },
      {
        code: '9432',
        name: '日本電信電話',
        price: 4500,
        change: 30,
        changePercent: 0.67,
        rsi: 40,
        macd: 0.1,
        volumeRatio: 1.2,
        priceMomentum: 0.03,
        peRatio: 16,
        pbRatio: 1.2,
        roe: 0.08
      },
      {
        code: '6861',
        name: 'キーエンス',
        price: 65000,
        change: 1000,
        changePercent: 1.56,
        rsi: 32,
        macd: 0.4,
        volumeRatio: 1.9,
        priceMomentum: 0.07,
        peRatio: 20,
        pbRatio: 1.4,
        roe: 0.14
      }
    ];
  }

  /**
   * ランキング設定の更新
   */
  static async updateRankingConfig(config: Partial<RankingConfig>): Promise<void> {
    try {
      await fetch('/api/ranking/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
    } catch (error) {
      console.error('ランキング設定更新エラー:', error);
      throw new Error('ランキング設定の更新に失敗しました');
    }
  }

  /**
   * ランキング履歴の取得
   */
  static async getRankingHistory(days: number = 7): Promise<any[]> {
    try {
      const response = await fetch(`/api/ranking/history?days=${days}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!response.ok) {
        throw new Error('ランキング履歴の取得に失敗しました');
      }

      const data = await response.json();
      return data.history || [];
    } catch (error) {
      console.error('ランキング履歴取得エラー:', error);
      return [];
    }
  }

  /**
   * パフォーマンス分析
   */
  static async analyzePerformance(candidates: CandidateStock[]): Promise<{
    averageScore: number;
    bestIndicator: string;
    worstIndicator: string;
    recommendations: string[];
  }> {
    if (candidates.length === 0) {
      return {
        averageScore: 0,
        bestIndicator: '',
        worstIndicator: '',
        recommendations: []
      };
    }

    const averageScore = candidates.reduce((sum, stock) => sum + stock.score, 0) / candidates.length;
    
    // 指標別の分析
    const indicatorStats = new Map<string, { total: number; count: number }>();
    
    candidates.forEach(stock => {
      stock.indicators.forEach(indicator => {
        const current = indicatorStats.get(indicator.name) || { total: 0, count: 0 };
        current.total += indicator.value;
        current.count += 1;
        indicatorStats.set(indicator.name, current);
      });
    });

    let bestIndicator = '';
    let worstIndicator = '';
    let bestAvg = -Infinity;
    let worstAvg = Infinity;

    indicatorStats.forEach((stats, name) => {
      const avg = stats.total / stats.count;
      if (avg > bestAvg) {
        bestAvg = avg;
        bestIndicator = name;
      }
      if (avg < worstAvg) {
        worstAvg = avg;
        worstIndicator = name;
      }
    });

    // 推奨事項の生成
    const recommendations: string[] = [];
    if (averageScore < 0.7) {
      recommendations.push('全体的なスコアが低いため、より厳しい選別基準を検討してください');
    }
    if (bestIndicator && worstIndicator) {
      recommendations.push(`${bestIndicator}が最も良好な指標です`);
      recommendations.push(`${worstIndicator}の改善が必要です`);
    }

    return {
      averageScore,
      bestIndicator,
      worstIndicator,
      recommendations
    };
  }
}
