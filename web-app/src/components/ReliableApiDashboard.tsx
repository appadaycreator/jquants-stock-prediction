"use client";

import { useState, useEffect } from "react";
import { 
  Activity, 
  Database, 
  Shield, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  RefreshCw,
  BarChart3,
  Settings,
  Download,
} from "lucide-react";
import ReliableApiSystem, { SystemHealth } from "@/lib/reliable-api-system";
import DataQualityMonitor, { QualityReport } from "@/lib/data-quality-monitor";

interface ReliableApiDashboardProps {
  system: ReliableApiSystem;
  onSystemUpdate?: (system: ReliableApiSystem) => void;
}

export default function ReliableApiDashboard({ system, onSystemUpdate }: ReliableApiDashboardProps) {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [qualityReport, setQualityReport] = useState<QualityReport | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    loadSystemHealth();
    loadQualityReport();
  }, [system]);

  const loadSystemHealth = async () => {
    try {
      const healthData = system.getSystemHealth();
      setHealth(healthData);
    } catch (error) {
      console.error("システムヘルス取得エラー:", error);
    }
  };

  const loadQualityReport = async () => {
    try {
      const endDate = new Date().toISOString();
      const startDate = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();
      
      const report = system.generateQualityReport({ start: startDate, end: endDate });
      setQualityReport(report);
    } catch (error) {
      console.error("品質レポート取得エラー:", error);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await loadSystemHealth();
      await loadQualityReport();
    } finally {
      setIsRefreshing(false);
    }
  };

  const getHealthColor = (status: string) => {
    switch (status) {
      case "healthy": return "text-green-600 bg-green-100";
      case "degraded": return "text-yellow-600 bg-yellow-100";
      case "unhealthy": return "text-red-600 bg-red-100";
      default: return "text-gray-600 bg-gray-100";
    }
  };

  const getHealthIcon = (status: string) => {
    switch (status) {
      case "healthy": return <CheckCircle className="w-5 h-5" />;
      case "degraded": return <AlertTriangle className="w-5 h-5" />;
      case "unhealthy": return <AlertTriangle className="w-5 h-5" />;
      default: return <Activity className="w-5 h-5" />;
    }
  };

  if (!health) {
    return (
      <div className="flex items-center justify-center p-8">
        <RefreshCw className="w-6 h-6 animate-spin" />
        <span className="ml-2">システム状態を読み込み中...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">API信頼性ダッシュボード</h2>
          <p className="text-gray-600">システムの健康状態とパフォーマンス監視</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isRefreshing ? "animate-spin" : ""}`} />
            更新
          </button>
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="flex items-center px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            <Settings className="w-4 h-4 mr-2" />
            {showDetails ? "簡易表示" : "詳細表示"}
          </button>
        </div>
      </div>

      {/* 全体ステータス */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">システム全体ステータス</h3>
          <div className={`flex items-center px-3 py-1 rounded-full ${getHealthColor(health.overall)}`}>
            {getHealthIcon(health.overall)}
            <span className="ml-2 font-medium capitalize">{health.overall}</span>
          </div>
        </div>

        {health.recommendations.length > 0 && (
          <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <h4 className="font-medium text-yellow-800 mb-2">推奨事項</h4>
            <ul className="text-sm text-yellow-700 space-y-1">
              {health.recommendations.map((rec, index) => (
                <li key={index} className="flex items-start">
                  <span className="mr-2">•</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* メトリクスカード */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* API接続 */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <Activity className="w-5 h-5 text-blue-600 mr-2" />
              <h4 className="font-semibold">API接続</h4>
            </div>
            <div className={`px-2 py-1 rounded text-xs font-medium ${getHealthColor(health.api.status)}`}>
              {health.api.status}
            </div>
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span>成功率:</span>
              <span className="font-medium">
                {health.api.metrics.totalRequests > 0 
                  ? Math.round((health.api.metrics.successfulRequests / health.api.metrics.totalRequests) * 100)
                  : 0}%
              </span>
            </div>
            <div className="flex justify-between">
              <span>平均応答時間:</span>
              <span className="font-medium">{Math.round(health.api.metrics.averageResponseTime)}ms</span>
            </div>
            <div className="flex justify-between">
              <span>連続失敗:</span>
              <span className="font-medium">{health.api.consecutiveFailures}回</span>
            </div>
          </div>
        </div>

        {/* キャッシュ */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center mb-4">
            <Database className="w-5 h-5 text-green-600 mr-2" />
            <h4 className="font-semibold">キャッシュ</h4>
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span>ヒット率:</span>
              <span className="font-medium">{Math.round(health.cache.hitRate)}%</span>
            </div>
            <div className="flex justify-between">
              <span>総サイズ:</span>
              <span className="font-medium">{(health.cache.totalSize / 1024 / 1024).toFixed(1)}MB</span>
            </div>
            <div className="flex justify-between">
              <span>効率性:</span>
              <span className="font-medium">{Math.round(health.cache.efficiency * 100)}%</span>
            </div>
          </div>
        </div>

        {/* データ品質 */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center mb-4">
            <Shield className="w-5 h-5 text-purple-600 mr-2" />
            <h4 className="font-semibold">データ品質</h4>
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span>品質スコア:</span>
              <span className="font-medium">{Math.round(health.quality.overallScore)}%</span>
            </div>
            <div className="flex justify-between">
              <span>アクティブ異常:</span>
              <span className="font-medium">{health.quality.activeAnomalies}件</span>
            </div>
            <div className="flex justify-between">
              <span>品質トレンド:</span>
              <span className="font-medium capitalize">{health.quality.trends.quality}</span>
            </div>
          </div>
        </div>

        {/* パフォーマンス */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center mb-4">
            <TrendingUp className="w-5 h-5 text-orange-600 mr-2" />
            <h4 className="font-semibold">パフォーマンス</h4>
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span>API応答時間:</span>
              <span className="font-medium">{Math.round(health.api.metrics.averageResponseTime)}ms</span>
            </div>
            <div className="flex justify-between">
              <span>キャッシュ効率:</span>
              <span className="font-medium">{Math.round(health.cache.efficiency * 100)}%</span>
            </div>
            <div className="flex justify-between">
              <span>パフォーマンストレンド:</span>
              <span className="font-medium capitalize">{health.quality.trends.performance}</span>
            </div>
          </div>
        </div>
      </div>

      {/* 詳細表示 */}
      {showDetails && (
        <div className="space-y-6">
          {/* 品質レポート */}
          {qualityReport && (
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">品質レポート</h3>
                <button
                  onClick={() => {
                    const reportData = JSON.stringify(qualityReport, null, 2);
                    const blob = new Blob([reportData], { type: "application/json" });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = `quality-report-${new Date().toISOString().split("T")[0]}.json`;
                    a.click();
                    URL.revokeObjectURL(url);
                  }}
                  className="flex items-center px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                >
                  <Download className="w-4 h-4 mr-1" />
                  ダウンロード
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">{qualityReport.overallQualityScore}%</div>
                  <div className="text-sm text-gray-600">全体品質スコア</div>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">{qualityReport.totalRecords}</div>
                  <div className="text-sm text-gray-600">総レコード数</div>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">{qualityReport.anomalies.length}</div>
                  <div className="text-sm text-gray-600">検出異常数</div>
                </div>
              </div>

              {qualityReport.recommendations.length > 0 && (
                <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <h4 className="font-medium text-blue-800 mb-2">品質改善推奨事項</h4>
                  <ul className="text-sm text-blue-700 space-y-1">
                    {qualityReport.recommendations.map((rec, index) => (
                      <li key={index} className="flex items-start">
                        <span className="mr-2">•</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* 詳細メトリクス */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">詳細メトリクス</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium mb-2">API統計</h4>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span>総リクエスト数:</span>
                    <span>{health.api.metrics.totalRequests}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>成功リクエスト:</span>
                    <span>{health.api.metrics.successfulRequests}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>失敗リクエスト:</span>
                    <span>{health.api.metrics.failedRequests}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>タイムアウトエラー:</span>
                    <span>{health.api.metrics.timeoutErrors}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>レート制限エラー:</span>
                    <span>{health.api.metrics.rateLimitErrors}</span>
                  </div>
                </div>
              </div>
              
              <div>
                <h4 className="font-medium mb-2">キャッシュ統計</h4>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span>総エントリ数:</span>
                    <span>{health.cache.totalSize}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>ヒット率:</span>
                    <span>{Math.round(health.cache.hitRate)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>ミス率:</span>
                    <span>{Math.round(100 - health.cache.hitRate)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>効率性:</span>
                    <span>{Math.round(health.cache.efficiency * 100)}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
