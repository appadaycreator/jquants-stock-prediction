"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
// Progress component is replaced with simple HTML progress bar
import { 
  Activity, 
  CheckCircle, 
  Clock, 
  AlertTriangle, 
  RefreshCw,
  Play,
  Pause,
  BarChart3,
  TrendingUp,
  Database,
  Cpu,
} from "lucide-react";

// 分析状況の型定義
interface AnalysisStatus {
  id: string;
  name: string;
  status: "running" | "completed" | "failed" | "pending";
  progress: number;
  startTime: string;
  endTime?: string;
  duration?: number;
  results?: {
    accuracy?: number;
    predictions?: number;
    models?: string[];
  };
  error?: string;
}

// システム統計の型定義
interface SystemStats {
  totalAnalyses: number;
  successfulAnalyses: number;
  failedAnalyses: number;
  averageDuration: number;
  lastUpdate: string;
}

export default function AnalysisProgressPage() {
  const [analyses, setAnalyses] = useState<AnalysisStatus[]>([]);
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadAnalysisData();
    
    // 自動更新の設定
    if (autoRefresh) {
      const interval = setInterval(loadAnalysisData, 5000); // 5秒ごと
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const loadAnalysisData = async () => {
    try {
      setLoading(true);
      
      // クライアントサイドでの分析状況シミュレーション
      // 実際の分析状況取得は静的サイトでは実行できないため、シミュレーション
      const mockAnalyses: AnalysisStatus[] = [
          {
            id: "1",
            name: "統合株価予測分析",
            status: "completed" as const,
            progress: 100,
            startTime: "2025-09-29T15:00:00Z",
            endTime: "2025-09-29T15:05:30Z",
            duration: 330,
            results: {
              accuracy: 0.85,
              predictions: 56,
              models: ["XGBoost", "Random Forest", "LSTM"],
            },
          },
          {
            id: "2",
            name: "感情分析システム",
            status: "running" as const,
            progress: 65,
            startTime: "2025-09-29T15:10:00Z",
            results: {
              accuracy: 0.78,
              predictions: 23,
              models: ["BERT", "Sentiment Analysis"],
            },
          },
          {
            id: "3",
            name: "リスク評価分析",
            status: "pending" as const,
            progress: 0,
            startTime: "2025-09-29T15:15:00Z",
          },
        ];
        
        setAnalyses(mockAnalyses);
        setSystemStats({
          totalAnalyses: 15,
          successfulAnalyses: 12,
          failedAnalyses: 3,
          averageDuration: 285,
          lastUpdate: new Date().toISOString(),
        });
    } catch (error) {
      console.error("分析状況データの読み込みエラー:", error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "running":
        return <Activity className="h-4 w-4 text-blue-500 animate-pulse" />;
      case "completed":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "failed":
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case "pending":
        return <Clock className="h-4 w-4 text-yellow-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "running":
        return "bg-blue-100 text-blue-800";
      case "completed":
        return "bg-green-100 text-green-800";
      case "failed":
        return "bg-red-100 text-red-800";
      case "pending":
        return "bg-yellow-100 text-yellow-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}分${remainingSeconds}秒`;
  };

  const formatTime = (timeString: string) => {
    return new Date(timeString).toLocaleString("ja-JP");
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>分析状況を読み込み中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">分析状況</h1>
          <p className="text-gray-600 mt-2">リアルタイム分析プロセスの監視と管理</p>
        </div>
        <div className="flex space-x-3">
          <Button
            onClick={loadAnalysisData}
            variant="outline"
            size="sm"
            aria-label="分析状況を更新"
            data-help="分析状況のデータを手動で更新します。実行中の分析の進捗状況、完了した分析の結果、システム統計を最新に取得します。リアルタイムで分析プロセスの状況を確認できます。"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            更新
          </Button>
          <Button
            onClick={() => setAutoRefresh(!autoRefresh)}
            variant={autoRefresh ? "default" : "outline"}
            size="sm"
            aria-label={autoRefresh ? "自動更新を停止" : "自動更新を開始"}
            data-help={autoRefresh ? "5秒ごとの自動更新を停止します。手動更新に切り替わります。バッテリー消費を抑えたい場合や、更新頻度を制御したい場合に使用します。" : "5秒ごとに分析状況を自動更新します。リアルタイムで分析の進捗を監視できます。長時間の分析プロセスを継続的に監視する際に便利です。"}
          >
            {autoRefresh ? <Pause className="h-4 w-4 mr-2" /> : <Play className="h-4 w-4 mr-2" />}
            {autoRefresh ? "自動更新停止" : "自動更新開始"}
          </Button>
        </div>
      </div>

      {/* システム統計 */}
      {systemStats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">総分析数</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{systemStats.totalAnalyses}</div>
              <p className="text-xs text-muted-foreground">
                累計実行回数
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">成功率</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {((systemStats.successfulAnalyses / systemStats.totalAnalyses) * 100).toFixed(1)}%
              </div>
              <p className="text-xs text-muted-foreground">
                {systemStats.successfulAnalyses}/{systemStats.totalAnalyses} 成功
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">平均時間</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatDuration(systemStats.averageDuration)}</div>
              <p className="text-xs text-muted-foreground">
                分析実行時間
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">最終更新</CardTitle>
              <Database className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-sm font-bold">{formatTime(systemStats.lastUpdate)}</div>
              <p className="text-xs text-muted-foreground">
                リアルタイム監視
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 分析一覧 */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-gray-900">実行中の分析</h2>
        {analyses.length === 0 ? (
          <Card>
            <CardContent className="flex items-center justify-center py-8">
              <div className="text-center">
                <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">実行中の分析はありません</p>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {analyses.map((analysis) => (
              <Card key={analysis.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(analysis.status)}
                      <div>
                        <h3 className="font-semibold">{analysis.name}</h3>
                        <p className="text-sm text-gray-600">
                          開始: {formatTime(analysis.startTime)}
                          {analysis.endTime && ` | 終了: ${formatTime(analysis.endTime)}`}
                        </p>
                      </div>
                    </div>
                    <Badge className={getStatusColor(analysis.status)}>
                      {analysis.status === "running" ? "実行中" :
                       analysis.status === "completed" ? "完了" :
                       analysis.status === "failed" ? "失敗" : "待機中"}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* 進捗バー */}
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span>進捗</span>
                        <span>{analysis.progress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${analysis.progress}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* 結果情報 */}
                    {analysis.results && (
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {analysis.results.accuracy && (
                          <div className="text-center">
                            <div className="text-2xl font-bold text-green-600">
                              {(analysis.results.accuracy * 100).toFixed(1)}%
                            </div>
                            <div className="text-sm text-gray-600">精度</div>
                          </div>
                        )}
                        {analysis.results.predictions && (
                          <div className="text-center">
                            <div className="text-2xl font-bold text-blue-600">
                              {analysis.results.predictions}
                            </div>
                            <div className="text-sm text-gray-600">予測数</div>
                          </div>
                        )}
                        {analysis.results.models && (
                          <div className="text-center">
                            <div className="text-2xl font-bold text-purple-600">
                              {analysis.results.models.length}
                            </div>
                            <div className="text-sm text-gray-600">モデル数</div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* 実行時間 */}
                    {analysis.duration && (
                      <div className="flex items-center text-sm text-gray-600">
                        <Clock className="h-4 w-4 mr-2" />
                        実行時間: {formatDuration(analysis.duration)}
                      </div>
                    )}

                    {/* エラー情報 */}
                    {analysis.error && (
                      <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                        <div className="flex items-center">
                          <AlertTriangle className="h-4 w-4 text-red-500 mr-2" />
                          <span className="text-red-800 font-medium">エラー</span>
                        </div>
                        <p className="text-red-700 text-sm mt-1">{analysis.error}</p>
                      </div>
                    )}

                    {/* 使用モデル */}
                    {analysis.results?.models && (
                      <div>
                        <div className="text-sm font-medium text-gray-700 mb-2">使用モデル:</div>
                        <div className="flex flex-wrap gap-2">
                          {analysis.results.models.map((model, index) => (
                            <Badge key={index} variant="outline">
                              {model}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* システム情報 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Cpu className="h-5 w-5 mr-2" />
            システム情報
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">パフォーマンス</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">CPU使用率</span>
                  <span className="text-sm font-medium">45%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">メモリ使用率</span>
                  <span className="text-sm font-medium">62%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">ディスク使用率</span>
                  <span className="text-sm font-medium">38%</span>
                </div>
              </div>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">分析エンジン</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">アクティブプロセス</span>
                  <span className="text-sm font-medium">3</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">キュー待機</span>
                  <span className="text-sm font-medium">1</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">処理速度</span>
                  <span className="text-sm font-medium">高速</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
