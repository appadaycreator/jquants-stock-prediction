"use client";

import { useState, useEffect } from "react";
import { TrendingUp, TrendingDown, Minus, AlertCircle, CheckCircle, RefreshCw, Zap, Target, Shield } from "lucide-react";

interface TradingSignal {
  symbol: string;
  signal_type: string;
  strength: string;
  price: number;
  confidence: number;
  timestamp: string;
  reason: string;
  risk_level: string;
  position_size: number;
  evidence?: {
    historical_accuracy_30d: number; // 0-1
    model: { name: string; description: string };
    top_features: { name: string; importance: number }[];
    news_headlines?: { title: string; url: string; published_at: string }[];
    technical_top3?: { name: string; value: number; signal: string }[];
  };
}

interface RealtimeSignalDisplayProps {
  symbols?: string[];
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export default function RealtimeSignalDisplay({ 
  symbols = [], 
  autoRefresh = true, 
  refreshInterval = 30000, 
}: RealtimeSignalDisplayProps) {
  const [signals, setSignals] = useState<TradingSignal[]>([]);
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [signalSummary, setSignalSummary] = useState({
    buy: 0,
    sell: 0,
    hold: 0,
    strong_buy: 0,
    strong_sell: 0,
  });

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(fetchSignals, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval]);

  useEffect(() => {
    fetchSignals();
  }, []);

  const fetchSignals = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // クライアントサイドでのシグナルシミュレーション
      // 実際のシグナル取得は静的サイトでは実行できないため、シミュレーション
      const mockSignals: TradingSignal[] = [
        {
          symbol: "7203.T",
          signal_type: "BUY",
          strength: "STRONG",
          confidence: 0.85,
          price: 2500,
          timestamp: new Date().toISOString(),
          reason: "テクニカル分析とファンダメンタル分析の両方で買いシグナル",
          risk_level: "MEDIUM",
          position_size: 1000,
          evidence: {
            historical_accuracy_30d: 0.78,
            model: {
              name: "統合予測モデル",
              description: "テクニカル分析とファンダメンタル分析を統合したAIモデル",
            },
            top_features: [
              { name: "RSI", importance: 0.85 },
              { name: "MACD", importance: 0.72 },
              { name: "業績成長率", importance: 0.68 },
            ],
            news_headlines: [
              { title: "株式市場全体が上昇", url: "https://example.com/news1", published_at: "2023-10-27T10:00:00Z" },
              { title: "7203.Tのテクニカル指標が改善", url: "https://example.com/news2", published_at: "2023-10-27T11:00:00Z" },
            ],
            technical_top3: [
              { name: "RSI", value: 70, signal: "買い" },
              { name: "MACD", value: 1.2, signal: "買い" },
              { name: "移動平均線", value: 2480, signal: "買い" },
            ],
          },
        },
        {
          symbol: "6758.T", 
          signal_type: "SELL",
          strength: "WEAK",
          confidence: 0.72,
          price: 12000,
          timestamp: new Date().toISOString(),
          reason: "テクニカル分析で売りシグナル、利益確定のタイミング",
          risk_level: "LOW",
          position_size: 500,
          evidence: {
            historical_accuracy_30d: 0.65,
            model: {
              name: "リスク評価モデル",
              description: "リスク要因を重点的に分析するAIモデル",
            },
            top_features: [
              { name: "RSI", importance: 0.72 },
              { name: "MACD", importance: 0.68 },
              { name: "PER", importance: 0.55 },
            ],
            news_headlines: [
              { title: "6758.Tの業績が悪化", url: "https://example.com/news3", published_at: "2023-10-27T12:00:00Z" },
            ],
            technical_top3: [
              { name: "RSI", value: 65, signal: "売り" },
              { name: "MACD", value: -0.5, signal: "売り" },
              { name: "移動平均線", value: 11800, signal: "売り" },
            ],
          },
        },
      ];
      
      const mockSummary = {
        buy: mockSignals.filter(s => s.signal_type === "BUY" && s.strength === "WEAK").length,
        sell: mockSignals.filter(s => s.signal_type === "SELL" && s.strength === "WEAK").length,
        hold: 0,
        strong_buy: mockSignals.filter(s => s.signal_type === "BUY" && s.strength === "STRONG").length,
        strong_sell: mockSignals.filter(s => s.signal_type === "SELL" && s.strength === "STRONG").length,
      };
      
      setSignals(mockSignals);
      setSignalSummary(mockSummary);
      setLastUpdate(new Date());
      
    } catch (err) {
      console.error("シグナル取得エラー:", err);
      setError("シグナルデータの取得に失敗しました");
    } finally {
      setLoading(false);
    }
  };

  const getSignalIcon = (signalType: string) => {
    switch (signalType) {
      case "STRONG_BUY":
        return <TrendingUp className="h-5 w-5 text-green-600" />;
      case "BUY":
        return <TrendingUp className="h-4 w-4 text-green-500" />;
      case "STRONG_SELL":
        return <TrendingDown className="h-5 w-5 text-red-600" />;
      case "SELL":
        return <TrendingDown className="h-4 w-4 text-red-500" />;
      default:
        return <Minus className="h-4 w-4 text-gray-500" />;
    }
  };

  const getSignalColor = (signalType: string) => {
    switch (signalType) {
      case "STRONG_BUY":
        return "text-green-700 bg-green-100 border-green-200";
      case "BUY":
        return "text-green-600 bg-green-50 border-green-100";
      case "STRONG_SELL":
        return "text-red-700 bg-red-100 border-red-200";
      case "SELL":
        return "text-red-600 bg-red-50 border-red-100";
      default:
        return "text-gray-600 bg-gray-50 border-gray-100";
    }
  };

  const getStrengthColor = (strength: string) => {
    switch (strength) {
      case "VERY_STRONG":
        return "text-green-600";
      case "STRONG":
        return "text-blue-600";
      case "MEDIUM":
        return "text-yellow-600";
      case "WEAK":
        return "text-gray-600";
      default:
        return "text-gray-500";
    }
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case "LOW":
        return "text-green-600 bg-green-50";
      case "MEDIUM":
        return "text-yellow-600 bg-yellow-50";
      case "HIGH":
        return "text-red-600 bg-red-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return "text-green-600";
    if (confidence >= 0.6) return "text-yellow-600";
    return "text-red-600";
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("ja-JP", {
      style: "currency",
      currency: "JPY",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <AlertCircle className="h-5 w-5 text-red-600 mr-2" />
          <span className="text-red-600">{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Zap className="h-6 w-6 text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-900">リアルタイム売買シグナル</h2>
        </div>
        <div className="flex items-center space-x-2">
          {lastUpdate && (
            <span className="text-sm text-gray-500">
              最終更新: {lastUpdate.toLocaleTimeString()}
            </span>
          )}
          <button
            onClick={fetchSignals}
            disabled={loading}
            className="flex items-center space-x-1 px-3 py-1 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            <span>更新</span>
          </button>
        </div>
      </div>

      {/* シグナルサマリー */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-green-600">強気買い</p>
              <p className="text-2xl font-bold text-green-700">{signalSummary.strong_buy}</p>
            </div>
            <TrendingUp className="h-6 w-6 text-green-600" />
          </div>
        </div>
        
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-green-600">買い</p>
              <p className="text-2xl font-bold text-green-700">{signalSummary.buy}</p>
            </div>
            <TrendingUp className="h-5 w-5 text-green-600" />
          </div>
        </div>
        
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">ホールド</p>
              <p className="text-2xl font-bold text-gray-700">{signalSummary.hold}</p>
            </div>
            <Minus className="h-5 w-5 text-gray-600" />
          </div>
        </div>
        
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-red-600">売り</p>
              <p className="text-2xl font-bold text-red-700">{signalSummary.sell}</p>
            </div>
            <TrendingDown className="h-5 w-5 text-red-600" />
          </div>
        </div>
        
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-red-600">強気売り</p>
              <p className="text-2xl font-bold text-red-700">{signalSummary.strong_sell}</p>
            </div>
            <TrendingDown className="h-6 w-6 text-red-600" />
          </div>
        </div>
      </div>

      {/* シグナル一覧 */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">上位シグナル</h3>
        </div>
        
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <RefreshCw className="h-6 w-6 animate-spin text-blue-600 mr-2" />
            <span className="text-gray-600">シグナルを取得中...</span>
          </div>
        ) : signals.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            シグナルがありません
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {signals.map((signal, index) => (
              <div key={`${signal.symbol}-${index}`} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      {getSignalIcon(signal.signal_type)}
                      <span className="text-lg font-semibold text-gray-900">{signal.symbol}</span>
                    </div>
                    
                    <div className={`px-3 py-1 rounded-full text-sm font-medium border ${getSignalColor(signal.signal_type)}`}>
                      {signal.signal_type}
                    </div>
                    
                    <div className={`px-2 py-1 rounded text-xs ${getStrengthColor(signal.strength)}`}>
                      {signal.strength}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-6">
                    <div className="text-right">
                      <p className="text-sm text-gray-600">現在価格</p>
                      <p className="text-lg font-semibold">{formatCurrency(signal.price)}</p>
                    </div>
                    
                    <div className="text-right">
                      <p className="text-sm text-gray-600">信頼度</p>
                      <p className={`text-lg font-semibold ${getConfidenceColor(signal.confidence)}`}>
                        {(signal.confidence * 100).toFixed(0)}%
                      </p>
                    </div>
                    
                    <div className="text-right">
                      <p className="text-sm text-gray-600">推奨ポジション</p>
                      <p className="text-lg font-semibold">{formatCurrency(signal.position_size)}</p>
                    </div>
                    
                    <div className={`px-2 py-1 rounded text-xs ${getRiskColor(signal.risk_level)}`}>
                      <Shield className="h-3 w-3 inline mr-1" />
                      {signal.risk_level}
                    </div>
                    <button
                      onClick={() => setExpandedIndex(expandedIndex === index ? null : index)}
                      className="ml-2 text-sm text-blue-600 hover:underline"
                    >
                      {expandedIndex === index ? "根拠を閉じる" : "根拠を表示"}
                    </button>
                  </div>
                </div>
                
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <p className="text-sm text-gray-600">
                    <Target className="h-4 w-4 inline mr-1" />
                    {signal.reason}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    更新時刻: {new Date(signal.timestamp).toLocaleString()}
                  </p>
                  {signal.reason?.includes("推薦抑制") && (
                    <div className="mt-2 text-xs text-red-600">
                      <AlertCircle className="h-3 w-3 inline mr-1" />
                      安全スイッチ作動: 根拠不足または信頼度不足でHOLDに抑制
                    </div>
                  )}
                </div>

                {expandedIndex === index && signal.evidence && (
                  <div className="mt-4 p-4 bg-gray-50 rounded border border-gray-200">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <p className="text-xs text-gray-600">過去30日的中率</p>
                        <p className="text-xl font-semibold text-gray-900">{(signal.evidence.historical_accuracy_30d * 100).toFixed(0)}%</p>
                      </div>
                      <div className="md:col-span-2">
                        <p className="text-xs text-gray-600">モデル</p>
                        <p className="text-sm font-medium text-gray-900">{signal.evidence.model.name}</p>
                        <p className="text-xs text-gray-600">{signal.evidence.model.description}</p>
                      </div>
                    </div>
                    <div className="mt-3">
                      <p className="text-xs text-gray-600 mb-1">主要特徴量（重要度上位）</p>
                      <div className="space-y-1">
                        {signal.evidence.top_features.map((f, i) => (
                          <div key={i} className="flex items-center justify-between text-xs text-gray-700">
                            <span>{f.name}</span>
                            <div className="flex items-center w-40">
                              <div className="w-full bg-gray-200 rounded h-1 mr-2">
                                <div className="bg-blue-500 h-1 rounded" style={{ width: `${Math.min(100, Math.round(f.importance * 100))}%` }} />
                              </div>
                              <span className="w-10 text-right">{Math.round(f.importance * 100)}%</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-xs text-gray-600 mb-1">直近ニュース/センチメント</p>
                        <div className="space-y-2">
                          {(signal.evidence.news_headlines || []).map((n, i) => (
                            <div key={i} className="text-xs">
                              <a className="text-blue-600 hover:underline" href={n.url} target="_blank" rel="noreferrer">
                                {n.title}
                              </a>
                              <div className="text-gray-500">{new Date(n.published_at).toLocaleString()}</div>
                            </div>
                          ))}
                          {(signal.evidence.news_headlines || []).length === 0 && (
                            <div className="text-xs text-gray-500">該当ニュースがありません</div>
                          )}
                        </div>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600 mb-1">テクニカル上位3指標</p>
                        <div className="space-y-1">
                          {(signal.evidence.technical_top3 || []).map((t, i) => (
                            <div key={i} className="flex items-center justify-between text-xs text-gray-700">
                              <span>{t.name}</span>
                              <span className="text-gray-500">{t.signal}</span>
                            </div>
                          ))}
                          {(signal.evidence.technical_top3 || []).length === 0 && (
                            <div className="text-xs text-gray-500">テクニカル根拠が不足しています</div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
