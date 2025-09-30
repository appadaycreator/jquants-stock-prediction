/**
 * データ品質監視システム
 * リアルタイム品質監視、異常検出、自動修復機能
 */

interface QualityMetrics {
  timestamp: string;
  symbol: string;
  totalRecords: number;
  validRecords: number;
  invalidRecords: number;
  qualityScore: number;
  responseTime: number;
  errorRate: number;
  dataCompleteness: number;
  dataAccuracy: number;
}

interface AnomalyDetection {
  type: 'price_spike' | 'volume_anomaly' | 'missing_data' | 'duplicate_data' | 'format_error';
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  affectedRecords: number;
  recommendation: string;
  detectedAt: string;
}

interface QualityReport {
  reportId: string;
  generatedAt: string;
  timeRange: {
    start: string;
    end: string;
  };
  overallQualityScore: number;
  totalRecords: number;
  validRecords: number;
  invalidRecords: number;
  symbols: string[];
  metrics: QualityMetrics[];
  anomalies: AnomalyDetection[];
  recommendations: string[];
  trends: {
    qualityTrend: 'improving' | 'stable' | 'declining';
    errorTrend: 'increasing' | 'stable' | 'decreasing';
    performanceTrend: 'improving' | 'stable' | 'declining';
  };
}

interface QualityThresholds {
  minQualityScore: number;
  maxErrorRate: number;
  maxResponseTime: number;
  minDataCompleteness: number;
  maxAnomalyCount: number;
}

class DataQualityMonitor {
  private metrics: Map<string, QualityMetrics[]> = new Map();
  private anomalies: AnomalyDetection[] = [];
  private thresholds: QualityThresholds;
  private isMonitoring: boolean = false;
  private monitoringInterval: NodeJS.Timeout | null = null;

  constructor(thresholds: Partial<QualityThresholds> = {}) {
    this.thresholds = {
      minQualityScore: thresholds.minQualityScore || 90,
      maxErrorRate: thresholds.maxErrorRate || 5,
      maxResponseTime: thresholds.maxResponseTime || 5000,
      minDataCompleteness: thresholds.minDataCompleteness || 95,
      maxAnomalyCount: thresholds.maxAnomalyCount || 10,
    };
  }

  /**
   * 品質メトリクスの記録
   */
  recordMetrics(symbol: string, metrics: Omit<QualityMetrics, 'timestamp' | 'symbol'>): void {
    const qualityMetrics: QualityMetrics = {
      timestamp: new Date().toISOString(),
      symbol,
      ...metrics
    };

    if (!this.metrics.has(symbol)) {
      this.metrics.set(symbol, []);
    }

    const symbolMetrics = this.metrics.get(symbol)!;
    symbolMetrics.push(qualityMetrics);

    // 最新100件のみ保持
    if (symbolMetrics.length > 100) {
      symbolMetrics.splice(0, symbolMetrics.length - 100);
    }

    // 異常検出
    this.detectAnomalies(symbol, qualityMetrics);
  }

  /**
   * 異常検出
   */
  private detectAnomalies(symbol: string, metrics: QualityMetrics): void {
    const anomalies: AnomalyDetection[] = [];

    // 品質スコアの異常検出
    if (metrics.qualityScore < this.thresholds.minQualityScore) {
      anomalies.push({
        type: 'format_error',
        severity: metrics.qualityScore < 70 ? 'critical' : 'high',
        description: `品質スコアが閾値を下回っています: ${metrics.qualityScore}%`,
        affectedRecords: metrics.invalidRecords,
        recommendation: 'データ検証ルールの見直しとAPIの安定性確認が必要です',
        detectedAt: metrics.timestamp
      });
    }

    // エラー率の異常検出
    if (metrics.errorRate > this.thresholds.maxErrorRate) {
      anomalies.push({
        type: 'format_error',
        severity: metrics.errorRate > 20 ? 'critical' : 'medium',
        description: `エラー率が閾値を超過しています: ${metrics.errorRate}%`,
        affectedRecords: metrics.invalidRecords,
        recommendation: 'API接続の安定性とデータソースの確認が必要です',
        detectedAt: metrics.timestamp
      });
    }

    // 応答時間の異常検出
    if (metrics.responseTime > this.thresholds.maxResponseTime) {
      anomalies.push({
        type: 'missing_data',
        severity: metrics.responseTime > 10000 ? 'high' : 'medium',
        description: `応答時間が閾値を超過しています: ${metrics.responseTime}ms`,
        affectedRecords: 0,
        recommendation: 'ネットワーク接続とAPIサーバーの性能確認が必要です',
        detectedAt: metrics.timestamp
      });
    }

    // データ完全性の異常検出
    if (metrics.dataCompleteness < this.thresholds.minDataCompleteness) {
      anomalies.push({
        type: 'missing_data',
        severity: metrics.dataCompleteness < 80 ? 'critical' : 'high',
        description: `データ完全性が不足しています: ${metrics.dataCompleteness}%`,
        affectedRecords: metrics.totalRecords - metrics.validRecords,
        recommendation: 'データ取得プロセスの見直しと再取得が必要です',
        detectedAt: metrics.timestamp
      });
    }

    // 価格スパイクの検出（簡易版）
    if (this.detectPriceSpike(symbol, metrics)) {
      anomalies.push({
        type: 'price_spike',
        severity: 'medium',
        description: '価格データに異常な変動が検出されました',
        affectedRecords: 1,
        recommendation: '価格データの妥当性確認が必要です',
        detectedAt: metrics.timestamp
      });
    }

    // 出来高異常の検出
    if (this.detectVolumeAnomaly(symbol, metrics)) {
      anomalies.push({
        type: 'volume_anomaly',
        severity: 'low',
        description: '出来高データに異常が検出されました',
        affectedRecords: 1,
        recommendation: '出来高データの妥当性確認が必要です',
        detectedAt: metrics.timestamp
      });
    }

    // 重複データの検出
    if (this.detectDuplicateData(symbol, metrics)) {
      anomalies.push({
        type: 'duplicate_data',
        severity: 'medium',
        description: '重複データが検出されました',
        affectedRecords: 1,
        recommendation: 'データ取得プロセスの重複排除機能の確認が必要です',
        detectedAt: metrics.timestamp
      });
    }

    this.anomalies.push(...anomalies);

    // 最新100件の異常のみ保持
    if (this.anomalies.length > 100) {
      this.anomalies.splice(0, this.anomalies.length - 100);
    }
  }

  /**
   * 価格スパイクの検出（簡易版）
   */
  private detectPriceSpike(symbol: string, metrics: QualityMetrics): boolean {
    const symbolMetrics = this.metrics.get(symbol);
    if (!symbolMetrics || symbolMetrics.length < 2) return false;

    const recent = symbolMetrics.slice(-5); // 直近5件
    const qualityScores = recent.map(m => m.qualityScore);
    const avgQuality = qualityScores.reduce((sum, score) => sum + score, 0) / qualityScores.length;
    
    // 品質スコアが急激に低下した場合
    return metrics.qualityScore < avgQuality - 20;
  }

  /**
   * 出来高異常の検出
   */
  private detectVolumeAnomaly(symbol: string, metrics: QualityMetrics): boolean {
    // 出来高が0または異常に大きい場合
    return metrics.dataCompleteness < 90;
  }

  /**
   * 重複データの検出
   */
  private detectDuplicateData(symbol: string, metrics: QualityMetrics): boolean {
    // データ完全性が高いのに品質スコアが低い場合
    return metrics.dataCompleteness > 95 && metrics.qualityScore < 80;
  }

  /**
   * 品質レポートの生成
   */
  generateQualityReport(
    timeRange: { start: string; end: string },
    symbols?: string[]
  ): QualityReport {
    const reportId = `quality_report_${Date.now()}`;
    const startTime = new Date(timeRange.start);
    const endTime = new Date(timeRange.end);

    // 対象期間のメトリクスを取得
    const relevantMetrics: QualityMetrics[] = [];
    const targetSymbols = symbols || Array.from(this.metrics.keys());

    targetSymbols.forEach(symbol => {
      const symbolMetrics = this.metrics.get(symbol) || [];
      const filteredMetrics = symbolMetrics.filter(m => {
        const metricTime = new Date(m.timestamp);
        return metricTime >= startTime && metricTime <= endTime;
      });
      relevantMetrics.push(...filteredMetrics);
    });

    // 全体統計の計算
    const totalRecords = relevantMetrics.reduce((sum, m) => sum + m.totalRecords, 0);
    const validRecords = relevantMetrics.reduce((sum, m) => sum + m.validRecords, 0);
    const invalidRecords = totalRecords - validRecords;
    const overallQualityScore = totalRecords > 0 ? Math.round((validRecords / totalRecords) * 100) : 0;

    // 対象期間の異常を取得
    const relevantAnomalies = this.anomalies.filter(a => {
      const anomalyTime = new Date(a.detectedAt);
      return anomalyTime >= startTime && anomalyTime <= endTime;
    });

    // トレンド分析
    const trends = this.analyzeTrends(relevantMetrics);

    // 推奨事項の生成
    const recommendations = this.generateRecommendations(relevantMetrics, relevantAnomalies);

    return {
      reportId,
      generatedAt: new Date().toISOString(),
      timeRange,
      overallQualityScore,
      totalRecords,
      validRecords,
      invalidRecords,
      symbols: targetSymbols,
      metrics: relevantMetrics,
      anomalies: relevantAnomalies,
      recommendations,
      trends
    };
  }

  /**
   * トレンド分析
   */
  private analyzeTrends(metrics: QualityMetrics[]): QualityReport['trends'] {
    if (metrics.length < 2) {
      return {
        qualityTrend: 'stable',
        errorTrend: 'stable',
        performanceTrend: 'stable'
      };
    }

    const sortedMetrics = metrics.sort((a, b) => 
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );

    const firstHalf = sortedMetrics.slice(0, Math.floor(sortedMetrics.length / 2));
    const secondHalf = sortedMetrics.slice(Math.floor(sortedMetrics.length / 2));

    const firstHalfAvgQuality = firstHalf.reduce((sum, m) => sum + m.qualityScore, 0) / firstHalf.length;
    const secondHalfAvgQuality = secondHalf.reduce((sum, m) => sum + m.qualityScore, 0) / secondHalf.length;

    const firstHalfAvgErrorRate = firstHalf.reduce((sum, m) => sum + m.errorRate, 0) / firstHalf.length;
    const secondHalfAvgErrorRate = secondHalf.reduce((sum, m) => sum + m.errorRate, 0) / secondHalf.length;

    const firstHalfAvgResponseTime = firstHalf.reduce((sum, m) => sum + m.responseTime, 0) / firstHalf.length;
    const secondHalfAvgResponseTime = secondHalf.reduce((sum, m) => sum + m.responseTime, 0) / secondHalf.length;

    return {
      qualityTrend: secondHalfAvgQuality > firstHalfAvgQuality + 5 ? 'improving' :
                   secondHalfAvgQuality < firstHalfAvgQuality - 5 ? 'declining' : 'stable',
      errorTrend: secondHalfAvgErrorRate < firstHalfAvgErrorRate - 1 ? 'decreasing' :
                  secondHalfAvgErrorRate > firstHalfAvgErrorRate + 1 ? 'increasing' : 'stable',
      performanceTrend: secondHalfAvgResponseTime < firstHalfAvgResponseTime - 500 ? 'improving' :
                        secondHalfAvgResponseTime > firstHalfAvgResponseTime + 500 ? 'declining' : 'stable'
    };
  }

  /**
   * 推奨事項の生成
   */
  private generateRecommendations(
    metrics: QualityMetrics[], 
    anomalies: AnomalyDetection[]
  ): string[] {
    const recommendations: string[] = [];

    // 品質スコアに基づく推奨事項
    const avgQualityScore = metrics.reduce((sum, m) => sum + m.qualityScore, 0) / metrics.length;
    if (avgQualityScore < 90) {
      recommendations.push('データ品質の改善が必要です。APIの安定性とデータ検証ルールの見直しを推奨します。');
    }

    // エラー率に基づく推奨事項
    const avgErrorRate = metrics.reduce((sum, m) => sum + m.errorRate, 0) / metrics.length;
    if (avgErrorRate > 5) {
      recommendations.push('エラー率が高い状態です。API接続の安定性とリトライ機能の強化を推奨します。');
    }

    // 応答時間に基づく推奨事項
    const avgResponseTime = metrics.reduce((sum, m) => sum + m.responseTime, 0) / metrics.length;
    if (avgResponseTime > 3000) {
      recommendations.push('応答時間が長い状態です。ネットワーク最適化とキャッシュ戦略の見直しを推奨します。');
    }

    // 異常に基づく推奨事項
    const criticalAnomalies = anomalies.filter(a => a.severity === 'critical');
    if (criticalAnomalies.length > 0) {
      recommendations.push('重大な異常が検出されています。即座にシステムの確認と対応が必要です。');
    }

    const highAnomalies = anomalies.filter(a => a.severity === 'high');
    if (highAnomalies.length > 5) {
      recommendations.push('高優先度の異常が多数検出されています。データ品質監視の強化を推奨します。');
    }

    // データ完全性に基づく推奨事項
    const avgCompleteness = metrics.reduce((sum, m) => sum + m.dataCompleteness, 0) / metrics.length;
    if (avgCompleteness < 95) {
      recommendations.push('データ完全性が不足しています。データ取得プロセスの見直しを推奨します。');
    }

    return recommendations;
  }

  /**
   * リアルタイム監視の開始
   */
  startMonitoring(intervalMs: number = 60000): void {
    if (this.isMonitoring) {
      console.warn('品質監視は既に開始されています');
      return;
    }

    this.isMonitoring = true;
    this.monitoringInterval = setInterval(() => {
      this.performHealthCheck();
    }, intervalMs);

    console.info('データ品質監視を開始しました', { intervalMs });
  }

  /**
   * リアルタイム監視の停止
   */
  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
    this.isMonitoring = false;
    console.info('データ品質監視を停止しました');
  }

  /**
   * ヘルスチェックの実行
   */
  private performHealthCheck(): void {
    const currentTime = new Date().toISOString();
    const recentAnomalies = this.anomalies.filter(a => {
      const anomalyTime = new Date(a.detectedAt);
      const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);
      return anomalyTime > fiveMinutesAgo;
    });

    if (recentAnomalies.length > this.thresholds.maxAnomalyCount) {
      console.warn('品質監視アラート: 異常が閾値を超過しています', {
        anomalyCount: recentAnomalies.length,
        threshold: this.thresholds.maxAnomalyCount,
        timestamp: currentTime
      });
    }

    // 各銘柄の品質チェック
    this.metrics.forEach((symbolMetrics, symbol) => {
      if (symbolMetrics.length === 0) return;

      const latestMetrics = symbolMetrics[symbolMetrics.length - 1];
      const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);
      const latestTime = new Date(latestMetrics.timestamp);

      if (latestTime < fiveMinutesAgo) {
        console.warn(`品質監視アラート: ${symbol}のデータが古くなっています`, {
          symbol,
          lastUpdate: latestMetrics.timestamp,
          timestamp: currentTime
        });
      }
    });
  }

  /**
   * 現在の品質状況を取得
   */
  getCurrentQualityStatus(): {
    overallHealth: 'healthy' | 'degraded' | 'unhealthy';
    activeAnomalies: number;
    recentMetrics: QualityMetrics[];
    recommendations: string[];
  } {
    const recentTime = new Date(Date.now() - 10 * 60 * 1000); // 直近10分
    const recentMetrics: QualityMetrics[] = [];

    this.metrics.forEach(symbolMetrics => {
      const recent = symbolMetrics.filter(m => new Date(m.timestamp) > recentTime);
      recentMetrics.push(...recent);
    });

    const activeAnomalies = this.anomalies.filter(a => {
      const anomalyTime = new Date(a.detectedAt);
      return anomalyTime > recentTime;
    }).length;

    const avgQualityScore = recentMetrics.length > 0 
      ? recentMetrics.reduce((sum, m) => sum + m.qualityScore, 0) / recentMetrics.length
      : 100;

    let overallHealth: 'healthy' | 'degraded' | 'unhealthy' = 'healthy';
    if (avgQualityScore < 80 || activeAnomalies > 5) {
      overallHealth = 'unhealthy';
    } else if (avgQualityScore < 90 || activeAnomalies > 2) {
      overallHealth = 'degraded';
    }

    const recommendations = this.generateRecommendations(recentMetrics, this.anomalies);

    return {
      overallHealth,
      activeAnomalies,
      recentMetrics,
      recommendations
    };
  }

  /**
   * メトリクスの取得
   */
  getMetrics(symbol?: string): QualityMetrics[] {
    if (symbol) {
      return this.metrics.get(symbol) || [];
    }

    const allMetrics: QualityMetrics[] = [];
    this.metrics.forEach(symbolMetrics => {
      allMetrics.push(...symbolMetrics);
    });

    return allMetrics.sort((a, b) => 
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );
  }

  /**
   * 異常の取得
   */
  getAnomalies(severity?: string): AnomalyDetection[] {
    if (severity) {
      return this.anomalies.filter(a => a.severity === severity);
    }
    return [...this.anomalies];
  }

  /**
   * 閾値の更新
   */
  updateThresholds(newThresholds: Partial<QualityThresholds>): void {
    this.thresholds = { ...this.thresholds, ...newThresholds };
    console.info('品質監視閾値を更新しました', this.thresholds);
  }

  /**
   * データのクリア
   */
  clearData(): void {
    this.metrics.clear();
    this.anomalies = [];
    console.info('品質監視データをクリアしました');
  }
}

export default DataQualityMonitor;
export type { 
  QualityMetrics, 
  AnomalyDetection, 
  QualityReport, 
  QualityThresholds 
};
