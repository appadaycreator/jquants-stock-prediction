"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Calendar,
  Trash2,
  RefreshCw,
  AlertTriangle,
  Info,
  Eye,
  ExternalLink,
} from "lucide-react";
import EnhancedTooltip from "@/components/EnhancedTooltip";
import { openMinkabuLink } from "@/lib/minkabu-utils";
import { formatStockCode } from "@/lib/stock-code-utils";

interface WatchlistItem {
  symbol: string;
  name: string;
  sector: string;
  market: string;
  currentPrice: number;
  addedAt: string;
  targetPrice?: number;
  riskLevel: string;
  recommendation: string;
  confidence: number;
}

export default function WatchlistPage() {
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    loadWatchlist();
  }, []);

  const loadWatchlist = () => {
    try {
      const watchlistData = JSON.parse(localStorage.getItem("user_watchlist") || "[]");
      setWatchlist(watchlistData);
    } catch (error) {
      console.error("ウォッチリスト読み込みエラー:", error);
      setMessage("ウォッチリストの読み込みに失敗しました");
    } finally {
      setLoading(false);
    }
  };

  const removeFromWatchlist = (symbol: string) => {
    try {
      const updatedWatchlist = watchlist.filter(item => item.symbol !== symbol);
      setWatchlist(updatedWatchlist);
      localStorage.setItem("user_watchlist", JSON.stringify(updatedWatchlist));
      setMessage(`${symbol} をウォッチリストから削除しました`);
    } catch (error) {
      console.error("ウォッチリスト削除エラー:", error);
      setMessage("ウォッチリストからの削除に失敗しました");
    }
  };

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation) {
      case "BUY":
        return "bg-green-100 text-green-800 border-green-200";
      case "SELL":
        return "bg-red-100 text-red-800 border-red-200";
      case "HOLD":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case "HIGH":
        return "text-red-600";
      case "MEDIUM":
        return "text-yellow-600";
      case "LOW":
        return "text-green-600";
      default:
        return "text-gray-600";
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>ウォッチリストを読み込み中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* ヘッダー */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">ウォッチリスト</h1>
          <p className="text-gray-600">注目銘柄の監視と分析</p>
        </div>
        <div className="flex space-x-2">
          <Button
            variant="outline"
            onClick={loadWatchlist}
            disabled={loading}
            aria-label="ウォッチリストを更新"
            data-help="ウォッチリストのデータを最新に更新します。銘柄の現在価格、推奨アクション、信頼度、リスクレベル、目標価格などの情報を再取得します。市場の最新動向に基づいて監視対象銘柄の状況を確認できます。リアルタイムで価格変動を監視し、投資機会を見逃さないようにサポートします。更新により、アラート条件の再評価も行われます。投資判断の精度向上のため、常に最新の情報を提供し、重要な価格変動や投資推奨の変更をリアルタイムで監視できます。投資機会の発見と銘柄監視の効率化をサポートします。"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
            更新
          </Button>
        </div>
      </div>

      {/* メッセージ */}
      {message && (
        <div className={`p-4 rounded-lg ${
          message.includes("失敗") 
            ? "bg-red-100 text-red-800 border border-red-200" 
            : "bg-green-100 text-green-800 border border-green-200"
        }`}>
          {message}
        </div>
      )}

      {/* ウォッチリスト統計 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">総銘柄数</CardTitle>
            <Eye className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <EnhancedTooltip
              content="ウォッチリストに登録されている銘柄の総数です。監視対象として設定した銘柄の数で、投資判断の参考となる銘柄の数を示します。例：10銘柄の場合、10つの銘柄がウォッチリストに登録されています。"
              type="info"
            >
              <div className="text-2xl font-bold cursor-help">{watchlist.length}</div>
            </EnhancedTooltip>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">買い推奨</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <EnhancedTooltip
              content="買い推奨の銘柄数です。AI分析により買い推奨される銘柄の数で、上昇期待値を持つ銘柄を示します。例：5銘柄の場合、5つの銘柄が買い推奨されています。"
              type="success"
            >
              <div className="text-2xl font-bold text-green-600 cursor-help">
                {watchlist.filter(item => item.recommendation === "BUY").length}
              </div>
            </EnhancedTooltip>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">ホールド</CardTitle>
            <TrendingDown className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <EnhancedTooltip
              content="ホールド推奨の銘柄数です。AI分析により現状維持が推奨される銘柄の数で、大きな変動が予想されない銘柄を示します。例：3銘柄の場合、3つの銘柄がホールド推奨されています。"
              type="info"
            >
              <div className="text-2xl font-bold text-yellow-600 cursor-help">
                {watchlist.filter(item => item.recommendation === "HOLD").length}
              </div>
            </EnhancedTooltip>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">売り推奨</CardTitle>
            <TrendingDown className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <EnhancedTooltip
              content="売り推奨の銘柄数です。AI分析により売り推奨される銘柄の数で、下落リスクを持つ銘柄を示します。例：2銘柄の場合、2つの銘柄が売り推奨されています。"
              type="warning"
            >
              <div className="text-2xl font-bold text-red-600 cursor-help">
                {watchlist.filter(item => item.recommendation === "SELL").length}
              </div>
            </EnhancedTooltip>
          </CardContent>
        </Card>
      </div>

      {/* ウォッチリスト一覧 */}
      {watchlist.length === 0 ? (
        <Card>
          <CardContent className="flex items-center justify-center py-12">
            <div className="text-center">
              <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">ウォッチリストが空です</h3>
              <p className="text-gray-600 mb-4">銘柄詳細ページから銘柄をウォッチリストに追加してください</p>
              <Button 
                onClick={() => window.location.href = "/listed-data"}
                className="bg-blue-600 text-white hover:bg-blue-700"
                aria-label="銘柄一覧ページへ移動"
                data-help="上場銘柄の一覧ページに移動して銘柄を選択できます。セクター別、市場別、価格帯別の詳細フィルタリングが可能です。投資対象となる銘柄を効率的に発見し、ウォッチリストに追加できます。機械学習による推奨銘柄やテクニカル分析結果も確認でき、投資判断の精度向上に役立ちます。CSVエクスポート機能で分析結果を外部ツールで活用できます。リアルタイム価格データ、出来高情報、テクニカル指標、投資推奨ランキングなど、包括的な銘柄情報を提供します。投資戦略に応じた銘柄選別機能も利用できます。投資機会の発見と銘柄選別の効率化をサポートします。"
              >
                銘柄一覧を見る
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {watchlist.map((item) => (
            <Card key={item.symbol} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div>
                      <h3 className="font-semibold">{formatStockCode(item.symbol)}</h3>
                      <p className="text-sm text-gray-600">{item.name}</p>
                    </div>
                    <Badge className={getRecommendationColor(item.recommendation)}>
                      {item.recommendation}
                    </Badge>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        // チャートページに遷移
                        window.location.href = `/analysis?symbol=${item.symbol}`;
                      }}
                      className="text-green-600 hover:text-green-800 hover:bg-green-50"
                      aria-label={`${item.symbol}のチャートを表示`}
                      data-help="この銘柄の詳細なチャートと分析を表示します。テクニカル指標、価格予測、機械学習分析結果を確認できます。移動平均線、RSI、MACD、ボリンジャーバンドなどの技術分析指標と、AIによる価格予測を詳細に分析できます。プロの投資家レベルの分析ツールで、投資判断の精度向上に役立ちます。インタラクティブなチャートで、ズーム、パン、指標の追加・削除が可能です。投資判断の信頼性を高めるため、推奨アクションの根拠となる分析結果を詳細に確認できます。投資判断の精度向上と継続的な改善をサポートします。"
                    >
                      <TrendingUp className="h-4 w-4 mr-1" />
                      チャート
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => openMinkabuLink(item.symbol)}
                      className="text-orange-600 hover:text-orange-800 hover:bg-orange-50"
                      aria-label={`${item.symbol}のみんかぶページを開く`}
                      data-help="みんかぶの詳細ページを新しいタブで開きます。投資家の意見、財務情報、ニュース、決算情報、業績予想などの詳細情報を確認できます。投資判断の参考となる外部情報を効率的に収集できます。ファンダメンタル分析の補完として、投資判断の精度向上に役立ちます。投資家コミュニティの意見や評価も確認でき、市場のセンチメントを把握できます。投資判断の信頼性を高めるため、複数の情報源から総合的な分析を行うことができます。投資判断の多角的な検証と精度向上をサポートします。"
                    >
                      <ExternalLink className="h-4 w-4 mr-1" />
                      みんかぶ
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => removeFromWatchlist(item.symbol)}
                      className="text-red-600 hover:text-red-800 hover:bg-red-50"
                      aria-label={`${item.symbol}をウォッチリストから削除`}
                      data-help="この銘柄をウォッチリストから削除します。削除後は監視対象から外れ、アラートも停止されます。投資対象から除外する際や、監視を終了する際に使用します。削除した銘柄は後から再度追加できます。ウォッチリストを整理して、重要な銘柄に集中できるようサポートします。削除操作は確認なしで実行されるため、注意して使用してください。投資戦略の見直しや、ポートフォリオの最適化に伴う銘柄の整理に役立ちます。投資判断の効率化と銘柄管理の最適化をサポートします。"
                    >
                      <Trash2 className="h-4 w-4 mr-1" />
                      削除
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600">現在価格</p>
                    <EnhancedTooltip
                      content="最新の取引終値です。この価格は最新の市場取引で確定した価格で、現在の株価の基準となります。例：トヨタ自動車の株価が3,000円の場合、1株あたり3,000円で取引されていることを示します。"
                      type="info"
                    >
                      <p className="font-medium cursor-help">¥{item.currentPrice.toLocaleString()}</p>
                    </EnhancedTooltip>
                  </div>
                  <div>
                    <p className="text-gray-600">セクター</p>
                    <p className="font-medium">{item.sector}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">リスクレベル</p>
                    <p className={`font-medium ${getRiskColor(item.riskLevel)}`}>
                      {item.riskLevel}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600">信頼度</p>
                    <EnhancedTooltip
                      content="AI分析結果の信頼度です。複数の技術指標を総合的に評価した結果の確信度を示します。80%以上が高信頼度、60-80%が中信頼度、60%未満が低信頼度とされます。例：信頼度85%の場合、分析結果が高い確率で正しいことを示します。"
                      type="info"
                    >
                      <p className="font-medium cursor-help">{(item.confidence * 100).toFixed(1)}%</p>
                    </EnhancedTooltip>
                  </div>
                </div>
                
                {item.targetPrice && (
                  <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">目標価格</span>
                      <EnhancedTooltip
                        content="AI分析による目標価格です。技術分析とファンダメンタル分析を総合して算出された期待価格で、投資判断の参考となります。例：目標価格3,500円の場合、この価格まで上昇する可能性が高いことを示します。"
                        type="info"
                      >
                        <span className="text-sm font-semibold text-blue-800 cursor-help">
                          ¥{item.targetPrice.toLocaleString()}
                        </span>
                      </EnhancedTooltip>
                    </div>
                  </div>
                )}
                
                <div className="mt-4 flex items-center text-xs text-gray-500">
                  <Calendar className="h-3 w-3 mr-1" />
                  追加日: {new Date(item.addedAt).toLocaleString("ja-JP")}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
