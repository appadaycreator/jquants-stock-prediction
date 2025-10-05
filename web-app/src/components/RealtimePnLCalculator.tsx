"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  RefreshCw,
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
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
  last_updated: string;
}

interface RealtimePnLCalculatorProps {
  positions: Position[];
  onPnLUpdate?: (updatedPositions: Position[]) => void;
  refreshInterval?: number; // ミリ秒
}

export default function RealtimePnLCalculator({ 
  positions, 
  onPnLUpdate,
  refreshInterval = 30000, // 30秒
}: RealtimePnLCalculatorProps) {
  const [updatedPositions, setUpdatedPositions] = useState<Position[]>(positions);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [connectionStatus, setConnectionStatus] = useState<"connected" | "disconnected" | "error">("connected");

  // リアルタイム価格取得のシミュレーション
  const fetchRealtimePrices = useCallback(async () => {
    try {
      setIsRefreshing(true);
      
      // 実際の実装では、リアルタイムAPIから価格を取得
      // ここではシミュレーションとして、ランダムな価格変動を生成
      const updated = updatedPositions.map(position => {
        const priceChange = (Math.random() - 0.5) * 0.02; // ±1%の変動
        const newPrice = position.current_price * (1 + priceChange);
        const newTotalValue = newPrice * position.quantity;
        const newUnrealizedPnL = newTotalValue - (position.cost_basis * position.quantity);
        const newPnLPercentage = (newUnrealizedPnL / (position.cost_basis * position.quantity)) * 100;

        return {
          ...position,
          current_price: newPrice,
          total_value: newTotalValue,
          unrealized_pnl: newUnrealizedPnL,
          pnl_percentage: newPnLPercentage,
          last_updated: new Date().toISOString(),
        };
      });

      setUpdatedPositions(updated);
      setLastUpdate(new Date());
      setConnectionStatus("connected");
      
      if (onPnLUpdate) {
        onPnLUpdate(updated);
      }
    } catch (error) {
      console.error("リアルタイム価格取得エラー:", error);
      setConnectionStatus("error");
    } finally {
      setIsRefreshing(false);
    }
  }, [updatedPositions, onPnLUpdate]);

  // 自動更新の設定
  useEffect(() => {
    const interval = setInterval(fetchRealtimePrices, refreshInterval);
    return () => clearInterval(interval);
  }, [fetchRealtimePrices, refreshInterval]);

  // 手動更新
  const handleManualRefresh = () => {
    fetchRealtimePrices();
  };

  // 総損益の計算
  const totalPnL = updatedPositions.reduce((sum, position) => sum + position.unrealized_pnl, 0);
  const totalInvestment = updatedPositions.reduce((sum, position) => sum + (position.cost_basis * position.quantity), 0);
  const totalValue = updatedPositions.reduce((sum, position) => sum + position.total_value, 0);
  const totalPnLPercentage = totalInvestment > 0 ? (totalPnL / totalInvestment) * 100 : 0;

  // 接続ステータスの表示
  const getConnectionStatusIcon = () => {
    switch (connectionStatus) {
      case "connected":
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case "disconnected":
        return <Clock className="h-4 w-4 text-yellow-600" />;
      case "error":
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      default:
        return <Activity className="h-4 w-4 text-gray-600" />;
    }
  };

  const getConnectionStatusText = () => {
    switch (connectionStatus) {
      case "connected":
        return "リアルタイム接続中";
      case "disconnected":
        return "接続切断";
      case "error":
        return "接続エラー";
      default:
        return "接続中...";
    }
  };

  return (
    <div className="space-y-4">
      {/* リアルタイム損益サマリー */}
      <Card className="bg-gradient-to-r from-blue-50 to-green-50 border-blue-200">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-semibold text-blue-900">
              リアルタイム損益
            </CardTitle>
            <div className="flex items-center space-x-2">
              <Badge 
                variant={connectionStatus === "connected" ? "default" : "secondary"}
                className="flex items-center space-x-1"
              >
                {getConnectionStatusIcon()}
                <span className="text-xs">{getConnectionStatusText()}</span>
              </Badge>
              <Button
                variant="outline"
                size="sm"
                onClick={handleManualRefresh}
                disabled={isRefreshing}
                title="手動で価格を更新"
              >
                <RefreshCw className={`h-4 w-4 mr-1 ${isRefreshing ? "animate-spin" : ""}`} />
                更新
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-900">
                ¥{totalValue.toLocaleString()}
              </div>
              <div className="text-sm text-blue-700">現在価値</div>
            </div>
            <div className="text-center">
              <div className={`text-3xl font-bold ${totalPnL >= 0 ? "text-green-600" : "text-red-600"}`}>
                {totalPnL >= 0 ? "+" : ""}¥{totalPnL.toLocaleString()}
              </div>
              <div className={`text-sm font-medium ${totalPnL >= 0 ? "text-green-700" : "text-red-700"}`}>
                {totalPnL >= 0 ? "+" : ""}{totalPnLPercentage.toFixed(2)}%
              </div>
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

      {/* 個別ポジションのリアルタイム更新 */}
      <div className="grid gap-3">
        {updatedPositions.map((position) => (
          <Card key={position.symbol} className="hover:shadow-md transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-lg">{position.symbol}</h3>
                  <p className="text-sm text-gray-600">{position.company_name}</p>
                </div>
                <div className="text-right">
                  <div className="text-xl font-bold">
                    ¥{position.current_price.toLocaleString()}
                  </div>
                  <div className={`text-lg font-semibold ${position.pnl_percentage >= 0 ? "text-green-600" : "text-red-600"}`}>
                    {position.pnl_percentage >= 0 ? "+" : ""}{position.pnl_percentage.toFixed(2)}%
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">数量</p>
                  <p className="font-medium">{position.quantity.toLocaleString()}株</p>
                </div>
                <div>
                  <p className="text-gray-600">評価額</p>
                  <p className="font-medium">¥{position.total_value.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-gray-600">損益</p>
                  <p className={`font-medium ${position.unrealized_pnl >= 0 ? "text-green-600" : "text-red-600"}`}>
                    ¥{position.unrealized_pnl.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">更新時刻</p>
                  <p className="font-medium text-xs">
                    {new Date(position.last_updated).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
