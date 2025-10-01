/**
 * 推奨アクションの詳細理由表示コンポーネント
 */

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Info, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  Target,
  Shield,
  BarChart3,
  Brain,
  DollarSign,
  Clock,
  Star
} from 'lucide-react';
import { useRiskCustomization } from '@/hooks/useRiskCustomization';
import { RiskCalculationAdapter } from '@/lib/risk-calculation-adapter';

interface RecommendationDetailsProps {
  symbol: string;
  action: 'STRONG_BUY' | 'BUY' | 'HOLD' | 'SELL' | 'STRONG_SELL';
  confidence: number;
  currentPrice: number;
  targetPrice?: number;
  stopLossPrice?: number;
  expectedReturn?: number;
  riskScore?: number;
  technicalIndicators?: {
    rsi?: number;
    macd?: number;
    bollinger?: { upper: number; lower: number; middle: number };
    movingAverage?: { sma20: number; sma50: number; sma200: number };
  };
  sentimentAnalysis?: {
    score: number;
    magnitude: number;
    newsCount: number;
  };
  onClose?: () => void;
}

export function RecommendationDetails({
  symbol,
  action,
  confidence,
  currentPrice,
  targetPrice,
  stopLossPrice,
  expectedReturn = 0,
  riskScore = 0,
  technicalIndicators,
  sentimentAnalysis,
  onClose
}: RecommendationDetailsProps) {
  const { settings, getIndividualStockSettings } = useRiskCustomization();
  const [activeTab, setActiveTab] = useState<'overview' | 'technical' | 'sentiment' | 'risk'>('overview');

  const stockSettings = getIndividualStockSettings(symbol);
  const adapter = new RiskCalculationAdapter(settings);

  // アクションの色とアイコンを取得
  const getActionDisplay = (action: string) => {
    const displays = {
      'STRONG_BUY': { 
        color: 'text-green-600', 
        bgColor: 'bg-green-50', 
        icon: TrendingUp, 
        label: '強力買い',
        description: '非常に強力な買いシグナル'
      },
      'BUY': { 
        color: 'text-green-500', 
        bgColor: 'bg-green-50', 
        icon: TrendingUp, 
        label: '買い',
        description: '買いシグナル'
      },
      'HOLD': { 
        color: 'text-gray-500', 
        bgColor: 'bg-gray-50', 
        icon: BarChart3, 
        label: 'ホールド',
        description: '現状維持推奨'
      },
      'SELL': { 
        color: 'text-red-500', 
        bgColor: 'bg-red-50', 
        icon: TrendingDown, 
        label: '売り',
        description: '売りシグナル'
      },
      'STRONG_SELL': { 
        color: 'text-red-600', 
        bgColor: 'bg-red-50', 
        icon: TrendingDown, 
        label: '強力売り',
        description: '非常に強力な売りシグナル'
      },
    };
    return displays[action as keyof typeof displays];
  };

  const actionDisplay = getActionDisplay(action);
  const ActionIcon = actionDisplay.icon;

  // 信頼度の表示
  const getConfidenceLevel = (confidence: number) => {
    if (confidence >= 0.8) return { level: '非常に高い', color: 'text-green-600' };
    if (confidence >= 0.6) return { level: '高い', color: 'text-blue-600' };
    if (confidence >= 0.4) return { level: '中程度', color: 'text-yellow-600' };
    return { level: '低い', color: 'text-red-600' };
  };

  const confidenceLevel = getConfidenceLevel(confidence);

  // 推奨理由を生成
  const generateRecommendationReasons = () => {
    const reasons: string[] = [];

    // 基本理由
    if (action === 'STRONG_BUY' || action === 'BUY') {
      reasons.push('テクニカル指標が買いシグナルを示している');
      if (expectedReturn > 0.1) {
        reasons.push(`期待リターンが高い（${(expectedReturn * 100).toFixed(1)}%）`);
      }
    } else if (action === 'SELL' || action === 'STRONG_SELL') {
      reasons.push('テクニカル指標が売りシグナルを示している');
      if (riskScore > 0.7) {
        reasons.push('リスクが高い状態');
      }
    } else {
      reasons.push('現状維持が最適と判断');
    }

    // テクニカル分析理由
    if (technicalIndicators) {
      if (technicalIndicators.rsi && technicalIndicators.rsi < 30) {
        reasons.push('RSIが売られすぎを示している');
      } else if (technicalIndicators.rsi && technicalIndicators.rsi > 70) {
        reasons.push('RSIが買われすぎを示している');
      }

      if (technicalIndicators.movingAverage) {
        const { sma20, sma50, sma200 } = technicalIndicators.movingAverage;
        if (currentPrice > sma20 && sma20 > sma50 && sma50 > sma200) {
          reasons.push('移動平均線が上昇トレンドを示している');
        } else if (currentPrice < sma20 && sma20 < sma50 && sma50 < sma200) {
          reasons.push('移動平均線が下降トレンドを示している');
        }
      }
    }

    // センチメント分析理由
    if (sentimentAnalysis) {
      if (sentimentAnalysis.score > 0.3) {
        reasons.push('市場センチメントがポジティブ');
      } else if (sentimentAnalysis.score < -0.3) {
        reasons.push('市場センチメントがネガティブ');
      }
    }

    // リスク分析理由
    if (riskScore > 0.8) {
      reasons.push('リスクレベルが非常に高い');
    } else if (riskScore < 0.3) {
      reasons.push('リスクレベルが低く安全');
    }

    return reasons;
  };

  const recommendationReasons = generateRecommendationReasons();

  return (
    <div className="space-y-4">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ActionIcon className={`h-5 w-5 ${actionDisplay.color}`} />
          <h2 className="text-xl font-semibold">{symbol} 推奨詳細</h2>
        </div>
        {onClose && (
          <Button variant="outline" size="sm" onClick={onClose}>
            閉じる
          </Button>
        )}
      </div>

      {/* アクションサマリー */}
      <Card className={actionDisplay.bgColor}>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <ActionIcon className={`h-6 w-6 ${actionDisplay.color}`} />
                <span className={`text-lg font-semibold ${actionDisplay.color}`}>
                  {actionDisplay.label}
                </span>
                <Badge variant="outline">{actionDisplay.description}</Badge>
              </div>
              <p className="text-sm text-gray-600">
                信頼度: <span className={confidenceLevel.color}>{confidenceLevel.level}</span> ({Math.round(confidence * 100)}%)
              </p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold">{currentPrice.toLocaleString()}円</p>
              {targetPrice && (
                <p className="text-sm text-gray-600">
                  目標: {targetPrice.toLocaleString()}円
                </p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* タブナビゲーション */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
        {[
          { id: 'overview', label: '概要', icon: Info },
          { id: 'technical', label: 'テクニカル', icon: BarChart3 },
          { id: 'sentiment', label: 'センチメント', icon: Brain },
          { id: 'risk', label: 'リスク', icon: Shield },
        ].map(({ id, label, icon: Icon }) => (
          <Button
            key={id}
            variant={activeTab === id ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setActiveTab(id as any)}
            className="flex items-center gap-1"
          >
            <Icon className="h-4 w-4" />
            {label}
          </Button>
        ))}
      </div>

      {/* タブコンテンツ */}
      {activeTab === 'overview' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Info className="h-5 w-5 text-blue-600" />
              推奨理由
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recommendationReasons.map((reason, index) => (
                <div key={index} className="flex items-start gap-2">
                  <Star className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                  <span className="text-sm">{reason}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {activeTab === 'technical' && technicalIndicators && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-purple-600" />
              テクニカル分析
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {technicalIndicators.rsi && (
              <div className="flex justify-between items-center">
                <span>RSI (14)</span>
                <Badge variant={technicalIndicators.rsi > 70 ? 'destructive' : technicalIndicators.rsi < 30 ? 'default' : 'secondary'}>
                  {technicalIndicators.rsi.toFixed(1)}
                </Badge>
              </div>
            )}
            
            {technicalIndicators.movingAverage && (
              <div className="space-y-2">
                <h4 className="font-medium">移動平均線</h4>
                <div className="grid grid-cols-3 gap-2 text-sm">
                  <div className="text-center">
                    <p className="text-gray-600">SMA20</p>
                    <p className="font-medium">{technicalIndicators.movingAverage.sma20.toFixed(0)}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-gray-600">SMA50</p>
                    <p className="font-medium">{technicalIndicators.movingAverage.sma50.toFixed(0)}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-gray-600">SMA200</p>
                    <p className="font-medium">{technicalIndicators.movingAverage.sma200.toFixed(0)}</p>
                  </div>
                </div>
              </div>
            )}

            {technicalIndicators.bollinger && (
              <div className="space-y-2">
                <h4 className="font-medium">ボリンジャーバンド</h4>
                <div className="grid grid-cols-3 gap-2 text-sm">
                  <div className="text-center">
                    <p className="text-gray-600">上限</p>
                    <p className="font-medium">{technicalIndicators.bollinger.upper.toFixed(0)}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-gray-600">中央</p>
                    <p className="font-medium">{technicalIndicators.bollinger.middle.toFixed(0)}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-gray-600">下限</p>
                    <p className="font-medium">{technicalIndicators.bollinger.lower.toFixed(0)}</p>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === 'sentiment' && sentimentAnalysis && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-pink-600" />
              センチメント分析
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span>センチメントスコア</span>
              <Badge variant={sentimentAnalysis.score > 0 ? 'default' : 'destructive'}>
                {sentimentAnalysis.score > 0 ? '+' : ''}{sentimentAnalysis.score.toFixed(2)}
              </Badge>
            </div>
            <div className="flex justify-between items-center">
              <span>マグニチュード</span>
              <Badge variant="outline">{sentimentAnalysis.magnitude.toFixed(2)}</Badge>
            </div>
            <div className="flex justify-between items-center">
              <span>ニュース件数</span>
              <Badge variant="outline">{sentimentAnalysis.newsCount}件</Badge>
            </div>
          </CardContent>
        </Card>
      )}

      {activeTab === 'risk' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-orange-600" />
              リスク分析
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span>リスクスコア</span>
              <Badge variant={riskScore > 0.7 ? 'destructive' : riskScore > 0.4 ? 'default' : 'secondary'}>
                {(riskScore * 100).toFixed(1)}%
              </Badge>
            </div>
            <div className="flex justify-between items-center">
              <span>期待リターン</span>
              <Badge variant={expectedReturn > 0 ? 'default' : 'destructive'}>
                {(expectedReturn * 100).toFixed(1)}%
              </Badge>
            </div>
            {stockSettings && (
              <div className="space-y-2">
                <h4 className="font-medium">個別設定</h4>
                {stockSettings.targetPrice && (
                  <div className="flex justify-between items-center">
                    <span>目標価格</span>
                    <Badge variant="outline">{stockSettings.targetPrice.toLocaleString()}円</Badge>
                  </div>
                )}
                {stockSettings.stopLossPrice && (
                  <div className="flex justify-between items-center">
                    <span>損切ライン</span>
                    <Badge variant="outline">{stockSettings.stopLossPrice.toLocaleString()}円</Badge>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* アクションボタン */}
      <div className="flex gap-2">
        <Button className="flex-1">
          <Target className="h-4 w-4 mr-1" />
          詳細分析
        </Button>
        <Button variant="outline" className="flex-1">
          <Clock className="h-4 w-4 mr-1" />
          監視設定
        </Button>
      </div>
    </div>
  );
}
