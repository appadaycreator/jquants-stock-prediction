import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";
import { TrendingUp, TrendingDown, AlertTriangle, Target, Shield } from "lucide-react";
import EnhancedTooltip from "./EnhancedTooltip";

interface LSTMPrediction {
  predictions: number[];
  prediction_dates: string[];
  confidence: {
    confidence: number;
    risk_level: string;
    prediction_volatility: number;
    historical_volatility: number;
  };
  training_result: {
    train_loss: number;
    val_loss: number;
    train_mae: number;
    val_mae: number;
  };
  visualization_data: {
    historical: {
      dates: string[];
      prices: number[];
    };
    predictions: {
      dates: string[];
      prices: number[];
    };
  };
}

interface PersonalInvestmentLSTMProps {
  symbol: string;
  symbolName: string;
  currentPrice: number;
  onPredictionComplete?: (prediction: LSTMPrediction) => void;
}

export function PersonalInvestmentLSTM({ 
  symbol, 
  symbolName, 
  currentPrice, 
  onPredictionComplete, 
}: PersonalInvestmentLSTMProps) {
  const [prediction, setPrediction] = useState<LSTMPrediction | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [predictionDays, setPredictionDays] = useState(22);

  const runLSTMPrediction = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch("/api/lstm-predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          symbol,
          prediction_days: predictionDays,
        }),
      });

      if (!response.ok) {
        throw new Error("LSTM予測の実行に失敗しました");
      }

      const result = await response.json();
      setPrediction(result);
      
      if (onPredictionComplete) {
        onPredictionComplete(result);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "予測実行中にエラーが発生しました");
    } finally {
      setIsLoading(false);
    }
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case "低": return "bg-green-100 text-green-800";
      case "中": return "bg-yellow-100 text-yellow-800";
      case "高": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return "text-green-600";
    if (confidence >= 0.6) return "text-yellow-600";
    return "text-red-600";
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat("ja-JP", {
      style: "currency",
      currency: "JPY",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  // チャート用データの準備
  const chartData = prediction ? [
    ...prediction.visualization_data.historical.dates.map((date, index) => ({
      date,
      price: prediction.visualization_data.historical.prices[index],
      type: "historical",
    })),
    ...prediction.visualization_data.predictions.dates.map((date, index) => ({
      date,
      price: prediction.visualization_data.predictions.prices[index],
      type: "prediction",
    })),
  ] : [];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            LSTM株価予測（個人投資用）
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div>
                <h3 className="font-semibold">{symbolName} ({symbol})</h3>
                <p className="text-sm text-gray-600">現在価格: {formatPrice(currentPrice)}</p>
              </div>
              <div className="flex gap-2">
                <select
                  value={predictionDays}
                  onChange={(e) => setPredictionDays(Number(e.target.value))}
                  className="px-3 py-1 border rounded-md text-sm"
                >
                  <option value={7}>7日先</option>
                  <option value={14}>14日先</option>
                  <option value={22}>22日先（1ヶ月）</option>
                  <option value={30}>30日先</option>
                </select>
                <Button 
                  onClick={runLSTMPrediction} 
                  disabled={isLoading}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {isLoading ? "予測実行中..." : "LSTM予測実行"}
                </Button>
              </div>
            </div>

            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            )}

            {isLoading && (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                  <span className="text-sm text-gray-600">LSTMモデルを訓練中...</span>
                </div>
                <Progress value={75} className="w-full" />
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {prediction && (
        <Tabs defaultValue="prediction" className="space-y-4">
          <TabsList>
            <TabsTrigger value="prediction">予測結果</TabsTrigger>
            <TabsTrigger value="confidence">信頼度分析</TabsTrigger>
            <TabsTrigger value="chart">チャート</TabsTrigger>
            <TabsTrigger value="training">訓練結果</TabsTrigger>
          </TabsList>

          <TabsContent value="prediction" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  予測結果
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <p className="text-sm text-gray-600">最終予測価格</p>
                    <EnhancedTooltip
                      content="LSTMモデルによる予測期間の最終日の予測価格です。AIが過去の価格パターンを学習して予測した価格で、投資判断の参考となります。例：現在価格3,000円から3,200円に予測される場合、+200円の上昇が予測されます。"
                      type="info"
                    >
                      <p className="text-2xl font-bold text-blue-600 cursor-help">
                        {formatPrice(prediction.predictions[prediction.predictions.length - 1])}
                      </p>
                    </EnhancedTooltip>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <p className="text-sm text-gray-600">予想上昇率</p>
                    <EnhancedTooltip
                      content="現在価格から予測価格への上昇率です。プラスは上昇予測、マイナスは下落予測を示します。AI予測による投資リターンの期待値を示し、投資判断の重要な指標となります。例：現在価格3,000円から3,200円に予測される場合、+6.67%の上昇率となります。"
                      type="success"
                    >
                      <p className="text-2xl font-bold text-green-600 cursor-help">
                        {formatPercent((prediction.predictions[prediction.predictions.length - 1] / currentPrice) - 1)}
                      </p>
                    </EnhancedTooltip>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <p className="text-sm text-gray-600">信頼度</p>
                    <EnhancedTooltip
                      content="LSTMモデルの予測信頼度です。複数の技術指標と過去の価格パターンを総合的に評価した結果の確信度を示します。80%以上が高信頼度、60-80%が中信頼度、60%未満が低信頼度とされます。例：信頼度85%の場合、予測結果が高い確率で正しいことを示します。"
                      type="info"
                    >
                      <p className={`text-2xl font-bold cursor-help ${getConfidenceColor(prediction.confidence.confidence)}`}>
                        {formatPercent(prediction.confidence.confidence)}
                      </p>
                    </EnhancedTooltip>
                  </div>
                </div>

                <div className="mt-6">
                  <h4 className="font-semibold mb-3">予測価格推移</h4>
                  <div className="space-y-2">
                    {prediction.predictions.slice(0, 10).map((price, index) => (
                      <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                        <span className="text-sm">{prediction.prediction_dates[index]}</span>
                        <span className="font-medium">{formatPrice(price)}</span>
                        <span className={`text-sm ${price > currentPrice ? "text-green-600" : "text-red-600"}`}>
                          {price > currentPrice ? "+" : ""}{formatPercent((price / currentPrice) - 1)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="confidence" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  信頼度分析
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">信頼度スコア</span>
                      <Badge className={getRiskColor(prediction.confidence.risk_level)}>
                        {formatPercent(prediction.confidence.confidence)}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">リスクレベル</span>
                      <Badge className={getRiskColor(prediction.confidence.risk_level)}>
                        {prediction.confidence.risk_level}
                      </Badge>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>予測変動性</span>
                        <span>{formatPercent(prediction.confidence.prediction_volatility)}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>過去変動性</span>
                        <span>{formatPercent(prediction.confidence.historical_volatility)}</span>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <h4 className="font-semibold">投資判断</h4>
                    {prediction.confidence.confidence > 0.7 ? (
                      <div className="p-3 bg-green-50 border border-green-200 rounded-md">
                        <p className="text-green-800 text-sm">
                          <strong>推奨:</strong> 信頼度が高く、投資検討に適しています
                        </p>
                      </div>
                    ) : prediction.confidence.confidence > 0.5 ? (
                      <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                        <p className="text-yellow-800 text-sm">
                          <strong>注意:</strong> 信頼度が中程度です。他の指標も併せて検討してください
                        </p>
                      </div>
                    ) : (
                      <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                        <p className="text-red-800 text-sm">
                          <strong>警告:</strong> 信頼度が低く、投資リスクが高い可能性があります
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="chart" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>価格推移チャート</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-96">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="date" 
                        tick={{ fontSize: 12 }}
                        tickFormatter={(value) => new Date(value).toLocaleDateString("ja-JP", { month: "short", day: "numeric" })}
                      />
                      <YAxis 
                        tick={{ fontSize: 12 }}
                        tickFormatter={(value) => formatPrice(value)}
                      />
                      <Tooltip 
                        formatter={(value: number) => [formatPrice(value), "価格"]}
                        labelFormatter={(label) => new Date(label).toLocaleDateString("ja-JP")}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="price" 
                        stroke="#3b82f6" 
                        strokeWidth={2}
                        dot={false}
                        name="価格"
                      />
                      <ReferenceLine 
                        x={prediction.visualization_data.historical.dates[prediction.visualization_data.historical.dates.length - 1]} 
                        stroke="#ef4444" 
                        strokeDasharray="5 5"
                        label="予測開始点"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="training" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>モデル訓練結果</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h4 className="font-semibold">損失値</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm">訓練損失</span>
                        <span className="font-medium">{prediction.training_result.train_loss.toFixed(4)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">検証損失</span>
                        <span className="font-medium">{prediction.training_result.val_loss.toFixed(4)}</span>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <h4 className="font-semibold">平均絶対誤差</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm">訓練MAE</span>
                        <span className="font-medium">{prediction.training_result.train_mae.toFixed(4)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">検証MAE</span>
                        <span className="font-medium">{prediction.training_result.val_mae.toFixed(4)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
}
