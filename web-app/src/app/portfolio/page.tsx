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
} from "lucide-react";

interface PortfolioItem {
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

export default function PortfolioPage() {
  const [portfolio, setPortfolio] = useState<PortfolioItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    loadPortfolio();
  }, []);

  const loadPortfolio = () => {
    try {
      const portfolioData = JSON.parse(localStorage.getItem("user_portfolio") || "[]");
      setPortfolio(portfolioData);
    } catch (error) {
      console.error("ポートフォリオ読み込みエラー:", error);
      setMessage("ポートフォリオの読み込みに失敗しました");
    } finally {
      setLoading(false);
    }
  };

  const removeFromPortfolio = (symbol: string) => {
    try {
      const updatedPortfolio = portfolio.filter(item => item.symbol !== symbol);
      setPortfolio(updatedPortfolio);
      localStorage.setItem("user_portfolio", JSON.stringify(updatedPortfolio));
      setMessage(`${symbol} をポートフォリオから削除しました`);
    } catch (error) {
      console.error("ポートフォリオ削除エラー:", error);
      setMessage("ポートフォリオからの削除に失敗しました");
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
          <p>ポートフォリオを読み込み中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* ヘッダー */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">マイポートフォリオ</h1>
          <p className="text-gray-600">保有銘柄の管理と分析</p>
        </div>
        <div className="flex space-x-2">
          <Button
            variant="outline"
            onClick={loadPortfolio}
            disabled={loading}
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

      {/* ポートフォリオ統計 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">総銘柄数</CardTitle>
            <Info className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{portfolio.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">買い推奨</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {portfolio.filter(item => item.recommendation === "BUY").length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">ホールド</CardTitle>
            <TrendingDown className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              {portfolio.filter(item => item.recommendation === "HOLD").length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">売り推奨</CardTitle>
            <TrendingDown className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {portfolio.filter(item => item.recommendation === "SELL").length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* ポートフォリオ一覧 */}
      {portfolio.length === 0 ? (
        <Card>
          <CardContent className="flex items-center justify-center py-12">
            <div className="text-center">
              <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">ポートフォリオが空です</h3>
              <p className="text-gray-600 mb-4">銘柄詳細ページから銘柄をポートフォリオに追加してください</p>
              <Button 
                onClick={() => window.location.href = "/listed-data"}
                className="bg-blue-600 text-white hover:bg-blue-700"
              >
                銘柄一覧を見る
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {portfolio.map((item) => (
            <Card key={item.symbol} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div>
                      <h3 className="font-semibold">{item.symbol}</h3>
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
                      onClick={() => removeFromPortfolio(item.symbol)}
                      className="text-red-600 hover:text-red-800 hover:bg-red-50"
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
                    <p className="font-medium">¥{item.currentPrice.toLocaleString()}</p>
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
                    <p className="font-medium">{(item.confidence * 100).toFixed(1)}%</p>
                  </div>
                </div>
                
                {item.targetPrice && (
                  <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">目標価格</span>
                      <span className="text-sm font-semibold text-blue-800">
                        ¥{item.targetPrice.toLocaleString()}
                      </span>
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
