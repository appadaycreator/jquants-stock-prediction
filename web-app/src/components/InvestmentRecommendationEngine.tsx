"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  RefreshCw,
  Activity,
  AlertTriangle,
  CheckCircle,
  Star,
  Target,
  Shield,
  Zap
} from "lucide-react";

interface Position {
  symbol: string;
  company_name: string;
  quantity: number;
  cost_basis: number;
  current_price: number;
  total_value: number;
  unrealized_pnl: number;
  pnl_percentage: number;
  risk_level: string;
  confidence: number;
}

interface MarketData {
  symbol: string;
  price: number;
  volume: number;
  volatility: number;
  rsi: number;
  macd: number;
  sma_20: number;
  sma_50: number;
  trend: 'up' | 'down' | 'sideways';
  momentum: number;
}

interface Recommendation {
  symbol: string;
  action: 'BUY' | 'SELL' | 'HOLD' | 'STRONG_BUY' | 'STRONG_SELL';
  confidence: number;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  reason: string;
  target_price?: number;
  stop_loss?: number;
  position_size?: number;
  expected_return?: number;
  risk_level: string;
  timeframe: string;
  technical_signals: string[];
  fundamental_signals: string[];
  risk_factors: string[];
}

interface InvestmentRecommendationEngineProps {
  positions: Position[];
  marketData: MarketData[];
  onRecommendationUpdate?: (recommendations: Recommendation[]) => void;
  refreshInterval?: number;
}

export default function InvestmentRecommendationEngine({ 
  positions, 
  marketData,
  onRecommendationUpdate,
  refreshInterval = 60000 // 1分
}: InvestmentRecommendationEngineProps) {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [generationStatus, setGenerationStatus] = useState<'idle' | 'generating' | 'completed' | 'error'>('idle');

  // 技術分析による推奨生成
  const generateTechnicalRecommendations = useCallback((position: Position, market: MarketData): Recommendation => {
    const signals: string[] = [];
    const riskFactors: string[] = [];
    let action: Recommendation['action'] = 'HOLD';
    let confidence = 0.5;
    let priority: Recommendation['priority'] = 'MEDIUM';
    let reason = '';

    // RSI分析
    if (market.rsi < 30) {
      signals.push('RSI過売り');
      if (position.pnl_percentage < -5) {
        action = 'BUY';
        confidence += 0.2;
        reason += 'RSI過売り + 損切り後の反発期待';
      }
    } else if (market.rsi > 70) {
      signals.push('RSI過買い');
      if (position.pnl_percentage > 10) {
        action = 'SELL';
        confidence += 0.2;
        reason += 'RSI過買い + 利確のタイミング';
      }
    }

    // MACD分析
    if (market.macd > 0 && market.momentum > 0) {
      signals.push('MACD上昇');
      if (action === 'HOLD') {
        action = 'BUY';
        confidence += 0.15;
        reason += 'MACD上昇トレンド';
      }
    } else if (market.macd < 0 && market.momentum < 0) {
      signals.push('MACD下降');
      if (action === 'HOLD') {
        action = 'SELL';
        confidence += 0.15;
        reason += 'MACD下降トレンド';
      }
    }

    // 移動平均線分析
    if (market.current_price > market.sma_20 && market.sma_20 > market.sma_50) {
      signals.push('上昇トレンド');
      if (action === 'BUY') {
        action = 'STRONG_BUY';
        confidence += 0.1;
        reason += ' + 上昇トレンド継続';
      }
    } else if (market.current_price < market.sma_20 && market.sma_20 < market.sma_50) {
      signals.push('下降トレンド');
      if (action === 'SELL') {
        action = 'STRONG_SELL';
        confidence += 0.1;
        reason += ' + 下降トレンド継続';
      }
    }

    // ボラティリティ分析
    if (market.volatility > 0.05) {
      riskFactors.push('高ボラティリティ');
      if (position.risk_level === 'HIGH') {
        priority = 'HIGH';
      }
    }

    // 損益状況による調整
    if (position.pnl_percentage < -15) {
      riskFactors.push('大幅損失');
      priority = 'CRITICAL';
      if (action === 'HOLD') {
        action = 'SELL';
        reason = '損切り推奨';
        confidence = 0.8;
      }
    } else if (position.pnl_percentage > 20) {
      signals.push('大幅利益');
      if (action === 'HOLD') {
        action = 'SELL';
        reason = '利確推奨';
        confidence = 0.7;
      }
    }

    // 信頼度の調整
    confidence = Math.min(confidence, 0.95);
    confidence = Math.max(confidence, 0.3);

    // 目標価格と損切り価格の設定
    let targetPrice: number | undefined;
    let stopLoss: number | undefined;

    if (action === 'BUY' || action === 'STRONG_BUY') {
      targetPrice = market.current_price * 1.15; // 15%上昇目標
      stopLoss = market.current_price * 0.92; // 8%損切り
    } else if (action === 'SELL' || action === 'STRONG_SELL') {
      targetPrice = market.current_price * 0.85; // 15%下落目標
      stopLoss = market.current_price * 1.08; // 8%上昇で損切り
    }

    return {
      symbol: position.symbol,
      action,
      confidence,
      priority,
      reason: reason || '技術分析による推奨',
      target_price: targetPrice,
      stop_loss: stopLoss,
      position_size: action.includes('BUY') ? Math.floor(position.quantity * 0.1) : undefined,
      expected_return: action.includes('BUY') ? 0.15 : action.includes('SELL') ? -0.15 : 0,
      risk_level: position.risk_level,
      timeframe: '1-2週間',
      technical_signals: signals,
      fundamental_signals: [],
      risk_factors: riskFactors
    };
  }, []);

  // 推奨生成の実行
  const generateRecommendations = useCallback(async () => {
    try {
      setIsGenerating(true);
      setGenerationStatus('generating');

      const newRecommendations: Recommendation[] = [];

      // 各ポジションに対して推奨を生成
      for (const position of positions) {
        const market = marketData.find(m => m.symbol === position.symbol);
        if (market) {
          const recommendation = generateTechnicalRecommendations(position, market);
          newRecommendations.push(recommendation);
        }
      }

      // 推奨を優先度でソート
      newRecommendations.sort((a, b) => {
        const priorityOrder = { 'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1 };
        return priorityOrder[b.priority] - priorityOrder[a.priority];
      });

      setRecommendations(newRecommendations);
      setLastUpdate(new Date());
      setGenerationStatus('completed');

      if (onRecommendationUpdate) {
        onRecommendationUpdate(newRecommendations);
      }
    } catch (error) {
      console.error('推奨生成エラー:', error);
      setGenerationStatus('error');
    } finally {
      setIsGenerating(false);
    }
  }, [positions, marketData, generateTechnicalRecommendations, onRecommendationUpdate]);

  // 自動生成の設定
  useEffect(() => {
    const interval = setInterval(generateRecommendations, refreshInterval);
    return () => clearInterval(interval);
  }, [generateRecommendations, refreshInterval]);

  // 手動生成
  const handleManualGeneration = () => {
    generateRecommendations();
  };

  // アクションアイコンの取得
  const getActionIcon = (action: string) => {
    switch (action) {
      case 'STRONG_BUY':
        return <TrendingUp className="h-4 w-4 text-green-600" />;
      case 'BUY':
        return <TrendingUp className="h-4 w-4 text-green-500" />;
      case 'HOLD':
        return <Activity className="h-4 w-4 text-gray-500" />;
      case 'SELL':
        return <TrendingDown className="h-4 w-4 text-red-500" />;
      case 'STRONG_SELL':
        return <TrendingDown className="h-4 w-4 text-red-600" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  // アクションカラーの取得
  const getActionColor = (action: string) => {
    switch (action) {
      case 'STRONG_BUY':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'BUY':
        return 'bg-green-50 text-green-700 border-green-100';
      case 'HOLD':
        return 'bg-gray-100 text-gray-700 border-gray-200';
      case 'SELL':
        return 'bg-red-50 text-red-700 border-red-100';
      case 'STRONG_SELL':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  // 優先度カラーの取得
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'CRITICAL':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'HIGH':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'LOW':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  return (
    <div className="space-y-4">
      {/* 推奨生成ステータス */}
      <Card className="bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-semibold text-purple-900">
              投資推奨エンジン
            </CardTitle>
            <div className="flex items-center space-x-2">
              <Badge 
                variant={generationStatus === 'completed' ? 'default' : 'secondary'}
                className="flex items-center space-x-1"
              >
                {generationStatus === 'completed' ? (
                  <CheckCircle className="h-4 w-4 text-green-600" />
                ) : generationStatus === 'generating' ? (
                  <RefreshCw className="h-4 w-4 text-blue-600 animate-spin" />
                ) : generationStatus === 'error' ? (
                  <AlertTriangle className="h-4 w-4 text-red-600" />
                ) : (
                  <Activity className="h-4 w-4 text-gray-600" />
                )}
                <span className="text-xs">
                  {generationStatus === 'completed' ? '推奨生成完了' :
                   generationStatus === 'generating' ? '生成中...' :
                   generationStatus === 'error' ? 'エラー' : '待機中'}
                </span>
              </Badge>
              <Button
                variant="outline"
                size="sm"
                onClick={handleManualGeneration}
                disabled={isGenerating}
                title="手動で推奨を生成"
              >
                <Zap className="h-4 w-4 mr-1" />
                生成
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-900">
                {recommendations.length}
              </div>
              <div className="text-sm text-purple-700">生成済み推奨</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-900">
                {recommendations.filter(r => r.priority === 'CRITICAL' || r.priority === 'HIGH').length}
              </div>
              <div className="text-sm text-purple-700">高優先度</div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-600">最終更新</div>
              <div className="text-sm font-medium text-gray-800">
                {lastUpdate.toLocaleTimeString()}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 推奨一覧 */}
      <div className="grid gap-3">
        {recommendations.map((recommendation, index) => (
          <Card key={index} className={`hover:shadow-md transition-shadow ${
            recommendation.priority === 'CRITICAL' ? 'border-red-300 bg-red-50' :
            recommendation.priority === 'HIGH' ? 'border-orange-300 bg-orange-50' :
            'border-gray-200'
          }`}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div>
                    <h3 className="font-semibold text-lg">{recommendation.symbol}</h3>
                    <p className="text-sm text-gray-600">{recommendation.reason}</p>
                  </div>
                  <Badge className={getActionColor(recommendation.action)}>
                    {getActionIcon(recommendation.action)}
                    <span className="ml-1">{recommendation.action}</span>
                  </Badge>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge className={getPriorityColor(recommendation.priority)}>
                    {recommendation.priority}
                  </Badge>
                  <div className="text-right">
                    <div className="text-sm font-medium">
                      信頼度: {(recommendation.confidence * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                <div>
                  <p className="text-gray-600">リスクレベル</p>
                  <p className={`font-medium ${recommendation.risk_level === 'HIGH' ? 'text-red-600' : 
                    recommendation.risk_level === 'MEDIUM' ? 'text-yellow-600' : 'text-green-600'}`}>
                    {recommendation.risk_level}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">期間</p>
                  <p className="font-medium">{recommendation.timeframe}</p>
                </div>
                <div>
                  <p className="text-gray-600">期待リターン</p>
                  <p className="font-medium">
                    {recommendation.expected_return ? `${(recommendation.expected_return * 100).toFixed(1)}%` : "N/A"}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">ポジションサイズ</p>
                  <p className="font-medium">
                    {recommendation.position_size ? `${recommendation.position_size}株` : "N/A"}
                  </p>
                </div>
              </div>

              {/* 技術シグナル */}
              {recommendation.technical_signals.length > 0 && (
                <div className="mb-4 p-3 bg-blue-50 rounded-lg">
                  <div className="flex items-center space-x-2 mb-2">
                    <Target className="h-4 w-4 text-blue-600" />
                    <span className="text-sm font-medium text-blue-800">技術シグナル</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {recommendation.technical_signals.map((signal, idx) => (
                      <Badge key={idx} variant="secondary" className="text-xs">
                        {signal}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* リスク要因 */}
              {recommendation.risk_factors.length > 0 && (
                <div className="mb-4 p-3 bg-red-50 rounded-lg">
                  <div className="flex items-center space-x-2 mb-2">
                    <Shield className="h-4 w-4 text-red-600" />
                    <span className="text-sm font-medium text-red-800">リスク要因</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {recommendation.risk_factors.map((factor, idx) => (
                      <Badge key={idx} variant="destructive" className="text-xs">
                        {factor}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* 価格目標 */}
              {(recommendation.target_price || recommendation.stop_loss) && (
                <div className="grid grid-cols-2 gap-4 text-sm">
                  {recommendation.target_price && (
                    <div className="bg-green-50 p-3 rounded">
                      <p className="text-gray-600">目標価格</p>
                      <p className="font-medium text-green-700">¥{recommendation.target_price.toLocaleString()}</p>
                    </div>
                  )}
                  {recommendation.stop_loss && (
                    <div className="bg-red-50 p-3 rounded">
                      <p className="text-gray-600">損切り価格</p>
                      <p className="font-medium text-red-700">¥{recommendation.stop_loss.toLocaleString()}</p>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 推奨がない場合のメッセージ */}
      {recommendations.length === 0 && (
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>推奨がありません</AlertTitle>
          <AlertDescription>
            推奨を生成するには、ポジションと市場データが必要です。
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}
