"use client";

import { useState, useEffect } from "react";
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  Target, 
  Star,
  ArrowUp,
  ArrowDown,
  Minus,
  Eye,
  EyeOff,
  RefreshCw,
  Clock,
  DollarSign,
  BarChart3
} from "lucide-react";

interface JudgmentCard {
  id: string;
  type: 'prediction_deviation' | 'decline_alert' | 'volume_surge' | 'recommendation';
  title: string;
  description: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  action: 'buy' | 'sell' | 'hold' | 'watch';
  confidence: number;
  value?: number;
  change?: number;
  symbol?: string;
  name?: string;
  timestamp: string;
}

interface JudgmentPanelProps {
  className?: string;
  onStockSelect?: (symbol: string) => void;
  onActionClick?: (action: string, symbol: string) => void;
}

export default function JudgmentPanel({ 
  className = "",
  onStockSelect,
  onActionClick
}: JudgmentPanelProps) {
  const [cards, setCards] = useState<JudgmentCard[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [showAll, setShowAll] = useState(false);

  // サンプルデータの生成
  useEffect(() => {
    const generateSampleCards = (): JudgmentCard[] => [
      {
        id: "1",
        type: "prediction_deviation",
        title: "予測乖離Top",
        description: "AI予測と実際の価格に大きな乖離が発生",
        priority: "critical",
        action: "buy",
        confidence: 85,
        value: 12.5,
        change: 3.2,
        symbol: "7203.T",
        name: "トヨタ自動車",
        timestamp: new Date().toISOString()
      },
      {
        id: "2",
        type: "decline_alert",
        title: "下落注意",
        description: "技術指標で下落シグナルが複数検出",
        priority: "high",
        action: "sell",
        confidence: 78,
        value: -5.8,
        change: -2.1,
        symbol: "6758.T",
        name: "ソニーグループ",
        timestamp: new Date(Date.now() - 300000).toISOString()
      },
      {
        id: "3",
        type: "volume_surge",
        title: "出来高急増",
        description: "通常の3倍以上の出来高を記録",
        priority: "medium",
        action: "watch",
        confidence: 92,
        value: 350,
        change: 15.2,
        symbol: "6861.T",
        name: "キーエンス",
        timestamp: new Date(Date.now() - 600000).toISOString()
      },
      {
        id: "4",
        type: "recommendation",
        title: "推奨アクション",
        description: "ポートフォリオバランスの調整を推奨",
        priority: "high",
        action: "buy",
        confidence: 88,
        value: 0,
        change: 0,
        symbol: "9984.T",
        name: "ソフトバンクグループ",
        timestamp: new Date(Date.now() - 900000).toISOString()
      },
      {
        id: "5",
        type: "prediction_deviation",
        title: "予測乖離",
        description: "予測精度が高く、信頼できるシグナル",
        priority: "medium",
        action: "hold",
        confidence: 75,
        value: 8.3,
        change: 1.8,
        symbol: "4063.T",
        name: "信越化学工業",
        timestamp: new Date(Date.now() - 1200000).toISOString()
      }
    ];

    // データ読み込みのシミュレーション
    setTimeout(() => {
      setCards(generateSampleCards());
      setIsLoading(false);
      setLastUpdate(new Date());
    }, 1000);
  }, []);

  // カードの優先度に基づく色の取得
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-50 border-red-200 text-red-800';
      case 'high': return 'bg-orange-50 border-orange-200 text-orange-800';
      case 'medium': return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'low': return 'bg-blue-50 border-blue-200 text-blue-800';
      default: return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  // アクションの色の取得
  const getActionColor = (action: string) => {
    switch (action) {
      case 'buy': return 'bg-green-100 text-green-800 border-green-200';
      case 'sell': return 'bg-red-100 text-red-800 border-red-200';
      case 'hold': return 'bg-gray-100 text-gray-800 border-gray-200';
      case 'watch': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  // アクションのアイコン取得
  const getActionIcon = (action: string) => {
    switch (action) {
      case 'buy': return <ArrowUp className="h-4 w-4" />;
      case 'sell': return <ArrowDown className="h-4 w-4" />;
      case 'hold': return <Minus className="h-4 w-4" />;
      case 'watch': return <Eye className="h-4 w-4" />;
      default: return <Minus className="h-4 w-4" />;
    }
  };

  // アクションの日本語名取得
  const getActionLabel = (action: string) => {
    switch (action) {
      case 'buy': return '買い';
      case 'sell': return '売り';
      case 'hold': return '様子見';
      case 'watch': return '監視';
      default: return '不明';
    }
  };

  // 表示するカードの取得
  const displayCards = showAll ? cards : cards.slice(0, 3);

  // カードのクリック処理
  const handleCardClick = (card: JudgmentCard) => {
    if (card.symbol) {
      onStockSelect?.(card.symbol);
    }
  };

  // アクションボタンのクリック処理
  const handleActionClick = (card: JudgmentCard) => {
    if (card.symbol) {
      onActionClick?.(card.action, card.symbol);
    }
  };

  // データの更新
  const refreshData = () => {
    setIsLoading(true);
    setTimeout(() => {
      setLastUpdate(new Date());
      setIsLoading(false);
    }, 1000);
  };

  // 時間のフォーマット
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'たった今';
    if (diffMins < 60) return `${diffMins}分前`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}時間前`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}日前`;
  };

  if (isLoading) {
    return (
      <div className={`bg-white rounded-lg shadow border ${className}`}>
        <div className="p-6">
          <div className="flex items-center justify-center">
            <RefreshCw className="h-6 w-6 animate-spin text-blue-600 mr-3" />
            <span className="text-gray-600">判断パネルを読み込み中...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow border ${className}`}>
      {/* ヘッダー */}
      <div className="p-4 border-b">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-900">判断パネル</h2>
            <p className="text-sm text-gray-600">
              今日の投資判断に必要な情報を集約
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={refreshData}
              className="flex items-center px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              更新
            </button>
            {cards.length > 3 && (
              <button
                onClick={() => setShowAll(!showAll)}
                className="flex items-center px-3 py-2 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
              >
                {showAll ? <EyeOff className="h-4 w-4 mr-2" /> : <Eye className="h-4 w-4 mr-2" />}
                {showAll ? '折りたたむ' : `全て表示 (${cards.length})`}
              </button>
            )}
          </div>
        </div>
        {lastUpdate && (
          <div className="flex items-center mt-2 text-sm text-gray-500">
            <Clock className="h-4 w-4 mr-1" />
            最終更新: {lastUpdate.toLocaleString('ja-JP')}
          </div>
        )}
      </div>

      {/* カード一覧 */}
      <div className="p-4">
        {displayCards.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {displayCards.map((card) => (
              <div
                key={card.id}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-all duration-200 hover:shadow-md ${getPriorityColor(card.priority)}`}
                onClick={() => handleCardClick(card)}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <div className="flex items-center space-x-1">
                      {card.type === 'prediction_deviation' && <TrendingUp className="h-5 w-5" />}
                      {card.type === 'decline_alert' && <TrendingDown className="h-5 w-5" />}
                      {card.type === 'volume_surge' && <BarChart3 className="h-5 w-5" />}
                      {card.type === 'recommendation' && <Target className="h-5 w-5" />}
                    </div>
                    <h3 className="font-semibold">{card.title}</h3>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Star className="h-4 w-4 text-yellow-500" />
                    <span className="text-sm font-medium">{card.confidence}%</span>
                  </div>
                </div>

                <p className="text-sm text-gray-700 mb-3">{card.description}</p>

                {card.symbol && (
                  <div className="mb-3">
                    <div className="text-sm font-medium text-gray-900">{card.symbol}</div>
                    <div className="text-xs text-gray-600">{card.name}</div>
                  </div>
                )}

                {card.value !== undefined && (
                  <div className="mb-3">
                    <div className="flex items-center space-x-2">
                      <DollarSign className="h-4 w-4 text-gray-500" />
                      <span className="text-lg font-bold">
                        {card.value > 0 ? '+' : ''}{card.value}%
                      </span>
                      {card.change !== undefined && (
                        <span className={`text-sm ${card.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          ({card.change >= 0 ? '+' : ''}{card.change}%)
                        </span>
                      )}
                    </div>
                  </div>
                )}

                <div className="flex items-center justify-between">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleActionClick(card);
                    }}
                    className={`flex items-center space-x-2 px-3 py-2 rounded-lg border text-sm font-medium transition-colors ${getActionColor(card.action)}`}
                  >
                    {getActionIcon(card.action)}
                    <span>{getActionLabel(card.action)}</span>
                  </button>
                  <span className="text-xs text-gray-500">
                    {formatTime(card.timestamp)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <AlertTriangle className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p className="text-lg font-medium text-gray-500">判断情報がありません</p>
            <p className="text-sm text-gray-400">データの更新を待っています</p>
          </div>
        )}
      </div>

      {/* サマリー統計 */}
      {cards.length > 0 && (
        <div className="p-4 border-t bg-gray-50">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-red-600">
                {cards.filter(c => c.priority === 'critical').length}
              </div>
              <div className="text-sm text-gray-600">緊急</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-orange-600">
                {cards.filter(c => c.priority === 'high').length}
              </div>
              <div className="text-sm text-gray-600">重要</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">
                {cards.filter(c => c.action === 'buy').length}
              </div>
              <div className="text-sm text-gray-600">買い推奨</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-red-600">
                {cards.filter(c => c.action === 'sell').length}
              </div>
              <div className="text-sm text-gray-600">売り推奨</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
